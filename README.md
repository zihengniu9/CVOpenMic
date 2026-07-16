<div align="center">

<img src="assets/cvopenmic-hero.webp" alt="简历开麦：AI 简历真话官" width="100%">

# 🎙️ 简历开麦

### 先听真话，再拿 Offer。

**不是把废话润色得更像废话。**  
简历开麦会结合目标 JD，指出最影响过筛的问题，并在不编造经历的前提下，生成一份更能打的简历。

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.56%2B-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![DeepSeek](https://img.shields.io/badge/AI-DeepSeek-4D6BFE)](https://platform.deepseek.com/)
[![Tests](https://img.shields.io/badge/tests-30%20passing-2ED573)](#-质量与安全)
[![License](https://img.shields.io/badge/license-MIT-yellow)](LICENSE)

[快速开始](#-3-分钟跑起来) · [产品能力](#-它和普通-ai-简历工具有什么不同) · [Docker 部署](#-docker-部署) · [参与贡献](CONTRIBUTING.md)

</div>

---

## 为什么需要“开麦”？

大多数 AI 简历工具做的是“润色”。但求职者真正缺的，通常不是更华丽的措辞，而是三个答案：

1. **为什么这份简历过不了筛？**
2. **它和目标岗位到底差在哪？**
3. **怎么改，既有说服力又不编造？**

简历开麦把“毒舌”留给表达，把“证据”写进产品逻辑。

```text
上传简历 ──→ 自动脱敏 ──→ 快速体检 / JD 匹配
                                  │
                                  ▼
                         最优先的 3 个问题
                                  │
                     补充真实事实（可选）
                                  │
                                  ▼
                  可信改写 ──→ Diff 对比 ──→ DOCX
```

## ✨ 它和普通 AI 简历工具有什么不同？

<table>
  <tr>
    <td width="33%" valign="top">
      <h3>🎯 有岗位参照</h3>
      <p>不填 JD 时只做简历体检；粘贴目标 JD 后，才评价关键词覆盖和岗位匹配。</p>
    </td>
    <td width="33%" valign="top">
      <h3>🧾 不编造成绩</h3>
      <p>模型只能使用简历和用户补充的事实。缺数据就追问或保留占位符，不凭空造百分比。</p>
    </td>
    <td width="33%" valign="top">
      <h3>🔒 默认先脱敏</h3>
      <p>邮箱、手机号、身份证号在本地替换为随机 HMAC token，再发送给模型处理。</p>
    </td>
  </tr>
  <tr>
    <td width="33%" valign="top">
      <h3>🎚️ 三档语气</h3>
      <p>温和、直接、毒舌自由选择。风格可以变，评价依据不变。</p>
    </td>
    <td width="33%" valign="top">
      <h3>🔍 证据式诊断</h3>
      <p>每个问题都带原文依据和修改动作，总分由程序汇总，避免模型随口“拍分”。</p>
    </td>
    <td width="33%" valign="top">
      <h3>📄 真正能交付</h3>
      <p>查看逐行 Diff，并导出 Markdown 或 ATS 友好的可编辑 DOCX。</p>
    </td>
  </tr>
</table>

## 🧭 两种使用方式

### 1. 快速体检

没有具体岗位也能用。检查基础信息、结构可读性、经历成果、量化证据和语言专业度。

### 2. 岗位匹配

填写目标岗位并粘贴 JD，得到岗位关键词覆盖、相关经历匹配、缺口提示和针对性改写。

## 🎙️ 一句话产品哲学

> **可以把话说得狠，但不能把事实写得假。**

重写阶段会执行双重事实保护：

- Prompt 约束：诊断结果不能作为新增事实来源。
- 程序校验：如果优化稿出现原始材料中不存在的新数字，结果会被拦截。

## 🚀 3 分钟跑起来

### Windows

```powershell
Copy-Item .env.example .env
# 编辑 .env，填入 DEEPSEEK_API_KEY
start.bat
```

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
# 编辑 .env，填入 DEEPSEEK_API_KEY
streamlit run app.py
```

浏览器打开 [http://localhost:8501](http://localhost:8501)。DeepSeek API Key 可在 [DeepSeek 开放平台](https://platform.deepseek.com/) 创建。

> 图片简历 OCR 需要额外安装 Tesseract 和 `chi_sim` 中文语言包。PDF、DOCX 和 TXT 不依赖 Tesseract。

## 🐳 Docker 部署

```bash
docker build -t cvopenmic .
docker run --rm -p 8501:8501 --env-file .env cvopenmic
```

镜像采用非 root 用户运行，包含健康检查和中英文 OCR 依赖。`.env` 不会进入构建上下文或镜像层。

## 📦 支持格式

| 格式 | 支持情况 | 说明 |
|---|---:|---|
| PDF | ✅ | 最多 5 页；扫描 PDF 会提示改用图片 OCR |
| DOCX | ✅ | 尽量保持正文中段落与表格顺序 |
| PNG / JPG | ✅ | 需要 Tesseract OCR；限制解码像素数 |
| TXT | ✅ | 支持 UTF-8 与 GB18030 |
| DOC | ❌ | 请先另存为 DOCX 或 PDF |

单文件上限为 **5 MB**，简历文本和 JD 也有字符上限，避免超额调用与资源滥用。

## 🛡️ 质量与安全

当前测试覆盖：

- PII 脱敏与恢复、提示注入隔离。
- 评分 Schema、越界分数、程序汇总总分。
- 防止新数字编造，同时允许日期格式调整。
- PDF / DOCX / 图片签名、扫描 PDF、压缩包与像素限制。
- HTML 转义和 Diff 注入防护。
- Streamlit 上传 → 分析 → 重写 → 下载 → 换文件重置全流程。

```bash
python -m unittest discover -s tests -v
```

## 🧱 项目结构

```text
CVOpenMic/
├── app.py                 # Streamlit 产品界面与状态管理
├── engine.py              # 结构化诊断、评分与事实安全重写
├── privacy.py             # PII 脱敏与安全恢复
├── parser.py              # PDF / DOCX / 图片 / TXT 解析
├── differ.py              # 安全的前后版本对比
├── exporter.py            # ATS 友好 DOCX 导出
├── config.py              # 配置、评分维度和 Prompt
├── tests/                 # 单元与端到端流程测试
└── .github/workflows/     # GitHub Actions
```

## 🗺️ Roadmap

- [ ] 逐条接受 / 拒绝 / 重生成修改建议
- [ ] 中文简历、英文 Résumé、学术 CV 专属规则
- [ ] 一份主简历批量适配多个 JD
- [ ] 分享型“开麦诊断卡”
- [ ] 面试追问与项目证据清单
- [ ] 可选本地模型与更多兼容 API

## 🤝 一起把它做成更好的开源产品

欢迎提交 Bug、评分规则、解析样例和产品建议。开始前请阅读 [贡献指南](CONTRIBUTING.md) 和 [安全策略](SECURITY.md)。

如果简历开麦对你有帮助，欢迎点一个 **Star**。它会让更多正在求职的人先听到真话，再拿到 Offer。

<div align="center">

**🎙️ 简历开麦 · CVOpenMic**  
不奉承，直说问题；不编造，只改表达。

[MIT License](LICENSE)

</div>
