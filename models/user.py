"""
用户数据模型 — 孩子的基础信息和对话历史
"""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class DialogueTurn:
    """一轮对话"""
    timestamp: datetime
    role: str          # "child" or "star_baby"
    content: str
    interest_tags: dict[str, float] | None = None  # 本轮标注的兴趣分数


@dataclass
class ChildUser:
    """孩子用户模型"""
    user_id: str
    nickname: str
    age: int = 8
    created_at: datetime = field(default_factory=datetime.now)
    dialogue_history: list[DialogueTurn] = field(default_factory=list)

    def add_dialogue(self, role: str, content: str, tags: dict[str, float] | None = None):
        turn = DialogueTurn(
            timestamp=datetime.now(),
            role=role,
            content=content,
            interest_tags=tags,
        )
        self.dialogue_history.append(turn)

    def get_recent_context(self, turns: int = 10) -> str:
        """获取最近N轮对话的文本上下文，用于API调用"""
        recent = self.dialogue_history[-turns:]
        lines = []
        for t in recent:
            name = "孩子" if t.role == "child" else "星宝"
            lines.append(f"{name}: {t.content}")
        return "\n".join(lines)

    def get_total_interactions(self) -> int:
        """获取有效互动次数（孩子的发言次数）"""
        return sum(1 for t in self.dialogue_history if t.role == "child")
