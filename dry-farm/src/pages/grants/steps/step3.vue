<template>
  <div
    ref="stepContent"
    class="step-content"
  >
    <v-card
      class="mt-4 mb-0 pa-0"
      flat
    >
      <v-card-text class="pb-0 pt-0">
        <!-- 填寫說明提示 -->
        <v-card
          flat
          class="mb-4 pa-4"
          color="#fff3e0"
          rounded="lg"
        >
          <div class="d-flex align-center mb-3">
            <v-icon
              size="small"
              color="#f57c00"
              class="me-2"
            >
              mdi-information-outline
            </v-icon>
            <span
              class="text-subtitle-1 font-weight-bold"
              style="color: #e65100;"
            >
              填寫說明
            </span>
          </div>
          <div class="text-body-2">
            <p class="mb-2">
              <strong>注意：</strong>本階段項目皆為<strong>選填項目</strong>，請依據農戶實際申請需求進行填寫。
            </p>
            <ul class="ml-4 mb-2">
              <li><strong>補助來源：</strong>申請任何設施補助前，請先確認補助來源是否正確</li>
              <li><strong>動力設備：</strong>僅在需要申請動力設備補助時填寫</li>
              <li><strong>調蓄設施：</strong>僅在需要申請調蓄設施補助時填寫</li>
              <li><strong>調節控制設施：</strong>僅在需要申請調控設施補助時填寫</li>
            </ul>
            <p class="mb-0">
              <v-icon
                size="small"
                color="#f57c00"
                class="me-1"
              >
                mdi-check-circle
              </v-icon>
              若不需要申請任何設施補助，可以直接進行下一步驟。
            </p>
          </div>
        </v-card>

        <v-form
          ref="form"
          v-model="localValid"
          @submit.prevent
        >
          <!-- 動力設備選擇區域 -->
          <v-card
            flat
            class="mb-4 pa-4"
            color="#e3f4f4"
            rounded="lg"
          >
            <v-card-title
              class="text-subtitle-1 font-weight-bold pa-0 pb-4 d-flex align-center"
              style="color: #2d8c8f"
            >
              <v-icon
                color="#3ea0a3"
                class="me-2"
                size="small"
              >
                mdi-hammer-wrench
              </v-icon>
              補助設施
              <!-- 補助來源 chip (僅在有值且非編輯模式時顯示) -->
              <template v-if="getFundingSourceName(localFormData.fundingSourceId) !== '未選擇補助來源' && !isEditingFundingSource">
                <v-chip
                  class="ms-4"
                  size="small"
                  variant="flat"
                  color="#3ea0a3"
                >
                  <v-icon
                    size="x-small"
                    class="me-1"
                  >
                    mdi-office-building
                  </v-icon>
                  補助來源：{{ getFundingSourceName(localFormData.fundingSourceId) }}
                </v-chip>
                <v-btn
                  icon
                  size="x-small"
                  variant="text"
                  color="#3ea0a3"
                  class="ms-2"
                  @click="isEditingFundingSource = true"
                >
                  <v-icon size="small">
                    mdi-pencil
                  </v-icon>
                </v-btn>
              </template>
            </v-card-title>
            <!-- 補助來源輸入區塊 (當補助來源未選擇或在編輯模式時顯示) -->
            <v-sheet
              v-if="isEditingFundingSource"
              class="mb-3 pa-4 rounded"
              color="#fff3e0"
            >
              <div
                v-if="getFundingSourceName(localFormData.fundingSourceId) === '未選擇補助來源'"
                class="d-flex align-center mb-3"
              >
                <v-icon
                  size="small"
                  color="#f57c00"
                  class="me-2"
                >
                  mdi-alert-circle
                </v-icon>
                <span
                  class="text-body-2 font-weight-bold"
                  style="color: #e65100;"
                >
                  請先選擇補助來源
                </span>
              </div>
              <div class="d-flex align-center flex-wrap">
                <v-select
                  v-model="localFormData.fundingSourceId"
                  :items="fundingSourceOptions"
                  item-title="name"
                  item-value="id"
                  label="本案補助來源"
                  variant="outlined"
                  density="comfortable"
                  color="#f57c00"
                  bg-color="white"
                  class="me-3 mb-2"
                  style="min-width: 300px;"
                  hide-details
                  autofocus
                  @update:model-value="updateFormData"
                />
                <v-btn
                  color="#f57c00"
                  variant="flat"
                  class="flex-grow-2 mb-2"
                  rounded="lg"
                  size="large"
                  :disabled="getFundingSourceName(localFormData.fundingSourceId) === '未選擇補助來源'"
                  @click="isEditingFundingSource = false"
                >
                  <v-icon class="me-1">
                    mdi-check
                  </v-icon>
                  確認
                </v-btn>
                <v-btn
                  v-if="localFormData.facilities.length === 0"
                  color="grey-darken-1"
                  variant="outlined"
                  class="ms-2 mb-2"
                  rounded="lg"
                  size="large"
                  @click="skipStep"
                >
                  <v-icon class="me-1">
                    mdi-skip-next
                  </v-icon>
                  不需申請灌溉調控設施補助
                </v-btn>
              </div>
              <div class="text-caption text-grey-darken-1 mt-2">
                <v-icon
                  size="x-small"
                  class="me-1"
                >
                  mdi-information-outline
                </v-icon>
                選擇的補助來源將自動套用至本案申請的所有補助項目
              </div>
            </v-sheet>
            <!-- 動力設備區域 -->
            <v-sheet
              v-if="!isEditingFundingSource"
              class="mb-3 pa-3 rounded"
              color="white"
            >
              <div class="d-flex align-center mb-2">
                <v-icon
                  size="small"
                  class="me-2"
                >
                  mdi-engine
                </v-icon>
                <span class="text-body-2 font-weight-medium">動力設備</span>
              </div>

              <div class="d-flex align-center flex-wrap">
                <v-select
                  v-model="localFormData.powerEquipment"
                  :items="powerEquipmentOptions"
                  variant="outlined"
                  density="comfortable"
                  class="me-2"
                  style="min-width: 200px"
                  clearable
                  hide-details
                  @update:model-value="onPowerEquipmentChange"
                />
                <v-btn
                  color="success"
                  class="flex-grow-2"
                  variant="flat"
                  rounded="lg"
                  size="large"
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
            <!-- 調蓄設施區域 -->
            <v-sheet
              v-if="!isEditingFundingSource"
              class="mb-3 pa-3 rounded"
              color="white"
            >
              <div class="d-flex align-center mb-2">
                <v-icon
                  size="small"
                  class="me-2"
                >
                  mdi-diving-scuba-tank-multiple
                </v-icon>
                <span class="text-body-2 font-weight-medium">調蓄設施</span>
              </div>
              <!-- 容量狀態提示 -->
              <v-alert
                v-if="facilityArea > 0"
                type="info"
                variant="tonal"
                density="compact"
                class="mb-3"
              >
                <template #prepend>
                  <v-icon size="small">
                    mdi-information-outline
                  </v-icon>
                </template>
                <div class="text-caption">
                  <strong>容量狀態：</strong>
                  面積 {{ facilityArea.toFixed(4) }} 公頃 →
                  最大容量 {{ maxStorageCapacity }} 噸 |
                  已申請 {{ existingStorageCapacity }} 噸 |
                  剩餘可申請 {{ availableStorageCapacity }} 噸
                </div>
              </v-alert>

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
                  <strong>提醒：</strong>未偵測到 Step2 的施作面積資料，以 0.1 公頃為基準計算（最大容量 50 噸）。請確認 Step2 已完成並儲存。
                </div>
              </v-alert>

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
                  :hint="tonnageOptions.length === 0 ? '當前容量已滿，無法加入更多調蓄設施' : `可選擇 ${tonnageOptions.length} 種噸數`"
                  persistent-hint
                />

                <v-text-field
                  v-model="localFormData.storageRemark"
                  label="備註"
                  variant="outlined"
                  density="comfortable"
                  class="me-2 mb-2"
                  style="min-width: 200px"
                />

                <v-btn
                  color="success"
                  class="flex-grow-2 mb-7"
                  variant="flat"
                  rounded="lg"
                  size="large"
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
            <!-- 調節控制設施區域 -->
            <v-sheet
              v-if="!isEditingFundingSource"
              class="pa-3 rounded"
              color="white"
            >
              <div class="d-flex align-center mb-2">
                <v-icon
                  size="small"
                  class="me-2"
                >
                  mdi-valve
                </v-icon>
                <span class="text-body-2 font-weight-medium">調節控制設施</span>
              </div>
              <!-- 補助額度狀態提示 -->
              <v-alert
                v-if="facilityArea > 0"
                type="info"
                variant="tonal"
                density="compact"
                class="mb-3"
              >
                <template #prepend>
                  <v-icon size="small">
                    mdi-information-outline
                  </v-icon>
                </template>
                <div class="text-caption">
                  <strong>補助額度狀態：</strong>
                  <!-- 判斷限制類型並顯示對應說明 -->
                  <template v-if="grantsStore.hasSubsidySummary && totalControlSubsidyLimit < getControlSubsidyLimit(facilityArea, regionType)">
                    面積 {{ facilityArea.toFixed(4) }} 公頃 → 有效額度 ${{ totalControlSubsidyLimit.toLocaleString() }}
                    <span class="text-warning font-weight-bold">（原補助上限 ${{ getControlSubsidyLimit(facilityArea, regionType).toLocaleString() }} 超過個人年度補助限額）</span>
                  </template>
                  <template v-else>
                    面積 {{ facilityArea.toFixed(4) }} 公頃 → 補助上限 ${{ totalControlSubsidyLimit.toLocaleString() }}
                  </template>
                  |
                  已申請 ${{ totalControlSubsidy.toLocaleString() }} |
                  剩餘額度 ${{ availableControlSubsidy.toLocaleString() }}
                  <span
                    v-if="overallControlSubsidyRatio > 0"
                    class="ms-2"
                  >
                    (整體補助比例: {{ (overallControlSubsidyRatio * 100).toFixed(1) }}%)
                  </span>
                </div>
              </v-alert>

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
              <!-- 第一行：調節控制設施選擇和設施名稱 -->
              <div class="d-flex align-center flex-wrap mb-3">
                <v-select
                  v-model="localFormData.controlType"
                  :items="controlTypeOptions"
                  label="調節控制設施"
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
                  autocomplete="off"
                />
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
                  autocomplete="off"
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
                  autocomplete="off"
                />

                <v-text-field
                  :model-value="controlActualSubsidyAmount.toLocaleString()"
                  label="補助款"
                  prefix="$"
                  variant="outlined"
                  density="comfortable"
                  class="me-2 mb-2"
                  style="width: 120px"
                  readonly
                  bg-color="green-lighten-5"
                />

                <v-text-field
                  :model-value="controlSelfPaidAmount.toLocaleString()"
                  label="自備款"
                  prefix="$"
                  variant="outlined"
                  density="comfortable"
                  class="me-2 mb-2"
                  style="width: 120px"
                  readonly
                  bg-color="orange-lighten-5"
                />

                <v-btn
                  color="success"
                  class="flex-grow-2 mb-7"
                  variant="flat"
                  rounded="lg"
                  size="large"
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
          </v-card>

          <!-- 設施列表 -->
          <v-card-title
            class="text-subtitle-1 font-weight-bold pa-0 pb-2 d-flex align-center"
            style="color: #2d8c8f"
          >
            <v-icon
              color="#3ea0a3"
              class="me-2"
              size="small"
            >
              mdi-format-list-bulleted
            </v-icon>
            補助設施列表
          </v-card-title>
          <!-- 💰 個人年度補助額度資訊 -->
          <v-alert
            v-if="grantsStore.hasSubsidySummary && localFormData.facilities.length > 0"
            type="info"
            variant="tonal"
            density="compact"
            class="mb-3"
            prominent
            border="start"
          >
            <template #prepend>
              <v-icon size="small">
                mdi-calculator
              </v-icon>
            </template>
            <div class="text-body-2">
              <div class="font-weight-bold mb-2">
                個人年度補助額度使用狀況
              </div>
              <v-row dense>
                <v-col cols="12" sm="6" md="3">
                  <div class="text-caption text-grey-darken-1">個人年度上限</div>
                  <div class="text-subtitle-2 font-weight-bold">
                    NT$ {{ grantsStore.subsidyLimit.toLocaleString() }}
                  </div>
                </v-col>
                <v-col cols="12" sm="6" md="3">
                  <div class="text-caption text-grey-darken-1">個人其他案件已用</div>
                  <div class="text-subtitle-2 font-weight-bold">
                    NT$ {{ grantsStore.totalSubsidyAmount.toLocaleString() }}
                  </div>
                </v-col>
                <v-col cols="12" sm="6" md="3">
                  <div class="text-caption text-grey-darken-1">本案件規劃補助（含田間管路）</div>
                  <div class="text-subtitle-2 font-weight-bold text-primary">
                    NT$ {{ currentGrantTotalSubsidy.toLocaleString() }}
                  </div>
                </v-col>
                <v-col cols="12" sm="6" md="3">
                  <div class="text-caption text-grey-darken-1">剩餘可用額度</div>
                  <div class="text-subtitle-2 font-weight-bold">
                    NT$ {{ remainingSubsidyQuota.toLocaleString() }}
                  </div>
                </v-col>
              </v-row>
              <v-divider class="my-2" />
              <div class="text-caption">
                灌溉調控設施補助：NT$ {{ totalSubsidyAmount.toLocaleString() }} |
                田間管路補助：NT$ {{ step4SubsidyAmount.toLocaleString() }} |
                使用率：{{ quotaUsageRate }}%
              </div>
            </div>
          </v-alert>

          <v-table
            class="rounded border"
            density="compact"
          >
            <thead class="bg-grey-lighten-3">
              <tr>
                <th
                  class="text-center"
                >
                  NO.
                </th>
                <th style="width: 140px">
                  設施類型
                </th>
                <th style="width: 180px">
                  設施名稱
                </th>
                <th
                  class="text-center"
                  style="width: 130px"
                >
                  數量
                </th>
                <th
                  class="text-center"
                >
                  單價
                </th>
                <th style="width: 200px">
                  補助標準
                </th>
                <!-- <th style="width: 180px">
                  補助來源
                </th> -->
                <th
                  class="text-center"
                  style="width: 10px"
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
                    :rules="[
                      v => !!v || '請輸入數量',
                      v => v > 0 || '數量必須大於0'
                    ]"
                    @focus="saveFacilitySnapshot(index)"
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
                    :readonly="facility.type === 'power' || facility.type === 'storage'"
                    @focus="saveFacilitySnapshot(index)"
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
            class="my-4"
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
        </v-form>
      </v-card-text>
    </v-card>
  </div>
