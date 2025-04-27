<template>
  <div class="step-content" ref="stepContent">
    <v-card class="mb-0 pa-0" flat>
      <v-card-text class="pb-0 pt-0">
        <v-form ref="form" v-model="localValid" @submit.prevent>
          <!-- 勘查資訊區域 -->
          <v-card class="mb-4" variant="outlined">
            <v-card-title class="bg-light-blue-lighten-4 d-flex align-center py-2 px-4">
              <v-icon class="me-2" size="small">mdi-clipboard-check</v-icon>
              <span class="text-subtitle-1 font-weight-medium">勘查資訊</span>
            </v-card-title>

            <v-card-text class="pa-4">
              <v-sheet class="pa-3 rounded" color="grey-lighten-5">
                <v-row>
                  <v-col cols="12">
                    <v-text-field
                      v-model="localFormData.inspector"
                      label="勘查人員"
                      variant="outlined"
                      density="comfortable"
                      :rules="[v => !!v || '請填寫勘查人員']"
                    ></v-text-field>
                  </v-col>
                </v-row>

                <v-row>
                  <v-col cols="12">
                    <label class="text-body-2 font-weight-medium mb-2 d-block">勘查結果</label>
                    <div class="d-flex align-center">
                      <v-radio-group
                        v-model="localFormData.inspectionResult"
                        inline
                        :rules="[v => !!v || '請選擇勘查結果']"
                      >
                        <v-radio value="comply" label="符合"></v-radio>
                        <v-radio value="notComply" label="不符合"></v-radio>
                        <v-radio value="other" label="其他"></v-radio>
                      </v-radio-group>
                    </div>
                  </v-col>
                </v-row>

                <v-row v-if="localFormData.inspectionResult === 'notComply' || localFormData.inspectionResult === 'other'">
                  <v-col cols="12">
                    <v-textarea
                      v-model="localFormData.reason"
                      label="原因說明"
                      variant="outlined"
                      density="comfortable"
                      rows="3"
                      auto-grow
                      :rules="reasonRules"
                    ></v-textarea>
                  </v-col>
                </v-row>

                <v-row>
                  <v-col cols="12" md="6">
                    <v-text-field
                      v-model="localFormData.inspectionDate"
                      label="勘查日期"
                      variant="outlined"
                      density="comfortable"
                      :rules="[v => !!v || '請選擇勘查日期']"
                      readonly
                      @click="datePickerDialog = true"
                    >
                      <template v-slot:append>
                        <v-icon>mdi-calendar</v-icon>
                      </template>
                    </v-text-field>

                    <v-dialog
                      v-model="datePickerDialog"
                      width="auto"
                    >
                      <v-card>
                        <v-card-text>
                          <v-date-picker
                            v-model="localFormData.inspectionDate"
                            @update:model-value="datePickerDialog = false"
                          ></v-date-picker>
                        </v-card-text>
                      </v-card>
                    </v-dialog>
                  </v-col>
                </v-row>

                <v-row>
                  <v-col cols="12">
                    <v-textarea
                      v-model="localFormData.remarks"
                      label="備註"
                      variant="outlined"
                      density="comfortable"
                      rows="3"
                      auto-grow
                    ></v-textarea>
                  </v-col>
                </v-row>
              </v-sheet>
            </v-card-text>
          </v-card>

          <!-- 照片上傳區域 -->
          <v-card variant="outlined">
            <v-card-title class="bg-light-blue-lighten-4 d-flex align-center py-2 px-4">
              <v-icon class="me-2" size="small">mdi-camera</v-icon>
              <span class="text-subtitle-1 font-weight-medium">現場照片</span>
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
                      label="選擇照片檔"
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
                      label="選擇照片檔"
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
            :disabled="currentStep === 1"
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
    </v-card> -->
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

// Use correct event names to match edit.vue
const emit = defineEmits(['update:formData', 'validated', 'go-back']);

// Set default valid state to true for demo
const localValid = ref(true);
const form = ref(null);
const datePickerDialog = ref(false);

// Create isValid computed property that always returns true for demo
const isValid = computed(() => true);

// 本地表單數據
const localFormData = reactive({
  inspector: '',
  inspectionResult: '',
  reason: '',
  inspectionDate: '',
  remarks: '',
  beforeConstructionPhoto: null,
  afterConstructionPhoto: null,
  beforePhotoPreview: null,
  afterPhotoPreview: null,
  valid: true // Always set to true for demo
});

// 驗證規則
const reasonRules = computed(() => {
  if (localFormData.inspectionResult === 'notComply' || localFormData.inspectionResult === 'other') {
    return [v => !!v || '請填寫原因說明'];
  }
  return [];
});

const photoRules = [v => !!v || '請上傳照片'];

// 处理照片预览 (simplified to handle string URLs stored in localStorage)
const handlePhotoChange = (type: 'before' | 'after') => {
  const file = type === 'before'
    ? localFormData.beforeConstructionPhoto
    : localFormData.afterConstructionPhoto;

  if (file) {
    // Only create object URLs for actual File objects
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

// Navigate to previous step - simplified for localStorage demo
const goToPreviousStep = () => {
  // Always update data before going back
  updateFormData();

  console.log('Going back from step 5');
  emit('go-back'); // FIXED: use 'go-back' to match edit.vue
};

// Navigate to next step - simplified for localStorage demo
const goToNextStep = async () => {
  // Always update data before moving forward
  updateFormData();

  console.log('Emitting validated event for step 5');
  emit('validated', { valid: true, step: 5 });
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
  }

  // 設置默認勘查日期（如果未設置）
  if (!localFormData.inspectionDate) {
    // 使用當前日期
    const today = new Date();
    const year = today.getFullYear();
    const month = String(today.getMonth() + 1).padStart(2, '0');
    const day = String(today.getDate()).padStart(2, '0');
    localFormData.inspectionDate = `${year}-${month}-${day}`;
  }

  // Set example data for demo
  if (!localFormData.inspector) {
    localFormData.inspector = '張工程師';
  }

  if (!localFormData.inspectionResult) {
    localFormData.inspectionResult = 'comply';
  }

  if (!localFormData.remarks) {
    localFormData.remarks = '設施符合規定，農地平整，排水良好。';
  }

  // Set example photo previews if none exist
  if (!localFormData.beforePhotoPreview) {
    localFormData.beforePhotoPreview = 'https://via.placeholder.com/400x300?text=施工前照片示例';
  }

  if (!localFormData.afterPhotoPreview) {
    localFormData.afterPhotoPreview = 'https://via.placeholder.com/400x300?text=施工後照片示例';
  }

  // Initial update to parent
  updateFormData();
});

// 監聽父組件數據變化
watch(() => props.formData, (newVal) => {
  if (newVal) {
    Object.keys(localFormData).forEach(key => {
      if (newVal[key] !== undefined &&
          JSON.stringify(newVal[key]) !== JSON.stringify(localFormData[key])) {
        localFormData[key] = newVal[key];
      }
    });
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

.bg-light-blue-lighten-4 {
  background-color: #B3E5FC !important;
}

.text-red {
  color: red;
}
</style>
