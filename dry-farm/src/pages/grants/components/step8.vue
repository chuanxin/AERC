<template>
  <div class="step-content" ref="stepContent">
    <v-card class="mb-0 pa-0" flat>
      <v-card-text class="pb-0 pt-0">
        <v-form ref="form" v-model="localValid" @submit.prevent>
          <!-- 申請資料區域 -->
          <v-card class="mb-4" variant="outlined">
            <v-card-title class="bg-light-blue-lighten-4 d-flex align-center py-2 px-4">
              <v-icon class="me-2" size="small">mdi-file-document</v-icon>
              <span class="text-subtitle-1 font-weight-medium">申請資料</span>
              <v-chip size="small" color="info" class="ms-2">擇一上傳</v-chip>
            </v-card-title>

            <v-card-text class="pa-4">
              <v-sheet class="pa-3 rounded" color="grey-lighten-5">
                <v-row>
                  <v-col cols="12" md="6">
                    <v-file-input
                      v-model="localFormData.idCardFront"
                      label="身分證正面"
                      variant="outlined"
                      density="comfortable"
                      accept="image/*"
                      prepend-icon="mdi-card-account-details"
                      @update:model-value="handleFileChange('idFront')"
                    ></v-file-input>

                    <div v-if="localFormData.idCardFrontPreview" class="mt-2">
                      <v-img
                        :src="localFormData.idCardFrontPreview"
                        max-height="200"
                        contain
                        class="bg-grey-lighten-3 rounded"
                      ></v-img>
                    </div>
                  </v-col>

                  <v-col cols="12" md="6">
                    <v-file-input
                      v-model="localFormData.idCardBack"
                      label="身分證反面"
                      variant="outlined"
                      density="comfortable"
                      accept="image/*"
                      prepend-icon="mdi-card-account-details"
                      @update:model-value="handleFileChange('idBack')"
                    ></v-file-input>

                    <div v-if="localFormData.idCardBackPreview" class="mt-2">
                      <v-img
                        :src="localFormData.idCardBackPreview"
                        max-height="200"
                        contain
                        class="bg-grey-lighten-3 rounded"
                      ></v-img>
                    </div>
                  </v-col>
                </v-row>

                <v-row>
                  <v-col cols="12" md="6">
                    <v-file-input
                      v-model="localFormData.applicationFile"
                      label="申請資料"
                      variant="outlined"
                      density="comfortable"
                      accept=".pdf,.jpg,.jpeg,.png"
                      prepend-icon="mdi-file-document"
                      @update:model-value="handleFileChange('applicationFile')"
                    ></v-file-input>

                    <div v-if="localFormData.applicationFilePreview" class="mt-2">
                      <v-img
                        :src="localFormData.applicationFilePreview"
                        max-height="200"
                        contain
                        class="bg-grey-lighten-3 rounded"
                      ></v-img>
                    </div>
                  </v-col>
                </v-row>
              </v-sheet>
            </v-card-text>
          </v-card>

          <!-- 土地資料區域 -->
          <v-card class="mb-4" variant="outlined">
            <v-card-title class="bg-light-blue-lighten-4 d-flex align-center py-2 px-4">
              <v-icon class="me-2" size="small">mdi-map</v-icon>
              <span class="text-subtitle-1 font-weight-medium">土地資料</span>
            </v-card-title>

            <v-card-text class="pa-4">
              <v-sheet class="pa-3 rounded" color="grey-lighten-5">
                <v-row>
                  <v-col cols="12" md="6">
                    <v-file-input
                      v-model="localFormData.landRegistration"
                      label="土地登記謄本"
                      variant="outlined"
                      density="comfortable"
                      accept=".pdf,.jpg,.jpeg,.png"
                      prepend-icon="mdi-file-document"
                      @update:model-value="handleFileChange('landReg')"
                    ></v-file-input>

                    <div v-if="localFormData.landRegistrationPreview" class="mt-2">
                      <v-img
                        :src="localFormData.landRegistrationPreview"
                        max-height="200"
                        contain
                        class="bg-grey-lighten-3 rounded"
                      ></v-img>
                    </div>
                  </v-col>

                  <v-col cols="12" md="6">
                    <v-file-input
                      v-model="localFormData.landMap"
                      label="地籍圖謄本"
                      variant="outlined"
                      density="comfortable"
                      accept=".pdf,.jpg,.jpeg,.png"
                      prepend-icon="mdi-map"
                      @update:model-value="handleFileChange('landMap')"
                    ></v-file-input>

                    <div v-if="localFormData.landMapPreview" class="mt-2">
                      <v-img
                        :src="localFormData.landMapPreview"
                        max-height="200"
                        contain
                        class="bg-grey-lighten-3 rounded"
                      ></v-img>
                    </div>
                  </v-col>
                </v-row>

                <v-row>
                  <v-col cols="12" md="6">
                    <v-file-input
                      v-model="localFormData.leaseAgreement"
                      label="租賃同意書"
                      variant="outlined"
                      density="comfortable"
                      accept=".pdf,.jpg,.jpeg,.png"
                      prepend-icon="mdi-file-document-outline"
                      @update:model-value="handleFileChange('lease')"
                    ></v-file-input>

                    <div v-if="localFormData.leaseAgreementPreview" class="mt-2">
                      <v-img
                        :src="localFormData.leaseAgreementPreview"
                        max-height="200"
                        contain
                        class="bg-grey-lighten-3 rounded"
                      ></v-img>
                    </div>
                  </v-col>

                  <v-col cols="12" md="6">
                    <v-file-input
                      v-model="localFormData.landUseConsent"
                      label="土地施設同意書"
                      variant="outlined"
                      density="comfortable"
                      accept=".pdf,.jpg,.jpeg,.png"
                      prepend-icon="mdi-file-document-outline"
                      @update:model-value="handleFileChange('landUse')"
                    ></v-file-input>

                    <div v-if="localFormData.landUseConsentPreview" class="mt-2">
                      <v-img
                        :src="localFormData.landUseConsentPreview"
                        max-height="200"
                        contain
                        class="bg-grey-lighten-3 rounded"
                      ></v-img>
                    </div>
                  </v-col>
                </v-row>
              </v-sheet>
            </v-card-text>
          </v-card>

          <!-- 其他資料區域 -->
          <v-card variant="outlined">
            <v-card-title class="bg-light-blue-lighten-4 d-flex align-center py-2 px-4">
              <v-icon class="me-2" size="small">mdi-file-multiple</v-icon>
              <span class="text-subtitle-1 font-weight-medium">其他資料</span>
            </v-card-title>

            <v-card-text class="pa-4">
              <v-sheet class="pa-3 rounded" color="grey-lighten-5">
                <v-row>
                  <v-col cols="12" md="6">
                    <v-file-input
                      v-model="localFormData.inspectionRecord"
                      label="現勘紀錄表"
                      variant="outlined"
                      density="comfortable"
                      accept=".pdf,.jpg,.jpeg,.png"
                      prepend-icon="mdi-clipboard-check"
                      @update:model-value="handleFileChange('inspection')"
                    ></v-file-input>

                    <div v-if="localFormData.inspectionRecordPreview" class="mt-2">
                      <v-img
                        :src="localFormData.inspectionRecordPreview"
                        max-height="200"
                        contain
                        class="bg-grey-lighten-3 rounded"
                      ></v-img>
                    </div>
                  </v-col>

                  <v-col cols="12" md="6">
                    <v-file-input
                      v-model="localFormData.planningDoc"
                      label="委託規劃書"
                      variant="outlined"
                      density="comfortable"
                      accept=".pdf,.jpg,.jpeg,.png"
                      prepend-icon="mdi-file-document-outline"
                      @update:model-value="handleFileChange('planning')"
                    ></v-file-input>

                    <div v-if="localFormData.planningDocPreview" class="mt-2">
                      <v-img
                        :src="localFormData.planningDocPreview"
                        max-height="200"
                        contain
                        class="bg-grey-lighten-3 rounded"
                      ></v-img>
                    </div>
                  </v-col>
                </v-row>

                <v-row>
                  <v-col cols="12" md="6">
                    <v-file-input
                      v-model="localFormData.subsidy"
                      label="接受補助切結書"
                      variant="outlined"
                      density="comfortable"
                      accept=".pdf,.jpg,.jpeg,.png"
                      prepend-icon="mdi-file-document-outline"
                      @update:model-value="handleFileChange('subsidy')"
                    ></v-file-input>

                    <div v-if="localFormData.subsidyPreview" class="mt-2">
                      <v-img
                        :src="localFormData.subsidyPreview"
                        max-height="200"
                        contain
                        class="bg-grey-lighten-3 rounded"
                      ></v-img>
                    </div>
                  </v-col>

                  <v-col cols="12" md="6">
                    <v-file-input
                      v-model="localFormData.workInspection"
                      label="竣工報驗書"
                      variant="outlined"
                      density="comfortable"
                      accept=".pdf,.jpg,.jpeg,.png"
                      prepend-icon="mdi-file-document-outline"
                      @update:model-value="handleFileChange('workInspection')"
                    ></v-file-input>

                    <div v-if="localFormData.workInspectionPreview" class="mt-2">
                      <v-img
                        :src="localFormData.workInspectionPreview"
                        max-height="200"
                        contain
                        class="bg-grey-lighten-3 rounded"
                      ></v-img>
                    </div>
                  </v-col>
                </v-row>

                <v-row>
                  <v-col cols="12" md="6">
                    <v-file-input
                      v-model="localFormData.inspectionReport"
                      label="驗收報告書"
                      variant="outlined"
                      density="comfortable"
                      accept=".pdf,.jpg,.jpeg,.png"
                      prepend-icon="mdi-file-document-outline"
                      @update:model-value="handleFileChange('inspectionReport')"
                    ></v-file-input>

                    <div v-if="localFormData.inspectionReportPreview" class="mt-2">
                      <v-img
                        :src="localFormData.inspectionReportPreview"
                        max-height="200"
                        contain
                        class="bg-grey-lighten-3 rounded"
                      ></v-img>
                    </div>
                  </v-col>

                  <v-col cols="12" md="6">
                    <v-file-input
                      v-model="localFormData.paymentReceipt"
                      label="領款收據"
                      variant="outlined"
                      density="comfortable"
                      accept=".pdf,.jpg,.jpeg,.png"
                      prepend-icon="mdi-receipt"
                      @update:model-value="handleFileChange('paymentReceipt')"
                    ></v-file-input>

                    <div v-if="localFormData.paymentReceiptPreview" class="mt-2">
                      <v-img
                        :src="localFormData.paymentReceiptPreview"
                        max-height="200"
                        contain
                        class="bg-grey-lighten-3 rounded"
                      ></v-img>
                    </div>
                  </v-col>
                </v-row>

                <v-row>
                  <v-col cols="12" md="6">
                    <v-file-input
                      v-model="localFormData.designDrawing"
                      label="設計圖"
                      variant="outlined"
                      density="comfortable"
                      accept=".pdf,.jpg,.jpeg,.png,.dwg,.dxf"
                      prepend-icon="mdi-drawing"
                      @update:model-value="handleFileChange('designDrawing')"
                    ></v-file-input>

                    <div v-if="localFormData.designDrawingPreview" class="mt-2">
                      <v-img
                        :src="localFormData.designDrawingPreview"
                        max-height="200"
                        contain
                        class="bg-grey-lighten-3 rounded"
                      ></v-img>
                    </div>
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

