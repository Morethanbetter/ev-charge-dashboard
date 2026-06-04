import api from '../../lib/api'
import type { ApiResponse } from '../../types/api'

export interface DedupDetail {
  id: number
  file_id: number
  original_count: number
  dedup_count: number
  removed_count: number
  dedup_rate: number
  status: string
  details: DedupRow[]
}

export interface DedupRow {
  row_index: number
  original_data: Record<string, unknown>
  duplicate_of: number
  reason: string
}

export async function fetchDedupDetail(fileId: number): Promise<DedupDetail> {
  const res = await api.get<ApiResponse<DedupDetail>>(`/files/${fileId}/dedup`)
  return res.data.data
}

export async function downloadDedupResult(fileId: number): Promise<void> {
  const res = await api.get(`/files/${fileId}/dedup/download`, { responseType: 'blob' })
  const url = window.URL.createObjectURL(new Blob([res.data]))
  const a = document.createElement('a')
  a.href = url
  a.download = `dedup_result_${fileId}.csv`
  document.body.appendChild(a)
  a.click()
  a.remove()
  window.URL.revokeObjectURL(url)
}
