import { ref, computed } from 'vue'
import { apiService } from './api/http'
import { AUTH } from './api/endpoints'

export interface PasswordPolicyLabels {
  min_length: string
  required_types: string
  has_digit: string
  has_upper: string
  has_lower: string
  has_special: string
}

export interface CharTypePatterns {
  digit: string
  upper: string
  lower: string
  special: string
}

export interface PasswordPolicy {
  min_length: number
  required_types_count: number
  total_types_count: number
  special_chars_pattern: string
  char_type_patterns: CharTypePatterns
  labels: PasswordPolicyLabels
}

export const passwordPolicy = ref<PasswordPolicy | null>(null)
export const policyLoadError = ref(false)
export const policyLoading = computed(() => !passwordPolicy.value && !policyLoadError.value)

export async function loadPasswordPolicy(): Promise<void> {
  try {
    passwordPolicy.value = await apiService.get<PasswordPolicy>(AUTH.PASSWORD_POLICY)
  } catch {
    console.warn('密碼規則 API 無法連線，密碼輸入功能暫時停用')
    policyLoadError.value = true
  }
}

export function getPasswordPolicy(): PasswordPolicy | null {
  return passwordPolicy.value
}
