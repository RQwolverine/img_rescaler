import type { ScaleMode } from '../../types/image'

interface Props {
  value: ScaleMode
  onChange: (v: ScaleMode) => void
}

const OPTIONS: { value: ScaleMode; label: string }[] = [
  { value: 'by_height', label: '按高度' },
  { value: 'by_width',  label: '按宽度' },
  { value: 'by_ratio',  label: '按倍率' },
]

export function ScaleModeSelect({ value, onChange }: Props) {
  return (
    <div className="flex gap-1 rounded-lg bg-gray-100 p-0.5">
      {OPTIONS.map((opt) => (
        <button
          key={opt.value}
          onClick={() => onChange(opt.value)}
          className={`flex-1 text-xs font-medium py-2 rounded-md transition-all
            ${value === opt.value
              ? 'bg-[#1aad6d] text-white shadow-sm'
              : 'text-gray-500 hover:text-gray-700'}`}
        >
          {opt.label}
        </button>
      ))}
    </div>
  )
}