</template>

<script setup lang="ts">
import { useGrantsStore } from '@/stores/grants';
import { useOfficesStore } from '@/stores/offices';
import { calculateSubsidyAmount, determineRegionType, validateStorageFacility, getStorageCapacityLimit, calculateExistingStorageCapacity, getAvailableStorageCapacity, canAddStorageFacility as canAddStorageFacilityUtil, getControlSubsidyLimit, calculateControlFacilitiesAllocation } from '@/utils/subsidyStandards';
import { useRoute } from 'vue-router';

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

// Access grants store and route
const grantsStore = useGrantsStore();
const officesStore = useOfficesStore();
const route = useRoute();

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

  // 調節控制設施
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
    originalSubsidyPrice?: number; // 原始單位補助定價（動力設備、調蓄設施）
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

// 用於保存編輯前的狀態（額度檢查失敗時恢復）
const facilitySnapshot = ref<{
  quantity: number;
  unitPrice: number;
  totalPrice: number;
  subsidyAmount: number;
  selfPaidAmount: number;
} | null>(null);

// 🔥 防止遞歸更新的標誌位
const isRestoringSnapshot = ref(false);

// 補助來源編輯模式控制
const isEditingFundingSource = ref(false);

// 選項
const powerEquipmentOptions = [
  '馬達（含抽水機）',
  '柱塞式泵',
  '汽油引擎',
  '柴油引擎'
];

