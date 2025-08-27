<template>
  <div
    ref="stepContent"
    class="step-content"
  >
    <v-card
      class="mb-0 pa-0"
      flat
    >
      <v-card-text class="pb-0 pt-0">
        <!-- 填寫說明提示 -->
        <v-alert
          type="info"
          variant="tonal"
          class="mb-4"
          prominent
          border="start"
        >
          <template #prepend>
            <v-icon size="large">
              mdi-information-outline
            </v-icon>
          </template>
          <div class="text-h6 mb-2">
            填寫說明
          </div>
          <div class="text-body-1">
            <p class="mb-2">
              <strong>注意：</strong>本階段項目皆為<strong>選填項目</strong>，請依據農戶實際申請需求進行填寫。
            </p>
            <ul class="ml-4 mb-2">
              <li><strong>補助來源：</strong>若您需要申請任何設施補助，請先選擇補助來源</li>
              <li><strong>動力設備：</strong>僅在需要申請動力設備補助時填寫</li>
              <li><strong>調蓄設施：</strong>僅在需要申請調蓄設施補助時填寫</li>
              <li><strong>調蓄控制設施：</strong>僅在需要申請蓄控制設施補助時填寫</li>
            </ul>
            <p class="mb-0">
              <v-icon
                size="small"
                class="me-1"
              >
                mdi-check-circle
              </v-icon>
              若不需要申請任何設施補助，可以直接進行下一步驟。
            </p>
          </div>
        </v-alert>

        <v-form
          ref="form"
          v-model="localValid"
          @submit.prevent
        >
          <!-- 補助來源選擇區域 -->
          <v-card
            class="mb-4"
            variant="outlined"
          >
            <v-card-title class="bg-light-blue-lighten-4 d-flex align-center py-2 px-4">
              <v-icon
                class="me-2"
                size="small"
              >
                mdi-hand-coin
              </v-icon>
              <span class="text-subtitle-1 font-weight-medium">補助來源</span>
            </v-card-title>

            <v-card-text class="pa-4">
              <v-sheet
                class="pa-3 rounded"
                color="grey-lighten-5"
              >
                <div class="d-flex align-center flex-wrap">
                  <v-select
                    v-model="localFormData.fundingSourceId"
                    :items="fundingSourceOptions"
                    item-title="name"
                    item-value="id"
                    variant="outlined"
                    density="comfortable"
                    class="me-2 mb-2"
                    style="min-width: 250px"
                    @update:model-value="updateFormData"
                  >
                    <template #label>
                      補助來源<span class="required-asterisk" />
                    </template>
                  </v-select>
                  <span class="text-body-2 text-grey ms-2">
                    選擇的補助來源將自動套用至下方新增的所有設施
                  </span>
                </div>
              </v-sheet>
            </v-card-text>
          </v-card>

          <!-- 動力設備選擇區域 -->
          <v-card
            class="mb-4"
            variant="outlined"
          >
            <v-card-title class="bg-light-blue-lighten-4 d-flex align-center py-2 px-4">
              <v-icon
                class="me-2"
                size="small"
              >
                mdi-engine
              </v-icon>
              <span class="text-subtitle-1 font-weight-medium">動力設備</span>
            </v-card-title>

            <v-card-text class="pa-4">
              <v-sheet
                class="pa-3 rounded"
                color="grey-lighten-5"
              >
                <div class="d-flex align-center flex-wrap">
                  <v-select
                    v-model="localFormData.powerEquipment"
                    :items="powerEquipmentOptions"
                    label="動力設備"
                    variant="outlined"
                    density="comfortable"
                    class="me-2 mb-2"
                    style="min-width: 200px"
                    @update:model-value="onPowerEquipmentChange"
                  />

                  <!-- <v-select
                    v-model="localFormData.fundingSource"
                    :items="powerSourceOptions"
                    label="補助單位"
                    variant="outlined"
                    density="comfortable"
                    class="me-2 mb-2"
                    style="min-width: 200px"
                  /> -->

                  <v-btn
                    color="primary"
                    class="mb-2"
                    :disabled="!canAddPowerEquipment"
                    @click="addPowerEquipment"
                  >
                    <v-icon
                      class="me-1"
                    >
                      mdi-plus
                    </v-icon>
                    加入
                  </v-btn>
                </div>
              </v-sheet>
            </v-card-text>
          </v-card>

          <!-- 調蓄設施區域 -->
          <v-card
            class="mb-4"
            variant="outlined"
          >
            <v-card-title class="bg-light-blue-lighten-4 d-flex align-center py-2 px-4">
              <v-icon
                class="me-2"
                size="small"
              >
                mdi-diving-scuba-tank-multiple
              </v-icon>
              <span class="text-subtitle-1 font-weight-medium">調蓄設施</span>
            </v-card-title>

            <v-card-text class="pa-4">
              <v-sheet
                class="pa-3 rounded"
                color="grey-lighten-5"
              >
                <div class="d-flex align-center flex-wrap">
                  <v-select
                    v-model="localFormData.storageType"
                    :items="storageTypeOptions"
                    label="調蓄設施"
                    variant="outlined"
                    density="comfortable"
                    class="me-2 mb-2"
                    style="min-width: 180px"
                    @update:model-value="onStorageTypeChange"
                  />

                  <v-select
                    v-model="localFormData.storageTonnage"
                    :items="tonnageOptions"
                    label="噸數"
                    variant="outlined"
                    density="comfortable"
                    class="me-2 mb-2"
                    style="min-width: 100px"
                  />

                  <!-- <v-select
                    v-model="localFormData.fundingSource"
                    :items="fundingSourceOptions"
                    label="補助單位"
                    variant="outlined"
                    density="comfortable"
                    class="me-2 mb-2"
                    style="min-width: 180px"
                  /> -->

                  <v-text-field
                    v-model="localFormData.storageRemark"
                    label="備註"
                    variant="outlined"
                    density="comfortable"
                    class="me-2 mb-2"
                    style="min-width: 200px"
                  />

                  <v-btn
                    color="primary"
                    class="mb-2"
                    :disabled="!canAddStorageFacility"
                    @click="addStorageFacility"
                  >
                    <v-icon class="me-1">
                      mdi-plus
                    </v-icon>
                    加入
                  </v-btn>
                </div>
              </v-sheet>
            </v-card-text>
          </v-card>

          <!-- 調蓄控制設施區域 -->
          <v-card
            class="mb-4"
            variant="outlined"
          >
            <v-card-title class="bg-light-blue-lighten-4 d-flex align-center py-2 px-4">
              <v-icon
                class="me-2"
                size="small"
              >
                mdi-valve
              </v-icon>
              <span class="text-subtitle-1 font-weight-medium">調蓄控制設施</span>
            </v-card-title>

            <v-card-text class="pa-4">
              <v-sheet
                class="pa-3 rounded"
                color="grey-lighten-5"
              >
                <!-- 面積狀態提示 -->
                <v-alert
                  v-if="facilityArea <= 0"
                  type="warning"
                  variant="tonal"
                  density="compact"
                  class="mb-3"
                >
                  <template #prepend>
                    <v-icon size="small">
                      mdi-alert-circle
                    </v-icon>
                  </template>
                  <div class="text-caption">
                    <strong>提醒：</strong>未偵測到 Step2 的施作面積資料，補助款以 0.1 公頃為基準計算。請確認 Step2 已完成並儲存。
                  </div>
                </v-alert>

                <!-- 第一行：調蓄控制設施選擇和設施名稱 -->
                <div class="d-flex align-center flex-wrap mb-3">
                  <v-select
                    v-model="localFormData.controlType"
                    :items="controlTypeOptions"
                    label="調蓄控制設施"
                    variant="outlined"
                    density="comfortable"
                    class="me-2 mb-2"
                    style="min-width: 180px"
                    @update:model-value="onControlTypeChange"
                  />

                  <v-text-field
                    v-model="localFormData.controlName"
                    label="設施名稱"
                    variant="outlined"
                    density="comfortable"
                    class="me-2 mb-2"
                    style="min-width: 220px"
                  />

                  <!-- <v-select
                    v-model="localFormData.fundingSource"
                    :items="fundingSourceOptions"
                    label="補助單位"
                    variant="outlined"
                    density="comfortable"
                    class="me-2 mb-2"
                    style="min-width: 180px"
                  /> -->
                </div>

                <!-- 第二行：數量、單價、總價和加入按鈕 -->
                <div class="d-flex align-center flex-wrap">
                  <v-text-field
                    v-model="localFormData.controlQuantity"
                    label="數量"
                    variant="outlined"
                    density="comfortable"
                    class="me-2 mb-2"
                    style="width: 80px"
                    type="number"
                    min="1"
                    :rules="[
                      v => !!v || '請輸入數量',
                      v => v > 0 || '數量必須大於0'
                    ]"
                  />

                  <v-text-field
                    v-model="localFormData.controlUnitPrice"
                    label="手動輸入單價"
                    prefix="$"
                    variant="outlined"
                    density="comfortable"
                    class="me-2 mb-2"
                    style="width: 120px"
                    type="number"
                    min="0"
                    placeholder="請輸入單價"
                    :rules="[
                      v => !!v || '請輸入單價',
                      v => v > 0 || '單價必須大於0'
                    ]"
                  />

                  <v-text-field
                    v-model="controlActualSubsidyAmount"
                    label="補助款"
                    prefix="$"
                    variant="outlined"
                    density="comfortable"
                    class="me-2 mb-2"
                    style="width: 120px"
                    readonly
                    bg-color="green-lighten-5"
                    :model-value="controlActualSubsidyAmount.toLocaleString()"
                  />

                  <v-text-field
                    v-model="controlSelfPaidAmount"
                    label="自備款"
                    prefix="$"
                    variant="outlined"
                    density="comfortable"
                    class="me-2 mb-2"
                    style="width: 120px"
                    readonly
                    bg-color="orange-lighten-5"
                    :model-value="controlSelfPaidAmount.toLocaleString()"
                  />

                  <v-btn
                    color="primary"
                    class="mb-2"
                    :disabled="!canAddControlFacility"
                    @click="addControlFacility"
                  >
                    <v-icon class="me-1">
                      mdi-plus
                    </v-icon>
                    加入
                  </v-btn>
                </div>
              </v-sheet>
            </v-card-text>
          </v-card>

          <!-- 設施列表 -->
          <v-card variant="outlined">
            <v-card-title class="bg-light-blue-lighten-4 d-flex align-center py-2 px-4">
              <v-icon
                class="me-2"
                size="small"
              >
                mdi-format-list-bulleted
              </v-icon>
              <span class="text-subtitle-1 font-weight-medium">已新增設施列表</span>
            </v-card-title>

            <v-card-text class="pa-4">
              <v-table class="rounded border">
                <thead class="bg-grey-lighten-3">
                  <tr>
                    <th
                      class="text-center"
                      style="width: 60px"
                    >
                      NO.
                    </th>
                    <th style="width: 140px">
                      設施類型
                    </th>
                    <th style="width: 200px">
                      設施名稱
                    </th>
                    <th
                      class="text-center"
                      style="width: 100px"
                    >
                      數量
                    </th>
                    <th
                      class="text-center"
                      style="width: 140px"
                    >
                      單價
                    </th>
                    <th style="width: 220px">
                      補助標準
                    </th>
                    <!-- <th style="width: 180px">
                      補助來源
                    </th> -->
                    <th
                      class="text-center"
                      style="width: 80px"
                    >
                      刪除
                    </th>
                  </tr>
                </thead>
                <tbody>
                  <tr
                    v-for="(facility, index) in localFormData.facilities"
                    :key="index"
                  >
                    <td class="text-center">
                      {{ index + 1 }}
                    </td>
                    <td>{{ facility.typeLabel }}</td>
                    <td>{{ facility.name }}</td>
                    <td class="text-center">
                      <v-text-field
                        v-model="facility.quantity"
                        type="number"
                        min="1"
                        density="compact"
                        variant="outlined"
                        hide-details="auto"
                        class="ma-1"
                        style="width: 70px"
                        :rules="[
                          v => !!v || '請輸入數量',
                          v => v > 0 || '數量必須大於0'
                        ]"
                        @update:model-value="updateFacilityTotal(index)"
                      />
                    </td>
                    <td class="text-center">
                      <v-text-field
                        v-model="facility.unitPrice"
                        type="number"
                        prefix="$"
                        min="0"
                        density="compact"
                        variant="outlined"
                        hide-details
                        class="ma-1"
                        style="width: 130px"
                        @update:model-value="updateFacilityTotal(index)"
                      />
                    </td>
                    <td>{{ facility.remark }}</td>
                    <!-- <td>{{ getFundingSourceName(facility.fundingSourceId) }}</td> -->
                    <td class="text-center">
                      <v-btn
                        icon
                        size="x-small"
                        color="error"
                        variant="text"
                        @click="removeFacility(index)"
                      >
                        <v-icon>mdi-close</v-icon>
                      </v-btn>
                    </td>
                  </tr>
                  <tr v-if="localFormData.facilities.length === 0">
                    <td
                      colspan="8"
                      class="text-center py-3 text-grey"
                    >
                      尚未新增任何設施，請使用上方各區塊的加入按鈕新增設施
                    </td>
                  </tr>
                </tbody>
              </v-table>

              <!-- 💰 金額統計區塊 -->
              <div
                v-if="localFormData.facilities.length > 0"
                class="mt-4"
              >
                <v-row>
                  <v-col
                    cols="12"
                    md="6"
                  >
                    <v-card
                      class="pa-4 text-center"
                      color="green-lighten-5"
                      variant="outlined"
                    >
                      <v-icon
                        class="mb-2"
                        color="green-darken-2"
                        size="large"
                      >
                        mdi-hand-coin
                      </v-icon>
                      <div class="text-h6 text-green-darken-2 font-weight-bold">
                        補助款總額
                      </div>
                      <div class="text-h4 text-green-darken-3 font-weight-bold mt-2">
                        ${{ totalSubsidyAmount.toLocaleString() }}
                      </div>
                      <div class="text-caption text-green-darken-1 mt-1">
                        共 {{ localFormData.facilities.length }} 項設施
                      </div>
                    </v-card>
                  </v-col>
                  <v-col
                    cols="12"
                    md="6"
                  >
                    <v-card
                      class="pa-4 text-center"
                      color="orange-lighten-5"
                      variant="outlined"
                    >
                      <v-icon
                        class="mb-2"
                        color="orange-darken-2"
                        size="large"
                      >
                        mdi-wallet
                      </v-icon>
                      <div class="text-h6 text-orange-darken-2 font-weight-bold">
                        自備款總額
                      </div>
                      <div class="text-h4 text-orange-darken-3 font-weight-bold mt-2">
                        ${{ totalSelfPaidAmount.toLocaleString() }}
                      </div>
                      <div class="text-caption text-orange-darken-1 mt-1">
                        {{ facilitiesWithSelfPaid }} 項需要自備款
                      </div>
                    </v-card>
                  </v-col>
                </v-row>
              </div>
            </v-card-text>
          </v-card>
        </v-form>
      </v-card-text>
    </v-card>
  </div>
