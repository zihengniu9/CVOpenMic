"""Dry-run contracts for evidence-safe role routing and rewrites."""

import re
import unittest


def numeric_claims(text: str) -> set[str]:
    return set(re.findall(r"(?<!\w)\d+(?:\.\d+)?%?", text))


class SkillScenarioTests(unittest.TestCase):
    def test_backend_jd_gaps_do_not_become_candidate_claims(self):
        source = "负责订单接口开发，使用 Redis。"
        jd = "后端工程师：熟悉 Spring、Redis、高并发与可观测性。"
        safe_rewrite = (
            "使用 Redis 开发订单接口，负责[补充具体职责范围]，"
            "解决[补充真实问题]并实现[补充可验证结果]。"
        )
        unproved = {"Spring", "高并发", "可观测性"}

        self.assertIn("Redis", safe_rewrite)
        for unsupported_claim in unproved:
            self.assertIn(unsupported_claim, jd)
            self.assertNotIn(unsupported_claim, safe_rewrite)
        self.assertFalse(numeric_claims(safe_rewrite) - numeric_claims(source))

    def test_coursework_is_not_promoted_to_production_experience(self):
        source = "课程项目：使用 React 开发校园活动页面。"
        safe_rewrite = (
            "课程项目｜校园活动页面：使用 React 完成[补充具体交互]，"
            "负责[补充个人贡献]，通过[补充测试或反馈]验证结果。"
        )

        self.assertIn("课程项目", safe_rewrite)
        self.assertIn("React", safe_rewrite)
        for unsupported_claim in ("生产环境", "线上用户", "性能提升", "无障碍达标"):
            self.assertNotIn(unsupported_claim, safe_rewrite)
        self.assertFalse(numeric_claims(safe_rewrite) - numeric_claims(source))


if __name__ == "__main__":
    unittest.main()
