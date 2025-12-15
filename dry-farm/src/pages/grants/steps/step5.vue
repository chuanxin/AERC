<template>
  <div
    ref="stepContent"
    class="step-content"
  >
    <v-card
      class="mt-4 pa-0"
      flat
    >
      <v-card-text class="pb-0 pt-0">
        <!-- 🆕 唯讀模式提示（硬鎖定） -->
        <v-alert
          v-if="props.readonly && grantsStore.currentGrant?.status !== 'rejected'"
          type="warning"
          variant="tonal"
          density="compact"
          class="mb-4"
          rounded="lg"
        >
          <div class="d-flex align-center">
            <span class="text-body-2">
              {{ grantsStore.currentGrant?.status === 'submitted'
                ? '已完成結案申報，此步驟已鎖定，無法編輯。'
                : '已完成申報並送審，此步驟已鎖定，無法編輯。' }}
            </span>
          </div>
        </v-alert>

        <!-- ⚠️ 軟鎖定警告 -->
        <v-alert
          v-if="props.softLocked && !props.readonly"
          color="warning"
          variant="tonal"
          density="compact"
          class="mb-4"
          rounded="lg"
        >
          <div class="d-flex align-center">
            <v-icon
              class="me-2"
              size="small"
            >mdi-alert</v-icon>
            <span class="text-body-2">
              已完成現場勘查，修改此步驟資料可能導致勘查結果無效，請謹慎編輯。
            </span>
          </div>
        </v-alert>

        <v-form
          ref="form"
          v-model="localValid"
          @submit.prevent
        >
          <!-- 勘查資訊區域 -->
          <v-card
            flat
            class="mb-4 pa-4"
            color="#e3f4f4"
            rounded="lg"
          >
            <v-card-title
              class="text-subtitle-1 font-weight-bold pa-0 pb-6"
              style="color: #2d8c8f"
            >
              <v-icon
                color="#3ea0a3"
                class="me-2 pb-1"
                size="small"
              >
                mdi-clipboard-check
              </v-icon>
              <span><span class="required-asterisk">*</span>勘查資訊</span>
            </v-card-title>

            <v-sheet
              class="mb-3 pa-3 rounded"
              color="white"
            >
              <v-row>
                <v-col
                  cols="12"
                  md="6"
                >
                  <v-text-field
                    v-model="localFormData.inspector"
                    variant="outlined"
                    density="comfortable"
                    color="#3ea0a3"
                    bg-color="white"
                    :rules="[v => !!v || '請填寫勘查人員']"
                    :readonly="props.readonly"
                  >
                    <template #label>
                      勘查人員
                    </template>
                  </v-text-field>
                </v-col>

                <v-col
                  cols="12"
                  md="6"
                >
                  <!-- 使用簡單的日期輸入 -->
                  <v-text-field
                    v-model="formattedInspectionDate"
                    prepend-icon="mdi-calendar"
                    variant="outlined"
                    density="comfortable"
                    color="#3ea0a3"
                    bg-color="white"
                    :rules="[v => !!v || '請選擇勘查日期']"
                    :readonly="props.readonly"
                    @click="!props.readonly && openDateDialog()"
                  >
                    <template #label>
                      勘查日期
                    </template>
                  </v-text-field>

                  <!-- 自定義日期選擇對話框 -->
                  <v-dialog
                    v-model="datePickerDialog"
                    width="600"
                  >
                    <v-card>
                      <v-card-title
                        class="text-h6 font-weight-bold"
                        style="color: #2d8c8f"
                      >
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
                            />
                          </v-col>
                          <v-col cols="4">
                            <v-select
                              v-model="dateComponents.month"
                              :items="monthOptions"
                              label="月"
                              variant="outlined"
                              density="comfortable"
                              color="#3ea0a3"
                            />
                          </v-col>
                          <v-col cols="4">
                            <v-select
                              v-model="dateComponents.day"
                              :items="dayOptions"
                              label="日"
                              variant="outlined"
                              density="comfortable"
                              color="#3ea0a3"
                            />
                          </v-col>
                        </v-row>
                      </v-card-text>
                      <v-card-actions>
                        <v-spacer />
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

              <v-row dense>
                <v-col cols="12">
                  <label class="d-flex align-center mb-2">
                    <v-icon
                      size="small"
                      class="me-2"
                    >
                      mdi-clipboard-check-outline
                    </v-icon>
                    <span class="text-body-2 font-weight-medium">勘查結果</span>
                  </label>
                  <v-radio-group
                    v-model="localFormData.inspectionResult"
                    inline
                    :rules="[v => !!v || '請選擇勘查結果']"
                    color="#3ea0a3"
                    class="mt-0"
                    hide-details="auto"
                    :readonly="props.readonly"
                  >
                    <v-radio
                      value="comply"
                      label="符合"
                    />
                    <v-radio
                      value="notComply"
                      label="不符合"
                    />
                    <!-- <v-radio
                      value="other"
                      label="其他"
                    /> -->
                  </v-radio-group>
                </v-col>
              </v-row>

              <v-row
                v-if="localFormData.inspectionResult === 'notComply'"
                dense
              >
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
                    :readonly="props.readonly"
                  />
                </v-col>
              </v-row>

              <v-row
                v-if="localFormData.inspectionResult === 'comply'"
                dense
              >
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
                    :readonly="props.readonly"
                  />
                </v-col>
              </v-row>
            </v-sheet>

            <!-- 照片上傳區域 -->
            <v-sheet
              class="pa-3 rounded"
              color="white"
            >
              <v-row>
                <v-col cols="12">
                  <label class="d-flex align-center">
                    <v-icon
                      size="small"
                      class="me-2"
                    >
                      mdi-camera-outline
                    </v-icon>
                    <span class="text-body-2 font-weight-medium">施工前照片</span><span class="ml-2 text-grey text-caption">(需要1-3張照片)</span>
                  </label>
                  <v-sheet
                    class="pa-3 rounded mb-4"
                    color="white"
                  >
                    <!-- 已上傳照片展示區域 -->
                    <div
                      v-if="localFormData.beforePhotoPreviews && localFormData.beforePhotoPreviews.length > 0"
                      class="mb-3"
                    >
                      <v-row>
                        <v-col
                          v-for="(preview, index) in localFormData.beforePhotoPreviews"
                          :key="`before-${index}`"
                          cols="6"
                          sm="4"
                          md="3"
                        >
                          <v-card
                            variant="outlined"
                            class="photo-card"
                          >
                            <div class="position-relative">
                              <v-img
                                :src="preview"
                                height="120"
                                cover
                                class="rounded-t"
                              />
                              <v-btn
                                icon
                                size="x-small"
                                color="error"
                                variant="elevated"
                                class="position-absolute"
                                style="top: 8px; right: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.3);"
                                :disabled="props.readonly"
                                @click="removeBeforePhoto(index)"
                              >
                                <v-icon size="small">
                                  mdi-close
                                </v-icon>
                              </v-btn>
                            </div>
                            <v-card-text class="pa-2 text-center">
                              <div class="text-caption text-grey-darken-1">
                                第 {{ index + 1 }} 張照片
                              </div>
                            </v-card-text>
                          </v-card>
                        </v-col>

                        <!-- 新增照片按鈕 (當未達到3張時顯示) -->
                        <v-col
                          v-if="localFormData.beforePhotoPreviews.length < 3"
                          cols="6"
                          sm="4"
                          md="3"
                        >
                          <v-card
                            variant="outlined"
                            class="photo-card add-photo-card"
                            :disabled="props.readonly"
                            @click="() => triggerFileInput()"
                          >
                            <div class="d-flex flex-column align-center justify-center h-100">
                              <v-icon
                                size="40"
                                color="grey-lighten-1"
                                class="mb-2"
                              >
                                mdi-plus-circle-outline
                              </v-icon>
                              <div class="text-caption text-grey text-center">
                                新增照片<br>
                                <span class="text-xs">({{ localFormData.beforePhotoPreviews.length }}/3)</span>
                              </div>
                            </div>
                          </v-card>
                        </v-col>
                      </v-row>
                    </div>

                    <!-- 初次上傳區域 (當沒有照片時顯示) -->
                    <div v-if="localFormData.beforePhotoPreviews.length === 0">
                      <v-card
                        variant="outlined"
                        class="upload-zone"
                        @click="() => !props.readonly && triggerFileInput()"
                      >
                        <v-card-text class="text-center pa-8">
                          <v-icon
                            size="48"
                            color="grey-lighten-1"
                            class="mb-3"
                          >
                            mdi-camera-plus-outline
                          </v-icon>
                          <div class="text-h6 text-grey-darken-1 mb-2">
                            上傳施工前照片
                          </div>
                          <div class="text-body-2 text-grey">
                            點擊選擇照片檔案<br>
                            <span class="text-caption">支援 JPG、PNG 格式，需要 1-3 張照片</span>
                          </div>
                        </v-card-text>
                      </v-card>
                    </div>

                    <!-- 隱藏的檔案輸入框 -->
                    <input
                      ref="fileInput"
                      type="file"
                      accept="image/*"
                      style="display: none"
                      @change="handleSinglePhotoUpload"
                    >

                    <!-- 上傳狀態提示 -->
                    <div
                      v-if="localFormData.beforePhotoPreviews.length > 0 && !props.readonly"
                      class="mt-2"
                    >
                      <v-chip
                        :color="getUploadStatusColor()"
                        variant="tonal"
                        size="small"
                      >
                        <v-icon
                          start
                          size="small"
                        >
                          {{ getUploadStatusIcon() }}
                        </v-icon>
                        {{ getUploadStatusText() }}
                      </v-chip>
                    </div>
                  </v-sheet>
                </v-col>

                <!-- <v-col
                  cols="12"
                  md="6"
                >
                  <label class="text-body-2 font-weight-medium mb-2 d-block">
                    竣工照片
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

                  <div
                    v-if="localFormData.afterPhotoPreview"
                    class="mt-2"
                  >
                    <v-img
                      :src="localFormData.afterPhotoPreview"
                      max-height="200"
                      contain
                      class="bg-grey-lighten-3 rounded"
                    />
                  </div>
                </v-col> -->
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
import { attachmentService } from '@/services/attachmentService';