const storageTypeOptions = [
  '鋁合金',
  '不鏽鋼',
  '塑膠類'
];

// 動態噸數選項 - 根據已有容量和面積限制
const existingStorageCapacity = computed(() => {
  return calculateExistingStorageCapacity(localFormData.facilities);
});

const availableStorageCapacity = computed(() => {
  const area = facilityArea.value > 0 ? facilityArea.value : 0.1; // 預設 0.1 公頃
  return getAvailableStorageCapacity(area, existingStorageCapacity.value);
});

const maxStorageCapacity = computed(() => {
  const area = facilityArea.value > 0 ? facilityArea.value : 0.1; // 預設 0.1 公頃
  return getStorageCapacityLimit(area);
});

const tonnageOptions = computed(() => {
  const allTonnages = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100];

  return allTonnages
    .filter(tonnage => {
      const area = facilityArea.value > 0 ? facilityArea.value : 0.1;
      return canAddStorageFacilityUtil(area, existingStorageCapacity.value, tonnage, 1);
    })
    .map(tonnage => tonnage.toString());
});

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

// 資料來源選擇器，參照 step6 的安全機制
const getStepDataSafely = (step: number) => {
  const currentCaseNumber = route.query.id as string;

  // 確保只處理當前案件的資料
  if (!currentCaseNumber || grantsStore.caseNumber !== currentCaseNumber) {
    return null;
  }

  const formData = grantsStore.formData[step];
  const allStepsData = (grantsStore.currentGrant?.active_version as any)?.all_steps_data?.steps?.[step.toString()];

  // 檢查 formData 是否屬於當前案件（透過 _caseNumber 欄位比對）
  const formDataCaseNumber = formData?._caseNumber;
  const isFormDataValid = formDataCaseNumber === currentCaseNumber;

  if (isFormDataValid && formData && Object.keys(formData).length > 1) { // >1 因為至少有 _caseNumber
    console.log(`✅ Step3: Using formData for step ${step} (case: ${formDataCaseNumber})`);
    return formData; // 使用 formData（即時同步）
  }

  // 使用 all_steps_data 作為備用資料源
  console.log(`⚡ Step3: Using all_steps_data for step ${step} (formData invalid or empty)`);
  return (allStepsData && Object.keys(allStepsData).length > 0) ? allStepsData : null;
};

// 消除多重資料源，統一計算邏輯
const regionType = computed(() => {
  const step2Data = getStepDataSafely(2) || {};
  // 修復：從 lands 陣列中判斷原民地區
  const isAboriginalArea = step2Data.lands?.some((land: any) => land.isAboriginalArea) ||
                          step2Data.isAboriginalArea || false;
  console.log('[Step3] 地區類型計算 - isAboriginalArea:', isAboriginalArea);
  return determineRegionType(isAboriginalArea);
});

// 使用安全資料來源，消除reload問題
const facilityArea = computed(() => {
  const step2Data = getStepDataSafely(2) || {};

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
  // DEBUG: 如果都沒有，提供診斷資訊
  else {
    console.warn('[Step3] 無法取得step2面積資料，檢查資料狀態:', {
      'step2Data': step2Data,
      'currentCase': route.query.id,
      'grantsStoreCase': grantsStore.caseNumber,
      'currentGrant': grantsStore.currentGrant?.case_number
    });
  }

  // 轉換為公頃
  const areaHa = totalArea / 10000;
  console.log('[Step3] 設施面積計算完成 - 總面積:', totalArea, 'm², 公頃:', areaHa);
  return areaHa;
});

// 調節控制設施整體性補助分配
const controlFacilitiesAllocation = computed(() => {
  const area = facilityArea.value > 0 ? facilityArea.value : 0.1;
  const controlFacilities = localFormData.facilities.filter(facility => facility.type === 'control');

  if (controlFacilities.length === 0) return [];

  // 🔥 計算個人年度可用補助額度
  let userAvailableSubsidy: number | undefined = undefined;

  if (grantsStore.hasSubsidySummary) {
    const nonControlSubsidy = localFormData.facilities
      .filter(f => f.type !== 'control')
      .reduce((sum, f) => sum + (f.subsidyAmount || 0), 0);

    const step4Subsidy = step4SubsidyAmount.value;

    userAvailableSubsidy = grantsStore.subsidyLimit
      - grantsStore.totalSubsidyAmount
      - step4Subsidy
      - nonControlSubsidy;
  }

  return calculateControlFacilitiesAllocation(area, regionType.value, controlFacilities, userAvailableSubsidy);
});

const totalControlSubsidyLimit = computed(() => {
  const area = facilityArea.value > 0 ? facilityArea.value : 0.1;

  // 🔥 計算個人年度可用補助額度
  let userAvailableSubsidy: number | undefined = undefined;

  if (grantsStore.hasSubsidySummary) {
    const nonControlSubsidy = localFormData.facilities
      .filter(f => f.type !== 'control')
      .reduce((sum, f) => sum + (f.subsidyAmount || 0), 0);

    const step4Subsidy = step4SubsidyAmount.value;

    userAvailableSubsidy = grantsStore.subsidyLimit
      - grantsStore.totalSubsidyAmount
      - step4Subsidy
      - nonControlSubsidy;
  }

  return getControlSubsidyLimit(area, regionType.value, userAvailableSubsidy);
});

const totalControlSubsidy = computed(() => {
  return controlFacilitiesAllocation.value.reduce((sum, allocation) => sum + allocation.subsidyAmount, 0);
});

const availableControlSubsidy = computed(() => {
  return Math.max(0, totalControlSubsidyLimit.value - totalControlSubsidy.value);
});

