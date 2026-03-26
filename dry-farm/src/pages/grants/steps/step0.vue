<template>
  <v-card
    flat
    class="form-container pa-6 pb-2"
  >
    <v-form
      ref="form"
      v-model="localValid"
      lazy-validation
      @submit.prevent
    >
      <v-row>
        <!-- 申請人基本資料 -->
        <v-col
          cols="12"
          md="6"
        >
          <v-card
            flat
            class="mb-4 pa-4"
            color="#e3f4f4"
            rounded="lg"
          >
            <v-card-title
              class="text-subtitle-1 font-weight-bold pa-0 pb-6"
              style="color: #2d8c8f"
            >
              <v-icon
                color="#3ea0a3"
                class="me-2 pb-1"
                size="small"
              >
                mdi-account
              </v-icon>
              <span class="required-asterisk">*</span>申請人基本資料
            </v-card-title>

            <v-row dense>
              <v-col
                cols="12"
                md="6"
              >
                <v-text-field
                  v-model="localFormData.name"
                  variant="outlined"
                  density="comfortable"
                  color="#3ea0a3"
                  bg-color="white"
                  required
                  autocomplete="off"
                  :rules="nameRules"
                >
                  <template #label>
                    申請人姓名
                  </template>
                </v-text-field>
              </v-col>

              <v-col
                cols="12"
                md="6"
              >
                <v-text-field
                  v-model="localFormData.id"
                  variant="outlined"
                  density="comfortable"
                  color="#3ea0a3"
                  bg-color="white"
                  hint="例：A123456789"
                  persistent-hint
                  required
                  autocomplete="off"
                  :rules="idRules"
                >
                  <template #label>
                    身分證字號
                  </template>
                </v-text-field>
              </v-col>
            </v-row>
            <v-row dense>
              <v-col cols="12">
                <v-text-field
                  v-model="localFormData.phone"
                  variant="outlined"
                  density="comfortable"
                  color="#3ea0a3"
                  bg-color="white"
                  required
                  autocomplete="off"
                  placeholder="手機或市話號碼"
                  :rules="phoneRules"
                >
                  <template #label>
                    聯絡電話
                  </template>
                </v-text-field>
              </v-col>
            </v-row>
          </v-card>
        </v-col>

        <!-- 申請人通訊地址 -->
        <v-col
          cols="12"
          md="6"
        >
          <v-card
            flat
            class="mb-4 pa-4"
            color="#e3f4f4"
            rounded="lg"
          >
            <v-card-title
              class="text-subtitle-1 font-weight-bold pa-0 pb-6"
              style="color: #2d8c8f"
            >
              <v-icon
                color="#3ea0a3"
                class="me-2 pb-1"
                size="small"
              >
                mdi-map-marker
              </v-icon>
              <span class="required-asterisk">*</span>申請人通訊地址
            </v-card-title>

            <v-row dense>
              <v-col
                cols="12"
                md="4"
              >
                <v-select
                  v-model="selectedCountyId"
                  :items="countyItems"
                  item-title="title"
                  item-value="value"
                  variant="outlined"
                  density="comfortable"
                  color="#3ea0a3"
                  bg-color="white"
                  :loading="domicileStore.isLoading"
                  return-object
                  @update:model-value="handleCountyChange"
                >
                  <template #label>
                    縣市
                  </template>
                </v-select>
              </v-col>

              <v-col
                cols="12"
                md="4"
              >
                <v-select
                  v-model="selectedTownId"
                  :items="townItems"
                  item-title="title"
                  item-value="value"
                  variant="outlined"
                  density="comfortable"
                  color="#3ea0a3"
                  bg-color="white"
                  :loading="domicileStore.isLoading"
                  :disabled="!selectedCountyId"
                  return-object
                  @update:model-value="handleTownChange"
                >
                  <template #label>
                    鄉鎮市區
                  </template>
                </v-select>
              </v-col>

              <v-col
                cols="12"
                md="4"
              >
                <v-select
                  v-model="selectedVillageId"
                  :items="villageItems"
                  item-title="title"
                  item-value="value"
                  variant="outlined"
                  density="comfortable"
                  color="#3ea0a3"
                  bg-color="white"
                  :loading="domicileStore.isLoading"
                  :disabled="!selectedTownId"
                  return-object
                  @update:model-value="handleVillageChange"
                >
                  <template #label>
                    村里
                  </template>
                </v-select>
              </v-col>

              <v-col cols="12">
                <v-text-field
                  v-model="localFormData.address"
                  variant="outlined"
                  density="comfortable"
                  color="#3ea0a3"
                  bg-color="white"
                  placeholder="例：中正路100號"
                  autocomplete="off"
                  :rules="[v => !!v || '請輸入詳細地址']"
                >
                  <template #label>
                    詳細地址
                  </template>
                </v-text-field>
              </v-col>
            </v-row>
          </v-card>
        </v-col>
      </v-row>

      <!-- 💰 年度補助額度簡要提示 -->
      <v-alert
        v-if="showSubsidySummary"
        :type="subsidyAlertType"
        variant="tonal"
        density="compact"
        class="mb-4"
      >
        <template #prepend>
          <v-icon :icon="subsidyIcon" />
        </template>

        <!-- Loading 狀態 -->
        <div
          v-if="grantsStore.subsidySummaryLoading"
          class="d-flex align-center"
        >
          <v-progress-circular
            indeterminate
            size="16"
            width="2"
            class="me-2"
          />
          <span class="text-body-2">查詢補助額度中...</span>
        </div>

        <!-- 錯誤狀態 -->
        <div
          v-else-if="grantsStore.subsidySummaryError"
          class="text-body-2"
        >
          {{ grantsStore.subsidySummaryError }}
        </div>

        <!-- 簡要額度資訊 -->
        <div
          v-else-if="grantsStore.hasSubsidySummary"
          class="d-flex align-center justify-space-between flex-wrap"
        >
          <div class="text-body-2">
            <strong>年度補助額度</strong>
            <span class="mx-2">｜</span>
            已用 <strong>{{ formatCurrency(grantsStore.totalSubsidyAmount) }}</strong>
            <span class="mx-1">/</span>
            上限 {{ formatCurrency(grantsStore.subsidyLimit) }}
            <span class="mx-2">｜</span>
            剩餘 <strong :class="remainingAmountColorClass">{{ formatCurrency(grantsStore.remainingSubsidyAmount) }}</strong>
            <span
              v-if="grantsStore.subsidySummary && grantsStore.subsidySummary.grant_count > 0"
              class="text-caption text-medium-emphasis ms-2"
            >
              (本年度已申請 {{ grantsStore.subsidySummary.grant_count }} 筆)
            </span>
          </div>

          <!-- 展開詳情按鈕 -->
          <v-btn
            v-if="grantsStore.hasSubsidySummary"
            :icon="subsidyDetailsExpanded ? 'mdi-chevron-up' : 'mdi-information-outline'"
            variant="text"
            size="x-small"
            density="compact"
            @click="subsidyDetailsExpanded = !subsidyDetailsExpanded"
          >
            <v-tooltip
              activator="parent"
              location="top"
            >
              {{ subsidyDetailsExpanded ? '收起詳情' : '查看詳情' }}
            </v-tooltip>
          </v-btn>
        </div>

        <!-- 展開的詳細資訊 -->
        <v-expand-transition>
          <div
            v-if="subsidyDetailsExpanded && grantsStore.hasSubsidySummary"
            class="mt-3 pt-3 border-t"
          >
            <!-- 案件列表 -->
            <div
              v-if="grantsStore.subsidySummary && grantsStore.subsidySummary.grant_count > 0"
              class="mb-2"
            >
              <div class="text-caption text-medium-emphasis mb-2">
                本年度已申請案件明細：
              </div>
              <v-chip-group column>
                <v-chip
                  v-for="grant in grantsStore.subsidySummary.grants"
                  :key="grant.case_number"
                  size="small"
                  variant="outlined"
                >
                  {{ grant.case_number }}
                  <span class="text-caption ms-1">({{ formatCurrency(grant.subsidy_amount) }})</span>
                </v-chip>
              </v-chip-group>
            </div>

            <!-- 詳細警告 -->
            <div
              v-if="grantsStore.isSubsidyLimitExceeded"
              class="text-body-2 text-warning mt-2"
            >
              <v-icon
                size="small"
                class="me-1"
              >
                mdi-alert
              </v-icon>
              <strong>注意：</strong>本次申請將超過年度補助上限！請調整申請金額或聯繫承辦人員。
            </div>
            <div
              v-else-if="grantsStore.remainingSubsidyAmount < 100000"
              class="text-body-2 text-info mt-2"
            >
              <v-icon
                size="small"
                class="me-1"
              >
                mdi-information
              </v-icon>
              提醒：剩餘額度不足 10 萬元，請注意申請金額規劃。
            </div>
          </div>
        </v-expand-transition>
      </v-alert>

      <!-- 表單提示說明 -->
      <v-card
        flat
        color="blue-grey-lighten-5"
        class="mt-0 mb-0 pa-4 pb-0"
        rounded="lg"
      >
        <v-row class="my-0 py-0">
          <v-col
            cols="12"
            sm="3"
            class="my-0 py-0"
          >
            <v-text-field
              v-model="localFormData.undertracker"
              variant="outlined"
              density="comfortable"
              autocomplete="off"
              bg-color="rgba(255, 255, 255, 1)"
            >
              <template #label>
                案件收件人姓名<span class="required-asterisk">*(必填)</span>
              </template>
            </v-text-field>
          </v-col>

          <v-col
            cols="12"
            sm="3"
            class="my-0 py-0"
          >
            <v-text-field
              v-model="localFormData.tag"
              variant="outlined"
              density="comfortable"
              label="自定義分類標籤（選填）"
              placeholder="輸入標籤"
              clearable
              hide-details
              maxlength="50"
              bg-color="rgba(255, 255, 255, 1)"
            />
          </v-col>

          <v-col
            cols="12"
            sm="6"
            class="my-0 py-0"
          >
            <div class="d-flex">
              <v-icon
                color="blue-grey-darken-1"
                class="me-2"
              >
                mdi-information-outline
              </v-icon>
              <div class="text-caption text-medium-emphasis">
                <strong>操作提示：</strong>
                完成基本資料輸入後，點擊「成立案件」按鈕會自動生成案件編號，並進入後續填寫詳細資料的頁面。
                成立案件後，系統將保留此記錄並可於「補助申請」頁面查詢。
              </div>
            </div>
          </v-col>
        </v-row>

        <!-- 災害案件提醒區塊 -->
        <v-row class="my-0 py-0">
          <v-col
            cols="12"
            class="pt-0"
          >
            <v-card
              flat
              color="orange-lighten-5"
              class="pa-2 border-warning my-0"
              rounded="lg"
            >
              <v-card-title
                class="text-subtitle-1 font-weight-bold pa-0 pb-3"
                style="color: #ef6c00"
              >
                <v-icon
                  color="orange-darken-2"
                  class="me-2 pb-1"
                  size="small"
                >
                  mdi-alert-circle-outline
                </v-icon>
                災害案件提醒
              </v-card-title>

              <v-row dense>
                <v-col
                  cols="12"
                  md="6"
                >
                  <v-radio-group
                    v-model="localFormData.isDisasterCase"
                    inline
                    hide-details
                    color="#ef6c00"
                  >
                    <template #label>
                      <span class="text-subtitle-2 font-weight-medium">
                        本件補助申請案是否為災害案件？
                      </span>
                    </template>
                    <v-radio
                      :value="false"
                      label="否"
                      color="#ef6c00"
                    />
                    <v-radio
                      :value="true"
                      label="是"
                      color="#ef6c00"
                    />
                  </v-radio-group>
                </v-col>

                <v-col
                  v-if="localFormData.isDisasterCase"
                  cols="12"
                  class="pt-0"
                >
                  <v-textarea
                    v-model="localFormData.disasterCaseDescription"
                    variant="outlined"
                    density="comfortable"
                    color="#ef6c00"
                    bg-color="white"
                    rows="3"
                    :rules="disasterDescriptionRules"
                    placeholder="請詳細說明災害情況、災害類型、發生時間等相關資訊..."
                  >
                    <template #label>
                      災害案件說明<span class="required-asterisk">*(必填)</span>
                    </template>
                  </v-textarea>
                </v-col>
              </v-row>
            </v-card>
          </v-col>
        </v-row>
      <!-- </v-card> -->
      </v-card>
      <!-- 表單底部按鈕 -->
      <div class="d-flex justify-end mt-2">
        <v-btn
          class="action-btn"
          color="#3ea0a3"
          variant="outlined"
          rounded="lg"
          :disabled="!isValid"
          size="large"
          append-icon="mdi-chevron-right-circle"
          @click="createProject"
        >
          成立案件
        </v-btn>
      </div>
    </v-form>
  </v-card>
