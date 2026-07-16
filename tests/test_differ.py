"""Diff 计算与安全 HTML 输出测试。"""

import unittest

from differ import compute_diff, diff_to_html, generate_export_markdown


class DifferTests(unittest.TestCase):
    def test_compute_diff_keeps_modified_lines_side_by_side(self):
        diff = compute_diff("姓名：张三\n负责运营", "姓名：张三\n推动运营增长")

        self.assertEqual(diff[0], ("=", "姓名：张三", "姓名：张三"))
        self.assertEqual(diff[1], ("~", "负责运营", "推动运营增长"))

    def test_untrusted_content_is_html_escaped(self):
        rendered = diff_to_html(
            [("~", "<script>alert('old')</script>", '<img src=x onerror="alert(1)">')]
        )

        self.assertNotIn("<script>", rendered)
        self.assertNotIn("<img src=x", rendered)
        self.assertIn("&lt;script&gt;", rendered)
        self.assertIn("&lt;img src=x onerror=&quot;alert(1)&quot;&gt;", rendered)

    def test_header_spans_all_six_columns(self):
        rendered = diff_to_html([])

        self.assertEqual(rendered.count('colspan="3"'), 2)
        self.assertNotIn('colspan="2"', rendered)

    def test_export_uses_new_brand(self):
        report = generate_export_markdown("原文", "优化稿", "点评", 80)

        self.assertIn("简历开麦", report)
        self.assertIn("开麦点评", report)
        self.assertNotIn("ResumeRoast", report)


if __name__ == "__main__":
    unittest.main()
