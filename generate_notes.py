import os
from dataclasses import dataclass
from typing import Literal, List


HoleState = Literal["closed", "half", "open"]

DIGIT_TO_STATE: dict[str, HoleState] = {
    "0": "open",
    "1": "half",
    "2": "closed",
}


@dataclass(frozen=True)
class Fingering:
    """State of 6 holes: 4 верхних слева направо, затем 2 нижних слева направо."""

    holes: List[HoleState]

    def to_svg(self, title: str) -> str:
        # Базовая геометрия — ближе к тому, что на бумажной схеме
        size = 90
        outer_r = 28
        main_r = 6      # 4 больших отверстия в круге
        thumb_r = 6     # 2 нижних отверстия такого же размера

        # Координаты: 4 основных отверстия внутри круга (квадратом),
        # затем 2 нижних отверстия снаружи круга, как на фотографии.
        main_coords = [
            (35, 28),  # верхнее левое
            (55, 28),  # верхнее правое
            (35, 48),  # нижнее левое
            (55, 48),  # нижнее правое
        ]
        thumb_coords = [
            (30, 70),
            (60, 70),
        ]
        coords = main_coords + thumb_coords

        def hole_svg(x: int, y: int, state: HoleState, r: float) -> str:
            if state == "closed":
                return f'<circle cx="{x}" cy="{y}" r="{r}" fill="black" />'
            if state == "open":
                return (
                    f'<circle cx="{x}" cy="{y}" r="{r}" '
                    f'fill="white" stroke="black" stroke-width="1.5" />'
                )
            # half-open: правая половина чёрная, левая белая
            return (
                f'<defs>'
                f'  <clipPath id="half-{x}-{y}">'
                f'    <rect x="{x}" y="{y - r}" '
                f'          width="{r}" height="{2 * r}" />'
                f'  </clipPath>'
                f'</defs>'
                f'<circle cx="{x}" cy="{y}" r="{r}" '
                f'fill="white" stroke="black" stroke-width="1.5" />'
                f'<circle cx="{x}" cy="{y}" r="{r}" '
                f'fill="black" clip-path="url(#half-{x}-{y})" />'
            )

        def radius_for_index(idx: int) -> float:
            # Базовый радиус: 4 верхних — main_r, 2 нижних — thumb_r
            base = main_r if idx < 4 else thumb_r
            # Правый верхний (второе основное отверстие) — на 20% меньше
            if idx == 1:
                return base * 0.8
            # Правый второй сверху внутри круга (правое нижнее из основных) — на 10% меньше
            if idx == 3:
                return base * 0.9
            return base

        holes_svg = "\n  ".join(
            hole_svg(x, y, state, radius_for_index(idx))
            for idx, ((x, y), state) in enumerate(zip(coords, self.holes))
        )

        label = NOTE_LABELS.get(title, title)

        return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 {size} {size}">
  <title>{title}</title>
  <circle cx="45" cy="40" r="{outer_r}" fill="#f26522" stroke="black" stroke-width="2" />
  {holes_svg}
  <text x="45" y="85" text-anchor="middle" font-family="sans-serif" font-size="12">{label}</text>
</svg>
"""


# Карта аппликатур по порядку нот инструмента.
# Ключи одновременно служат именами файлов SVG.
# Порядок отверстий: 4 верхних (слева направо), затем 2 нижних (слева направо).
# Цифры: 0 — открыто, 1 — полуоткрыто, 2 — закрыто.
NOTE_FINGERINGS: dict[str, str] = {
    # Первая «октава»
    "do": "222222",
    "do+": "212222",
    "re": "202222",
    "re+": "222122",
    "re-": "212222",  # то же, что до♯
    "mi": "222022",
    "mi-": "222122",
    "fa": "202022",
    "fa+": "022222",
    "sol": "002222",
    "sol+": "022022",
    "sol-": "022222",
    "la": "002022",
    "la+": "000222",
    "la-": "022022",
    "si": "020022",
    "si-": "000222",
    # Верхние ноты
    "2do": "000022",
    "2do+": "020002",
    "2re": "000002",
    "2re+": "020000",
    "2re-": "020002",
    "2mi": "000000",
    "2mi-": "020000",
}

NOTE_LABELS: dict[str, str] = {
    "do": "до",
    "do+": "до♯",
    "re": "ре",
    "re+": "ре♯",
    "re-": "ре♭",
    "mi": "ми",
    "mi-": "ми♭",
    "fa": "фа",
    "fa+": "фа♯",
    "sol": "соль",
    "sol+": "соль♯",
    "sol-": "соль♭",
    "la": "ля",
    "la+": "ля♯",
    "la-": "ля♭",
    "si": "си",
    "si-": "си♭",
    "2do": "до",
    "2do+": "до♯",
    "2re": "ре",
    "2re+": "ре♯",
    "2re-": "ре♭",
    "2mi": "ми",
    "2mi-": "ми♭",
}


def main() -> None:
    notes_dir = os.path.join(os.path.dirname(__file__), "notes")
    os.makedirs(notes_dir, exist_ok=True)

    for note_name, pattern in NOTE_FINGERINGS.items():
        fingering = Fingering([DIGIT_TO_STATE[d] for d in pattern])
        svg = fingering.to_svg(title=note_name)
        path = os.path.join(notes_dir, f"{note_name}.svg")
        with open(path, "w", encoding="utf-8") as f:
            f.write(svg)


if __name__ == "__main__":
    main()