// Props definition
// 🆕 新增 readonly 和 softLocked prop 支援
const props = defineProps({
  formData: {
    type: Object,
    required: true,
    default: () => ({})
  },
  currentStep: {
    type: Number,
    required: true
  },
  grantId: {
    type: Number,
    required: true
  },
  readonly: {
    type: Boolean,
    default: false
  },
  softLocked: {
    type: Boolean,
    default: false
  }
});

// Event emitters - using expected event names from edit.vue
const emit = defineEmits([
  'update:formData',
  'validated',
  'go-back',
  'case-archived',
  'navigation-state-changed',
  'button-config-changed'
]);

// Access grants store
const grantsStore = useGrantsStore();

// Form ref and validation state
const form = ref(null);
const localValid = ref(true);

// 上傳狀態管理
const uploading = ref(false);
const uploadProgress = ref<Record<string, number>>({});

// 已上傳照片介面
interface UploadedPhoto {
  id: number;
  original_filename: string;
  filesize: number;
  mime_type: string;
  category: string;
  uploaded_at: string;
  uploaded_by: string;
}

// 已上傳照片列表
const uploadedPhotos = ref<UploadedPhoto[]>([]);

// 新增：導航狀態管理
const navigationState = reactive({
  canNavigate: true,
  isEditing: true,
  reason: ''
});

