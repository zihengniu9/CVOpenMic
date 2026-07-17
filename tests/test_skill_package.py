"""Repository-level checks for the installable CVOpenMic skill."""

from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = ROOT / "skills" / "cvopenmic"


class SkillPackageTests(unittest.TestCase):
    def test_required_files_exist(self):
        for relative in (
            "SKILL.md",
            "agents/openai.yaml",
            "references/rubric.md",
        ):
            self.assertTrue((SKILL_DIR / relative).is_file(), relative)

    def test_frontmatter_and_name_are_valid(self):
        content = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        match = re.match(r"\A---\n(.*?)\n---\n", content, re.DOTALL)
        self.assertIsNotNone(match)
        frontmatter = match.group(1)
        self.assertRegex(frontmatter, r"(?m)^name: cvopenmic$")
        description = re.search(r"(?m)^description: (.+)$", frontmatter)
        self.assertIsNotNone(description)
        self.assertIn("resume", description.group(1).lower())

    def test_ui_prompt_invokes_the_skill(self):
        metadata = (SKILL_DIR / "agents" / "openai.yaml").read_text(
            encoding="utf-8"
        )
        self.assertIn("$cvopenmic", metadata)

    def test_rubric_totals_one_hundred(self):
        rubric = (SKILL_DIR / "references" / "rubric.md").read_text(
            encoding="utf-8"
        )
        maxima = [int(value) for value in re.findall(r"\| (\d+) \|", rubric)]
        self.assertEqual(sum(maxima[:5]), 100)


if __name__ == "__main__":
    unittest.main()
