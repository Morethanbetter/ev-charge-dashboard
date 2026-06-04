import api from '../../lib/api'
import type { ApiResponse } from '../../types/api'
import type { UploadFile } from '../../types/upload'

export async function uploadFile(file: File, onProgress?: (pct: number) => void): Promise<UploadFile> {
  const formData = new FormData()
  formData.append('file', file)

  const res = await api.post<ApiResponse<UploadFile>>('/files/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    onUploadProgress: (e) => {
      if (e.total && onProgress) {
        onProgress(Math.round((e.loaded / e.total) * 100))
      }
    },
  })

  return res.data.data
}
