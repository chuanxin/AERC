<template>
  <div class="step-content" ref="stepContent">
    <v-card class="mb-0 pa-0" flat>
      <v-card-text class="pb-0 pt-0">
        <v-form ref="form" v-model="localValid" @submit.prevent>
          <!-- 結案申報基本資訊區域 -->
          <v-card class="mb-4" variant="outlined">
            <v-card-title class="bg-light-blue-lighten-4 d-flex align-center py-2 px-4">
              <v-icon class="me-2" size="small">mdi-clipboard-text</v-icon>
              <span class="text-subtitle-1 font-weight-medium">結案申報基本資訊</span>
            </v-card-title>

            <v-card-text class="pa-4">
              <v-sheet
                class="pa-3 rounded"
                color="bg-amber-lighten-5 border border-amber"
              >
                <v-table
                  class="preview-table"
                  style="background-color: transparent"
                  density="compact"
                >
                  <tbody>
                    <tr>
                      <td
                        class="font-weight-medium text-center"
                        style="width: 15%"
                      >
                        申請年度
                      </td>
                      <td style="width: 35%">
                        {{ localFormData.applicationYear }}
                      </td>
                      <td
                        class="font-weight-medium text-center"
                        style="width: 15%"
                      >
                        案號
                      </td>
                      <td style="width: 35%">
                        {{ localFormData.caseNumber }}
                      </td>
                    </tr>
                    <tr>
                      <td class="font-weight-medium text-center">
                        農戶姓名
                      </td>
                      <td>
                        {{ localFormData.applicantName }}
                      </td>
                      <td class="font-weight-medium text-center">
                        農戶住址
                      </td>
                      <td>
                        {{ localFormData.applicantAddress }}
                      </td>
                    </tr>
                    <tr>
                      <td class="font-weight-medium text-center">
                        設施地段
                      </td>
                      <td>
                        {{ localFormData.facilityLocation }}
                      </td>
                      <td class="font-weight-medium text-center">
                        設施地號
                      </td>
                      <td>
                        {{ localFormData.facilityNumber }}
                      </td>
                    </tr>
                    <tr>
                      <td class="font-weight-medium text-center">
                        設施面積
                      </td>
                      <td>
                        {{ localFormData.facilityArea }}公頃
                      </td>
                      <td class="font-weight-medium text-center">
                        設施型式
                      </td>
                      <td>
                        {{ localFormData.facilityType }}
                      </td>
                    </tr>
                  </tbody>
                </v-table>
              </v-sheet>
            </v-card-text>
          </v-card>

          <!-- 竣工和測試資訊區域 -->
          <v-card class="mb-4" variant="outlined">
            <v-card-title class="bg-light-blue-lighten-4 d-flex align-center py-2 px-4">
              <v-icon class="me-2" size="small">mdi-check-decagram</v-icon>
              <span class="text-subtitle-1 font-weight-medium">竣工與測試資訊</span>
            </v-card-title>

            <v-card-text class="pa-4">
              <v-sheet class="pa-3 rounded" color="grey-lighten-5">
                <v-row>
                  <v-col cols="12" md="6">
                    <v-text-field
                      v-model="localFormData.completionDate"
                      label="竣工日期"
                      variant="outlined"
                      density="comfortable"
                      readonly
                      @click="datePickerDialog1 = true"
                      :rules="[v => !!v || '請選擇竣工日期']"
                      prepend-icon="mdi-calendar"
                      @update:model-value="updateFormData"
                    ></v-text-field>

                    <v-dialog
                      v-model="datePickerDialog1"
                      width="auto"
                    >
                      <v-card>
                        <v-card-text>
                          <v-date-picker
                            v-model="localFormData.completionDate"
                            @update:model-value="datePickerDialog1 = false"
                          ></v-date-picker>
                        </v-card-text>
                      </v-card>
                    </v-dialog>
                  </v-col>

                  <v-col cols="12" md="6">
                    <label class="text-body-2 font-weight-medium mb-2 d-block">竣工狀況</label>
                    <div class="d-flex align-center">
                      <v-radio-group
                        v-model="localFormData.completionStatus"
                        inline
                        :rules="[v => !!v || '請選擇竣工狀況']"
                        @update:model-value="updateFormData"
                      >
                        <v-radio value="completed" label="完工"></v-radio>
                        <v-radio value="incomplete" label="未完工"></v-radio>
                      </v-radio-group>
                    </div>
                  </v-col>
                </v-row>

                <v-row>
                  <v-col cols="12" md="6">
                    <v-text-field
                      v-model="localFormData.testDate"
                      label="測試日期"
                      variant="outlined"
                      density="comfortable"
                      readonly
                      @click="datePickerDialog2 = true"
                      :rules="[v => !!v || '請選擇測試日期']"
                      prepend-icon="mdi-calendar"
                      @update:model-value="updateFormData"
                    ></v-text-field>

                    <v-dialog
                      v-model="datePickerDialog2"
                      width="auto"
                    >
                      <v-card>
                        <v-card-text>
                          <v-date-picker
                            v-model="localFormData.testDate"
                            @update:model-value="datePickerDialog2 = false"
                          ></v-date-picker>
                        </v-card-text>
                      </v-card>
                    </v-dialog>
                  </v-col>

                  <v-col cols="12" md="6">
                    <v-text-field
                      v-model="localFormData.tester"
                      label="測試人員"
                      variant="outlined"
                      density="comfortable"
                      :rules="[v => !!v || '請填寫測試人員']"
                      prepend-icon="mdi-account"
                      @update:model-value="updateFormData"
                    ></v-text-field>
                  </v-col>
                </v-row>

                <v-row>
                  <v-col cols="12">
                    <v-select
                      v-model="localFormData.testResult"
                      :items="testResultOptions"
                      label="測試結果"
                      variant="outlined"
                      density="comfortable"
                      :rules="[v => !!v || '請選擇測試結果']"
                      prepend-icon="mdi-clipboard-check"
                      @update:model-value="updateFormData"
                    ></v-select>
                  </v-col>
                </v-row>
              </v-sheet>
            </v-card-text>
          </v-card>

          <!-- 測試結果詳細資訊區域 -->
          <v-card class="mb-4" variant="outlined" v-if="localFormData.testResult">
            <v-card-title class="bg-light-blue-lighten-4 d-flex align-center py-2 px-4">
              <v-icon class="me-2" size="small">mdi-check-circle</v-icon>
              <span class="text-subtitle-1 font-weight-medium">測試結果詳細資訊</span>
            </v-card-title>

            <v-card-text class="pa-4">
              <v-sheet class="pa-3 rounded" color="bg-amber-lighten-5 border border-amber">
                <v-row v-if="localFormData.testResult === 'original'">
                  <v-col cols="12">
                    <v-text-field
                      v-model="localFormData.originalPayment"
                      label="原應發放"
                      variant="outlined"
                      density="comfortable"
                      readonly
                      bg-color="yellow-lighten-3"
                      @update:model-value="updateFormData"
                    ></v-text-field>
                  </v-col>
                </v-row>

                <v-row v-if="localFormData.testResult === 'adjusted'">
                  <v-col cols="12">
                    <v-text-field
                      v-model="localFormData.increasedDecreasedAmount"
                      label="增減列"
                      variant="outlined"
                      density="comfortable"
                      :rules="localFormData.testResult === 'adjusted' ? [v => !!v || '請填寫增減列金額'] : []"
                      bg-color="yellow-lighten-3"
                      @update:model-value="updateFormData"
                    ></v-text-field>
                  </v-col>
                </v-row>

                <v-row v-if="localFormData.testResult === 'adjusted' || localFormData.testResult === 'original'">
                  <v-col cols="12">
                    <v-text-field
                      v-model="localFormData.actualPayment"
                      label="實際發放"
                      variant="outlined"
                      density="comfortable"
                      readonly
                      bg-color="yellow-lighten-3"
                      @update:model-value="updateFormData"
                    ></v-text-field>
                  </v-col>
                </v-row>

                <v-row>
                  <v-col cols="12">
                    <v-textarea
                      v-model="localFormData.testResultDescription"
                      label="結果說明"
                      variant="outlined"
                      density="comfortable"
                      rows="3"
                      auto-grow
                      :rules="[v => localFormData.testResult !== 'improvement' || !!v || '請填寫結果說明']"
                      @update:model-value="updateFormData"
                    ></v-textarea>
                  </v-col>
                </v-row>
              </v-sheet>
            </v-card-text>
          </v-card>

          <!-- 變更設計部分 -->
          <v-card class="mb-4" variant="outlined">
            <v-card-title class="bg-light-blue-lighten-4 d-flex align-center py-2 px-4">
              <v-icon class="me-2" size="small">mdi-file-compare</v-icon>
              <span class="text-subtitle-1 font-weight-medium">變更設計</span>
            </v-card-title>

            <v-card-text class="pa-4">
              <v-sheet class="pa-3 rounded" color="grey-lighten-5">
                <v-btn
                  color="primary"
                  block
                  class="mb-4"
                  @click="toggleDesignChange"
                >
                  {{ isDesignChangeVisible ? '取消變更設計' : '進行變更設計' }}
                </v-btn>

                <div v-if="isDesignChangeVisible">
                  <v-table class="design-change-table border-table">
                    <thead>
                      <tr>
                        <th>變更項目</th>
                        <th>變更前數量</th>
                        <th>變更後數量</th>
                        <th>增減數量</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="(item, index) in designChangeItems" :key="index">
                        <td>{{ item.name }}</td>
                        <td>
                          <v-text-field
                            v-model="item.beforeQuantity"
                            variant="outlined"
                            density="compact"
                            type="number"
                            @update:model-value="calculateDifference"
                          ></v-text-field>
                        </td>
                        <td>
                          <v-text-field
                            v-model="item.afterQuantity"
                            variant="outlined"
                            density="compact"
                            type="number"
                            @update:model-value="calculateDifference"
                          ></v-text-field>
                        </td>
                        <td>{{ item.afterQuantity - item.beforeQuantity }}</td>
                      </tr>
                    </tbody>
                    <tfoot>
                      <tr>
                        <td colspan="3" class="text-right font-weight-bold">合計增減</td>
                        <td>{{ totalQuantityChange }}</td>
                      </tr>
                    </tfoot>
                  </v-table>
                </div>
              </v-sheet>
            </v-card-text>
          </v-card>

          <!-- 照片上傳區域 -->
          <v-card variant="outlined">
            <v-card-title class="bg-light-blue-lighten-4 d-flex align-center py-2 px-4">
              <v-icon class="me-2" size="small">mdi-camera</v-icon>
              <span class="text-subtitle-1 font-weight-medium">施工照片</span>
            </v-card-title>

            <v-card-text class="pa-4">
              <v-sheet class="pa-3 rounded" color="grey-lighten-5">
                <v-row>
                  <v-col cols="12" md="6">
                    <label class="text-body-2 font-weight-medium mb-2 d-block">
                      <span class="text-red">*</span> 施工前照片
                    </label>
                    <v-file-input
                      v-model="localFormData.beforeConstructionPhoto"
                      label="選擇檔案"
                      variant="outlined"
                      density="comfortable"
                      accept="image/*"
                      prepend-icon="mdi-camera"
                      :rules="photoRules"
                      @update:model-value="handlePhotoChange('before')"
                    ></v-file-input>

                    <div v-if="localFormData.beforePhotoPreview" class="mt-2">
                      <v-img
                        :src="localFormData.beforePhotoPreview"
                        max-height="200"
                        contain
                        class="bg-grey-lighten-3 rounded"
                      ></v-img>
                    </div>
                  </v-col>

                  <v-col cols="12" md="6">
                    <label class="text-body-2 font-weight-medium mb-2 d-block">
                      <span class="text-red">*</span> 施工後照片
                    </label>
                    <v-file-input
                      v-model="localFormData.afterConstructionPhoto"
                      label="選擇檔案"
                      variant="outlined"
                      density="comfortable"
                      accept="image/*"
                      prepend-icon="mdi-camera"
                      :rules="photoRules"
                      @update:model-value="handlePhotoChange('after')"
                    ></v-file-input>

                    <div v-if="localFormData.afterPhotoPreview" class="mt-2">
                      <v-img
                        :src="localFormData.afterPhotoPreview"
                        max-height="200"
                        contain
                        class="bg-grey-lighten-3 rounded"
                      ></v-img>
                    </div>

                    <div v-if="!localFormData.afterConstructionPhoto && !localFormData.afterPhotoPreview" class="mt-2 d-flex align-center text-red">
                      <v-icon color="red" class="me-1" size="small">mdi-alert-circle</v-icon>
                      <span class="text-caption">卡驗收照片(尚未上傳施工後照片)</span>
                    </div>
                  </v-col>
                </v-row>

                <v-row v-if="!localFormData.afterConstructionPhoto && !localFormData.beforeConstructionPhoto && !localFormData.afterPhotoPreview && !localFormData.beforePhotoPreview">
                  <v-col cols="12">
                    <v-alert
                      type="warning"
                      variant="tonal"
                      class="mb-0"
                      density="comfortable"
                    >
                      <div class="d-flex align-center">
                        <v-icon class="me-2">mdi-alert</v-icon>
                        <span>尚未上傳施工前後照片，請儘速上傳以完成結案申報程序。</span>
                      </div>
                    </v-alert>
                  </v-col>
                </v-row>
              </v-sheet>
            </v-card-text>
          </v-card>
        </v-form>
      </v-card-text>
    </v-card>
  </div>