const overallControlSubsidyRatio = computed(() => {
  // 統一從 localFormData.facilities 計算，與 totalSubsidyAmount/totalSelfPaidAmount 一致
  const controlFacilities = localFormData.facilities.filter(f => f.type === 'control');
  const totalCost = controlFacilities.reduce((sum, f) => sum + (f.totalPrice || 0), 0);
  const totalSubsidy = controlFacilities.reduce((sum, f) => sum + (f.subsidyAmount || 0), 0);

  if (totalCost === 0) return 0;
  return totalSubsidy / totalCost;
});

// 簡單直接的補助計算 - 總成本與剩餘額度取最小值
const controlActualSubsidyAmount = computed(() => {
  if (!localFormData.controlType) return 0;

  const unitPrice = parseFloat(localFormData.controlUnitPrice as any) || 0;
  const quantity = parseFloat(localFormData.controlQuantity as any) || 1;
  const totalCost = unitPrice * quantity;

  // 剩餘額度 = 總額度 - 已使用
  const remaining = availableControlSubsidy.value;

  // 總成本 <= 剩餘額度 → 全額補助；總成本 > 剩餘額度 → 補助到上限
  return Math.min(totalCost, remaining);
});

const controlSelfPaidAmount = computed(() => {
  const unitPrice = parseFloat(localFormData.controlUnitPrice as any) || 0;
  const quantity = parseFloat(localFormData.controlQuantity as any) || 1;
  const totalCost = unitPrice * quantity;

  // 自備款 = 總成本 - 補助款
  return totalCost - controlActualSubsidyAmount.value;
});

// 統一金額統計計算邏輯
const totalSubsidyAmount = computed(() => {
  return localFormData.facilities.reduce((total, facility) => {
    // 所有設施類型統一使用 subsidyAmount
    return total + (facility.subsidyAmount || 0);
  }, 0);
});

const totalSelfPaidAmount = computed(() => {
  return localFormData.facilities.reduce((total, facility) => {
    // 所有設施類型統一使用 selfPaidAmount
    return total + (facility.selfPaidAmount || 0);
  }, 0);
});

const facilitiesWithSelfPaid = computed(() => {
  return localFormData.facilities.filter(facility =>
    (facility.selfPaidAmount || 0) > 0
  ).length;
});

// 個人年度補助額度計算
const step4SubsidyAmount = computed(() => {
  const step4Data = getStepDataSafely(4) || {};
  return parseFloat(step4Data.subsidyAmount) || 0;
});

const currentGrantTotalSubsidy = computed(() => {
  return totalSubsidyAmount.value + step4SubsidyAmount.value;
});

const remainingSubsidyQuota = computed(() => {
  if (!grantsStore.hasSubsidySummary) return 0;
  const estimatedTotal = grantsStore.totalSubsidyAmount + currentGrantTotalSubsidy.value;
  return grantsStore.subsidyLimit - estimatedTotal;
});

const quotaUsageRate = computed(() => {
  if (!grantsStore.hasSubsidySummary || grantsStore.subsidyLimit === 0) return '0.0';
  const estimatedTotal = grantsStore.totalSubsidyAmount + currentGrantTotalSubsidy.value;
  const rate = (estimatedTotal / grantsStore.subsidyLimit) * 100;
  return rate.toFixed(1);
});

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

const onPowerEquipmentChange = () => {
  updateFormData();
};

const onStorageTypeChange = () => {
  updateFormData();
};