</template>

<script setup lang="ts">
import { useGrantsStore } from '@/stores/grants';
import { useOfficesStore } from '@/stores/offices';
import { calculateSubsidyAmount, determineRegionType, validateStorageFacility, getStorageCapacityLimit } from '@/utils/subsidyStandards';

// Props definition
const props = defineProps({
  formData: {
    type: Object,
    required: true,
    default: () => ({})
  },
  currentStep: {
    type: Number,
    required: true
  }
});

// Event emitters
const emit = defineEmits(['update:formData', 'validated', 'go-back']);

// Access grants store
const grantsStore = useGrantsStore();
const officesStore = useOfficesStore();

// Form ref and validation state
const form = ref(null);
const localValid = ref(true);

// 本地表單數據
const localFormData = reactive({
  fundingSourceId: 0,
  // 動力設備
  powerEquipment: '',

  // 調蓄設施
  storageType: '',
  storageTonnage: '',
  storageSource: '',
  storageRemark: '',

  // 調蓄控制設施
  controlType: '',
  controlName: '',
  controlQuantity: 1,
  controlUnitPrice: '',
  controlSource: '',

  // 設施列表
  facilities: [] as Array<{
    type: string;
    typeLabel: string;
    name: string;
    quantity: number;
    unitPrice: number;
    totalPrice: number;
    subsidyAmount?: number;  // 補助款
    selfPaidAmount?: number; // 自備款
    remark: string;
    fundingSourceId: string | number;
  }>,

  // Always valid for seamless navigation
  valid: true
});

