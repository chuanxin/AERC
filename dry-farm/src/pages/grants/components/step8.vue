<template>
  <div class="step-content" ref="stepContent">
    <v-card class="mb-6 pa-0" flat>
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
            @click="goToNextStep"
            size="large"
            rounded="pill"
          >
            完成
            <v-icon end>mdi-check</v-icon>
          </v-btn>
        </div>
      </div>
    </v-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, watch, computed } from 'vue';

const props = defineProps<{
  formData: any;  // 接收父組件數據
  currentStep: number;
}>();

const emit = defineEmits(['update:formData', 'validated', 'goBack']);
const localValid = ref(true); // 由於所有欄位都是選填，預設為有效
const form = ref(null);

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
  }
});

// 判斷檔案是否為圖片類型
const isImageFile = (file) => {
  if (!file) return false;

  const imageTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/jpg'];
  return imageTypes.includes(file.type);
};

// 處理檔案變更並產生預覽（如果是圖片）
const handleFileChange = (type: string) => {
  // 更新檔案上傳狀態
  localFormData.uploadStatus[type] = true;

  // 根據不同類型的檔案處理預覽
  switch(type) {
    case 'idFront':
      if (isImageFile(localFormData.idCardFront)) {
        if (localFormData.idCardFrontPreview) {
          URL.revokeObjectURL(localFormData.idCardFrontPreview);
        }
        localFormData.idCardFrontPreview = URL.createObjectURL(localFormData.idCardFront);
      } else {
        localFormData.idCardFrontPreview = null;
      }
      break;

    case 'idBack':
      if (isImageFile(localFormData.idCardBack)) {
        if (localFormData.idCardBackPreview) {
          URL.revokeObjectURL(localFormData.idCardBackPreview);
        }
        localFormData.idCardBackPreview = URL.createObjectURL(localFormData.idCardBack);
      } else {
        localFormData.idCardBackPreview = null;
      }
      break;

    case 'applicationFile':
      if (isImageFile(localFormData.applicationFile)) {
        if (localFormData.applicationFilePreview) {
          URL.revokeObjectURL(localFormData.applicationFilePreview);
        }
        localFormData.applicationFilePreview = URL.createObjectURL(localFormData.applicationFile);
      } else {
        localFormData.applicationFilePreview = null;
      }
      break;

    case 'landReg':
      if (isImageFile(localFormData.landRegistration)) {
        if (localFormData.landRegistrationPreview) {
          URL.revokeObjectURL(localFormData.landRegistrationPreview);
        }
        localFormData.landRegistrationPreview = URL.createObjectURL(localFormData.landRegistration);
      } else {
        localFormData.landRegistrationPreview = null;
      }
      break;

    case 'landMap':
      if (isImageFile(localFormData.landMap)) {
        if (localFormData.landMapPreview) {
          URL.revokeObjectURL(localFormData.landMapPreview);
        }
        localFormData.landMapPreview = URL.createObjectURL(localFormData.landMap);
      } else {
        localFormData.landMapPreview = null;
      }
      break;

    case 'lease':
      if (isImageFile(localFormData.leaseAgreement)) {
        if (localFormData.leaseAgreementPreview) {
          URL.revokeObjectURL(localFormData.leaseAgreementPreview);
        }
        localFormData.leaseAgreementPreview = URL.createObjectURL(localFormData.leaseAgreement);
      } else {
        localFormData.leaseAgreementPreview = null;
      }
      break;

    case 'landUse':
      if (isImageFile(localFormData.landUseConsent)) {
        if (localFormData.landUseConsentPreview) {
          URL.revokeObjectURL(localFormData.landUseConsentPreview);
        }
        localFormData.landUseConsentPreview = URL.createObjectURL(localFormData.landUseConsent);
      } else {
        localFormData.landUseConsentPreview = null;
      }
      break;

    case 'inspection':
      if (isImageFile(localFormData.inspectionRecord)) {
        if (localFormData.inspectionRecordPreview) {
          URL.revokeObjectURL(localFormData.inspectionRecordPreview);
        }
        localFormData.inspectionRecordPreview = URL.createObjectURL(localFormData.inspectionRecord);
      } else {
        localFormData.inspectionRecordPreview = null;
      }
      break;

    case 'planning':
      if (isImageFile(localFormData.planningDoc)) {
        if (localFormData.planningDocPreview) {
          URL.revokeObjectURL(localFormData.planningDocPreview);
        }
        localFormData.planningDocPreview = URL.createObjectURL(localFormData.planningDoc);
      } else {
        localFormData.planningDocPreview = null;
      }
      break;

    case 'subsidy':
      if (isImageFile(localFormData.subsidy)) {
        if (localFormData.subsidyPreview) {
          URL.revokeObjectURL(localFormData.subsidyPreview);
        }
        localFormData.subsidyPreview = URL.createObjectURL(localFormData.subsidy);
      } else {
        localFormData.subsidyPreview = null;
      }
      break;

    case 'workInspection':
      if (isImageFile(localFormData.workInspection)) {
        if (localFormData.workInspectionPreview) {
          URL.revokeObjectURL(localFormData.workInspectionPreview);
        }
        localFormData.workInspectionPreview = URL.createObjectURL(localFormData.workInspection);
      } else {
        localFormData.workInspectionPreview = null;
      }
      break;

    case 'inspectionReport':
      if (isImageFile(localFormData.inspectionReport)) {
        if (localFormData.inspectionReportPreview) {
          URL.revokeObjectURL(localFormData.inspectionReportPreview);
        }
        localFormData.inspectionReportPreview = URL.createObjectURL(localFormData.inspectionReport);
      } else {
        localFormData.inspectionReportPreview = null;
      }
      break;

    case 'paymentReceipt':
      if (isImageFile(localFormData.paymentReceipt)) {
        if (localFormData.paymentReceiptPreview) {
          URL.revokeObjectURL(localFormData.paymentReceiptPreview);
        }
        localFormData.paymentReceiptPreview = URL.createObjectURL(localFormData.paymentReceipt);
      } else {
        localFormData.paymentReceiptPreview = null;
      }
      break;

    case 'designDrawing':
      if (isImageFile(localFormData.designDrawing)) {
        if (localFormData.designDrawingPreview) {
          URL.revokeObjectURL(localFormData.designDrawingPreview);
        }
        localFormData.designDrawingPreview = URL.createObjectURL(localFormData.designDrawing);
      } else {
        localFormData.designDrawingPreview = null;
      }
      break;
  }

  updateFormData();
};

