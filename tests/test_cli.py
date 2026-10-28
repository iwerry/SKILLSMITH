import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from skillsmith.__main__ import create, validate, metadata, warnings, audit, count_tests

ROOT = Path(__file__).resolve().parent.parent

def write(folder, header, body="# T\n\n## Examples\n- Input: x -> y\n"):
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "SKILL.md").write_text(f"---\n{header}\n---\n{body}", encoding="utf-8")
    return folder

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

    def test_not_for_and_evals(self):
        with tempfile.TemporaryDirectory() as tmp:
            create(SimpleNamespace(name="shot-list", purpose="Creates shot lists", when="the user asks for a shot list",
                                   not_for="equipment shopping", output=tmp))
            folder = Path(tmp) / "shot-list"
            self.assertIn("Do not use for equipment shopping", metadata(folder)[0]["description"])
            self.assertTrue((folder / "evals" / "tests.yaml").is_file())
            self.assertEqual((1, 1, 1), count_tests(folder))

    def test_description_angle_brackets(self):
        with tempfile.TemporaryDirectory() as tmp:
            f = write(Path(tmp) / "bad-desc", "name: bad-desc\ndescription: Use when <html> is needed.")
            self.assertIn("Description must not contain < or >", validate(f))

    def test_brand_name(self):
        with tempfile.TemporaryDirectory() as tmp:
            f = write(Path(tmp) / "claude-helper", "name: claude-helper\ndescription: Use when needed.")
            self.assertTrue(any("AI product" in i for i in validate(f)))

    def test_missing_reference(self):
        with tempfile.TemporaryDirectory() as tmp:
            f = write(Path(tmp) / "refs", "name: refs\ndescription: Use when needed.", "# T\nRead `references/guide.md` first.\n")
            self.assertIn("Referenced file not found: references/guide.md", validate(f))
            (f / "references").mkdir()
            (f / "references" / "guide.md").write_text("ok", encoding="utf-8")
            self.assertEqual([], validate(f))

    def test_secret_in_support_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            f = write(Path(tmp) / "leak", "name: leak\ndescription: Use when needed.")
            (f / "scripts").mkdir()
            (f / "scripts" / "run.py").write_text("API_KEY = 'abcdefghijklmnop1234'\n", encoding="utf-8")
            self.assertTrue(any("credential" in i for i in validate(f)))

    def test_warnings(self):
        with tempfile.TemporaryDirectory() as tmp:
            f = write(Path(tmp) / "thin", "name: thin\ndescription: Helps with reports.")
            w = warnings(f)
            self.assertIn("Description does not say when to use the skill", w)
            self.assertIn("Description has no negative boundary", w)

    def test_bundled_creator_is_ready(self):
        report = audit(ROOT / "skill-smith")
        self.assertEqual([], report["static_issues"])
        self.assertTrue(report["ready"], report)

if __name__ == "__main__":
    unittest.main()
