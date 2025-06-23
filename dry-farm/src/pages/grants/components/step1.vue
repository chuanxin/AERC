<template>
  <div
    ref="stepContent"
    class="step-content"
  >
    <v-card
      class="mt-4 pa-0"
      flat
    >
      <v-card-text class="pb-0 pt-0">
        <v-form
          ref="form"
          v-model="localValid"
          @submit.prevent
        >
          <!-- 申請人基本資料區塊 -->
          <v-row>
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

                <!-- 姓名與身分證區塊 -->
                <v-row dense>
                  <v-col
                    cols="12"
                    md="6"
                  >
                    <v-text-field
                      v-model="localFormData.name"
                      variant="outlined"
                      density="comfortable"
                      :rules="nameRules"
                      color="#3ea0a3"
                      bg-color="white"
                    >
                      <template #label>
                        申請人
                      </template>
                    </v-text-field>
                  </v-col>
                  <v-col
                    cols="12"
                    md="6"
                  >
                    <v-text-field
                      v-model="localFormData.id"
                      label="身分證字號"
                      variant="outlined"
                      density="comfortable"
                      :rules="idRules"
                      color="#3ea0a3"
                      bg-color="white"
                    >
                      <template #label>
                        身分證字號
                      </template>
                    </v-text-field>
                  </v-col>
                </v-row>

                <!-- 聯絡資訊區塊 -->
                <v-row dense>
                  <v-col cols="12">
                    <v-text-field
                      v-model="localFormData.phone"
                      placeholder="請輸入手機號碼"
                      variant="outlined"
                      density="comfortable"
                      :rules="phoneRules"
                      color="#3ea0a3"
                      bg-color="white"
                    >
                      <template #label>
                        連絡電話
                      </template>
                    </v-text-field>
                  </v-col>
                </v-row>
              </v-card>
            </v-col>

            <!-- 地址資訊區塊 -->
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

                <div class="d-flex align-center mb-2 justify-space-between">
                  <div class="d-flex align-center">
                    <v-btn
                      v-if="!isEditingAddress"
                      variant="text"
                      density="comfortable"
                      size="small"
                      color="#3ea0a3"
                      rounded="sm"
                      @click="isEditingAddress = true"
                    >
                      <v-icon>mdi-pencil</v-icon>
                      編輯地址
                    </v-btn>
                    <v-btn
                      v-else
                      variant="text"
                      density="comfortable"
                      size="small"
                      color="success"
                      rounded="circle"
                      @click="finishEditingAddress"
                    >
                      <v-icon>mdi-check</v-icon>
                      完成編輯
                    </v-btn>
                  </div>
                </div>

                <!-- Read-only address display -->
                <div
                  v-if="!isEditingAddress"
                  class="pa-2"
                >
                  <div class="d-flex flex-column">
                    <span class="text-subtitle-1 mb-2">{{ getFullAddress }}</span>
                    <span class="text-caption text-grey">點擊編輯按鈕以修改地址</span>
                  </div>
                </div>

                <!-- Editable address controls -->
                <div v-else>
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
                        :loading="domicileStore.isLoading"
                        :rules="[v => !!v || '請選擇縣市']"
                        return-object
                        color="#3ea0a3"
                        bg-color="white"
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
                        :loading="domicileStore.isLoading"
                        :rules="[v => !!v || '請選擇鄉鎮市區']"
                        :disabled="!selectedCountyId"
                        return-object
                        color="#3ea0a3"
                        bg-color="white"
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
                        :loading="domicileStore.isLoading"
                        :rules="[v => !!v || '請選擇村里']"
                        :disabled="!selectedTownId"
                        return-object
                        color="#3ea0a3"
                        bg-color="white"
                        @update:model-value="handleVillageChange"
                      >
                        <template #label>
                          村里
                        </template>
                      </v-select>
                    </v-col>
                  </v-row>
                  <v-row dense>
                    <v-col cols="12">
                      <v-text-field
                        v-model="localFormData.address"
                        placeholder="請輸入門牌號碼及其他地址資訊"
                        variant="outlined"
                        density="comfortable"
                        :rules="[v => !!v || '請輸入詳細地址']"
                        color="#3ea0a3"
                        bg-color="white"
                      >
                        <template #label>
                          詳細地址
                        </template>
                      </v-text-field>
                    </v-col>
                  </v-row>
                </div>
              </v-card>
            </v-col>
          </v-row>

          <!-- 承辦資訊區塊 -->
          <v-card
            flat
            class="mb-4 pa-4"
            color="blue-grey-lighten-5"
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
                mdi-account-tie
              </v-icon>
              <span class="required-asterisk">*</span>承辦資訊
            </v-card-title>

            <v-row>
              <v-col
                cols="12"
                md="6"
              >
                <v-text-field
                  v-model="localFormData.undertracker"
                  variant="outlined"
                  density="comfortable"
                  :rules="[v => !!v || '請輸入承辦人']"
                  color="#3ea0a3"
                  bg-color="white"
                >
                  <template #label>
                    收件人
                  </template>
                </v-text-field>
              </v-col>
              <v-col
                cols="12"
                md="6"
              >
                <v-text-field
                  v-model="localFormData.office"
                  label="管理處"
                  variant="outlined"
                  density="comfortable"
                  disabled
                  bg-color="white"
                  color="#3ea0a3"
                />
              </v-col>
            </v-row>
          </v-card>

          <!-- 系統資訊區塊 -->
          <v-card
            v-if="localFormData.caseNumber"
            flat
            class="mb-4 pa-4"
            color="blue-grey-lighten-5"
            rounded="lg"
          >
            <v-card-title
              class="text-subtitle-1 font-weight-bold pa-0 pb-6"
              style="color: #2d8c8f"
            >
              <v-icon
                class="me-2 pb-1"
                size="small"
                color="#3ea0a3"
              >
                mdi-information
              </v-icon>
              案件資訊
            </v-card-title>

            <v-row>
              <!-- 左半邊：災害案件資訊 -->
              <v-col
                cols="12"
                md="6"
              >
                <v-card
                  flat
                  :color="localFormData.isDisasterCase ? 'orange-lighten-5' : 'grey-lighten-4'"
                  class="pa-4"
                  :class="localFormData.isDisasterCase ? 'border-warning' : 'border-grey'"
                  rounded="lg"
                  elevation="0"
                >
                  <div class="d-flex align-center justify-space-between mb-3">
                    <v-card-title
                      class="text-subtitle-1 font-weight-bold pa-0"
                      :style="localFormData.isDisasterCase ? 'color: #ef6c00' : 'color: #666'"
                    >
                      <v-icon
                        :color="localFormData.isDisasterCase ? 'orange-darken-2' : 'grey-darken-1'"
                        class="me-2 pb-1"
                        size="small"
                      >
                        {{ localFormData.isDisasterCase ? 'mdi-alert-circle-outline' : 'mdi-shield-check' }}
                      </v-icon>
                      災害案件資訊
                    </v-card-title>
                    <v-btn
                      v-if="!isEditingDisasterInfo"
                      variant="text"
                      density="comfortable"
                      size="small"
                      :color="localFormData.isDisasterCase ? '#ef6c00' : '#666'"
                      rounded="sm"
                      @click="isEditingDisasterInfo = true"
                    >
                      <v-icon>mdi-pencil</v-icon>
                      編輯
                    </v-btn>
                    <v-btn
                      v-else
                      variant="text"
                      density="comfortable"
                      size="small"
                      color="success"
                      rounded="sm"
                      @click="finishEditingDisasterInfo"
                    >
                      <v-icon>mdi-check</v-icon>
                      完成
                    </v-btn>
                  </div>

                  <!-- 顯示模式 -->
                  <div v-if="!isEditingDisasterInfo">
                    <div class="d-flex flex-column">
                      <div class="d-flex align-center mb-2">
                        <span class="text-subtitle-2">災害案件：</span>
                        <v-checkbox
                          v-model="localFormData.isDisasterCase"
                          :color="localFormData.isDisasterCase ? '#ef6c00' : '#666'"
                          :label="localFormData.isDisasterCase ? '是' : '否'"
                          disabled
                          hide-details
                          ensity="compact"
                        />
                      </div>
                      <div
                        v-if="localFormData.isDisasterCase && localFormData.disasterCaseDescription"
                        class="mt-2"
                      >
                        <span class="text-subtitle-2 text-grey-darken-1">災害說明：</span>
                        <div class="mt-1 pa-3 bg-white rounded border">
                          <span class="text-body-2">{{ localFormData.disasterCaseDescription }}</span>
                        </div>
                      </div>
                      <div
                        v-if="!localFormData.isDisasterCase"
                        class="text-center text-grey-darken-1 mt-2"
                      >
                        <div class="text-caption">
                          此案件非災害相關案件
                        </div>
                      </div>
                    </div>
                  </div>

                  <!-- 編輯模式 -->
                  <div v-else>
                    <v-row dense>
                      <v-col cols="12">
                        <v-radio-group
                          v-model="localFormData.isDisasterCase"
                          inline
                          hide-details
                          :color="localFormData.isDisasterCase ? '#ef6c00' : '#666'"
                        >
                          <template #label>
                            <span class="text-subtitle-2 font-weight-medium">
                              本件補助申請案是否為災害案件？
                            </span>
                          </template>
                          <v-radio
                            :value="false"
                            label="否"
                            :color="localFormData.isDisasterCase ? '#ef6c00' : '#666'"
                          />
                          <v-radio
                            :value="true"
                            label="是"
                            :color="localFormData.isDisasterCase ? '#ef6c00' : '#666'"
                          />
                        </v-radio-group>
                      </v-col>
                      <v-col
                        v-if="localFormData.isDisasterCase"
                        cols="12"
                        class="pt-2"
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
                  </div>
                </v-card>
              </v-col>

              <!-- 右半邊：案件編號和收件日期垂直排列 -->
              <v-col
                cols="12"
                md="6"
              >
                <v-row dense>
                  <v-col cols="12">
                    <v-text-field
                      v-model="localFormData.caseNumber"
                      label="案件編號"
                      variant="outlined"
                      density="comfortable"
                      disabled
                      bg-color="white"
                      color="#3ea0a3"
                    />
                  </v-col>
                  <v-col cols="12">
                    <v-text-field
                      v-model="localFormData.receivedDate"
                      label="收件日期"
                      disabled
                      variant="outlined"
                      density="comfortable"
                      bg-color="white"
                      color="#3ea0a3"
                    />
                  </v-col>
                </v-row>
              </v-col>
            </v-row>
          </v-card>
        </v-form>
      </v-card-text>
    </v-card>
  </div>