// 選項
const powerEquipmentOptions = [
  '馬達（含抽水機）',
  '柱塞式泵',
  '汽油引擎',
  '柴油引擎'
];

const powerSourceOptions = [
  '農田水利署',
  '七星管理處作業基金',
  '瑠公管理處作業基金'
];

const storageTypeOptions = [
  '鋁合金',
  '不鏽鋼',
  '塑膠類'
];

const tonnageOptions = [
  '10',
  '20',
  '30',
  '40',
  '50',
  '60',
  '70',
  '80',
  '90',
  '100'
];

const controlTypeOptions = [
  '自動化控制',
  '微氣象調節',
  '液肥注入器',
  '過濾器',
  '其他調控設施',
  '農藥混入設施',
  '肥料混入設施',
  '控制箱',
  '電磁閥',
  '流量表'
];

// 🔥 Linus式修復：消除愚蠢的多重資料源，統一計算邏輯
const regionType = computed(() => {
  const step2Data = grantsStore.formData[2] || {};
  // 🔧 修復：從 lands 陣列中判斷原民地區
  const isAboriginalArea = step2Data.lands?.some((land: any) => land.isAboriginalArea) ||
                          step2Data.isAboriginalArea || false;
  console.log('[Step3] 地區類型計算 - isAboriginalArea:', isAboriginalArea);
  return determineRegionType(isAboriginalArea);
});