</template>

<script setup lang="ts">
import { useUserStore } from '@/stores/users'
import { useDomicileStore } from '@/stores/domicile'
import { useGrantsStore } from '@/stores/grants'
import type { GrantCreateRequest } from '@/types/grantForms'
import type { VForm } from 'vuetify/components'

const userStore = useUserStore()
const domicileStore = useDomicileStore()
const grantsStore = useGrantsStore()

const emit = defineEmits<{
  'create:case': [data: GrantCreateRequest]
}>();
const localValid = ref(false);
const form = ref<VForm | null>(null);

const localFormData = reactive<GrantCreateRequest>({
  name: '',
  id: '',
  phone: '',
  county: '',
  countyId: null,
  town: '',
  townId: null,
  village: '',
  villageId: null,
  address: '',
  phone2: null,
  undertracker: '',
  office: userStore.currentUser?.office?.name || '',
  officeId: userStore.currentUser?.office?.id || null,
  valid: false,
  isDisasterCase: false, // 預設為否
  disasterCaseDescription: '',
  tag: ''
});

// For the v-select components
const selectedCountyId = ref<{ title: string; value: number } | null>(null)
const selectedTownId = ref<{ title: string; value: number } | null>(null)
const selectedVillageId = ref<{ title: string; value: number } | null>(null)