</template>

<script setup lang="ts">
import { useRoute } from 'vue-router';
import { useUserStore } from '@/stores/users';
import { useDomicileStore } from '@/stores/domicile';
import { useGrantsStore } from '@/stores/grants';
import type { Step1Data } from '@/types/grantForms'

// const props = defineProps({
//   currentStep: {
//     type: Number,
//     required: true
//   }
// });

const emit = defineEmits(['step-data-changed', 'validation-changed', 'ready-to-proceed', 'go-back-requested']);
const localValid = ref(true);
const form = ref<{ validate: () => Promise<{ valid: boolean }> } | null>(null);

const userStore = useUserStore();
const domicileStore = useDomicileStore();
const grantsStore = useGrantsStore();

// 🆕 初始化狀態管理
const isInitialized = ref(false);
const isInitializing = ref(false);

// For the v-select components
const selectedCountyId = ref<{ title: string; value: number } | null>(null);
const selectedTownId = ref<{ title: string; value: number } | null>(null);
const selectedVillageId = ref<{ title: string; value: number } | null>(null);

const createInitialFormData = (overrideData?: Partial<Step1Data>): Step1Data => {
  const baseData: Step1Data = {
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
    office: userStore.currentUser?.office?.name ?? '',
    officeId: userStore.currentUser?.office?.id ?? null,
    caseNumber: '',
    receivedDate: '',
    receivedTime: '',
    valid: false,
    isDisasterCase: false,
    disasterCaseDescription: ''
  };

  // 支援覆蓋資料的合併
  return overrideData ? { ...baseData, ...overrideData } : baseData;
};