// 🔥 Linus式修復：強制載入step2資料，消除reload問題
const facilityArea = computed(() => {
  const step2Data = grantsStore.formData[2] || {};

  // 🔧 修復：正確計算總施作面積
  let totalArea = 0;

  // 新版多筆土地格式
  if (step2Data.lands && Array.isArray(step2Data.lands)) {
    totalArea = step2Data.lands.reduce((sum: number, land: any) => {
      const area = parseFloat(land.facilityArea) || 0;
      return sum + area;
    }, 0);
    console.log('[Step3] 多筆土地總面積計算 - lands:', step2Data.lands.length, 'totalArea:', totalArea);
  }
  // 向後相容：舊版單筆土地格式
  else if (step2Data.facilityArea) {
    totalArea = parseFloat(step2Data.facilityArea) || 0;
    console.log('[Step3] 單筆土地面積計算 - facilityArea:', totalArea);
  }
  // 🆘 DEBUG: 如果都沒有，強制檢查整個grantsStore狀態
  else {
    console.warn('[Step3] 無法取得step2面積資料，檢查grantsStore狀態:', {
      'formData[2]': grantsStore.formData[2],
      'currentGrant': grantsStore.currentGrant?.case_number,
      'currentStep': grantsStore.currentStep
    });
  }

  // 轉換為公頃
  const areaHa = totalArea / 10000;
  console.log('[Step3] 設施面積計算完成 - 總面積:', totalArea, 'm², 公頃:', areaHa);
  return areaHa;
});

