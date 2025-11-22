import argparse
import pathlib
import re

NOTE_FILES = {
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
    "2do": "notes/2do.svg",
    "2do+": "notes/2do+.svg",
    "2re-": "notes/2re-.svg",
    "2re": "notes/2re.svg",
    "2re+": "notes/2re+.svg",
    "2mi-": "notes/2mi-.svg",
    "2mi": "notes/2mi.svg",
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
        (?:2)?{NOTE_WORD}(?:2)?
        |
        [A-GH]
    )
    ([+#♯b♭-]?)
    {RIGHT_BOUNDARY}
    """,
    re.IGNORECASE | re.VERBOSE,
)


def normalize(note: str, accidental: str) -> str:
    token = note
    acc = accidental
    acc = acc.replace("#", "+").replace("♯", "+").replace("b", "-").replace("♭", "-")

    octave = ""
    core = token
    if core.lower().startswith("2"):
        octave = "2"
        core = core[1:]
    elif core.lower().endswith("2"):
        octave = "2"
        core = core[:-1]

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
    key = key.replace("do", "do").replace("sol", "sol")
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


