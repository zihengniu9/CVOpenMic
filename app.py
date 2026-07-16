"""简历开麦（CVOpenMic）— 基于证据的 AI 简历诊断与改写。"""

from __future__ import annotations

import hashlib
import html
import logging
import re
from pathlib import Path

import streamlit as st

import config
from differ import compute_diff, diff_to_html
from engine import analyze_resume, rewrite_resume
from exporter import create_docx_bytes
from parser import parse_resume
from privacy import redact_sensitive_data


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("cvopenmic")

BRAND_NAME = "简历开麦"
BRAND_CODE = "CVOpenMic"
MAX_FILE_SIZE_MB = config.MAX_FILE_SIZE_MB
MAX_SESSION_CALLS = getattr(config, "MAX_LLM_CALLS_PER_SESSION", 12)


st.set_page_config(
    page_title=f"{BRAND_NAME} · AI简历真话官",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
<style>
    html, body, [class*="css"] {
        font-family: "Microsoft YaHei", "PingFang SC", "Noto Sans CJK SC", sans-serif;
    }
    .block-container { max-width: 1120px; padding-top: 2rem; }
    .brand-header { text-align: center; padding: 1.25rem 0 1.5rem; }
    .brand-header h1 {
        margin: 0;
        font-size: clamp(2.3rem, 6vw, 4.2rem);
        font-weight: 900;
        letter-spacing: -0.04em;
        background: linear-gradient(125deg, #ff4d67, #ff8a3d 58%, #ffc857);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .brand-header .code {
        display: inline-block; margin-top: .35rem; padding: .18rem .6rem;
        border: 1px solid rgba(255,138,61,.35); border-radius: 999px;
        color: #ff9f62; font-size: .78rem; letter-spacing: .08em;
    }
    .brand-header p { color: #9aa0aa; font-size: 1.05rem; margin: .7rem 0 0; }
    .promise-grid {
        display: grid; grid-template-columns: repeat(3, 1fr); gap: .8rem;
        margin: .5rem 0 1.5rem;
    }
    .promise-card {
        border: 1px solid rgba(128,128,128,.22); border-radius: 14px;
        padding: 1rem; background: rgba(128,128,128,.045);
    }
    .promise-card b { display: block; margin-bottom: .25rem; }
    .promise-card span { color: #8f96a3; font-size: .88rem; }
    .score-circle {
        width: 158px; height: 158px; border-radius: 50%; display: flex;
        flex-direction: column; align-items: center; justify-content: center;
        margin: .5rem auto; font-weight: 900; border: 6px solid;
    }
    .score-number { font-size: 3.35rem; line-height: 1; }
    .score-label { font-size: .82rem; color: #8d939e; margin-top: .25rem; }
    .dimension-bar { margin: 10px 0; }
    .dimension-label { display: flex; justify-content: space-between; font-size: .86rem; }
    .top-action {
        border-left: 4px solid #ff7a45; border-radius: 8px;
        padding: .7rem .85rem; margin: .5rem 0; background: rgba(255,122,69,.075);
    }
    .verdict-box {
        border: 1px solid rgba(255,138,61,.25); border-radius: 12px;
        padding: .9rem 1rem; margin: .5rem 0 1rem; background: rgba(255,138,61,.06);
    }
    .privacy-note {
        border: 1px solid rgba(46,213,115,.25); border-radius: 12px;
        padding: .8rem 1rem; color: #9ca5b1; background: rgba(46,213,115,.045);
        font-size: .88rem; margin-bottom: 1rem;
    }
    .footer { text-align: center; padding: 2rem 0 1rem; color: #6f7680; font-size: .82rem; }
    @media (max-width: 760px) { .promise-grid { grid-template-columns: 1fr; } }
</style>
""",
    unsafe_allow_html=True,
)


def _init_state() -> None:
    defaults = {
        "analysis_key": "",
        "analysis_result": None,
        "rewrite_key": "",
        "rewritten": "",
        "llm_call_count": 0,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


@st.cache_data(show_spinner=False, max_entries=12)
def _parse_cached(file_bytes: bytes, filename: str) -> tuple[str, str]:
    return parse_resume(file_bytes, filename)


def _build_analysis_key(
    file_bytes: bytes,
    mode: str,
    target_role: str,
    job_description: str,
    tone: str,
) -> str:
    digest = hashlib.sha256()
    digest.update(file_bytes)
    for value in (mode, target_role, job_description, tone, "privacy_v1"):
        digest.update(b"\x00")
        digest.update(value.strip().encode("utf-8"))
    return digest.hexdigest()


def _can_call_model() -> bool:
    if st.session_state.llm_call_count >= MAX_SESSION_CALLS:
        st.error("本次会话的 AI 调用次数已达上限。请刷新页面后谨慎重试。")
        return False
    return True


def _safe_download_stem(filename: str) -> str:
    stem = Path(filename).stem
    stem = re.sub(r"[^\w\u4e00-\u9fff-]+", "_", stem, flags=re.UNICODE).strip("_")
    return stem[:60] or "resume"


def _render_footer() -> None:
    st.markdown(
        f'<div class="footer">🎙️ {BRAND_NAME} · {BRAND_CODE}<br>'
        "AI 建议仅供参考，最终内容请由本人核验。</div>",
        unsafe_allow_html=True,
    )


_init_state()

st.markdown(
    f"""
<div class="brand-header">
  <h1>🎙️ {BRAND_NAME}</h1>
  <span class="code">{BRAND_CODE}</span>
  <p>先听真话，再拿 Offer。</p>
</div>
<div class="promise-grid">
  <div class="promise-card"><b>岗位有参照</b><span>粘贴目标 JD，再谈关键词和匹配度。</span></div>
  <div class="promise-card"><b>改写不编造</b><span>缺失数据明确追问，不替你虚构成绩。</span></div>
  <div class="promise-card"><b>建议能落地</b><span>定位原文证据，生成可编辑、可导出的版本。</span></div>
</div>
""",
    unsafe_allow_html=True,
)

st.markdown(
    """
<div class="privacy-note">
🔒 简历文本会发送给你配置的 DeepSeek API 进行分析。默认在本地先遮盖邮箱、手机号和身份证号；
应用本身不主动把文件写入磁盘。公开部署前，请同时确认模型供应商的数据处理条款。
</div>
""",
    unsafe_allow_html=True,
)

uploaded_file = st.file_uploader(
    "上传简历",
    type=["pdf", "docx", "png", "jpg", "jpeg", "txt"],
    help=f"支持 PDF、DOCX、PNG、JPG、TXT，最大 {MAX_FILE_SIZE_MB}MB。不支持旧版 .doc。",
)

if not uploaded_file:
    st.info("上传简历后，可选择快速体检，或粘贴目标 JD 做岗位匹配。")
    _render_footer()
    st.stop()

if uploaded_file.size > MAX_FILE_SIZE_MB * 1024 * 1024:
    st.error(f"文件超过 {MAX_FILE_SIZE_MB}MB，请压缩后重试。")
    st.stop()

file_bytes = uploaded_file.getvalue()
try:
    with st.spinner("正在安全解析简历…"):
        resume_text, file_format = _parse_cached(file_bytes, uploaded_file.name)
except Exception as exc:
    logger.warning("Resume parsing failed: %s", type(exc).__name__)
    st.error(f"简历解析失败：{exc}")
    st.stop()

st.success(f"解析完成 · {file_format.upper()} · {len(resume_text):,} 个字符")
with st.expander("检查解析后的文本", expanded=False):
    st.text_area("解析内容", resume_text, height=280, disabled=True)

st.markdown("## 选择诊断方式")
mode_label = st.radio(
    "诊断模式",
    ["快速体检", "岗位匹配"],
    horizontal=True,
    help="快速体检不评价岗位关键词；岗位匹配会根据目标 JD 评估相关性。",
)
mode = "quick" if mode_label == "快速体检" else "job_match"

target_role = ""
job_description = ""
if mode == "job_match":
    col_role, col_hint = st.columns([2, 1])
    with col_role:
        target_role = st.text_input(
            "目标岗位",
            placeholder="例如：高级产品经理",
        )
    with col_hint:
        st.caption("岗位名称帮助模型选择更合适的评价标准。")
    job_description = st.text_area(
        "职位描述（JD）",
        height=190,
        placeholder="粘贴岗位职责、任职要求和加分项…",
    )

tone_label = st.radio(
    "反馈语气",
    ["温和", "直接", "毒舌"],
    index=1,
    horizontal=True,
)
tone = {"温和": "gentle", "直接": "direct", "毒舌": "roast"}[tone_label]
redacted_preview, preview_mapping = redact_sensitive_data(resume_text)
st.caption("🔒 自动脱敏始终开启；发送前会遮盖邮箱、手机号和身份证号。")
with st.expander(
    f"查看将发送给模型的脱敏文本（已遮盖 {len(preview_mapping)} 处）",
    expanded=False,
):
    st.text_area(
        "脱敏内容",
        redacted_preview,
        height=240,
        disabled=True,
        key=f"redacted_preview_{hashlib.sha256(file_bytes).hexdigest()}",
    )

analysis_key = _build_analysis_key(
    file_bytes,
    mode,
    target_role,
    job_description,
    tone,
)

analyze_btn = st.button(
    "开始岗位匹配" if mode == "job_match" else "开始简历体检",
    type="primary",
    use_container_width=True,
)

if analyze_btn:
    if mode == "job_match" and (not target_role.strip() or len(job_description.strip()) < 30):
        st.error("岗位匹配需要填写目标岗位，并粘贴较完整的 JD。")
    elif _can_call_model():
        try:
            st.session_state.llm_call_count += 1
            with st.spinner("AI 正在定位最影响过筛的问题…"):
                result = analyze_resume(
                    resume_text,
                    mode=mode,
                    target_role=target_role,
                    job_description=job_description,
                    tone=tone,
                )
            st.session_state.analysis_key = analysis_key
            st.session_state.analysis_result = result
            st.session_state.rewrite_key = ""
            st.session_state.rewritten = ""
            st.rerun()
        except Exception as exc:
            logger.exception("Resume analysis failed (%s)", type(exc).__name__)
            if "DEEPSEEK_API_KEY" in str(exc):
                st.error(str(exc))
            else:
                st.error("分析暂时失败，没有扣除本地调用额度。请稍后重试。")

result = (
    st.session_state.analysis_result
    if st.session_state.analysis_key == analysis_key
    else None
)

if not result:
    st.info("完成以上设置后开始分析；修改文件、JD 或语气会生成一份新的报告。")
    _render_footer()
    st.stop()

display_result = result
score = int(display_result["score"])
dimensions = display_result["dimensions"]
dimension_config = config.get_dimension_config(mode)

st.divider()
st.markdown("## 简历体检报告")
if display_result.get("verdict"):
    st.markdown(
        f'<div class="verdict-box">{html.escape(str(display_result["verdict"]))}</div>',
        unsafe_allow_html=True,
    )

score_color = "#ff4757" if score < 50 else "#ffa502" if score < 75 else "#2ed573"
col_score, col_dims = st.columns([1, 2])

with col_score:
    st.markdown(
        f"""
<div class="score-circle" style="border-color:{score_color};color:{score_color};">
  <div class="score-number">{score}</div>
  <div class="score-label">/ 100</div>
</div>
""",
        unsafe_allow_html=True,
    )

with col_dims:
    for label, key, full_score in dimension_config:
        value = int(dimensions[key])
        ratio = max(0.0, min(1.0, value / full_score))
        bar_color = "#ff4757" if ratio < 0.5 else "#ffa502" if ratio < 0.75 else "#2ed573"
        st.markdown(
            f"""
<div class="dimension-bar">
  <div class="dimension-label"><span>{label}</span><span style="color:{bar_color}">{value}/{full_score}</span></div>
  <div style="background:#30343b;border-radius:4px;height:8px;overflow:hidden;">
    <div style="width:{ratio * 100:.1f}%;height:100%;background:{bar_color};border-radius:4px;"></div>
  </div>
</div>
""",
            unsafe_allow_html=True,
        )

top_actions = display_result.get("top_actions", []) or [
    f"{issue['title']}：{issue['suggestion']}"
    for issue in display_result.get("issues", [])
    if isinstance(issue, dict) and issue.get("title") and issue.get("suggestion")
]
if top_actions:
    st.markdown("### 最该先改的 3 件事")
    for index, action in enumerate(top_actions[:3], 1):
        st.markdown(
            f'<div class="top-action"><b>{index}.</b> {html.escape(str(action))}</div>',
            unsafe_allow_html=True,
        )

if mode == "job_match":
    matched_keywords = display_result.get("matched_keywords", [])
    missing_keywords = display_result.get("missing_keywords", [])
    col_matched, col_missing = st.columns(2)
    with col_matched:
        st.markdown("### 已覆盖的岗位关键词")
        if matched_keywords:
            for keyword in matched_keywords:
                st.text(f"• {keyword}")
        else:
            st.caption("暂未识别到明确匹配项。")
    with col_missing:
        st.markdown("### 值得核实的缺口")
        if missing_keywords:
            for keyword in missing_keywords:
                st.text(f"• {keyword}")
        else:
            st.caption("没有发现需要补充的重要关键词。")

st.markdown("### 详细点评")
st.markdown(display_result["roast"])

fact_questions = display_result.get("fact_questions", [])
if fact_questions:
    st.markdown("### AI 不会替你编的数据")
    st.caption("下面这些信息如果能补充，改写会更有说服力；不知道就留空。")
    for question in fact_questions:
        st.text(f"• {question}")

fact_answers = st.text_area(
    "补充真实事实（可选）",
    key=f"facts_{analysis_key}",
    height=130,
    placeholder="例如：活动覆盖 3,200 人；转化率从 6% 提升到 9%；团队共 5 人…",
    help="只填写你能确认的事实，不要在这里填写新的联系方式。",
)

rewrite_key = hashlib.sha256(
    f"{analysis_key}\0{fact_answers.strip()}".encode("utf-8")
).hexdigest()

if st.button("生成事实可信的优化版", use_container_width=True):
    if _can_call_model():
        try:
            st.session_state.llm_call_count += 1
            with st.spinner("正在重写，并检查是否引入了未提供的事实…"):
                rewritten = rewrite_resume(
                    resume_text,
                    result,
                    target_role=target_role,
                    job_description=job_description,
                    fact_answers=fact_answers,
                )
            st.session_state.rewrite_key = rewrite_key
            st.session_state.rewritten = rewritten
            st.rerun()
        except Exception as exc:
            logger.exception("Resume rewrite failed (%s)", type(exc).__name__)
            if "DEEPSEEK_API_KEY" in str(exc):
                st.error(str(exc))
            else:
                st.error("优化版生成失败，请稍后重试。原始报告仍然保留。")

rewritten = (
    st.session_state.rewritten
    if st.session_state.rewrite_key == rewrite_key
    else ""
)

if rewritten:
    st.divider()
    st.markdown("## 优化前后对比")
    diff_html = diff_to_html(compute_diff(resume_text, rewritten))
    st.iframe(diff_html, height=640)

    stem = _safe_download_stem(uploaded_file.name)
    col_md, col_docx = st.columns(2)
    with col_md:
        st.download_button(
            "下载 Markdown",
            data=rewritten,
            file_name=f"{stem}_CVOpenMic.md",
            mime="text/markdown",
            use_container_width=True,
        )
    with col_docx:
        st.download_button(
            "下载 ATS 友好 DOCX",
            data=create_docx_bytes(rewritten, title=f"{stem} 优化简历"),
            file_name=f"{stem}_CVOpenMic.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            use_container_width=True,
        )

_render_footer()
