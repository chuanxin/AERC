<template>
  <v-container class="migration-container">
    <v-card
      max-width="450"
      class="mx-auto"
      rounded
    >
      <v-card-title>帳號轉移</v-card-title>

      <!-- Step 1: 驗證 OTP -->
      <div v-if="step === 'verify-otp'">
        <v-card-text>
          <p>請輸入您收到的6位數驗證碼</p>
          <v-text-field
            v-model="otp"
            label="驗證碼"
            maxlength="6"
          />
        </v-card-text>
        <v-card-actions>
          <v-btn
            variant="outlined"
            rounded="lg"
            block
            :ripple="false"
            :loading="loading"
            @click="verifyOTP"
          >
            驗證
          </v-btn>
        </v-card-actions>
      </div>

      <!-- Step 2: 更新個人資訊 + 設定密碼 -->
      <div v-if="step === 'update-info'">
        <v-card-text class="py-0">
          <v-alert
            type="info"
            class="mb-4"
            rounded
          >
            請確認並更新您的個人資訊，並設定新的登入密碼
          </v-alert>

          <!-- 姓名與帳號並列 -->
          <v-row>
            <v-col
              cols="7"
            >
              <v-text-field
                v-model="userInfo.full_name"
                variant="outlined"
                density="compact"
                :rules="[v => !!v || '姓名為必填欄位']"
                required
                hide-details
              >
                <template #label>
                  姓名 <span class="text-error">*</span>
                </template>
              </v-text-field>
            </v-col>
            <v-col
              cols="5"
            >
              <span class="d-block mt-2">
                原帳號：{{ userInfo.username }}
              </span>
            </v-col>
          </v-row>

          <!-- 所屬部門（條件式三級聯動） -->
          <!-- 管理處：獨立一列 -->
          <v-row>
            <v-col
              cols="12"
              class="pb-0"
            >
              <v-select
                v-model="selectedManagementOffice"
                :items="managementOffices"
                item-title="title"
                item-value="value"
                variant="outlined"
                density="compact"
                clearable
                :rules="[v => v != null || '管理處為必填欄位']"
                required
                hide-details
                @update:model-value="onManagementOfficeChange"
              >
                <template #label>
                  管理處 <span class="text-error">*</span>
                </template>
              </v-select>
            </v-col>
          </v-row>

          <!-- 分處 + 工作站：共用一列 -->
          <v-row v-if="hasBranches || hasStations">
            <!-- 分處（僅當有分處資料時顯示） -->
            <v-col
              v-if="hasBranches"
              cols="12"
              sm="6"
              class="pb-0"
            >
              <v-select
                v-model="selectedBranchOffice"
                :items="branchOffices"
                label="分處"
                item-title="title"
                item-value="value"
                variant="outlined"
                density="compact"
                clearable
                hide-details
                @update:model-value="onBranchOfficeChange"
              />
            </v-col>

            <!-- 工作站（僅當有工作站資料時顯示） -->
            <v-col
              v-if="hasStations"
              cols="12"
              :sm="hasBranches ? 6 : 12"
              class="pb-0"
            >
              <v-select
                v-model="selectedWorkStation"
                :items="workStations"
                label="工作站"
                item-title="title"
                item-value="value"
                variant="outlined"
                density="compact"
                clearable
                hide-details
                :disabled="hasBranches && !selectedBranchOffice"
              />
            </v-col>
          </v-row>

          <!-- 職稱 -->
          <v-row>
            <v-col
              cols="12"
              class="pb-0"
            >
              <v-select
                v-model="userInfo.job_title"
                :items="jobTitleOptions"
                variant="outlined"
                density="compact"
                clearable
                :rules="[v => !!v || '職稱為必填欄位']"
                required
                hide-details
              >
                <template #label>
                  職稱 <span class="text-error">*</span>
                </template>
              </v-select>
            </v-col>
          </v-row>

          <!-- 公務電話和分機 -->
          <v-row class="mb-0">
            <v-col
              cols="12"
              sm="8"
            >
              <v-text-field
                v-model="userInfo.phone"
                variant="outlined"
                density="compact"
                placeholder="區碼-號碼，例：04-12345678"
                :rules="[v => !!v || '公務電話為必填欄位']"
                required
                hide-details
              >
                <template #label>
                  公務電話 <span class="text-error">*</span>
                </template>
              </v-text-field>
            </v-col>
            <v-col
              cols="12"
              sm="4"
            >
              <v-text-field
                v-model="userInfo.phone_ext"
                label="分機"
                variant="outlined"
                density="compact"
                placeholder="例：123"
                hide-details
              />
            </v-col>
          </v-row>

          <!-- 手機 -->
          <v-text-field
            v-model="userInfo.mobile"
            label="手機"
            variant="outlined"
            density="compact"
            class="mb-2"
            placeholder="例：0912345678"
            hide-details
          />

          <v-divider class="my-0" />

          <v-text-field
            v-model="newPassword"
            type="password"
            hint="至少8字元，需包含以下4項中至少3項：數字、大寫、小寫、特殊符號"
            persistent-hint
            :rules="[v => !!v || '新密碼為必填欄位']"
            required
          >
            <template #label>
              新密碼 <span class="text-error">*</span>
            </template>
          </v-text-field>
          <v-text-field
            v-model="confirmPassword"
            type="password"
            :rules="[v => !!v || '確認密碼為必填欄位']"
            required
          >
            <template #label>
              確認密碼 <span class="text-error">*</span>
            </template>
          </v-text-field>
        </v-card-text>
        <v-card-actions>
          <v-btn
            variant="outlined"
            rounded="lg"
            block
            :ripple="false"
            :loading="loading"
            @click="completeMigration"
          >
            完成轉移
          </v-btn>
        </v-card-actions>
      </div>

      <!-- Step 3: 完成 -->
      <div v-if="step === 'completed'">
        <v-card-text>
          <v-alert
            type="success"
            rounded
          >
            帳號轉移成功！3秒後將跳轉至登入頁面...
          </v-alert>
        </v-card-text>
      </div>
    </v-card>
  </v-container>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { apiService } from '@/services/api/http'
