<template>
  <v-container
    fluid
    class="grants-container px-6 pb-0 pt-0"
    style="background-color: white"
  >
    <v-row justify="center">
      <v-col cols="10" lg="10" align-self="center" class="pt-0">
        <!-- 變更密碼按鈕 -->
        <div class="d-flex flex-wrap align-center pr-2">
          <v-spacer />
          <div class="d-flex gap-2">
            <v-btn
              class="action-btn"
              color="primary"
              prepend-icon="mdi-lock-reset"
              variant="outlined"
              rounded="lg"
              size="large"
              @click="showPasswordDialog = true"
            >
              變更密碼
            </v-btn>
          </div>
        </div>

        <div class="section-wrapper">
          <v-card class="mx-auto section-card pa-4" rounded="lg" variant="outlined">
            <v-card-item class="custom-title">
              <v-card-title class="text-h5 font-weight-black">
                我的帳號
                <v-chip :color="roleColor" size="small" label class="ml-2">
                  {{ roleLabel }}
                </v-chip>
              </v-card-title>
            </v-card-item>

            <v-card-text>
              <v-alert
                v-if="profileMessage.show"
                :type="profileMessage.color"
                variant="tonal"
                density="compact"
                border="start"
                class="mb-3"
                closable
                @click:close="profileMessage.show = false"
              >
                {{ profileMessage.text }}
              </v-alert>

              <v-form ref="profileFormRef">
                <v-row dense>
                  <v-col cols="12" sm="6">
                    <div class="d-flex align-center field-row">
                      <span class="text-subtitle-2 text-grey-darken-1" style="min-width: 70px;">帳號</span>
                      <v-divider vertical class="mx-3" />
                      <span class="text-body-1 font-weight-medium">{{ userStore.currentUser?.username || '—' }}</span>
                    </div>
                  </v-col>
                  <v-col cols="12" sm="6">
                    <div class="d-flex align-center field-row">
                      <span class="text-subtitle-2 text-grey-darken-1" style="min-width: 70px;">Email</span>
                      <v-divider vertical class="mx-3" />
                      <span class="text-body-1 font-weight-medium">{{ userStore.currentUser?.email || '—' }}</span>
                    </div>
                  </v-col>
                  <v-col cols="12" sm="6">
                    <div class="d-flex align-center field-row">
                      <span class="text-subtitle-2 text-grey-darken-1" style="min-width: 70px;">所屬管理處</span>
                      <v-divider vertical class="mx-3" />
                      <span class="text-body-1 font-weight-medium">{{ userStore.currentUser?.office?.name || '—' }}</span>
                    </div>
                  </v-col>
                  <v-col cols="12" sm="6">
                    <div class="d-flex align-center field-row">
                      <span class="text-subtitle-2 text-grey-darken-1" style="min-width: 70px;">工作站</span>
                      <v-divider vertical class="mx-3" />
                      <span class="text-body-1 font-weight-medium">{{ stationName || '—' }}</span>
                    </div>
                  </v-col>
                  <v-col
                    v-for="field in editableFieldDefs"
                    :key="field.key"
                    cols="12"
                    sm="6"
                  >
                    <div class="d-flex align-center field-row">
                      <!-- 左側 label 脈絡固定保留，不隨編輯態消失 -->
                      <span class="text-subtitle-2 text-grey-darken-1" style="min-width: 70px;">{{ field.label }}</span>
                      <v-divider vertical class="mx-3" />
                      <!-- 未編輯態：值 + 鉛筆；有未儲存異動時鉛筆旁附「還原」按鈕 -->
                      <template v-if="!editingFields[field.key]">
                        <span class="text-body-1 font-weight-medium">{{ displayFieldValue(field.key) }}</span>
                        <v-btn
                          v-if="hasUnsavedChange(field.key)"
                          icon="mdi-restore"
                          size="x-small"
                          variant="text"
                          color="orange-darken-2"
                          class="ml-1"
                          :aria-label="`還原${field.label}`"
                          :title="`還原${field.label}為已儲存值`"
                          @click="revertField(field.key)"
                        />
                        <v-btn
                          icon="mdi-pencil-outline"
                          size="x-small"
                          variant="text"
                          color="grey"
                          class="ml-1"
                          :aria-label="`編輯${field.label}`"
                          @click="startEditField(field.key)"
                        />
                      </template>
                      <!-- 編輯態：輸入框 + ✕ 就地還原（Inverse Action） -->
                      <template v-else>
                        <v-text-field
                          v-model="profileForm[field.key]"
                          variant="outlined"
                          density="compact"
                          hide-details="auto"
                          autofocus
                          class="flex-grow-1"
                          :rules="field.rules"
                          :maxlength="field.maxlength"
                          @input="onFieldInput()"
                          @focus="onFieldFocus(field.key)"
                          @blur="onFieldBlur(field.key)"
                        />
                        <v-btn
                          icon="mdi-close-circle-outline"
                          size="small"
                          variant="text"
                          color="grey"
                          class="ml-1"
                          :aria-label="`完成編輯${field.label}`"
                          :title="`完成編輯${field.label}（值已保留，可稍後一次儲存）`"
                          @click="cancelEditField(field.key)"
                        />
                      </template>
                    </div>
                  </v-col>
                </v-row>
              </v-form>
            </v-card-text>

            <v-card-actions v-if="hasPendingChanges">
              <v-spacer />
              <!-- 底部僅保留「儲存」：以 partial 批次送出所有正在編輯的欄位；
                   每個欄位自身的 ✕ 已提供就地逆向動作，故不再需要全域「取消」 -->
              <v-btn
                color="primary"
                variant="flat"
                :loading="profileSaving"
                @click="handleSaveProfile"
              >
                儲存
              </v-btn>
            </v-card-actions>
          </v-card>
        </div>
      </v-col>
    </v-row>

    <!-- 變更密碼對話窗 -->
    <v-dialog v-model="showPasswordDialog" max-width="600" persistent>
      <v-card rounded="lg">
        <v-card-title class="text-h6 font-weight-bold">
          變更密碼
        </v-card-title>

        <v-card-text>
          <v-form ref="passwordFormRef" @submit.prevent="handleChangePassword">
            <div class="text-body-2 font-weight-medium mb-2">新密碼</div>
            <v-text-field
              v-model="newPassword"
              :type="showNewPassword ? 'text' : 'password'"
              variant="outlined"
              density="compact"
              bg-color="white"
              :error="!!newPasswordError"
              :error-messages="newPasswordError"
              hide-details="auto"
              autocomplete="new-password"
              class="mb-3"
            >
              <template #append-inner>
                <v-icon
                  :icon="showNewPassword ? 'mdi-eye-off' : 'mdi-eye'"
                  size="small"
                  @click="showNewPassword = !showNewPassword"
                />
              </template>
            </v-text-field>

            <div class="text-body-2 font-weight-medium mb-2">確認新密碼</div>
            <v-text-field
              v-model="confirmPassword"
              :type="showConfirmPassword ? 'text' : 'password'"
              variant="outlined"
              density="compact"
              bg-color="white"
              :error="!!confirmPasswordError"
              :error-messages="confirmPasswordError"
              hide-details="auto"
              autocomplete="new-password"
              class="mb-3"
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
                <div class="text-body-2 font-weight-medium mb-2">密碼要求</div>
                <template v-if="policyLoading">
                  <div class="d-flex align-center text-grey py-1">
                    <v-progress-circular size="14" width="2" indeterminate class="mr-2" />
                    密碼規則載入中...
                  </div>
                </template>
                <template v-else-if="policyLoadError">
                  <div class="d-flex align-center text-error py-1">
                    <v-icon size="small" icon="mdi-alert-circle" class="mr-1" />
                    無法取得密碼規則，請重新整理頁面
                  </div>
                </template>
                <template v-else-if="passwordRequirements">
                  <div class="d-flex align-center mb-1">
                    <v-icon
                      :icon="passwordRequirements.length ? 'mdi-check-circle' : 'mdi-circle-outline'"
                      :color="passwordRequirements.length ? 'success' : 'grey'"
                      size="x-small" class="mr-1"
                    />
                    <span>{{ passwordRequirements.labels.min_length }}</span>
                  </div>
                  <div class="d-flex align-center mb-1">
                    <v-icon
                      :icon="passwordRequirements.characterTypesValid ? 'mdi-check-circle' : 'mdi-circle-outline'"
                      :color="passwordRequirements.characterTypesValid ? 'success' : 'grey'"
                      size="x-small" class="mr-1"
                    />
                    <span>{{ passwordRequirements.labels.required_types }} (目前 {{ passwordRequirements.characterTypesMet }}/{{ passwordRequirements.totalTypesCount }})</span>
                  </div>
                  <div class="ml-4">
                    <div class="d-flex align-center">
                      <v-icon
                        :icon="passwordRequirements.number ? 'mdi-check' : 'mdi-minus'"
                        :color="passwordRequirements.number ? 'success' : 'grey'"
                        size="x-small" class="mr-1"
                      />
                      <span>{{ passwordRequirements.labels.has_digit }}</span>
                      <span class="mx-1">•</span>
                      <v-icon
                        :icon="passwordRequirements.uppercase ? 'mdi-check' : 'mdi-minus'"
                        :color="passwordRequirements.uppercase ? 'success' : 'grey'"
                        size="x-small" class="mr-1"
                      />
                      <span>{{ passwordRequirements.labels.has_upper }}</span>
                    </div>
                    <div class="d-flex align-center">
                      <v-icon
                        :icon="passwordRequirements.lowercase ? 'mdi-check' : 'mdi-minus'"
                        :color="passwordRequirements.lowercase ? 'success' : 'grey'"
                        size="x-small" class="mr-1"
                      />
                      <span>{{ passwordRequirements.labels.has_lower }}</span>
                      <span class="mx-1">•</span>
                      <v-icon
                        :icon="passwordRequirements.special ? 'mdi-check' : 'mdi-minus'"
                        :color="passwordRequirements.special ? 'success' : 'grey'"
                        size="x-small" class="mr-1"
                      />
                      <span>{{ passwordRequirements.labels.has_special }}</span>
                    </div>
                  </div>
                </template>
              </v-card-text>
            </v-card>

            <v-alert v-if="errorMessage" type="error" variant="tonal" density="compact" border="start" icon="mdi-alert-circle" class="mb-3">
              {{ errorMessage }}
            </v-alert>

            <v-alert v-if="successMessage" type="success" variant="tonal" density="compact" border="start" class="mb-3">
              {{ successMessage }}
            </v-alert>
          </v-form>
        </v-card-text>

        <v-card-actions>
          <v-spacer />
          <v-btn variant="text" @click="cancelChangePassword">取消</v-btn>
          <v-btn color="primary" :loading="isSubmitting" :disabled="!isPasswordValid || isSubmitting" @click="handleChangePassword">
            變更密碼
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script lang="ts" setup>
import { useUserStore } from '@/stores/users'
import { DEFAULT_ROLES, getRoleColor } from '@/types/permissions'
import {
  getPasswordPolicy,
  policyLoading,
  policyLoadError,
} from '@/services/passwordPolicyService'
import { userService } from '@/services/userService'

