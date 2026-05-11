"""
对话引擎 — 星宝的核心大脑，管理对话流程、API调用和状态协调
"""
from __future__ import annotations
from openai import OpenAI
from config import (
    DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, DEEPSEEK_MODEL,
    EVOLUTION_BRANCHES,
)
from engine.persona import PERSONA_SYSTEM_PROMPT
from engine.safety import check_input_safety, check_output_safety, get_safe_response
from engine.tagging import InterestTagger, InterestAccumulator
from models.user import ChildUser
from models.star_baby import StarBaby
from models.report import TalentReport, WeeklyBrief


class DialogueEngine:
    """星宝对话引擎 — 整合所有子系统"""

    def __init__(self, child_name: str, child_age: int = 8):
        self.client = OpenAI(
            api_key=DEEPSEEK_API_KEY,
            base_url=DEEPSEEK_BASE_URL,
        )
        self.child = ChildUser(
            user_id=f"child_{child_name}",
            nickname=child_name,
            age=child_age,
        )
        self.star_baby = StarBaby()
        self.tagger = InterestTagger(use_api=True)
        self.accumulator = InterestAccumulator()
        self.message_count = 0  # 用于控制主动提问节奏

    # ── 核心对话接口 ──

    def chat(self, child_input: str) -> str:
        """处理一轮对话：安全校验 → 兴趣标注 → AI回复 → 能量结算"""
        # 1. 安全检查
        is_safe, reason = check_input_safety(child_input)
        if not is_safe:
            return self._safe_redirect(reason)

        # 2. 兴趣标注
        context = self.child.get_recent_context(turns=6)
        full_context = context + f"\n孩子: {child_input}"
        tags, keywords = self.tagger.tag(child_input, full_context)
        self.accumulator.add(tags, keywords)

        # 3. 生成回复
        self.message_count += 1
        response = self._generate_response(child_input, tags)

        # 4. 输出安全检查
        safe_response = get_safe_response(response)

        # 5. 记录对话
        self.child.add_dialogue("child", child_input, tags)
        self.child.add_dialogue("star_baby", safe_response)

        # 6. 能量结算
        tag_richness = sum(tags.values()) / len(tags)  # 本次标注的平均丰富度
        gained = self.star_baby.gain_energy(tag_richness)

        # 7. 检查进化
        if self.star_baby.can_evolve():
            branch = self.accumulator.determine_branch()
            event = self.star_baby.evolve(branch)
            if event:
                safe_response += f"\n\n{event.message}\n{EVOLUTION_BRANCHES[branch]['visual']}"

        return safe_response

    def _generate_response(self, child_input: str, tags: dict[str, float]) -> str:
        """调用DeepSeek API生成星宝的回复"""
        # 构建对话模式
        mode_hint = ""
        if self.message_count % 4 == 0:
            mode_hint = "\n【提示：这轮你应该主动提出一个开放式问题，引导孩子分享新知识。】"
        if self.star_baby.can_evolve():
            mode_hint += f"\n【重要：星宝的能量快满了，孩子表现出对以下领域的强烈兴趣：{self._describe_interests(tags)}。请在对话中适当体现你很好奇这个领域。】"

        messages = [
            {"role": "system", "content": PERSONA_SYSTEM_PROMPT + mode_hint},
        ]

        # 添加历史上下文
        for turn in self.child.dialogue_history[-8:]:
            role = "user" if turn.role == "child" else "assistant"
            messages.append({"role": role, "content": turn.content})

        # 添加当前输入
        messages.append({"role": "user", "content": child_input})

        try:
            response = self.client.chat.completions.create(
                model=DEEPSEEK_MODEL,
                messages=messages,
                temperature=0.8,
                max_tokens=200,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"哎呀，我刚才走神了～你能再说一遍吗？（{e}）"

    def _describe_interests(self, tags: dict[str, float]) -> str:
        """将标注结果转为人话"""
        top = sorted(tags.items(), key=lambda x: x[1], reverse=True)[:2]
        from config import INTEREST_DIMENSIONS
        return "、".join([INTEREST_DIMENSIONS[d]["label"] for d, s in top if s > 3])

    def _safe_redirect(self, reason: str) -> str:
        """当内容不安全时，安全转移话题"""
        return "嗯...我们聊点别的吧！你今天在学校有没有学到什么有趣的知识呀？"

    # ── 批量测试接口 ──

    def run_simulated_conversation(self, dialogues: list[str], verbose: bool = True) -> dict:
        """用一组模拟对话跑通完整链路，返回最终状态"""
        for i, msg in enumerate(dialogues):
            reply = self.chat(msg)
            if verbose:
                print(f"\n{'─'*40}")
                print(f"👦 孩子: {msg}")
                print(f"⭐ 星宝: {reply}")
                from config import ENERGY_MAX_LEVEL_10
                print(f"🔋 能量: {self.star_baby.energy}/{ENERGY_MAX_LEVEL_10}")
                if self.star_baby.current_branch:
                    print(f"🌿 已转职: {self.star_baby.current_form}")

        return self.summary()

    # ── CLI交互接口 ──

    def interactive(self):
        """命令行交互模式 — 直接和星宝聊天"""
        print("\n🌟 === 星宝 · 你的AI成长伙伴 === 🌟")
        print("（输入 'quit' 退出，输入 'status' 查看星宝状态，输入 'report' 查看天赋报告）\n")

        while True:
            try:
                user_input = input("👦 你: ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\n\n星宝要回家啦，下次再见哦～👋")
                break

            if not user_input:
                continue
            if user_input.lower() == "quit":
                print("星宝: 你要走了吗？下次再来教我新东西哦～👋")
                break
            if user_input.lower() == "status":
                print(f"\n{self.star_baby.status()}\n")
                continue
            if user_input.lower() == "report":
                print(f"\n{self.accumulator.summary()}\n")
                continue

            reply = self.chat(user_input)
            print(f"⭐ 星宝: {reply}\n")

    # ── 状态查询 ──

    def summary(self) -> dict:
        """返回引擎当前状态摘要"""
        return {
            "child": self.child.nickname,
            "interactions": self.child.get_total_interactions(),
            "star_baby_level": self.star_baby.level,
            "star_baby_energy": self.star_baby.energy,
            "current_form": self.star_baby.current_form,
            "evolution_branch": self.star_baby.current_branch,
            "dominant_interest": self.accumulator.get_dominant_dimension(),
            "radar": self.accumulator.get_radar_data(),
            "evolution_history": [
                {"from": e.from_level, "to": e.to_level, "branch": e.branch}
                for e in self.star_baby.evolution_history
            ],
        }

    def get_parent_report(self) -> str:
        """获取家长端天赋报告"""
        report = TalentReport.generate(
            child_nickname=self.child.nickname,
            accumulator=self.accumulator,
        )
        return report.format_for_parent()

    def get_weekly_brief(self) -> str:
        """获取免费版周报"""
        dim = self.accumulator.get_dominant_dimension()
        from config import INTEREST_DIMENSIONS
        brief = WeeklyBrief(
            child_nickname=self.child.nickname,
            total_interactions=self.child.get_total_interactions(),
            top_dimension=dim,
            top_dimension_label=INTEREST_DIMENSIONS[dim]["label"],
            hot_topics=list(set(self.accumulator.top_keywords))[:10],
        )
        return brief.format()
