import { motion, AnimatePresence } from 'framer-motion'
import { useEffect, useState } from 'react'

interface Props {
  open: boolean
  onClose: () => void
}

function Ruler2Diagram() {
  // Dimensions of the A4-shaped diagram canvas (portrait, px)
  const W = 560
  const H = 720
  const rulerTop = 38     // height of top ruler strip
  const rulerLeft = 52    // width of left ruler strip
  const labelBottom = 130 // height of product-code area at bottom-right
  const labelRight = 200  // width of product-code area at bottom-right

  // Colour palette matching tutorial.jpg
  const green = '#c8e6c9'
  const greenDark = '#4caf50'
  const gray = '#b0bec5'
  const orange = '#ffcc80'
  const orangeDark = '#f57c00'
  const textDark = '#37474f'
  const textMid = '#546e7a'

  // Ruler tick helpers
  const ticksTop: number[] = []
  for (let i = 1; i * 28 < W - rulerLeft - 4; i++) ticksTop.push(rulerLeft + i * 28)

  const ticksLeft: number[] = []
  for (let i = 1; i * 28 < H - rulerTop - 4; i++) ticksLeft.push(rulerTop + i * 28)

  return (
    <div className="flex flex-col items-center gap-4 px-5 py-6 bg-white min-h-full">
      {/* Title */}
      <div className="text-center">
        <p className="text-sm font-bold text-gray-700">设计尺2 — 缩放区域示意图</p>
        <p className="text-xs text-gray-500 mt-1">数字在外侧，刻度朝向内容区域，黑色边线为分界</p>
      </div>

      {/* Legend */}
      <div className="flex flex-wrap gap-3 justify-center text-xs">
        {[
          { color: green, border: greenDark, label: '标尺区域（保留不变）' },
          { color: gray,  border: '#78909c',  label: '内容区域（按比例缩放）' },
          { color: orange, border: orangeDark, label: '编号区域（原样保留）' },
        ].map(({ color, border, label }) => (
          <div key={label} className="flex items-center gap-1.5">
            <div className="w-3 h-3 rounded-sm border" style={{ background: color, borderColor: border }} />
            <span style={{ color: textMid }}>{label}</span>
          </div>
        ))}
      </div>

      {/* SVG diagram */}
      <svg
        viewBox={`0 0 ${W} ${H}`}
        width="100%"
        style={{ maxWidth: 420, border: '1px solid #cfd8dc', borderRadius: 4 }}
      >
        {/* White background */}
        <rect x={0} y={0} width={W} height={H} fill="white" />

        {/* ── Top ruler strip (green) ── */}
        <rect x={0} y={0} width={W} height={rulerTop} fill={green} />

        {/* Numbers ABOVE the ruler strip (on the outside) — shown as thin label band */}
        {/* We indicate the concept via a label inside the top strip */}
        {/* Major-tick marks pointing DOWN into the content */}
        {ticksTop.map((x) => (
          <line key={x} x1={x} y1={rulerTop - 10} x2={x} y2={rulerTop} stroke={greenDark} strokeWidth={1} />
        ))}
        {/* Minor half-tick marks */}
        {ticksTop.map((x, i) =>
          i < ticksTop.length - 1 ? (
            <line key={x + 0.5} x1={x + 14} y1={rulerTop - 5} x2={x + 14} y2={rulerTop} stroke={greenDark} strokeWidth={0.7} />
          ) : null
        )}

        {/* ── Left ruler strip (green) ── */}
        <rect x={0} y={0} width={rulerLeft} height={H} fill={green} />

        {/* Major-tick marks pointing RIGHT into the content */}
        {ticksLeft.map((y) => (
          <line key={y} x1={rulerLeft - 10} y1={y} x2={rulerLeft} y2={y} stroke={greenDark} strokeWidth={1} />
        ))}
        {ticksLeft.map((y, i) =>
          i < ticksLeft.length - 1 ? (
            <line key={y + 0.5} x1={rulerLeft - 5} y1={y + 14} x2={rulerLeft} y2={y + 14} stroke={greenDark} strokeWidth={0.7} />
          ) : null
        )}

        {/* ── Black border lines (ruler-content boundary) ── */}
        <line x1={rulerLeft} y1={0} x2={rulerLeft} y2={H} stroke="#212121" strokeWidth={1.5} />
        <line x1={0} y1={rulerTop} x2={W} y2={rulerTop} stroke="#212121" strokeWidth={1.5} />

        {/* ── Content area (gray) ── */}
        <rect x={rulerLeft} y={rulerTop} width={W - rulerLeft} height={H - rulerTop} fill={gray} />

        {/* ── Product-code area (orange, bottom-right) ── */}
        <rect
          x={W - labelRight} y={H - labelBottom}
          width={labelRight} height={labelBottom}
          fill={orange}
        />
        <text x={W - labelRight / 2} y={H - labelBottom + 40} textAnchor="middle" fontSize={11} fontWeight="bold" fill={orangeDark}>产品编号区域</text>
        <text x={W - labelRight / 2} y={H - labelBottom + 58} textAnchor="middle" fontSize={9} fill={orangeDark}>原样保留，不参与缩放</text>
        <text x={W - labelRight / 2} y={H - labelBottom + 74} textAnchor="middle" fontSize={9} fill={orangeDark}>150 × 450 像素</text>

        {/* ── Ruler-area labels ── */}
        {/* Top ruler label */}
        <text x={W / 2 + rulerLeft / 2} y={rulerTop / 2 + 5} textAnchor="middle" fontSize={10} fill={greenDark} fontWeight="bold">
          顶部标尺区域（保留不变）
        </text>
        {/* "numbers outside" annotation */}
        <text x={W / 2 + rulerLeft / 2} y={8} textAnchor="middle" fontSize={8} fill={greenDark}>
          ← 数字在外侧 →
        </text>

        {/* Left ruler label (rotated) */}
        <text
          x={rulerLeft / 2}
          y={H / 2}
          textAnchor="middle"
          fontSize={10}
          fill={greenDark}
          fontWeight="bold"
          transform={`rotate(-90, ${rulerLeft / 2}, ${H / 2})`}
        >
          左侧标尺区域（保留不变）
        </text>

        {/* Content area label */}
        <text x={rulerLeft + (W - rulerLeft) / 2} y={rulerTop + (H - rulerTop) / 2 - 50} textAnchor="middle" fontSize={18} fontWeight="bold" fill={textDark}>
          内容缩放区域
        </text>

        {/* Dimension note */}
        <text x={rulerLeft + (W - rulerLeft) / 2} y={rulerTop + (H - rulerTop) / 2 - 20} textAnchor="middle" fontSize={10} fill={textMid}>
          38px (顶部标尺)
        </text>
        <text x={8} y={H - 4} fontSize={8} fill={textMid}>52px</text>
      </svg>

      {/* Step-by-step explanation */}
      <div className="w-full max-w-md space-y-3">
        {[
          {
            n: '1',
            title: '自动识别标尺刻度（设计尺2）',
            body: '数字印在标尺条外侧（上方/左侧），刻度朝内。系统通过刻度间距计算 px/cm 比例，并以黑色边线为基准定位内容区域起点。',
          },
          {
            n: '2',
            title: '选择缩放模式，计算缩放倍率 scale',
            body: '',
            buttons: ['按目标高度\nscale = 目标高 ÷ H', '按目标宽度\nscale = 目标宽 ÷ W', '按缩放倍率\nscale = 用户输入值'],
          },
          {
            n: '3',
            title: '对缩放区域内所有线稿进行等比例缩放输出',
            body: '标尺区域与右下角产品编号保持原样不变',
          },
        ].map(({ n, title, body, buttons }) => (
          <div key={n} className="text-sm">
            <div className="flex items-start gap-2">
              <span className="shrink-0 w-5 h-5 rounded bg-[#1aad6d] text-white text-xs font-bold flex items-center justify-center mt-0.5">{n}</span>
              <p className="font-semibold text-gray-700">{title}</p>
            </div>
            {body && <p className="text-xs text-gray-500 mt-1 ml-7 leading-relaxed">{body}</p>}
            {buttons && (
              <div className="flex flex-wrap gap-2 mt-2 ml-7">
                {buttons.map((b) => (
                  <div key={b} className="flex-1 min-w-[80px] border border-gray-300 rounded-lg px-2 py-2 text-center text-xs text-gray-600 leading-snug whitespace-pre-line">
                    {b}
                  </div>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}

export function TutorialModal({ open, onClose }: Props) {
  const [tab, setTab] = useState<'ruler1' | 'ruler2'>('ruler1')

  // Close on Escape
  useEffect(() => {
    if (!open) return
    const handler = (e: KeyboardEvent) => { if (e.key === 'Escape') onClose() }
    window.addEventListener('keydown', handler)
    return () => window.removeEventListener('keydown', handler)
  }, [open, onClose])

  return (
    <AnimatePresence>
      {open && (
        <motion.div
          className="fixed inset-0 z-50 flex flex-col"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.2 }}
        >
          {/* Backdrop */}
          <div
            className="absolute inset-0 bg-black/70 backdrop-blur-sm"
            onClick={onClose}
          />

          {/* Panel */}
          <motion.div
            className="relative z-10 flex flex-col h-full max-w-3xl w-full mx-auto"
            initial={{ y: 40, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            exit={{ y: 40, opacity: 0 }}
            transition={{ duration: 0.25, type: 'spring', stiffness: 260, damping: 28 }}
          >
            {/* Top bar */}
            <div className="flex items-center justify-between px-5 py-4 shrink-0"
              style={{ background: 'linear-gradient(135deg, #0f7a52, #1aad6d)' }}>
              <div>
                <p className="text-white font-semibold text-base">缩放逻辑说明</p>
                <p className="text-white/70 text-xs mt-0.5">了解系统如何识别尺寸并缩放线稿</p>
              </div>
              <motion.button
                onClick={onClose}
                className="flex items-center gap-2 px-3 sm:px-5 py-2 rounded-xl font-semibold text-sm
                  bg-white text-[#0f7a52] shadow-md hover:bg-gray-50 transition-colors shrink-0"
                whileTap={{ scale: 0.96 }}
              >
                <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                  <path d="M8.5 2L3.5 7L8.5 12" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
                <span className="hidden sm:inline">返回主页面</span>
              </motion.button>
            </div>

            {/* Tab selector */}
            <div className="flex shrink-0 bg-white border-b border-gray-200">
              {(['ruler1', 'ruler2'] as const).map((t) => (
                <button
                  key={t}
                  onClick={() => setTab(t)}
                  className={`flex-1 py-2.5 text-xs sm:text-sm font-semibold transition-colors border-b-2
                    ${tab === t
                      ? t === 'ruler1'
                        ? 'border-[#1aad6d] text-[#0f7a52]'
                        : 'border-[#6366f1] text-[#4f46e5]'
                      : 'border-transparent text-gray-400 hover:text-gray-600'}`}
                >
                  <span className="sm:hidden">{t === 'ruler1' ? '设计尺1' : '设计尺2'}</span>
                  <span className="hidden sm:inline">{t === 'ruler1' ? '设计尺1（数字朝内）' : '设计尺2（数字朝外）'}</span>
                </button>
              ))}
            </div>

            {/* Scrollable content */}
            <div className="flex-1 overflow-y-auto bg-white/95">
              <AnimatePresence mode="wait">
                {tab === 'ruler1' ? (
                  <motion.div key="ruler1" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
                    <img
                      src="/tutorial.jpg"
                      alt="设计尺1缩放区域示意图"
                      className="w-full block"
                      draggable={false}
                    />
                  </motion.div>
                ) : (
                  <motion.div key="ruler2" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
                    <Ruler2Diagram />
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  )
}
