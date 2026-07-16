"""在文本发往外部模型前，对常见简历隐私字段做可逆脱敏。"""

from __future__ import annotations

import base64
import hmac
import re
import secrets
from collections.abc import Mapping


_EMAIL_RE = re.compile(
    r"(?<![\w.+-])"
    r"[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+"
    r"@[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?"
    r"(?:\.[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?)+"
    r"(?![\w.-])"
)

# 中国大陆 18 位与旧版 15 位身份证号。日期合法性由上游业务校验，这里只负责识别脱敏。
_ID_RE = re.compile(
    r"(?<!\d)(?:"
    r"\d{6}(?:18|19|20)\d{2}(?:0[1-9]|1[0-2])(?:0[1-9]|[12]\d|3[01])\d{3}[0-9Xx]"
    r"|"
    r"\d{6}\d{2}(?:0[1-9]|1[0-2])(?:0[1-9]|[12]\d|3[01])\d{3}"
    r")(?!\d)"
)

# 支持 13800138000、+86 13800138000、138-0013-8000 等常见写法。
_PHONE_RE = re.compile(r"(?<!\d)(?:\+?86[\s-]?)?1[3-9]\d(?:[\s-]?\d){8}(?!\d)")

_PATTERNS = (
    ("EMAIL", _EMAIL_RE),
    ("ID", _ID_RE),
    ("PHONE", _PHONE_RE),
)

# 仅驻留当前进程内存。相同值在同一进程内 token 稳定，同时避免手机号等低熵字段
# 被拿到 token 后离线枚举。服务重启后 token 改变不影响请求内恢复。
_TOKEN_KEY = secrets.token_bytes(32)


def _token_for(kind: str, value: str) -> str:
    """生成不含原文、跨调用稳定的 token。"""

    digest = hmac.digest(
        _TOKEN_KEY,
        f"CVOpenMic\0{kind}\0{value}".encode("utf-8"),
        "sha256",
    )
    fingerprint = base64.b32encode(digest).decode("ascii").rstrip("=")[:20]
    return f"<PII_{kind}_{fingerprint}>"


def redact_sensitive_data(text: str) -> tuple[str, dict[str, str]]:
    """脱敏邮箱、手机号和身份证号，返回脱敏文本及 token→原文映射。

    token 由进程内随机密钥、字段类型和原始值确定：同一进程内相同原文会稳定得到
    相同 token，重复出现也只保留一份映射。映射仅应存在当前请求内存中，不应记录
    到日志或发送给模型。
    """

    if not isinstance(text, str):
        raise TypeError("text 必须是字符串")

    redacted = text
    mapping: dict[str, str] = {}

    for kind, pattern in _PATTERNS:

        def replace(match: re.Match[str], *, _kind: str = kind) -> str:
            original = match.group(0)
            token = _token_for(_kind, original)
            previous = mapping.get(token)
            if previous is not None and previous != original:
                # 20 个 Base32 字符已有 100 bit；不要在理论碰撞时复用映射。
                raise RuntimeError("隐私 token 发生碰撞，请重试")
            mapping[token] = original
            return token

        redacted = pattern.sub(replace, redacted)

    return redacted, mapping


def restore_sensitive_data(text: str, mapping: Mapping[str, str]) -> str:
    """使用当前请求的映射恢复隐私 token；未知 token 保持原样。"""

    if not isinstance(text, str):
        raise TypeError("text 必须是字符串")
    if not isinstance(mapping, Mapping):
        raise TypeError("mapping 必须是映射")

    restored = text
    # 先替换较长 token，避免未来 token 命名出现前缀重叠。
    for token in sorted(mapping, key=len, reverse=True):
        original = mapping[token]
        if not isinstance(token, str) or not isinstance(original, str):
            raise TypeError("mapping 的键和值都必须是字符串")
        restored = restored.replace(token, original)
    return restored