// Form validation references
const form = ref(null);
const localValid = ref(true);

// 本地表單數據
const localFormData = reactive({
  // 申請資料
  idCardFront: null,
  idCardBack: null,
  idCardFrontPreview: null,
  idCardBackPreview: null,
  applicationFile: null,
  applicationFilePreview: null,

  // 土地資料
  landRegistration: null,
  landRegistrationPreview: null,
  landMap: null,
  landMapPreview: null,
  leaseAgreement: null,
  leaseAgreementPreview: null,
  landUseConsent: null,
  landUseConsentPreview: null,

  // 其他資料
  inspectionRecord: null,
  inspectionRecordPreview: null,
  planningDoc: null,
  planningDocPreview: null,
  subsidy: null,
  subsidyPreview: null,
  workInspection: null,
  workInspectionPreview: null,
  inspectionReport: null,
  inspectionReportPreview: null,
  paymentReceipt: null,
  paymentReceiptPreview: null,
  designDrawing: null,
  designDrawingPreview: null,

  // 檔案上傳狀態
  uploadStatus: {
    idFront: false,
    idBack: false,
    applicationFile: false,
    landReg: false,
    landMap: false,
    lease: false,
    landUse: false,
    inspection: false,
    planning: false,
    subsidy: false,
    workInspection: false,
    inspectionReport: false,
    paymentReceipt: false,
    designDrawing: false
  },

  // Always set to true for seamless navigation
  valid: true
});