// 🗑️ 移除垃圾的 localStorage 邏輯 - Linus: "Never break userspace, but always fix bad design"

// 🔥 Linus式修復：統一手動輸入邏輯，清晰分離補助款和自備款
const controlSubsidyAmount = computed(() => {
  if (!localFormData.controlType) return 0;

  // 🔧 修復：即使沒有面積，也要給一個參考值（預設 0.1 公頃）
  const area = facilityArea.value > 0 ? facilityArea.value : 0.1;

  // 計算政府補助上限（按面積）
  const subsidyLimit = calculateSubsidyAmount('control', localFormData.controlType, regionType.value, 1, undefined, area);
  console.log(`[調蓄控制設施] 補助上限計算 - 地區:${regionType.value}, 使用面積:${area}公頃, 補助上限:${subsidyLimit}`);
  return subsidyLimit;
});

const controlSelfPaidAmount = computed(() => {
  const unitPrice = parseFloat(localFormData.controlUnitPrice as any) || 0;
  const quantity = parseFloat(localFormData.controlQuantity as any) || 1;
  const totalCost = unitPrice * quantity;
  const subsidyAmount = controlSubsidyAmount.value;

  // 自備款 = 總成本 - 補助款（不能小於0）
  const selfPaid = Math.max(0, totalCost - subsidyAmount);
  console.log(`[調蓄控制設施] 自備款計算 - 總成本:${totalCost}, 補助:${subsidyAmount}, 自備:${selfPaid}`);
  return selfPaid;
});

const controlActualSubsidyAmount = computed(() => {
  const unitPrice = parseFloat(localFormData.controlUnitPrice as any) || 0;
  const quantity = parseFloat(localFormData.controlQuantity as any) || 1;
  const totalCost = unitPrice * quantity;
  const subsidyLimit = controlSubsidyAmount.value;

  // 實際補助款 = min(總成本, 補助上限)
  return Math.min(totalCost, subsidyLimit);
});

