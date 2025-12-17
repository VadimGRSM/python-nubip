import json
import os
import re
import importlib

def _count_words(text: str) -> int:
    return len([w for w in re.split(r"\s+", text.strip()) if w])

def _count_sentences(text: str) -> int:
    parts = re.split(r"[.!?…]+", text.strip())
    return len([p for p in parts if p.strip()])

def _read_limited_text(path: str, max_chars: int, max_words: int, max_sentences: int) -> str:
    buffer = []
    chars = words = sentences = 0

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if not line:
                break

            buffer.append(line)
            chunk = "".join(buffer)

            chars = len(chunk)
            words = _count_words(chunk)
            sentences = _count_sentences(chunk)

            if chars >= max_chars or words >= max_words or sentences >= max_sentences:
                break

    text = "".join(buffer)
    return text[:max_chars]

def main():
    cfg_path = "config.json"
    if not os.path.exists(cfg_path):
        print("Помилка: конфігураційний файл config.json не знайдено")
        return

    with open(cfg_path, "r", encoding="utf-8") as f:
        cfg = json.load(f)

    input_file = cfg.get("input_file")
    dest_lang = cfg.get("dest_lang")
    module_name = cfg.get("module")
    output_mode = (cfg.get("output") or "screen").lower()

    max_chars = int(cfg.get("max_chars", 1000))
    max_words = int(cfg.get("max_words", 200))
    max_sentences = int(cfg.get("max_sentences", 10))

    if not input_file or not os.path.exists(input_file):
        print(f"Помилка: файл '{input_file}' не знайдено")
        return

    full_text = open(input_file, "r", encoding="utf-8").read()
    file_size = os.path.getsize(input_file)

    print("Файл:", input_file)
    print("Розмір (байт):", file_size)
    print("Кількість символів:", len(full_text))
    print("Кількість слів:", _count_words(full_text))
    print("Кількість речень:", _count_sentences(full_text))

    try:
        mod = importlib.import_module(f"translation_pkg.{module_name}")
    except Exception as e:
        print("Помилка: не вдалося імпортувати модуль пакету:", e)
        return

    print("Мова тексту:", mod.LangDetect(full_text, "all"))

    limited_text = _read_limited_text(input_file, max_chars, max_words, max_sentences)
    translated = mod.TransLate(limited_text, "auto", dest_lang)

    dest_code = mod.CodeLang(dest_lang)
    if dest_code.startswith("Помилка"):
        dest_code = (dest_lang or "").lower()

    if output_mode == "screen":
        print("\nМова перекладу:", dest_lang)
        print("Модуль:", module_name)
        print("Переклад:")
        print(translated)
    else:
        base, ext = os.path.splitext(input_file)
        out_file = f"{base}_{dest_code}{ext or '.txt'}"
        with open(out_file, "w", encoding="utf-8") as f:
            f.write(translated)
        print("Ok")

if __name__ == "__main__":
    main()
