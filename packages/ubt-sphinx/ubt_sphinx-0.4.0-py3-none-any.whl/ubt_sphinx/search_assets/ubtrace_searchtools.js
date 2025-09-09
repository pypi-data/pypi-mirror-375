/*
 * ubtrace_searchtools.js
 * ~~~~~~~~~~~~~~~~~~~~~~
 *
 * ubTrace Sphinx JavaScript utilities for the full-text search.
 *
 * :copyright: Copyright 2007-2023 by the Sphinx team, see AUTHORS.
 * :license: BSD, see LICENSE for details.
 *
 * Reference from the Sphinx searchtools.js and
 * edited by the useblocks Team.
 */
'use strict'

/**
 * Simple result scoring code.
 */
if (typeof Scorer === 'undefined') {
  var Scorer = {
    // Implement the following function to further tweak the score for each result
    // The function takes a result array [docname, title, anchor, descr, score, filename]
    // and returns the new score.
    /*
    score: result => {
      const [docname, title, anchor, descr, score, filename] = result
      return score
    },
    */

    // query matches the full name of an object
    objNameMatch: 11,
    // or matches in the last dotted part of the object name
    objPartialMatch: 6,
    // Additive scores depending on the priority of the object
    objPrio: {
      0: 15, // used to be importantResults
      1: 5, // used to be objectResults
      2: -5, // used to be unimportantResults
    },
    //  Used when the priority is not in the mapping.
    objPrioDefault: 0,

    // query found in title
    title: 15,
    partialTitle: 7,
    // query found in terms
    term: 5,
    partialTerm: 2,
  }
}

const _removeChildren = (element) => {
  while (element && element.lastChild) element.removeChild(element.lastChild)
}

/**
 * See https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Regular_Expressions#escaping
 */
const _escapeRegExp = (string) => string.replace(/[.*+\-?^${}()|[\]\\]/g, '\\$&') // $& means the whole matched string

/**
 * Default splitQuery function. Can be overridden in ``sphinx.search`` with a
 * custom function per language.
 *
 * The regular expression works by splitting the string on consecutive characters
 * that are not Unicode letters, numbers, underscores, or emoji characters.
 * This is the same as ``\W+`` in Python, preserving the surrogate pair area.
 */
if (typeof splitQuery === 'undefined') {
  var splitQuery = (query) =>
    query.split(/[^\p{Letter}\p{Number}_\p{Emoji_Presentation}]+/gu).filter((term) => term) // remove remaining empty strings
}

/**
 * Search Module
 *
 * The Search module handles loading search index,
 * querying the search index using the search terms,
 * and displaying search results in the search box.
 * It also applies highlighting to the search result summary.
 */