// 新增：按鈕配置管理
const buttonConfig = computed(() => {
  if (localFormData.inspectionResult === 'notComply') {
    return {
      text: '不受理',
      color: 'warning',
      icon: 'mdi-archive-outline',
      action: 'archive',
      disabled: false
    };
  }

  // 預設正常流程
  return {
    text: '下一步',
    color: '#3ea0a3',
    icon: 'mdi-arrow-right',
    action: 'proceed',
    disabled: false
  };
});

// 本地表單數據
const localFormData = reactive({
  inspector: '',
  inspectionResult: '',
  reason: '',
  inspectionDate: '',
  remarks: '',
  beforeConstructionPhotos: [] as File[], // 改為陣列以支援多張照片
  afterConstructionPhoto: null as File | null,
  beforePhotoPreviews: [] as string[], // 改為陣列以支援多張照片預覽
  afterPhotoPreview: null as string | null,
  valid: true // Always true for seamless navigation
});

// 驗證規則
const reasonRules = computed(() => {
  if (localFormData.inspectionResult === 'notComply' || localFormData.inspectionResult === 'other') {
    return [(v: string | undefined | null) => !!v || '請填寫原因說明'];
  }
  return [];
});

// 新增：處理不受理案件歸檔
const handleArchiveCase = async () => {
  console.log('📦 [step3] Processing case archive - inspection not compliant');

  try {
    // 1. 驗證必填欄位
    if (!localFormData.inspector || !localFormData.inspectionDate || !localFormData.reason) {
      alert('請填寫完整的勘查資訊和不符合原因');
      return;
    }

    // 2. 更新案件狀態為 rejected（不受理）
    if (grantsStore.currentGrant?.case_number) {
      console.log('🔄 [step3] Updating grant status to rejected...')
      await grantsStore.updateGrantStatus(grantsStore.currentGrant.case_number, 'rejected')
      console.log('✅ [step3] Grant status updated to rejected')
    } else {
      console.error('❌ [step3] No case_number available, cannot update status')
      alert('找不到案件編號，無法更新狀態')
      return
    }

    // 3. 準備歸檔資料
    const archiveData = {
      ...localFormData,
      status: 'rejected',
      archived: true,
      archiveReason: localFormData.reason,
      archiveDate: new Date().toISOString(),
      finalStep: props.currentStep, // 標記最終停留在 UI step（當前為 3）
      valid: true
    };

    // 4. 發送歸檔事件給父組件（edit.vue 會處理鎖定和 disable 邏輯）
    emit('case-archived', {
      step: props.currentStep,
      data: archiveData,
      reason: localFormData.reason
    });

    // 5. 禁用進一步編輯
    navigationState.canNavigate = false;
    navigationState.isEditing = false;
    navigationState.reason = '案件已歸檔：勘查結果不符合';

    // 6. 發送導航狀態變更事件
    emit('navigation-state-changed', {
      step: props.currentStep,
      canNavigate: false,
      isEditing: false,
      reason: '案件已歸檔：勘查結果不符合'
    });

    console.log('✅ [step3] Case archived successfully');

  } catch (error) {
    console.error('❌ [step3] Failed to archive case:', error);
    alert('歸檔失敗，請稍後再試');
  }
};

