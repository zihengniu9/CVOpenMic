"""Repository-level checks for the installable CVOpenMic skill."""

from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = ROOT / "skills" / "cvopenmic"


class SkillPackageTests(unittest.TestCase):
    def test_private_runtime_artifacts_are_excluded_from_publish_contexts(self):
        gitignore = (ROOT / ".gitignore").read_text(encoding="utf-8")
        dockerignore = (ROOT / ".dockerignore").read_text(encoding="utf-8")
        self.assertIn("output/", gitignore)
        self.assertIn("output", dockerignore)
        self.assertIn(".streamlit/secrets.toml", dockerignore)

    def test_required_files_exist(self):
        for relative in (
            "SKILL.md",
            "agents/openai.yaml",
            "references/rubric.md",
            "references/bazi-career.md",
            "references/resume-patterns.md",
            "references/cv-architecture.md",
            "references/word-layout.md",
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

    def test_readme_defaults_to_cross_agent_install(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("# 把经历说成人话，把优势写成证据。", readme)
        self.assertIn("简历开麦 · 先提炼，再开麦", readme)
        self.assertIn("30 秒开麦", readme)
        self.assertIn("https://github.com/zihengniu9/CVOpenMic", readme)
        self.assertIn(
            "npx skills add zihengniu9/CVOpenMic --skill cvopenmic -g\n",
            readme,
        )
        self.assertIn("-a codex", readme)
        self.assertIn("-a claude-code", readme)
        self.assertIn("-a cursor", readme)
        self.assertIn("~/.workbuddy/skills/cvopenmic/", readme)
        self.assertNotIn("如果同时安装", readme)

    def test_readme_visuals_are_repository_native(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        for relative in (
            "assets/brand-hero.svg",
            "assets/modules.svg",
        ):
            self.assertTrue((ROOT / relative).is_file(), relative)
            self.assertIn(relative, readme)
        for removed in (
            "assets/workflow.svg",
            "assets/framework.svg",
            "assets/bazi-lens.svg",
            "assets/cvopenmic-hero.webp",
        ):
            self.assertNotIn(removed, readme)
            self.assertFalse((ROOT / removed).exists(), removed)
        self.assertTrue((ROOT / "assets/hero-scene.png").is_file())
        hero = (ROOT / "assets/brand-hero.svg").read_text(encoding="utf-8")
        self.assertIn('href="hero-scene.png"', hero)
        self.assertEqual(readme.count('<img src="assets/'), 2)
        self.assertIn("八字职业镜像", readme)

    def test_readme_visuals_are_self_contained_and_safe(self):
        for asset in (
            "brand-hero.svg",
            "modules.svg",
        ):
            svg = (ROOT / "assets" / asset).read_text(encoding="utf-8")
            for banned in (
                "<foreignObject",
                "<script",
                "<iframe",
                "<animate",
                'href="http',
                "xlink:href",
            ):
                self.assertNotIn(banned, svg, f"{asset}: {banned}")
            self.assertIn("viewBox=", svg)

    def test_modules_visual_keeps_the_clear_seven_module_structure(self):
        modules = (ROOT / "assets" / "modules.svg").read_text(encoding="utf-8")
        for title in (
            "材料解析与隐私",
            "目标岗位路由",
            "证据账本与评分",
            "毒舌开麦诊断",
            "事实安全改写",
            "Word / PDF 交付",
            "八字职业镜像",
        ):
            self.assertIn(title, modules)
        for boundary in (
            "可选模块",
            "不进评分",
            "不写入简历",
            "不用于录用判断",
        ):
            self.assertIn(boundary, modules)

    def test_rubric_totals_one_hundred(self):
        rubric = (SKILL_DIR / "references" / "rubric.md").read_text(
            encoding="utf-8"
        )
        maxima = [int(value) for value in re.findall(r"\| (\d+) \|", rubric)]
        self.assertEqual(sum(maxima[:5]), 100)

    def test_bazi_module_is_optional_and_non_decisional(self):
        skill = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        bridge = (SKILL_DIR / "references" / "bazi-career.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("explicit opt-in", skill)
        self.assertIn("Do not let it affect", skill)
        self.assertIn("相合信号 / 待验证 / 存在张力", bridge)
        self.assertIn("八字职业镜像", skill)
        self.assertIn("Do not use birth information", bridge)

    def test_bazi_module_is_self_contained_and_minimal(self):
        skill = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        bridge = (SKILL_DIR / "references" / "bazi-career.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("Keep CVOpenMic self-contained", skill)
        self.assertIn("Do not ask the user to install or invoke another skill", skill)
        self.assertIn("Gregorian birth date, local birth time, and birth city", bridge)
        self.assertIn("Gender is unnecessary", bridge)
        self.assertNotIn("birth time, gender", skill)
        self.assertIn("does not require that skill at runtime", bridge)
        self.assertNotIn("ask the user to install", bridge)

    def test_role_routing_covers_distinct_resume_families(self):
        patterns = (SKILL_DIR / "references" / "resume-patterns.md").read_text(
            encoding="utf-8"
        )
        for family in (
            "Backend",
            "Frontend",
            "Mobile or client",
            "Data or machine learning",
            "Infrastructure, SRE, or security",
            "Architecture or technical leadership",
            "Product, design, or operations",
            "AI product or AI strategy",
        ):
            self.assertIn(family, patterns)
        self.assertIn("Use scope and demonstrated ownership, not years alone", patterns)
        self.assertIn("API calls", patterns)
        self.assertIn("user problem → product hypothesis", patterns)

    def test_bullet_patterns_require_source_evidence_or_placeholders(self):
        patterns = (SKILL_DIR / "references" / "resume-patterns.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("真实结果或占位符", patterns)
        self.assertIn("Never copy example numbers", patterns)
        self.assertIn("Do not manufacture a performance improvement", patterns)
        self.assertIn("Do not convert coursework into employment", patterns)

    def test_delivery_checklist_preserves_fact_safety(self):
        skill = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        patterns = (SKILL_DIR / "references" / "resume-patterns.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("references/resume-patterns.md", skill)
        self.assertIn("Run the delivery checklist", skill)
        self.assertIn("no new number, award, tool, credential", patterns)
        self.assertIn("universal one-page rule", patterns)

    def test_complete_cv_preserves_education_and_work_history(self):
        skill = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        architecture = (SKILL_DIR / "references" / "cv-architecture.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("references/cv-architecture.md", skill)
        self.assertIn("every source education entry and work entry", skill)
        self.assertIn("New graduate or early career", architecture)
        self.assertIn("AI strategy or AI product, early career", architecture)
        self.assertIn("retain every employer and internship entry", architecture)
        self.assertIn("remove an entire education or work entry only with explicit user approval", architecture)
        self.assertIn("Conclusion and data first", architecture)
        self.assertIn("Two coherent pages", architecture)

    def test_render_prompt_prevents_large_unused_page_regions(self):
        skill = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        architecture = (SKILL_DIR / "references" / "cv-architecture.md").read_text(
            encoding="utf-8"
        )
        metadata = (SKILL_DIR / "agents" / "openai.yaml").read_text(
            encoding="utf-8"
        )
        self.assertIn("choose the page count from the actual content", skill)
        self.assertIn("Page count and visual density", architecture)
        self.assertIn("70–90% body-area utilization", architecture)
        self.assertIn("empty lower half as a layout failure", architecture)
        self.assertIn("Avoid forced page breaks", architecture)
        self.assertIn("no large empty lower half", metadata)

    def test_docx_is_canonical_and_pdf_is_rendered_preview(self):
        skill = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        architecture = (SKILL_DIR / "references" / "cv-architecture.md").read_text(
            encoding="utf-8"
        )
        metadata = (SKILL_DIR / "agents" / "openai.yaml").read_text(
            encoding="utf-8"
        )
        self.assertIn("editable DOCX as the canonical source", skill)
        self.assertIn("Editable delivery workflow", architecture)
        self.assertIn("Render the DOCX to PDF from the same file", architecture)
        self.assertIn("Images are previews, not the source of truth", architecture)
        self.assertIn("editable DOCX as the canonical file", metadata)

    def test_default_word_layout_matches_compact_reference_style(self):
        skill = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        layout = (SKILL_DIR / "references" / "word-layout.md").read_text(
            encoding="utf-8"
        )
        metadata = (SKILL_DIR / "agents" / "openai.yaml").read_text(
            encoding="utf-8"
        )
        self.assertIn("references/word-layout.md", skill)
        self.assertIn("black-and-white, single-column layout", layout)
        self.assertIn("bold heading followed by a thin horizontal rule", layout)
        self.assertIn("real Word bullets", layout)
        self.assertIn("Omit age, gender, and photo by default", layout)
        self.assertIn("compact black-and-white single-column Word layout", metadata)

    def test_review_answers_before_asking_questions(self):
        skill = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("Do not turn the review into an interview", skill)
        self.assertIn("Ask at most two bundled questions", skill)
        self.assertIn("answer first, verify last", skill)
        self.assertIn("核心提炼", skill)
        self.assertIn("毒舌开麦", skill)
        self.assertIn("可以这样写", skill)
        self.assertIn("do not drip-feed follow-up questions", skill)


if __name__ == "__main__":
    unittest.main()
