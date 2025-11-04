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
        <!-- 🆕 唯讀模式提示 -->
        <v-alert
          v-if="props.readonly"
          type="warning"
          variant="tonal"
          density="compact"
          class="mb-4"
          rounded="lg"
        >
          <div class="d-flex align-center">
            <span class="text-body-2">已完成現場勘查，此步驟已鎖定，無法編輯。</span>
          </div>
        </v-alert>

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
                      :readonly="props.readonly"
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
                      :readonly="props.readonly"
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
                      :readonly="props.readonly"
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
                <div class="d-flex align-center justify-space-between mb-6">
                  <v-card-title
                    class="text-subtitle-1 font-weight-bold pa-0"
                    style="color: #2d8c8f"
                  >
                    <v-icon
                      color="#3ea0a3"
                      class="me-2 pb-1"
                      size="small"
                    >
                      mdi-map-marker
                    </v-icon>
                    <span class="required-asterisk">*</span>
                    申請人通訊地址
                  </v-card-title>
                  <v-btn
                    v-if="!isEditingAddress"
                    variant="text"
                    density="comfortable"
                    size="small"
                    color="#3ea0a3"
                    rounded="sm"
                    :disabled="props.readonly"
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

                <!-- Read-only address display -->
                <div
                  v-if="!isEditingAddress"
                  class="pa-2 pt-0"
                >
                  <div class="d-flex flex-column">
                    <span class="text-subtitle-1 mb-2">{{ getFullAddress }}</span>
                    <span
                      v-if="!props.readonly"
                      class="text-caption text-grey"
                    >點擊編輯按鈕以修改地址</span>
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
                        :disabled="props.readonly"
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
                        :disabled="!selectedCountyId || props.readonly"
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
                        :disabled="!selectedTownId || props.readonly"
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
                        :readonly="props.readonly"
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

          <!-- 年度補助額度簡要提示 -->
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
                  :readonly="props.readonly"
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
                      v-if="!isEditingDisasterInfo && !props.readonly"
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
                      v-else-if="!props.readonly"
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
                          :disabled="props.readonly"
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
                          :readonly="props.readonly"
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

              <!-- 右半邊：案件編號和建檔日期垂直排列 -->
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
                      label="建檔日期"
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

// 🆕 Props 定義
interface Step1Props {
  currentStep: number;
  readonly?: boolean;
}

const props = withDefaults(defineProps<Step1Props>(), {
  readonly: false
})

interface Step1Events {
  'step-data-changed': [eventData: { step: number; data: Record<string, unknown>; valid: boolean }];
  'validation-changed': [eventData: { step: number; valid: boolean }];
  'ready-to-proceed': [eventData: { step: number; data: Record<string, unknown> }];
  'go-back-requested': [eventData: { step: number }];
}

const emit = defineEmits<Step1Events>();
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

// 💰 補助額度詳情展開狀態
const subsidyDetailsExpanded = ref(false);

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

// =============================================================================
// 地址初始化 - 統一架構（Linus式扁平化設計）
// =============================================================================

/**
 * 確保縣市 ID 存在
 * - 如果有 countyId，直接使用
 * - 如果只有 county 字串，從 store 解析 ID
 */
const ensureCountyId = async () => {
  if (!localFormData.county) return false;

  // 如果已有 ID，驗證並設置下拉選項
  if (localFormData.countyId) {
    const countyObj = domicileStore.counties.find(c => c.id === localFormData.countyId);
    if (countyObj) {
      selectedCountyId.value = { title: countyObj.name, value: countyObj.id };
      return true;
    }
  }

  // 只有 name，需要解析 ID
  const countyObj = domicileStore.counties.find(c => c.name === localFormData.county);
  if (countyObj) {
    localFormData.countyId = countyObj.id;
    selectedCountyId.value = { title: countyObj.name, value: countyObj.id };
    return true;
  }

  console.warn('⚠️ step1: Could not resolve county:', localFormData.county);
  return false;
};

/**
 * 確保鄉鎮 ID 存在
 */
const ensureTownId = async () => {
  if (!localFormData.town || !localFormData.countyId) return false;

  // 載入鄉鎮資料
  await domicileStore.loadTownsByCountyId(localFormData.countyId);

  // 如果已有 ID，驗證並設置下拉選項
  if (localFormData.townId) {
    const townObj = domicileStore.towns.find(t => t.id === localFormData.townId);
    if (townObj) {
      selectedTownId.value = { title: townObj.name, value: townObj.id };
      return true;
    }
  }

  // 只有 name，需要解析 ID
  const townObj = domicileStore.towns.find(t => t.name === localFormData.town);
  if (townObj) {
    localFormData.townId = townObj.id;
    selectedTownId.value = { title: townObj.name, value: townObj.id };
    return true;
  }

  console.warn('⚠️ step1: Could not resolve town:', localFormData.town);
  return false;
};

/**
 * 確保村里 ID 存在
 */
