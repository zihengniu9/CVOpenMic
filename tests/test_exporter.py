import io
import unittest

from docx import Document

from exporter import create_docx_bytes


class ExporterTests(unittest.TestCase):
    def test_create_docx_bytes_produces_readable_document(self):
        payload = create_docx_bytes(
            "# 张三\n\n## 工作经历\n- 将处理时长降低 20%\n- 未提供的数据保留待补充",
            title="测试简历",
        )

        self.assertTrue(payload.startswith(b"PK"))
        document = Document(io.BytesIO(payload))
        text = "\n".join(paragraph.text for paragraph in document.paragraphs)
        self.assertIn("张三", text)
        self.assertIn("降低 20%", text)


if __name__ == "__main__":
    unittest.main()
