"""
星宝 MVP — 入口程序
用法:
  python3 main.py                 交互模式，直接和星宝聊天
  python3 main.py --test          用模拟对话跑通链路
  python3 main.py --report        生成示例天赋报告
"""
import sys
from engine.dialogue import DialogueEngine

# ── 模拟对话数据（模拟一个8岁男孩"小明"的风格） ──
SIMULATED_DIALOGUES = [
    # 日常聊天 + 科学兴趣
    "星宝星宝，我今天学了太阳系！",
    "太阳有八个行星围着它转，地球是第三个！",
    "木星最大了，它上面有个大红斑，是风暴！",
    "我最喜欢火星，因为它是红色的，老师说可能有水。",
    "长大了我想当宇航员，飞到火星上去看看。",

    # 数学逻辑
    "今天数学课老师教我们乘法口诀了。",
    "一一得一，一二得二，二二得四，我背得可快了！",
    "七乘八等于五十六，这个最难记了。",
    "但是老师说有个口诀，七八五十六，像顺口溜一样。",

    # 艺术兴趣
    "美术课上我画了一只恐龙，老师说画得很好！",
    "我给恐龙涂了绿色，背上还有黄色的刺。",
    "我们班有个同学画画超厉害，她画的小动物像真的一样。",
    "我也想像她一样画得那么好。",

    # 社交分享
    "今天我和同桌一起搭了一个大城堡，用乐高！",
    "他负责搭城墙，我负责搭塔楼，我们合作得特别好。",
    "搭完了老师还给我们拍了照片，贴在教室后墙上。",
    "明天我们打算搭一个太空飞船，更酷！",

    # 自然观察
    "昨天我和妈妈去公园，看到一只好大的蝴蝶！",
    "它是黄色的，翅膀上有黑色的花纹，可漂亮了。",
    "妈妈说那是凤蝶，我回家还查了百科书。",
    "原来蝴蝶小时候是毛毛虫，好神奇啊！",
    "我还想养蚕宝宝，看它们怎么变成蛾子。",
]

# ── 第二个孩子模拟（女孩"小美"，偏艺术/语言） ──
SIMULATED_DIALOGUES_2 = [
    "星宝你好！今天我读了一个故事，叫《小王子》。",
    "小王子住在一个很小的星球上，上面只有一朵玫瑰花。",
    "我觉得玫瑰花很骄傲，但小王子还是爱她。",
    "我喜欢书里面的狐狸，它说驯养就是建立联系。",
    "我也想写一个故事，关于一只会飞的猫！",

    "音乐课老师教我们唱了一首新歌，叫《虫儿飞》。",
    "黑黑的天空低垂，亮亮的繁星相随～我唱给你听！",
    "我还在学钢琴，已经会弹《小星星》了。",
    "弹钢琴的时候我觉得手指在跳舞，特别开心。",

    "我和好朋友一起做了手工，折了千纸鹤。",
    "我们折了好多颜色，红的蓝的黄的绿的，挂在教室里。",
    "好朋友说过生日的时候想让我教她弹钢琴。",
    "我觉得教别人东西的时候，自己也变得更厉害了。",

    "今天语文课我背了一首古诗，叫《静夜思》。",
    "床前明月光，疑是地上霜。举头望明月，低头思故乡。",
    "老师说李白是想家了，我也觉得写得让人心里暖暖的。",

    "我在家里种了一盆小多肉，每天给它浇水。",
    "它长出了新的小叶子，胖嘟嘟的，超级可爱！",
    "妈妈说养植物要有耐心，不能天天浇太多水。",
    "我觉得看着小植物长大，心里特别高兴。",
]


def main():
    args = sys.argv[1:]

    if "--test" in args:
        run_test()
    elif "--report" in args:
        show_report()
    else:
        interactive_mode()


def interactive_mode():
    """直接和星宝聊天"""
    name = input("请输入孩子的昵称: ").strip() or "小明"
    age = input("请输入孩子的年龄(6-12): ").strip() or "8"
    engine = DialogueEngine(child_name=name, child_age=int(age))
    engine.interactive()


def run_test():
    """用模拟对话跑通完整链路"""
    print("=" * 50)
    print("🧪 模拟对话测试 — 小明（偏科学/逻辑型）")
    print("=" * 50)

    engine1 = DialogueEngine(child_name="小明", child_age=8)
    result1 = engine1.run_simulated_conversation(SIMULATED_DIALOGUES, verbose=True)

    print("\n\n" + "=" * 50)
    print("📊 小明 — 最终状态")
    print("=" * 50)
    print(f"有效互动: {result1['interactions']} 次")
    print(f"星宝等级: Lv.{result1['star_baby_level']}")
    print(f"当前形态: {result1['current_form']}")
    print(f"主导兴趣: {result1['dominant_interest']}")
    print(f"进化分支: {result1['evolution_branch']}")
    print(f"\n雷达数据: {result1['radar']}")

    if result1['evolution_history']:
        print("\n🌟 进化事件:")
        for e in result1['evolution_history']:
            print(f"  Lv.{e['from']} → Lv.{e['to']} 转职为「{e['branch']}」")

    print("\n" + engine1.get_parent_report())

    # 测试第二个孩子
    print("\n\n" + "=" * 50)
    print("🧪 模拟对话测试 — 小美（偏艺术/语言型）")
    print("=" * 50)

    engine2 = DialogueEngine(child_name="小美", child_age=7)
    result2 = engine2.run_simulated_conversation(SIMULATED_DIALOGUES_2, verbose=True)

    print("\n" + engine2.get_parent_report())


def show_report():
    """生成示例天赋报告（用于演示）"""
    print("=" * 50)
    print("📄 示例：家长端天赋报告")
    print("=" * 50)

    engine = DialogueEngine(child_name="小明", child_age=8)
    engine.run_simulated_conversation(SIMULATED_DIALOGUES, verbose=False)

    print("\n" + "=" * 50)
    print("📊 免费版 · 每周简报")
    print("=" * 50)
    print(engine.get_weekly_brief())

    print("\n" + "=" * 50)
    print("🔒 付费版 · 完整天赋报告")
    print("=" * 50)
    print(engine.get_parent_report())


if __name__ == "__main__":
    main()