// 判斷檔案是否為圖片類型
const isImageFile = (file) => {
  if (!file) return false;

  // Handle string URLs (like placeholders or previously saved images)
  if (typeof file === 'string') return true;

  const imageTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/jpg'];
  return file instanceof File && imageTypes.includes(file.type);
};

// 處理檔案變更並產生預覽（如果是圖片）
const handleFileChange = (type: string) => {
  // 更新檔案上傳狀態
  localFormData.uploadStatus[type] = true;

  // 根據不同類型的檔案處理預覽
  switch(type) {
    case 'idFront':
      createPreview(localFormData.idCardFront, 'idCardFrontPreview');
      break;
    case 'idBack':
      createPreview(localFormData.idCardBack, 'idCardBackPreview');
      break;
    case 'applicationFile':
      createPreview(localFormData.applicationFile, 'applicationFilePreview');
      break;
    case 'landReg':
      createPreview(localFormData.landRegistration, 'landRegistrationPreview');
      break;
    case 'landMap':
      createPreview(localFormData.landMap, 'landMapPreview');
      break;
    case 'lease':
      createPreview(localFormData.leaseAgreement, 'leaseAgreementPreview');
      break;
    case 'landUse':
      createPreview(localFormData.landUseConsent, 'landUseConsentPreview');
      break;
    case 'inspection':
      createPreview(localFormData.inspectionRecord, 'inspectionRecordPreview');
      break;
    case 'planning':
      createPreview(localFormData.planningDoc, 'planningDocPreview');
      break;
    case 'subsidy':
      createPreview(localFormData.subsidy, 'subsidyPreview');
      break;
    case 'workInspection':
      createPreview(localFormData.workInspection, 'workInspectionPreview');
      break;
    case 'inspectionReport':
      createPreview(localFormData.inspectionReport, 'inspectionReportPreview');
      break;
    case 'paymentReceipt':
      createPreview(localFormData.paymentReceipt, 'paymentReceiptPreview');
      break;
    case 'designDrawing':
      createPreview(localFormData.designDrawing, 'designDrawingPreview');
      break;
  }

  updateFormData();
};

