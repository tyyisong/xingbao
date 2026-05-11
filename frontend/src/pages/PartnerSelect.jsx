import { useState, useMemo } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'

function makeStars(n) {
  return Array.from({ length: n }, (_, i) => ({
    id: i,
    x: Math.random() * 100,
    y: Math.random() * 100,
    size: 3 + Math.random() * 10,
    delay: Math.random() * 5,
    duration: 2 + Math.random() * 3,
    drift: Math.random() * 30 - 15,
  }))
}

export default function PartnerSelect() {
  const [hatching, setHatching] = useState(false)
  const [hatched, setHatched] = useState(false)
  const navigate = useNavigate()
  const stars = useMemo(() => makeStars(40), [])

  const handleHatch = () => {
    if (hatching) return
    setHatching(true)
    setTimeout(() => setHatched(true), 800)
  }

  return (
    <div className="paper-texture h-full flex flex-col items-center justify-center relative overflow-hidden select-none">

      {/* ── 背景散落蜡笔星星 ── */}
      {stars.map((s) => (
        <svg
          key={s.id}
          className="absolute pointer-events-none"
          style={{
            left: `${s.x}%`, top: `${s.y}%`,
            width: s.size, height: s.size,
            opacity: 0,
            animation: `twinkle-sketch ${s.duration}s ease-in-out ${s.delay}s infinite`,
          }}
          viewBox="0 0 24 24" fill="none"
        >
          <path
            d="M12 2 L14.5 9.5 L22 12 L14.5 14.5 L12 22 L9.5 14.5 L2 12 L9.5 9.5 Z"
            fill="rgba(124,111,247,0.2)"
            stroke="rgba(124,111,247,0.1)"
            strokeWidth="0.5"
          />
        </svg>
      ))}

      {/* ── 画框线 ── */}
      <div className="absolute inset-4 border-2 border-dashed border-ink/8 rounded-2xl pointer-events-none z-0" />

      {/* ── 顶部文字 ── */}
      <motion.div
        initial={{ opacity: 0, y: -30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8, ease: 'easeOut' }}
        className="text-center mb-8 z-10 px-4"
      >
        <p className="text-xs tracking-[0.3em] text-ink-light/50 mb-3 font-sketch">
          ── 知识星球 · 特别呈现 ──
        </p>
        <h1 className="font-sketch text-4xl font-bold text-ink crayon-shadow leading-tight">
          你的AI
          <span className="text-crayon-purple">成长</span>
          伙伴
        </h1>
        <p className="text-ink-light/50 text-sm mt-3 max-w-52 mx-auto leading-relaxed">
          一个陪你聊天、悄悄进化、发现你<span className="text-crayon-coral">隐藏天赋</span>的小星星
        </p>
      </motion.div>

      {/* ── 核心区：蛋 / 星宝 ── */}
      <div className="relative z-10 flex items-center justify-center" style={{ minHeight: 280 }}>
        <AnimatePresence mode="wait">
          {!hatched ? (
            <motion.div
              key="egg-stage"
              initial={{ opacity: 0, scale: 0.7 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.5, filter: 'blur(8px)' }}
              transition={{ duration: 0.5 }}
              className="flex flex-col items-center cursor-pointer"
              onClick={handleHatch}
            >
              {/* ── 星蛋 ── */}
              <motion.div
                animate={hatching
                  ? { scale: [1, 1.12, 1.08, 0.85], rotate: [0, -3, 5, -8] }
                  : { y: [0, -6, 0], rotate: [0, 0.5, 0, -0.5, 0] }
                }
                transition={hatching
                  ? { duration: 0.8, times: [0, 0.3, 0.6, 1] }
                  : { duration: 3.5, repeat: Infinity, ease: 'easeInOut' }
                }
                className="relative w-48 h-56"
              >
                <svg viewBox="0 0 160 190" className="w-full h-full drop-shadow-[0_8px_20px_rgba(124,111,247,0.15)]">
                  <defs>
                    <radialGradient id="eggSurface" cx="38%" cy="32%">
                      <stop offset="0%" stopColor="#FFFDF7"/>
                      <stop offset="45%" stopColor="#FFF3CD"/>
                      <stop offset="100%" stopColor="#F0D98D"/>
                    </radialGradient>
                    <filter id="eggNoise">
                      <feTurbulence type="fractalNoise" baseFrequency="0.05" numOctaves="4" result="n"/>
                      <feDisplacementMap in="SourceGraphic" in2="n" scale="2.5"/>
                    </filter>
                  </defs>
                  {/* 蛋体 */}
                  <ellipse cx="80" cy="100" rx="60" ry="70" fill="url(#eggSurface)" filter="url(#eggNoise)"/>
                  {/* 蛋的高光 */}
                  <ellipse cx="62" cy="68" rx="18" ry="26" fill="rgba(255,255,255,0.5)" transform="rotate(-15,62,68)"/>
                  {/* 蜡笔星星装饰 */}
                  <g transform="translate(80,42)">
                    <path d="M0 -18 L4 -6 L18 -6 L8 3 L12 15 L0 8 L-12 15 L-8 3 L-18 -6 L-4 -6 Z"
                      fill="rgba(124,111,247,0.35)" transform="scale(0.8)"/>
                  </g>
                  <g transform="translate(45,120)">
                    <path d="M0 -10 L2 -4 L10 -4 L4 2 L6 9 L0 5 L-6 9 L-4 2 L-10 -4 L-2 -4 Z"
                      fill="rgba(255,107,107,0.3)" transform="scale(0.6)"/>
                  </g>
                  <g transform="translate(115,105)">
                    <path d="M0 -8 L2 -3 L8 -3 L3 1 L5 8 L0 4 L-5 8 L-3 1 L-8 -3 L-2 -3 Z"
                      fill="rgba(72,181,224,0.3)" transform="scale(0.7)"/>
                  </g>
                </svg>

                {/* 戳我标签 */}
                <motion.div
                  className="absolute -bottom-2 left-1/2 -translate-x-1/2 whitespace-nowrap"
                  animate={{ y: [0, -6, 0], scale: [1, 1.05, 1] }}
                  transition={{ duration: 1.8, repeat: Infinity }}
                >
                  <span className="font-sketch text-lg text-crayon-purple font-bold crayon-shadow bg-paper/80 px-3 py-1 rounded-full sketch-border-solid">
                    👆 戳我孵化星宝
                  </span>
                </motion.div>
              </motion.div>
            </motion.div>
          ) : (
            /* ── 孵化后的星宝 ── */
            <motion.div
              key="star-reveal"
              className="flex flex-col items-center"
              style={{ animation: 'star-emerge 0.7s cubic-bezier(0.34,1.56,0.64,1) both' }}
            >
              <motion.div
                className="float-sketch"
                animate={{ y: [0, -10, 0] }}
                transition={{ duration: 4, repeat: Infinity, ease: 'easeInOut' }}
              >
                <svg viewBox="0 0 140 160" className="w-40 h-48 drop-shadow-[0_8px_24px_rgba(124,111,247,0.2)]">
                  {/* 光晕 */}
                  <defs>
                    <radialGradient id="starGlow" cx="50%" cy="40%">
                      <stop offset="0%" stopColor="rgba(255,229,102,0.3)"/>
                      <stop offset="100%" stopColor="rgba(255,229,102,0)"/>
                    </radialGradient>
                    <radialGradient id="bodyFill" cx="50%" cy="40%">
                      <stop offset="0%" stopColor="#F0EAFF"/>
                      <stop offset="100%" stopColor="#C5B4E3"/>
                    </radialGradient>
                  </defs>
                  {/* 光环 */}
                  <circle cx="70" cy="70" r="60" fill="url(#starGlow)"/>
                  {/* 身体 */}
                  <ellipse cx="70" cy="95" rx="42" ry="46" fill="url(#bodyFill)"/>
                  {/* 眼睛（大而有神） */}
                  <circle cx="50" cy="78" r="9" fill="#1B1A3B"/>
                  <circle cx="90" cy="78" r="9" fill="#1B1A3B"/>
                  {/* 眼内高光 */}
                  <circle cx="53" cy="75" r="3.5" fill="white"/>
                  <circle cx="93" cy="75" r="3.5" fill="white"/>
                  {/* 小嘴 */}
                  <path d="M60 96 Q70 108 80 96" fill="none" stroke="#1B1A3B" strokeWidth="2.2" strokeLinecap="round"/>
                  {/* 腮红（蜡笔质感） */}
                  <ellipse cx="35" cy="92" rx="9" ry="6" fill="rgba(255,107,107,0.25)"/>
                  <ellipse cx="105" cy="92" rx="9" ry="6" fill="rgba(255,107,107,0.25)"/>
                  {/* 星星触角 */}
                  <path d="M30 48 Q22 30 15 34" fill="none" stroke="#7C6FF7" strokeWidth="2.5" strokeLinecap="round"/>
                  <circle cx="14" cy="33" r="5" fill="#FFE566" opacity="0.7"/>
                  <path d="M110 48 Q118 30 125 34" fill="none" stroke="#7C6FF7" strokeWidth="2.5" strokeLinecap="round"/>
                  <circle cx="126" cy="33" r="5" fill="#FFE566" opacity="0.7"/>
                </svg>
              </motion.div>

              {/* 信息卡 */}
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.4 }}
                className="text-center mt-2"
              >
                <h2 className="font-sketch text-3xl font-bold text-ink">星宝</h2>
                <div className="flex items-center gap-2 justify-center mt-1">
                  <span className="text-xs bg-crayon-yellow/40 text-ink-light px-2 py-0.5 rounded-full font-bold">
                    Lv.1
                  </span>
                  <span className="text-xs text-ink-light/50">·</span>
                  <span className="text-xs text-ink-light/50 font-sketch">初始形态</span>
                </div>
                <div className="flex items-center justify-center gap-1 mt-2">
                  {[1,2,3,4,5].map(i => (
                    <svg key={i} className="w-3 h-3 text-crayon-yellow/30" viewBox="0 0 24 24" fill="currentColor">
                      <path d="M12 2 L14.5 9.5 L22 12 L14.5 14.5 L12 22 L9.5 14.5 L2 12 L9.5 9.5 Z"/>
                    </svg>
                  ))}
                  <span className="text-[10px] text-ink-light/40 ml-1">0/50</span>
                </div>
              </motion.div>

              {/* CTA按钮 */}
              <motion.button
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.7, type: 'spring', stiffness: 200 }}
                whileHover={{ scale: 1.04 }}
                whileTap={{ scale: 0.94 }}
                onClick={() => navigate('/chat')}
                className="mt-6 px-12 py-3.5 bg-space-deep text-paper rounded-full font-sketch text-lg font-bold
                           shadow-[0_6px_0_rgba(0,0,0,0.15)] active:shadow-[0_2px_0_rgba(0,0,0,0.15)]
                           active:translate-y-1 transition-all duration-150
                           hover:bg-space-mid"
              >
                出发探险 ✦
              </motion.button>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* ── 底部手绘云朵 ── */}
      <svg className="absolute bottom-0 left-0 w-full opacity-[0.06] pointer-events-none z-0" viewBox="0 0 400 60" preserveAspectRatio="none">
        <ellipse cx="30" cy="50" rx="120" ry="35" fill="#7C6FF7"/>
        <ellipse cx="200" cy="45" rx="140" ry="40" fill="#48B5E0"/>
        <ellipse cx="380" cy="55" rx="100" ry="30" fill="#7C6FF7"/>
      </svg>
    </div>
  )
}
