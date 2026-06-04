export interface LoginRequest {
  username: string
  password: string
}

export interface LoginResponse {
  access_token: string
  token_type: string
  user: UserInfo
}

export interface UserInfo {
  id: number
  username: string
  email: string
  is_active: boolean
}