// 驗證規則
const nameRules = [
  (v: string) => !!v || '請填寫申請人姓名',
  (v: string) => (v && v.length <= 20) || '姓名不可超過20個字'
];

const idRules = [
  (v: string) => !!v || '請填寫身分證字號',
  (v: string) => /^[A-Z][12]\d{8}$/.test(v) || '身分證字號格式不正確'
];

const phoneRules = [
  (v: string) => !!v || '請填寫連絡電話',
  (v: string) => {
    // 手機號碼格式：09 開頭 + 8 碼數字
    const mobilePattern = /^09\d{8}$/
    // 室內電話格式：區碼(2-3碼) + 3-4碼 + 4碼，可有或無連字號
    const landlinePattern = /^(\d{2,3}-?|\(\d{2,3}\))\d{3,4}-?\d{4}$/

    if (mobilePattern.test(v) || landlinePattern.test(v)) {
      return true
    }

    return '請輸入有效的手機號碼或室內電話'
  }
];

const disasterDescriptionRules = [
  (v: string) => {
    if (localFormData.isDisasterCase) {
      return !!v || '災害案件必須填寫說明內容'
    }
    return true
  },
  (v: string) => {
    if (localFormData.isDisasterCase && v) {
      return v.length >= 10 || '災害案件說明至少需要10個字'
    }
    return true
  },
  (v: string) => {
    if (v && v.length > 500) {
      return '災害案件說明不可超過500個字'
    }
    return true
  }
];

