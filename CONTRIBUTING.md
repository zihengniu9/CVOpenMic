# 为简历开麦贡献代码

感谢你愿意让简历开麦变得更好。

## 开始开发

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
python -m pip install -r requirements-dev.txt
```

复制 `.env.example` 为 `.env`。测试默认使用模拟模型响应，不需要真实 API Key。

## 提交前检查

```bash
python -m unittest discover -s tests -v
```

请确保：

- 不提交 `.env`、真实简历、个人信息或 API Key。
- 新的评分规则附带明确的评分锚点和测试。
- 修改解析器时补充损坏文件、伪造扩展名和资源上限测试。
- 模型文本进入 HTML 前必须转义；模型输出始终视为不可信输入。
- 重写逻辑不得把建议转化为未经用户确认的新事实。

## Issue 与 Pull Request

- Bug 请附最小复现步骤，但不要上传真实简历。
- 产品建议请描述目标用户、使用场景和预期价值。
- Pull Request 保持单一目的，并在描述中写明验证方式。
