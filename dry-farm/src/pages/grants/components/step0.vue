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
                  :rules="nameRules"
                  bg-color="white"
                  required
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
                  :rules="idRules"
                  bg-color="white"
                  required
                  hint="例：A123456789"
                  persistent-hint
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

      <!-- 表單提示說明 -->
      <v-card
        flat
        color="blue-grey-lighten-5"
        class="mt-0 mb-0 pa-4 pb-0"
        rounded="lg"
      >
        <v-row>
          <v-col
            cols="12"
            sm="3"
          >
            <v-text-field
              v-model="localFormData.undertracker"
              variant="outlined"
              density="comfortable"
              bg-color="rgba(255, 255, 255, 1)"
            >
              <template #label>
                承辦人姓名<span class="required-asterisk">*(必填)</span>
              </template>
            </v-text-field>
          </v-col>

          <v-col
            cols="12"
            sm="9"
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
import type { GrantCreateRequest } from '@/types/grantForms'
import type { VForm } from 'vuetify/components'

const userStore = useUserStore()
const domicileStore = useDomicileStore()

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
  undertracker: '',
  office: userStore.currentUser?.office?.name || '',
  officeId: userStore.currentUser?.office?.id || null,
  valid: false
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
  (v: string) => /^09\d{8}$/.test(v) || '手機號碼格式不正確'
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
</style>