const userStore = useUserStore()
const showPasswordDialog = ref(false)

const roleLabel = computed(() => {
  const role = userStore.currentUser?.role
  return DEFAULT_ROLES.find(r => r.value === role)?.title ?? role ?? '—'
})

const roleColor = computed(() => getRoleColor(userStore.currentUser?.role))

// 個人資料編輯（039-account-verification-profile）
const stationName = computed(() => {
  const department = userStore.currentUser?.department as { station?: { name?: string } } | undefined
  return department?.station?.name || ''
})

type EditableFieldKey = 'full_name' | 'phone' | 'phone_ext' | 'mobile'
type FieldRule = (v: string) => boolean | string

// 必填規則比照註冊表單（signup.vue）：姓名／聯絡電話必填，分機／手機選填可清空。
// 長度上限由 maxlength 屬性擋下，與後端 schema 一致，不重複宣告規則。
const requiredRule = (label: string): FieldRule =>
  (v: string) => !!(v || '').trim() || `${label}為必填欄位`

const editableFieldDefs: Array<{
  key: EditableFieldKey
  label: string
  maxlength: number
  rules: FieldRule[]
}> = [
  { key: 'full_name', label: '姓名', maxlength: 50, rules: [requiredRule('姓名')] },
  { key: 'mobile', label: '手機', maxlength: 20, rules: [] },
  { key: 'phone', label: '聯絡電話', maxlength: 20, rules: [requiredRule('聯絡電話')] },
  { key: 'phone_ext', label: '分機', maxlength: 10, rules: [] },
]