</template>

<script setup lang="ts">
import { useGrantsStore } from '@/stores/grants';

// Props and emits
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

// Access the grants store
const grantsStore = useGrantsStore();

// Form validation and dialogs
const form = ref(null);
const localValid = ref(true);
const datePickerDialog1 = ref(false);
const datePickerDialog2 = ref(false);
const isDesignChangeVisible = ref(false);

// 測試結果選項
const testResultOptions = [
  { title: '測試合格，依核定補助款發放', value: 'original' },
  { title: '測試合格，依核定補助款增減列', value: 'adjusted' },
  { title: '測試不合格，改善後另行複查', value: 'improvement' },
  { title: '限期改善後，測試不合格，取消補助資格', value: 'cancel' }
];

// 本地表單數據
const localFormData = reactive({
  // 基本資訊
  applicationYear: '',     // 申請年度
  caseNumber: '',          // 案號
  applicantName: '',       // 農戶姓名
  applicantAddress: '',    // 農戶住址
  facilityLocation: '',    // 設施地段
  facilityNumber: '',      // 設施地號
  facilityArea: '',        // 設施面積
  facilityType: '',        // 設施型式

  // 竣工資訊
  completionDate: '',      // 竣工日期
  completionStatus: '',    // 竣工狀況
  testDate: '',            // 測試日期
  tester: '',              // 測試人員
  testResult: '',          // 測試結果

  // 測試結果詳細資訊
  originalPayment: '',          // 原應發放
  increasedDecreasedAmount: '', // 增減列
  actualPayment: '',            // 實際發放
  testResultDescription: '',    // 結果說明

  // 照片
  beforeConstructionPhoto: null,
  afterConstructionPhoto: null,
  beforePhotoPreview: null,
  afterPhotoPreview: null,

  // 設置默認值，確保與edit.vue中的顯示邏輯保持一致
  valid: true
});

