"""
兴趣标注引擎 — 从对话中提取关键词并标注兴趣维度
"""
from __future__ import annotations
import json
import re
from openai import OpenAI
from config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, DEEPSEEK_MODEL, INTEREST_DIMENSIONS
from engine.persona import INTEREST_TAGGING_PROMPT

# ── 关键词-兴趣映射表（规则层，快速标注） ──
KEYWORD_MAP = {
    "science": ["星星", "太空", "宇宙", "星球", "太阳", "月亮", "地球", "恐龙",
                 "化石", "实验", "科学", "火山", "地震", "矿石", "显微镜", "放大镜",
                 "为什么天", "为什么水", "为什么火", "闪电", "彩虹"],
    "art": ["画画", "颜色", "彩色", "唱歌", "跳舞", "音乐", "钢琴", "小提琴",
            "吉他", "手工", "折纸", "剪纸", "泥塑", "涂鸦", "颜料", "画笔",
            "好听", "好看", "漂亮"],
    "logic": ["数学", "数字", "计算", "等于", "加", "减", "乘", "除",
              "谜语", "解谜", "推理", "规律", "积木", "乐高", "编程", "代码",
              "象棋", "围棋", "数独", "排序", "分类"],
    "language": ["故事", "讲故事", "语文", "汉字", "写字", "拼音", "成语",
                 "阅读", "读书", "课文", "古诗", "朗诵", "日记", "作文", "造句"],
    "social": ["同学", "朋友", "好朋友", "同桌", "班长", "小组", "帮助",
               "分享", "一起", "教我", "教他", "吵架", "和好", "过生日"],
    "nature": ["动物", "小狗", "小猫", "兔子", "鸟", "鱼", "昆虫", "蝴蝶",
               "蚂蚁", "花", "草", "树叶", "公园", "户外", "爬山", "游泳",
               "下雨", "刮风", "下雪", "云", "天气"],
}


class InterestTagger:
    """对话兴趣标注器"""

    def __init__(self, use_api: bool = True):
        self.use_api = use_api
        self.client = None
        if use_api:
            self.client = OpenAI(
                api_key=DEEPSEEK_API_KEY,
                base_url=DEEPSEEK_BASE_URL,
            )

    def tag_by_keywords(self, text: str) -> dict[str, float]:
        """基于关键词规则的快速标注"""
        scores = {dim: 0.0 for dim in INTEREST_DIMENSIONS}
        text_lower = text.lower()

        for dim, keywords in KEYWORD_MAP.items():
            hit_count = sum(1 for kw in keywords if kw in text_lower)
            if hit_count > 0:
                # 每个命中得2分，上限10分
                scores[dim] = min(hit_count * 2.0, 10.0)

        return scores

    def tag_by_api(self, dialogue_context: str) -> dict[str, float]:
        """基于DeepSeek API的智能标注"""
        if not self.client:
            return self.tag_by_keywords(dialogue_context)

        try:
            response = self.client.chat.completions.create(
                model=DEEPSEEK_MODEL,
                messages=[
                    {"role": "system", "content": INTEREST_TAGGING_PROMPT},
                    {"role": "user", "content": f"请分析这段对话中孩子的兴趣表现：\n{dialogue_context}"},
                ],
                temperature=0.1,
                max_tokens=150,
            )
            result = response.choices[0].message.content.strip()
            # 解析JSON
            return json.loads(result)
        except Exception as e:
            print(f"  [标注API调用失败: {e}] 降级为关键词标注")
            return self.tag_by_keywords(dialogue_context)

    def extract_keywords(self, text: str) -> list[str]:
        """从文本中提取匹配到的兴趣关键词"""
        found = []
        text_lower = text.lower()
        for dim, keywords in KEYWORD_MAP.items():
            for kw in keywords:
                if kw in text_lower and kw not in found:
                    found.append(kw)
        return found

    def tag(self, child_message: str, full_context: str = "") -> tuple[dict[str, float], list[str]]:
        """综合标注：先用关键词快速标注，重要对话调用API。
        返回 (兴趣分数, 匹配到的关键词列表)"""
        kw_scores = self.tag_by_keywords(child_message)
        keywords = self.extract_keywords(child_message)

        # 如果关键词命中数 >= 2，说明信息量足够，不调API
        hit_count = sum(1 for v in kw_scores.values() if v > 0)
        if hit_count >= 2 or not self.use_api:
            return kw_scores, keywords

        # 否则调用API做更精细的标注
        return self.tag_by_api(full_context if full_context else child_message), keywords


# ── 兴趣累计器 ──
class InterestAccumulator:
    """累积对话中的兴趣分数，追踪孩子的兴趣倾向"""

    def __init__(self):
        self.dimension_scores = {dim: 0.0 for dim in INTEREST_DIMENSIONS}
        self.dimension_counts = {dim: 0 for dim in INTEREST_DIMENSIONS}
        self.total_messages = 0
        self.top_keywords: list[str] = []

    def add(self, tag_scores: dict[str, float], keywords: list[str] = None):
        """累加一次标注结果"""
        for dim, score in tag_scores.items():
            if score > 0:
                self.dimension_scores[dim] += score
                self.dimension_counts[dim] += 1
        self.total_messages += 1
        if keywords:
            self.top_keywords.extend(keywords)

    def get_dominant_dimension(self) -> str:
        """获取当前最突出的兴趣维度"""
        if self.total_messages == 0:
            return "language"  # 默认偏语言
        return max(self.dimension_scores, key=self.dimension_scores.get)

    def get_radar_data(self) -> dict[str, float]:
        """获取归一化后的雷达图数据（0-100）"""
        if self.total_messages == 0:
            return {dim: 0.0 for dim in INTEREST_DIMENSIONS}

        max_score = max(self.dimension_scores.values()) or 1.0
        return {
            dim: round(self.dimension_scores[dim] / max_score * 100, 1)
            for dim in INTEREST_DIMENSIONS
        }

    def determine_branch(self) -> str:
        """根据兴趣累积判断应该进化的分支"""
        # 按分支聚合分数
        branch_scores = {"scholar": 0.0, "artist": 0.0, "engineer": 0.0}
        for dim, info in INTEREST_DIMENSIONS.items():
            branch_scores[info["branch"]] += self.dimension_scores[dim]

        return max(branch_scores, key=branch_scores.get)

    def summary(self) -> str:
        """生成兴趣摘要"""
        dominant = self.get_dominant_dimension()
        branch = self.determine_branch()
        radar = self.get_radar_data()

        top3 = sorted(radar.items(), key=lambda x: x[1], reverse=True)[:3]
        lines = [f"📊 互动分析 (共{self.total_messages}条有效对话)"]
        lines.append(f"🏆 主导维度: {INTEREST_DIMENSIONS[dominant]['label']}")
        lines.append(f"🌿 进化倾向: {branch}")
        lines.append("📈 兴趣雷达:")
        for dim, score in top3:
            bar = "█" * int(score / 10) + "░" * (10 - int(score / 10))
            lines.append(f"  {INTEREST_DIMENSIONS[dim]['icon']} {INTEREST_DIMENSIONS[dim]['label']}: {bar} {score:.0f}%")
        return "\n".join(lines)
