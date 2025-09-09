wiki.footer = {};

wiki.footer.body = document.body;
wiki.footer.lastUpdateDate = document.getElementById("last-update-date");
wiki.footer.copyRightDate = document.getElementById("copyright-date");

wiki.footer.setCopyrightDate = function() {
  let year = new Date().getFullYear();
  wiki.footer.copyRightDate.innerHTML = year;
};

wiki.footer.setLastUpdateDate = function(date) {
  wiki.footer.lastUpdateDate.innerHTML = date;
};

wiki.footer.getMonthTranslation = function(month) {
  let languages = wiki.locales.languages;
  let language = languages.find(element => element.active);
  let code = language ? language.code : 'en';
  let translatedMonth = wiki.languages[code].months[month];
  
  return translatedMonth;
};

wiki.footer.formatDate = function(date) {
  let splittedDate = date ? date.split(" ")[0] : undefined;
  let year = splittedDate ? splittedDate.split("-")[0] : undefined;
  let month = splittedDate ? splittedDate.split("-")[1] : undefined;
  let day = splittedDate ? splittedDate.split("-")[2] : undefined;
  let tranlatedMonth = wiki.footer.getMonthTranslation(month);
  let newFormatDate = tranlatedMonth + " " + day + ", " + year;
  wiki.footer.setLastUpdateDate(newFormatDate);
};

document.addEventListener('DOMContentLoaded', function() {
  if (wiki.footer.lastUpdateDate) {
    let date = wiki.footer.lastUpdateDate.innerHTML;
    wiki.footer.formatDate(date);
  }
  if (wiki.footer.copyRightDate) {
    wiki.footer.setCopyrightDate();
  }
});