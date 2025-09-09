# mkdocs-bioinformatic-izsam-theme

This is an MkDocs theme designed to layout the documentation provided by Bioinformatic Unit of the Istituto Zooprofilattico Sperimentale dell'Abruzzo e del Molise "G. Caporale".

#### Important!

The theme is intended to work with the plugin **mkdocs-izsam-search** [https://pypi.org/project/mkdocs-izsam-search/](https://pypi.org/project/mkdocs-izsam-search/)

```bash
pip install mkdocs-izsam-search
```

## Theme customization

The theme allows you to customize platform title and footer contents by using your mdkdocs configuration file `mkdocs.yml`.

```yaml
extra:
  platform_title: Piattaforma GenPat, Wiki
  language: it
  useful_links:
    link_1:
      label: CRN Sequenze Genomiche
      url: https://www.izs.it/IZS/Eccellenza/Centri_nazionali/CRN_-_Sequenze_Genomiche
    link_2:
      label: IZSAM "G. Caporale"
      url: https://www.izs.it
  support:
    support_1:
      label: bioinformatica@izs.it
      url: mailto:bioinformatica@izs.it
    support_2:
      label: +39 0861 3321
      url: tel:+3908613321
  tools:
    tool_1:
      icon: iconic-print
      label: Versione PDF
      target: _blank
      url: https://genpat.izs.it/genpat_wiki/en/pdf/genpat_platform_wiki.pdf
  copyright: IZSAM "G. Caporale"
```

## Multi language support

The theme supports a localization system written in javascript. At the moment it supports Italian and English but it is possible to add new languages.

### Add a language

1. Create a new language file in `js/i18n` folder by using `en.js` or `it.js` as template and translate values.
2. List it in `js/languages-builder.js`
3. Pack language files in `languages.js` 

#### Pack language files

To pack files we use [**packjs**](https://www.npmjs.com/package/packjs) npm library:

```bash
npm install --save-dev packjs
```

Then from `js` folder:

```bash
  packjs i18n/languages-builder.js languages.js
```

The code will loop through the `wiki.languages` object keys and for each key, it will add an option to the language switcher. By selecting an available language, the code will redirect to the language subfolder.

The theme is designed to handle different builds for each language. Specifically, we will have the documentation in Italian hosted under `https://mywiki.eu/it`, the documentation in English under `https://mywiki.eu/en`, and so on.

> **Please note:** If you have a single language site, just remove the languages you don't need from `js/languages.js`. If you want to modify the behavior of the language switcher, you can override the `js/locales.js` file.

### Language definition

Each build relies on `config.extra.language` parameter to define the wiki language (the default is `en`), on `base.html` we set the html `lang` attribute and a global javascript constant `config_lang` with that value:

```html
<html lang="{{ config.extra.language|default('en') }}">
```

```javascript
const config_lang = "{{ config.extra.language|default('en') }}";
```

The `config.extra.language` variable is used also to set **search functionalities**. There are some limitations on the values it can assume. Allowed languages are: `ar`, `da`, `de`, `du`, `es`, `fi`, `fr`, `hi`, `hu`, `it`, `ja`, `jp`, `nl`, `no`, `pt`, `ro`, `ru`, `sv`, `ta`, `th`, `tr`, `vi`, `zh`. If you want to use a different language, you should not to use **mkdocs-izsam-search** plugin and customize the `base.html` file removing all the code related to it.

```html
{% if config.extra.language and not 'en' in config.extra.language %}
  <script src="{{ 'js/lunr-languages/lunr.stemmer.support.js'|url }}"></script>
  <script src="{{ 'js/lunr-languages/lunr.multi.js'|url }}"></script>
  {% set js_path = 'js/lunr-languages/lunr.' ~ config.extra.language ~ '.js' %}
  <script src="{{ js_path|url }}"></script>
{% endif %}
```

## Theme features

#### Use image caption

If you need to use a caption for images, you can use the markdown image title sintax.

`![](image.png "image title")`

> A function in `theme.js` loops all images and if a title exists will append a `figcaption` tag after the image.

#### Use icons inline

To use icons inline inside the contents, please add the alt attribute `inline-icon`:

```
![inline-icon](icon.png)
```

> Images will have inherent size and displayed inline.

#### Use diagram as images (no plantuml)

To use diagram inside the contents as images, please add the alt attribute `diagram` to avoid box shadow.

```
![diagram](file.png)
```

## Credits

For the icons, we are using the free [Iconic](https://iconic.app/) package, converted to a font with the [IcoMoon app](https://icomoon.io/app/#/select).