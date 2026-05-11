"""
星宝 MVP — 全局配置
"""
import os

# ── DeepSeek API ──
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "your-api-key-here")
DEEPSEEK_BASE_URL = "https://api.deepseek.com"
DEEPSEEK_MODEL = "deepseek-chat"

# ── 星宝进化系统 ──
ENERGY_PER_MESSAGE = 3          # 每次有效互动获得的能量
ENERGY_MAX_LEVEL_10 = 50        # 达到10级转职需要的总能量（MVP演示用，生产环境应为100）
LEVEL_CAP = 10                  # MVP阶段只做到10级

# ── 兴趣维度 (加德纳多元智能映射) ──
INTEREST_DIMENSIONS = {
    "science":    {"label": "科学探索", "icon": "🔬", "branch": "engineer"},
    "art":        {"label": "艺术审美", "icon": "🎨", "branch": "artist"},
    "logic":      {"label": "数理逻辑", "icon": "🧮", "branch": "scholar"},
    "language":   {"label": "语言表达", "icon": "📖", "branch": "scholar"},
    "social":     {"label": "人际社交", "icon": "🤝", "branch": "artist"},
    "nature":     {"label": "自然观察", "icon": "🌿", "branch": "engineer"},
}

# ── 10级转职分支 ──
EVOLUTION_BRANCHES = {
    "scholar":  {"name": "智识学者", "description": "对语言、数字和逻辑充满热情", "visual": "戴眼镜，手持书本"},
    "artist":   {"name": "艺术大师", "description": "对色彩、音乐和人际关系敏感", "visual": "色彩斑斓，长出翅膀"},
    "engineer": {"name": "创造工程师", "description": "对科学、搭建和自然充满好奇", "visual": "机械化外观，手持工具"},
}

# ── 内容安全 ──
FORBIDDEN_TOPICS = ["暴力", "色情", "自杀", "家庭隐私", "个人身份信息", "联系方式"]
MAX_SAFE_RESPONSE_LENGTH = 300  # 单次回复最多字数
