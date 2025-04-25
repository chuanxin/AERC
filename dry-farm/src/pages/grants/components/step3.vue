<template>
  <div class="step-content" ref="stepContent">
    <v-card class="mb-6 pa-0" flat>
      <v-card-text class="pb-0 pt-0">
        <v-form ref="form" v-model="localValid" @submit.prevent>
          <!-- 動力設備選擇區域 -->
          <v-card class="mb-4" variant="outlined">
            <v-card-title class="bg-light-blue-lighten-4 d-flex align-center py-2 px-4">
              <v-icon class="me-2" size="small">mdi-engine</v-icon>
              <span class="text-subtitle-1 font-weight-medium">動力設備</span>
            </v-card-title>

            <v-card-text class="pa-4">
              <v-sheet class="pa-3 rounded" color="grey-lighten-5">
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
                  ></v-select>

                  <v-select
                    v-model="localFormData.powerSource"
                    :items="powerSourceOptions"
                    label="農田水利署"
                    variant="outlined"
                    density="comfortable"
                    class="me-2 mb-2"
                    style="min-width: 200px"
                  ></v-select>

                  <v-btn
                    color="primary"
                    class="mb-2"
                    @click="addPowerEquipment"
                    :disabled="!canAddPowerEquipment"
                  >
                    <v-icon class="me-1">mdi-plus</v-icon>
                    加入
                  </v-btn>
                </div>
              </v-sheet>
            </v-card-text>
          </v-card>

          <!-- 調蓄設施區域 -->
          <v-card class="mb-4" variant="outlined">
            <v-card-title class="bg-light-blue-lighten-4 d-flex align-center py-2 px-4">
              <v-icon class="me-2" size="small">mdi-diving-scuba-tank-multiple</v-icon>
              <span class="text-subtitle-1 font-weight-medium">調蓄設施</span>
            </v-card-title>

            <v-card-text class="pa-4">
              <v-sheet class="pa-3 rounded" color="grey-lighten-5">
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
                  ></v-select>

                  <v-select
                    v-model="localFormData.storageTonnage"
                    :items="tonnageOptions"
                    label="噸數"
                    variant="outlined"
                    density="comfortable"
                    class="me-2 mb-2"
                    style="min-width: 100px"
                  ></v-select>

                  <v-select
                    v-model="localFormData.storageSource"
                    :items="fundingSourceOptions"
                    label="補助來源"
                    variant="outlined"
                    density="comfortable"
                    class="me-2 mb-2"
                    style="min-width: 180px"
                  ></v-select>

                  <v-text-field
                    v-model="localFormData.storageRemark"
                    label="備註"
                    variant="outlined"
                    density="comfortable"
                    class="me-2 mb-2"
                    style="min-width: 200px"
                  ></v-text-field>

                  <v-btn
                    color="primary"
                    class="mb-2"
                    @click="addStorageFacility"
                    :disabled="!canAddStorageFacility"
                  >
                    <v-icon class="me-1">mdi-plus</v-icon>
                    加入
                  </v-btn>
                </div>
              </v-sheet>
            </v-card-text>
          </v-card>

          <!-- 調節控制設施區域 -->
          <v-card class="mb-4" variant="outlined">
            <v-card-title class="bg-light-blue-lighten-4 d-flex align-center py-2 px-4">
              <v-icon class="me-2" size="small">mdi-valve</v-icon>
              <span class="text-subtitle-1 font-weight-medium">調節控制設施</span>
            </v-card-title>

            <v-card-text class="pa-4">
              <v-sheet class="pa-3 rounded" color="grey-lighten-5">
                <div class="d-flex align-center flex-wrap">
                  <v-select
                    v-model="localFormData.controlType"
                    :items="controlTypeOptions"
                    label="調節控制設施"
                    variant="outlined"
                    density="comfortable"
                    class="me-2 mb-2"
                    style="min-width: 180px"
                  ></v-select>

                  <v-text-field
                    v-model="localFormData.controlQuantity"
                    label="數量"
                    variant="outlined"
                    density="comfortable"
                    class="me-2 mb-2"
                    style="width: 80px"
                    type="number"
                    min="1"
                  ></v-text-field>

                  <v-text-field
                    v-model="localFormData.controlUnitPrice"
                    label="單價"
                    variant="outlined"
                    density="comfortable"
                    class="me-2 mb-2"
                    style="width: 120px"
                  ></v-text-field>

                  <v-text-field
                    v-model="controlTotalPrice"
                    label="總價"
                    variant="outlined"
                    density="comfortable"
                    class="me-2 mb-2"
                    style="width: 120px"
                    readonly
                    bg-color="grey-lighten-4"
                  ></v-text-field>

                  <v-select
                    v-model="localFormData.controlSource"
                    :items="fundingSourceOptions"
                    label="補助來源"
                    variant="outlined"
                    density="comfortable"
                    class="me-2 mb-2"
                    style="min-width: 180px"
                  ></v-select>

                  <v-btn
                    color="primary"
                    class="mb-2"
                    @click="addControlFacility"
                    :disabled="!canAddControlFacility"
                  >
                    <v-icon class="me-1">mdi-plus</v-icon>
                    加入
                  </v-btn>
                </div>
              </v-sheet>
            </v-card-text>
          </v-card>

          <!-- 設施列表 -->
          <v-card variant="outlined">
            <v-card-title class="bg-light-blue-lighten-4 d-flex align-center py-2 px-4">
              <v-icon class="me-2" size="small">mdi-format-list-bulleted</v-icon>
              <span class="text-subtitle-1 font-weight-medium">已新增設施列表</span>
            </v-card-title>

            <v-card-text class="pa-4">
              <v-table class="rounded border">
                <thead class="bg-grey-lighten-3">
                  <tr>
                    <th class="text-center" style="width: 50px">NO.</th>
                    <th>設施類型</th>
                    <th>設施名稱</th>
                    <th class="text-center">數量</th>
                    <th class="text-center">單價</th>
                    <th class="text-center">小計</th>
                    <th>備註</th>
                    <th>補助來源</th>
                    <th class="text-center" style="width: 80px">刪除</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(facility, index) in localFormData.facilities" :key="index">
                    <td class="text-center">{{ index + 1 }}</td>
                    <td>{{ facility.typeLabel }}</td>
                    <td>{{ facility.name }}</td>
                    <td class="text-center">{{ facility.quantity }}</td>
                    <td class="text-center">{{ facility.unitPrice }}</td>
                    <td class="text-center">{{ facility.totalPrice }}</td>
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
                    <td colspan="9" class="text-center py-3 text-grey">
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

    <!-- Navigation buttons -->
    <v-card class="step-navigation-card ma-0 pa-0" flat>
      <div class="d-flex align-center pr-4">
        <v-spacer />
        <div class="navigation-buttons">
          <v-btn
            variant="outlined"
            color="grey-darken-1"
            class="me-2"
            size="large"
            :disabled="currentStep === 1"
            rounded="pill"
            @click="goToPreviousStep"
          >
            <v-icon start>mdi-arrow-left</v-icon>
            上一步
          </v-btn>

          <v-btn
            color="green-darken-1"
            :disabled="!isValid"
            size="large"
            rounded="pill"
            @click="goToNextStep"
          >
            {{ currentStep === 8 ? '完成' : '下一步' }}
            <v-icon end v-if="currentStep < 8">mdi-arrow-right</v-icon>
            <v-icon end v-else>mdi-check</v-icon>
          </v-btn>
        </div>
      </div>
    </v-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, watch, computed } from 'vue';

