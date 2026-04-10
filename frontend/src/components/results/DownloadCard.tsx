import { motion } from 'framer-motion'
import type { ProcessingResultItem } from '../../types/image'

interface Props {
  result: ProcessingResultItem
  index: number
}

export function DownloadCard({ result, index }: Props) {
  function handleDownload() {
    if (!result.output_b64) return
    const link = document.createElement('a')
    link.href = `data:image/jpeg;base64,${result.output_b64}`
    link.download = `rescaled_${result.filename}`
    link.click()
  }

  return (
    <motion.div
      className="bg-white rounded-xl overflow-hidden"
      style={{ boxShadow: '0 2px 12px rgba(0,0,0,0.08), 0 1px 3px rgba(0,0,0,0.05)' }}
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ delay: index * 0.07, duration: 0.25, type: 'spring', stiffness: 220 }}
    >
      {/* Thumbnail */}
      <div className="aspect-[3/4] bg-gray-50 overflow-hidden">
        {result.status === 'ok' && result.output_b64 ? (
          <img
            src={`data:image/jpeg;base64,${result.output_b64}`}
            alt={result.filename}
            className="w-full h-full object-contain"
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center text-red-400 text-xs px-3 text-center">
            处理失败：{result.error_message}
          </div>
        )}
      </div>

      {/* Info + action */}
      <div className="p-2.5 flex flex-col gap-1.5">
        <p className="text-xs text-gray-600 truncate font-medium">{result.filename}</p>

        {result.status === 'ok' && result.detected_top_art_cm && (
          <div className="text-xs text-gray-400 space-y-0.5">
            <p>识别：{result.detected_top_art_cm.width.toFixed(1)} × {result.detected_top_art_cm.height.toFixed(1)} cm</p>
            <p>倍率：{result.scale_factor?.toFixed(3)}</p>
          </div>
        )}

        {result.warnings?.length > 0 && (
          <p className="text-xs text-amber-500 truncate">⚠ {result.warnings[0]}</p>
        )}

        {result.status === 'ok' && (
          <motion.button
            onClick={handleDownload}
            className="w-full py-2 rounded-lg bg-[#1aad6d] text-white text-xs font-medium
              hover:bg-[#158f5a] transition-colors mt-0.5"
            whileTap={{ scale: 0.97 }}
          >
            下载图片
          </motion.button>
        )}
      </div>
    </motion.div>
  )
}