// 統一的重置方法
const resetFormData = () => {
  console.log('🔄 step1.vue: Resetting form data to initial state');

  // 使用標準化的初始資料重置
  const initialData = createInitialFormData();
  Object.assign(localFormData, initialData);

  // 重置地址選擇器
  selectedCountyId.value = null;
  selectedTownId.value = null;
  selectedVillageId.value = null;

  // 重置編輯狀態
  isEditingAddress.value = false;
  isEditingDisasterInfo.value = false;
};

// 🆕 標準化的資料載入方法 (方案一：專用載入方法)
const loadFormData = (stepData: Partial<Step1Data>) => {
  console.log('📥 step1.vue: Loading form data with merge strategy');
  console.log('📊 step1.vue: Incoming data keys:', Object.keys(stepData));

  // ✨ 利用升級後的 createInitialFormData 進行型別安全的合併
  const mergedData = createInitialFormData(stepData);
  Object.assign(localFormData, mergedData);

  console.log('✅ step1.vue: Form data loaded successfully');
  console.log('📊 step1.vue: Final form data sample:', {
    name: localFormData.name,
    caseNumber: localFormData.caseNumber,
    county: localFormData.county,
    office: localFormData.office
  });
};

// 🆕 更簡潔的載入方法 (方案二：直接使用 createInitialFormData)
// const loadFormDataDirect = (stepData: Partial<Step1Data>) => {
//   console.log('📥 step1.vue: Direct loading with createInitialFormData');
//   Object.assign(localFormData, createInitialFormData(stepData));
// };

