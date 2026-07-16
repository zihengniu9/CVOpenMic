"""CVOpenMic（简历开麦）结构化诊断与事实安全重写引擎。"""

from __future__ import annotations

import html
import json
import re
from collections.abc import Mapping
from functools import lru_cache
from typing import Any

from openai import OpenAI

from config import (
    ANALYSIS_MAX_TOKENS,
    ANALYSIS_SYSTEM_PROMPT,
    DEEPSEEK_API_KEY,
    DEEPSEEK_BASE_URL,
    DEEPSEEK_MAX_RETRIES,
    DEEPSEEK_MODEL,
    DEEPSEEK_TIMEOUT_SECONDS,
    MAX_FACT_ANSWERS_CHARS,
    MAX_JOB_DESCRIPTION_CHARS,
    MAX_RESUME_CHARS,
    REWRITE_MAX_TOKENS,
    REWRITE_SYSTEM_PROMPT,
    TONE_GUIDANCE,
    VALID_MODES,
    VALID_TONES,
    get_dimension_config,
)
from privacy import redact_sensitive_data, restore_sensitive_data


class EngineError(RuntimeError):
    """可安全展示给调用方的引擎错误基类。"""


class ModelResponseError(EngineError):
    """模型返回为空、截断或不满足结构约束。"""


_MODE_ALIASES = {
    "quick": "quick",
    "快速体检": "quick",
    "job_match": "job_match",
    "match": "job_match",
    "岗位匹配": "job_match",
}
_TONE_ALIASES = {
    "gentle": "gentle",
    "温和": "gentle",
    "direct": "direct",
    "直接": "direct",
    "roast": "roast",
    "毒舌": "roast",
}
_SEVERITY_ALIASES = {
    "high": "high",
    "高": "high",
    "medium": "medium",
    "中": "medium",
    "low": "low",
    "低": "low",
}
_PII_TOKEN_RE = re.compile(r"<PII_(?:EMAIL|PHONE|ID)_[A-Z2-7]+>")
_NUMBER_RE = re.compile(r"(?<![A-Za-z])\d+(?:[.,]\d+)?%?(?![A-Za-z])")
_LIST_NUMBER_RE = re.compile(r"(?m)^\s*(?:#{1,6}\s*)?\d+[.)、]\s+")
_MARKDOWN_SPECIAL_RE = re.compile(r"([`*_{}\[\]()#+\-.!|>])")


@lru_cache(maxsize=1)
def get_client() -> OpenAI:
    """创建并复用带明确超时、重试策略的 DeepSeek 客户端。"""

    if not DEEPSEEK_API_KEY or DEEPSEEK_API_KEY == "your-api-key-here":
        raise ValueError("请先设置 DEEPSEEK_API_KEY 环境变量")
    return OpenAI(
        api_key=DEEPSEEK_API_KEY,
        base_url=DEEPSEEK_BASE_URL,
        timeout=DEEPSEEK_TIMEOUT_SECONDS,
        max_retries=DEEPSEEK_MAX_RETRIES,
    )


def _normalize_mode(mode: str) -> str:
    normalized = _MODE_ALIASES.get(mode.strip() if isinstance(mode, str) else "")
    if normalized is None:
        raise ValueError(f"mode 必须是 {', '.join(VALID_MODES)} 之一")
    return normalized


def _normalize_tone(tone: str) -> str:
    normalized = _TONE_ALIASES.get(tone.strip() if isinstance(tone, str) else "")
    if normalized is None:
        raise ValueError(f"tone 必须是 {', '.join(VALID_TONES)} 之一")
    return normalized


def _validated_text(
    value: str,
    *,
    field: str,
    max_chars: int,
    required: bool = False,
) -> str:
    if not isinstance(value, str):
        raise TypeError(f"{field} 必须是字符串")
    cleaned = value.strip()
    if required and not cleaned:
        raise ValueError(f"{field} 不能为空")
    if len(cleaned) > max_chars:
        raise ValueError(f"{field} 过长，最多支持 {max_chars} 个字符")
    return cleaned


def _merge_mapping(target: dict[str, str], incoming: Mapping[str, str]) -> None:
    for token, original in incoming.items():
        existing = target.get(token)
        if existing is not None and existing != original:
            raise EngineError("隐私 token 发生冲突，请重试")
        target[token] = original


def _redact_fields(**fields: str) -> tuple[dict[str, str], dict[str, str]]:
    redacted: dict[str, str] = {}
    mapping: dict[str, str] = {}
    for name, value in fields.items():
        safe_value, field_mapping = redact_sensitive_data(value)
        redacted[name] = safe_value
        _merge_mapping(mapping, field_mapping)
    return redacted, mapping