import { USERS, OFFICES } from '@/services/api/endpoints'
import { useOfficesStore } from '@/stores/offices'

// 類型定義
interface UserInfo {
  username?: string
  full_name: string
  email?: string
  office_id?: number
  office_name?: string
  department?: string | Record<string, unknown>
  job_title?: string
  phone: string
  phone_ext: string
  mobile: string
}

interface OTPVerifyResponse {
  message: string
  success: boolean
  user_info: UserInfo
}

interface MigrationCompleteResponse {
  message: string
  success: boolean
}

interface ValidationError {
  loc: string[]
  msg: string
  type: string
}

interface ApiError {
  response?: {
    data?: {
      detail?: ValidationError[] | string | Record<string, unknown>
    }
    status?: number
  }
  message?: string
}

const route = useRoute()
const router = useRouter()
const officesStore = useOfficesStore()

const token = ref(route.query.token as string)
const step = ref('verify-otp')
const loading = ref(false)

const otp = ref('')
const userInfo = ref<UserInfo>({
  full_name: '',
  phone: '',
  phone_ext: '',
  mobile: ''
})

const newPassword = ref('')
const confirmPassword = ref('')

// 所屬部門三級聯動
const selectedManagementOffice = ref<number | null>(null)
const selectedBranchOffice = ref<string | null>(null)  // 改為 string（mng_code）
const selectedWorkStation = ref<string | null>(null)    // 改為 string（stn_code）

// 暫存需要還原的部門資料（用於 OTP 驗證後自動還原選擇）
const pendingDepartmentRestore = ref<{branch?: string, station?: string} | null>(null)

// 下拉選單選項
interface SelectOption {
  title: string
  value: string | number
}

const branchOffices = ref<SelectOption[]>([])
const workStations = ref<SelectOption[]>([])