// Helper function to create previews
const createPreview = (file, previewKey) => {
  if (isImageFile(file)) {
    // Clean up existing preview if it's a blob URL
    if (localFormData[previewKey] &&
        typeof localFormData[previewKey] === 'string' &&
        localFormData[previewKey].startsWith('blob:')) {
      URL.revokeObjectURL(localFormData[previewKey]);
    }

    // Create new preview if file is a File object
    if (file instanceof File) {
      localFormData[previewKey] = URL.createObjectURL(file);
    }
  }
};

// 更新父組件數據
const updateFormData = () => {
  emit('update:formData', {
    ...props.formData,
    ...localFormData,
    valid: true // Always true for seamless navigation
  });
};

// 清理所有預覽資源的函數
const cleanupAllPreviews = () => {
  const previewKeys = [
    'idCardFrontPreview', 'idCardBackPreview', 'applicationFilePreview',
    'landRegistrationPreview', 'landMapPreview', 'leaseAgreementPreview',
    'landUseConsentPreview', 'inspectionRecordPreview', 'planningDocPreview',
    'subsidyPreview', 'workInspectionPreview', 'inspectionReportPreview',
    'paymentReceiptPreview', 'designDrawingPreview'
  ];

  previewKeys.forEach(key => {
    if (localFormData[key] &&
        typeof localFormData[key] === 'string' &&
        localFormData[key].startsWith('blob:')) {
      URL.revokeObjectURL(localFormData[key]);
      localFormData[key] = null;
    }
  });
};

