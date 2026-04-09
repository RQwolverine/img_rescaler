import { useReducer, useCallback, useState } from 'react'
import { AnimatePresence, motion } from 'framer-motion'
import type { AppState, ImageFile, ProcessingResultItem } from './types/image'
import { processImages } from './api/client'
import { DropZone } from './components/upload/DropZone'
import { ImageCard } from './components/controls/ImageCard'
import { GenerateButton } from './components/processing/GenerateButton'
import { DownloadCard } from './components/results/DownloadCard'
import { TutorialModal } from './components/TutorialModal'

// ── Reducer ────────────────────────────────────────────────────────────────

type Action =
  | { type: 'ADD_FILES'; files: ImageFile[] }
  | { type: 'UPDATE_FILE'; id: string; patch: Partial<ImageFile> }
  | { type: 'REMOVE_FILE'; id: string }
  | { type: 'START_PROCESSING' }
  | { type: 'SET_RESULTS'; results: ProcessingResultItem[] }
  | { type: 'RESET' }

function reducer(state: AppState, action: Action): AppState {
  switch (action.type) {
    case 'ADD_FILES': {
      const existing = state.phase !== 'upload' ? (state as any).files as ImageFile[] : []
      const combined = [...existing, ...action.files].slice(0, 15)
      return combined.length > 0 ? { phase: 'configure', files: combined } : { phase: 'upload' }
    }
    case 'UPDATE_FILE': {
      if (state.phase !== 'configure') return state
      return { ...state, files: state.files.map((f) => f.id === action.id ? { ...f, ...action.patch } : f) }
    }
    case 'REMOVE_FILE': {
      if (state.phase !== 'configure') return state
      const files = state.files.filter((f) => f.id !== action.id)
      return files.length === 0 ? { phase: 'upload' } : { ...state, files }
    }
    case 'START_PROCESSING': {
      if (state.phase !== 'configure') return state
      return { phase: 'processing', files: state.files }
    }
    case 'SET_RESULTS': {
      if (state.phase !== 'processing') return state
      return { phase: 'results', files: state.files, results: action.results }
    }
    case 'RESET':
      return { phase: 'upload' }
    default:
      return state
  }
}

// ── Helpers ────────────────────────────────────────────────────────────────

let _idCounter = 0
function makeId() { return `file_${++_idCounter}` }

function fileToImageFile(file: File): ImageFile {
  return {
    id: makeId(),
    file,
    previewUrl: URL.createObjectURL(file),
    scaleMode: 'by_height',
    targetCm: '',
    ratio: '1.0',
  }
}

function validateFiles(files: ImageFile[]): string | null {
  for (const f of files) {
    if (f.scaleMode === 'by_ratio') {
      const r = parseFloat(f.ratio)
      if (isNaN(r) || r <= 0) return `"${f.file.name}"：请输入有效倍率`
    } else {
      const cm = parseFloat(f.targetCm)
      if (isNaN(cm) || cm <= 0) return `"${f.file.name}"：请输入目标尺寸 (cm)`
    }
  }
  return null
}

// ── App ────────────────────────────────────────────────────────────────────

