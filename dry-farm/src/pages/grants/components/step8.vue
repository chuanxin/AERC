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

    <!-- <v-card class="step-navigation-card ma-0 pa-0" flat>
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
    </v-card> -->
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, watch, computed, onUnmounted } from 'vue';

const props = defineProps<{
  formData: any;  // 接收父組件數據
  currentStep: number;
}>();

// FIXED: Changed 'goBack' to 'go-back' to match edit.vue expectations
const emit = defineEmits(['update:formData', 'validated', 'go-back']);
// Default to valid for demo purposes
const localValid = ref(true);
const form = ref(null);

// ADDED: Create isValid computed property that always returns true for demo
const isValid = computed(() => true);

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

  // ADDED: Always set to true for demo
  valid: true
});

// 判斷檔案是否為圖片類型
const isImageFile = (file) => {
  if (!file) return false;

  if (typeof file === 'string') return true; // For demo URLs

  const imageTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/jpg'];
  return imageTypes.includes(file.type);
};

// 處理檔案變更並產生預覽（如果是圖片）- MODIFIED for localStorage compatibility
const handleFileChange = (type: string) => {
  // 更新檔案上傳狀態
  localFormData.uploadStatus[type] = true;

  // 根據不同類型的檔案處理預覽
  switch(type) {
    case 'idFront':
      if (isImageFile(localFormData.idCardFront)) {
        if (localFormData.idCardFrontPreview &&
            typeof localFormData.idCardFrontPreview === 'string' &&
            localFormData.idCardFrontPreview.startsWith('blob:')) {
          URL.revokeObjectURL(localFormData.idCardFrontPreview);
        }
        if (localFormData.idCardFront instanceof File) {
          localFormData.idCardFrontPreview = URL.createObjectURL(localFormData.idCardFront);
        }
      }
      break;

    case 'idBack':
      if (isImageFile(localFormData.idCardBack)) {
        if (localFormData.idCardBackPreview &&
            typeof localFormData.idCardBackPreview === 'string' &&
            localFormData.idCardBackPreview.startsWith('blob:')) {
          URL.revokeObjectURL(localFormData.idCardBackPreview);
        }
        if (localFormData.idCardBack instanceof File) {
          localFormData.idCardBackPreview = URL.createObjectURL(localFormData.idCardBack);
        }
      }
      break;

    case 'applicationFile':
      if (isImageFile(localFormData.applicationFile)) {
        if (localFormData.applicationFilePreview &&
            typeof localFormData.applicationFilePreview === 'string' &&
            localFormData.applicationFilePreview.startsWith('blob:')) {
          URL.revokeObjectURL(localFormData.applicationFilePreview);
        }
        if (localFormData.applicationFile instanceof File) {
          localFormData.applicationFilePreview = URL.createObjectURL(localFormData.applicationFile);
        }
      }
      break;

    case 'landReg':
      if (isImageFile(localFormData.landRegistration)) {
        if (localFormData.landRegistrationPreview &&
            typeof localFormData.landRegistrationPreview === 'string' &&
            localFormData.landRegistrationPreview.startsWith('blob:')) {
          URL.revokeObjectURL(localFormData.landRegistrationPreview);
        }
        if (localFormData.landRegistration instanceof File) {
          localFormData.landRegistrationPreview = URL.createObjectURL(localFormData.landRegistration);
        }
      }
      break;

    case 'landMap':
      if (isImageFile(localFormData.landMap)) {
        if (localFormData.landMapPreview &&
            typeof localFormData.landMapPreview === 'string' &&
            localFormData.landMapPreview.startsWith('blob:')) {
          URL.revokeObjectURL(localFormData.landMapPreview);
        }
        if (localFormData.landMap instanceof File) {
          localFormData.landMapPreview = URL.createObjectURL(localFormData.landMap);
        }
      }
      break;

    case 'lease':
      if (isImageFile(localFormData.leaseAgreement)) {
        if (localFormData.leaseAgreementPreview &&
            typeof localFormData.leaseAgreementPreview === 'string' &&
            localFormData.leaseAgreementPreview.startsWith('blob:')) {
          URL.revokeObjectURL(localFormData.leaseAgreementPreview);
        }
        if (localFormData.leaseAgreement instanceof File) {
          localFormData.leaseAgreementPreview = URL.createObjectURL(localFormData.leaseAgreement);
        }
      }
      break;

    case 'landUse':
      if (isImageFile(localFormData.landUseConsent)) {
        if (localFormData.landUseConsentPreview &&
            typeof localFormData.landUseConsentPreview === 'string' &&
            localFormData.landUseConsentPreview.startsWith('blob:')) {
          URL.revokeObjectURL(localFormData.landUseConsentPreview);
        }
        if (localFormData.landUseConsent instanceof File) {
          localFormData.landUseConsentPreview = URL.createObjectURL(localFormData.landUseConsent);
        }
      }
      break;

    case 'inspection':
      if (isImageFile(localFormData.inspectionRecord)) {
        if (localFormData.inspectionRecordPreview &&
            typeof localFormData.inspectionRecordPreview === 'string' &&
            localFormData.inspectionRecordPreview.startsWith('blob:')) {
          URL.revokeObjectURL(localFormData.inspectionRecordPreview);
        }
        if (localFormData.inspectionRecord instanceof File) {
          localFormData.inspectionRecordPreview = URL.createObjectURL(localFormData.inspectionRecord);
        }
      }
      break;

    case 'planning':
      if (isImageFile(localFormData.planningDoc)) {
        if (localFormData.planningDocPreview &&
            typeof localFormData.planningDocPreview === 'string' &&
            localFormData.planningDocPreview.startsWith('blob:')) {
          URL.revokeObjectURL(localFormData.planningDocPreview);
        }
        if (localFormData.planningDoc instanceof File) {
          localFormData.planningDocPreview = URL.createObjectURL(localFormData.planningDoc);
        }
      }
      break;

    case 'subsidy':
      if (isImageFile(localFormData.subsidy)) {
        if (localFormData.subsidyPreview &&
            typeof localFormData.subsidyPreview === 'string' &&
            localFormData.subsidyPreview.startsWith('blob:')) {
          URL.revokeObjectURL(localFormData.subsidyPreview);
        }
        if (localFormData.subsidy instanceof File) {
          localFormData.subsidyPreview = URL.createObjectURL(localFormData.subsidy);
        }
      }
      break;

    case 'workInspection':
      if (isImageFile(localFormData.workInspection)) {
        if (localFormData.workInspectionPreview &&
            typeof localFormData.workInspectionPreview === 'string' &&
            localFormData.workInspectionPreview.startsWith('blob:')) {
          URL.revokeObjectURL(localFormData.workInspectionPreview);
        }
        if (localFormData.workInspection instanceof File) {
          localFormData.workInspectionPreview = URL.createObjectURL(localFormData.workInspection);
        }
      }
      break;

    case 'inspectionReport':
      if (isImageFile(localFormData.inspectionReport)) {
        if (localFormData.inspectionReportPreview &&
            typeof localFormData.inspectionReportPreview === 'string' &&
            localFormData.inspectionReportPreview.startsWith('blob:')) {
          URL.revokeObjectURL(localFormData.inspectionReportPreview);
        }
        if (localFormData.inspectionReport instanceof File) {
          localFormData.inspectionReportPreview = URL.createObjectURL(localFormData.inspectionReport);
        }
      }
      break;

    case 'paymentReceipt':
      if (isImageFile(localFormData.paymentReceipt)) {
        if (localFormData.paymentReceiptPreview &&
            typeof localFormData.paymentReceiptPreview === 'string' &&
            localFormData.paymentReceiptPreview.startsWith('blob:')) {
          URL.revokeObjectURL(localFormData.paymentReceiptPreview);
        }
        if (localFormData.paymentReceipt instanceof File) {
          localFormData.paymentReceiptPreview = URL.createObjectURL(localFormData.paymentReceipt);
        }
      }
      break;

    case 'designDrawing':
      if (isImageFile(localFormData.designDrawing)) {
        if (localFormData.designDrawingPreview &&
            typeof localFormData.designDrawingPreview === 'string' &&
            localFormData.designDrawingPreview.startsWith('blob:')) {
          URL.revokeObjectURL(localFormData.designDrawingPreview);
        }
        if (localFormData.designDrawing instanceof File) {
          localFormData.designDrawingPreview = URL.createObjectURL(localFormData.designDrawing);
        }
      }
      break;
  }

  updateFormData();
};