// 上一步
const goToPreviousStep = () => {
  emit('goBack');
};

// 下一步（完成）
const goToNextStep = async () => {
  // 所有欄位都是選填，直接更新數據並觸發驗證事件
  updateFormData();
  emit('validated', { valid: true, step: 8 });
};

// 更新父組件數據
const updateFormData = () => {
  emit('update:formData', {
    ...props.formData,
    ...localFormData,
    valid: true // 所有欄位選填，表單始終為有效
  });
};

// 表單驗證 - 由於所有欄位都是選填，這個函數會直接返回 true
const validate = async () => {
  const { valid } = await form.value.validate();
  updateFormData();
  emit('validated', { valid: true, step: 8 });
};

// 清理預覽資源的函數
const cleanupPreviews = () => {
  // 清理所有的 URL 對象以避免內存洩漏
  if (localFormData.idCardFrontPreview) URL.revokeObjectURL(localFormData.idCardFrontPreview);
  if (localFormData.idCardBackPreview) URL.revokeObjectURL(localFormData.idCardBackPreview);
  if (localFormData.applicationFilePreview) URL.revokeObjectURL(localFormData.applicationFilePreview);
  if (localFormData.landRegistrationPreview) URL.revokeObjectURL(localFormData.landRegistrationPreview);
  if (localFormData.landMapPreview) URL.revokeObjectURL(localFormData.landMapPreview);
  if (localFormData.leaseAgreementPreview) URL.revokeObjectURL(localFormData.leaseAgreementPreview);
  if (localFormData.landUseConsentPreview) URL.revokeObjectURL(localFormData.landUseConsentPreview);
  if (localFormData.inspectionRecordPreview) URL.revokeObjectURL(localFormData.inspectionRecordPreview);
  if (localFormData.planningDocPreview) URL.revokeObjectURL(localFormData.planningDocPreview);
  if (localFormData.subsidyPreview) URL.revokeObjectURL(localFormData.subsidyPreview);
  if (localFormData.workInspectionPreview) URL.revokeObjectURL(localFormData.workInspectionPreview);
  if (localFormData.inspectionReportPreview) URL.revokeObjectURL(localFormData.inspectionReportPreview);
  if (localFormData.paymentReceiptPreview) URL.revokeObjectURL(localFormData.paymentReceiptPreview);
  if (localFormData.designDrawingPreview) URL.revokeObjectURL(localFormData.designDrawingPreview);
};

// 初始化數據
onMounted(() => {
  // 從父組件接收數據
  if (props.formData) {
    Object.keys(localFormData).forEach(key => {
      if (key !== 'uploadStatus' && props.formData[key] !== undefined) {
        localFormData[key] = props.formData[key];
      }
    });

    // 處理上傳狀態
    if (props.formData.uploadStatus) {
      Object.keys(props.formData.uploadStatus).forEach(key => {
        if (props.formData.uploadStatus[key] !== undefined) {
          localFormData.uploadStatus[key] = props.formData.uploadStatus[key];
        }
      });
    }
  }
});

// 監聽父組件數據變化
watch(() => props.formData, (newVal) => {
  if (newVal) {
    Object.keys(localFormData).forEach(key => {
      if (key !== 'uploadStatus' && newVal[key] !== undefined && newVal[key] !== localFormData[key]) {
        localFormData[key] = newVal[key];
      }
    });

    // 處理上傳狀態
    if (newVal.uploadStatus) {
      Object.keys(newVal.uploadStatus).forEach(key => {
        if (newVal.uploadStatus[key] !== undefined &&
            newVal.uploadStatus[key] !== localFormData.uploadStatus[key]) {
          localFormData.uploadStatus[key] = newVal.uploadStatus[key];
        }
      });
    }
  }
}, { deep: true });

// 監聽本地數據變化，更新父組件
watch(localFormData, () => {
  updateFormData();
}, { deep: true });

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

.text-red {
  color: red;
}
</style>
