import { useState, useRef, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'

const API_BASE = '/api'

async function callApi(endpoint, body) {
  const res = await fetch(`${API_BASE}${endpoint}`, {
    method: body ? 'POST' : 'GET',
    headers: body ? { 'Content-Type': 'application/json' } : {},
    body: body ? JSON.stringify(body) : undefined,
  })
  if (!res.ok) throw new Error(`API error: ${res.status}`)
  return res.json()
}

function StarAvatar({ evolved }) {
  return (
    <div className={`w-10 h-10 rounded-full flex items-center justify-center shadow-sm flex-shrink-0
      ${evolved
        ? 'bg-gradient-to-br from-crayon-purple/30 to-crayon-sky/30 ring-2 ring-crayon-yellow/50'
        : 'bg-gradient-to-br from-crayon-purple/20 to-crayon-sky/20'
      }`}
    >
      <span className="text-lg">{evolved ? '🌟' : '⭐'}</span>
    </div>
  )
}

function EnergyStars({ energy, max }) {
  const filled = Math.round((energy / max) * 5)
  return (
    <div className="flex items-center gap-0.5">
      {[1,2,3,4,5].map(i => (
        <motion.svg
          key={i}
          className={`w-3 h-3 ${i <= filled ? 'text-crayon-yellow' : 'text-ink/8'}`}
          viewBox="0 0 24 24" fill="currentColor"
          animate={i === filled && energy > 0 ? { scale: [1, 1.3, 1] } : {}}
          transition={{ duration: 0.4 }}
        >
          <path d="M12 2 L14.5 9.5 L22 12 L14.5 14.5 L12 22 L9.5 14.5 L2 12 L9.5 9.5 Z"/>
        </motion.svg>
      ))}
    </div>
  )
}

export default function ChatPage() {
  const navigate = useNavigate()
  const [messages, setMessages] = useState([
    { id: 0, role: 'star', text: '嗨！我是星宝～今天有什么好玩的事想告诉我呀？', time: '' },
  ])
  const [input, setInput] = useState('')
  const [energy, setEnergy] = useState(0)
  const [level, setLevel] = useState(1)
  const [isListening, setIsListening] = useState(false)
  const [evolving, setEvolving] = useState(false)
  const [evolved, setEvolved] = useState(false)
  const [loading, setLoading] = useState(false)
  const bottomRef = useRef(null)

  useEffect(() => { bottomRef.current?.scrollIntoView({ behavior: 'smooth' }) }, [messages])

  const sendMessage = async (text) => {
    if (!text.trim() || loading) return
    const childMsg = { id: Date.now(), role: 'child', text, time: '刚刚' }
    setMessages(prev => [...prev, childMsg])
    setInput('')
    setLoading(true)

    try {
      const data = await callApi('/chat', { message: text })
      setMessages(prev => [...prev, { id: Date.now()+1, role: 'star', text: data.reply, time: '刚刚' }])
      setEnergy(data.energy)
      setLevel(data.level)

      if (data.evolved && !evolved) {
        setEvolving(true)
        setTimeout(() => { setEvolving(false); setEvolved(true) }, 2200)
      }
    } catch {
      setMessages(prev => [...prev, { id: Date.now()+1, role: 'star', text: '哎呀，我走神了一下～再说一次好不好？', time: '刚刚' }])
    }
    setLoading(false)
  }

  const startListening = () => {
    const SR = window.SpeechRecognition || window.webkitSpeechRecognition
    if (!SR) { alert('浏览器不支持语音～请打字跟我聊天吧！'); return }
    const r = new SR()
    r.lang = 'zh-CN'
    r.interimResults = false
    r.onstart = () => setIsListening(true)
    r.onend = () => setIsListening(false)
    r.onresult = (e) => sendMessage(e.results[0][0].transcript)
    r.onerror = () => setIsListening(false)
    r.start()
  }

  return (
    <div className="paper-texture h-full flex flex-col max-w-md mx-auto relative">

      {/* ── 进化遮罩 ── */}
      <AnimatePresence>
        {evolving && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="absolute inset-0 z-50 flex flex-col items-center justify-center bg-paper/95 backdrop-blur-sm"
          >
            <motion.div
              className="w-36 h-36 rounded-full flex items-center justify-center"
              style={{ animation: 'evolve-burst 2s ease-out' }}
            >
              <motion.span
                className="text-6xl"
                animate={{ scale: [1, 1.2, 1], rotate: [0, 10, -10, 0] }}
                transition={{ duration: 1, repeat: 2 }}
              >🌟</motion.span>
            </motion.div>
            <motion.p
              className="mt-6 font-sketch text-2xl text-crayon-purple font-bold"
              animate={{ opacity: [0.4, 1, 0.4] }}
              transition={{ duration: 1.3, repeat: Infinity }}
            >
              星宝 正在进化...
            </motion.p>
            <motion.p
              className="mt-2 text-sm text-ink-light/50"
              initial={{ opacity: 0 }} animate={{ opacity: 1 }}
              transition={{ delay: 0.8 }}
            >
              即将揭开新的形态 ✨
            </motion.p>
          </motion.div>
        )}
      </AnimatePresence>

      {/* ── 顶部栏 ── */}
      <header className="bg-paper/90 backdrop-blur-sm px-4 py-3 flex items-center gap-3 z-10 sketch-border-solid mx-3 mt-3">
        <button onClick={() => navigate('/')} className="text-ink-light/60 hover:text-ink text-xl font-sketch">&larr;</button>
        <StarAvatar evolved={evolved} />
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <span className="font-sketch font-bold text-ink text-sm">
              {evolved ? '星宝 · 智识学者' : '星宝'}
            </span>
            <span className="text-[10px] bg-crayon-yellow/30 text-ink-light px-1.5 py-0.5 rounded-full font-bold">
              Lv.{level}
            </span>
          </div>
          <div className="mt-1.5">
            <EnergyStars energy={energy} max={50} />
          </div>
        </div>
        <button
          onClick={() => navigate('/parent')}
          className="text-[11px] text-ink-light/40 underline underline-offset-2 font-sketch whitespace-nowrap hover:text-ink-light/70"
        >
          家长端
        </button>
      </header>

      {/* ── 聊天区 ── */}
      <div className="flex-1 overflow-y-auto px-4 py-4 space-y-4">
        {messages.map((msg, i) => (
          <motion.div
            key={msg.id}
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.35, delay: i === messages.length-1 ? 0 : 0 }}
            className={`flex ${msg.role === 'child' ? 'justify-end' : 'justify-start'}`}
          >
            {msg.role === 'star' && (
              <div className="w-7 h-7 rounded-full bg-crayon-purple/15 flex items-center justify-center mr-2 mt-1.5 flex-shrink-0">
                <span className="text-[10px]">⭐</span>
              </div>
            )}

            <div className={`max-w-[75%] px-4 py-3 text-sm leading-relaxed
              ${msg.role === 'child'
                ? 'bg-crayon-yellow/25 text-ink rounded-2xl rounded-br-md sketch-border'
                : 'bg-white/80 text-ink rounded-2xl rounded-bl-md sketch-border'
              }`}
            >
              {msg.text}
            </div>

            {msg.role === 'child' && (
              <div className="w-7 h-7 rounded-full bg-crayon-coral/15 flex items-center justify-center ml-2 mt-1.5 flex-shrink-0">
                <span className="text-[10px]">👦</span>
              </div>
            )}
          </motion.div>
        ))}

        {/* 加载中的铅笔动画 */}
        {loading && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="flex items-center gap-2 ml-9"
          >
            <div className="flex gap-1">
              {[0,1,2].map(i => (
                <motion.div
                  key={i}
                  className="w-1.5 h-1.5 rounded-full bg-crayon-purple/30"
                  animate={{ y: [0, -6, 0], opacity: [0.3, 1, 0.3] }}
                  transition={{ duration: 0.8, delay: i * 0.15, repeat: Infinity }}
                />
              ))}
            </div>
            <span className="text-[11px] text-ink-light/40 font-sketch">星宝正在用蜡笔写字...</span>
          </motion.div>
        )}

        <div ref={bottomRef} />
      </div>

      {/* ── 进化预警 ── */}
      {energy >= 38 && !evolved && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="px-4 py-1.5 text-center"
        >
          <span className="text-[11px] text-crayon-purple/70 font-sketch" style={{ animation: 'wiggle-hint 2s ease-in-out infinite', display: 'inline-block' }}>
            ⚡ 能量快满了...星宝快要进化啦！
          </span>
        </motion.div>
      )}

      {/* ── 底部输入 ── */}
      <div className="px-3 py-3 bg-paper/90 backdrop-blur-sm flex items-center gap-2 mx-3 mb-3 sketch-border">
        {/* 语音按钮 */}
        <button
          onClick={startListening}
          className={`w-11 h-11 rounded-full flex items-center justify-center flex-shrink-0 transition-all shadow-sm
            ${isListening
              ? 'bg-crayon-coral text-white scale-110'
              : 'bg-white text-crayon-purple hover:bg-crayon-purple/5'
            }`}
        >
          <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
            <path d="M12 14a3 3 0 003-3V5a3 3 0 10-6 0v6a3 3 0 003 3zm5-3a5 5 0 01-10 0H5a7 7 0 0014 0h-2zm-6 8v3h2v-3h-2z"/>
          </svg>
        </button>

        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && sendMessage(input)}
          placeholder="打字跟星宝聊天..."
          className="flex-1 px-4 py-2.5 bg-white/70 rounded-full text-sm font-sketch
                     placeholder:text-ink-light/25 outline-none
                     focus:bg-white focus:ring-2 focus:ring-crayon-purple/15 transition-all"
        />

        <button
          onClick={() => sendMessage(input)}
          disabled={!input.trim() || loading}
          className="w-11 h-11 rounded-full bg-crayon-purple text-white flex items-center justify-center
                     flex-shrink-0 shadow-sm disabled:opacity-25 disabled:scale-100
                     hover:bg-crayon-purple/90 active:scale-90 transition-all"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
              d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"/>
          </svg>
        </button>
      </div>
    </div>
  )
}