const profileFormRef = ref()

const profileForm = reactive<Record<EditableFieldKey, string>>({
  full_name: '',
  phone: '',
  phone_ext: '',
  mobile: '',
})

const editingFields = reactive<Record<EditableFieldKey, boolean>>({
  full_name: false,
  phone: false,
  phone_ext: false,
  mobile: false,
})

// 該欄是否有未儲存異動：工作值 vs 已儲存值（兩邊都 trim，避免已儲存資料本身帶空白時
// 頁面一載入就誤判為有未儲存異動）
function hasUnsavedChange(key: EditableFieldKey): boolean {
  return profileForm[key].trim() !== (userStore.currentUser?.[key] || '').trim()
}

// 未編輯態顯示值：有未儲存異動顯示工作值，否則顯示已儲存值。
// 待儲存的「清空」也要顯示 '—'，否則該列只剩分隔線與按鈕、看起來像破圖
function displayFieldValue(key: EditableFieldKey): string {
  return hasUnsavedChange(key) ? (profileForm[key] || '—') : (userStore.currentUser?.[key] || '—')
}

// 真正還原該欄為已儲存值（放棄未儲存異動）
function revertField(key: EditableFieldKey) {
  profileForm[key] = userStore.currentUser?.[key] || ''
}

// 是否任一欄有未儲存異動（決定底部「儲存」是否顯示）
const hasPendingChanges = computed(() =>
  editableFieldDefs.some(f => hasUnsavedChange(f.key))
)

