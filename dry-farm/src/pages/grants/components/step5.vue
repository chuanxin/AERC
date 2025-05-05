<template>
  <div class="step-content" ref="stepContent">
    <v-card class="mb-0 pa-0" flat>
      <v-card-text class="pb-0 pt-0">
        <v-form ref="form" v-model="localValid" @submit.prevent>
          <!-- 勘查資訊區域 -->
          <v-card flat class="mb-4 pa-4" color="#e3f4f4" rounded="lg">
            <v-card-title class="text-subtitle-1 font-weight-bold pa-0 pb-6" style="color: #2d8c8f">
              <v-icon color="#3ea0a3" class="me-2 pb-1" size="small">mdi-clipboard-check</v-icon>
              <span>勘查資訊</span>
            </v-card-title>

            <v-sheet class="pa-3 rounded" color="white">
              <v-row>
                <v-col cols="12" md="6">
                  <v-text-field
                    v-model="localFormData.inspector"
                    label="勘查人員"
                    variant="outlined"
                    density="comfortable"
                    color="#3ea0a3"
                    bg-color="white"
                    :rules="[v => !!v || '請填寫勘查人員']"
                    @update:model-value="updateFormData"
                  />
                </v-col>

                <v-col cols="12" md="6">
                  <!-- 使用簡單的日期輸入 -->
                  <v-text-field
                    v-model="formattedInspectionDate"
                    label="勘查日期"
                    prepend-icon="mdi-calendar"
                    variant="outlined"
                    density="comfortable"
                    color="#3ea0a3"
                    bg-color="white"
                    readonly
                    @click="openDateDialog"
                    :rules="[v => !!v || '請選擇勘查日期']"
                  />

                  <!-- 自定義日期選擇對話框 -->
                  <v-dialog
                    v-model="datePickerDialog"
                    width="600"
                  >
                    <v-card>
                      <v-card-title class="text-h6 font-weight-bold" style="color: #2d8c8f">
                        選擇日期
                      </v-card-title>
                      <v-card-text>
                        <v-row>
                          <v-col cols="4">
                            <v-select
                              v-model="dateComponents.year"
                              :items="yearOptions"
                              label="年"
                              variant="outlined"
                              density="comfortable"
                              color="#3ea0a3"
                            ></v-select>
                          </v-col>
                          <v-col cols="4">
                            <v-select
                              v-model="dateComponents.month"
                              :items="monthOptions"
                              label="月"
                              variant="outlined"
                              density="comfortable"
                              color="#3ea0a3"
                            ></v-select>
                          </v-col>
                          <v-col cols="4">
                            <v-select
                              v-model="dateComponents.day"
                              :items="dayOptions"
                              label="日"
                              variant="outlined"
                              density="comfortable"
                              color="#3ea0a3"
                            ></v-select>
                          </v-col>
                        </v-row>
                      </v-card-text>
                      <v-card-actions>
                        <v-spacer></v-spacer>
                        <v-btn
                          variant="text"
                          @click="datePickerDialog = false"
                        >
                          取消
                        </v-btn>
                        <v-btn
                          color="#3ea0a3"
                          variant="text"
                          @click="confirmDateSelection"
                        >
                          確定
                        </v-btn>
                      </v-card-actions>
                    </v-card>
                  </v-dialog>
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
                      @update:model-value="updateFormData"
                      color="#3ea0a3"
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
                    color="#3ea0a3"
                    bg-color="white"
                    rows="3"
                    auto-grow
                    :rules="reasonRules"
                    @update:model-value="updateFormData"
                  />
                </v-col>
              </v-row>

              <v-row>
                <v-col cols="12">
                  <v-textarea
                    v-model="localFormData.remarks"
                    label="備註"
                    variant="outlined"
                    density="comfortable"
                    color="#3ea0a3"
                    bg-color="white"
                    rows="3"
                    auto-grow
                    @update:model-value="updateFormData"
                  />
                </v-col>
              </v-row>
            </v-sheet>
          </v-card>

          <!-- 照片上傳區域 -->
          <v-card flat class="mb-4 pa-4" color="#e3f4f4" rounded="lg">
            <v-card-title class="text-subtitle-1 font-weight-bold pa-0 pb-6" style="color: #2d8c8f">
              <v-icon color="#3ea0a3" class="me-2 pb-1" size="small">mdi-camera</v-icon>
              <span>現場照片</span>
            </v-card-title>

            <v-sheet class="pa-3 rounded" color="white">
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
                    color="#3ea0a3"
                    bg-color="white"
                    accept="image/*"
                    prepend-icon="mdi-camera"
                    :rules="photoRules"
                    @update:model-value="handlePhotoChange('before')"
                  />

                  <div v-if="localFormData.beforePhotoPreview" class="mt-2">
                    <v-img
                      :src="localFormData.beforePhotoPreview"
                      max-height="200"
                      contain
                      class="bg-grey-lighten-3 rounded"
                    />
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
                    color="#3ea0a3"
                    bg-color="white"
                    accept="image/*"
                    prepend-icon="mdi-camera"
                    :rules="photoRules"
                    @update:model-value="handlePhotoChange('after')"
                  />

                  <div v-if="localFormData.afterPhotoPreview" class="mt-2">
                    <v-img
                      :src="localFormData.afterPhotoPreview"
                      max-height="200"
                      contain
                      class="bg-grey-lighten-3 rounded"
                    />
                  </div>
                </v-col>
              </v-row>
            </v-sheet>
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