// 上一步 - FIXED: Changed to use 'go-back' instead of 'goBack'
const goToPreviousStep = () => {
  // Update data before going back
  updateFormData();

  console.log('Going back from step 8');
  emit('go-back');
};

// 下一步（完成）- MODIFIED for simplified localStorage approach
const goToNextStep = async () => {
  // Always update and consider valid for demo
  updateFormData();

  console.log('Emitting validated event for step 8');
  emit('validated', { valid: true, step: 8 });
};

// 更新父組件數據 - MODIFIED to always set valid: true
const updateFormData = () => {
  emit('update:formData', {
    ...props.formData,
    ...localFormData,
    valid: true // Always valid for demo purposes
  });
};

// 表單驗證 - SIMPLIFIED for demo purposes
const validate = async () => {
  updateFormData();
  return { valid: true }; // Always return valid for demo
};

// 清理預覽資源的函數 - ENHANCED to handle string URLs
const cleanupPreviews = () => {
  // Only clean up blob URLs, not external URLs
  if (localFormData.idCardFrontPreview && typeof localFormData.idCardFrontPreview === 'string' &&
      localFormData.idCardFrontPreview.startsWith('blob:'))
    URL.revokeObjectURL(localFormData.idCardFrontPreview);

  if (localFormData.idCardBackPreview && typeof localFormData.idCardBackPreview === 'string' &&
      localFormData.idCardBackPreview.startsWith('blob:'))
    URL.revokeObjectURL(localFormData.idCardBackPreview);

  if (localFormData.applicationFilePreview && typeof localFormData.applicationFilePreview === 'string' &&
      localFormData.applicationFilePreview.startsWith('blob:'))
    URL.revokeObjectURL(localFormData.applicationFilePreview);

  if (localFormData.landRegistrationPreview && typeof localFormData.landRegistrationPreview === 'string' &&
      localFormData.landRegistrationPreview.startsWith('blob:'))
    URL.revokeObjectURL(localFormData.landRegistrationPreview);

  if (localFormData.landMapPreview && typeof localFormData.landMapPreview === 'string' &&
      localFormData.landMapPreview.startsWith('blob:'))
    URL.revokeObjectURL(localFormData.landMapPreview);

  if (localFormData.leaseAgreementPreview && typeof localFormData.leaseAgreementPreview === 'string' &&
      localFormData.leaseAgreementPreview.startsWith('blob:'))
    URL.revokeObjectURL(localFormData.leaseAgreementPreview);

  if (localFormData.landUseConsentPreview && typeof localFormData.landUseConsentPreview === 'string' &&
      localFormData.landUseConsentPreview.startsWith('blob:'))
    URL.revokeObjectURL(localFormData.landUseConsentPreview);

  if (localFormData.inspectionRecordPreview && typeof localFormData.inspectionRecordPreview === 'string' &&
      localFormData.inspectionRecordPreview.startsWith('blob:'))
    URL.revokeObjectURL(localFormData.inspectionRecordPreview);

  if (localFormData.planningDocPreview && typeof localFormData.planningDocPreview === 'string' &&
      localFormData.planningDocPreview.startsWith('blob:'))
    URL.revokeObjectURL(localFormData.planningDocPreview);

  if (localFormData.subsidyPreview && typeof localFormData.subsidyPreview === 'string' &&
      localFormData.subsidyPreview.startsWith('blob:'))
    URL.revokeObjectURL(localFormData.subsidyPreview);

  if (localFormData.workInspectionPreview && typeof localFormData.workInspectionPreview === 'string' &&
      localFormData.workInspectionPreview.startsWith('blob:'))
    URL.revokeObjectURL(localFormData.workInspectionPreview);

  if (localFormData.inspectionReportPreview && typeof localFormData.inspectionReportPreview === 'string' &&
      localFormData.inspectionReportPreview.startsWith('blob:'))
    URL.revokeObjectURL(localFormData.inspectionReportPreview);

  if (localFormData.paymentReceiptPreview && typeof localFormData.paymentReceiptPreview === 'string' &&
      localFormData.paymentReceiptPreview.startsWith('blob:'))
    URL.revokeObjectURL(localFormData.paymentReceiptPreview);

  if (localFormData.designDrawingPreview && typeof localFormData.designDrawingPreview === 'string' &&
      localFormData.designDrawingPreview.startsWith('blob:'))
    URL.revokeObjectURL(localFormData.designDrawingPreview);
};

// 初始化數據 - ENHANCED with sample preview URLs for better demo experience
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

  // ADDED: Set placeholder previews for demo purposes if none exist
  if (!localFormData.idCardFrontPreview) {
    localFormData.idCardFrontPreview = 'https://via.placeholder.com/400x250?text=身分證正面';
    localFormData.uploadStatus.idFront = true;
  }

  if (!localFormData.idCardBackPreview) {
    localFormData.idCardBackPreview = 'https://via.placeholder.com/400x250?text=身分證反面';
    localFormData.uploadStatus.idBack = true;
  }

  if (!localFormData.landRegistrationPreview) {
    localFormData.landRegistrationPreview = 'https://via.placeholder.com/400x250?text=土地登記謄本';
    localFormData.uploadStatus.landReg = true;
  }

  if (!localFormData.landMapPreview) {
    localFormData.landMapPreview = 'https://via.placeholder.com/400x250?text=地籍圖謄本';
    localFormData.uploadStatus.landMap = true;
  }

  // Initial update to parent
  updateFormData();
});

// 監聽父組件數據變化 - SIMPLIFIED for demo purposes
watch(() => props.formData, (newVal) => {
  if (newVal) {
    // Simplify for demo - just update form data
    updateFormData();
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