const profileSaving = ref(false)

const profileMessage = ref<{ show: boolean; text: string; color: 'success' | 'error' | 'info' }>({
  show: false,
  text: '',
  color: 'success',
})

// 初次（currentUser 尚未載入）時 profileForm 全為空、無從比對異動，故一律種子化；
// 之後只覆寫「無未儲存異動」的欄位——避免任何 fetchCurrentUser 路徑把收起中的未儲存異動靜默清掉。
let profileFormInitialized = false
function fillProfileFormFromCurrentUser() {
  const cu = userStore.currentUser
  if (!profileFormInitialized) {
    if (cu) {
      for (const field of editableFieldDefs) {
        profileForm[field.key] = cu?.[field.key] || ''
      }
      profileFormInitialized = true
    }
    return
  }
  for (const field of editableFieldDefs) {
    if (!hasUnsavedChange(field.key)) {
      profileForm[field.key] = cu?.[field.key] || ''
    }
  }
}

watch(() => userStore.currentUser, fillProfileFormFromCurrentUser, { immediate: true })

function startEditField(key: EditableFieldKey) {
  // 不重設 profileForm[key]：保留既有值（可能含先前未儲存異動），避免打斷累積編輯
  clearBlurTimer(key)
  profileMessage.value.show = false
  editingFields[key] = true
}

// 收起該欄輸入框（僅還原編輯「樣式」）：保留使用者尚未儲存的異動值。
// 若要真正放棄該欄異動，改用鉛筆旁的「還原」按鈕（revertField）。
function cancelEditField(key: EditableFieldKey) {
  editingFields[key] = false
}

// 每個欄位一個 pending blur-cancel timer；focus 恢復時清除，避免「blur 後快速重新聚焦」被誤收起
const fieldBlurTimers: Partial<Record<EditableFieldKey, number>> = {}

function clearBlurTimer(key: EditableFieldKey) {
  if (fieldBlurTimers[key] !== undefined) {
    window.clearTimeout(fieldBlurTimers[key])
    delete fieldBlurTimers[key]
  }
}

