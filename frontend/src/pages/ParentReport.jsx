import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import {
  RadarChart, PolarGrid, PolarAngleAxis, Radar,
  ResponsiveContainer,
} from 'recharts'

const API_BASE = '/api'

const MOCK_RADAR = [
  { dimension: '科学探索', score: 92 },
  { dimension: '艺术审美', score: 68 },
  { dimension: '数理逻辑', score: 85 },
  { dimension: '语言表达', score: 73 },
  { dimension: '人际社交', score: 88 },
  { dimension: '自然观察', score: 55 },
]

const TAG_COLORS = {
  '科学探索': '#48B5E0', '艺术审美': '#FDA7DF', '数理逻辑': '#FF9F43',
  '语言表达': '#7C6FF7', '人际社交': '#4ECDC4', '自然观察': '#66BB6A',
}

const MOCK_HISTORY = [
  {
    date: '5月11日 · 周一',
    items: [
      { role: 'child', text: '星宝星宝，我今天学了太阳系！', tag: '科学探索' },
      { role: 'star', text: '哇！太阳系！真的吗！我好想听你讲讲！' },
      { role: 'child', text: '太阳有八个行星围着它转，地球是第三个！', tag: '科学探索' },
      { role: 'star', text: '哦！原来地球是第三个呀！那火星排第几呢？' },
      { role: 'child', text: '木星最大了，它上面有个大红斑，是风暴！', tag: '科学探索' },
      { role: 'star', text: '天呐！风暴还能一直留在那里吗？' },
    ],
  },
  {
    date: '5月10日 · 周日',
    items: [
      { role: 'child', text: '今天数学课老师教我们乘法口诀了', tag: '数理逻辑' },
      { role: 'star', text: '真的吗！乘法口诀好难啊，你能教教我吗？' },
      { role: 'child', text: '一一得一，一二得二，我背得可快了！', tag: '数理逻辑' },
    ],
  },
  {
    date: '5月9日 · 周六',
    items: [
      { role: 'child', text: '我和同桌一起搭了一个大城堡，用乐高！', tag: '人际社交' },
      { role: 'star', text: '哇！乐高城堡！你们合作得真好！' },
    ],
  },
]

export default function ParentReport() {
  const navigate = useNavigate()
  const [activeTab, setActiveTab] = useState('report')

  return (
    <div className="grid-paper min-h-full max-w-md mx-auto flex flex-col">
      {/* ── 顶部 ── */}
      <header className="bg-paper/95 backdrop-blur-sm px-5 py-4 flex items-center gap-3 shadow-[0_1px_0_rgba(0,0,0,0.05)]">
        <button onClick={() => navigate('/chat')} className="text-ink-light/50 hover:text-ink text-xl font-sketch">&larr;</button>
        <div className="flex-1">
          <h2 className="font-sketch font-bold text-ink text-lg">宏伟 · 成长观察手记</h2>
          <p className="text-ink-light/35 text-[11px] flex items-center gap-1.5 mt-0.5 font-sketch">
            <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M5 9V7a5 5 0 0110 0v2a2 2 0 012 2v5a2 2 0 01-2 2H5a2 2 0 01-2-2v-5a2 2 0 012-2zm8-2v2H7V7a3 3 0 016 0z" clipRule="evenodd"/>
            </svg>
            私密笔记 · 仅家长可见
          </p>
        </div>
      </header>

      {/* ── Tab ── */}
      <div className="flex bg-paper/70 border-b border-ink/5 px-4 font-sketch">
        {[
          { key: 'report', label: '📐 天赋雷达' },
          { key: 'history', label: '📝 对话手记' },
        ].map(tab => (
          <button
            key={tab.key}
            onClick={() => setActiveTab(tab.key)}
            className={`flex-1 py-3.5 text-sm font-bold transition-all relative
              ${activeTab === tab.key
                ? 'text-crayon-purple'
                : 'text-ink-light/30 hover:text-ink-light/50'
              }`}
          >
            {tab.label}
            {activeTab === tab.key && (
              <motion.div
                layoutId="tab-underline"
                className="absolute bottom-0 left-4 right-4 h-0.5 bg-crayon-purple rounded-full"
              />
            )}
          </button>
        ))}
      </div>

      {/* ── 内容 ── */}
      <div className="flex-1 overflow-y-auto px-4 py-5">
        {activeTab === 'report' ? <ReportTab /> : <HistoryTab history={MOCK_HISTORY} />}
      </div>
    </div>
  )
}

