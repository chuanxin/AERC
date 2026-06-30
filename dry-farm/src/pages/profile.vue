<template>
  <v-container
    fluid
    class="px-6 pb-0 pt-0"
    style="background-color: white"
  >
    <v-row justify="center">
      <v-col
        cols="12"
        md="6"
        lg="5"
        class="pt-0"
      >
        <!-- 帳號資訊 -->
        <v-card
          class="mb-3"
          rounded="lg"
          elevation="0"
          variant="outlined"
        >
          <div
            class="d-flex align-center gap-3 pa-3"
            style="background-color: #f5f5f5;"
          >
            <v-icon
              icon="mdi-account-circle"
              color="#3ea0a3"
              size="small"
            />
            <span class="text-subtitle-2 font-weight-medium">帳號資訊</span>
          </div>

          <v-card-text class="pa-3">
            <v-row dense>
              <v-col cols="6">
                <div class="text-body-2 font-weight-medium mb-1">
                  帳號
                </div>
                <div class="text-body-2">
                  {{ userStore.currentUser?.username || '—' }}
                </div>
              </v-col>
              <v-col cols="6">
                <div class="text-body-2 font-weight-medium mb-1">
                  姓名
                </div>
                <div class="text-body-2">
                  {{ userStore.currentUser?.full_name || '—' }}
                </div>
              </v-col>
              <v-col
                cols="6"
                class="mt-3"
              >
                <div class="text-body-2 font-weight-medium mb-1">
                  角色
                </div>
                <v-chip
                  :color="roleColor"
                  size="small"
                  label
                >
                  {{ roleLabel }}
                </v-chip>
              </v-col>
              <v-col
                cols="6"
                class="mt-3"
              >
                <div class="text-body-2 font-weight-medium mb-1">
                  所屬管理處
                </div>
                <div class="text-body-2">
                  {{ userStore.currentUser?.office?.name || '—' }}
                </div>
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>

        <!-- 更換密碼 -->
        <v-card
          class="mb-3"
          rounded="lg"
          elevation="0"
          variant="outlined"
        >
          <div
            class="d-flex align-center gap-3 pa-3"
            style="background-color: #f5f5f5;"
          >
            <v-icon
              icon="mdi-lock-reset"
              color="#3ea0a3"
              size="small"
            />
            <span class="text-subtitle-2 font-weight-medium">更換密碼</span>
          </div>

          <v-card-text class="pa-3">
            <v-form @submit.prevent="handleChangePassword">
              <div class="text-body-2 font-weight-medium mb-2">
                新密碼
              </div>
              <v-text-field
                v-model="newPassword"
                :type="showNewPassword ? 'text' : 'password'"
                variant="outlined"
                density="compact"
                class="mb-3"
                bg-color="white"
                :error="!!newPasswordError"
                :error-messages="newPasswordError"
                hide-details="auto"
                autocomplete="new-password"
              >
                <template #append-inner>
                  <v-icon
                    :icon="showNewPassword ? 'mdi-eye-off' : 'mdi-eye'"
                    size="small"
                    @click="showNewPassword = !showNewPassword"
                  />
                </template>
              </v-text-field>

              <div class="text-body-2 font-weight-medium mb-2">
                確認新密碼
              </div>
              <v-text-field
                v-model="confirmPassword"
                :type="showConfirmPassword ? 'text' : 'password'"
                variant="outlined"
                density="compact"
                class="mb-3"
                bg-color="white"
                :error="!!confirmPasswordError"
                :error-messages="confirmPasswordError"
                hide-details="auto"
                autocomplete="new-password"
              >
                <template #append-inner>
                  <v-icon
                    :icon="showConfirmPassword ? 'mdi-eye-off' : 'mdi-eye'"
                    size="small"
                    @click="showConfirmPassword = !showConfirmPassword"
                  />
                </template>
              </v-text-field>

              <!-- 密碼強度即時檢核 -->
              <v-card
                rounded="lg"
                elevation="0"
                variant="tonal"
                :color="isPasswordValid ? 'success' : 'blue-grey-lighten-4'"
                class="mb-3"
              >
                <v-card-text class="text-caption pa-3">
                  <div class="text-body-2 font-weight-medium mb-2">
                    密碼要求
                  </div>
                  <template v-if="policyLoading">
                    <div class="d-flex align-center text-grey py-1">
                      <v-progress-circular
                        size="14"
                        width="2"
                        indeterminate
                        class="mr-2"
                      />
                      密碼規則載入中...
                    </div>
                  </template>
                  <template v-else-if="policyLoadError">
                    <div class="d-flex align-center text-error py-1">
                      <v-icon
                        size="small"
                        icon="mdi-alert-circle"
                        class="mr-1"
                      />
                      無法取得密碼規則，請重新整理頁面
                    </div>
                  </template>
                  <template v-else-if="passwordRequirements">
                    <div class="d-flex align-center mb-1">
                      <v-icon
                        :icon="passwordRequirements.length ? 'mdi-check-circle' : 'mdi-circle-outline'"
                        :color="passwordRequirements.length ? 'success' : 'grey'"
                        size="x-small"
                        class="mr-1"
                      />
                      <span>{{ passwordRequirements.labels.min_length }}</span>
                    </div>
                    <div class="d-flex align-center mb-1">
                      <v-icon
                        :icon="passwordRequirements.characterTypesValid ? 'mdi-check-circle' : 'mdi-circle-outline'"
                        :color="passwordRequirements.characterTypesValid ? 'success' : 'grey'"
                        size="x-small"
                        class="mr-1"
                      />
                      <span>{{ passwordRequirements.labels.required_types }} (目前 {{ passwordRequirements.characterTypesMet }}/{{ passwordRequirements.totalTypesCount }})</span>
                    </div>
                    <div class="ml-4">
                      <div class="d-flex align-center">
                        <v-icon
                          :icon="passwordRequirements.number ? 'mdi-check' : 'mdi-minus'"
                          :color="passwordRequirements.number ? 'success' : 'grey'"
                          size="x-small"
                          class="mr-1"
                        />
                        <span>{{ passwordRequirements.labels.has_digit }}</span>
                        <span class="mx-1">•</span>
                        <v-icon
                          :icon="passwordRequirements.uppercase ? 'mdi-check' : 'mdi-minus'"
                          :color="passwordRequirements.uppercase ? 'success' : 'grey'"
                          size="x-small"
                          class="mr-1"
                        />
                        <span>{{ passwordRequirements.labels.has_upper }}</span>
                      </div>
                      <div class="d-flex align-center">
                        <v-icon
                          :icon="passwordRequirements.lowercase ? 'mdi-check' : 'mdi-minus'"
                          :color="passwordRequirements.lowercase ? 'success' : 'grey'"
                          size="x-small"
                          class="mr-1"
                        />
                        <span>{{ passwordRequirements.labels.has_lower }}</span>
                        <span class="mx-1">•</span>
                        <v-icon
                          :icon="passwordRequirements.special ? 'mdi-check' : 'mdi-minus'"
                          :color="passwordRequirements.special ? 'success' : 'grey'"
                          size="x-small"
                          class="mr-1"
                        />
                        <span>{{ passwordRequirements.labels.has_special }}</span>
                      </div>
                    </div>
                  </template>
                </v-card-text>
              </v-card>

              <v-alert
                v-if="errorMessage"
                type="error"
                variant="tonal"
                density="compact"
                border="start"
                icon="mdi-alert-circle"
                class="mb-3"
              >
                {{ errorMessage }}
              </v-alert>

              <v-alert
                v-if="successMessage"
                type="success"
                variant="tonal"
                density="compact"
                border="start"
                class="mb-3"
              >
                {{ successMessage }}
              </v-alert>

              <v-btn
                type="submit"
                color="#3ea0a3"
                variant="flat"
                size="large"
                rounded="lg"
                :loading="isSubmitting"
                :disabled="!isPasswordValid || isSubmitting"
                block
              >
                更換密碼
              </v-btn>
            </v-form>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script lang="ts" setup>
