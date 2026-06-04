import { create } from 'zustand'
import type { UserInfo } from '../../types/auth'
import { getToken, setToken, removeToken, setUser, getUser } from '../../lib/auth'

interface AuthState {
  token: string | null
  user: UserInfo | null
  login: (token: string, user: UserInfo) => void
  logout: () => void
}

export const useAuth = create<AuthState>((set) => ({
  token: getToken(),
  user: getUser<UserInfo>() as UserInfo | null,
  login: (token, user) => {
    setToken(token)
    setUser(user)
    set({ token, user })
  },
  logout: () => {
    removeToken()
    set({ token: null, user: null })
  },
}))