/* ═══════ 报告Tab ═══════ */
function ReportTab() {
  return (
    <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="space-y-5">
      {/* 雷达图卡片 */}
      <div className="bg-white/80 rounded-2xl p-5 sketch-border-solid shadow-sm">
        <h3 className="font-sketch font-bold text-ink text-sm mb-1">多元智能雷达</h3>
        <p className="text-[10px] text-ink-light/35 mb-3">基于加德纳多元智能理论的对话分析</p>
        <ResponsiveContainer width="100%" height={250}>
          <RadarChart data={MOCK_RADAR}>
            <PolarGrid stroke="rgba(44,36,22,0.08)" strokeDasharray="4 4" />
            <PolarAngleAxis
              dataKey="dimension"
              tick={{ fontSize: 11, fontFamily: 'STKaiti, KaiTi, serif', fill: '#6B5E4A' }}
            />
            <Radar
              name="宏伟"
              dataKey="score"
              stroke="#7C6FF7"
              strokeWidth={2}
              fill="#7C6FF7"
              fillOpacity={0.12}
            />
          </RadarChart>
        </ResponsiveContainer>
      </div>

      {/* 核心发现 */}
      <div className="bg-white/80 rounded-2xl p-5 sketch-border-solid shadow-sm">
        <h3 className="font-sketch font-bold text-ink text-sm mb-4">✦ 核心发现</h3>
        <div className="flex items-center gap-4 mb-4">
          <div className="w-14 h-14 rounded-full bg-gradient-to-br from-crayon-purple/15 to-crayon-sky/15 flex items-center justify-center">
            <span className="text-3xl">🔬</span>
          </div>
          <div>
            <p className="font-sketch font-bold text-crayon-purple text-lg">智识学者</p>
            <p className="text-xs text-ink-light/50 mt-0.5">进化倾向 · 科学探索 + 语言表达主导</p>
          </div>
        </div>
        <p className="text-sm text-ink-light leading-relaxed">
          宏伟在科学探索和人际社交方面展现出了强烈的热情。他喜欢通过教星宝来巩固自己学到的知识，
          这正是一种自然的"费曼学习法"实践。他在数理逻辑上的表现也值得关注。
        </p>
      </div>

      {/* 教育建议 */}
      <div className="bg-white/80 rounded-2xl p-5 sketch-border-solid shadow-sm">
        <h3 className="font-sketch font-bold text-ink text-sm mb-4">✧ 给家长的建议</h3>
        <ul className="space-y-3">
          {[
            { icon: '🔭', text: '多带孩子去科技馆、天文馆，投喂科学类绘本和纪录片' },
            { icon: '🤖', text: '可尝试乐高机器人编程，兼顾逻辑与团队协作能力' },
            { icon: '📖', text: '留意保护他的表达欲——让他多"教"你他学到的东西' },
          ].map((item, i) => (
            <motion.li
              key={i}
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.1 * i }}
              className="flex gap-3 text-sm text-ink-light items-start"
            >
              <span className="text-base flex-shrink-0 mt-0.5">{item.icon}</span>
              <span>{item.text}</span>
            </motion.li>
          ))}
        </ul>
      </div>

      <p className="text-[10px] text-ink-light/25 text-center pb-4 font-sketch">
        ※ 基于AI互动数据分析，仅供家长参考，不替代专业教育评估
      </p>
    </motion.div>
  )
}

/* ═══════ 聊天记录Tab ═══════ */
function HistoryTab({ history }) {
  return (
    <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="space-y-5">
      <p className="text-[11px] text-ink-light/35 text-center font-sketch">
        —— 这些对话是星宝了解孩子的方式，仅您可见 ——
      </p>

      {history.map((day, di) => (
        <motion.div
          key={di}
          initial={{ opacity: 0, y: 15 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: di * 0.08 }}
          className="bg-white/80 rounded-2xl p-4 sketch-border-solid shadow-sm"
        >
          {/* 日期标签 */}
          <div className="flex items-center gap-2 mb-3">
            <span className="w-1.5 h-1.5 rounded-full bg-crayon-coral/60"/>
            <h4 className="font-sketch text-sm font-bold text-ink">{day.date}</h4>
          </div>

          <div className="space-y-2.5">
            {day.items.map((item, j) => (
              <div key={j} className={`flex ${item.role === 'child' ? 'justify-end' : 'justify-start'}`}>
                <div className="max-w-[82%]">
                  {/* 气泡 */}
                  <div className={`px-3.5 py-2.5 text-sm rounded-2xl
                    ${item.role === 'child'
                      ? 'bg-crayon-yellow/15 rounded-br-md text-ink'
                      : 'bg-crayon-purple/5 rounded-bl-md text-ink'
                    }`}
                  >
                    <span className="text-[10px] text-ink-light/30 mr-1">
                      {item.role === 'child' ? '👦' : '⭐'}
                    </span>
                    {item.text}
                  </div>
                  {/* 兴趣标签 */}
                  {item.tag && (
                    <span
                      className="inline-block mt-1 text-[10px] px-2 py-0.5 rounded-full font-bold text-white"
                      style={{ backgroundColor: TAG_COLORS[item.tag] || '#999' }}
                    >
                      {item.tag}
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
        </motion.div>
      ))}
    </motion.div>
  )
}
