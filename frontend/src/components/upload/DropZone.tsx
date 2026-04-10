import { useRef, useState } from 'react'
import { motion } from 'framer-motion'

interface DropZoneProps {
  onFiles: (files: File[]) => void
}

const ACCEPTED = ['image/jpeg', 'image/png', 'image/webp', 'image/bmp', 'image/tiff']

export function DropZone({ onFiles }: DropZoneProps) {
  const [dragging, setDragging] = useState(false)
  const inputRef = useRef<HTMLInputElement>(null)

  function handleFiles(raw: FileList | null) {
    if (!raw) return
    const valid = Array.from(raw).filter((f) => ACCEPTED.includes(f.type))
    if (valid.length) onFiles(valid)
  }

  return (
    <motion.div
      className={`w-full rounded-xl border-2 border-dashed cursor-pointer transition-all
        flex flex-col items-center justify-center gap-3 py-8 md:py-14 px-5 md:px-8
        ${dragging
          ? 'border-[#1aad6d] bg-[#f0fdf7]'
          : 'border-gray-300 bg-gray-50 hover:border-[#1aad6d] hover:bg-[#f0fdf7]'}`}
      animate={{ scale: dragging ? 1.01 : 1 }}
      transition={{ type: 'spring', stiffness: 300, damping: 20 }}
      onDragOver={(e) => { e.preventDefault(); setDragging(true) }}
      onDragLeave={() => setDragging(false)}
      onDrop={(e) => {
        e.preventDefault()
        setDragging(false)
        handleFiles(e.dataTransfer.files)
      }}
      onClick={() => inputRef.current?.click()}
    >
      {/* Image icon */}
      <svg
        width="52" height="52" viewBox="0 0 52 52" fill="none"
        className={`transition-colors ${dragging ? 'text-[#1aad6d]' : 'text-gray-400'}`}
      >
        <rect x="4" y="10" width="44" height="32" rx="4" stroke="currentColor" strokeWidth="2.5" fill="none"/>
        <circle cx="17" cy="21" r="4" stroke="currentColor" strokeWidth="2.5" fill="none"/>
        <path d="M4 34 L15 24 L24 33 L33 23 L48 34" stroke="currentColor" strokeWidth="2.5" strokeLinejoin="round" fill="none"/>
      </svg>

      <div className="text-center">
        <p className="text-sm font-medium text-gray-700">点击或拖拽上传图片</p>
        <p className="text-xs text-gray-400 mt-1">支持 JPG、JPEG、PNG、WEBP，最多不超过15张图片</p>
      </div>

      <input
        ref={inputRef}
        type="file"
        accept={ACCEPTED.join(',')}
        multiple
        className="hidden"
        onChange={(e) => handleFiles(e.target.files)}
      />
    </motion.div>
  )
}