// 變更設計項目
const designChangeItems = reactive([
  { name: '主管', beforeQuantity: 2, afterQuantity: 1 },
  { name: '馬達+抽水機', beforeQuantity: 1, afterQuantity: 0 },
  { name: '單口噴頭-塑鋼', beforeQuantity: 0, afterQuantity: 10 }
]);

// 計算變更總量
const totalQuantityChange = computed(() => {
  return designChangeItems.reduce((total, item) => {
    return total + (Number(item.afterQuantity) - Number(item.beforeQuantity));
  }, 0);
});

// 驗證規則
const photoRules = [v => !!v || '請上傳照片'];

// 處理照片預覽
const handlePhotoChange = (type: 'before' | 'after') => {
  const file = type === 'before'
    ? localFormData.beforeConstructionPhoto
    : localFormData.afterConstructionPhoto;

  if (file) {
    // Only create object URLs for actual File objects
    if (file instanceof File) {
      // 清除之前的預覽
      if (type === 'before') {
        if (localFormData.beforePhotoPreview && typeof localFormData.beforePhotoPreview === 'string' &&
            localFormData.beforePhotoPreview.startsWith('blob:')) {
          URL.revokeObjectURL(localFormData.beforePhotoPreview);
        }
        localFormData.beforePhotoPreview = URL.createObjectURL(file);
      } else {
        if (localFormData.afterPhotoPreview && typeof localFormData.afterPhotoPreview === 'string' &&
            localFormData.afterPhotoPreview.startsWith('blob:')) {
          URL.revokeObjectURL(localFormData.afterPhotoPreview);
        }
        localFormData.afterPhotoPreview = URL.createObjectURL(file);
      }
    }
  }

  updateFormData();
};