const ensureVillageId = async () => {
  if (!localFormData.village || !localFormData.townId) return false;

  // 載入村里資料
  await domicileStore.loadVillagesByTownId(localFormData.townId);

  // 如果已有 ID，驗證並設置下拉選項
  if (localFormData.villageId) {
    const villageObj = domicileStore.villages.find(v => v.id === localFormData.villageId);
    if (villageObj) {
      selectedVillageId.value = { title: villageObj.name, value: villageObj.id };
      return true;
    }
  }

  // 只有 name，需要解析 ID
  const villageObj = domicileStore.villages.find(v => v.name === localFormData.village);
  if (villageObj) {
    localFormData.villageId = villageObj.id;
    selectedVillageId.value = { title: villageObj.name, value: villageObj.id };
    return true;
  }

  console.warn('⚠️ step1: Could not resolve village:', localFormData.village);
  return false;
};

/**
 * 統一的地址初始化入口
 * 扁平化設計，消除嵌套條件判斷
 */
const initializeAddress = async () => {
  if (!localFormData.county) {
    console.log('ℹ️ step1: No address data to initialize');
    return;
  }

  console.log('🏠 step1: Initializing address data');

  // 順序執行三個步驟，無嵌套
  const countyOk = await ensureCountyId();
  if (!countyOk) return;

  const townOk = await ensureTownId();
  if (!townOk && localFormData.town) return; // 如果有 town 但解析失敗，停止

  await ensureVillageId(); // 最後一步，失敗也沒關係
};

// 🆕 追蹤當前正在載入的案件編號（防止重複請求）
const loadingCaseNumber = ref<string | null>(null);

