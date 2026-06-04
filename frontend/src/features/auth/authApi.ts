import api from '../../lib/api'
import type { LoginRequest, LoginResponse } from '../../types/auth'
import type { ApiResponse } from '../../types/api'

export async function login(data: LoginRequest): Promise<LoginResponse> {
  const res = await api.post<ApiResponse<LoginResponse>>('/auth/login', data)
  return res.data.data
}
