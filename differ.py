"""简历开麦对比展示模块 - 原文 vs 优化版 diff。"""
import difflib
import html as html_lib
from typing import List, Tuple


DiffLine = Tuple[str, str, str]  # (sign, old_line, new_line)


def compute_diff(original: str, rewritten: str) -> List[DiffLine]:
    """
    计算两段文本的差异
    返回: [(标记, 原文行, 优化行), ...]
    标记: "=" 相同, "-" 删除, "+" 新增, "~" 修改
    """
    original_lines = original.splitlines()
    rewritten_lines = rewritten.splitlines()

    matcher = difflib.SequenceMatcher(None, original_lines, rewritten_lines)
    result: List[DiffLine] = []

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            for k in range(i1, i2):
                result.append(("=", original_lines[k], rewritten_lines[j1 + k - i1]))
        elif tag == "delete":
            for k in range(i1, i2):
                result.append(("-", original_lines[k], ""))
        elif tag == "insert":
            for k in range(j1, j2):
                result.append(("+", "", rewritten_lines[k]))
        elif tag == "replace":
            # 逐行对比替换
            old_block = original_lines[i1:i2]
            new_block = rewritten_lines[j1:j2]
            for k in range(max(len(old_block), len(new_block))):
                old_line = old_block[k] if k < len(old_block) else ""
                new_line = new_block[k] if k < len(new_block) else ""
                result.append(("~", old_line, new_line))

    return result


def diff_to_html(diff: List[DiffLine]) -> str:
    """将 diff 结果转为 HTML 表格"""
    html = """
    <style>
    .diff-table { width: 100%; border-collapse: collapse; font-size: 14px; }
    .diff-table td { padding: 8px 12px; vertical-align: top; border-bottom: 1px solid #333; }
    .diff-table .diff-content { white-space: pre-wrap; overflow-wrap: anywhere; }
    .diff-table .line-num { width: 30px; color: #666; text-align: right; padding-right: 12px; user-select: none; }
    .diff-table .diff-equal { background: transparent; }
    .diff-table .diff-delete { background: rgba(255, 80, 80, 0.15); }
    .diff-table .diff-insert { background: rgba(80, 255, 80, 0.15); }
    .diff-table .diff-replace { background: rgba(255, 200, 50, 0.15); }
    .diff-sign { font-weight: bold; width: 20px; text-align: center; }
    .diff-sign-equal { color: #666; }
    .diff-sign-delete { color: #ff5050; }
    .diff-sign-insert { color: #50ff50; }
    .diff-sign-replace { color: #ffc832; }
    .diff-col-header { color: #999; font-weight: bold; font-size: 13px; border-bottom: 2px solid #555; background: #1a1a2e; }
    </style>
    <table class="diff-table">
    <tr>
        <th class="diff-col-header" colspan="3">❌ 原简历</th>
        <th class="diff-col-header" colspan="3">✅ 优化后</th>
    </tr>
    """

    signs = {"=": " ", "-": "-", "+": "+", "~": "~"}
    sign_classes = {
        "=": "diff-equal diff-sign-equal",
        "-": "diff-delete diff-sign-delete",
        "+": "diff-insert diff-sign-insert",
        "~": "diff-replace diff-sign-replace",
    }
    row_classes = {
        "=": "diff-equal",
        "-": "diff-delete",
        "+": "diff-insert",
        "~": "diff-replace",
    }

    old_num = new_num = 0
    for sign, old_line, new_line in diff:
        old_num += 1 if old_line else 0
        new_num += 1 if new_line else 0

        # 简历原文与模型输出都属于不可信输入，进入 HTML 前必须转义。
        old_display = html_lib.escape(old_line, quote=True) if old_line else "&nbsp;"
        new_display = html_lib.escape(new_line, quote=True) if new_line else "&nbsp;"

        html += f"""<tr class="{row_classes[sign]}">
            <td class="line-num">{old_num if old_line else ''}</td>
            <td class="diff-sign {sign_classes[sign]}">{signs[sign]}</td>
            <td class="diff-content">{old_display}</td>
            <td class="line-num">{new_num if new_line else ''}</td>
            <td class="diff-sign {sign_classes[sign]}">{signs[sign]}</td>
            <td class="diff-content">{new_display}</td>
        </tr>"""

    html += "</table>"
    return html


def generate_export_markdown(original: str, rewritten: str, roast: str, score: int) -> str:
    """生成导出的完整 Markdown"""
    return f"""# 简历开麦 · 优化报告

## 📊 综合评分: {score}/100

---

## 💬 开麦点评

{roast}

---

## 📝 优化后简历

{rewritten}

---
*由「简历开麦」生成 · 先说真话，再把简历改好*
"""
