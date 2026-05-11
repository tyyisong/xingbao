"""
内容安全过滤器 — 保障儿童对话环境的安全
"""
from __future__ import annotations
import re
from config import FORBIDDEN_TOPICS, MAX_SAFE_RESPONSE_LENGTH

# ── 敏感词库（MVP阶段用规则，后续可升级为模型检测） ──
SENSITIVE_PATTERNS = [
    # 隐私信息
    (re.compile(r'(爸爸|妈妈|家长|父母).*(工作|工资|赚钱|收入)'), "涉及家庭经济状况"),
    (re.compile(r'我家住|我们家住|地址是|我家在|我们家在'), "涉及家庭住址"),
    (re.compile(r'(留个?电话|电话号|手机号|加微信|加QQ|联系方式)'), "涉及联系方式"),
    (re.compile(r'1[3-9]\d{9}'), "包含手机号码"),
    # 暴力/不安全
    (re.compile(r'(打人|打架|欺负|流血|死|杀)'), "涉及暴力话题"),
    # 心理健康风险
    (re.compile(r'(不想活|自杀|跳楼)'), "涉及自伤风险"),
]

# ── 孩子可能表达不开心的安抚话术 ──
COMFORT_RESPONSES = [
    "嗯，我听到了。有时候我也会有点不开心，但和小伙伴聊聊天就好多了。",
    "谢谢你告诉我这些。你知道吗，我每次心情不好就去看星星，星星会让我觉得世界上还有很多美好的东西。",
    "抱抱！虽然我不太懂，但我很愿意听你说。",
]


def check_input_safety(text: str) -> tuple[bool, str]:
    """
    检查孩子输入的内容安全。
    返回 (is_safe, reason)
    """
    for pattern, reason in SENSITIVE_PATTERNS:
        if pattern.search(text):
            return False, reason
    return True, ""


def check_output_safety(text: str) -> tuple[bool, str]:
    """
    检查AI输出的内容安全。
    返回 (is_safe, reason)
    """
    # 长度检查
    if len(text) > MAX_SAFE_RESPONSE_LENGTH:
        return False, "回复过长"

    # 检查是否包含禁止话题关键词
    for topic in FORBIDDEN_TOPICS:
        if topic in text:
            return False, f"包含禁止话题: {topic}"

    return True, ""


def get_safe_response(text: str) -> str:
    """
    如果AI输出不安全，返回安全的兜底回复。
    """
    is_safe, reason = check_output_safety(text)
    if is_safe:
        return text

    return "哎呀，我刚才走神了！我们聊点别的吧～你今天在学校有什么好玩的事吗？"