// 職稱選項（依 Title_Id 順序）
const jobTitleOptions = [
  '管理師',      // 1
  '工程師',      // 2
  '秘書',        // 3
  '專員',        // 4
  '副管理師',    // 5
  '副工程師',    // 6
  '副專員',      // 7
  '二等助理管理師', // 8
  '二等助理工程師', // 9
  '二等組員',    // 10
  '三等助理管理師', // 11
  '三等助理工程師', // 12
  '三等組員',    // 13
  '管理員',      // 14
  '工程員',      // 15
  '辦事員',      // 16
  '助理員',      // 17
  '技工',        // 18
  '工友',        // 19
  '約僱',        // 20
  '組長',         // 21
  '灌溉股長', // 22
  '臨時人員',  // 23
  '職代',       // 24
  '專門委員', // 25
  '計畫人員',  // 26
  '科長',      // 27
  '正工程師', // 28
  '駐點/協辦',  // 29
  '助理技師', // 30
  '助理研究員', // 31
  '副技師', // 32
]

// 管理處選項（從 officesStore 載入）
const managementOffices = computed(() => {
  return officesStore.sortedOffices
    .filter(office => office.classification != 3)
    .map(office => ({
      title: office.name,
      value: office.id
    }))
})

// 判斷是否有分處資料
const hasBranches = computed(() => branchOffices.value.length > 0)

// 判斷是否有工作站資料
const hasStations = computed(() => workStations.value.length > 0)

// 當管理處變更時，載入分處列表，並根據是否有分處決定是否載入工作站
watch(selectedManagementOffice, async (officeId) => {
  selectedBranchOffice.value = null
  selectedWorkStation.value = null
  branchOffices.value = []
  workStations.value = []

  if (officeId != null) {
    try {
      // 先載入分處列表
      const branchesResponse = await apiService.get<Array<{code: string, name: string}>>(
        OFFICES.BRANCHES(officeId)
      )

      branchOffices.value = branchesResponse.map(b => ({
        title: b.name,
        value: b.code
      }))

      // 如果沒有分處，直接載入該管理處的所有工作站
      if (branchOffices.value.length === 0) {
        const stationsResponse = await apiService.get<Array<{code: string, name: string}>>(
          OFFICES.STATIONS(officeId)
        )
        workStations.value = stationsResponse.map(s => ({
          title: s.name,
          value: s.code
        }))

        // 載入完成後，檢查是否有待還原的工作站
        if (pendingDepartmentRestore.value?.station) {
          selectedWorkStation.value = pendingDepartmentRestore.value.station
          pendingDepartmentRestore.value = null
        }
      } else if (pendingDepartmentRestore.value?.branch) {
        // 如果有待還原的分處，自動選擇
        selectedBranchOffice.value = pendingDepartmentRestore.value.branch
      }
      // 如果有分處，等待使用者選擇分處後才載入工作站（由下面的 watch 處理）
    } catch (error) {
      console.error('載入分處/工作站列表失敗:', error)
    }
  }
})

// 當分處變更時，載入該分處的工作站列表
watch(selectedBranchOffice, async (branchCode) => {
  selectedWorkStation.value = null
  workStations.value = []

  // 只有當選擇了分處時才載入工作站
  if (branchCode && selectedManagementOffice.value) {
    try {
      const response = await apiService.get<Array<{code: string, name: string}>>(
        OFFICES.STATIONS_BY_BRANCH(selectedManagementOffice.value, branchCode)
      )
      workStations.value = response.map(s => ({
        title: s.name,
        value: s.code
      }))

      // 載入完成後，檢查是否有待還原的工作站
      if (pendingDepartmentRestore.value?.station) {
        selectedWorkStation.value = pendingDepartmentRestore.value.station
        pendingDepartmentRestore.value = null
      }
    } catch (error) {
      console.error('載入工作站列表失敗:', error)
    }
  }
})

