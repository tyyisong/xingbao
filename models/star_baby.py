"""
星宝进化模型 — 管理星宝的等级、能量、形态和转职状态
"""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from config import ENERGY_PER_MESSAGE, ENERGY_MAX_LEVEL_10, EVOLUTION_BRANCHES


@dataclass
class EvolutionEvent:
    """一次进化事件"""
    timestamp: datetime
    from_level: int
    to_level: int
    branch: str
    message: str


@dataclass
class StarBaby:
    """星宝的完整状态"""
    name: str = "星宝"
    level: int = 1
    energy: int = 0
    current_branch: str | None = None    # 当前进化分支
    current_form: str = "初始形态"         # 当前形态名称
    evolution_history: list[EvolutionEvent] = field(default_factory=list)
    total_dialogues: int = 0

    def gain_energy(self, tag_score: float = 1.0) -> int:
        """
        每次有效互动获得能量。
        tag_score 是本次互动的兴趣标注质量（用于加权），
        如果孩子教了有深度的内容，给更多能量。
        """
        base = ENERGY_PER_MESSAGE
        bonus = int(tag_score / 10)  # 0-1 bonus based on interest richness
        gained = base + bonus
        self.energy = min(self.energy + gained, ENERGY_MAX_LEVEL_10)
        self.total_dialogues += 1
        return gained

    def can_evolve(self) -> bool:
        """是否满足进化条件"""
        return self.energy >= ENERGY_MAX_LEVEL_10 and self.level < 10

    def evolve(self, branch: str) -> EvolutionEvent | None:
        """执行进化转职"""
        if branch not in EVOLUTION_BRANCHES:
            return None

        old_level = self.level
        self.level = 10
        self.current_branch = branch
        self.current_form = EVOLUTION_BRANCHES[branch]["name"]
        self.energy = 0  # 重置能量，准备下一阶段

        event = EvolutionEvent(
            timestamp=datetime.now(),
            from_level=old_level,
            to_level=self.level,
            branch=branch,
            message=f"🌟 星宝进化了！从{old_level}级进化到{self.level}级，转职为「{self.current_form}」！",
        )
        self.evolution_history.append(event)
        return event

    def status(self) -> str:
        """获取星宝当前状态摘要"""
        bar_len = 10
        filled = int(self.energy / ENERGY_MAX_LEVEL_10 * bar_len)
        bar = "█" * filled + "░" * (bar_len - filled)
        lines = [
            f"⭐ {self.name} Lv.{self.level}",
            f"🔋 能量: [{bar}] {self.energy}/{ENERGY_MAX_LEVEL_10}",
            f"🎭 形态: {self.current_form}",
        ]
        if self.current_branch:
            lines.append(f"🌿 分支: {EVOLUTION_BRANCHES[self.current_branch]['name']}")
        return "\n".join(lines)
