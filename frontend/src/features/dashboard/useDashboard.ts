import api from '../../lib/api'
import type { ApiResponse } from '../../types/api'
import type { DashboardData } from '../../types/dashboard'

export async function fetchDashboardData(): Promise<DashboardData> {
  const res = await api.get<ApiResponse<DashboardData>>('/dashboard')
  if (!res.data?.data?.stats) {
    throw new Error('Invalid dashboard data')
  }
  return res.data.data
}
