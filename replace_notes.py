import argparse
import pathlib
import re

NOTE_FILES = {
    # Нижняя октава (концертные ноты ниже центральной «до»)
    "0la": "notes/0la.svg",
    "0la+": "notes/0la+.svg",
    "0si-": "notes/0si-.svg",
    "0si": "notes/0si.svg",
    # Центральная октава
    "do": "notes/do.svg",
    "do+": "notes/do+.svg",
    "re-": "notes/re-.svg",
    "re": "notes/re.svg",
    "re+": "notes/re+.svg",
    "mi-": "notes/mi-.svg",
    "mi": "notes/mi.svg",
    "fa": "notes/fa.svg",
    "fa+": "notes/fa+.svg",
    "sol-": "notes/sol-.svg",
    "sol": "notes/sol.svg",
    "sol+": "notes/sol+.svg",
    "la-": "notes/la-.svg",
    "la": "notes/la.svg",
    "la+": "notes/la+.svg",
    "si-": "notes/si-.svg",
    "si": "notes/si.svg",
    # Верхняя октава на инструменте
    "2do": "notes/2do.svg",
    "2do+": "notes/2do+.svg",
    "2re-": "notes/2re-.svg",
    # Старые имена ступеней → тот же фингеринг по концертной высоте
    "2re": "notes/si.svg",
    "2re+": "notes/2do.svg",
    "2mi": "notes/2do+.svg",
    "2mi-": "notes/2do.svg",
}

RU_BASE = {
    "до": "do",
    "ре": "re",
    "ми": "mi",
    "фа": "fa",
    "соль": "sol",
    "сол": "sol",
    "ля": "la",
    "си": "si",
}

EN_BASE = {
    "do": "do",
    "re": "re",
    "mi": "mi",
    "fa": "fa",
    "sol": "sol",
    "la": "la",
    "si": "si",
}

LETTER_MAP = {
    "A": ("la", ""),
    "B": ("si", "-"),
    "C": ("do", ""),
    "D": ("re", ""),
    "E": ("mi", ""),
    "F": ("fa", ""),
    "G": ("sol", ""),
    "H": ("si", ""),
}

LEFT_BOUNDARY = r"(?<![^\s.,;:!?()\"'«»…-])"
RIGHT_BOUNDARY = r"(?=(?:\s|$|[.,;:!?()\"'«»…-]))"
NOTE_WORD = r"(?:до|ре|ми|фа|соль|сол|ля|си|do|re|mi|fa|sol|la|si)"

PATTERN = re.compile(
    rf"""
    {LEFT_BOUNDARY}
    (
        (?:0|2)?{NOTE_WORD}(?:0|2)?
        |
        [A-GH]
    )
    ([+#♯b♭-]?)
    {RIGHT_BOUNDARY}
    """,
    re.IGNORECASE | re.VERBOSE,
)


def _strip_octave(token: str) -> tuple[str, str]:
    """Возвращает (ядро_ноты_в_нижнем_регистре, октава '' | '0' | '2')."""
    t = token.strip()
    low = t.lower()
    if low.startswith("2"):
        return t[1:], "2"
    if low.endswith("2"):
        return t[:-1], "2"
    if low.startswith("0"):
        return t[1:], "0"
    if low.endswith("0"):
        return t[:-1], "0"
    return t, ""


def normalize(note: str, accidental: str) -> str:
    acc = accidental
    acc = acc.replace("#", "+").replace("♯", "+").replace("b", "-").replace("♭", "-")

    core, octave = _strip_octave(note)
    core = core.strip()

    default_acc = ""
    base = ""
    if core in LETTER_MAP:
        base, default_acc = LETTER_MAP[core]
    else:
        core_lower = core.lower()
        if core_lower in RU_BASE:
            base = RU_BASE[core_lower]
        elif core_lower in EN_BASE:
            base = EN_BASE[core_lower]
        else:
            return ""

    final_acc = acc if acc else default_acc
    key = (octave + base + final_acc).replace("+-", "-").replace("-+", "+")
    return NOTE_FILES.get(key, "")


def replace_notes(text: str) -> str:
    def repl(match: re.Match) -> str:
        token = match.group(1)
        acc = match.group(2)
        svg = normalize(token, acc)
        if not svg:
            return match.group(0)
        label = token + acc
        return f"![{label}]({svg})"

    return PATTERN.sub(repl, text)


def main():
    parser = argparse.ArgumentParser(
        description="Заменяет названия нот в Markdown на картинки аппликатур."
    )
    parser.add_argument("file", type=pathlib.Path, help="Markdown файл для обработки")
    args = parser.parse_args()

    content = args.file.read_text(encoding="utf-8")
    replaced = replace_notes(content)
    args.file.write_text(replaced, encoding="utf-8")


if __name__ == "__main__":
    main()