// 🔥 Linus式修復：金額統計計算邏輯
const totalSubsidyAmount = computed(() => {
  return localFormData.facilities.reduce((total, facility) => {
    // 動力設備和調蓄設施：補助款 = 總價
    if (facility.type === 'power' || facility.type === 'storage') {
      return total + (facility.totalPrice || 0);
    }
    // 調蓄控制設施：使用 subsidyAmount
    else if (facility.type === 'control') {
      return total + (facility.subsidyAmount || 0);
    }
    return total;
  }, 0);
});

const totalSelfPaidAmount = computed(() => {
  return localFormData.facilities.reduce((total, facility) => {
    // 只有調蓄控制設施才有自備款
    if (facility.type === 'control') {
      return total + (facility.selfPaidAmount || 0);
    }
    return total;
  }, 0);
});

const facilitiesWithSelfPaid = computed(() => {
  return localFormData.facilities.filter(facility =>
    facility.type === 'control' && (facility.selfPaidAmount || 0) > 0
  ).length;
});

// 🔥 Linus式修復：區分設施類型的顯示邏輯
const hasSelfPaidFacilities = computed(() => {
  // 只有調蓄控制設施需要顯示自備款欄位
  return localFormData.facilities.some(facility => facility.type === 'control');
});

const getFacilitySubsidyDisplay = (facility: any): string => {
  // 動力設備和調蓄設施：補助款 = 總價
  if (facility.type === 'power' || facility.type === 'storage') {
    return facility.totalPrice ? facility.totalPrice.toLocaleString() : '0';
  }
  // 調蓄控制設施：使用 subsidyAmount
  else if (facility.type === 'control') {
    return facility.subsidyAmount ? facility.subsidyAmount.toLocaleString() : '0';
  }
  return '0';
};

const getFacilitySelfPaidDisplay = (facility: any): string => {
  // 只有調蓄控制設施才有自備款
  if (facility.type === 'control') {
    return facility.selfPaidAmount ? facility.selfPaidAmount.toLocaleString() : '0';
  }
  return '-'; // 其他設施類型顯示 '-'
};

const fundingSourceOptions = computed(() => {
  const filtered = officesStore.offices
    .filter(office => {
      return office.is_funding_source === true
    })
    .map(office => ({
      id: office.id,
      name: office.name
    }))

  return filtered
});

// 驗證條件
const canAddPowerEquipment = computed(() => {
  return !!localFormData.powerEquipment;
});

const canAddStorageFacility = computed(() => {
  return !!localFormData.storageType && !!localFormData.storageTonnage;
});

const canAddControlFacility = computed(() => {
  return !!localFormData.controlType &&
         !!localFormData.controlName &&
         !!localFormData.controlQuantity &&
         !!localFormData.controlUnitPrice;
});

const formattedPrice = computed({
  get() {
    // 顯示格式化價格
    return formatPrice(localFormData.controlUnitPrice);
  },
  set(value) {
    // 將輸入轉換回純數字儲存
    const numericValue = value.replace(/[^\d]/g, '');
    localFormData.controlUnitPrice = numericValue;
  }
});

// 方法
const onPowerEquipmentChange = () => {
  updateFormData();
};

const onStorageTypeChange = () => {
  updateFormData();
};

// 🔥 Linus式修復：不同設施類型使用不同邏輯
// 動力設備 - 直接使用補助款作為單價，無自備款
const addPowerEquipment = () => {
  if (canAddPowerEquipment.value) {
    const correctSubsidy = calculateSubsidyAmount('power', localFormData.powerEquipment, regionType.value, 1);

    localFormData.facilities.push({
      type: 'power',
      typeLabel: '動力設備',
      name: localFormData.powerEquipment,
      quantity: 1,
      unitPrice: correctSubsidy, // 補助款即為單價
      totalPrice: correctSubsidy, // 總價等於補助款
      remark: `[${regionType.value === 'indigenous' ? '原民地區' : '一般地區'}]`,
      fundingSourceId: localFormData.fundingSourceId !== null && localFormData.fundingSourceId !== undefined ? localFormData.fundingSourceId : '未選擇補助來源'
    });

    // 清空選擇
    localFormData.powerEquipment = '';

    updateFormData();
  }
};

