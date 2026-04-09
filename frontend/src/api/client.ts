import axios from 'axios'
import type { ImageFile, ProcessingResponse } from '../types/image'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL ?? '',
})

export async function processImages(files: ImageFile[]): Promise<ProcessingResponse> {
  const formData = new FormData()

  for (const f of files) {
    formData.append('files', f.file)
  }

  const configs = files.map((f) => ({
    filename: f.file.name,
    scale_mode: f.scaleMode,
    target_cm: f.scaleMode !== 'by_ratio' ? parseFloat(f.targetCm) : null,
    ratio: f.scaleMode === 'by_ratio' ? parseFloat(f.ratio) : null,
  }))

  formData.append('configs', JSON.stringify(configs))

  const response = await api.post<ProcessingResponse>('/api/process', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })

  return response.data
}