def _restore_tree(value: Any, mapping: Mapping[str, str]) -> Any:
    if isinstance(value, str):
        return restore_sensitive_data(value, mapping)
    if isinstance(value, list):
        return [_restore_tree(item, mapping) for item in value]
    if isinstance(value, dict):
        return {key: _restore_tree(item, mapping) for key, item in value.items()}
    return value


def _response_content(response: Any) -> str:
    choices = getattr(response, "choices", None)
    if not choices:
        raise ModelResponseError("模型未返回结果，请重试")
    choice = choices[0]
    if getattr(choice, "finish_reason", None) == "length":
        raise ModelResponseError("模型输出被截断，请缩短简历后重试")
    message = getattr(choice, "message", None)
    content = getattr(message, "content", None)
    if not isinstance(content, str) or not content.strip():
        raise ModelResponseError("模型返回了空内容，请重试")
    return content.strip()


def _parse_json_object(content: str) -> dict[str, Any]:
    stripped = content.strip().lstrip("\ufeff")
    if stripped.startswith("```") and stripped.endswith("```"):
        lines = stripped.splitlines()
        if len(lines) >= 3:
            stripped = "\n".join(lines[1:-1]).strip()
    try:
        payload = json.loads(stripped)
    except json.JSONDecodeError as exc:
        raise ModelResponseError("模型未返回合法 JSON，请重试") from exc
    if not isinstance(payload, dict):
        raise ModelResponseError("模型返回结构错误，请重试")
    return payload


def _required_string(value: Any, field: str, *, max_length: int = 800) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ModelResponseError(f"模型字段 {field} 缺失或类型错误")
    cleaned = re.sub(r"\s+", " ", value).strip()
    if len(cleaned) > max_length:
        raise ModelResponseError(f"模型字段 {field} 过长")
    return cleaned


def _escape_markdown(value: Any) -> str:
    """Escape validated model text before placing it in generated Markdown."""

    escaped_html = html.escape(str(value), quote=False)
    return _MARKDOWN_SPECIAL_RE.sub(r"\\\1", escaped_html)


def _string_list(
    value: Any,
    field: str,
    *,
    max_items: int,
    max_length: int = 300,
) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise ModelResponseError(f"模型字段 {field} 必须是数组")
    if len(value) > max_items:
        raise ModelResponseError(f"模型字段 {field} 条目过多")
    return [
        _required_string(item, f"{field}[{index}]", max_length=max_length)
        for index, item in enumerate(value)
    ]


def _bounded_score(value: Any, *, key: str, maximum: int) -> int:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ModelResponseError(f"维度 {key} 必须是整数")
    if isinstance(value, float) and not value.is_integer():
        raise ModelResponseError(f"维度 {key} 必须是整数")
    score = int(value)
    if not 0 <= score <= maximum:
        raise ModelResponseError(f"维度 {key} 必须在 0 到 {maximum} 之间")
    return score


def _validate_issues(value: Any) -> list[dict[str, str]]:
    if value is None:
        return []
    if not isinstance(value, list) or len(value) > 5:
        raise ModelResponseError("模型字段 issues 必须是最多 5 条的数组")
    issues: list[dict[str, str]] = []
    for index, item in enumerate(value):
        if not isinstance(item, Mapping):
            raise ModelResponseError(f"模型字段 issues[{index}] 类型错误")
        raw_severity = item.get("severity")
        severity = _SEVERITY_ALIASES.get(
            raw_severity.strip() if isinstance(raw_severity, str) else ""
        )
        if severity is None:
            raise ModelResponseError(f"模型字段 issues[{index}].severity 错误")
        issues.append(
            {
                "severity": severity,
                "title": _required_string(item.get("title"), f"issues[{index}].title"),
                "evidence": _required_string(
                    item.get("evidence"), f"issues[{index}].evidence"
                ),
                "suggestion": _required_string(
                    item.get("suggestion"), f"issues[{index}].suggestion"
                ),
            }
        )
    return issues


def _format_analysis_markdown(result: Mapping[str, Any]) -> str:
    lines = ["## 🎯 总体评价", _escape_markdown(result["verdict"])]
    strengths = result.get("strengths", [])
    if strengths:
        lines.extend(
            [
                "",
                "## ✅ 已经做对的",
                *[f"- {_escape_markdown(item)}" for item in strengths],
            ]
        )

    issues = result.get("issues", [])
    issue_heading = {
        "gentle": "## 🌱 优先改进",
        "direct": "## 🔍 重点问题",
        "roast": "## 🎤 开麦点评",
    }[str(result["tone"])]
    if issues:
        lines.extend(["", issue_heading])
        severity_label = {"high": "高", "medium": "中", "low": "低"}
        for issue in issues:
            lines.extend(
                [
                    f"### [{severity_label[issue['severity']]}] {_escape_markdown(issue['title'])}",
                    f"- 依据：{_escape_markdown(issue['evidence'])}",
                    f"- 怎么改：{_escape_markdown(issue['suggestion'])}",
                ]
            )

    questions = result.get("fact_questions", [])
    if questions:
        lines.extend(["", "## ❓ 重写前需要补充的事实"])
        lines.extend(
            f"{index}. {_escape_markdown(question)}"
            for index, question in enumerate(questions, 1)
        )
    return "\n\n".join(lines)