// focus 只負責維持編輯態、取消待執行的收起動作。
// 欄位錯誤本身交給 Vuetify 的 :rules 管理（validate-on 預設為 input，輸入當下即時顯示紅框與訊息）。
function onFieldFocus(key: EditableFieldKey) {
  clearBlurTimer(key)
  editingFields[key] = true
}

// 使用者一開始輸入就收起頁面層級提示（欄位層級錯誤由 :rules 自行處理）
function onFieldInput() {
  profileMessage.value.show = false
}

// blur 退出編輯態（暫時性）：點擊輸入框之外的任一位置即「收起輸入框」、保留未儲存值。
// 用 setTimeout 延遲，避免「點『儲存』按鈕」先觸發 blur 而把編輯態關掉、導致儲存讀到空清單的競態。
function onFieldBlur(key: EditableFieldKey) {
  if (!editingFields[key]) return
  if (fieldBlurTimers[key] !== undefined) window.clearTimeout(fieldBlurTimers[key])
  fieldBlurTimers[key] = window.setTimeout(() => {
    delete fieldBlurTimers[key]
    if (editingFields[key]) cancelEditField(key)
  }, 150)
}

// 組裝 partial payload：送「所有有未儲存異動」的欄位（驗證已由 v-form 完成）。
// phone_ext / mobile 可清空，空字串也送出。
function buildPartialPayload(): Partial<Record<EditableFieldKey, string>> {
  const payload: Partial<Record<EditableFieldKey, string>> = {}
  for (const field of editableFieldDefs) {
    if (!hasUnsavedChange(field.key)) continue
    payload[field.key] = profileForm[field.key].trim()
  }
  return payload
}

async function handleSaveProfile() {
  const changedKeys = editableFieldDefs.filter(f => hasUnsavedChange(f.key)).map(f => f.key)
  if (changedKeys.length === 0) return

  // v-form.validate() 只會驗證「已掛載」的輸入框，故先展開所有有異動的欄位，
  // 讓 Vuetify 就地渲染紅框與錯誤訊息；同時取消點「儲存」前 blur 已排定的收起 timer。
  for (const key of changedKeys) {
    clearBlurTimer(key)
    editingFields[key] = true
  }
  await nextTick()

  const { valid } = await profileFormRef.value.validate()
  if (!valid) {
    profileMessage.value = { show: true, text: '請修正標示的欄位後再儲存', color: 'error' }
    return
  }

  const payload = buildPartialPayload()
  if (Object.keys(payload).length === 0) return  // 無異動可送（防禦性）

  profileSaving.value = true
  try {
    await userService.updateMyProfile(payload)
    profileMessage.value = { show: true, text: '個人資料已更新', color: 'success' }
  } catch (error: unknown) {
    const detail = (error as { response?: { data?: { detail?: string } } })?.response?.data?.detail
    profileMessage.value = {
      show: true,
      text: typeof detail === 'string' ? detail : '更新失敗，請稍後再試',
      color: 'error',
    }
    return
  } finally {
    profileSaving.value = false
  }

  // 更新成功後才關閉編輯態並同步最新值；fetch 失敗不影響已成功的更新結果
  for (const key of Object.keys(payload)) editingFields[key as EditableFieldKey] = false
  try {
    await userStore.fetchCurrentUser()
    fillProfileFormFromCurrentUser()
  } catch {
    /* 同步失敗可忽略——資料已更新成功 */
  }
}

const passwordFormRef = ref()
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

function cancelChangePassword() {
  showPasswordDialog.value = false
  newPassword.value = ''
  confirmPassword.value = ''
  newPasswordError.value = ''
  confirmPasswordError.value = ''
  errorMessage.value = ''
  successMessage.value = ''
}

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
      showPasswordDialog.value = false
    } else {
      errorMessage.value = userStore.error || '密碼更換失敗，請重試'
    }
  } finally {
    isSubmitting.value = false
  }
}
</script>

<style scoped>
.section-wrapper {
  margin-top: 16px;
}

/* 我的帳號卡片：統一每個 col 內容行高（含按鈕列與編輯態輸入框），行距視覺一致 */
.field-row {
  min-height: 44px;
}
</style>