// 新增：處理正常進入下一步
const handleProceedToNext = async () => {
  console.log('➡️ [step3] Proceeding to next step');

  // 驗證表單
  if (!validateForm()) {
    return;
  }

  // 🆕 更新案件狀態為已核准（完成現場勘查）
  if (grantsStore.currentGrant?.case_number) {
    try {
      console.log('🔄 [step3] Updating grant status to approved...')
      await grantsStore.updateGrantStatus(grantsStore.currentGrant.case_number, 'approved')
      console.log('✅ [step3] Grant status updated to approved')
    } catch (error) {
      console.error('❌ [step3] Failed to update status:', error)
      alert('更新案件狀態失敗，請稍後再試')
      return
    }
  } else {
    console.error('❌ [step3] No case_number available, cannot update status')
    alert('找不到案件編號，無法更新狀態')
    return
  }

  // 發送驗證成功事件
  emit('validated', {
    valid: true,
    step: props.currentStep + 1
  });
};

// 新增：表單驗證函數
const validateForm = () => {
  // 基本必填欄位檢查
  if (!localFormData.inspector) {
    alert('請填寫勘查人員');
    return false;
  }

  if (!localFormData.inspectionDate) {
    alert('請選擇勘查日期');
    return false;
  }

  if (!localFormData.inspectionResult) {
    alert('請選擇勘查結果');
    return false;
  }

  // 照片檢查
  if (localFormData.beforePhotoPreviews.length === 0) {
    alert('請至少上傳1張施工前照片');
    return false;
  }

  // 不符合時必須填寫原因
  if (localFormData.inspectionResult === 'notComply' && !localFormData.reason) {
    alert('請填寫不符合的原因說明');
    return false;
  }

  return true;
};