def _validate_analysis_payload(
    payload: Mapping[str, Any], *, mode: str, tone: str
) -> dict[str, Any]:
    raw_dimensions = payload.get("dimensions")
    if not isinstance(raw_dimensions, Mapping):
        raise ModelResponseError("模型字段 dimensions 缺失或类型错误")

    dimensions: dict[str, int] = {}
    for _label, key, maximum in get_dimension_config(mode):
        dimensions[key] = _bounded_score(
            raw_dimensions.get(key), key=key, maximum=maximum
        )

    result: dict[str, Any] = {
        "mode": mode,
        "tone": tone,
        "score": sum(dimensions.values()),
        "dimensions": dimensions,
        "verdict": _required_string(payload.get("verdict"), "verdict"),
        "strengths": _string_list(
            payload.get("strengths"), "strengths", max_items=3
        ),
        "issues": _validate_issues(payload.get("issues")),
        "fact_questions": _string_list(
            payload.get("fact_questions"), "fact_questions", max_items=5
        ),
        "matched_keywords": _string_list(
            payload.get("matched_keywords"), "matched_keywords", max_items=20
        ),
        "missing_keywords": _string_list(
            payload.get("missing_keywords"), "missing_keywords", max_items=20
        ),
    }
    if mode == "quick":
        result["matched_keywords"] = []
        result["missing_keywords"] = []
    result["roast"] = _format_analysis_markdown(result)
    return result


def analyze_resume(
    resume_text: str,
    mode: str = "quick",
    target_role: str = "",
    job_description: str = "",
    tone: str = "direct",
) -> dict[str, Any]:
    """用一轮结构化调用完成快速体检或岗位匹配诊断。"""

    normalized_mode = _normalize_mode(mode)
    normalized_tone = _normalize_tone(tone)
    resume = _validated_text(
        resume_text, field="resume_text", max_chars=MAX_RESUME_CHARS, required=True
    )
    target = _validated_text(
        target_role,
        field="target_role",
        max_chars=500,
    )
    job = _validated_text(
        job_description,
        field="job_description",
        max_chars=MAX_JOB_DESCRIPTION_CHARS,
    )
    if normalized_mode == "job_match" and not (target or job):
        raise ValueError("岗位匹配模式至少需要 target_role 或 job_description")

    redacted, mapping = _redact_fields(
        resume=resume,
        target_role=target,
        job_description=job,
    )
    request_payload = {
        "task": "resume_diagnosis",
        "mode": normalized_mode,
        "tone": TONE_GUIDANCE[normalized_tone],
        "dimension_rubric": [
            {"label": label, "key": key, "maximum": maximum}
            for label, key, maximum in get_dimension_config(normalized_mode)
        ],
        **redacted,
    }
    response = get_client().chat.completions.create(
        model=DEEPSEEK_MODEL,
        messages=[
            {"role": "system", "content": ANALYSIS_SYSTEM_PROMPT},
            {
                "role": "user",
                "content": "请严格按系统规则分析以下 JSON 数据包：\n"
                + json.dumps(request_payload, ensure_ascii=False),
            },
        ],
        response_format={"type": "json_object"},
        temperature=0.2,
        max_tokens=ANALYSIS_MAX_TOKENS,
    )
    payload = _parse_json_object(_response_content(response))
    validated = _validate_analysis_payload(
        payload, mode=normalized_mode, tone=normalized_tone
    )
    return _restore_tree(validated, mapping)


def _analysis_for_rewrite(analysis: Mapping[str, Any] | str) -> dict[str, Any]:
    if isinstance(analysis, str):
        return {"legacy_feedback": analysis}
    if not isinstance(analysis, Mapping):
        raise TypeError("analysis 必须是诊断字典或点评字符串")
    allowed = (
        "mode",
        "tone",
        "verdict",
        "dimensions",
        "issues",
        "fact_questions",
        "matched_keywords",
        "missing_keywords",
    )
    return {key: analysis[key] for key in allowed if key in analysis}


def _numeric_literals(text: str) -> set[str]:
    without_tokens = _PII_TOKEN_RE.sub("", text)
    without_list_numbers = _LIST_NUMBER_RE.sub("", without_tokens)
    literals: set[str] = set()
    for match in _NUMBER_RE.finditer(without_list_numbers):
        raw = match.group(0).replace(",", "")
        value = raw.removesuffix("%")
        canonical = value.lstrip("0") or "0"
        literals.update({raw, value, canonical})

        # 允许模型只改变日期/小数的书写方式，例如 2023.01 → 2023年1月；
        # 仍会拦截来源中完全不存在的新数字。
        if "." in value:
            for component in value.split("."):
                literals.add(component.lstrip("0") or "0")
    return literals


