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
              <li><strong>調節控制設施：</strong>僅在需要申請調節控制設施補助時填寫</li>
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

          <!-- 調節控制設施區域 -->
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
              <span class="text-subtitle-1 font-weight-medium">調節控制設施</span>
            </v-card-title>

            <v-card-text class="pa-4">
              <v-sheet
                class="pa-3 rounded"
                color="grey-lighten-5"
              >
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
                    label="單價"
                    prefix="$"
                    variant="outlined"
                    density="comfortable"
                    class="me-2 mb-2"
                    style="width: 120px"
                  />

                  <v-text-field
                    v-model="controlTotalPrice"
                    label="總價"
                    prefix="$"
                    variant="outlined"
                    density="comfortable"
                    class="me-2 mb-2"
                    style="width: 120px"
                    readonly
                    bg-color="grey-lighten-4"
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
                      style="width: 50px"
                    >
                      NO.
                    </th>
                    <th>設施類型</th>
                    <th>設施名稱</th>
                    <th class="text-center">
                      數量
                    </th>
                    <th class="text-center">
                      單價
                    </th>
                    <th class="text-center">
                      小計
                    </th>
                    <th>備註</th>
                    <th>補助來源</th>
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
                        style="width: 100px"
                        @update:model-value="updateFacilityTotal(index)"
                      />
                    </td>
                    <td
                      class="text-center"
                    >
                      {{ facility.totalPrice }}
                    </td>
                    <td>{{ facility.remark }}</td>
                    <td>{{ facility.source }}</td>
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
                      colspan="9"
                      class="text-center py-3 text-grey"
                    >
                      尚未新增任何設施，請使用上方各區塊的加入按鈕新增設施
                    </td>
                  </tr>
                </tbody>
              </v-table>
            </v-card-text>
          </v-card>
        </v-form>
      </v-card-text>
    </v-card>
  </div>
</template>

<script setup lang="ts">
import { useGrantsStore } from '@/stores/grants';
import { useOfficesStore } from '@/stores/offices'

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
// const grantsStore = useGrantsStore();
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
    unitPrice: number;
    totalPrice: number;
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

// 計算屬性
const controlTotalPrice = computed(() => {
  const quantity = parseFloat(localFormData.controlQuantity as any) || 0;
  const unitPrice = parseFloat(localFormData.controlUnitPrice as any) || 0;
  return (quantity * unitPrice).toString();
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

// 添加動力設備
const addPowerEquipment = () => {
  if (canAddPowerEquipment.value) {
    localFormData.facilities.push({
      type: 'power',
      typeLabel: '動力設備',
      name: localFormData.powerEquipment,
      quantity: 1,
      unitPrice: 4500, // 假設這是預設價格，實際上可能需要根據選擇動態獲取
      totalPrice: 4500,
      remark: '',
      fundingSourceId: localFormData.fundingSourceId || '未選擇補助來源'
    });

    // 清空選擇
    localFormData.powerEquipment = '';

    updateFormData();
  }
};

// 添加調蓄設施
const addStorageFacility = () => {
  if (canAddStorageFacility.value) {
    const tonnage = parseInt(localFormData.storageTonnage);
    // 假設價格根據噸數計算
    const unitPrice = tonnage * 1000;

    localFormData.facilities.push({
      type: 'storage',
      typeLabel: '調蓄設施',
      name: `${localFormData.storageType}-${localFormData.storageTonnage}噸`,
      quantity: 1,
      unitPrice: unitPrice,
      totalPrice: unitPrice,
      remark: localFormData.storageRemark || '',
      fundingSourceId: localFormData.fundingSourceId || '未選擇補助來源'
    });

    // 清空選擇
    localFormData.storageType = '';
    localFormData.storageTonnage = '';
    localFormData.storageRemark = '';

    updateFormData();
  }
};

// 添加調節控制設施
const addControlFacility = () => {
  if (canAddControlFacility.value) {
    const quantity = parseFloat(localFormData.controlQuantity as any);
    const unitPrice = parseFloat(localFormData.controlUnitPrice as any);

    localFormData.facilities.push({
      type: 'control',
      typeLabel: '調節控制設施',
      name: localFormData.controlName,
      quantity: quantity,
      unitPrice: unitPrice,
      totalPrice: quantity * unitPrice,
      remark: '',
      fundingSourceId: localFormData.fundingSourceId || '未選擇補助來源'
    });

    // 清空選擇，但保留數量
    localFormData.controlType = '';
    localFormData.controlName = '';
    localFormData.controlSource = '';

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

// 添加在 script 區塊頂部的工具函數
const formatPrice = (value) => {
  if (!value && value !== 0) return '';
  return Number(value).toLocaleString();
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
  // 當選擇變化時，將調節控制設施類型的值自動帶入到設施名稱
  localFormData.controlName = localFormData.controlType;
  updateFormData();
};

// 初始化數據
onMounted(() => {
  console.log("Step 3 mounted, formData:", props.formData);

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

  // Initial update to parent
  updateFormData();
});

// Watch for props changes
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
