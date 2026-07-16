"""简历解析模块 - 支持 PDF / DOCX / 图片 OCR / 纯文本。"""

import io
import re
import zipfile
from pathlib import Path

import config as app_config
from config import MAX_FILE_SIZE_MB, MAX_PAGES


# 新旧配置名均可用；当前产品配置统一使用 MAX_RESUME_CHARS。
MAX_TEXT_CHARS = getattr(
    app_config, "MAX_RESUME_CHARS", getattr(app_config, "MAX_TEXT_CHARS", 30_000)
)
MAX_IMAGE_PIXELS = getattr(app_config, "MAX_IMAGE_PIXELS", 20_000_000)
MIN_TEXT_CHARS = 50

_IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff", ".webp"}
_IMAGE_FORMAT_BY_EXTENSION = {
    ".png": "png",
    ".jpg": "jpeg",
    ".jpeg": "jpeg",
    ".bmp": "bmp",
    ".tif": "tiff",
    ".tiff": "tiff",
    ".webp": "webp",
}


def _enforce_text_limit(text: str) -> None:
    if len(text) > MAX_TEXT_CHARS:
        raise ValueError(f"简历文本过长（最多 {MAX_TEXT_CHARS:,} 个字符）")


def _append_with_limit(parts: list[str], text: str, current_length: int) -> int:
    """追加非空文本，并在解析过程中尽早阻止超长输入。"""
    if not text or not text.strip():
        return current_length

    new_length = current_length + len(text) + (1 if parts else 0)
    if new_length > MAX_TEXT_CHARS:
        raise ValueError(f"简历文本过长（最多 {MAX_TEXT_CHARS:,} 个字符）")
    parts.append(text)
    return new_length


def _image_format_from_signature(file_bytes: bytes) -> str | None:
    if file_bytes.startswith(b"\x89PNG\r\n\x1a\n"):
        return "png"
    if file_bytes.startswith(b"\xff\xd8\xff"):
        return "jpeg"
    if file_bytes.startswith(b"BM"):
        return "bmp"
    if file_bytes.startswith((b"II*\x00", b"MM\x00*")):
        return "tiff"
    if len(file_bytes) >= 12 and file_bytes.startswith(b"RIFF") and file_bytes[8:12] == b"WEBP":
        return "webp"
    return None


def _looks_like_docx(file_bytes: bytes) -> bool:
    """DOCX 应为包含 Word 主文档的 ZIP 包。"""
    try:
        with zipfile.ZipFile(io.BytesIO(file_bytes)) as archive:
            names = set(archive.namelist())
            return "[Content_Types].xml" in names and "word/document.xml" in names
    except (OSError, zipfile.BadZipFile):
        return False


def _validate_file_signature(file_bytes: bytes, filename: str, fmt: str) -> None:
    if not file_bytes:
        raise ValueError("上传的文件为空")

    if fmt == "pdf":
        # PDF 规范允许文件头出现在开头后的少量字节内。
        if b"%PDF-" not in file_bytes[:1024]:
            raise ValueError("文件内容不是有效的 PDF，请检查文件后重试")
    elif fmt == "docx":
        if not _looks_like_docx(file_bytes):
            raise ValueError("文件内容不是有效的 DOCX，请重新另存为 .docx 后上传")
    elif fmt == "image":
        actual_format = _image_format_from_signature(file_bytes)
        expected_format = _IMAGE_FORMAT_BY_EXTENSION[Path(filename).suffix.lower()]
        if actual_format is None:
            raise ValueError("文件内容不是受支持的图片格式")
        if actual_format != expected_format:
            raise ValueError("图片扩展名与实际格式不一致，请修正文件名后重试")


def parse_pdf(file_bytes: bytes) -> str:
    """解析文本型 PDF；扫描件应走图片 OCR。"""
    from PyPDF2 import PdfReader

    if b"%PDF-" not in file_bytes[:1024]:
        raise ValueError("文件内容不是有效的 PDF，请检查文件后重试")

    try:
        reader = PdfReader(io.BytesIO(file_bytes))
        if reader.is_encrypted:
            raise ValueError("暂不支持加密 PDF，请解除密码后重试")

        page_count = len(reader.pages)
        if page_count > MAX_PAGES:
            raise ValueError(f"PDF 页数超过限制（最多 {MAX_PAGES} 页）")

        texts: list[str] = []
        current_length = 0
        for page in reader.pages:
            text = page.extract_text() or ""
            current_length = _append_with_limit(texts, text, current_length)
    except ValueError:
        raise
    except Exception as exc:
        raise ValueError("PDF 文件损坏或无法解析") from exc

    if not texts:
        raise ValueError("PDF 未提取到文本，可能是扫描件，请上传清晰图片进行 OCR")

    content = clean_text("\n--- 分页 ---\n".join(texts))
    _enforce_text_limit(content)
    return content