def _assert_no_new_numbers(rewritten: str, factual_sources: str) -> None:
    allowed = _numeric_literals(factual_sources)
    introduced = sorted(_numeric_literals(rewritten) - allowed)
    if introduced:
        raise ModelResponseError(
            "重写结果出现原始事实中不存在的数字，已阻止可能的编造；请重试"
        )


def _append_fact_placeholders(
    rewritten: str, analysis: Mapping[str, Any] | str, fact_answers: str
) -> str:
    if fact_answers.strip() or not isinstance(analysis, Mapping):
        return rewritten
    questions = analysis.get("fact_questions")
    if not isinstance(questions, list) or not questions:
        return rewritten
    if "【待补充：" in rewritten:
        return rewritten
    valid_questions = [item.strip() for item in questions if isinstance(item, str) and item.strip()]
    if not valid_questions:
        return rewritten
    placeholders = "\n".join(f"- 【待补充：{question}】" for question in valid_questions)
    return f"{rewritten.rstrip()}\n\n## 待补充事实\n\n{placeholders}"


def rewrite_resume(
    resume_text: str,
    analysis: Mapping[str, Any] | str,
    target_role: str = "",
    job_description: str = "",
    fact_answers: str = "",
) -> str:
    """按诊断重写简历；只使用原文与用户补充答案作为事实来源。"""

    resume = _validated_text(
        resume_text, field="resume_text", max_chars=MAX_RESUME_CHARS, required=True
    )
    target = _validated_text(target_role, field="target_role", max_chars=500)
    job = _validated_text(
        job_description,
        field="job_description",
        max_chars=MAX_JOB_DESCRIPTION_CHARS,
    )
    answers = _validated_text(
        fact_answers,
        field="fact_answers",
        max_chars=MAX_FACT_ANSWERS_CHARS,
    )
    analysis_payload = _analysis_for_rewrite(analysis)
    serialized_analysis = json.dumps(analysis_payload, ensure_ascii=False, default=str)

    redacted, mapping = _redact_fields(
        resume=resume,
        target_role=target,
        job_description=job,
        fact_answers=answers,
        analysis=serialized_analysis,
    )
    request_payload = {
        "task": "fact_safe_resume_rewrite",
        "resume": redacted["resume"],
        "target_role": redacted["target_role"],
        "job_description": redacted["job_description"],
        "fact_answers": redacted["fact_answers"],
        "analysis": json.loads(redacted["analysis"]),
    }
    response = get_client().chat.completions.create(
        model=DEEPSEEK_MODEL,
        messages=[
            {"role": "system", "content": REWRITE_SYSTEM_PROMPT},
            {
                "role": "user",
                "content": "请严格按系统规则重写以下 JSON 数据包：\n"
                + json.dumps(request_payload, ensure_ascii=False),
            },
        ],
        temperature=0.2,
        max_tokens=REWRITE_MAX_TOKENS,
    )
    rewritten = _response_content(response)
    _assert_no_new_numbers(
        rewritten, redacted["resume"] + "\n" + redacted["fact_answers"]
    )
    rewritten = _append_fact_placeholders(rewritten, analysis, answers)
    return restore_sensitive_data(rewritten, mapping)


def roast_resume(
    resume_text: str,
    mode: str = "quick",
    target_role: str = "",
    job_description: str = "",
    tone: str = "roast",
) -> dict[str, Any]:
    """兼容旧接口：现在由单轮结构化诊断生成点评与分数。"""

    return analyze_resume(resume_text, mode, target_role, job_description, tone)


def quick_analyze_only(
    resume_text: str,
    mode: str = "quick",
    target_role: str = "",
    job_description: str = "",
    tone: str = "direct",
) -> dict[str, Any]:
    """仅诊断，不执行重写。"""

    return analyze_resume(resume_text, mode, target_role, job_description, tone)


def full_analyze(
    resume_text: str,
    mode: str = "quick",
    target_role: str = "",
    job_description: str = "",
    tone: str = "direct",
    fact_answers: str = "",
) -> dict[str, Any]:
    """兼容旧接口：一轮诊断后执行一次事实安全重写。"""

    result = analyze_resume(resume_text, mode, target_role, job_description, tone)
    result["rewritten"] = rewrite_resume(
        resume_text,
        result,
        target_role=target_role,
        job_description=job_description,
        fact_answers=fact_answers,
    )
    return result


__all__ = [
    "EngineError",
    "ModelResponseError",
    "analyze_resume",
    "full_analyze",
    "get_client",
    "get_dimension_config",
    "quick_analyze_only",
    "rewrite_resume",
    "roast_resume",
]
