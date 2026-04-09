import { motion, AnimatePresence } from 'framer-motion'
import { useEffect } from 'react'

interface Props {
  open: boolean
  onClose: () => void
}

export function TutorialModal({ open, onClose }: Props) {
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
                className="flex items-center gap-2 px-5 py-2 rounded-xl font-semibold text-sm
                  bg-white text-[#0f7a52] shadow-md hover:bg-gray-50 transition-colors"
                whileTap={{ scale: 0.96 }}
              >
                <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                  <path d="M8.5 2L3.5 7L8.5 12" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
                返回主页面
              </motion.button>
            </div>

            {/* Scrollable image area */}
            <div className="flex-1 overflow-y-auto bg-white/95">
              <img
                src="/tutorial.jpg"
                alt="缩放区域示意图"
                className="w-full block"
                draggable={false}
              />
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  )
}