// County dropdown items
const countyItems = computed(() => {
  return domicileStore.countyOptions.map(county => ({
    title: county.title,
    value: county.value
  }))
})

// Town dropdown items (filtered by selected county)
const townItems = computed(() => {
  if (!selectedCountyId.value) return []
  return domicileStore.getTownsForCountyId(selectedCountyId.value?.value).map(town => ({
    title: town.title,
    value: town.value
  }))
})

// Village dropdown items (filtered by selected town)
const villageItems = computed(() => {
  if (!selectedTownId.value) return []
  return domicileStore.getVillagesForTownId(selectedTownId.value?.value).map(village => ({
    title: village.title,
    value: village.value
  }))
})


const handleCountyChange = async (county: { title: string; value: number }): Promise<void> => {
  if (!county) return

  // Reset dependent fields
  selectedTownId.value = null
  selectedVillageId.value = null
  localFormData.town = ''
  localFormData.townId = null
  localFormData.village = ''
  localFormData.villageId = null

  // Update form data with selected county
  localFormData.county = county.title
  localFormData.countyId = county.value

  // Load towns for this county
  await domicileStore.loadTownsByCountyId(county.value)
}

// Handle town selection change
const handleTownChange = async (town: { title: string; value: number }) => {
  if (!town) return

  // Reset dependent fields
  selectedVillageId.value = null
  localFormData.village = ''
  localFormData.villageId = null

  // Update form data with selected town
  localFormData.town = town.title
  localFormData.townId = town.value

  // Load villages for this town
  await domicileStore.loadVillagesByTownId(town.value)
}

