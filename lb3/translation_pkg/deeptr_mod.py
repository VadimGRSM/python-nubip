import os
from deep_translator import GoogleTranslator
from langdetect import detect_langs

def _supported_langs_dict():
    return GoogleTranslator().get_supported_languages(as_dict=True)

def _normalize_lang(lang: str):
    if not isinstance(lang, str):
        return None
    s = lang.strip()
    if not s:
        return None

    low = s.lower()
    if low == "auto":
        return "auto"

    d = _supported_langs_dict()

    if low in d:
        return d[low]

    if low in d.values():
        return low

    return None

def TransLate(text: str, scr: str, dest: str) -> str:
    try:
        src = _normalize_lang(scr)
        dst = _normalize_lang(dest)

        if src is None:
            return "Помилка перекладу: невідома мова джерела"
        if dst is None or dst == "auto":
            return "Помилка перекладу: невідома мова перекладу"

        translator = GoogleTranslator(source=src, target=dst)
        return translator.translate(text)
    except Exception as e:
        return f"Помилка перекладу: {e}"

def LangDetect(text: str, set: str = "all") -> str:
    try:
        probs = detect_langs(text)
        best = probs[0]
        lang = best.lang
        conf = float(best.prob)

        mode = (set or "all").strip().lower()
        if mode == "lang":
            return str(lang)
        if mode == "confidence":
            return str(conf)
        return f"Detected(lang={lang}, confidence={conf})"
    except Exception as e:
        return f"Помилка визначення мови: {e}"

def CodeLang(lang: str) -> str:
    if not isinstance(lang, str) or not lang.strip():
        return "Помилка: порожнє значення мови"

    s = lang.strip().lower()
    d = _supported_langs_dict()

    if s in d:
        return d[s]

    if s in d.values():
        for name, code in d.items():
            if code == s:
                return name.title()

    return "Помилка: мову не знайдено"

def LanguageList(out: str = "screen", text: str | None = None) -> str:
    try:
        limit_env = os.getenv("LANG_LIST_LIMIT")
        limit = int(limit_env) if limit_env and limit_env.isdigit() else None

        d = _supported_langs_dict()
        items = list(d.items())
        if limit:
            items = items[:limit]

        rows = []
        for i, (name, code) in enumerate(items, start=1):
            translated = ""
            if text:
                try:
                    translated = GoogleTranslator(source="auto", target=code).translate(text)
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
            with open("languages_deeptr.txt", "w", encoding="utf-8") as f:
                f.write(result)
            return "Ok"
        else:
            print(result)
            return "Ok"
    except Exception as e:
        return f"Помилка: {e}"