const localFormData = reactive<Step1Data>(createInitialFormData());

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

// Add a state to control address editing
const isEditingAddress = ref(false);

// Add a state to control disaster case info editing
const isEditingDisasterInfo = ref(false);

// Computed property to display the full address
const getFullAddress = computed(() => {
  let address = '';
  if (localFormData.county) address += localFormData.county;
  if (localFormData.town) address += localFormData.town;
  if (localFormData.village) address += localFormData.village;
  if (localFormData.address) address += localFormData.address;

  return address || '尚未填寫地址';
});

// Method to finish editing and validate address
const finishEditingAddress = () => {
  // Check if the address is valid before closing edit mode
  const hasRequiredFields = !!selectedCountyId.value &&
                           !!selectedTownId.value &&
                           !!selectedVillageId.value &&
                           !!localFormData.address;

  if (hasRequiredFields) {
    isEditingAddress.value = false;
    // updateFormData();
  } else {
    // Show error or keep edit mode open
    alert('請填寫完整地址資訊');
  }
};

// Method to finish editing disaster case info
const finishEditingDisasterInfo = () => {
  // Validate disaster case info if it's marked as disaster case
  if (localFormData.isDisasterCase) {
    if (!localFormData.disasterCaseDescription || localFormData.disasterCaseDescription.trim().length < 10) {
      alert('災害案件必須填寫說明內容，且至少需要10個字');
      return;
    }
    if (localFormData.disasterCaseDescription.trim().length > 500) {
      alert('災害案件說明不可超過500個字');
      return;
    }
  }

  isEditingDisasterInfo.value = false;
  // Trigger form data change event
  emitDataChanged();
};

// County dropdown items
const countyItems = computed(() => {
  return domicileStore.countyOptions.map(county => ({
    title: county.title,
    value: county.value
  }));
});