export default function App() {
  const [state, dispatch] = useReducer(reducer, { phase: 'upload' })
  const [tutorialOpen, setTutorialOpen] = useState(false)

  const handleFiles = useCallback((raw: File[]) => {
    dispatch({ type: 'ADD_FILES', files: raw.map(fileToImageFile) })
  }, [])

  async function handleGenerate() {
    if (state.phase !== 'configure') return
    const err = validateFiles(state.files)
    if (err) { alert(err); return }
    dispatch({ type: 'START_PROCESSING' })
    try {
      const response = await processImages(state.files)
      dispatch({ type: 'SET_RESULTS', results: response.results })
    } catch (e: any) {
      alert('处理失败：' + (e?.response?.data?.detail ?? e?.message ?? '未知错误'))
      dispatch({ type: 'ADD_FILES', files: [] })
    }
  }

  const files = state.phase !== 'upload' ? (state as any).files as ImageFile[] : []
  const isProcessing = state.phase === 'processing'
  const hasResults = state.phase === 'results'

  return (
    <div className="min-h-screen" style={{ background: 'linear-gradient(160deg, #e8eef6 0%, #dde6f0 100%)' }}>

      {/* ── Hero Header ── */}
      <div style={{ background: 'linear-gradient(135deg, #0f7a52 0%, #1aad6d 60%, #22c97d 100%)' }}
        className="relative overflow-hidden">
        {/* Decorative blobs */}
        <div className="absolute -top-10 -right-10 w-48 h-48 rounded-full opacity-20"
          style={{ background: 'radial-gradient(circle, #fff 0%, transparent 70%)' }} />
        <div className="absolute bottom-0 left-1/3 w-32 h-32 rounded-full opacity-10"
          style={{ background: 'radial-gradient(circle, #fff 0%, transparent 70%)' }} />

        <div className="relative max-w-4xl mx-auto px-5 py-8 text-center">
          <h1 className="text-2xl font-bold text-white tracking-tight drop-shadow-sm">
            设计稿尺寸调整工具
          </h1>
          <p className="text-sm mt-1.5" style={{ color: 'rgba(255,255,255,0.75)' }}>
            上传设计稿，填写目标尺寸，自动生成可下载结果
          </p>

          {/* Tutorial button */}
          <div className="mt-4 flex items-center justify-center gap-3">
            <motion.button
              onClick={() => setTutorialOpen(true)}
              className="flex items-center gap-2 px-5 py-2 rounded-xl text-sm font-semibold
                bg-white/20 text-white border border-white/30 hover:bg-white/30 transition-colors backdrop-blur-sm"
              whileTap={{ scale: 0.97 }}
            >
              <svg width="15" height="15" viewBox="0 0 15 15" fill="none">
                <circle cx="7.5" cy="7.5" r="6.5" stroke="currentColor" strokeWidth="1.5"/>
                <path d="M7.5 5v1M7.5 7.5v3" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round"/>
              </svg>
              查看缩放逻辑说明
            </motion.button>

            {state.phase !== 'upload' && (
              <button
                onClick={() => dispatch({ type: 'RESET' })}
                className="text-xs underline underline-offset-2 transition-opacity hover:opacity-70"
                style={{ color: 'rgba(255,255,255,0.8)' }}
              >
                重新开始
              </button>
            )}
          </div>
        </div>
      </div>

      {/* ── Two-panel layout ── */}
      <main className="max-w-4xl mx-auto px-5 py-7 pb-14 flex gap-5 items-start">

        {/* ── Left panel ── */}
        <div className="flex-1 rounded-2xl overflow-hidden"
          style={{ boxShadow: '0 4px 24px rgba(0,0,0,0.10), 0 1px 4px rgba(0,0,0,0.06)' }}>
          {/* Accent bar */}
          <div className="h-1" style={{ background: 'linear-gradient(90deg, #1aad6d, #22c97d)' }} />

          <div className="bg-white">
            <div className="px-5 pt-4 pb-3 flex items-center justify-between">
              <div className="flex items-center gap-2">
                {/* Icon */}
                <div className="w-7 h-7 rounded-lg flex items-center justify-center"
                  style={{ background: 'linear-gradient(135deg, #e6f9f0, #c8f0de)' }}>
                  <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                    <path d="M2 2h10M2 5h6M2 8h8M2 11h4" stroke="#1aad6d" strokeWidth="1.5" strokeLinecap="round"/>
                  </svg>
                </div>
                <h2 className="text-sm font-semibold text-gray-700">上传设计稿</h2>
              </div>
              {files.length > 0 && (
                <span className="text-xs px-2 py-0.5 rounded-full font-medium"
                  style={{ background: '#e6f9f0', color: '#0f7a52' }}>
                  {files.length} / 15
                </span>
              )}
            </div>

            <div className="px-5 pb-5">
              <AnimatePresence mode="wait">
                {state.phase === 'upload' ? (
                  <motion.div key="dropzone" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
                    <DropZone onFiles={handleFiles} />
                  </motion.div>
                ) : (
                  <motion.div key="configure" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
                    className="flex flex-col gap-4">
                    <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
                      {files.map((f, i) => (
                        <ImageCard key={f.id} file={f} index={i}
                          onUpdate={(id, patch) => dispatch({ type: 'UPDATE_FILE', id, patch })}
                          onRemove={(id) => dispatch({ type: 'REMOVE_FILE', id })} />
                      ))}
                    </div>

                    <div className="flex items-center justify-between pt-1">
                      {files.length < 15 ? (
                        <label className="cursor-pointer text-xs transition-colors"
                          style={{ color: '#1aad6d' }}
                          onMouseEnter={e => (e.currentTarget.style.color = '#0f7a52')}
                          onMouseLeave={e => (e.currentTarget.style.color = '#1aad6d')}>
                          + 添加更多图片
                          <input type="file" accept="image/*" multiple className="hidden"
                            onChange={(e) => { if (e.target.files) handleFiles(Array.from(e.target.files)) }} />
                        </label>
                      ) : (
                        <span className="text-xs text-gray-400">已达上限</span>
                      )}
                      <GenerateButton
                        loading={isProcessing}
                        disabled={files.length === 0 || hasResults}
                        onClick={handleGenerate}
                      />
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          </div>
        </div>

        {/* ── Right panel ── */}
        <div className="flex-1 rounded-2xl overflow-hidden"
          style={{ boxShadow: '0 4px 24px rgba(0,0,0,0.10), 0 1px 4px rgba(0,0,0,0.06)' }}>
          {/* Accent bar */}
          <div className="h-1" style={{ background: 'linear-gradient(90deg, #3b82f6, #6366f1)' }} />

          <div className="bg-white">
            <div className="px-5 pt-4 pb-3 flex items-center gap-2">
              <div className="w-7 h-7 rounded-lg flex items-center justify-center"
                style={{ background: 'linear-gradient(135deg, #eff6ff, #dbeafe)' }}>
                <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                  <rect x="1.5" y="2.5" width="11" height="9" rx="1.5" stroke="#3b82f6" strokeWidth="1.4" fill="none"/>
                  <circle cx="5" cy="5.5" r="1.2" stroke="#3b82f6" strokeWidth="1.2" fill="none"/>
                  <path d="M1.5 9.5 L4.5 7 L7 9.5 L9.5 6.5 L12.5 9.5" stroke="#3b82f6" strokeWidth="1.3" strokeLinejoin="round" fill="none"/>
                </svg>
              </div>
              <h2 className="text-sm font-semibold text-gray-700">处理结果</h2>
            </div>

            <div className="px-5 pb-5 min-h-72 flex flex-col">
              <AnimatePresence mode="wait">

                {/* Placeholder */}
                {!isProcessing && !hasResults && (
                  <motion.div key="placeholder"
                    className="flex-1 flex flex-col items-center justify-center gap-3 py-14 text-center"
                    initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
                    {/* Illustrated placeholder */}
                    <div className="w-20 h-20 rounded-2xl flex items-center justify-center"
                      style={{ background: 'linear-gradient(135deg, #f1f5f9, #e2e8f0)' }}>
                      <svg width="36" height="36" viewBox="0 0 36 36" fill="none">
                        <rect x="3" y="6" width="30" height="24" rx="3" stroke="#94a3b8" strokeWidth="1.8" fill="none"/>
                        <circle cx="12" cy="14" r="2.5" stroke="#94a3b8" strokeWidth="1.8" fill="none"/>
                        <path d="M3 24.5 L10.5 18 L16.5 23.5 L23 16.5 L33 24.5" stroke="#94a3b8" strokeWidth="1.8" strokeLinejoin="round" fill="none"/>
                      </svg>
                    </div>
                    <div>
                      <p className="text-sm font-medium text-gray-400">等待生成结果</p>
                      <p className="text-xs text-gray-300 mt-1 leading-relaxed">
                        请先上传设计稿并填写目标尺寸<br />
                        系统将为您生成缩放后的设计稿预览
                      </p>
                    </div>
                  </motion.div>
                )}

                {/* Processing */}
                {isProcessing && (
                  <motion.div key="spinner"
                    className="flex-1 flex flex-col items-center justify-center gap-4 py-14"
                    initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
                    <div className="relative w-14 h-14">
                      <motion.div
                        className="absolute inset-0 rounded-full"
                        style={{ border: '3px solid #e6f9f0', borderTop: '3px solid #1aad6d' }}
                        animate={{ rotate: 360 }}
                        transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
                      />
                      <div className="absolute inset-0 flex items-center justify-center">
                        <div className="w-4 h-4 rounded-full" style={{ background: '#e6f9f0' }} />
                      </div>
                    </div>
                    <p className="text-sm text-gray-500">正在处理 {files.length} 张图片…</p>
                  </motion.div>
                )}

                {/* Results */}
                {hasResults && state.phase === 'results' && (
                  <motion.div key="results"
                    className="flex flex-col gap-4"
                    initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
                    <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
                      {state.results.map((r, i) => (
                        <DownloadCard key={r.filename + i} result={r} index={i} />
                      ))}
                    </div>
                    <div className="flex items-center justify-center gap-1.5 pt-1">
                      <div className="w-1.5 h-1.5 rounded-full" style={{ background: '#1aad6d' }} />
                      <p className="text-xs text-gray-400">
                        共 {state.results.filter(r => r.status === 'ok').length} 张处理成功
                      </p>
                    </div>
                  </motion.div>
                )}

              </AnimatePresence>
            </div>
          </div>
        </div>

      </main>

      {/* Footer */}
      <footer className="text-center pb-8">
        <p className="text-xs text-gray-400">线稿图缩放工具 · 自动识别标尺，等比例缩放</p>
      </footer>

      {/* Tutorial Modal */}
      <TutorialModal open={tutorialOpen} onClose={() => setTutorialOpen(false)} />

    </div>
  )
}