// 切換變更設計顯示狀態
const toggleDesignChange = () => {
  isDesignChangeVisible.value = !isDesignChangeVisible.value;
  updateFormData();
};

// 計算變更前後差異
const calculateDifference = () => {
  updateFormData();
};

// 更新父組件數據
const updateFormData = () => {
  emit('update:formData', {
    ...props.formData,
    ...localFormData,
    designChangeItems: [...designChangeItems],
    valid: true // Always set to true for seamless navigation
  });
};

// 清理預覽資源的函數
const cleanupPreviews = () => {
  // Only clean up blob URLs, not external URLs
  if (localFormData.beforePhotoPreview && typeof localFormData.beforePhotoPreview === 'string' &&
      localFormData.beforePhotoPreview.startsWith('blob:')) {
    URL.revokeObjectURL(localFormData.beforePhotoPreview);
  }

  if (localFormData.afterPhotoPreview && typeof localFormData.afterPhotoPreview === 'string' &&
      localFormData.afterPhotoPreview.startsWith('blob:')) {
    URL.revokeObjectURL(localFormData.afterPhotoPreview);
  }
};

// 初始化數據
onMounted(() => {
  // 從父組件接收數據
  if (props.formData) {
    // 設置基本屬性
    Object.keys(localFormData).forEach(key => {
      if (props.formData[key] !== undefined) {
        localFormData[key] = props.formData[key];
      }
    });

    // 變更設計項目
    if (Array.isArray(props.formData.designChangeItems)) {
      props.formData.designChangeItems.forEach((item, index) => {
        if (index < designChangeItems.length) {
          designChangeItems[index].beforeQuantity = item.beforeQuantity;
          designChangeItems[index].afterQuantity = item.afterQuantity;
        } else {
          designChangeItems.push({ ...item });
        }
      });
    }
  }

  // Initialize data from other steps if necessary
  if (!localFormData.applicationYear) {
    // Try to get from store or use default
    if (grantsStore.formData[6]?.applicationYear) {
      localFormData.applicationYear = grantsStore.formData[6].applicationYear;
    } else {
      const currentYear = new Date().getFullYear() - 1911; // Taiwan calendar year
      localFormData.applicationYear = `${currentYear}`;
    }
  }

  // Get case number
  if (!localFormData.caseNumber) {
    if (grantsStore.caseNumber) {
      localFormData.caseNumber = grantsStore.caseNumber;
    }
  }

  // Get applicant info
  if (!localFormData.applicantName) {
    if (grantsStore.formData[1]?.name) {
      localFormData.applicantName = grantsStore.formData[1].name;
    } else if (grantsStore.formData[6]?.applicantName) {
      localFormData.applicantName = grantsStore.formData[6].applicantName;
    }
  }

  // Get applicant address
  if (!localFormData.applicantAddress) {
    if (grantsStore.formData[6]?.applicantAddress) {
      localFormData.applicantAddress = grantsStore.formData[6].applicantAddress;
    } else {
      const step1Data = grantsStore.formData[1];
      if (step1Data) {
        const county = step1Data.county || '';
        const town = step1Data.town || '';
        const village = step1Data.village || '';
        const address = step1Data.address || '';

        if (county || town || village || address) {
          localFormData.applicantAddress = `${county}${town}${village}${address}`;
        }
      }
    }
  }

  // Get facility info from previous steps
  if (!localFormData.facilityLocation) {
    if (grantsStore.formData[6]?.facilityLocation) {
      localFormData.facilityLocation = grantsStore.formData[6].facilityLocation;
    } else if (grantsStore.formData[2]) {
      const step2Data = grantsStore.formData[2];
      const county = step2Data.addressCounty || '';
      const town = step2Data.addressTown || '';
      const village = step2Data.addressVillage || '';

      if (county || town || village) {
        localFormData.facilityLocation = `${county}${town}${village}`;
      }
    }
  }

  if (!localFormData.facilityNumber) {
    if (grantsStore.formData[6]?.facilityNumber) {
      localFormData.facilityNumber = grantsStore.formData[6].facilityNumber;
    } else if (grantsStore.formData[2]?.landNumber) {
      localFormData.facilityNumber = grantsStore.formData[2].landNumber;
    }
  }

  if (!localFormData.facilityArea) {
    if (grantsStore.formData[6]?.facilityArea) {
      localFormData.facilityArea = grantsStore.formData[6].facilityArea;
    } else if (grantsStore.formData[2]?.landAreaHa) {
      localFormData.facilityArea = grantsStore.formData[2].landAreaHa;
    }
  }

  if (!localFormData.facilityType) {
    if (grantsStore.formData[6]?.facilityType) {
      localFormData.facilityType = grantsStore.formData[6].facilityType;
    } else {
      // Try to construct from step4 data
      const step4Data = grantsStore.formData[4];
      if (step4Data) {
        const installationType = step4Data.installationType || '';
        const irrigationType = step4Data.irrigationType || '';

        if (installationType || irrigationType) {
          localFormData.facilityType = `${installationType}${irrigationType}系統`;
        }
      }
    }
  }

  // Set default completion information
  if (!localFormData.completionDate) {
    const today = new Date();
    const year = today.getFullYear();
    const month = String(today.getMonth() + 1).padStart(2, '0');
    const day = String(today.getDate()).padStart(2, '0');
    localFormData.completionDate = `${year}-${month}-${day}`;
  }

  if (!localFormData.testDate) {
    const today = new Date();
    const year = today.getFullYear();
    const month = String(today.getMonth() + 1).padStart(2, '0');
    const day = String(today.getDate()).padStart(2, '0');
    localFormData.testDate = `${year}-${month}-${day}`;
  }

  // Set default values for new forms
  if (!localFormData.completionStatus) {
    localFormData.completionStatus = 'completed';
  }

  if (!localFormData.tester) {
    localFormData.tester = '王工程師';
  }

  if (!localFormData.testResult) {
    localFormData.testResult = 'original';
  }

  // Set default payment info
  if (!localFormData.originalPayment && localFormData.testResult === 'original') {
    if (grantsStore.formData[6]?.totalBudget) {
      localFormData.originalPayment = grantsStore.formData[6].totalBudget;
    } else {
      localFormData.originalPayment = '13,378';
    }

    localFormData.actualPayment = localFormData.originalPayment;
  }

  // Set sample description if needed
  if (!localFormData.testResultDescription && localFormData.testResult === 'original') {
    localFormData.testResultDescription = '工程完工符合規範，依核定補助款發放。';
  }

  // Set sample photo previews if none exist
  if (!localFormData.beforePhotoPreview) {
    localFormData.beforePhotoPreview = 'https://via.placeholder.com/400x300?text=施工前照片示例';
  }

  if (!localFormData.afterPhotoPreview) {
    localFormData.afterPhotoPreview = 'https://via.placeholder.com/400x300?text=施工後照片示例';
  }

  // Initial update to parent
  updateFormData();
});

