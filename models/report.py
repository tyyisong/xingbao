"""
天赋报告生成器 — 为家长端生成兴趣分析报告
"""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from engine.tagging import InterestAccumulator
from config import INTEREST_DIMENSIONS, EVOLUTION_BRANCHES


@dataclass
class TalentReport:
    """天赋分析报告"""
    child_nickname: str
    generated_at: datetime = field(default_factory=datetime.now)
    total_interactions: int = 0
    active_days: int = 0
    dominant_dimension: str = ""
    evolution_branch: str = ""
    radar_data: dict[str, float] = field(default_factory=dict)
    top_keywords: list[str] = field(default_factory=list)
    summary: str = ""
    suggestion: str = ""

    def format_for_parent(self) -> str:
        """格式化为家长可读的报告文本"""
        dim = INTEREST_DIMENSIONS
        branch = EVOLUTION_BRANCHES

        lines = [
            "╔════════════════════════════════╗",
            f"║   🌟 星宝 · 天赋观察报告 🌟   ║",
            "╚════════════════════════════════╝",
            "",
            f"👶 孩子: {self.child_nickname}",
            f"📅 报告周期: 首周观察",
            f"💬 有效互动: {self.total_interactions} 次",
            "",
            "━━━━ 兴趣雷达图 ━━━━",
        ]

        for dim_key, score in sorted(self.radar_data.items(), key=lambda x: x[1], reverse=True):
            bar = "█" * int(score / 10) + "░" * (10 - int(score / 10))
            lines.append(f"  {dim[dim_key]['icon']} {dim[dim_key]['label']:　<6} {bar} {score:.0f}%")

        lines.extend([
            "",
            "━━━━ 核心发现 ━━━━",
            f"🏆 主导兴趣: {dim[self.dominant_dimension]['label']}",
            f"🌿 进化倾向: {branch[self.evolution_branch]['name']}",
            f"📝 {self.summary}",
            "",
            "━━━━ 教育建议 ━━━━",
            f"💡 {self.suggestion}",
            "",
            "━━━━ 热门话题词 ━━━━",
            f"🔤 {', '.join(self.top_keywords[:15]) if self.top_keywords else '数据积累中...'}",
            "",
            "─" * 40,
            "⚠️ 本报告基于AI互动数据分析生成，",
            "   仅供家长参考，不替代专业教育评估。",
            "   数据来源：孩子在「星宝」APP中的自然对话。",
        ])

        return "\n".join(lines)

    @staticmethod
    def generate(
        child_nickname: str,
        accumulator: InterestAccumulator,
        active_days: int = 7,
    ) -> "TalentReport":
        """从兴趣累加器生成报告"""
        dominant = accumulator.get_dominant_dimension()
        branch = accumulator.determine_branch()
        radar = accumulator.get_radar_data()

        # 生成教育建议
        suggestions = {
            "science": "建议为孩子提供科学实验套装、天文望远镜等探索工具，带孩子参观科技馆。",
            "art": "建议提供丰富的绘画材料，鼓励参加音乐或舞蹈体验课，多带孩子看艺术展览。",
            "logic": "建议引入数独、编程积木、棋类等逻辑游戏，可以考虑少儿编程启蒙课程。",
            "language": "建议增加亲子阅读时间，鼓励孩子写日记或编故事，可以参加朗诵或戏剧活动。",
            "social": "建议多组织小组活动，鼓励团队运动，培养孩子的领导力和合作能力。",
            "nature": "建议增加户外活动时间，带孩子露营、观察动植物，建立自然探索笔记本。",
        }

        return TalentReport(
            child_nickname=child_nickname,
            total_interactions=accumulator.total_messages,
            active_days=active_days,
            dominant_dimension=dominant,
            evolution_branch=branch,
            radar_data=radar,
            top_keywords=list(set(accumulator.top_keywords))[:20],
            summary=f"孩子在 {INTEREST_DIMENSIONS[dominant]['label']} 维度表现最为活跃，"
                    f"互动中频繁展现出对相关话题的好奇心和表达欲。"
                    f"星宝进化为「{EVOLUTION_BRANCHES[branch]['name']}」分支。",
            suggestion=suggestions.get(dominant, "建议持续观察孩子的兴趣变化，保持多元化的体验机会。"),
        )


@dataclass
class WeeklyBrief:
    """每周简报 — 免费版家长报告（轻量版）"""
    child_nickname: str
    total_interactions: int
    top_dimension: str
    top_dimension_label: str
    hot_topics: list[str]

    def format(self) -> str:
        lines = [
            f"📊 {self.child_nickname}的本周互动速览",
            f"💬 本周互动 {self.total_interactions} 次",
            f"🏆 最活跃领域: {self.top_dimension_label}",
            f"🔤 热门话题: {', '.join(self.hot_topics[:8])}",
            "",
            "🔒 解锁完整天赋报告，查看多元智能雷达图 →",
        ]
        return "\n".join(lines)