// 調蓄設施 - 直接使用補助款作為單價，無自備款
const addStorageFacility = () => {
  if (canAddStorageFacility.value) {
    const tonnage = parseInt(localFormData.storageTonnage);
    const equipment = `${localFormData.storageType}-${tonnage}噸`;

    // 驗證設施參數
    if (!validateStorageFacility(localFormData.storageType, tonnage, facilityArea.value)) {
      alert('調蓄設施參數不符合補助標準（材料、噸數或面積不符）');
      return;
    }

    const correctSubsidy = calculateSubsidyAmount('storage', equipment, regionType.value, 1, tonnage);

    if (correctSubsidy === 0) {
      alert('無法計算補助金額，請確認設施參數是否正確');
      return;
    }

    localFormData.facilities.push({
      type: 'storage',
      typeLabel: '調蓄設施',
      name: equipment,
      quantity: 1,
      unitPrice: correctSubsidy, // 補助款即為單價
      totalPrice: correctSubsidy, // 總價等於補助款
      remark: `${localFormData.storageRemark || ''} [${regionType.value === 'indigenous' ? '原民地區' : '一般地區'}]`,
      fundingSourceId: localFormData.fundingSourceId !== null && localFormData.fundingSourceId !== undefined ? localFormData.fundingSourceId : '未選擇補助來源'
    });

    // 清空選擇
    localFormData.storageType = '';
    localFormData.storageTonnage = '';
    localFormData.storageRemark = '';

    updateFormData();
  }
};

// 🔥 Linus式修復：統一手動輸入邏輯，清晰分離補助和自備款
const addControlFacility = () => {
  if (canAddControlFacility.value) {
    const quantity = parseFloat(localFormData.controlQuantity as any) || 1;
    const unitPrice = parseFloat(localFormData.controlUnitPrice as any) || 0;
    const totalCost = unitPrice * quantity;
    const subsidyAmount = controlActualSubsidyAmount.value;
    const selfPaidAmount = controlSelfPaidAmount.value;

    console.log(`[調蓄控制設施] 新增 - 單價:${unitPrice}, 數量:${quantity}, 總成本:${totalCost}, 補助:${subsidyAmount}, 自備:${selfPaidAmount}`);

    localFormData.facilities.push({
      type: 'control',
      typeLabel: '調蓄控制設施',
      name: localFormData.controlName,
      quantity: quantity,
      unitPrice: unitPrice,
      totalPrice: totalCost, // 總成本
      subsidyAmount: subsidyAmount, // 實際補助款
      selfPaidAmount: selfPaidAmount, // 自備款
      remark: `[${regionType.value === 'indigenous' ? '原民地區' : '一般地區'}] 設施面積: ${formatArea(facilityArea.value)}公頃`,
      fundingSourceId: localFormData.fundingSourceId !== null && localFormData.fundingSourceId !== undefined ? localFormData.fundingSourceId : '未選擇補助來源'
    });

    // 清空選擇
    localFormData.controlType = '';
    localFormData.controlName = '';
    localFormData.controlUnitPrice = '';

    updateFormData();
  }
};

// 移除設施
const removeFacility = (index: number) => {
  localFormData.facilities.splice(index, 1);
  updateFormData();
};

// 更新設施的總價
const updateFacilityTotal = (index) => {
  const facility = localFormData.facilities[index];

  // 確保數量和單價為有效數字
  const quantity = parseFloat(facility.quantity) || 0;
  const unitPrice = parseFloat(facility.unitPrice) || 0;

  // 重新計算總價並更新
  facility.totalPrice = quantity * unitPrice;

  // 更新父組件資料
  updateFormData();
};

// 🔥 Linus式修復：工具函數 - 消除重複邏輯
const formatPrice = (value) => {
  if (!value && value !== 0) return '';
  return Number(value).toLocaleString();
};

const formatArea = (area: number): string => {
  if (!area && area !== 0) return '0.0000';
  return Number(area).toFixed(4);
};

const getFundingSourceName = (fundingSourceId: string | number): string => {
  // 🔥 Linus式修復：使用嚴格比較，避免 0 被判斷為 falsy
  if (fundingSourceId === null || fundingSourceId === undefined || fundingSourceId === '未選擇補助來源') {
    return '未選擇補助來源';
  }

  const source = fundingSourceOptions.value.find(option => option.id === fundingSourceId);
  return source ? source.name : '未找到補助來源';
};


// 更新父組件數據
const updateFormData = () => {
  emit('update:formData', {
    ...props.formData,
    ...localFormData,
    valid: true // Always true for seamless navigation
  });
};

const onControlTypeChange = () => {
  // 當選擇變化時，將調蓄控制設施類型的值自動帶入到設施名稱
  localFormData.controlName = localFormData.controlType;
  updateFormData();
};

