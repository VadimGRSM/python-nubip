import os
from translation_pkg.gtrans4_mod import TransLate, LangDetect, CodeLang, LanguageList

os.environ["LANG_LIST_LIMIT"] = "25"

txt = "Доброго дня. Як справи?"
print(txt)
print(LangDetect(txt, "all"))
print(TransLate(txt, "auto", "en"))
print(CodeLang("En"))
print(CodeLang("English"))

LanguageList("screen", "Добрий день")