// 管理處變更時，重置下級選項（由 watch 處理）
const onManagementOfficeChange = () => {
  // watch 會自動處理
}

// 分處變更時，重置工作站（由 watch 處理）
const onBranchOfficeChange = () => {
  // watch 會自動處理
}

// 載入 offices 資料
onMounted(async () => {
  if (!officesStore.isOfficesLoaded) {
    await officesStore.fetchOffices()
  }
})

const verifyOTP = async () => {
  loading.value = true
  try {
    const response = await apiService.post<OTPVerifyResponse>(USERS.MIGRATE_VERIFY_OTP, {
      token: token.value,
      otp: otp.value
    })

    if (response.success && response.user_info) {
      // 填充基本使用者資訊
      userInfo.value = {
        username: response.user_info.username || '',
        full_name: response.user_info.full_name || '',
        email: response.user_info.email,
        office_name: response.user_info.office_name,
        department: response.user_info.department,
        job_title: response.user_info.job_title || '',
        phone: response.user_info.phone || '',
        phone_ext: response.user_info.phone_ext || '',
        mobile: response.user_info.mobile || ''
      }

      // 解析並暫存需要還原的部門資料
      if (response.user_info.department && typeof response.user_info.department === 'object') {
        const dept = response.user_info.department as Record<string, { code: string, name: string }>

        // 暫存部門資料，讓 watch 在載入完成後自動還原
        pendingDepartmentRestore.value = {
          branch: dept.branch?.code,
          station: dept.station?.code
        }
      }

      // 還原所屬管理處（會觸發 watch 載入分處/工作站，並自動還原選擇）
      if (response.user_info.office_id != null) {
        selectedManagementOffice.value = response.user_info.office_id
      }

      step.value = 'update-info'
    }
  } catch {
    alert('驗證碼錯誤或已過期')
  } finally {
    loading.value = false
  }
}