// 新增：處理按鈕動作請求（來自父組件）
const handleActionRequest = (action: string) => {
  console.log(`🎯 [step3] handleActionRequest called with action: ${action}`);

  if (action === 'archive') {
    handleArchiveCase();
  } else if (action === 'proceed') {
    handleProceedToNext();
  }
};

// 暴露方法給父組件調用
defineExpose({
  handleActionRequest,
  validateForm
});

const photoRules = [
  (v: File[] | null | undefined) => {
    if (!v || (Array.isArray(v) && v.length === 0)) {
      return '請至少上傳1張照片';
    }
    if (Array.isArray(v) && v.length > 3) {
      return '最多只能上傳3張照片';
    }
    return true;
  }
];

// 處理照片預覽
const handlePhotoChange = (type: 'before' | 'after') => {
  if (type === 'before') {
    const files = localFormData.beforeConstructionPhotos;

    // 清除之前的預覽
    localFormData.beforePhotoPreviews.forEach(preview => {
      if (preview && typeof preview === 'string' && preview.startsWith('blob:')) {
        URL.revokeObjectURL(preview);
      }
    });
    localFormData.beforePhotoPreviews = [];

    if (files && files.length > 0) {
      // 限制最多3張照片
      const limitedFiles = files.slice(0, 3);
      localFormData.beforeConstructionPhotos = limitedFiles;

      // 為每張照片創建預覽
      limitedFiles.forEach(file => {
        if (file instanceof File) {
          const preview = URL.createObjectURL(file);
          localFormData.beforePhotoPreviews.push(preview);
        }
      });
    }
  } else {
    const file = localFormData.afterConstructionPhoto;

    if (file) {
      // Only create object URLs for actual File objects
      if (file instanceof File) {
        // 清除之前的預覽
        if (localFormData.afterPhotoPreview && localFormData.afterPhotoPreview.startsWith('blob:')) {
          URL.revokeObjectURL(localFormData.afterPhotoPreview);
        }
        localFormData.afterPhotoPreview = URL.createObjectURL(file);
      }
    }
  }

  updateFormData();
};

// 移除單張施工前照片
const removeBeforePhoto = async (index: number) => {
  try {
    // 如果是已上傳的照片，從後端刪除
    if (uploadedPhotos.value[index]) {
      const photoToDelete = uploadedPhotos.value[index];
      console.log(`[step3] 刪除照片 ID: ${photoToDelete.id}`);

      await attachmentService.delete(photoToDelete.id);
      console.log(`[step3] 成功刪除照片 ID: ${photoToDelete.id}`);
    }

    // 清除預覽
    if (localFormData.beforePhotoPreviews[index] &&
        typeof localFormData.beforePhotoPreviews[index] === 'string' &&
        localFormData.beforePhotoPreviews[index].startsWith('blob:')) {
      URL.revokeObjectURL(localFormData.beforePhotoPreviews[index]);
    }

    // 重新載入照片列表
    await loadPhotos();

    updateFormData();
  } catch (error) {
    console.error('[step3] 刪除照片失敗:', error);
    alert('刪除照片失敗，請稍後再試');
  }
};

// 檔案輸入框引用
const fileInput = ref<HTMLInputElement | null>(null);

// 觸發檔案選擇
const triggerFileInput = () => {
  if (localFormData.beforePhotoPreviews.length < 3) {
    fileInput.value?.click();
  }
};