// 初始化數據 及 step2 資料監聽
onMounted(async () => {
  console.log("Step 3 mounted, formData:", props.formData);

  // 🔥 Linus式修復：確保 caseNumber 與當前案件一致，避免載入錯誤資料
  const currentCaseNumber = grantsStore.currentGrant?.case_number;
  if (currentCaseNumber && (!grantsStore.formData[2] || Object.keys(grantsStore.formData[2]).length === 0)) {
    console.log('[Step3] 偵測到step2資料缺失，為當前案件載入...', currentCaseNumber);
    try {
      await grantsStore.loadStepData(currentCaseNumber, 2);
      console.log('[Step3] step2資料載入完成:', grantsStore.formData[2]);
    } catch (error) {
      console.error('[Step3] 載入step2資料失敗:', error);
    }
  } else if (!currentCaseNumber) {
    console.warn('[Step3] 沒有當前案件，無法載入step2資料');
  }

  // Set form data from props
  if (props.formData) {
    // Set basic properties
    Object.keys(localFormData).forEach(key => {
      if (props.formData[key] !== undefined) {
        localFormData[key] = props.formData[key];
      }
    });

    // Ensure facilities array is properly set
    if (Array.isArray(props.formData.facilities)) {
      localFormData.facilities = [...props.formData.facilities];
    }
  }

  // 初始記錄 step2 資料狀態
  logStep2DataStatus();

  // Initial update to parent
  updateFormData();
});

// 🔧 簡化的診斷函數
const logStep2DataStatus = () => {
  const grantsStoreData = grantsStore.formData[2];

  console.log('[Step3 診斷] Step2 資料狀態:');
  console.log('  - grantsStore.formData[2]:', grantsStoreData);
  console.log('  - 土地數量:', grantsStoreData?.lands?.length || '單筆土地模式');
  console.log('  - 當前地區類型:', regionType.value);
  console.log('  - 當前設施面積（公頃）:', facilityArea.value);
};

// Watch for props changes and localStorage changes
watch(() => props.formData, (newData) => {
  if (newData) {
    Object.keys(localFormData).forEach(key => {
      if (key !== 'facilities' && newData[key] !== undefined &&
          JSON.stringify(newData[key]) !== JSON.stringify(localFormData[key])) {
        localFormData[key] = newData[key];
      }
    });

    // Special handling for facilities array
    if (Array.isArray(newData.facilities) &&
        JSON.stringify(newData.facilities) !== JSON.stringify(localFormData.facilities)) {
      localFormData.facilities = [...newData.facilities];
    }
  }
}, { deep: true });

// 🔥 簡化：統一監聽 grantsStore 的變化即可
watch(() => grantsStore.formData[2], (newStep2Data) => {
  console.log('[Step3] Step2 資料變化，重新計算補助標準');
  nextTick(() => {
    console.log('[Step3] 重新計算後 - 地區類型:', regionType.value, '設施面積（公頃）:', facilityArea.value);
  });
}, { deep: true });

// Watch local form data and update parent
watch(localFormData, () => {
  updateFormData();
}, { deep: true });

// Watch for validation status changes
watch(localValid, (newVal) => {
  if (props.formData?.valid !== newVal) {
    updateFormData();
  }
});
</script>

<style scoped>
.step-content {
  padding: 0;
}

.v-card-title {
  color: rgba(0, 0, 0, 0.87);
  font-size: 1.25rem;
  font-weight: 500;
  padding: 16px;
}

.bg-light-blue-lighten-4 {
  background-color: #B3E5FC !important;
}

.border {
  border: 1px solid rgba(0, 0, 0, 0.12);
}

.v-table {
  background-color: white;
}

.v-table th {
  font-weight: 600;
  color: rgba(0, 0, 0, 0.7);
}

/* 可編輯欄位的樣式 */
.v-text-field.v-input--density-compact .v-field__input {
  padding-top: 4px;
  padding-bottom: 4px;
  min-height: 32px;
}

.v-text-field.v-input--density-compact {
  margin-top: 0;
  margin-bottom: 0;
}

/* 提示可編輯欄位的背景色 */
.v-text-field.v-input--density-compact .v-field {
  background-color: rgba(0, 0, 0, 0.02);
  border: 1px solid rgba(0, 0, 0, 0.1);
}

/* 必填欄位紅色星號樣式 */
.required-asterisk {
  color: #ff0000 !important;
  font-weight: bold;
  margin-left: 2px;
}
</style>