// 監聽測試結果變化
watch(() => localFormData.testResult, (newValue) => {
  if (newValue === 'original') {
    // 如果是 "依核定補助款發放"，則自動設置相關金額
    if (!localFormData.originalPayment) {
      // 可以從父組件中獲取預設的補助款金額
      if (grantsStore.formData[6]?.totalBudget) {
        localFormData.originalPayment = grantsStore.formData[6].totalBudget;
      } else {
        localFormData.originalPayment = '13,378';
      }
    }
    localFormData.actualPayment = localFormData.originalPayment;
    localFormData.increasedDecreasedAmount = '';

    // Add a default description
    if (!localFormData.testResultDescription) {
      localFormData.testResultDescription = '工程完工符合規範，依核定補助款發放。';
    }
  } else if (newValue === 'adjusted') {
    // 如果是 "依核定補助款增減列"，則重置金額欄位
    if (!localFormData.originalPayment) {
      if (grantsStore.formData[6]?.totalBudget) {
        localFormData.originalPayment = grantsStore.formData[6].totalBudget;
      } else {
        localFormData.originalPayment = '13,378';
      }
    }
    if (!localFormData.increasedDecreasedAmount) {
      localFormData.increasedDecreasedAmount = '-1,000';
    }

    // Add a default description
    if (!localFormData.testResultDescription) {
      localFormData.testResultDescription = '因部分材料規格變更，調整補助金額。';
    }

    // 實際發放金額會通過增減列計算
    try {
      const original = parseFloat(localFormData.originalPayment.replace(/,/g, ''));
      const adjustment = parseFloat(localFormData.increasedDecreasedAmount.replace(/,/g, ''));
      if (!isNaN(original) && !isNaN(adjustment)) {
        const actual = original + adjustment;
        localFormData.actualPayment = actual.toLocaleString();
      }
    } catch (e) {
      console.error('計算實際發放金額時出錯', e);
    }
  } else if (newValue === 'improvement') {
    // Add a default description for improvement needed
    if (!localFormData.testResultDescription) {
      localFormData.testResultDescription = '末端噴頭設置不符合設計規範，需重新安裝調整。';
    }

    // 其他情況，清空金額欄位
    localFormData.originalPayment = '';
    localFormData.increasedDecreasedAmount = '';
    localFormData.actualPayment = '';
  } else {
    // Add a default description for cancelation
    if (!localFormData.testResultDescription) {
      localFormData.testResultDescription = '經限期改善後，仍未符合設計規範，取消本次補助資格。';
    }

    // 其他情況，清空金額欄位
    localFormData.originalPayment = '';
    localFormData.increasedDecreasedAmount = '';
    localFormData.actualPayment = '';
  }

  updateFormData();
});