// Handle village selection change
const handleVillageChange = (village: { title: string; value: number }) => {
  if (!village) return

  // Update form data with selected village
  localFormData.village = village.title
  localFormData.villageId = village.value
}

const isValid = computed(() => {
  return localValid.value;
});

// 表單驗證
const validate = async () => {
  if (!form.value) return false;
  const { valid } = await form.value.validate();
  return valid;
};

// 建立專案
const createProject = async () => {
  const valid = await validate()
  if (!valid) return

  try {
    // 發送事件給父組件 - 直接傳遞完整資料
    emit('create:case', {
      ...localFormData,
      valid: Boolean(localValid.value)
    })

    console.log('📋 [step0.createProject] 開始建立案件，資料:', {
      name: localFormData.name,
      id: localFormData.id,
      county: localFormData.county,
      town: localFormData.town,
      office: localFormData.office
    });

  } catch (error) {
    console.error('❌ [step0.createProject] 建立案件失敗:', error);
    // 可以在這裡添加錯誤提示
    // 例如使用 Vuetify 的 snackbar 或其他通知組件
  }
};

// Initialize form data from user context
onMounted(async () => {
  // Initialize the domicile store
  await domicileStore.initializeStore()

  // Set default values from user store
  // if (userStore.currentUser?.office) {
  //   localFormData.office = userStore.currentUser.office.name || ''
  //   localFormData.officeId = userStore.currentUser.office.id || null
  // }
})

// 僅監聽表單驗證狀態
watch(localValid, (newVal) => {
  localFormData.valid = Boolean(newVal)
})

// 監聽災害案件選項變化
watch(() => localFormData.isDisasterCase, (newVal) => {
  if (!newVal) {
    // 當選擇「否」時，清空災害案件說明
    localFormData.disasterCaseDescription = ''
  }
})

// =============================================================================
// 年度補助額度限制功能
// =============================================================================

/**
 * 補助額度詳情展開狀態
 */
const subsidyDetailsExpanded = ref(false)

/**
 * 取得當前民國年
 */
const getCurrentROCYear = (): number => {
  const westernYear = new Date().getFullYear()
  return westernYear - 1911
}

/**
 * 是否顯示補助額度提示
 * step0 中只需要有效的身份證字號即可
 */
const showSubsidySummary = computed(() => {
  const hasValidId = localFormData.id && /^[A-Z][12]\d{8}$/.test(localFormData.id)
  return !!hasValidId
})

/**
 * 格式化貨幣顯示
 */
const formatCurrency = (amount: number): string => {
  return `NT$ ${amount.toLocaleString('zh-TW')}`
}

/**
 * 剩餘額度顏色樣式
 */
