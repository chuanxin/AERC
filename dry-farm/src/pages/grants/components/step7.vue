<template>
  <div class="step-content" ref="stepContent">
    <v-card class="mb-6 pa-0" flat>
      <v-card-text class="pb-0 pt-0">
        <v-form ref="form" v-model="localValid" @submit.prevent>
          <!-- 結案申報基本資訊區域 -->
          <v-card class="mb-4" variant="outlined">
            <v-card-title class="bg-light-blue-lighten-4 d-flex align-center py-2 px-4">
              <v-icon class="me-2" size="small">mdi-clipboard-text</v-icon>
              <span class="text-subtitle-1 font-weight-medium">結案申報基本資訊</span>
            </v-card-title>

            <v-card-text class="pa-4">
              <v-sheet class="pa-3 rounded" color="grey-lighten-5">
                <v-table class="report-table">
                  <tbody>
                    <tr>
                      <td style="width: 150px" class="font-weight-medium text-center">申請年度</td>
                      <td>{{ localFormData.applicationYear }}</td>
                      <td style="width: 150px" class="font-weight-medium text-center">案件編號</td>
                      <td>{{ localFormData.caseNumber }}</td>
                    </tr>
                    <tr>
                      <td class="font-weight-medium text-center">農戶姓名</td>
                      <td>{{ localFormData.applicantName }}</td>
                      <td class="font-weight-medium text-center">農戶住址</td>
                      <td>{{ localFormData.applicantAddress }}</td>
                    </tr>
                    <tr>
                      <td class="font-weight-medium text-center">設施地段</td>
                      <td>{{ localFormData.facilityLocation }}</td>
                      <td class="font-weight-medium text-center">設施地號</td>
                      <td>{{ localFormData.facilityNumber }}</td>
                    </tr>
                    <tr>
                      <td class="font-weight-medium text-center">設施面積</td>
                      <td>{{ localFormData.facilityArea }}公頃</td>
                      <td class="font-weight-medium text-center">設施型式</td>
                      <td>{{ localFormData.facilityType }}</td>
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
                            hide-details
                            readonly
                            bg-color="grey-lighten-4"
                          ></v-text-field>
                        </td>
                        <td>
                          <v-text-field
                            v-model="item.afterQuantity"
                            variant="outlined"
                            density="compact"
                            type="number"
                            hide-details
                            @update:model-value="calculateDifference"
                          ></v-text-field>
                        </td>
                      </tr>
                    </tbody>
                    <tfoot>
                      <tr>
                        <td colspan="3" class="caption text-grey pa-2">
                          註：從3開始統計差異
                        </td>
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

                    <div v-if="!localFormData.afterConstructionPhoto" class="mt-2 d-flex align-center text-red">
                      <v-icon color="red" class="me-1" size="small">mdi-alert-circle</v-icon>
                      <span class="text-caption">卡驗收照片(尚未上傳施工後照片)</span>
                    </div>
                  </v-col>
                </v-row>

                <v-row v-if="!localFormData.afterConstructionPhoto || !localFormData.beforeConstructionPhoto">
                  <v-col cols="12">
                    <v-alert
                      type="warning"
                      variant="tonal"
                      class="mb-0"
                      density="comfortable"
                    >
                      <div class="d-flex align-center">
                        <v-icon class="me-2">mdi-arrow-right-bold</v-icon>
                        <span>跳回資料缺失處</span>
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

    <v-card class="step-navigation-card ma-0 pa-0" flat>
      <div class="d-flex align-center pr-4">
        <v-spacer></v-spacer>
        <div class="navigation-buttons">
          <v-btn
            variant="outlined"
            color="grey-darken-1"
            class="me-2"
            size="large"
            @click="goToPreviousStep"
            rounded="pill"
          >
            <v-icon start>mdi-arrow-left</v-icon>
            上一步
          </v-btn>

          <v-btn
            color="green-darken-1"
            :disabled="!isValid"
            @click="goToNextStep"
            size="large"
            rounded="pill"
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

// FIXED: Changed 'goBack' to 'go-back' to match edit.vue
const emit = defineEmits(['update:formData', 'validated', 'go-back']);