// Event emitters - using expected event names from edit.vue
const emit = defineEmits(['update:formData', 'validated', 'go-back']);

// Access grants store
const grantsStore = useGrantsStore();

// Form ref and validation state
const form = ref(null);
const localValid = ref(true);

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
  valid: true // Always true for seamless navigation
});

// 驗證規則
const reasonRules = computed(() => {
  if (localFormData.inspectionResult === 'notComply' || localFormData.inspectionResult === 'other') {
    return [v => !!v || '請填寫原因說明'];
  }
  return [];
});

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

// 日期格式化（民國年）
const formattedInspectionDate = computed(() => {
  if (!localFormData.inspectionDate) return '';

  try {
    const date = new Date(localFormData.inspectionDate);
    if (isNaN(date.getTime())) return ''; // 無效日期

    // 計算民國年
    const twYear = date.getFullYear() - 1911;
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');

    return `民國 ${twYear} 年 ${month} 月 ${day} 日`;
  } catch (error) {
    console.error('日期格式化錯誤:', error);
    return '';
  }
});

// 日期對話框狀態
const datePickerDialog = ref(false);

// 日期選擇器元件
const dateComponents = reactive({
  year: new Date().getFullYear(),
  month: new Date().getMonth() + 1,
  day: new Date().getDate()
});

// 產生年份選項 (民國年)
const yearOptions = computed(() => {
  const currentYear = new Date().getFullYear();
  const years = [];
  // 產生從當前年份到五年前的年份選項
  for (let year = currentYear - 5; year <= currentYear; year++) {
    years.push({
      title: `民國 ${year - 1911} 年`,
      value: year
    });
  }
  return years;
});

// 產生月份選項
const monthOptions = computed(() => {
  return Array.from({ length: 12 }, (_, i) => ({
    title: `${i + 1} 月`,
    value: i + 1
  }));
});

// 產生日期選項 (考慮每月天數)
const dayOptions = computed(() => {
  const year = dateComponents.year;
  const month = dateComponents.month;

  // 計算當月天數
  const daysInMonth = new Date(year, month, 0).getDate();

  return Array.from({ length: daysInMonth }, (_, i) => ({
    title: `${i + 1} 日`,
    value: i + 1
  }));
});

// 開啟日期選擇對話框
const openDateDialog = () => {
  // 如果已有日期，解析它
  if (localFormData.inspectionDate) {
    try {
      const date = new Date(localFormData.inspectionDate);
      if (!isNaN(date.getTime())) {
        dateComponents.year = date.getFullYear();
        dateComponents.month = date.getMonth() + 1;
        dateComponents.day = date.getDate();
      }
    } catch (error) {
      console.error('日期解析錯誤:', error);
      // 預設為今天
      const today = new Date();
      dateComponents.year = today.getFullYear();
      dateComponents.month = today.getMonth() + 1;
      dateComponents.day = today.getDate();
    }
  }

  datePickerDialog.value = true;
};

// 確認日期選擇
const confirmDateSelection = () => {
  // 用選擇的年、月、日構建日期字串
  const year = dateComponents.year;
  const month = String(dateComponents.month).padStart(2, '0');
  const day = String(dateComponents.day).padStart(2, '0');

  // 更新 localFormData 中的日期
  localFormData.inspectionDate = `${year}-${month}-${day}`;

  // 關閉對話框
  datePickerDialog.value = false;

  // 更新父組件數據
  updateFormData();
};

// 更新父組件數據
const updateFormData = () => {
  emit('update:formData', {
    ...props.formData,
    ...localFormData,
    valid: true // Always true for seamless navigation
  });
};

// 初始化數據
onMounted(() => {
  console.log("Step 5 mounted, formData:", props.formData);

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

// 組件卸載時清理資源
onUnmounted(() => {
  cleanupPreviews();
});
</script>

<style scoped>
.step-content {
  padding: 0;
  background-color: transparent !important;
}

/* 卡片懸停效果 */
.v-card.pa-4 {
  transition: all 0.3s ease;
}

.v-card.pa-4:hover {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05) !important;
}

.text-red {
  color: red;
}

/* 表單輸入區塊樣式 */
:deep(.v-field__input) {
  padding: 8px 16px;
}

/* :deep(.v-field--variant-outlined .v-field__outline__start),
:deep(.v-field--variant-outlined .v-field__outline__end),
:deep(.v-field--variant-outlined .v-field__outline__notch) {
  border-color: rgba(62, 160, 163, 0.2);
}

:deep(.v-field--variant-outlined:hover .v-field__outline__start),
:deep(.v-field--variant-outlined:hover .v-field__outline__end),
:deep(.v-field--variant-outlined:hover .v-field__outline__notch) {
  border-color: rgba(62, 160, 163, 0.5);
} */

/* 唯讀輸入框樣式 */
:deep(.v-field--disabled .v-field__input) {
  color: rgba(0, 0, 0, 1) !important;
}
</style>