const Search = {
  _index: null,
  _queued_query: null,
  _project_info: null,

  loadIndex: (url) => (document.body.appendChild(document.createElement('script')).src = url),

  setIndex: (index) => {
    Search._index = index
    if (Search._queued_query !== null) {
      const query = Search._queued_query
      Search._queued_query = null
      Search.query(query)
    }
  },

  hasIndex: () => Search._index !== null,

  deferQuery: (query) => (Search._queued_query = query),

  /**
   * perform a search for something (or wait until index is loaded)
   */
  performSearch: (query) => {
    if (query.trim().length > 0) {
      // index already loaded, the browser was quick!
      if (Search.hasIndex()) {
        return Search.query(query)
      } else Search.deferQuery(query)
    }
  },

  /**
   * execute search (requires search index to be loaded)
   */
  query: (query) => {
    const filenames = Search._index.filenames
    const docNames = Search._index.docnames
    const titles = Search._index.titles
    const allTitles = Search._index.alltitles
    const indexEntries = Search._index.indexentries
    const docHTMLs = Search._index.dochtmls

    // stem the search terms and add them to the correct list
    const stemmer = new Stemmer()
    const searchTerms = new Set()
    const excludedTerms = new Set()
    const highlightTerms = new Set()
    const objectTerms = new Set(splitQuery(query.toLowerCase().trim()))
    splitQuery(query.trim()).forEach((queryTerm) => {
      const queryTermLower = queryTerm.toLowerCase()

      // maybe skip this "word"
      // stopwords array is from language_data.js
      if (stopwords.indexOf(queryTermLower) !== -1 || queryTerm.match(/^\d+$/)) return

      // stem the word
      let word = stemmer.stemWord(queryTermLower)
      // select the correct list
      if (word[0] === '-') excludedTerms.add(word.substr(1))
      else {
        searchTerms.add(word)
        highlightTerms.add(queryTermLower)
      }
    })

    if (SPHINX_HIGHLIGHT_ENABLED) {
      // set in sphinx_highlight.js
      localStorage.setItem('sphinx_highlight_terms', [...highlightTerms].join(' '))
    }

    // console.debug("SEARCH: searching for:");
    // console.info("required: ", [...searchTerms]);
    // console.info("excluded: ", [...excludedTerms]);

    // array of [docname, title, anchor, descr, score, filename, dochtml, project_details]
    let results = []

    const queryLower = query.toLowerCase()
    for (const [title, foundTitles] of Object.entries(allTitles)) {
      if (title.toLowerCase().includes(queryLower) && queryLower.length >= title.length / 2) {
        for (const [file, id] of foundTitles) {
          let score = Math.round((100 * queryLower.length) / title.length)
          results.push([
            docNames[file],
            titles[file] !== title ? `${titles[file]} > ${title}` : title,
            id !== null ? '#' + id : '',
            null,
            score,
            filenames[file],
            docHTMLs[docNames[file]],
            Search._project_info,
          ])
        }
      }
    }

    // search for explicit entries in index directives
    for (const [entry, foundEntries] of Object.entries(indexEntries)) {
      if (entry.includes(queryLower) && queryLower.length >= entry.length / 2) {
        for (const [file, id] of foundEntries) {
          let score = Math.round((100 * queryLower.length) / entry.length)
          results.push([
            docNames[file],
            titles[file],
            id ? '#' + id : '',
            null,
            score,
            filenames[file],
            docHTMLs[docNames[file]],
            Search._project_info,
          ])
        }
      }
    }

    // lookup as object
    objectTerms.forEach((term) => results.push(...Search.performObjectSearch(term, objectTerms)))

    // lookup as search terms in fulltext
    results.push(...Search.performTermsSearch(searchTerms, excludedTerms))

    // let the scorer override scores with a custom scoring function
    if (Scorer.score) results.forEach((item) => (item[4] = Scorer.score(item)))

    // now sort the results by score (in opposite order of appearance, since the
    // display function below uses pop() to retrieve items) and then
    // alphabetically
    results.sort((a, b) => {
      const leftScore = a[4]
      const rightScore = b[4]
      if (leftScore === rightScore) {
        // same score: sort alphabetically
        const leftTitle = a[1].toLowerCase()
        const rightTitle = b[1].toLowerCase()
        if (leftTitle === rightTitle) return 0
        return leftTitle > rightTitle ? -1 : 1 // inverted is intentional
      }
      return leftScore > rightScore ? 1 : -1
    })

    // remove duplicate search results
    // note the reversing of results, so that in the case of duplicates, the highest-scoring entry is kept
    let seen = new Set()
    results = results.reverse().reduce((acc, result) => {
      let resultStr = result
        .slice(0, 4)
        .concat([result[5]])
        .map((v) => String(v))
        .join(',')
      if (!seen.has(resultStr)) {
        acc.push(result)
        seen.add(resultStr)
      }
      return acc
    }, [])

    // for debugging
    // Search.lastresults = results.slice() // a copy
    // console.info('search results:')
    // console.info(Search.lastresults)

    // We add the search query terms to the searchTerms set object so
    // so we can use the terms when generating the search summary.
    splitQuery(query.trim()).forEach((queryTerm) => {
      searchTerms.add(queryTerm.toLowerCase())
    })
    return [results, searchTerms, highlightTerms]
  },

  /**
   * search for object names
   */
  performObjectSearch: (object, objectTerms) => {
    const filenames = Search._index.filenames
    const docNames = Search._index.docnames
    const objects = Search._index.objects
    const objNames = Search._index.objnames
    const titles = Search._index.titles
    const docHTMLs = Search._index.dochtmls

    const results = []

    const objectSearchCallback = (prefix, match) => {
      const name = match[4]
      const fullname = (prefix ? prefix + '.' : '') + name
      const fullnameLower = fullname.toLowerCase()
      if (fullnameLower.indexOf(object) < 0) return

      let score = 0
      const parts = fullnameLower.split('.')

      // check for different match types: exact matches of full name or
      // "last name" (i.e. last dotted part)
      if (fullnameLower === object || parts.slice(-1)[0] === object) score += Scorer.objNameMatch
      else if (parts.slice(-1)[0].indexOf(object) > -1) score += Scorer.objPartialMatch // matches in last name

      const objName = objNames[match[1]][2]
      const title = titles[match[0]]

      // If more than one term searched for, we require other words to be
      // found in the name/title/description
      const otherTerms = new Set(objectTerms)
      otherTerms.delete(object)
      if (otherTerms.size > 0) {
        const haystack = `${prefix} ${name} ${objName} ${title}`.toLowerCase()
        if ([...otherTerms].some((otherTerm) => haystack.indexOf(otherTerm) < 0)) return
      }

      let anchor = match[3]
      if (anchor === '') anchor = fullname
      else if (anchor === '-') anchor = objNames[match[1]][1] + '-' + fullname

      const descr = objName + _(', in ') + title

      // add custom score for some objects according to scorer
      if (Scorer.objPrio.hasOwnProperty(match[2])) score += Scorer.objPrio[match[2]]
      else score += Scorer.objPrioDefault

      results.push([
        docNames[match[0]],
        fullname,
        '#' + anchor,
        descr,
        score,
        filenames[match[0]],
        docHTMLs[docNames[match[0]]],
        Search._project_info,
      ])
    }
    Object.keys(objects).forEach((prefix) =>
      objects[prefix].forEach((array) => objectSearchCallback(prefix, array))
    )
    return results
  },

  /**
   * search for full-text terms in the index
   */
  performTermsSearch: (searchTerms, excludedTerms) => {
    // prepare search
    const terms = Search._index.terms
    const titleTerms = Search._index.titleterms
    const filenames = Search._index.filenames
    const docNames = Search._index.docnames
    const titles = Search._index.titles
    const docHTMLs = Search._index.dochtmls

    const scoreMap = new Map()
    const fileMap = new Map()

    // perform the search on the required terms
    searchTerms.forEach((word) => {
      const files = []
      const arr = [
        { files: terms[word], score: Scorer.term },
        { files: titleTerms[word], score: Scorer.title },
      ]
      // add support for partial matches
      if (word.length > 2) {
        const escapedWord = _escapeRegExp(word)
        Object.keys(terms).forEach((term) => {
          if (term.match(escapedWord) && !terms[word])
            arr.push({ files: terms[term], score: Scorer.partialTerm })
        })
        Object.keys(titleTerms).forEach((term) => {
          if (term.match(escapedWord) && !titleTerms[word])
            arr.push({ files: titleTerms[word], score: Scorer.partialTitle })
        })
      }

      // no match but word was a required one
      if (arr.every((record) => record.files === undefined)) return

      // found search word in contents
      arr.forEach((record) => {
        if (record.files === undefined) return

        let recordFiles = record.files
        if (recordFiles.length === undefined) recordFiles = [recordFiles]
        files.push(...recordFiles)

        // set score for the word in each file
        recordFiles.forEach((file) => {
          if (!scoreMap.has(file)) scoreMap.set(file, {})
          scoreMap.get(file)[word] = record.score
        })
      })

      // create the mapping
      files.forEach((file) => {
        if (fileMap.has(file) && fileMap.get(file).indexOf(word) === -1)
          fileMap.get(file).push(word)
        else fileMap.set(file, [word])
      })
    })

    // now check if the files don't contain excluded terms
    const results = []
    for (const [file, wordList] of fileMap) {
      // check if all requirements are matched

      // as search terms with length < 3 are discarded
      const filteredTermCount = [...searchTerms].filter((term) => term.length > 2).length
      if (wordList.length !== searchTerms.size && wordList.length !== filteredTermCount) continue

      // ensure that none of the excluded terms is in the search result
      if (
        [...excludedTerms].some(
          (term) =>
            terms[term] === file ||
            titleTerms[term] === file ||
            (terms[term] || []).includes(file) ||
            (titleTerms[term] || []).includes(file)
        )
      )
        break

      // select one (max) score for the file.
      const score = Math.max(...wordList.map((w) => scoreMap.get(file)[w]))
      // add result to the result list
      results.push([
        docNames[file],
        titles[file],
        '',
        null,
        score,
        filenames[file],
        docHTMLs[docNames[file]],
        Search._project_info,
      ])
    }
    return results
  },
}

/** Assign the “Search” module to the “window” object as “SphinxSearch”, to make it globally accessible. */
window.SphinxSearch = Search

/** Assign the “_highlightText” module to the “window” object as “SearchHighlighter”, to make it globally accessible. */
window.SearchHighlighter = _highlightText
