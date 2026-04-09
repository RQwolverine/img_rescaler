import { motion } from 'framer-motion'
import type { ImageFile, ScaleMode } from '../../types/image'
import { ScaleModeSelect } from './ScaleModeSelect'

interface Props {
  file: ImageFile
  index: number
  onUpdate: (id: string, patch: Partial<ImageFile>) => void
  onRemove: (id: string) => void
}

export function ImageCard({ file, index, onUpdate, onRemove }: Props) {
  const isRatio = file.scaleMode === 'by_ratio'

  return (
    <motion.div
      className="bg-white rounded-xl overflow-hidden"
      style={{ boxShadow: '0 2px 12px rgba(0,0,0,0.08), 0 1px 3px rgba(0,0,0,0.05)' }}
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.05, duration: 0.25 }}
      layout
    >
      {/* Thumbnail */}
      <div className="relative aspect-[3/4] bg-gray-50 overflow-hidden">
        <img
          src={file.previewUrl}
          alt={file.file.name}
          className="w-full h-full object-contain"
        />
        <button
          onClick={() => onRemove(file.id)}
          className="absolute top-1.5 right-1.5 w-5 h-5 rounded-full bg-black/40 text-white
            text-xs flex items-center justify-center hover:bg-black/60 transition-colors leading-none"
        >
          ✕
        </button>
      </div>

      {/* Controls */}
      <div className="p-2.5 flex flex-col gap-2">
        <p className="text-xs text-gray-500 truncate">{file.file.name}</p>

        <ScaleModeSelect
          value={file.scaleMode}
          onChange={(v: ScaleMode) => onUpdate(file.id, { scaleMode: v })}
        />

        {isRatio ? (
          <div className="flex items-center gap-1.5">
            <label className="text-xs text-gray-400 shrink-0">倍率</label>
            <input
              type="number"
              min="0.1" max="20" step="0.1"
              value={file.ratio}
              onChange={(e) => onUpdate(file.id, { ratio: e.target.value })}
              placeholder="如 1.5"
              className="flex-1 text-xs border border-gray-200 rounded-lg px-2 py-1.5
                focus:outline-none focus:ring-2 focus:ring-[#1aad6d]/30 focus:border-[#1aad6d]"
            />
          </div>
        ) : (
          <div className="flex items-center gap-1.5">
            <label className="text-xs text-gray-400 shrink-0">
              目标{file.scaleMode === 'by_height' ? '高' : '宽'}
            </label>
            <div className="flex-1 flex items-center gap-1">
              <input
                type="number"
                min="0.1" max="200" step="0.1"
                value={file.targetCm}
                onChange={(e) => onUpdate(file.id, { targetCm: e.target.value })}
                placeholder="cm"
                className="flex-1 text-xs border border-gray-200 rounded-lg px-2 py-1.5
                  focus:outline-none focus:ring-2 focus:ring-[#1aad6d]/30 focus:border-[#1aad6d]"
              />
              <span className="text-xs text-gray-400">cm</span>
            </div>
          </div>
        )}
      </div>
    </motion.div>
  )
}