// Props definition
const props = defineProps({
  formData: {
    type: Object,
    default: () => ({})
  },
  currentStep: {
    type: Number,
    required: true
  }
});

// Event emitters
const emit = defineEmits(['update:formData', 'validated', 'go-back']);

// Make isValid always true for demo
const isValid = computed(() => true);

// Form ref and validation state
const form = ref(null);
const localValid = ref(true); // Default to true for demo purposes

// Navigation methods - simplified for localStorage demo
const goToNextStep = async () => {
  // Always update data before moving forward
  updateFormData();

  console.log('Emitting validated event for step 3');
  emit('validated', { valid: true, step: 3 });
};

const goToPreviousStep = () => {
  // Always update data before going back
  updateFormData();

  console.log('Going back from step 3');
  emit('go-back'); // Make sure this matches what edit.vue expects
};

// 本地表單數據
const localFormData = reactive({
  // 動力設備
  powerEquipment: '',
  powerSource: '',

  // 調蓄設施
  storageType: '',
  storageTonnage: '',
  storageSource: '',
  storageRemark: '',

  // 調節控制設施
  controlType: '',
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
    source: string;
  }>,

  // Default valid state for demo
  valid: true
});

// 選項
const powerEquipmentOptions = [
  '馬達+抽水機',
  '馬達+柱塞泵',
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

const fundingSourceOptions = [
  '農田水利署',
  '七星管理處作業基金',
  '瑠公管理處作業基金'
];

// 計算屬性
const controlTotalPrice = computed(() => {
  const quantity = parseFloat(localFormData.controlQuantity as any) || 0;
  const unitPrice = parseFloat(localFormData.controlUnitPrice as any) || 0;
  return (quantity * unitPrice).toString();
});

// 驗證條件
const canAddPowerEquipment = computed(() => {
  return !!localFormData.powerEquipment && !!localFormData.powerSource;
});

const canAddStorageFacility = computed(() => {
  return !!localFormData.storageType && !!localFormData.storageTonnage && !!localFormData.storageSource;
});

const canAddControlFacility = computed(() => {
  return !!localFormData.controlType &&
         !!localFormData.controlQuantity &&
         !!localFormData.controlUnitPrice &&
         !!localFormData.controlSource;
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
      source: localFormData.powerSource
    });

    // 清空選擇
    localFormData.powerEquipment = '';
    localFormData.powerSource = '';

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
      source: localFormData.storageSource
    });

    // 清空選擇
    localFormData.storageType = '';
    localFormData.storageTonnage = '';
    localFormData.storageSource = '';
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
      name: localFormData.controlType,
      quantity: quantity,
      unitPrice: unitPrice,
      totalPrice: quantity * unitPrice,
      remark: '',
      source: localFormData.controlSource
    });

    // 清空選擇，但保留數量
    localFormData.controlType = '';
    localFormData.controlUnitPrice = '';
    localFormData.controlSource = '';

    updateFormData();
  }
};