const completeMigration = async () => {
  console.log('=== completeMigration START ===')
  console.log('Current state:', {
    token: token.value,
    otp: otp.value,
    userInfo: userInfo.value,
    newPassword: newPassword.value ? '***' : '(empty)',
    confirmPassword: confirmPassword.value ? '***' : '(empty)'
  })

  // 驗證必填欄位
  if (!userInfo.value.full_name) {
    alert('請填寫姓名')
    return
  }

  if (selectedManagementOffice.value == null) {
    alert('請選擇管理處')
    return
  }

  if (!userInfo.value.job_title) {
    alert('請選擇職稱')
    return
  }

  if (!userInfo.value.phone) {
    alert('請填寫公務電話')
    return
  }

  // 驗證台灣市話格式：區碼-號碼（以連字號分隔）
  // 台灣市話區碼規則：
  // - 02: 台北/新北/基隆 (8位號碼)
  // - 03: 桃園/新竹/宜蘭/花蓮 (7位號碼)
  // - 04: 台中/彰化 (7-8位號碼)
  // - 05: 雲林/嘉義 (7位號碼)
  // - 06: 台南 (7位號碼)
  // - 07: 高雄 (7位號碼)
  // - 08: 屏東 (7位號碼)
  // - 037: 苗栗 (6位號碼)
  // - 049: 南投 (7位號碼)
  // - 089: 台東 (6位號碼)
  // - 082: 金門 (6位號碼)
  // - 0836: 馬祖 (5位號碼)
  const phonePatterns = [
    /^02-\d{8}$/,           // 台北/新北/基隆: 02-12345678
    /^0[3-8]-\d{7,8}$/,     // 桃園~屏東: 03-1234567, 04-12345678
    /^037-\d{6}$/,          // 苗栗: 037-123456
    /^049-\d{7}$/,          // 南投: 049-1234567
    /^089-\d{6}$/,          // 台東: 089-123456
    /^082-\d{6}$/,          // 金門: 082-123456
    /^0836-\d{5}$/          // 馬祖: 0836-12345
  ]
  const isValidPhone = phonePatterns.some(pattern => pattern.test(userInfo.value.phone))
  if (!isValidPhone) {
    alert('公務電話格式不正確，請使用「區碼-號碼」格式\n\n範例：\n• 02-12345678（台北）\n• 04-12345678（台中）\n• 049-1234567（南投）')
    return
  }

  // 驗證手機格式（選填，但若有填寫則需符合格式）
  if (userInfo.value.mobile) {
    const mobileRegex = /^09\d{8}$/
    if (!mobileRegex.test(userInfo.value.mobile)) {
      alert('手機號碼格式不正確，請使用格式：09開頭的10位數字（例：0912345678）')
      return
    }
  }

  if (!newPassword.value) {
    alert('請填寫新密碼')
    return
  }

  if (!confirmPassword.value) {
    alert('請填寫確認密碼')
    return
  }

  if (newPassword.value !== confirmPassword.value) {
    alert('密碼與確認密碼不符')
    return
  }

  loading.value = true
  try {
    // 準備請求資料
    const payload: Record<string, string | number> = {
      token: token.value,
      otp: otp.value,
      new_password: newPassword.value,
      confirm_password: confirmPassword.value
    }

    // 只添加有值的欄位
    if (userInfo.value.full_name) payload.full_name = userInfo.value.full_name
    if (userInfo.value.job_title) payload.job_title = userInfo.value.job_title
    if (userInfo.value.phone) payload.phone = userInfo.value.phone
    if (userInfo.value.phone_ext) payload.phone_ext = userInfo.value.phone_ext
    if (userInfo.value.mobile) payload.mobile = userInfo.value.mobile

    // 所屬單位：儲存管理處 ID 到 office_id（使用數字類型）
    if (selectedManagementOffice.value != null) {
      payload.office_id = selectedManagementOffice.value
    }

    // 部門詳細資訊：儲存為 JSON
    const departmentData: Record<string, unknown> = {}
    if (selectedBranchOffice.value && branchOffices.value.length) {
      const branch = branchOffices.value.find(b => b.value === selectedBranchOffice.value)
      if (branch) {
        departmentData.branch = {
          code: String(selectedBranchOffice.value),
          name: branch.title
        }
      }
    }
    if (selectedWorkStation.value && workStations.value.length) {
      const station = workStations.value.find(s => s.value === selectedWorkStation.value)
      if (station) {
        departmentData.station = {
          code: String(selectedWorkStation.value),
          name: station.title
        }
      }
    }
    if (Object.keys(departmentData).length > 0) {
      payload.department = JSON.stringify(departmentData)
    }

    console.log('Migration payload:', payload)
    console.log('Sending request to:', USERS.MIGRATE)

    const response = await apiService.post<MigrationCompleteResponse>(USERS.MIGRATE, payload)

    if (response.success) {
      step.value = 'completed'

      // 3秒後跳轉登入頁
      setTimeout(() => {
        router.push('/login')
      }, 3000)
    }
  } catch (err) {
    const error = err as ApiError
    console.error('=== Migration error ===')
    console.error('Full error object:', error)
    console.error('Response data:', error?.response?.data)
    console.error('Response status:', error?.response?.status)

    // 處理 Pydantic 驗證錯誤（422）
    let errorMessage = '轉移失敗，請稍後再試'
    if (error?.response?.data?.detail) {
      const detail = error.response.data.detail
      console.log('Error detail:', detail)

      if (Array.isArray(detail)) {
        // Pydantic 驗證錯誤格式
        errorMessage = detail.map((err: ValidationError) =>
          `${err.loc?.join('.') || '欄位'}: ${err.msg}`
        ).join('\n')
      } else if (typeof detail === 'string') {
        errorMessage = detail
      } else {
        // 其他格式，直接 JSON 化
        errorMessage = JSON.stringify(detail, null, 2)
      }
    }

    console.error('Final error message:', errorMessage)
    alert(errorMessage)
  } finally {
    loading.value = false
  }
}
</script>

<route lang="yaml">
meta:
  layout: auth
  public: true
</route>
