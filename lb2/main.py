import asyncio
import inspect
from googletrans import Translator, LANGUAGES

def _to_code(lang: str):
    if not isinstance(lang, str) or not lang.strip():
        return None
    s = lang.strip().lower()

    if s in LANGUAGES:        # вже ISO-код
        return s

    for code, name in LANGUAGES.items():   # назва мови
        if name.lower() == s:
            return code

    return None


def TransLate(text: str, lang: str):
    try:
        dest = _to_code(lang)
        if dest is None:
            return "Помилка перекладу: невідома мова"

        # async googletrans
        if inspect.iscoroutinefunction(Translator.translate):
            async def _job():
                tr = Translator(service_urls=["translate.googleapis.com"])
                res = await tr.translate(text, dest=dest)
                return res.text
            return asyncio.run(_job())

        # sync googletrans
        tr = Translator(service_urls=["translate.googleapis.com"])
        res = tr.translate(text, dest=dest)
        return res.text

    except Exception as e:
        return f"Помилка перекладу: {e}"


def LangDetect(txt: str):
    try:
        # async googletrans
        if inspect.iscoroutinefunction(Translator.detect):
            async def _job():
                tr = Translator(service_urls=["translate.googleapis.com"])
                return await tr.detect(txt)
            res = asyncio.run(_job())
        else:
            tr = Translator(service_urls=["translate.googleapis.com"])
            res = tr.detect(txt)

        conf = getattr(res, "confidence", None)
        if conf is None:
            return f"Detected(lang={res.lang})"
        return f"Detected(lang={res.lang}, confidence={conf})"

    except Exception as e:
        return f"Помилка визначення мови: {e}"


def CodeLang(lang: str):
    if not isinstance(lang, str) or not lang.strip():
        return "Невідома мова"

    s = lang.strip()
    code = s.lower()

    if code in LANGUAGES:                 # ввели код → повертаємо назву
        return LANGUAGES[code].title()

    name = s.lower()                      # ввели назву → повертаємо код
    for c, n in LANGUAGES.items():
        if n.lower() == name:
            return c

    return "Невідома мова"


def main():
    txt = input("Введіть текст для перекладу: ").strip()
    lang = input("Введіть мову перекладу (назва або ISO-639 код): ").strip()

    print("\n" + txt)
    print(LangDetect(txt))
    print(TransLate(txt, lang))
    print(CodeLang("En"))
    print(CodeLang("English"))

if __name__ == "__main__":
    main()
