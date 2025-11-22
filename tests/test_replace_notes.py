import subprocess
import sys
import tempfile
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "replace_notes.py"


class ReplaceNotesCliTest(unittest.TestCase):
    def run_case(self, source: str, expected: str) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            file_path = Path(tmp) / "sample.md"
            file_path.write_text(source, encoding="utf-8")

            result = subprocess.run(
                [sys.executable, str(SCRIPT), str(file_path)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            self.assertEqual(
                result.returncode,
                0,
                msg=f"CLI failed: {result.stderr}",
            )

            content = file_path.read_text(encoding="utf-8")
            self.assertEqual(content, expected)

    def test_basic_russian_notes(self):
        self.run_case(
            "до ре ми",
            "![до](notes/do.svg) ![ре](notes/re.svg) ![ми](notes/mi.svg)",
        )

    def test_letters_and_upper_octave(self):
        self.run_case(
            "A B C# do2 re2 2ми",
            "![A](notes/la.svg) ![B](notes/si-.svg) ![C#](notes/do+.svg) "
            "![do2](notes/2do.svg) ![re2](notes/2re.svg) ![2ми](notes/2mi.svg)",
        )

    def test_mixed_with_punctuation(self):
        self.run_case(
            "ля.\nреb, 2до ре2",
            "![ля](notes/la.svg).\n![реb](notes/re-.svg), "
            "![2до](notes/2do.svg) ![ре2](notes/2re.svg)",
        )


if __name__ == "__main__":
    unittest.main()