// Changed for demo: Set to true by default for frictionless navigation
const localValid = ref(true);
const form = ref(null);
const datePickerDialog1 = ref(false);
const datePickerDialog2 = ref(false);
const isDesignChangeVisible = ref(false);

// ADDED: Create isValid property that always returns true for demo
const isValid = computed(() => true);

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

  // ADDED: Set this to true by default for demo
  valid: true
});

// 變更設計項目
const designChangeItems = reactive([
  { name: '主管', beforeQuantity: 2, afterQuantity: 1 },
  { name: '馬達+抽水機', beforeQuantity: 1, afterQuantity: 0 },
  { name: '單口噴頭-塑鋼', beforeQuantity: 0, afterQuantity: 10 }
]);

// 驗證規則
const photoRules = [v => !!v || '請上傳照片'];

// 處理照片預覽
const handlePhotoChange = (type: 'before' | 'after') => {
  const file = type === 'before'
    ? localFormData.beforeConstructionPhoto
    : localFormData.afterConstructionPhoto;

  if (file) {
    // MODIFIED: Only create object URLs for actual File objects
    if (file instanceof File) {
      // 清除之前的預覽
      if (type === 'before') {
        if (localFormData.beforePhotoPreview && localFormData.beforePhotoPreview.startsWith('blob:')) {
          URL.revokeObjectURL(localFormData.beforePhotoPreview);
        }
        localFormData.beforePhotoPreview = URL.createObjectURL(file);
      } else {
        if (localFormData.afterPhotoPreview && localFormData.afterPhotoPreview.startsWith('blob:')) {
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
};

// 計算變更前後差異
const calculateDifference = () => {
  // 計算差異並可能更新其他相關數據
  updateFormData();
};

// 上一步 - MODIFIED for localStorage approach
const goToPreviousStep = () => {
  // Always update data before going back
  updateFormData();

  console.log('Going back from step 7');
  // FIXED: Changed 'goBack' to 'go-back'
  emit('go-back');
};

// 下一步 - MODIFIED for localStorage approach
const goToNextStep = async () => {
  // For demo, no validation needed
  updateFormData();

  console.log('Emitting validated event for step 7');
  emit('validated', { valid: true, step: 7 });
};

// 更新父組件數據 - MODIFIED for localStorage approach
const updateFormData = () => {
  emit('update:formData', {
    ...props.formData,
    ...localFormData,
    designChangeItems,
    valid: true // CHANGED: Always set to true for demo
  });
};

// 初始化數據 - ENHANCED for demo data
onMounted(() => {
  // 設置初始數據
  if (props.formData) {
    // 基本資訊
    Object.keys(localFormData).forEach(key => {
      if (props.formData[key] !== undefined) {
        localFormData[key] = props.formData[key];
      }
    });

    // 變更設計項目
    if (props.formData.designChangeItems) {
      props.formData.designChangeItems.forEach((item, index) => {
        if (index < designChangeItems.length) {
          designChangeItems[index].beforeQuantity = item.beforeQuantity;
          designChangeItems[index].afterQuantity = item.afterQuantity;
        }
      });
    }
  }

  // 初始化數據（確保有默認值）
  // 基本資訊 - Use data from previous steps if available
  // Try to get from step6 or use default values
  if (props.formData.applicationYear) {
    localFormData.applicationYear = props.formData.applicationYear;
  } else {
    localFormData.applicationYear = '113';
  }

  // Get case number from URL or use default
  if (!localFormData.caseNumber) {
    const urlParams = new URLSearchParams(window.location.search);
    const idParam = urlParams.get('id');
    localFormData.caseNumber = idParam || '113010001';
  }

  // Get applicant information from previous steps if available
  if (!localFormData.applicantName) {
    // Try step1 data
    if (props.formData.name) {
      localFormData.applicantName = props.formData.name;
    } else if (props.formData.applicantName) {
      localFormData.applicantName = props.formData.applicantName;
    } else {
      localFormData.applicantName = '林嘉寶';
    }
  }

  if (!localFormData.applicantAddress) {
    if (props.formData.applicantAddress) {
      localFormData.applicantAddress = props.formData.applicantAddress;
    } else {
      // Try to build from step1 data
      const county = props.formData.county || '';
      const town = props.formData.town || '';
      const village = props.formData.village || '';
      const address = props.formData.address || '';
      if (county || town || village || address) {
        localFormData.applicantAddress = `${county}${town}${village}${address}`;
      } else {
        localFormData.applicantAddress = '嘉義縣竹崎鄉龍山村16鄰過坑14號';
      }
    }
  }

  // Get facility info from step2 or step6
  if (!localFormData.facilityLocation) {
    if (props.formData.facilityLocation) {
      localFormData.facilityLocation = props.formData.facilityLocation;
    } else {
      localFormData.facilityLocation = '嘉義縣竹崎鄉瓦厝埔段';
    }
  }

  if (!localFormData.facilityNumber) {
    if (props.formData.facilityNumber) {
      localFormData.facilityNumber = props.formData.facilityNumber;
    } else if (props.formData.landNumber) {
      localFormData.facilityNumber = props.formData.landNumber;
    } else {
      localFormData.facilityNumber = '0966-0001';
    }
  }

  if (!localFormData.facilityArea) {
    if (props.formData.facilityArea) {
      localFormData.facilityArea = props.formData.facilityArea;
    } else if (props.formData.landAreaHa) {
      localFormData.facilityArea = props.formData.landAreaHa;
    } else {
      localFormData.facilityArea = '0.8455';
    }
  }

  if (!localFormData.facilityType) {
    if (props.formData.facilityType) {
      localFormData.facilityType = props.formData.facilityType;
    } else {
      // Try to construct from step4 data
      const installationType = props.formData.installationType || '';
      const irrigationType = props.formData.irrigationType || '';
      if (installationType && irrigationType) {
        localFormData.facilityType = `${installationType}${irrigationType}系統`;
      } else {
        localFormData.facilityType = '地表定置式噴頭式系統';
      }
    }
  }

  // 竣工和測試資訊 - Set default values if empty
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

  localFormData.completionStatus = localFormData.completionStatus || 'completed';
  localFormData.tester = localFormData.tester || '王工程師';
  localFormData.testResult = localFormData.testResult || 'original';

  // 預設支付金額 - Use data from step6 if available
  if (!localFormData.originalPayment) {
    if (props.formData.totalBudget) {
      localFormData.originalPayment = props.formData.totalBudget;
    } else {
      localFormData.originalPayment = '13,378';
    }
  }

  if (localFormData.testResult === 'original') {
    localFormData.actualPayment = localFormData.originalPayment;
  }

  // Set sample description if empty
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

  // Update after initialization
  updateFormData();
});

// 監聽原應發放和增減列變化，計算實際發放
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
  } else if (localFormData.testResult === 'original' && localFormData.originalPayment) {
    localFormData.actualPayment = localFormData.originalPayment;
  }
});

// 監聽測試結果變化
watch(() => localFormData.testResult, (newValue) => {
  if (newValue === 'original') {
    // 如果是 "依核定補助款發放"，則自動設置相關金額
    if (!localFormData.originalPayment) {
      // 可以從父組件中獲取預設的補助款金額
      if (props.formData.totalBudget) {
        localFormData.originalPayment = props.formData.totalBudget;
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
      if (props.formData.totalBudget) {
        localFormData.originalPayment = props.formData.totalBudget;
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

    // 實際發放金額會通過上面的 watch 自動計算
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
});

// Simplified watch handlers for demo
watch(() => props.formData, (newVal) => {
  if (newVal) {
    updateFormData();
  }
}, { deep: true });

// Simplified watch for local data changes
watch([localFormData, designChangeItems], () => {
  updateFormData();
}, { deep: true });
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

.text-red {
  color: red;
}

.report-table {
  width: 100%;
  border-collapse: collapse;
}

.report-table td {
  border: 1px solid rgba(0, 0, 0, 0.12);
  padding: 10px;
}

.report-table td.font-weight-medium {
  background-color: rgba(255, 224, 130, 0.15);
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
