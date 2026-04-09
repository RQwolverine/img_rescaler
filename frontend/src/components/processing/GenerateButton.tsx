import { motion } from 'framer-motion'

interface Props {
  loading: boolean
  disabled: boolean
  onClick: () => void
}

export function GenerateButton({ loading, disabled, onClick }: Props) {
  return (
    <motion.button
      onClick={onClick}
      disabled={disabled || loading}
      className={`px-8 py-2.5 rounded-lg font-medium text-sm text-white transition-colors
        ${disabled || loading
          ? 'bg-[#1aad6d]/40 cursor-not-allowed'
          : 'bg-[#1aad6d] hover:bg-[#158f5a] cursor-pointer'}`}
      whileTap={disabled || loading ? {} : { scale: 0.97 }}
    >
      {loading ? (
        <span className="flex items-center gap-2">
          <motion.span
            className="inline-block w-4 h-4 border-2 border-white/30 border-t-white rounded-full"
            animate={{ rotate: 360 }}
            transition={{ duration: 0.8, repeat: Infinity, ease: 'linear' }}
          />
          处理中…
        </span>
      ) : (
        '生成处理图片'
      )}
    </motion.button>
  )
}