// 監聽原金額與增減列變化
watch([() => localFormData.originalPayment, () => localFormData.increasedDecreasedAmount], () => {
  if (localFormData.testResult === 'adjusted' && localFormData.originalPayment && localFormData.increasedDecreasedAmount) {
    try {
      const original = parseFloat(localFormData.originalPayment.replace(/,/g, ''));
      const adjustment = parseFloat(localFormData.increasedDecreasedAmount.replace(/,/g, ''));
      if (!isNaN(original) && !isNaN(adjustment)) {
        const actual = original + adjustment;
        localFormData.actualPayment = actual.toLocaleString();
      }
    } catch (e) {
      console.error('計算實際發放金額時出錯', e);
    }
  }
  updateFormData();
});

// 監聽父組件數據變化
watch(() => props.formData, (newVal) => {
  if (newVal) {
    // 更新基本屬性
    Object.keys(localFormData).forEach(key => {
      if (newVal[key] !== undefined &&
          JSON.stringify(newVal[key]) !== JSON.stringify(localFormData[key])) {
        localFormData[key] = newVal[key];
      }
    });

    // 更新變更設計項目
    if (Array.isArray(newVal.designChangeItems) &&
        JSON.stringify(newVal.designChangeItems) !== JSON.stringify(designChangeItems)) {
      // Clear existing items
      while (designChangeItems.length > 0) {
        designChangeItems.pop();
      }

      // Add new items
      newVal.designChangeItems.forEach(item => {
        designChangeItems.push({ ...item });
      });
    }
  }
}, { deep: true });

