import os
import asyncio
import inspect
from googletrans import Translator, LANGUAGES

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

async def _await_if_needed(x):
    return await x if inspect.isawaitable(x) else x

async def _detect_async(text: str):
    tr = Translator(service_urls=["translate.googleapis.com"])
    res = tr.detect(text)
    return await _await_if_needed(res)

async def _translate_async(text: str, src: str, dst: str):
    tr = Translator(service_urls=["translate.googleapis.com"])
    res = tr.translate(text, src=src, dest=dst)
    res = await _await_if_needed(res)
    return getattr(res, "text", str(res))

def TransLate(text: str, scr: str, dest: str) -> str:
    try:
        src_code = _normalize_lang(scr)
        dst_code = _normalize_lang(dest)

        if src_code is None:
            return "Помилка перекладу: невідома мова джерела"
        if dst_code is None or dst_code == "auto":
            return "Помилка перекладу: невідома мова перекладу"

        return asyncio.run(_translate_async(text, src_code, dst_code))
    except Exception as e:
        return f"Помилка перекладу: {e}"

def LangDetect(text: str, set: str = "all") -> str:
    try:
        res = asyncio.run(_detect_async(text))
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
    if not isinstance(lang, str) or not lang.strip():
        return "Помилка: невідома мова"

    s = lang.strip()
    code = s.lower()

    if code in LANGUAGES:
        return LANGUAGES[code].title()

    name = s.lower()
    for c, n in LANGUAGES.items():
        if n.lower() == name:
            return c

    return "Помилка: невідома мова"

def LanguageList(out: str = "screen", text: str | None = None) -> str:
    try:
        limit_env = os.getenv("LANG_LIST_LIMIT")
        limit = int(limit_env) if limit_env and limit_env.isdigit() else None

        items = list(LANGUAGES.items())
        if limit:
            items = items[:limit]

        async def _job():
            tr = Translator(service_urls=["translate.googleapis.com"])
            rows = []
            for i, (code, name) in enumerate(items, start=1):
                translated = ""
                if text:
                    try:
                        r = tr.translate(text, src="auto", dest=code)
                        r = await _await_if_needed(r)
                        translated = getattr(r, "text", "")
                    except Exception:
                        translated = "-"
                rows.append((i, name.title(), code, translated))
            return rows

        rows = asyncio.run(_job())

        headers = ["№", "Language", "Code"] + (["Translation"] if text else [])
        data = [headers]
        for r in rows:
            if text:
                data.append([str(r[0]), r[1], r[2], r[3]])
            else:
                data.append([str(r[0]), r[1], r[2]])

        widths = [max(len(row[c]) for row in data) for c in range(len(data[0]))]

        def fmt(row):
            return "  ".join(row[i].ljust(widths[i]) for i in range(len(row)))

        lines = [fmt(data[0]), fmt(["-"*w for w in widths])]
        for row in data[1:]:
            lines.append(fmt(row))

        result = "\n".join(lines)
        mode = (out or "screen").strip().lower()

        if mode == "file":
            with open("languages_gtrans4.txt", "w", encoding="utf-8") as f:
                f.write(result)
            return "Ok"

        print(result)
        return "Ok"

    except Exception as e:
        return f"Помилка: {e}"