// 載入已上傳的照片
const loadPhotos = async () => {
  if (!props.grantId || props.grantId === 0) {
    console.warn('[step3] loadPhotos: grantId 無效，跳過載入', props.grantId);
    return;
  }

  try {
    const stepNumber = 5;
    console.log(`[step3] 開始載入照片 - grantId: ${props.grantId}, step: ${stepNumber}`);

    const response = await attachmentService.list(props.grantId, stepNumber, 'inspection_before');
    console.log(`[step3] API 回應:`, response);

    uploadedPhotos.value = response.attachments || [];

    // 清除本地預覽並使用 API 照片
    cleanupPreviews();
    localFormData.beforePhotoPreviews = [];
    localFormData.beforeConstructionPhotos = [];

    // 為每張已上傳的照片創建預覽 URL
    for (const photo of uploadedPhotos.value) {
      try {
        const blob = await attachmentService.download(photo.id);
        const previewUrl = URL.createObjectURL(blob);
        localFormData.beforePhotoPreviews.push(previewUrl);
      } catch (error) {
        console.error(`[step3] 載入照片預覽失敗 (ID: ${photo.id}):`, error);
      }
    }

    console.log(`[step3] 成功載入 ${uploadedPhotos.value.length} 張照片`);
  } catch (error: any) {
    console.error('[step3] 載入照片列表失敗:', {
      error,
      message: error?.message,
      response: error?.response?.data,
      status: error?.response?.status,
      grantId: props.grantId
    });
    uploadedPhotos.value = [];
  }
};

// 處理單張照片上傳
const handleSinglePhotoUpload = async (event: Event) => {
  const target = event.target as HTMLInputElement;
  const file = target.files?.[0];

  if (file && localFormData.beforePhotoPreviews.length < 3) {
    // 檢查檔案類型
    if (!file.type.startsWith('image/')) {
      alert('請選擇圖片檔案');
      return;
    }

    // 檢查檔案大小 (限制為 5MB)
    if (file.size > 5 * 1024 * 1024) {
      alert('檔案大小不能超過 5MB');
      return;
    }

    // 開始上傳
    uploading.value = true;
    const stepNumber = 5;
    const progressKey = file.name;

    try {
      uploadProgress.value[progressKey] = 0;

      console.log(`[step3] 上傳照片: ${file.name} 到類別 inspection_before`);

      // 上傳到後端
      const response = await attachmentService.upload(
        props.grantId,
        stepNumber,
        file,
        'inspection_before',
        undefined,
        (progress) => {
          uploadProgress.value[progressKey] = progress;
        }
      );

      console.log('[step3] 照片上傳成功:', response);

      // 重新載入照片列表
      await loadPhotos();

      delete uploadProgress.value[progressKey];
    } catch (error) {
      console.error(`[step3] 上傳照片 ${file.name} 失敗:`, error);
      alert('照片上傳失敗，請稍後再試');
      delete uploadProgress.value[progressKey];
    } finally {
      uploading.value = false;
      // 清空 input value 以允許重複選擇同一檔案
      target.value = '';
    }

    updateFormData();
  }
};

// 取得上傳狀態顏色
const getUploadStatusColor = () => {
  const count = localFormData.beforePhotoPreviews.length;
  if (count >= 1 && count <= 3) return 'success';
  return 'warning';
};

// 取得上傳狀態圖示
const getUploadStatusIcon = () => {
  const count = localFormData.beforePhotoPreviews.length;
  if (count >= 1 && count <= 3) return 'mdi-check-circle';
  return 'mdi-alert-circle';
};

// 取得上傳狀態文字
const getUploadStatusText = () => {
  const count = localFormData.beforePhotoPreviews.length;
  if (count === 1) return '已上傳 1 張照片，可繼續添加';
  if (count === 2) return '已上傳 2 張照片，可再添加 1 張';
  if (count === 3) return '已上傳 3 張照片（已達上限）';
  return '請上傳照片';
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
  // 排除應從 API 載入的欄位（這些欄位不應傳回父組件）
  const { beforePhotoPreviews, beforeConstructionPhotos, afterPhotoPreview, afterConstructionPhoto, ...dataToEmit } = localFormData;

  emit('update:formData', {
    ...props.formData,
    ...dataToEmit,
    valid: true // Always true for seamless navigation
  });
};

