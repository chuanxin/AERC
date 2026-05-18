import { apiService } from './api/http'
import { AUTH } from './api/endpoints'

interface PublicKeyResponse {
  kid: string
  public_key: string
  algorithm: string
}

let cachedKey: { kid: string; publicKey: string } | null = null

export async function getServerPublicKey(): Promise<{ kid: string; publicKey: string }> {
  if (cachedKey) return cachedKey
  const response = await apiService.get<PublicKeyResponse>(AUTH.PUBLIC_KEY)
  cachedKey = { kid: response.kid, publicKey: response.public_key }
  return cachedKey
}

export function clearKeyCache(): void {
  cachedKey = null
}
