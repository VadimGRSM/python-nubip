import os
import sys
from googletrans import Translator, LANGUAGES

_translator = Translator()

def _check_py() -> str | None:
    if sys.version_info >= (3, 13):
        return "Помилка: модуль gtrans3 призначений для Python 3.12 або нижче. Запустіть gtrans3.py у Docker."
    return None

def _normalize_lang(lang: str):
    if not isinstance(lang, str):
        return None
    s = lang.strip()
    if not s:
        return None

    low = s.lower()
    if low == "auto":
        return "auto"
    if low in LANGUAGES:
        return low
    for code, name in LANGUAGES.items():
        if name.lower() == low:
            return code
    return None

def TransLate(text: str, scr: str, dest: str) -> str:
    err = _check_py()
    if err:
        return err
    try:
        src_code = _normalize_lang(scr)
        dest_code = _normalize_lang(dest)
        if src_code is None:
            return "Помилка перекладу: невідома мова джерела"
        if dest_code is None or dest_code == "auto":
            return "Помилка перекладу: невідома мова перекладу"

        res = _translator.translate(text, src=src_code, dest=dest_code)
        return res.text
    except Exception as e:
        return f"Помилка перекладу: {e}"

def LangDetect(text: str, set: str = "all") -> str:
    err = _check_py()
    if err:
        return err
    try:
        res = _translator.detect(text)
        lang = getattr(res, "lang", None)
        conf = getattr(res, "confidence", None)

        mode = (set or "all").strip().lower()
        if mode == "lang":
            return str(lang)
        if mode == "confidence":
            return str(conf)
        return f"Detected(lang={lang}, confidence={conf})"
    except Exception as e:
        return f"Помилка визначення мови: {e}"

def CodeLang(lang: str) -> str:
    err = _check_py()
    if err:
        return err
    if not isinstance(lang, str) or not lang.strip():
        return "Помилка: порожнє значення мови"

    s = lang.strip()
    low = s.lower()

    if low in LANGUAGES:
        return LANGUAGES[low].title()

    for code, name in LANGUAGES.items():
        if name.lower() == low:
            return code

    return "Помилка: мову не знайдено"

def LanguageList(out: str = "screen", text: str | None = None) -> str:
    err = _check_py()
    if err:
        return err
    try:
        limit_env = os.getenv("LANG_LIST_LIMIT")
        limit = int(limit_env) if limit_env and limit_env.isdigit() else None

        rows = []
        items = list(LANGUAGES.items())
        if limit:
            items = items[:limit]

        for i, (code, name) in enumerate(items, start=1):
            translated = ""
            if text:
                try:
                    tr = _translator.translate(text, dest=code, src="auto")
                    translated = getattr(tr, "text", "")
                except Exception:
                    translated = "-"
            rows.append((i, name.title(), code, translated))

        header = ["№", "Language", "Code"] + (["Translation"] if text else [])
        widths = [4, 20, 8] + ([40] if text else [])

        def fmt_row(cols):
            parts = []
            for val, w in zip(cols, widths):
                parts.append(str(val)[:w].ljust(w))
            return " ".join(parts).rstrip()

        lines = [fmt_row(header), fmt_row(["-"*3, "-"*18, "-"*4] + (["-"*11] if text else []))]
        for r in rows:
            cols = [r[0], r[1], r[2]] + ([r[3]] if text else [])
            lines.append(fmt_row(cols))

        result = "\n".join(lines)

        mode = (out or "screen").strip().lower()
        if mode == "file":
            with open("languages_gtrans3.txt", "w", encoding="utf-8") as f:
                f.write(result)
            return "Ok"
        else:
            print(result)
            return "Ok"
    except Exception as e:
        return f"Помилка: {e}"
