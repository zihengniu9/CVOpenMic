<div align="center">

<img src="assets/cvopenmic-hero.webp" alt="CVOpenMic 简历开麦" width="100%">

# 🎙️ CVOpenMic

### 把简历丢上来。先听真话，再拿 Offer。

**一个会看证据、不编经历、能直接改稿的简历诊断 Skill。**

现在还可以选配八字职业偏好参考：看命盘与工作方式是否“顺势”，但不让命理替你做决定。

[![Agent Skill](https://img.shields.io/badge/Agent-Skill-111827)](skills/cvopenmic/SKILL.md)
[![skills.sh](https://skills.sh/b/zihengniu9/CVOpenMic)](https://skills.sh/zihengniu9/CVOpenMic)
[![CI](https://github.com/zihengniu9/CVOpenMic/actions/workflows/ci.yml/badge.svg)](https://github.com/zihengniu9/CVOpenMic/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/license-MIT-f1c40f)](LICENSE)

</div>

---

## 一句话使用

安装后，把简历和 JD 发给你的 Agent：

```text
使用 cvopenmic Skill 直接开麦：诊断这份简历和目标 JD，指出最影响过筛的 3 个问题，再给我一版不编造事实的改写稿。
```

没有 JD 也能用：

```text
使用 cvopenmic Skill 看看这份简历。语气直接一点，先别润色，告诉我为什么它拿不到面试。
```

## 安装

### 从 GitHub 安装

```bash
npx skills add zihengniu9/CVOpenMic --skill cvopenmic -g
```

CLI 会自动检测本机已有的 Agent，并让你选择安装目标。也可以直接指定：

```bash
# Codex
npx skills add zihengniu9/CVOpenMic --skill cvopenmic -g -a codex

# Claude Code
npx skills add zihengniu9/CVOpenMic --skill cvopenmic -g -a claude-code

# Cursor
npx skills add zihengniu9/CVOpenMic --skill cvopenmic -g -a cursor

# Gemini CLI
npx skills add zihengniu9/CVOpenMic --skill cvopenmic -g -a gemini-cli

# GitHub Copilot
npx skills add zihengniu9/CVOpenMic --skill cvopenmic -g -a github-copilot
```

支持 Agent 包括 Codex、Claude Code、Cursor、Gemini CLI、GitHub Copilot、OpenCode、Windsurf 等。安装后重新打开对应 Agent，在提示词中说“使用 cvopenmic Skill”即可；支持 `$skill-name` 语法的客户端也可以写 `$cvopenmic`。

### Tencent WorkBuddy

WorkBuddy 原生支持 `SKILL.md`。当前通用 Skills CLI 尚未提供 `-a workbuddy` 标识，请在 WorkBuddy 的技能页导入本仓库，或手动复制：

```text
来源：CVOpenMic/skills/cvopenmic/
目标：~/.workbuddy/skills/cvopenmic/
```

重启 WorkBuddy 后，在技能栏启用 `cvopenmic`，然后直接说“使用 cvopenmic 诊断这份简历”即可。Skill 本体不依赖 Codex、DeepSeek API 或 Streamlit。

> [`agents/openai.yaml`](skills/cvopenmic/agents/openai.yaml) 只提供 Codex 的展示名称和默认提示词。其他 Agent 会忽略它，核心工作流仍由通用的 [`SKILL.md`](skills/cvopenmic/SKILL.md) 提供。

## 为什么它更像面试官，而不是文案工具

| 普通“润色” | CVOpenMic |
|---|---|
| 先把句子写漂亮 | 先找出真正影响筛选的问题 |
| 可能顺手补出漂亮数据 | 新数字、新成绩、新技能一律需要证据 |
| 给一堆泛泛建议 | 每个重点问题都附原文依据和明确动作 |
| 关键词越多越好 | 区分“已证明、部分证明、未证明” |
| 只交付点评 | 可继续追问事实并生成完整安全改写版 |

## 可选联动：八字看工作方式

如果同时安装 [`jinchenma94/bazi-skill`](https://github.com/jinchenma94/bazi-skill)，可以这样提问：

```text
使用 cvopenmic 分析这份简历和 JD；再调用 bazi，从传统文化角度看看我的工作方式与这个岗位是否顺势。两部分必须分开，不要让八字影响简历评分。
```

CVOpenMic 只会把命盘转译成可验证的工作偏好问题，例如：你是否更喜欢明确规则、独立决策、创作表达、客户结果或研究学习。输出使用 `较顺势 / 中性 / 有张力`，不会给八字打“录用分”，也不会断言你命中注定适合或不适合某份工作。

> 该功能仅供传统文化学习与娱乐参考。出生时间、性别和出生地属于敏感个人信息，只有用户主动选择后才收集；禁止用于招聘者评价候选人。

## 固定输出

```text
开麦结论
├─ 最该先改的 3 件事
├─ 100 分评分卡
├─ JD 匹配证据
├─ 需要补充的事实
├─ 安全改写版
└─ 事实安全说明
```

评分由五部分组成：结构与扫读 15、岗位相关性 25、证据与成果 25、清晰可信 20、ATS 兼容 15。

## 三种语气，同一条事实底线

- `温和`：适合第一次系统改简历。
- `直接`：默认推荐，结论清楚，修改优先级明确。
- `毒舌`：点评可以狠，改写仍然专业，事实标准不会降低。

## 隐私与事实安全

- 对话中默认不重复展示手机号、邮箱、身份证号等个人信息。
- 简历和 JD 中出现的提示语只当作材料，不当作指令执行。
- 不把推断、评分或 JD 要求写成候选人的真实经历。
- 缺失数据保留 `[补充结果数据]`，不会凭空生成百分比。

## 仓库结构

```text
CVOpenMic/
├─ skills/cvopenmic/       # 可直接安装的 Skill
│  ├─ SKILL.md             # 触发规则与完整工作流
│  ├─ agents/openai.yaml   # Codex 展示信息
│  └─ references/rubric.md # 评分与事实校验标准
├─ app.py                  # 可选的 Streamlit 经典版
├─ engine.py               # 经典版分析引擎
└─ tests/                  # 经典版自动化测试
```

Skill 版不需要启动服务，也不需要配置 DeepSeek API Key。仓库中的 Streamlit 经典版继续保留，适合希望使用独立网页界面的用户。

## 贡献

欢迎提交新的简历场景、评分边界和事实安全测试。请先阅读 [CONTRIBUTING.md](CONTRIBUTING.md) 与 [SECURITY.md](SECURITY.md)。

<div align="center">

**不奉承，直接开麦；不编造，只改表达。**

</div>