// 移除設施
const removeFacility = (index: number) => {
  localFormData.facilities.splice(index, 1);
  updateFormData();
};

// 更新父組件數據 - modified for localStorage approach
const updateFormData = () => {
  emit('update:formData', {
    ...props.formData,
    ...localFormData,
    valid: true // Always set to true for demo
  });
};

// 初始化數據 - enhanced for demo data
onMounted(() => {
  // 從父組件接收數據
  if (props.formData) {
    // 設置基本屬性
    Object.keys(localFormData).forEach(key => {
      if (props.formData[key] !== undefined) {
        localFormData[key] = props.formData[key];
      }
    });

    // 確保設施列表被正確設置
    if (Array.isArray(props.formData.facilities)) {
      localFormData.facilities = [...props.formData.facilities];
    }
  }

  // 如果設施列表為空，添加示例設施數據
  if (!localFormData.facilities || localFormData.facilities.length === 0) {
    localFormData.facilities = [
      {
        type: 'power',
        typeLabel: '動力設備',
        name: '馬達+抽水機',
        quantity: 1,
        unitPrice: 4500,
        totalPrice: 4500,
        remark: '',
        source: '農田水利署'
      },
      {
        type: 'storage',
        typeLabel: '調蓄設施',
        name: '鋁合金-20噸',
        quantity: 1,
        unitPrice: 20000,
        totalPrice: 20000,
        remark: '示範用',
        source: '農田水利署'
      }
    ];
  }

  // Initial update to parent
  updateFormData();
});

// 監聽父組件數據變化
watch(() => props.formData, (newVal) => {
  if (newVal) {
    Object.keys(localFormData).forEach(key => {
      if (key !== 'facilities' && newVal[key] !== undefined &&
          JSON.stringify(newVal[key]) !== JSON.stringify(localFormData[key])) {
        localFormData[key] = newVal[key];
      }
    });

    // 特別處理設施列表
    if (Array.isArray(newVal.facilities) &&
        JSON.stringify(newVal.facilities) !== JSON.stringify(localFormData.facilities)) {
      localFormData.facilities = [...newVal.facilities];
    }
  }
}, { deep: true });

// 監聽本地數據變化，更新父組件
watch(localFormData, () => {
  updateFormData();
}, { deep: true });

// 監聽本地表單驗證狀態
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

.bg-primary {
  background-color: #1976D2 !important;
}

.bg-light-blue-lighten-4 {
  background-color: #B3E5FC !important;
}

.border {
  border: 1px solid rgba(0, 0, 0, 0.12);
}

.v-card .v-card-title {
  line-height: 1.5;
}

.v-table {
  background-color: white;
}

.v-table th {
  font-weight: 600;
  color: rgba(0, 0, 0, 0.7);
}
</style>