// 不同設施類型使用不同邏輯
// 動力設備 - 直接使用補助款作為單價，無自備款
const addPowerEquipment = () => {
  if (canAddPowerEquipment.value) {
    const correctSubsidy = calculateSubsidyAmount('power', localFormData.powerEquipment, regionType.value, 1);

    // 個人年度補助額度查驗
    if (grantsStore.hasSubsidySummary) {
      // Step3 加入新設施後的總額
      const step3TotalAfterAdd = totalSubsidyAmount.value + correctSubsidy;

      // 取得 step4（田間管路）的補助
      const step4Data = getStepDataSafely(4) || {};
      const step4Subsidy = parseFloat(step4Data.subsidyAmount) || 0;
      console.log('📊 [addPowerEquipment] step4 資料:', {
        'step4Data': step4Data,
        'subsidyAmount原始值': step4Data.subsidyAmount,
        'step4Subsidy解析值': step4Subsidy
      });

      // 本案件總補助 = step3 + step4
      const thisGrantTotal = step3TotalAfterAdd + step4Subsidy;

      // 總使用額 = 其他案件 + 本案件
      const estimatedTotal = grantsStore.totalSubsidyAmount + thisGrantTotal;
      const remaining = grantsStore.subsidyLimit - estimatedTotal;

      console.log('💰 [addPowerEquipment] 補助額度驗算:', {
        '新增設施補助': correctSubsidy,
        'step3加入後總額': step3TotalAfterAdd,
        'step4補助': step4Subsidy,
        '本案件總補助': thisGrantTotal,
        '其他案件已用': grantsStore.totalSubsidyAmount,
        '預估總使用': estimatedTotal,
        '年度上限': grantsStore.subsidyLimit,
        '剩餘額度': remaining
      });

      if (remaining < 0) {
        alert(
          `個人年度補助額度不足！\n\n` +
          `欲新增設施補助：NT$ ${correctSubsidy.toLocaleString()}\n` +
          `灌溉調控設施預估補助總額：NT$ ${step3TotalAfterAdd.toLocaleString()}\n` +
          `本案件總補助（含田間管路）：NT$ ${thisGrantTotal.toLocaleString()}\n` +
          `其他案件已用額度：NT$ ${grantsStore.totalSubsidyAmount.toLocaleString()}\n` +
          `預估總使用：NT$ ${estimatedTotal.toLocaleString()}\n` +
          `個人年度上限：NT$ ${grantsStore.subsidyLimit.toLocaleString()}\n` +
          `超出金額：NT$ ${Math.abs(remaining).toLocaleString()}\n\n` +
          `無法加入此設施，請調整申請內容！`
        );
        return;
      // } else if (remaining < 100000) {
      //   const confirmAdd = confirm(
      //     `⚠️ 年度補助額度即將不足！\n\n` +
      //     `本次新增設施補助：NT$ ${correctSubsidy.toLocaleString()}\n` +
      //     `加入後剩餘額度：NT$ ${remaining.toLocaleString()}\n\n` +
      //     `是否確定要加入此設施？`
      //   );
      //   if (!confirmAdd) return;
      }
    }

    localFormData.facilities.push({
      type: 'power',
      typeLabel: '動力設備',
      name: localFormData.powerEquipment,
      quantity: 1,
      originalSubsidyPrice: correctSubsidy, // 保存原始單位補助定價
      unitPrice: correctSubsidy,            // 初始單價 = 補助定價
      totalPrice: correctSubsidy,           // 初始總價 = 補助定價
      subsidyAmount: correctSubsidy,        // 初始補助總額 = 補助定價
      selfPaidAmount: 0,                    // 初始自備款 = 0
      remark: `[${regionType.value === 'indigenous' ? '原民區域' : '一般地區'}]`,
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
    const area = facilityArea.value > 0 ? facilityArea.value : 0.1;

    // 先檢查容量限制
    if (!canAddStorageFacilityUtil(area, existingStorageCapacity.value, tonnage, 1)) {
      const maxCap = maxStorageCapacity.value;
      const existing = existingStorageCapacity.value;
      const available = availableStorageCapacity.value;

      alert(`無法加入 ${tonnage} 噸調蓄設施！\n\n` +
            `面積限制：${area.toFixed(4)} 公頃 → 最大容量 ${maxCap} 噸\n` +
            `已申請容量：${existing} 噸\n` +
            `剩餘可申請：${available} 噸\n` +
            `嘗試加入：${tonnage} 噸`);
      return;
    }

    // 驗證設施參數
    if (!validateStorageFacility(localFormData.storageType, tonnage, area)) {
      alert('調蓄設施參數不符合補助標準（材料、噸數或面積不符）');
      return;
    }

    const correctSubsidy = calculateSubsidyAmount('storage', equipment, regionType.value, 1, tonnage);

    if (correctSubsidy === 0) {
      alert('無法計算補助金額，請確認設施參數是否正確');
      return;
    }

    // 年度補助額度查驗
    if (grantsStore.hasSubsidySummary) {
      // Step3 加入新設施後的總額
      const step3TotalAfterAdd = totalSubsidyAmount.value + correctSubsidy;

      // 取得 step4（田間管路）的補助
      const step4Data = getStepDataSafely(4) || {};
      const step4Subsidy = parseFloat(step4Data.subsidyAmount) || 0;
      console.log('📊 [addStorageFacility] step4 資料:', {
        'step4Data': step4Data,
        'subsidyAmount原始值': step4Data.subsidyAmount,
        'step4Subsidy解析值': step4Subsidy
      });

      // 本案件總補助 = step3 + step4
      const thisGrantTotal = step3TotalAfterAdd + step4Subsidy;

      // 總使用額 = 其他案件 + 本案件
      const estimatedTotal = grantsStore.totalSubsidyAmount + thisGrantTotal;
      const remaining = grantsStore.subsidyLimit - estimatedTotal;

      console.log('💰 [addStorageFacility] 補助額度驗算:', {
        '新增設施補助': correctSubsidy,
        'step3加入後總額': step3TotalAfterAdd,
        'step4補助': step4Subsidy,
        '本案件總補助': thisGrantTotal,
        '其他案件已用': grantsStore.totalSubsidyAmount,
        '預估總使用': estimatedTotal,
        '年度上限': grantsStore.subsidyLimit,
        '剩餘額度': remaining
      });

      if (remaining < 0) {
        alert(
          `⚠️ 年度補助額度不足！\n\n` +
          `欲新增設施補助：NT$ ${correctSubsidy.toLocaleString()}\n` +
          `灌溉調控設施預估補助總額：NT$ ${step3TotalAfterAdd.toLocaleString()}\n` +
          `本案件總補助（含田間管路）：NT$ ${thisGrantTotal.toLocaleString()}\n` +
          `其他案件已用額度：NT$ ${grantsStore.totalSubsidyAmount.toLocaleString()}\n` +
          `預估總使用：NT$ ${estimatedTotal.toLocaleString()}\n` +
          `年度上限：NT$ ${grantsStore.subsidyLimit.toLocaleString()}\n` +
          `超出金額：NT$ ${Math.abs(remaining).toLocaleString()}\n\n` +
          `無法加入此設施，請調整申請內容！`
        );
        return;
      // } else if (remaining < 100000) {
      //   const confirmAdd = confirm(
      //     `⚠️ 年度補助額度即將不足！\n\n` +
      //     `本次新增設施補助：NT$ ${correctSubsidy.toLocaleString()}\n` +
      //     `加入後剩餘額度：NT$ ${remaining.toLocaleString()}\n\n` +
      //     `是否確定要加入此設施？`
      //   );
      //   if (!confirmAdd) return;
      }
    }

    localFormData.facilities.push({
      type: 'storage',
      typeLabel: '調蓄設施',
      name: equipment,
      quantity: 1,
      originalSubsidyPrice: correctSubsidy, // 保存原始單位補助定價
      unitPrice: correctSubsidy,            // 初始單價 = 補助定價
      totalPrice: correctSubsidy,           // 初始總價 = 補助定價
      subsidyAmount: correctSubsidy,        // 初始補助總額 = 補助定價
      selfPaidAmount: 0,                    // 初始自備款 = 0
      remark: `${localFormData.storageRemark || ''} [${regionType.value === 'indigenous' ? '原民區域' : '一般地區'}]`,
      fundingSourceId: localFormData.fundingSourceId !== null && localFormData.fundingSourceId !== undefined ? localFormData.fundingSourceId : '未選擇補助來源'
    });

    // 清空選擇
    localFormData.storageType = '';
    localFormData.storageTonnage = '';
    localFormData.storageRemark = '';

    updateFormData();
  }
};

// 使用整體分配邏輯的調節控制設施新增
const addControlFacility = () => {
  if (canAddControlFacility.value) {
    const quantity = parseFloat(localFormData.controlQuantity as any) || 1;
    const unitPrice = parseFloat(localFormData.controlUnitPrice as any) || 0;
    const totalCost = unitPrice * quantity;

    console.log(`[調節控制設施] 新增設施 - 單價:${unitPrice}, 數量:${quantity}, 總成本:${totalCost}`);

    // 年度補助額度查驗（僅用於顯示信息，不阻止加入）
    // 超過額度的部分會自動轉為自備款，不需要阻止加入
    if (grantsStore.hasSubsidySummary) {
      const area = facilityArea.value > 0 ? facilityArea.value : 0.1;
      const currentControlFacilities = localFormData.facilities.filter(f => f.type === 'control');

      // 計算個人年度可用補助額度
      const nonControlSubsidy = localFormData.facilities
        .filter(f => f.type !== 'control')
        .reduce((sum, f) => sum + (f.subsidyAmount || 0), 0);

      const step4Subsidy = step4SubsidyAmount.value;

      const userAvailableSubsidy = grantsStore.subsidyLimit
        - grantsStore.totalSubsidyAmount
        - step4Subsidy
        - nonControlSubsidy;

      // 模擬新增設施
      const simulatedFacilities = [
        ...currentControlFacilities,
        {
          type: 'control',
          name: localFormData.controlName,
          quantity: quantity,
          unitPrice: unitPrice,
          totalPrice: totalCost,
          subsidyAmount: 0,
          selfPaidAmount: totalCost
        }
      ];

      // 傳入個人年度可用額度進行模擬計算
      const allocations = calculateControlFacilitiesAllocation(area, regionType.value, simulatedFacilities, userAvailableSubsidy);
      const newControlSubsidy = allocations.reduce((sum, allocation) => sum + allocation.subsidyAmount, 0);
      const newControlSelfPaid = allocations.reduce((sum, allocation) => sum + allocation.selfPaidAmount, 0);

      // Step3 總補助
      const step3TotalSubsidy = newControlSubsidy + nonControlSubsidy;

      // 本案件總補助 = step3 + step4
      const thisGrantTotal = step3TotalSubsidy + step4Subsidy;

      // 總使用額 = 其他案件 + 本案件
      const estimatedTotal = grantsStore.totalSubsidyAmount + thisGrantTotal;
      const remaining = grantsStore.subsidyLimit - estimatedTotal;

      console.log('💰 [addControlFacility] 補助額度驗算:', {
        '個人年度可用': userAvailableSubsidy,
        '調節控制設施補助': newControlSubsidy,
        '調節控制設施自備': newControlSelfPaid,
        '非控制設施補助': nonControlSubsidy,
        'step3總補助': step3TotalSubsidy,
        'step4補助': step4Subsidy,
        '本案件總補助': thisGrantTotal,
        '其他案件已用': grantsStore.totalSubsidyAmount,
        '預估總使用': estimatedTotal,
        '年度上限': grantsStore.subsidyLimit,
        '剩餘額度': remaining
      });
    }

    // 先加入設施（補助金額暫時設為0，稍後重新分配）
    localFormData.facilities.push({
      type: 'control',
      typeLabel: '調節控制設施',
      name: localFormData.controlName,
      quantity: quantity,
      unitPrice: unitPrice,
      totalPrice: totalCost,
      subsidyAmount: 0, // 稍後重新分配
      selfPaidAmount: totalCost, // 稍後重新分配
      remark: `[${regionType.value === 'indigenous' ? '原民區域' : '一般地區'}] 設施面積: ${formatArea(facilityArea.value)}公頃`,
      fundingSourceId: localFormData.fundingSourceId !== null && localFormData.fundingSourceId !== undefined ? localFormData.fundingSourceId : '未選擇補助來源'
    });

    // 重新分配所有調節控制設施的補助金額
    nextTick(() => {
      reallocateControlSubsidies();
    });

    // 清空選擇
    localFormData.controlType = '';
    localFormData.controlName = '';
    localFormData.controlUnitPrice = '';

    updateFormData();
  }
};

// 保存設施快照（在用戶開始編輯前）
const saveFacilitySnapshot = (index: number) => {
  const facility = localFormData.facilities[index];
  facilitySnapshot.value = {
    quantity: facility.quantity,
    unitPrice: facility.unitPrice,
    totalPrice: facility.totalPrice || 0,
    subsidyAmount: facility.subsidyAmount || 0,
    selfPaidAmount: facility.selfPaidAmount || 0
  };
  console.log(`[快照保存] 設施 ${index} - 數量:${facility.quantity}, 單價:${facility.unitPrice}`);
};

// 統一的年度補助額度檢查函數
const checkSubsidyLimit = (operation: string, newStep3Subsidy: number): { allowed: boolean; remaining: number } => {
  if (!grantsStore.hasSubsidySummary) {
    return { allowed: true, remaining: Infinity };
  }

  // 取得 step4（田間管路）的補助
  const step4Data = getStepDataSafely(4) || {};
  const step4Subsidy = parseFloat(step4Data.subsidyAmount) || 0;

  // 本案件總補助 = step3 + step4
  const thisGrantTotal = newStep3Subsidy + step4Subsidy;

  // 總使用額 = 其他案件 + 本案件
  const estimatedTotal = grantsStore.totalSubsidyAmount + thisGrantTotal;
  const remaining = grantsStore.subsidyLimit - estimatedTotal;

  console.log(`💰 [${operation}] 補助額度驗算:`, {
    'step3補助': newStep3Subsidy,
    'step4補助': step4Subsidy,
    '本案件總補助': thisGrantTotal,
    '其他案件已用': grantsStore.totalSubsidyAmount,
    '預估總使用': estimatedTotal,
    '年度上限': grantsStore.subsidyLimit,
    '剩餘額度': remaining
  });

  if (remaining < 0) {
    alert(
      `⚠️ 個人年度補助額度不足！\n\n` +
      `操作：${operation}\n` +
      `灌溉調控設施預估補助總額：NT$ ${newStep3Subsidy.toLocaleString()}\n` +
      `本案件總補助（含田間管路）：NT$ ${thisGrantTotal.toLocaleString()}\n` +
      `其他案件已用額度：NT$ ${grantsStore.totalSubsidyAmount.toLocaleString()}\n` +
      `預估總使用：NT$ ${estimatedTotal.toLocaleString()}\n` +
      `年度上限：NT$ ${grantsStore.subsidyLimit.toLocaleString()}\n` +
      `超出金額：NT$ ${Math.abs(remaining).toLocaleString()}\n\n` +
      `無法完成此操作，請調整申請內容！`
    );
    return { allowed: false, remaining };
  // } else if (remaining < 100000) {
  //   const confirmOperation = confirm(
  //     `⚠️ 年度補助額度即將不足！\n\n` +
  //     `操作：${operation}\n` +
  //     `本步驟補助：NT$ ${newStep3Subsidy.toLocaleString()}\n` +
  //     `完成後剩餘額度：NT$ ${remaining.toLocaleString()}\n\n` +
  //     `是否確定要執行此操作？`
  //   );
  //   return { allowed: confirmOperation, remaining };
  }

  return { allowed: true, remaining };
};

// 移除設施
const removeFacility = (index: number) => {
  // const facility = localFormData.facilities[index];

  localFormData.facilities.splice(index, 1);

  // 🔥 Good Taste: 任何設施刪除都可能釋出個人年度補助額度
  // 需要檢查是否有調節控制設施需要重新分配
  const hasControlFacilities = localFormData.facilities.some(f => f.type === 'control');

  if (hasControlFacilities) {
    // 有調節控制設施：重新分配（可能有更多額度可用）
    nextTick(() => {
      reallocateControlSubsidies();
      // reallocateControlSubsidies 內部已經調用 updateFormData()
    });
  } else {
    // 沒有調節控制設施：直接更新
    updateFormData();
  }
};

// 更新設施的總價
const updateFacilityTotal = (index: number) => {
  // 防止遞歸更新：如果正在恢復快照，直接返回
  if (isRestoringSnapshot.value) {
    console.log(`[updateFacilityTotal] 正在恢復快照，跳過更新`);
    return;
  }

  const facility = localFormData.facilities[index];

  // 從快照獲取舊值（如果沒有快照，則使用當前值）
  const oldQuantity = facilitySnapshot.value?.quantity ?? facility.quantity;
  const oldUnitPrice = facilitySnapshot.value?.unitPrice ?? facility.unitPrice;

  const newQuantity = parseFloat(facility.quantity.toString()) || 0;
  const unitPrice = parseFloat(facility.unitPrice.toString()) || 0;

  console.log(`[updateFacilityTotal] 設施 ${index} - 舊數量:${oldQuantity}, 新數量:${newQuantity}, 舊單價:${oldUnitPrice}, 新單價:${unitPrice}`);

  // 調蓄設施需要檢查容量限制
  if (facility.type === 'storage') {
    const tonnageMatch = facility.name.match(/-(\d+)噸/);
    if (tonnageMatch) {
      const tonnage = parseInt(tonnageMatch[1], 10);
      const area = facilityArea.value > 0 ? facilityArea.value : 0.1;

      // 計算其他調蓄設施的總容量（排除當前正在編輯的設施）
      const otherFacilities = localFormData.facilities.filter((_, i) => i !== index);
      const otherStorageCapacity = calculateExistingStorageCapacity(otherFacilities);

      // 檢查新數量是否會超過容量限制
      if (!canAddStorageFacilityUtil(area, otherStorageCapacity, tonnage, newQuantity)) {
        const maxCap = maxStorageCapacity.value;
        const available = getAvailableStorageCapacity(area, otherStorageCapacity);
        const maxAllowedQuantity = Math.floor(available / tonnage);

        alert(`調蓄設施數量超過容量限制！\n\n` +
              `面積限制：${area.toFixed(4)} 公頃 → 最大補助容量 ${maxCap} 噸\n` +
              `${tonnage} 噸設施最多可申請 ${maxAllowedQuantity} 個\n` +
              `其他設施已用：${otherStorageCapacity} 噸\n`);

        // 恢復為原始數量（使用快照）
        if (facilitySnapshot.value) {
          isRestoringSnapshot.value = true;
          facility.quantity = facilitySnapshot.value.quantity;
          nextTick(() => {
            isRestoringSnapshot.value = false;
          });
        }
        facilitySnapshot.value = null;
        return;
      }
    }
  }

  // 重新計算總價並更新
  facility.totalPrice = newQuantity * unitPrice;

  // 定價補助設施（動力設備、調蓄設施）：計算自備款差額
  if (facility.type === 'power' || facility.type === 'storage') {
    if (!facility.originalSubsidyPrice) {
      console.error(`[updateFacilityTotal] 設施缺少 originalSubsidyPrice:`, facility);
      alert('錯誤：設施資料不完整，缺少原始補助定價。請重新加入此設施。');

      // 恢復原始值
      if (facilitySnapshot.value) {
        isRestoringSnapshot.value = true;
        facility.quantity = facilitySnapshot.value.quantity;
        facility.unitPrice = facilitySnapshot.value.unitPrice;
        nextTick(() => {
          isRestoringSnapshot.value = false;
        });
      }
      facilitySnapshot.value = null;
      return;
    }

    // 原始補助總額 = 原始單位補助定價 × 數量
    const originalSubsidyTotal = facility.originalSubsidyPrice * newQuantity;

    // 補助金額 = min(原始補助總額, 實際總價)
    // 如果調低單價，補助款不能超過實際花費
    facility.subsidyAmount = Math.min(originalSubsidyTotal, facility.totalPrice);

    // 自備款 = max(0, 實際總價 - 補助金額)
    facility.selfPaidAmount = Math.max(0, facility.totalPrice - facility.subsidyAmount);

    console.log(`[updateFacilityTotal] ${facility.typeLabel} - 數量:${newQuantity}, 單價:${unitPrice}, 總價:${facility.totalPrice}, 原始補助:${originalSubsidyTotal}, 實際補助:${facility.subsidyAmount}, 自備:${facility.selfPaidAmount}`);
  }

  // 年度補助額度檢查
  // 只對定價補助設施（動力、調蓄）檢查
  // 調節控制設施超額部分會自動轉為自備款，不需要檢查
  if (facility.type === 'power' || facility.type === 'storage') {
    const limitCheck = checkSubsidyLimit(
      `調整${facility.typeLabel} (數量: ${oldQuantity} → ${newQuantity}, 單價: ${oldUnitPrice} → ${unitPrice})`,
      totalSubsidyAmount.value
    );

    if (!limitCheck.allowed) {
      // 恢復快照中的原始值
      if (facilitySnapshot.value) {
        console.log(`[額度檢查失敗] 開始恢復設施 ${index} 的原始值`);

        // 設置恢復標誌，防止觸發遞歸更新
        isRestoringSnapshot.value = true;

        facility.quantity = facilitySnapshot.value.quantity;
        facility.unitPrice = facilitySnapshot.value.unitPrice;
        facility.totalPrice = facilitySnapshot.value.totalPrice;
        facility.subsidyAmount = facilitySnapshot.value.subsidyAmount;
        facility.selfPaidAmount = facilitySnapshot.value.selfPaidAmount;

        // 使用 nextTick 確保 DOM 更新完成後再清除標誌
        nextTick(() => {
          isRestoringSnapshot.value = false;
          console.log(`[額度檢查失敗] 已完成恢復設施 ${index}，值：數量=${facility.quantity}, 單價=${facility.unitPrice}`);
        });
      }
      // 清除快照
      facilitySnapshot.value = null;
      return;
    }
  }

  // 調節控制設施修改後需要重新分配所有設施的補助金額
  if (facility.type === 'control') {
    // 延遲重新分配，確保資料更新完成
    nextTick(() => {
      reallocateControlSubsidies();
    });
  }

  // 更新快照為當前成功的值（支持連續修改）
  // 這樣下次修改失敗時，能恢復到上次成功的值而不是最初的值
  facilitySnapshot.value = {
    quantity: facility.quantity,
    unitPrice: facility.unitPrice,
    totalPrice: facility.totalPrice,
    subsidyAmount: facility.subsidyAmount || 0,
    selfPaidAmount: facility.selfPaidAmount || 0
  };
  console.log(`[快照更新] 設施 ${index} 更新成功，保存新快照 - 數量:${facility.quantity}, 單價:${facility.unitPrice}`);

  // 更新父組件資料
  updateFormData();
};

// 重新分配所有調節控制設施的補助金額
const reallocateControlSubsidies = () => {
  const area = facilityArea.value > 0 ? facilityArea.value : 0.1;
  const controlFacilities = localFormData.facilities.filter(facility => facility.type === 'control');

  // 即使沒有調節控制設施，也要調用 updateFormData 確保 UI 更新
  if (controlFacilities.length === 0) {
    updateFormData();
    return;
  }

  // 計算個人年度可用補助額度（考慮兩層限制）
  let userAvailableSubsidy: number | undefined = undefined;

  if (grantsStore.hasSubsidySummary) {
    // 1. 計算非調節控制設施的補助總額
    const nonControlSubsidy = localFormData.facilities
      .filter(f => f.type !== 'control')
      .reduce((sum, f) => sum + (f.subsidyAmount || 0), 0);

    // 2. 取得 step4 的補助額
    const step4Subsidy = step4SubsidyAmount.value;

    // 3. 計算個人年度可用額度 = 總上限 - 其他案件已用 - step4 - 非調節控制設施
    userAvailableSubsidy = grantsStore.subsidyLimit
      - grantsStore.totalSubsidyAmount
      - step4Subsidy
      - nonControlSubsidy;

    console.log(`[重新分配] 個人年度上限:${grantsStore.subsidyLimit}, 其他案件已用:${grantsStore.totalSubsidyAmount}, step4:${step4Subsidy}, 非控制設施:${nonControlSubsidy}, 可用於調節控制:${userAvailableSubsidy}`);
  }

  // 獲取新的分配結果（傳入個人年度可用額度）
  const allocations = calculateControlFacilitiesAllocation(area, regionType.value, controlFacilities, userAvailableSubsidy);

  // 更新每個調節控制設施的補助金額和自備款
  let controlIndex = 0;
  localFormData.facilities.forEach((facility, index) => {
    if (facility.type === 'control') {
      const allocation = allocations[controlIndex];
      if (allocation) {
        facility.subsidyAmount = allocation.subsidyAmount;
        facility.selfPaidAmount = allocation.selfPaidAmount;

        console.log(`[調節控制設施重新分配] 設施${controlIndex + 1}: 成本${allocation.totalCost}, 補助${allocation.subsidyAmount}, 自備${allocation.selfPaidAmount}, 比例${(allocation.subsidyRatio * 100).toFixed(1)}%`);
      }
      controlIndex++;
    }
  });

  // 更新父組件資料
  updateFormData();
};

const formatArea = (area: number): string => {
  if (!area && area !== 0) return '0.0000';
  return Number(area).toFixed(4);
};

const getFundingSourceName = (fundingSourceId: string | number): string => {
  // 使用嚴格比較，避免 0 被判斷為 falsy
  if (fundingSourceId === null || fundingSourceId === undefined || fundingSourceId === '未選擇補助來源') {
    return '未選擇補助來源';
  }

  const source = fundingSourceOptions.value.find(option => option.id === fundingSourceId);
  // 統一處理：找不到補助來源或 id 為 0（預設值）都視為未選擇
  return source ? source.name : '未選擇補助來源';
};


// 更新父組件數據
const updateFormData = () => {
  emit('update:formData', {
    ...props.formData,
    ...localFormData,
    valid: true // Always true for seamless navigation
  });
};

// 跳過灌溉調控設施步驟功能
const skipStep = () => {
  console.log('⏭️ Skipping step3 (灌溉調控設施)');

  // 重置所有表單數據為初始狀態
  Object.assign(localFormData, {
    fundingSourceId: 0,

    // 動力設備
    powerEquipment: '',

    // 調蓄設施
    storageType: '',
    storageTonnage: '',
    storageSource: '',
    storageRemark: '',

    // 調節控制設施
    controlType: '',
    controlName: '',
    controlQuantity: 1,
    controlUnitPrice: '',
    controlSource: '',

    // 設施列表
    facilities: [],

    valid: true
  });

  // 關閉編輯模式
  isEditingFundingSource.value = false;

  // 設置為有效狀態，允許跳過
  localValid.value = true;

  // 更新父組件數據
  updateFormData();

  // 觸發 validated 事件，進入下一步
  emit('validated', {
    valid: true,
    step: props.currentStep
  });

  console.log('✅ Step3 skipped successfully');
};

const onControlTypeChange = () => {
  // 當選擇變化時，將調節控制設施類型的值自動帶入到設施名稱
  localFormData.controlName = localFormData.controlType;
  updateFormData();
};

// 初始化數據 及 step2 資料監聽
onMounted(async () => {
  console.log("Step 3 mounted, formData:", props.formData);

  // 參照 step6 的完整載入機制，確保資料正確性
  const caseNumberFromRoute = route.query.id as string;

  if (caseNumberFromRoute) {
    console.log('🔄 Step3: 載入案件資料...', caseNumberFromRoute);
    try {
      // 總是載入案件基本資料
      if (grantsStore.caseNumber !== caseNumberFromRoute) {
        await grantsStore.loadGrant(caseNumberFromRoute);
      }

      // 總是載入必要的步驟資料，確保相關資料正確載入
      await grantsStore.loadStepData(caseNumberFromRoute, 2); // step2: 土地資料（用於計算面積）
      await grantsStore.loadStepData(caseNumberFromRoute, 3); // step3: 本身的資料
      await grantsStore.loadStepData(caseNumberFromRoute, 4); // step4: 田間管路（用於補助額度驗算）

      console.log('✅ Step3: 案件資料載入完成 (step2, step3, step4)');
    } catch (error) {
      console.error('❌ Step3: 載入案件資料時發生錯誤:', error);
    }
  } else {
    console.warn('⚠️ Step3: URL 中沒有案件號，無法載入資料');
  }

  // Set form data from props (props.formData = grantsStore.formData[3])
  console.log('📊 [step3] props.formData:', props.formData);
  console.log('📊 [step3] props.formData.facilities:', props.formData?.facilities);

  if (props.formData) {
    // Set basic properties
    Object.keys(localFormData).forEach(key => {
      if (props.formData[key] !== undefined) {
        (localFormData as any)[key] = props.formData[key];
      }
    });

    // Ensure facilities array is properly set
    if (Array.isArray(props.formData.facilities)) {
      localFormData.facilities = [...props.formData.facilities];
      console.log('✅ [step3] 已複製 facilities 陣列，長度:', localFormData.facilities.length);
    } else {
      console.warn('⚠️ [step3] props.formData.facilities 不是陣列');
    }
  } else {
    console.warn('⚠️ [step3] props.formData 為空');
  }

  // UX 改進：根據設施列表狀態決定是否進入補助來源編輯模式
  // 必須在 facilities 設置完成後立即執行
  const facilitiesLength = localFormData.facilities.length;
  console.log('🔍 [step3] 檢查設施列表長度:', facilitiesLength);

  if (facilitiesLength === 0) {
    isEditingFundingSource.value = true;
    console.log('📝 [step3] 設施列表為空，自動進入補助來源編輯模式');
  } else {
    isEditingFundingSource.value = false;
    console.log('📝 [step3] 設施列表不為空 (長度:', facilitiesLength, ')，退出補助來源編輯模式');
  }

  // 初始記錄 step2 資料狀態
  logStep2DataStatus();

  // 💰 初始化補助額度查詢
  if (caseNumberFromRoute && grantsStore.currentGrant) {
    const applicantId = grantsStore.currentGrant.applicant_id;
    const year = grantsStore.currentGrant.year;
    const currentGrantId = grantsStore.currentGrant.id;

    if (applicantId && year) {
      console.log('💰 [step3] 初始化補助額度查詢:', {
        applicantId,
        year,
        currentGrantId
      });
      try {
        await grantsStore.fetchSubsidySummary(applicantId, year, currentGrantId);
        console.log('✅ [step3] 補助額度查詢完成');
      } catch (error) {
        console.error('❌ [step3] 補助額度查詢失敗:', error);
      }
    }
  }

  // Initial update to parent
  updateFormData();
});

// 簡化的診斷函數
const logStep2DataStatus = () => {
  const step2Data = getStepDataSafely(2);

  console.log('[Step3 診斷] Step2 資料狀態:');
  console.log('  - step2Data:', step2Data);
  console.log('  - 土地數量:', step2Data?.lands?.length || '單筆土地模式');
  console.log('  - 當前地區類型:', regionType.value);
  console.log('  - 當前設施面積（公頃）:', facilityArea.value);
};

// Watch for props changes and localStorage changes
watch(() => props.formData, (newData) => {
  if (newData) {
    Object.keys(localFormData).forEach(key => {
      if (key !== 'facilities' && newData[key] !== undefined &&
          JSON.stringify(newData[key]) !== JSON.stringify((localFormData as any)[key])) {
        (localFormData as any)[key] = newData[key];
      }
    });

    // Special handling for facilities array
    if (Array.isArray(newData.facilities) &&
        JSON.stringify(newData.facilities) !== JSON.stringify(localFormData.facilities)) {
      const oldLength = localFormData.facilities.length;
      localFormData.facilities = [...newData.facilities];
      const newLength = localFormData.facilities.length;

      console.log(`🔄 [step3] facilities 陣列更新: ${oldLength} -> ${newLength}`);

      // 🎯 UX 改進：當 facilities 從空變為有數據時，自動退出編輯模式
      if (oldLength === 0 && newLength > 0) {
        isEditingFundingSource.value = false;
        console.log('📝 [step3] facilities 從空變為有數據，自動退出編輯模式');
      } else if (oldLength > 0 && newLength === 0) {
        isEditingFundingSource.value = true;
        console.log('📝 [step3] facilities 從有數據變為空，自動進入編輯模式');
      }
    }
  }
}, { deep: true });

// 簡化：統一監聽 grantsStore 的變化即可
watch(() => grantsStore.formData[2], () => {
  console.log('[Step3] Step2 資料變化，重新計算補助標準');
  nextTick(() => {
    console.log('[Step3] 重新計算後 - 地區類型:', regionType.value, '設施面積（公頃）:', facilityArea.value);
    // 面積變化時重新分配調節控制設施補助
    reallocateControlSubsidies();
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
