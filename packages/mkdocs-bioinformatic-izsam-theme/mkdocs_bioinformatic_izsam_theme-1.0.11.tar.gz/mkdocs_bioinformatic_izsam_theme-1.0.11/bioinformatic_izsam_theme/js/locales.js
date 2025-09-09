wiki.locales = {};

wiki.locales.lang = undefined;

wiki.locales.languages = [];

wiki.locales.current = {};

wiki.locales.body = document.querySelector('body');
wiki.locales.languageSwitcher = document.querySelector('.tool-lang');
wiki.locales.changeLanguageLabel = document.querySelector('.tool-lang .tool-label');
wiki.locales.changeLanguageTrigger = document.querySelector('.tool-lang .tool-trigger');

wiki.locales.getActiveLanguageCode = function() {
  let languages = wiki.locales.languages;
  let language = languages.find(element => element.active);
  let code = language ? language.code : 'en';
  return code;
}

wiki.locales.getActiveLanguageTerms = function() {
  let languages = wiki.locales.languages;
  let language = languages.find(element => element.active);
  let code = language ? language.code : 'en';
  let terms = { ...wiki.languages[code]};
  Object.keys(terms).forEach(key => {
    terms[key] = terms[key];
  });
  return terms;
}

/**
 * Translate page UI with wiki.locales terms
 * 
 * @param {DOM Node} container A DOM node containing elements to translate
 */
wiki.locales.translate = function (container) {
  let languages = wiki.locales.languages;
  let language = languages.find(element => element.active);
  let code = language ? language.code : 'en';
  let terms = wiki.languages[code];
  if (wiki.locales.changeLanguageLabel) {
    wiki.locales.changeLanguageLabel.innerHTML = code;
  }
  let nodes = !container ? document.querySelectorAll('[data-i18n-key]') : container.querySelectorAll('[data-i18n-key]');
  if (nodes && nodes.length > 0) {
    nodes.forEach(element => {
      let key = element.getAttribute("data-i18n-key");
      let translation = key ? terms[key] : undefined;
      if (translation) {
        if (element.hasAttribute('placeholder')) {
          element.setAttribute('placeholder', translation);
        } else if ((element.tagName === 'IMG') && (element.hasAttribute('alt'))) {
          element.setAttribute('alt', translation);
        } else {
          element.innerHTML = translation;
        }
      }
    });
  }
}

wiki.locales.setLanguageSwitcher = function() {
  let languages = wiki.locales.languages;
  if (languages.length > 1 && wiki.locales.languageSwitcher) {
    wiki.locales.languageSwitcher.classList.remove('hidden');
  }
};

wiki.locales.setLanguagesCfg = function(lang) {
  let languages = Object.keys(wiki.languages);
  languages.forEach(langugage => {
    let obj = {};
    obj.code = wiki.languages[langugage].__code;
    obj.description = wiki.languages[langugage].__description;
    if (langugage === lang) { 
      obj.active = true;
    } else {
      obj.active = false;
    }
    wiki.locales.languages.push(obj);
  });
}

wiki.locales.setLanguage = function(lang) {
  wiki.locales.setLanguagesCfg(lang);
  wiki.locales.setLanguageSwitcher();
  wiki.locales.translate();
}

wiki.locales.changeLanguage = function(lang) {
  if (lang && !wiki.locales.lang.includes(lang)) {
    let url = new URL(window.location.href);
    let path = url.pathname;
    let langPath = '/' + lang + '/';
    let newPath = path.replace(/\/[a-z]{2}\//, langPath);
    fetch(newPath)
      .then(response => {
        if (response.status === 404) {
          newPath = path.replace(/\/[a-z]{2}\/.*/, langPath);
          window.location.href = newPath;
        } else {
          window.location.href = newPath;
        }
      })
      .catch(error => {
        console.error('Error:', error);
        newPath = path.replace(/\/[a-z]{2}\/.*/, langPath);
        window.location.href = newPath;
      });
  }
}

/**
 * 
 * Build modal
 * 
 */
wiki.locales.buildChangeLanguageModal = function() {
  let languages = wiki.locales.languages;
  let language = languages.find(element => element.active);
  let code = language ? language.code : 'en';
  let title = wiki.languages[code].change_language;
  let contents = [];
  // Build language selector
  let select_box = document.createElement('div');
  select_box.setAttribute('class', 'select-box');
  let label = document.createElement('div');
  label.setAttribute('class', 'form-label');
  label.innerHTML = '<i class="iconic iconic-globe"></i>' + wiki.languages[code].select_language;
  select_box.append(label);
  let select = document.createElement('select');
  languages.forEach(element => {    
    let option = document.createElement('option');
    option.setAttribute('value', element.code);
    option.innerHTML = element.description + ' (' + element.code.toUpperCase() + ')';
    if (element.code === code) {
      option.setAttribute('selected', 'selected');
    }
    select.append(option);
  });
  select.addEventListener('change', function(event) {
    let lang = event.target.value;
    if (lang != '') {
      wiki.locales.changeLanguage(lang);
    }
  });
  select_box.append(select);
  contents.push(select_box);
  let cfg = {
    title: title,
    contents: contents
  };
  wiki.modal.buildModal(cfg);
};

if (wiki.locales.changeLanguageTrigger) {
  wiki.locales.changeLanguageTrigger.addEventListener('click', function(e) {
    wiki.locales.buildChangeLanguageModal();
    wiki.locales.body.classList.add('show-modal');
  });
}

if (!wiki.locales.lang) {
  let lang = config_lang;
  if (lang) {
    wiki.locales.lang = lang;
  } else {
    wiki.locales.lang = 'en';
  }
  wiki.locales.setLanguage(wiki.locales.lang);
  wiki.locales.current = wiki.locales.getActiveLanguageTerms();
}