// Town dropdown items (filtered by selected county)
const townItems = computed(() => {
  if (!selectedCountyId.value) return [];
  return domicileStore.getTownsForCountyId(selectedCountyId.value?.value).map(town => ({
    title: town.title,
    value: town.value
  }));
});

// Village dropdown items (filtered by selected town)
const villageItems = computed(() => {
  if (!selectedTownId.value) return [];
  return domicileStore.getVillagesForTownId(selectedTownId.value?.value).map(village => ({
    title: village.title,
    value: village.value
  }));
});

// Handle county selection change
const handleCountyChange = async (county: { title: string; value: number }) => {
  if (!county) return;

  // Reset dependent fields
  selectedTownId.value = null;
  selectedVillageId.value = null;
  localFormData.town = '';
  localFormData.townId = null;
  localFormData.village = '';
  localFormData.villageId = null;

  // Update form data with selected county
  localFormData.county = county.title;
  localFormData.countyId = county.value;

  // Load towns for this county
  await domicileStore.loadTownsByCountyId(county.value);
  // emitDataChanged 會由 watch 自動觸發
};

// Handle town selection change
const handleTownChange = async (town: { title: string; value: number }) => {
  if (!town) return;

  // Reset dependent fields
  selectedVillageId.value = null;
  localFormData.village = '';
  localFormData.villageId = null;

  // Update form data with selected town
  localFormData.town = town.title;
  localFormData.townId = town.value;

  // Load villages for this town
  await domicileStore.loadVillagesByTownId(town.value);
  // emitDataChanged 會由 watch 自動觸發
};

// Handle village selection change
const handleVillageChange = (village: { title: string; value: number }) => {
  if (!village) return;

  // Update form data with selected village
  localFormData.village = village.title;
  localFormData.villageId = village.value;
  // emitDataChanged 會由 watch 自動觸發
};

// 事件驅動：向父組件發送資料變更事件
const emitDataChanged = () => {
  console.log('📤 step1.vue: Emitting step-data-changed event');
  emit('step-data-changed', {
    step: 1,
    data: { ...localFormData },
    valid: localValid.value
  });
};

// 發送驗證狀態變更事件
const emitValidationChanged = (isValid: boolean) => {
  console.log('📋 step1.vue: Emitting validation-changed event:', isValid);
  emit('validation-changed', {
    step: 1,
    valid: isValid
  });
};

// 發送準備進入下一步事件
const emitReadyToProceed = () => {
  console.log('✅ step1.vue: Emitting ready-to-proceed event');
  emit('ready-to-proceed', {
    step: 1,
    data: { ...localFormData }
  });
};

// Validate and emit validated event
// const validate = async () => {
//   if (!form.value) return { valid: false };

//   const { valid } = await form.value.validate();

//   if (valid) {
//     updateFormData();
//   }

//   return { valid };
// };

// Initialize address dropdowns based on string values from the store
const initializeAddressDropdowns = async () => {
  try {
    // First ensure counties are loaded
    if (domicileStore.counties.length === 0) {
      await domicileStore.loadCounties();
    }      // Ensure countyOptions exists before using find()
      if (!domicileStore.countyOptions || !Array.isArray(domicileStore.countyOptions)) {
        console.warn('County options not available yet, using direct county string');
        // Fallback: Create a temporary county option
        if (localFormData.county) {
          selectedCountyId.value = {
            title: localFormData.county,
            value: localFormData.countyId || 0
          };
          return; // Exit early since we can't proceed with cascading data
        }
        return;
      }

      // Find county by name
      const county = domicileStore.countyOptions.find(c => c.title === localFormData.county);
      if (county) {
        selectedCountyId.value = county;
        localFormData.countyId = county.value;

        // Load towns for this county
        await domicileStore.loadTownsByCountyId(county.value);

        // Get towns for this county from the map
        const countyTowns = domicileStore.townsByCountyId.get(county.value) || [];
        if (countyTowns.length === 0) {
          console.warn('Towns not available yet for county:', county.title);
          return;
        }

        // Find town by name
        const town = countyTowns.find(t => t.name === localFormData.town);
        if (town) {
          selectedTownId.value = {
            title: town.name,
            value: town.id
          };
          localFormData.townId = town.id;

          // Load villages for this town
          await domicileStore.loadVillagesByTownId(town.id);

          // Get villages for this town from the map
          const townVillages = domicileStore.villagesByTownId.get(town.id) || [];
          if (townVillages.length === 0) {
            console.warn('Villages not available yet for town:', town.name);
            return;
          }

          // Find village by name
          const village = townVillages.find(v => v.name === localFormData.village);
          if (village) {
            selectedVillageId.value = {
              title: village.name,
              value: village.id
            };
            localFormData.villageId = village.id;
          }
        }
      }
    } catch (error) {
      console.error('Error initializing address dropdowns:', error);
    }
};