// 🆕 初始化數據 - 自主載入模式（優化防重複邏輯）
const initializeFormData = async (forceReload = false) => {
  const route = useRoute();
  const caseNumber = route.query.id as string;

  if (!caseNumber) {
    console.error('❌ step1.vue: No case number in route query');
    return;
  }

  // 🔥 防止重複請求：檢查是否正在載入相同案件
  if (loadingCaseNumber.value === caseNumber && !forceReload) {
    console.log('⏳ step1.vue: Already loading this case, skipping...');
    return;
  }

  // 防止重複初始化
  if (isInitializing.value && !forceReload) {
    console.log('⏳ step1.vue: Already initializing, skipping...');
    return;
  }

  // 如果已經初始化且非強制重載，且案件相同，跳過
  if (isInitialized.value && !forceReload && loadingCaseNumber.value === caseNumber) {
    console.log('✅ step1.vue: Already initialized for this case, skipping...');
    return;
  }

  // 🆕 強制重載時重置狀態
  if (forceReload) {
    console.log('🔄 step1.vue: Force reload triggered');
    resetFormData();
    isInitialized.value = false;
  }

  // 設置標記，防止重複請求
  loadingCaseNumber.value = caseNumber;
  isInitializing.value = true;
  console.log('🔄 step1.vue: Initializing form data with autonomous loading for case:', caseNumber);

  try {
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
      currentCaseNumber: caseNumber,
      forceReload
    });

    // 只有在沒有有效快取、案件不匹配或強制重載時才從伺服器載入
    if (!hasValidData || !isSameCaseNumber || forceReload) {
      if (!hasValidData) {
        console.log('🔄 step1.vue: No valid cached data, loading fresh data from server');
      } else if (!isSameCaseNumber) {
        console.log('🔄 step1.vue: Case number mismatch, loading fresh data from server');
        console.log(`   Previous case: ${existingData?.caseNumber}, Current case: ${caseNumber}`);
      } else {
        console.log('🔄 step1.vue: Force reload requested');
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

      // 統一地址初始化處理
      await initializeAddress();

      // 🔥 Linus式修復：在發送初始化資料前，先標記為已初始化
      // 但暫時不觸發 watch，避免地址解析被視為變更
      console.log('✅ step1.vue: Autonomous initialization complete');

      // 標記為已初始化（在發送資料之前）
      isInitialized.value = true;

      // 🔥 關鍵修復：使用 nextTick 確保地址解析完成後再發送資料
      // 這樣可以避免地址解析過程中的欄位修改被視為「變更」
      await nextTick();

      // 發送資料到父組件（只發送一次完整的初始化資料）
      emitDataChanged();
      emitValidationChanged(localValid.value);

      // 💰 初始化完成後，立即查詢補助額度
      if (localFormData.id && localFormData.caseNumber) {
        console.log('💰 [step1] Data initialized, fetching subsidy summary');
        await fetchSubsidySummaryIfNeeded();
      }
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
  emit('go-back-requested', { step: 1 });
};

// =============================================================================
// 年度補助額度限制功能
// =============================================================================

/**
 * 獲取案件年度（民國年） - Computed
 * 🔥 Linus式修復：單一資料來源，無回退方案
 * 只從 grantsStore.currentGrant.year 取得，資料缺失時記錄錯誤
 */
const caseYear = computed((): number | null => {
  // 單一資料來源：currentGrant.year
  const year = grantsStore.currentGrant?.year

  if (!year) {
    // 資料缺失是系統問題，需要明確記錄
    console.error('❌ [caseYear] CRITICAL: currentGrant.year is missing!', {
      hasCurentGrant: !!grantsStore.currentGrant,
      currentGrantKeys: grantsStore.currentGrant ? Object.keys(grantsStore.currentGrant) : [],
      caseNumber: grantsStore.currentGrant?.case_number
    })
    return null
  }

  console.log('✅ [caseYear] Year from currentGrant:', year)
  return year
})

/**
 * 是否顯示補助額度提示卡片
 */
const showSubsidySummary = computed(() => {
  const hasId = !!localFormData.id
  const hasCaseNumber = !!localFormData.caseNumber
  const year = caseYear.value

  console.log('💰 [showSubsidySummary] Check:', {
    hasId,
    hasCaseNumber,
    id: localFormData.id,
    caseNumber: localFormData.caseNumber,
    year
  })

  // 必須有身分證字號和案件編號
  return hasId && hasCaseNumber && year !== null
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
 * Alert 類型（簡化版）
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

// const subsidyAlertColor = computed(() => {
//   if (grantsStore.isSubsidyLimitExceeded) {
//     return 'orange'
//   } else if (grantsStore.remainingSubsidyAmount < 100000) {
//     return 'amber'
//   } else {
//     return 'teal'
//   }
// })

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
 * 🔥 Linus式修復：使用 currentGrant 作為唯一資料來源
 *
 * 資料來源架構：
 * Layer 1 (唯一真相): grantsStore.currentGrant (GrantCreateResponse)
 *   - 包含所有 step1 完整資料
 *   - 來自 GET /grants/case/{caseNumber}
 *
 * Layer 2 (編輯緩衝): localFormData
 *   - 用戶即時編輯狀態
 *   - 未保存前使用此層的最新值
 */
const fetchSubsidySummaryIfNeeded = async () => {
  // 🔥 優先使用編輯緩衝區的值（用戶可能修改但未保存）
  // 如果編輯緩衝區沒有值，回退到 currentGrant（已保存的值）
  const applicantId = localFormData.id || grantsStore.currentGrant?.applicant_id
  const year = caseYear.value  // 從 currentGrant.year 取得
  const currentGrantId = grantsStore.currentGrant?.id

  console.log('💰 [fetchSubsidySummaryIfNeeded] Data source:', {
    applicantId,
    year,
    currentGrantId,
    source: {
      applicantId: localFormData.id
        ? 'localFormData.id (user editing)'
        : 'currentGrant.applicant_id (saved)',
      year: 'currentGrant.year',
      currentGrantId: 'currentGrant.id'
    }
  })

  // 🔥 Fail fast：缺少任何必要資料時立即返回
  if (!applicantId) {
    console.error('❌ [fetchSubsidySummaryIfNeeded] CRITICAL: applicant_id missing!', {
      localFormDataId: localFormData.id,
      currentGrantApplicantId: grantsStore.currentGrant?.applicant_id,
      currentGrant: grantsStore.currentGrant
    })
    return
  }

  if (!year) {
    console.error('❌ [fetchSubsidySummaryIfNeeded] CRITICAL: year missing!')
    return
  }

  console.log('💰 [fetchSubsidySummaryIfNeeded] Calling API...')

  try {
    await grantsStore.fetchSubsidySummary(applicantId, year, currentGrantId)
    console.log('✅ [fetchSubsidySummaryIfNeeded] Success')
  } catch (error) {
    console.error('❌ [fetchSubsidySummaryIfNeeded] Error:', error)
  }
}

// 監聽身分證字號和案件編號變化，自動查詢補助額度
watch(
  () => [localFormData.id, localFormData.caseNumber],
  async ([newId, newCaseNumber], [oldId, oldCaseNumber]) => {
    console.log('💰 [step1] Watch triggered - ID/CaseNumber changed:', {
      newId,
      newCaseNumber,
      oldId,
      oldCaseNumber,
      isInitialized: isInitialized.value
    })

    // 只在已初始化且身分證字號或案件編號真正變化時才查詢
    if (isInitialized.value && (newId !== oldId || newCaseNumber !== oldCaseNumber) && newId && newCaseNumber) {
      console.log('💰 [step1] Applicant ID or case number changed, fetching subsidy summary')
      await fetchSubsidySummaryIfNeeded()
    }
  }
)

// 在組件掛載完成且資料初始化後，查詢補助額度
watch(
  () => isInitialized.value,
  async (initialized) => {
    console.log('💰 [step1] isInitialized watch triggered:', initialized)
    if (initialized && localFormData.id && localFormData.caseNumber) {
      console.log('💰 [step1] Component initialized, fetching subsidy summary')
      await fetchSubsidySummaryIfNeeded()
    }
  },
  { immediate: true }  // 立即執行一次，即使 isInitialized 已經是 true
)

// =============================================================================
// Expose
// =============================================================================

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

/* 補助額度資訊卡片樣式 */
/* .subsidy-info-card {
  padding: 12px;
  background-color: white;
  border-radius: 8px;
  border: 1px solid #e0e0e0;
  transition: all 0.3s ease;
}

.subsidy-info-card:hover {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  transform: translateY(-2px);
} */
</style>
