export type ScaleMode = 'by_height' | 'by_width' | 'by_ratio'

export interface ImageFile {
  id: string
  file: File
  previewUrl: string
  scaleMode: ScaleMode
  targetCm: string   // string to allow empty input
  ratio: string
}

export interface TopArtDimensions {
  width: number
  height: number
}

export interface ProcessingResultItem {
  filename: string
  status: 'ok' | 'error'
  detected_top_art_cm?: TopArtDimensions
  scale_factor?: number
  output_b64?: string
  warnings: string[]
  error_message?: string
}

export interface ProcessingResponse {
  results: ProcessingResultItem[]
}

export type AppPhase = 'upload' | 'configure' | 'processing' | 'results'

export type AppState =
  | { phase: 'upload' }
  | { phase: 'configure'; files: ImageFile[] }
  | { phase: 'processing'; files: ImageFile[] }
  | { phase: 'results'; files: ImageFile[]; results: ProcessingResultItem[] }