// 🆕 檢查資料是否已準備好
// const isDataReady = computed(() => {
//   const stepData = grantsStore.formData[1];
//   return stepData && Object.keys(stepData).length > 0;
// });

// 🆕 初始化數據 - 自主載入模式
const initializeFormData = async (forceReload = false) => {
  // 防止重複初始化
  if (isInitializing.value) {
    console.log('⏳ step1.vue: Already initializing, skipping...');
    return;
  }

  // 如果已經初始化且非強制重載，跳過
  if (isInitialized.value && !forceReload) {
    console.log('✅ step1.vue: Already initialized, skipping...');
    return;
  }

  // 🆕 強制重載時重置狀態
  if (forceReload) {
    console.log('🔄 step1.vue: Force reload triggered');
    resetFormData();
  }

  isInitializing.value = true;
  console.log('🔄 step1.vue: Initializing form data with autonomous loading');

  try {
    // 🆕 自主載入：直接從路由獲取案件ID並載入資料
    const route = useRoute();
    const caseNumber = route.query.id as string;

    if (!caseNumber) {
      console.error('❌ step1.vue: No case number in route query');
      return;
    }

    console.log('📥 step1.vue: Loading step 1 data autonomously for case:', caseNumber);

    // 檢查是否已有快取資料，並確認案件編號匹配
    const existingData = grantsStore.formData[1];
    const hasValidData = existingData && Object.keys(existingData).length > 0 &&
                        (existingData.name || existingData.id || existingData.phone || existingData.county);

    // 檢查快取資料是否屬於當前案件
    const isSameCaseNumber = existingData &&
                            existingData.caseNumber &&
                            existingData.caseNumber === caseNumber;

    console.log('🔍 step1.vue: Cache validation:', {
      hasValidData,
      isSameCaseNumber,
      cachedCaseNumber: existingData?.caseNumber,
      currentCaseNumber: caseNumber
    });

    if (!hasValidData || !isSameCaseNumber) {
      if (!hasValidData) {
        console.log('🔄 step1.vue: No valid cached data, loading fresh data from server');
      } else {
        console.log('🔄 step1.vue: Case number mismatch, loading fresh data from server');
        console.log(`   Previous case: ${existingData?.caseNumber}, Current case: ${caseNumber}`);
      }
      await grantsStore.loadStepData(caseNumber, 1);
    } else {
      console.log('📋 step1.vue: Using existing cached data for same case');
    }

    // 取得載入後的資料
    const stepData = grantsStore.formData[1];

    if (stepData && Object.keys(stepData).length > 0) {
      console.log('📊 step1.vue: Step data loaded successfully');

      // ✨ 使用標準化載入方法替換原有合併邏輯
      // 方案一：使用專用載入方法（推薦用於複雜邏輯）
      loadFormData(stepData);

      // 方案二：直接使用 createInitialFormData（推薦用於簡單載入）
      // Object.assign(localFormData, createInitialFormData(stepData));

      // 初始化地址下拉選單系統
      await domicileStore.initializeStore();

      // 智能地址處理
      await handleSmartAddressInitialization();

      // 標記為已初始化
      isInitialized.value = true;

      console.log('✅ step1.vue: Autonomous initialization complete');

      // 發送資料到父組件
      emitDataChanged();
      emitValidationChanged(localValid.value);
    } else {
      console.warn('⚠️ step1.vue: No data available after loading');
    }

  } catch (error) {
    console.error('❌ step1.vue: Error in autonomous initializeFormData:', error);
    // 即使出錯也要初始化基本設置
    await domicileStore.initializeStore();
    if (!localFormData.office) {
      localFormData.office = userStore.currentUser?.office?.name ?? '';
    }
  } finally {
    isInitializing.value = false;
  }
};

