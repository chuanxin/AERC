export interface User {
  id: number
  email: string
  username: string
  role: 'buyer' | 'seller' | 'admin'
  is_verified: boolean
  avatar_url: string | null
  created_at: string
}

export interface LoginCredentials {
  username: string
  password: string
}

export interface RegisterData {
  email: string
  username: string
  password: string
}