def _iter_docx_blocks(document):
    """按正文中的实际顺序遍历段落和表格。"""
    from docx.oxml.table import CT_Tbl
    from docx.oxml.text.paragraph import CT_P
    from docx.table import Table
    from docx.text.paragraph import Paragraph

    for child in document.element.body.iterchildren():
        if isinstance(child, CT_P):
            yield Paragraph(child, document)
        elif isinstance(child, CT_Tbl):
            yield Table(child, document)


def parse_docx(file_bytes: bytes) -> str:
    """解析 DOCX，并尽量保留段落与表格在正文中的先后顺序。"""
    from docx import Document
    from docx.table import Table

    if not _looks_like_docx(file_bytes):
        raise ValueError("文件内容不是有效的 DOCX，请重新另存为 .docx 后上传")

    try:
        doc = Document(io.BytesIO(file_bytes))
        texts: list[str] = []
        current_length = 0

        for block in _iter_docx_blocks(doc):
            if isinstance(block, Table):
                for row in block.rows:
                    row_text = " | ".join(
                        cell.text.strip() for cell in row.cells if cell.text.strip()
                    )
                    current_length = _append_with_limit(texts, row_text, current_length)
            else:
                current_length = _append_with_limit(texts, block.text, current_length)
    except ValueError:
        raise
    except Exception as exc:
        raise ValueError("DOCX 文件损坏或无法解析") from exc

    if not texts:
        raise ValueError("Word 文档中未提取到文本")

    content = clean_text("\n".join(texts))
    _enforce_text_limit(content)
    return content


def parse_image(file_bytes: bytes) -> str:
    """通过 OCR 识别图片；在 OCR 前限制解码后的像素数。"""
    from PIL import Image, UnidentifiedImageError

    if _image_format_from_signature(file_bytes) is None:
        raise ValueError("文件内容不是受支持的图片格式")

    try:
        with Image.open(io.BytesIO(file_bytes)) as image:
            width, height = image.size
            if width <= 0 or height <= 0:
                raise ValueError("图片尺寸无效")
            if width * height > MAX_IMAGE_PIXELS:
                raise ValueError(
                    f"图片像素过大（最多 {MAX_IMAGE_PIXELS:,} 像素）"
                )

            # 强制在上下文关闭前完成解码，损坏图片会在这里报错。
            image.load()
            import pytesseract

            text = pytesseract.image_to_string(image, lang="chi_sim+eng")
    except ValueError:
        raise
    except (UnidentifiedImageError, OSError) as exc:
        raise ValueError("图片损坏或无法解析") from exc

    if not text.strip():
        raise ValueError("图片中未识别到文字，请确保图片清晰且包含文字")

    content = clean_text(text)
    _enforce_text_limit(content)
    return content


def parse_text(file_bytes: bytes) -> str:
    """解析 UTF-8（含 BOM）或 GB18030 纯文本。"""
    for encoding in ("utf-8-sig", "gb18030"):
        try:
            content = clean_text(file_bytes.decode(encoding, errors="strict"))
            _enforce_text_limit(content)
            return content
        except UnicodeDecodeError:
            continue
    raise ValueError("文本编码不受支持，请使用 UTF-8 或 GB18030")


def detect_format(filename: str) -> str:
    """根据扩展名判断文件格式。"""
    suffix = Path(filename).suffix.lower()
    if suffix == ".pdf":
        return "pdf"
    if suffix == ".docx":
        return "docx"
    if suffix == ".doc":
        raise ValueError("暂不支持旧版 .doc，请另存为 .docx 或 PDF 后上传")
    if suffix in _IMAGE_EXTENSIONS:
        return "image"
    if suffix == ".txt":
        return "txt"
    raise ValueError(f"不支持的文件格式: {filename}，请上传 PDF、DOCX、图片或 TXT")


def parse_resume(file_bytes: bytes, filename: str) -> tuple[str, str]:
    """解析简历文件，返回 ``(清洗后的文本, 文件格式)``。"""
    if len(file_bytes) > MAX_FILE_SIZE_MB * 1024 * 1024:
        raise ValueError(f"文件太大（最大支持 {MAX_FILE_SIZE_MB}MB）")

    fmt = detect_format(filename)
    _validate_file_signature(file_bytes, filename, fmt)

    if fmt == "pdf":
        text = parse_pdf(file_bytes)
    elif fmt == "docx":
        text = parse_docx(file_bytes)
    elif fmt == "image":
        text = parse_image(file_bytes)
    elif fmt == "txt":
        text = parse_text(file_bytes)
    else:  # pragma: no cover - detect_format 已保证穷尽
        raise ValueError(f"不支持的格式: {fmt}")

    text = clean_text(text)
    _enforce_text_limit(text)
    if len(text) < MIN_TEXT_CHARS:
        raise ValueError(
            f"简历内容太少（少于 {MIN_TEXT_CHARS} 字符），可能解析失败，请检查文件"
        )

    return text, fmt


def clean_text(text: str) -> str:
    """清洗文本。"""
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = "\n".join(line.strip() for line in text.split("\n"))
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]", "", text)
    return text.strip()