import { useUserStore } from '@/stores/users'
import { DEFAULT_ROLES } from '@/types/permissions'
import {
  getPasswordPolicy,
  policyLoading,
  policyLoadError,
} from '@/services/passwordPolicyService'

const userStore = useUserStore()

const roleLabel = computed(() => {
  const role = userStore.currentUser?.role
  return DEFAULT_ROLES.find(r => r.value === role)?.title ?? role ?? '—'
})

const roleColor = computed(() => {
  switch (userStore.currentUser?.role) {
    case 'admin':   return 'purple'
    case 'manager': return 'blue'
    case 'staff':   return 'teal'
    default:        return 'grey'
  }
})

const newPassword = ref('')
const confirmPassword = ref('')
const showNewPassword = ref(false)
const showConfirmPassword = ref(false)
const isSubmitting = ref(false)
const newPasswordError = ref('')
const confirmPasswordError = ref('')
const errorMessage = ref('')
const successMessage = ref('')

const passwordRequirements = computed(() => {
  const policy = getPasswordPolicy()
  if (!policy) return null
  const p = policy.char_type_patterns
  const reqs = {
    length:    newPassword.value.length >= policy.min_length,
    uppercase: new RegExp(p.upper).test(newPassword.value),
    lowercase: new RegExp(p.lower).test(newPassword.value),
    number:    new RegExp(p.digit).test(newPassword.value),
    special:   new RegExp(p.special).test(newPassword.value),
  }
  const characterTypesMet = [reqs.uppercase, reqs.lowercase, reqs.number, reqs.special].filter(Boolean).length
  return {
    ...reqs,
    characterTypesMet,
    characterTypesValid: characterTypesMet >= policy.required_types_count,
    totalTypesCount: policy.total_types_count,
    labels: policy.labels,
  }
})

const isPasswordValid = computed(() =>
  passwordRequirements.value?.length &&
  passwordRequirements.value?.characterTypesValid &&
  newPassword.value === confirmPassword.value &&
  confirmPassword.value.length > 0
)

const handleChangePassword = async () => {
  newPasswordError.value = ''
  confirmPasswordError.value = ''
  errorMessage.value = ''
  successMessage.value = ''

  const policy = getPasswordPolicy()
  if (!policy) {
    newPasswordError.value = '密碼規則尚未載入，請重新整理頁面'
    return
  }
  if (!newPassword.value) {
    newPasswordError.value = '請輸入新密碼'
    return
  }
  if (!passwordRequirements.value?.length) {
    newPasswordError.value = policy.labels.min_length
    return
  }
  if (!passwordRequirements.value?.characterTypesValid) {
    newPasswordError.value = `密碼需符合以下字元類型要求：${policy.labels.required_types}`
    return
  }
  if (!confirmPassword.value) {
    confirmPasswordError.value = '請確認新密碼'
    return
  }
  if (newPassword.value !== confirmPassword.value) {
    confirmPasswordError.value = '兩次輸入的密碼不一致'
    return
  }

  isSubmitting.value = true
  try {
    const result = await userStore.changePassword(newPassword.value)
    if (result) {
      successMessage.value = '密碼已成功更換'
      newPassword.value = ''
      confirmPassword.value = ''
    } else {
      errorMessage.value = userStore.error || '密碼更換失敗，請重試'
    }
  } finally {
    isSubmitting.value = false
  }
}
</script>