const remainingAmountColorClass = computed(() => {
  const remaining = grantsStore.remainingSubsidyAmount

  if (remaining < 0) {
    return 'text-error'
  } else if (remaining < 100000) {
    return 'text-warning'
  } else {
    return 'text-success'
  }
})

/**
 * Alert 類型
 */
const subsidyAlertType = computed(() => {
  if (grantsStore.isSubsidyLimitExceeded) {
    return 'error'
  } else if (grantsStore.remainingSubsidyAmount < 100000) {
    return 'warning'
  } else {
    return 'info'
  }
})

/**
 * 補助額度圖示
 */
const subsidyIcon = computed(() => {
  if (grantsStore.isSubsidyLimitExceeded) {
    return 'mdi-alert-circle'
  } else if (grantsStore.remainingSubsidyAmount < 100000) {
    return 'mdi-alert'
  } else {
    return 'mdi-cash-check'
  }
})

/**
 * 查詢補助額度摘要
 * step0 使用當前年度，不需要 currentGrantId
 */
const fetchSubsidySummaryIfNeeded = async () => {
  const applicantId = localFormData.id
  const year = getCurrentROCYear()

  console.log('💰 [step0.fetchSubsidySummaryIfNeeded] Data:', {
    applicantId,
    year
  })

  if (!applicantId || !/^[A-Z][12]\d{8}$/.test(applicantId)) {
    console.log('💰 [step0.fetchSubsidySummaryIfNeeded] Invalid applicant ID, skipping')
    return
  }

  console.log('💰 [step0.fetchSubsidySummaryIfNeeded] Calling API...')

  try {
    await grantsStore.fetchSubsidySummary(applicantId, year)
    console.log('✅ [step0.fetchSubsidySummaryIfNeeded] Success')
  } catch (error) {
    console.error('❌ [step0.fetchSubsidySummaryIfNeeded] Error:', error)
  }
}

// 監聽身分證字號變化，自動查詢補助額度
watch(
  () => localFormData.id,
  async (newId, oldId) => {
    console.log('💰 [step0] Watch triggered - ID changed:', {
      newId,
      oldId
    })

    // 當身分證字號符合格式時才查詢
    if (newId && newId !== oldId && /^[A-Z][12]\d{8}$/.test(newId)) {
      console.log('💰 [step0] Valid ID format, fetching subsidy summary')
      await fetchSubsidySummaryIfNeeded()
    } else if (!newId) {
      // 清空身分證字號時，清除補助額度資訊
      grantsStore.clearSubsidySummary()
    }
  }
)
</script>

<style scoped>
.form-container {
  background-color: transparent !important;
}

/* 卡片懸停效果 */
.v-card.pa-4 {
  transition: all 0.3s ease;
}

.v-card.pa-4:hover {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05) !important;
  /* transform: translateY(-2px); */
}

/* 按鈕懸停效果 */
.action-btn {
  font-weight: 500;
  margin: 8px 0 12px 0;
  transition: all 0.2s ease;
  min-width: 120px;
}

.action-btn:hover:not(:disabled) {
  background-color: #3ea0a3 !important;
  color: white !important;
  box-shadow: 0 2px 8px rgba(62, 160, 163, 0.3);
  transform: translateY(-1px);
}

.action-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* 唯讀輸入框樣式 */
:deep(.v-field--disabled .v-field__input) {
  color: rgba(0, 0, 0, 1) !important;
}

/* 必填欄位紅色星號樣式 */
.required-asterisk {
  color: #ff0000 !important;
  font-weight: bold;
  margin-left: 2px;
}

/* 災害案件提醒區塊樣式 */
.border-warning {
  border: 1px solid #ffb74d !important;
}

:deep(.v-radio-group) .v-radio {
  margin-right: 16px;
}

:deep(.v-radio-group) .v-radio .v-selection-control__wrapper {
  margin-inline-end: 8px;
}

/* 災害案件區塊動畫效果 */
.v-card.pa-4.border-warning {
  transition: all 0.3s ease;
}

.v-card.pa-4.border-warning:hover {
  box-shadow: 0 2px 12px rgba(255, 183, 77, 0.2) !important;
}
</style>
