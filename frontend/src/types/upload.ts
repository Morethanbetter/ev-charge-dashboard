export interface UploadFile {
  id: string
  filename: string
  file_size: number
  file_type: string
  upload_time: string
  dedup_status: '已去重' | '待处理' | '处理中'
  dedup_rate?: number
  original_rows?: number
  dedup_rows?: number
}

export interface UploadProgress {
  loaded: number
  total: number
  percentage: number
}