// 🆕 智能地址初始化處理
const handleSmartAddressInitialization = async () => {
  console.log('🏠 step1.vue: Handling smart address initialization');

  // 情況1：有 countyId，使用正常流程
  if (localFormData.countyId && domicileStore.counties.length > 0) {
    console.log('📍 step1.vue: Using existing countyId:', localFormData.countyId);

    const countyObj = domicileStore.counties.find(c => c.id === localFormData.countyId);
    if (countyObj) {
      selectedCountyId.value = {
        title: countyObj.name,
        value: countyObj.id
      };

      await domicileStore.loadTownsByCountyId(countyObj.id);

      if (localFormData.townId) {
        const townObj = domicileStore.towns.find(t => t.id === localFormData.townId);
        if (townObj) {
          selectedTownId.value = {
            title: townObj.name,
            value: townObj.id
          };

          await domicileStore.loadVillagesByTownId(townObj.id);

          if (localFormData.villageId) {
            const villageObj = domicileStore.villages.find(v => v.id === localFormData.villageId);
            if (villageObj) {
              selectedVillageId.value = {
                title: villageObj.name,
                value: villageObj.id
              };
            }
          }
        }
      }
    }
  }
  // 情況2：沒有 countyId 但有 county 字串，嘗試解析
  else if (localFormData.county && !localFormData.countyId && domicileStore.counties.length > 0) {
    console.log('🔍 step1.vue: Attempting to resolve county by name:', localFormData.county);

    const countyObj = domicileStore.counties.find(c => c.name === localFormData.county);
    if (countyObj) {
      console.log('✅ step1.vue: Found county match:', countyObj);

      // 更新 localFormData 的 countyId
      localFormData.countyId = countyObj.id;

      selectedCountyId.value = {
        title: countyObj.name,
        value: countyObj.id
      };

      // 載入鄉鎮資料
      await domicileStore.loadTownsByCountyId(countyObj.id);

      // 如果有 town 字串但沒有 townId，嘗試解析
      if (localFormData.town && !localFormData.townId) {
        console.log('🔍 step1.vue: Attempting to resolve town by name:', localFormData.town);

        const townObj = domicileStore.towns.find(t => t.name === localFormData.town);
        if (townObj) {
          console.log('✅ step1.vue: Found town match:', townObj);

          localFormData.townId = townObj.id;
          selectedTownId.value = {
            title: townObj.name,
            value: townObj.id
          };

          // 載入村里資料
          await domicileStore.loadVillagesByTownId(townObj.id);

          // 如果有 village 字串但沒有 villageId，嘗試解析
          if (localFormData.village && !localFormData.villageId) {
            console.log('🔍 step1.vue: Attempting to resolve village by name:', localFormData.village);

            const villageObj = domicileStore.villages.find(v => v.name === localFormData.village);
            if (villageObj) {
              console.log('✅ step1.vue: Found village match:', villageObj);

              localFormData.villageId = villageObj.id;
              selectedVillageId.value = {
                title: villageObj.name,
                value: villageObj.id
              };
            } else {
              console.warn('⚠️ step1.vue: Could not resolve village:', localFormData.village);
            }
          }
        } else {
          console.warn('⚠️ step1.vue: Could not resolve town:', localFormData.town);
        }
      }
    } else {
      console.warn('⚠️ step1.vue: Could not resolve county:', localFormData.county);
      // 如果無法解析，使用原有的 initializeAddressDropdowns 方法
      await initializeAddressDropdowns();
    }
  }
  // 情況3：完全沒有地址資料，不需要處理
  else {
    console.log('ℹ️ step1.vue: No address data to initialize');
  }
};

