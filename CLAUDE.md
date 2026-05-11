# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

星宝（Star Baby）MVP — 一款基于大语言模型的儿童AI养成陪伴应用。通过"孩子教，AI学"的反向互动模式，结合游戏化进化树，为6-12岁儿童提供情感陪伴，同时为家长生成天赋分析报告。

## 启动服务

```bash
# 终端1: Python API 服务（端口 8080）
DEEPSEEK_API_KEY="sk-xxx" python3 server.py

# 终端2: Vite 前端开发服务（端口 5173，自动代理 /api → 8080）
cd frontend && npm run dev
```

前端已配置 Vite proxy：`/api/*` 请求自动转发到 `http://localhost:8080`。

## 架构总览

```
┌─────────────┐     HTTP/JSON      ┌──────────────┐     OpenAI SDK     ┌──────────┐
│  React H5   │ ────────────────── │  Flask API   │ ───────────────── │ DeepSeek │
│  (Vite)     │   /api/chat        │  server.py   │  对话+兴趣标注      │   API    │
│  :5173      │   /api/report      │  :8080       │                   │          │
│             │   /api/history     │              │                   └──────────┘
└─────────────┘                    └──────┬───────┘
                                          │ 调用
                               ┌──────────▼──────────┐
                               │  engine/dialogue.py │  ← 核心对话引擎
                               │  engine/tagging.py  │  ← 兴趣标注+关键词提取
                               │  engine/safety.py   │  ← 内容安全过滤
                               │  engine/persona.py  │  ← 星宝人设Prompt
                               │  models/user.py     │  ← 孩子+对话历史
                               │  models/star_baby.py│  ← 星宝进化+能量
                               │  models/report.py   │  ← 天赋报告生成
                               └─────────────────────┘
```

## 对话引擎数据流

`engine/dialogue.py` 的 `DialogueEngine.chat()` 处理每一轮对话：

1. **安全检查** → `safety.check_input_safety()` 过滤隐私/暴力内容
2. **兴趣标注** → `tagging.InterestTagger.tag()` 返回 `(dict, list)` — 6维兴趣分数 + 匹配关键词
3. **生成回复** → 调用 DeepSeek API，使用 `persona.PERSONA_SYSTEM_PROMPT` 人设
4. **输出安全** → `safety.check_output_safety()` 兜底
5. **能量结算** → `StarBaby.gain_energy()` 每次+3，满50触发10级转职
6. **进化检查** → `InterestAccumulator.determine_branch()` 判定 scholar/artist/engineer

## 关键设计决策

- **Python 3.9 兼容**：所有类型标注使用 `from __future__ import annotations`，避免 `dict[str, float] | None` 语法错误
- **API降级**：`InterestTagger` 优先调 DeepSeek API 标注兴趣，失败时自动降级为关键词规则匹配
- **能量阈值**：MVP演示用50（config.py `ENERGY_MAX_LEVEL_10`），生产环境应改回100
- **单用户模式**：server.py 全局单例 `DialogueEngine`，后续需改为 session 管理
- **TailwindCSS v4**：使用 `@tailwindcss/vite` 插件 + CSS `@theme` 配置，无 tailwind.config.js

## 内容安全过滤器

`safety.py` 基于正则匹配，已知误判修复记录：
- "住在" 过于宽泛 → 改为 `我家住|我们家住|地址是`（避免匹配"小王子住在一个星球上"）
- "手机" 过于宽泛 → 改为 `留个?电话|电话号|手机号|加微信`（避免匹配"玩手机游戏"）

## 前端页面路由

| 路由 | 组件 | 功能 |
|------|------|------|
| `/` | PartnerSelect | 手绘水彩星空 + 孵化动画 → 选星宝 |
| `/chat` | ChatPage | 气泡聊天 + 语音输入 + 能量条 + 进化特效 |
| `/parent` | ParentReport | Tab: 雷达图报告 / 聊天记录(带兴趣标注) |

前端通过 Vite proxy 调用 `/api/*`，无需在代码中硬编码后端地址。

## 子目录说明

- `engine/` — Python核心引擎（人设、对话、标注、安全）
- `models/` — Python数据模型（孩子、星宝、报告）
- `frontend/` — React H5前端（Vite + TailwindCSS v4 + framer-motion + recharts）
- `data/` — 测试数据
- `output/reports/` — 生成的报告文件
