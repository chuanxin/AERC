function b64urlEncode(buf: ArrayBuffer | Uint8Array): string {
  const bytes = buf instanceof Uint8Array ? buf : new Uint8Array(buf)
  let binary = ''
  for (let i = 0; i < bytes.byteLength; i++) {
    binary += String.fromCharCode(bytes[i])
  }
  return btoa(binary).replace(/\+/g, '-').replace(/\//g, '_').replace(/=/g, '')
}

function b64urlDecode(s: string): Uint8Array {
  const padded = s.replace(/-/g, '+').replace(/_/g, '/').padEnd(s.length + ((4 - (s.length % 4)) % 4), '=')
  const binary = atob(padded)
  const bytes = new Uint8Array(binary.length)
  for (let i = 0; i < binary.length; i++) {
    bytes[i] = binary.charCodeAt(i)
  }
  return bytes
}

export async function encryptPassword(
  password: string,
  publicKeyBase64: string,
): Promise<{ encrypted_password: string; encrypted_key: string; iv: string }> {
  const publicKey = await crypto.subtle.importKey(
    'spki',
    b64urlDecode(publicKeyBase64),
    { name: 'RSA-OAEP', hash: 'SHA-256' },
    false,
    ['encrypt'],
  )

  const aesKey = await crypto.subtle.generateKey({ name: 'AES-GCM', length: 256 }, true, ['encrypt'])

  const iv = crypto.getRandomValues(new Uint8Array(12))

  const encryptedPassword = await crypto.subtle.encrypt(
    { name: 'AES-GCM', iv },
    aesKey,
    new TextEncoder().encode(password),
  )

  const rawAesKey = await crypto.subtle.exportKey('raw', aesKey)

  const encryptedKey = await crypto.subtle.encrypt({ name: 'RSA-OAEP' }, publicKey, rawAesKey)

  return {
    encrypted_password: b64urlEncode(encryptedPassword),
    encrypted_key: b64urlEncode(encryptedKey),
    iv: b64urlEncode(iv),
  }
}

export function generateNonce(length = 32): string {
  const bytes = crypto.getRandomValues(new Uint8Array(length))
  return b64urlEncode(bytes).slice(0, length)
}