// 監聽表單驗證狀態變化
watch(localValid, (newVal) => {
  if (props.formData?.valid !== newVal) {
    updateFormData();
  }
});

// 組件卸載時清理資源
onUnmounted(() => {
  cleanupPreviews();
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

.bg-amber-lighten-5 {
  background-color: #FFF8E1 !important;
}

.border-amber {
  border-color: #FFD54F !important;
  border-width: 1px;
  border-style: solid;
}

.bg-yellow-lighten-3 {
  background-color: #FFF59D !important;
}

.v-table {
  background-color: white;
}

.v-table th {
  font-weight: 600;
  color: rgba(0, 0, 0, 0.7);
}

.inner-table {
  border: none !important;
  font-size: 0.875rem;
}

.inner-table th,
.inner-table td {
  padding: 2px 4px !important;
  border-bottom: 1px solid rgba(0, 0, 0, 0.12) !important;
}

.inner-table th {
  background-color: rgba(0, 0, 0, 0.03);
  font-weight: 500;
  font-size: 0.8rem;
}

.inner-table tr:last-child td {
  border-bottom: none !important;
}

.preview-table {
  width: 100%;
  border-collapse: collapse;
}

.preview-table td {
  border: 1px solid rgba(0, 0, 0, 0.12);
  padding: 10px;
}

.preview-table td.font-weight-medium {
  background-color: rgba(255, 224, 130, 0.15);
}

.text-red {
  color: red;
}

.design-change-table {
  width: 100%;
  border-collapse: collapse;
}

.design-change-table th,
.design-change-table td {
  border: 1px solid rgba(0, 0, 0, 0.12);
  padding: 8px;
}

.design-change-table th {
  background-color: rgba(0, 0, 0, 0.05);
  font-weight: 600;
}
</style>