// 初始化數據
onMounted(async () => {
  console.log("Step 5 mounted, formData:", props.formData);

  // 從父組件接收數據（排除應從 API 載入的欄位）
  if (props.formData) {
    // 設置基本屬性，使用類型安全的方式
    const formDataKeys = Object.keys(localFormData) as Array<keyof typeof localFormData>;
    formDataKeys.forEach(key => {
      // 排除應從 API 載入的欄位
      if (key === 'beforePhotoPreviews' ||
          key === 'beforeConstructionPhotos' ||
          key === 'afterPhotoPreview' ||
          key === 'afterConstructionPhoto') {
        return;
      }

      if (props.formData[key] !== undefined) {
        (localFormData as any)[key] = props.formData[key];
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

  // 載入已上傳的照片
  if (props.grantId && props.grantId > 0) {
    await loadPhotos();
  }

  // Initial update to parent
  updateFormData();

  // 初始發送按鈕配置
  nextTick(() => {
    emit('button-config-changed', buttonConfig.value);
  });
});

// 監聽父組件數據變化
watch(() => props.formData, (newVal) => {
  if (newVal) {
    const formDataKeys = Object.keys(localFormData) as Array<keyof typeof localFormData>;
    formDataKeys.forEach(key => {
      // 排除應從 API 載入的欄位
      if (key === 'beforePhotoPreviews' ||
          key === 'beforeConstructionPhotos' ||
          key === 'afterPhotoPreview' ||
          key === 'afterConstructionPhoto') {
        return;
      }

      if (newVal[key] !== undefined &&
          JSON.stringify(newVal[key]) !== JSON.stringify((localFormData as any)[key])) {
        (localFormData as any)[key] = newVal[key];
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

// 新增：監聽勘查結果變化，動態調整導航狀態和按鈕配置
watch(() => localFormData.inspectionResult, (newValue, oldValue) => {
  console.log(`🔄 [step3] Inspection result changed: ${oldValue} → ${newValue}`);

  if (newValue === 'notComply') {
    // 不符合時，仍允許編輯以填寫原因，但改變按鈕行為
    navigationState.canNavigate = true;
    navigationState.isEditing = true;
    navigationState.reason = '需要填寫不符合原因';
  } else if (newValue === 'comply') {
    // 符合時，恢復正常導航
    navigationState.canNavigate = true;
    navigationState.isEditing = true;
    navigationState.reason = '';
  }

  // 發送按鈕配置變更事件給父組件
  emit('button-config-changed', buttonConfig.value);

  // 發送導航狀態變更事件
  emit('navigation-state-changed', {
    step: props.currentStep,
    canNavigate: navigationState.canNavigate,
    isEditing: navigationState.isEditing,
    reason: navigationState.reason
  });
});

// 清理預覽資源的函數
const cleanupPreviews = () => {
  // 清理施工前照片預覽
  localFormData.beforePhotoPreviews.forEach(preview => {
    if (preview && typeof preview === 'string' && preview.startsWith('blob:')) {
      URL.revokeObjectURL(preview);
    }
  });

  // 清理竣工照片預覽
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

/* 必填欄位紅色星號樣式 */
.required-asterisk {
  color: #ff0000 !important;
  font-weight: bold;
  margin-left: 2px;
}

/* 照片卡片樣式 */
.photo-card {
  transition: all 0.2s ease;
  cursor: default;
  height: 180px;
}

.add-photo-card {
  cursor: pointer;
  border: 2px dashed #ccc !important;
  background-color: #fafafa;
}

.add-photo-card:hover {
  border-color: #3ea0a3 !important;
  background-color: #f0f8f8;
}

.upload-zone {
  cursor: pointer;
  transition: all 0.2s ease;
  border: 2px dashed #ccc !important;
  background-color: #fafafa;
}

.upload-zone:hover {
  border-color: #3ea0a3 !important;
  background-color: #f0f8f8;
}
</style>
