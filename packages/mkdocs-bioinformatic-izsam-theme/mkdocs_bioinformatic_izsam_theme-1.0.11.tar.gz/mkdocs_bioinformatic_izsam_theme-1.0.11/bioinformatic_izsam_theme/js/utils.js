wiki.utils = {};

wiki.utils.postMessage = undefined;
wiki.utils.medatadata_select_nodes = ['#tree-metadata-select', '#tree-node-label-text', '#legend-menu-color-by', '#metadata-menu-color-by', '#metadata-map-select', '#legend-title-menu-color-by'];
wiki.utils.css_vars = {};


/**
 * Highlight keyword in text
 * 
 * @param {String} text text where find keyword to highlight
 * @param {String} keyword keyword to highlight
 */
wiki.utils.highlightKeyword = function(text, keyword) {
  // Create a regex to match the whole word containing the keyword
  const wordRegex = new RegExp(`\\b\\w*${keyword}\\w*\\b`, 'gi');
  
  // Replace the whole word with a span
  return text.replace(wordRegex, (match) => {
    // Create a regex to match the keyword within the word
    const keywordRegex = new RegExp(`(${keyword})`, 'gi');
    
    // Replace the keyword with a span
    const highlightedKeyword = match.replace(keywordRegex, '<span class="highlight-keyword">$&</span>');
    
    // Wrap the whole word in a span
    return `<span class="highlight-word">${highlightedKeyword}</span>`;
  });
};

/**
 * Uitility to check if an object exist and it is not empty
 * 
 */
wiki.utils.isObjectNotEmpty = function(obj) {
  // Check if the object exists and is not null or undefined
  // Then check if the object has any own properties
  return obj != null && typeof obj === 'object' && Object.keys(obj).length > 0;
}

/**
 * Utility to extract numbers for string and generate array
 * 
 * @param {String} input
 * @returns 
 */
wiki.utils.extractNumbersFromString = function(input) {
  // Use a regular expression to find all sequences of digits
  const matches = input.match(/\d+/g);
  // Convert the matched strings to numbers
  const numbers = matches ? matches.map(Number) : [];
  return numbers;
}

/**
 * Utility to extract comma separated numbers and ranges separated by `-`
 * 
 * @param {String} input 
 * @returns 
 */
wiki.utils.extractNumbersAndRanges = function(input) {
  // Split the input string by commas
  const parts = input.split(',');
  
  // Use a Set to ensure uniqueness
  const numberSet = new Set(parts.flatMap(part => {
    if (part.includes('-')) {
      // If the part is a range, split it by the hyphen to get start and end
      const [start, end] = part.split('-').map(Number);
      // Generate an array for the range and add each number to the Set
      return Array.from({ length: end - start + 1 }, (_, i) => start + i);
    } else {
      // If the part is a single number, convert it to Number and return
      return Number(part);
    }
  }));

  // Convert the Set back to an array
  return Array.from(numberSet);
}

/**
 * Set the copy right year.
 * 
 */
wiki.utils.setCopyRightYear = function() {
  let footer = document.querySelector('footer');
  if (footer) {
    let copyright = footer.querySelector('.copyright-year');
    if (copyright) {
      let year = new Date().getFullYear();
      copyright.innerHTML = year;
    }
  }
}

/**
 * Get all css variables of the document as an object
 */
wiki.utils.getAllCssVariables = function() {
  if (wiki.utils.isObjectNotEmpty(wiki.utils.css_vars)) {
    return wiki.utils.css_vars;
  }
  // Iterate through all stylesheets
  for (let stylesheet of document.styleSheets) {
    try {
      // Iterate through all rules within each stylesheet
      for (let rule of stylesheet.cssRules) {
        // Check if the rule is a CSSStyleRule and its selector is :root
        if (rule instanceof CSSStyleRule && rule.selectorText === ':root') {
          // Iterate through all CSS variables in the rule
          for (let property of rule.style) {
            if (property.startsWith('--')) {
              // Get the value of the CSS variable
              let value = rule.style.getPropertyValue(property).trim();
              // Store the variable and its value
              wiki.utils.css_vars[property] = value;
            }
          }
        }
      }
    } catch (e) {
      // Catch and log any errors (e.g., CORS issues)
      console.error("Error accessing stylesheet: ", e);
    }
  }
  return wiki.utils.css_vars;
};

window.addEventListener('message', (event) => {
  let url = new URL(window.location.href);
  let pathname = url.pathname.endsWith('/') ? url.pathname.slice(0, -1) : url.pathname;
  let domain = url.origin + pathname;

  if (event.origin === domain) {
    wiki.utils.postMessage = event.data;
  }
});

window.addEventListener('DOMContentLoaded', (event) => {
  wiki.utils.setCopyRightYear();
});