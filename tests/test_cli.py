import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from skillsmith.__main__ import create, validate, metadata

class SkillSmithTest(unittest.TestCase):
    def test_create_validate(self):
        with tempfile.TemporaryDirectory() as tmp:
            create(SimpleNamespace(name="video-production", purpose="Plans production", when="the user requests a video plan", output=tmp))
            folder = Path(tmp) / "video-production"
            self.assertEqual([], validate(folder))
            self.assertEqual("video-production", metadata(folder)[0]["name"])

    def test_reject_invalid_name(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):
                create(SimpleNamespace(name="../unsafe", purpose="Plan", when="asked", output=tmp))

    def test_directory_mismatch(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp) / "wrong"
            folder.mkdir()
            (folder / "SKILL.md").write_text("---\nname: right\ndescription: Creates reports when requested.\n---\n# Test\n", encoding="utf-8")
            self.assertTrue(validate(folder))

if __name__ == "__main__":
    unittest.main()
