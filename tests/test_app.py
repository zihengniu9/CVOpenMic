from __future__ import annotations

import unittest
from pathlib import Path
from unittest.mock import patch

from streamlit.testing.v1 import AppTest


ROOT = Path(__file__).resolve().parents[1]


def _analysis_result() -> dict:
    return {
        "mode": "quick",
        "tone": "direct",
        "score": 65,
        "dimensions": {
            "keywords": 21,
            "structure": 13,
            "content": 14,
            "quantification": 7,
            "professionalism": 10,
        },
        "verdict": "信息基本完整，但成果证据不足。",
        "strengths": ["时间线清楚"],
        "issues": [
            {
                "severity": "high",
                "title": "成果不具体",
                "evidence": "多处只描述负责事项",
                "suggestion": "补充项目规模和可核验结果",
            }
        ],
        "fact_questions": ["代表项目的规模是多少？"],
        "matched_keywords": [],
        "missing_keywords": [],
        "roast": "## 重点问题\n\n成果表达缺少证据。",
    }


class AppSmokeTests(unittest.TestCase):
    def test_upload_analyze_rewrite_and_new_file_reset(self):
        sample_a = (
            "张三\n邮箱 foo@example.com\n产品经理\n"
            "负责需求分析、跨团队协作和版本上线，参与多个产品项目并持续复盘。"
        ).encode("utf-8")
        sample_b = (
            "李四\n数据分析师\n负责报表建设、指标治理和业务复盘，支持多个团队完成经营分析；"
            "持续维护核心指标口径，协同业务团队定位异常，并沉淀周期性分析方法。"
        ).encode("utf-8")

        with patch("engine.analyze_resume", return_value=_analysis_result()), patch(
            "engine.rewrite_resume",
            return_value="# 张三\n\n## 工作经历\n\n- 负责需求分析与版本上线",
        ):
            app = AppTest.from_file(str(ROOT / "app.py"), default_timeout=30).run()
            self.assertFalse(app.exception)

            app.get("file_uploader")[0].upload(
                "resume-a.txt", sample_a, "text/plain"
            ).run(timeout=30)
            self.assertFalse(app.exception)

            analyze_button = next(
                button for button in app.button if button.label == "开始简历体检"
            )
            analyze_button.click().run(timeout=30)
            self.assertFalse(app.exception)
            self.assertTrue(
                any(button.label == "生成事实可信的优化版" for button in app.button)
            )

            rewrite_button = next(
                button
                for button in app.button
                if button.label == "生成事实可信的优化版"
            )
            rewrite_button.click().run(timeout=30)
            self.assertFalse(app.exception)
            self.assertEqual(len(app.get("download_button")), 2)

            app.get("file_uploader")[0].upload(
                "resume-b.txt", sample_b, "text/plain"
            ).run(timeout=30)
            self.assertFalse(app.exception)
            self.assertFalse(
                any(button.label == "生成事实可信的优化版" for button in app.button)
            )


if __name__ == "__main__":
    unittest.main()