// 初始化數據
onMounted(() => {
  console.log("Step 8 mounted, formData:", props.formData);

  // 從父組件接收數據
  if (props.formData) {
    // 設置基本屬性
    Object.keys(localFormData).forEach(key => {
      if (props.formData[key] !== undefined) {
        if (key === 'uploadStatus') {
          // Handle nested uploadStatus object
          if (props.formData.uploadStatus) {
            Object.keys(props.formData.uploadStatus).forEach(statusKey => {
              if (props.formData.uploadStatus[statusKey] !== undefined) {
                localFormData.uploadStatus[statusKey] = props.formData.uploadStatus[statusKey];
              }
            });
          }
        } else {
          // Handle normal properties
          localFormData[key] = props.formData[key];
        }
      }
    });
  }

  // Set example data for demonstration purposes
  if (!localFormData.idCardFrontPreview) {
    localFormData.idCardFrontPreview = 'https://via.placeholder.com/400x250?text=身分證正面示例';
    localFormData.uploadStatus.idFront = true;
  }

  if (!localFormData.idCardBackPreview) {
    localFormData.idCardBackPreview = 'https://via.placeholder.com/400x250?text=身分證反面示例';
    localFormData.uploadStatus.idBack = true;
  }

  if (!localFormData.landRegistrationPreview) {
    localFormData.landRegistrationPreview = 'https://via.placeholder.com/400x250?text=土地登記謄本示例';
    localFormData.uploadStatus.landReg = true;
  }

  if (!localFormData.landMapPreview) {
    localFormData.landMapPreview = 'https://via.placeholder.com/400x250?text=地籍圖謄本示例';
    localFormData.uploadStatus.landMap = true;
  }

  // Initial update to parent
  updateFormData();
});

// 監聽父組件數據變化
watch(() => props.formData, (newVal) => {
  if (newVal) {
    // Simple re-copy of new values, skipping complex file objects
    Object.keys(localFormData).forEach(key => {
      if (key !== 'uploadStatus' && newVal[key] !== undefined &&
          !(newVal[key] instanceof File) && // Skip File objects which can't be deeply compared
          JSON.stringify(newVal[key]) !== JSON.stringify(localFormData[key])) {
        localFormData[key] = newVal[key];
      }
    });

    // Handle uploadStatus specifically
    if (newVal.uploadStatus) {
      Object.keys(newVal.uploadStatus).forEach(statusKey => {
        if (newVal.uploadStatus[statusKey] !== undefined &&
            newVal.uploadStatus[statusKey] !== localFormData.uploadStatus[statusKey]) {
          localFormData.uploadStatus[statusKey] = newVal.uploadStatus[statusKey];
        }
      });
    }
  }
}, { deep: true });

// Watch local form validation status
watch(localValid, (newVal) => {
  if (props.formData?.valid !== newVal) {
    updateFormData();
  }
});

// Clean up on component unmount
onUnmounted(() => {
  cleanupAllPreviews();
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

.text-red {
  color: red;
}
</style>