// 🆕 自主載入模式：在組件掛載時直接載入資料
// 優點：
// 1. 解決父子組件時序問題 - 不再依賴父組件的 loadStepData
// 2. 組件職責更明確 - step1.vue 完全負責自己的資料載入
// 3. 避免 watch 失效問題 - 直接在 onMounted 中載入，不依賴響應式變化
// 4. 更容易調試 - 資料載入流程在單一組件內完成
onMounted(async () => {
  console.log('🏗️ step1.vue: Component mounted, starting autonomous data loading');
  await initializeFormData();
});

// 🆕 監聽路由參數變化，處理案件切換
const route = useRoute();
watch(
  () => route.query.id,
  async (newCaseNumber, oldCaseNumber) => {
    if (newCaseNumber && newCaseNumber !== oldCaseNumber) {
      console.log('🔄 step1.vue: Case number changed in route', {
        from: oldCaseNumber,
        to: newCaseNumber
      });

      // 重置初始化狀態，強制重新載入
      isInitialized.value = false;
      await initializeFormData(true); // forceReload = true
    }
  }
);

// 監聽本地表單資料變化 - 事件驅動設計
watch(localFormData, () => {
  // 只有在已初始化的情況下才發送事件，避免初始化過程中的無效事件
  if (isInitialized.value) {
    console.log('📤 step1.vue: localFormData changed, emitting events');
    emitDataChanged();
  }
}, { deep: true });

// 監聽驗證狀態變化
watch(localValid, (newVal) => {
  console.log('📋 step1.vue: Validation status changed:', newVal);
  emitValidationChanged(newVal);
});

// 監聽災害案件狀態變化
watch(() => localFormData.isDisasterCase, (newVal) => {
  if (!newVal) {
    // 當選擇「否」時，清空災害案件說明
    localFormData.disasterCaseDescription = '';
  }
  // 觸發資料變更事件
  if (isInitialized.value) {
    emitDataChanged();
  }
});

// 提供給父組件調用的方法：觸發進入下一步
const handleProceedToNext = async () => {
  console.log('🔄 step1.vue: handleProceedToNext called');

  // 執行表單驗證
  if (form.value) {
    const { valid } = await form.value.validate();
    if (valid) {
      emitReadyToProceed();
    } else {
      console.warn('⚠️ step1.vue: Form validation failed, cannot proceed');
    }
  }
};

// 提供給父組件調用的方法：返回上一步
const handleGoBack = () => {
  console.log('🔄 step1.vue: handleGoBack called');
  emit('go-back-requested');
};

// 暴露方法給父組件使用
defineExpose({
  handleProceedToNext,
  handleGoBack
});
</script>

<style scoped>
.step-content {
  padding: 0;
  background-color: transparent !important;
}

/* 卡片懸停效果 */
.v-card.pa-4 {
  transition: all 0.3s ease;
}

.v-card.pa-4:hover {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05) !important;
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

/* 災害案件區塊樣式 */
.border-grey {
  border: 1px solid #bdbdbd !important;
}

/* 災害案件區塊動畫效果 */
.v-card.pa-4.border-warning {
  transition: all 0.3s ease;
}

.v-card.pa-4.border-warning:hover {
  box-shadow: 0 2px 12px rgba(255, 183, 77, 0.2) !important;
}

.v-card.pa-4.border-grey {
  transition: all 0.3s ease;
}

.v-card.pa-4.border-grey:hover {
  box-shadow: 0 2px 8px rgba(189, 189, 189, 0.15) !important;
}

:deep(.v-radio-group) .v-radio {
  margin-right: 16px;
}

:deep(.v-radio-group) .v-radio .v-selection-control__wrapper {
  margin-inline-end: 8px;
}
</style>
