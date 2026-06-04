import api from '../../lib/api'
import type { ApiResponse, PaginatedResponse } from '../../types/api'
import type { UploadFile } from '../../types/upload'

export async function fetchHistory(params: { page: number; page_size: number; keyword?: string; sort_by?: string; sort_order?: string }): Promise<PaginatedResponse<UploadFile>> {
  const res = await api.get<ApiResponse<PaginatedResponse<UploadFile>>>('/files/history', { params })
  return res.data.data
}

export async function deleteFile(fileId: string): Promise<void> {
  await api.delete(`/files/${fileId}`)
}
