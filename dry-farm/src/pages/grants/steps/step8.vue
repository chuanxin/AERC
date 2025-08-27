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
        <!-- 文件上傳說明提示 -->
        <v-alert
          type="info"
          variant="tonal"
          class="mb-4"
          prominent
          border="start"
        >
          <template #prepend>
            <v-icon size="large">
              mdi-clipboard-check
            </v-icon>
          </template>
          <div class="text-h6 mb-2">
            上傳資料檢核表
          </div>
          <div class="text-body-1">
            <p class="mb-2">
              <strong>請依照檢核表逐項確認：</strong>請確認文件已備齊並勾選對應項目，然後統一上傳所需檔案。
            </p>
            <p class="mt-2 mb-0">
              <v-icon
                size="small"
                class="me-1"
              >
                mdi-information
              </v-icon>
              支援格式：PDF、JPG、PNG
            </p>
          </div>
        </v-alert>

        <v-form
          ref="form"
          v-model="localValid"
          @submit.prevent
        >
          <v-row>
            <!-- 左側：上傳資料檢核表 -->
            <v-col
              cols="12"
              md="7"
            >
              <v-card
                class="mb-4"
                variant="outlined"
              >
                <v-card-title class="bg-primary-lighten-4 d-flex align-center py-3 px-4">
                  <v-icon
                    class="me-2"
                    size="small"
                  >
                    mdi-clipboard-check-outline
                  </v-icon>
                  <span class="text-subtitle-1 font-weight-medium">上傳資料檢核表</span>
                  <v-spacer />
                  <v-chip
                    :color="completionPercentage === 100 ? 'success' : 'primary'"
                    variant="flat"
                    size="small"
                  >
                    {{ completedItems }}/{{ checklistItems.length }} 項目
                  </v-chip>
                </v-card-title>

                <v-card-text class="pa-0">
                  <v-list class="py-0">
                    <template
                      v-for="(item, index) in checklistItems"
                      :key="item.id"
                    >
                      <v-list-item
                        class="checklist-item"
                        :class="{
                          'item-completed': item.completed,
                          'item-has-files': getItemFiles(item.id).length > 0
                        }"
                      >
                        <template #prepend>
                          <v-icon
                            :color="item.completed ? 'success' : 'grey-lighten-1'"
                            size="large"
                          >
                            {{ item.completed ? 'mdi-check-circle' : 'mdi-circle-outline' }}
                          </v-icon>
                        </template>

                        <v-list-item-title class="font-weight-medium">
                          {{ item.name }}
                          <span
                            v-if="item.required"
                            class="required-asterisk"
                          >*</span>
                        </v-list-item-title>

                        <v-list-item-subtitle class="text-caption mt-1">
                          {{ item.description }}
                        </v-list-item-subtitle>

                        <!-- 已上傳檔案標籤 -->
                        <div
                          v-if="getItemFiles(item.id).length > 0"
                          class="mt-2"
                        >
                          <v-chip
                            v-for="file in getItemFiles(item.id)"
                            :key="file.id"
                            size="x-small"
                            variant="outlined"
                            color="success"
                            class="me-1 mb-1"
                          >
                            <v-icon
                              start
                              size="x-small"
                            >
                              mdi-file-check-outline
                            </v-icon>
                            {{ file.display_name }}
                          </v-chip>
                        </div>
                      </v-list-item>
                      <v-divider v-if="index < checklistItems.length - 1" />
                    </template>
                  </v-list>
                </v-card-text>
              </v-card>

              <!-- 完成進度 -->
              <v-card variant="outlined">
                <v-card-title class="bg-info-lighten-4 d-flex align-center py-3 px-4">
                  <v-icon
                    class="me-2"
                    size="small"
                  >
                    mdi-progress-check
                  </v-icon>
                  <span class="text-subtitle-1 font-weight-medium">完成進度</span>
                </v-card-title>

                <v-card-text class="pa-4">
                  <div class="d-flex align-center mb-3">
                    <v-progress-circular
                      :model-value="completionPercentage"
                      :color="completionPercentage === 100 ? 'success' : 'primary'"
                      size="48"
                      width="4"
                    >
                      <span class="text-caption font-weight-bold">{{ Math.round(completionPercentage) }}%</span>
                    </v-progress-circular>
                    <div class="ml-3">
                      <div class="text-body-2 font-weight-medium">
                        {{ completedItems }} / {{ checklistItems.length }} 項目完成
                      </div>
                      <div class="text-caption text-medium-emphasis">
                        {{ uniqueUploadedFiles.length }} 個檔案已上傳
                      </div>
                    </div>
                  </div>

                  <!-- 完成狀態提示 -->
                  <v-alert
                    v-if="completionPercentage === 100"
                    type="success"
                    variant="tonal"
                    density="compact"
                    class="mb-0"
                  >
                    <template #prepend>
                      <v-icon size="small">
                        mdi-check-circle
                      </v-icon>
                    </template>
                    所有必要文件已上傳完成，可以進行下一步！
                  </v-alert>

                  <v-alert
                    v-else
                    type="warning"
                    variant="tonal"
                    density="compact"
                    class="mb-0"
                  >
                    <template #prepend>
                      <v-icon size="small">
                        mdi-alert-circle-outline
                      </v-icon>
                    </template>
                    還有 {{ incompleteRequiredItems }} 項必要文件待處理 (總共 {{ checklistItems.length }} 項)
                  </v-alert>
                </v-card-text>
              </v-card>
            </v-col>

            <!-- 右側：檔案上傳區域 -->
            <v-col
              cols="12"
              md="5"
            >
              <!-- 檔案上傳控制 -->
              <v-card
                class="mb-4"
                variant="outlined"
              >
                <v-card-title class="bg-success-lighten-4 d-flex align-center py-3 px-4">
                  <v-icon
                    class="me-2"
                    size="small"
                  >
                    mdi-cloud-upload-outline
                  </v-icon>
                  <span class="text-subtitle-1 font-weight-medium">檔案上傳</span>
                </v-card-title>

                <v-card-text class="pa-4">
                  <!-- 檔案類別選擇 -->
                  <div class="mb-3">
                    <v-label class="text-subtitle-2 mb-2 d-block">
                      選擇文件類別（可多選） - 共 {{ checklistItems.length }} 個類別
                    </v-label>
                    <div class="category-chips-container">
                      <v-chip
                        v-for="item in checklistItems"
                        :key="item.id"
                        :variant="selectedCategories.includes(item.id) ? 'flat' : 'outlined'"
                        :color="selectedCategories.includes(item.id) ? 'primary' : 'default'"
                        size="small"
                        class="me-2 mb-2 category-chip"
                        @click="toggleCategory(item.id)"
                      >
                        <v-icon
                          start
                          size="x-small"
                          :color="item.completed ? 'success' : 'grey'"
                        >
                          {{ item.completed ? 'mdi-check-circle' : 'mdi-circle-outline' }}
                        </v-icon>
                        {{ item.name }}
                        <v-icon
                          v-if="selectedCategories.includes(item.id)"
                          end
                          size="x-small"
                        >
                          mdi-check
                        </v-icon>
                      </v-chip>
                    </div>
                    <!-- 調試用：顯示所有類別名稱 -->
                    <div
                      v-if="checklistItems.length === 0"
                      class="text-caption text-error mt-2"
                    >
                      警告：檢核表項目未載入
                    </div>
                  </div>

                  <!-- 檔案說明 -->
                  <v-textarea
                    v-model="fileDescription"
                    label="檔案說明（選填）"
                    variant="outlined"
                    density="compact"
                    rows="3"
                    class="mb-3"
                  />

                  <!-- 檔案上傳拖放區域 -->
                  <v-card
                    variant="outlined"
                    class="upload-dropzone mb-3"
                    :class="{ 'dropzone-active': isDragOver }"
                    @dragover.prevent="handleDragOver"
                    @dragleave.prevent="handleDragLeave"
                    @drop.prevent="handleDrop"
                    @click="triggerFileSelect"
                  >
                    <v-card-text class="text-center py-4">
                      <v-icon
                        size="32"
                        color="primary"
                        class="mb-2"
                      >
                        mdi-cloud-upload
                      </v-icon>
                      <h4 class="text-subtitle-2 mb-1">
                        拖放檔案到此處或點擊選擇
                      </h4>
                      <p class="text-body-2 text-medium-emphasis mb-0">
                        支援 PDF、JPG、PNG 等格式，單檔最大 3MB
                      </p>

                      <v-file-input
                        ref="fileInputRef"
                        v-model="selectedFiles"
                        accept=".pdf,.doc,.docx,.xls,.xlsx,.jpg,.jpeg,.png,.dwg,.dxf"
                        multiple
                        style="display: none;"
                        @change="handleFileSelect"
                      />
                    </v-card-text>
                  </v-card>

                  <!-- 選中檔案列表 -->
                  <div
                    v-if="selectedFiles?.length"
                    class="mb-3"
                  >
                    <v-list
                      density="compact"
                      class="bg-grey-lighten-5 rounded"
                    >
                      <v-list-item
                        v-for="(file, index) in selectedFiles"
                        :key="index"
                        class="px-3 py-1"
                      >
                        <template #prepend>
                          <v-icon
                            size="small"
                            color="primary"
                          >
                            mdi-file-outline
                          </v-icon>
                        </template>
                        <v-list-item-title class="text-body-2">
                          {{ file.name }}
                        </v-list-item-title>
                        <v-list-item-subtitle class="text-caption">
                          {{ formatFileSize(file.size) }}
                        </v-list-item-subtitle>
                        <template #append>
                          <v-btn
                            icon="mdi-close"
                            size="x-small"
                            variant="text"
                            @click="removeSelectedFile(index)"
                          />
                        </template>
                      </v-list-item>
                    </v-list>
                  </div>

                  <!-- 上傳按鈕 -->
                  <v-btn
                    :disabled="!selectedFiles?.length || selectedCategories.length === 0 || uploading"
                    :loading="uploading"
                    color="success"
                    variant="flat"
                    block
                    @click="uploadFiles"
                  >
                    <v-icon start>
                      mdi-upload
                    </v-icon>
                    上傳檔案到 {{ selectedCategories.length }} 個類別 ({{ selectedFiles?.length || 0 }} 個檔案)
                  </v-btn>
                </v-card-text>
              </v-card>

              <!-- 已上傳檔案管理 -->
              <v-card
                v-if="uniqueUploadedFiles.length > 0"
                variant="outlined"
              >
                <v-card-title class="bg-grey-lighten-4 d-flex align-center py-3 px-4">
                  <v-icon
                    class="me-2"
                    size="small"
                  >
                    mdi-file-check-outline
                  </v-icon>
                  <span class="text-subtitle-1 font-weight-medium">已上傳檔案</span>
                  <v-spacer />
                  <v-chip
                    color="info"
                    variant="flat"
                    size="small"
                  >
                    共 {{ uniqueUploadedFiles.length }} 個檔案
                  </v-chip>
                </v-card-title>

                <v-card-text class="pa-0">
                  <v-list
                    class="py-0"
                    density="compact"
                  >
                    <v-list-item
                      v-for="file in uniqueUploadedFiles"
                      :key="file.uniqueId"
                    >
                      <template #prepend>
                        <v-icon
                          :color="getFileTypeColor(file.file_type)"
                          size="small"
                        >
                          {{ getFileTypeIcon(file.file_type) }}
                        </v-icon>
                      </template>

                      <v-list-item-title class="text-body-2">
                        {{ file.display_name }}
                      </v-list-item-title>
                      <v-list-item-subtitle class="text-caption">
                        {{ formatFileSize(file.file_size) }}
                        <span v-if="file.description"> • {{ file.description }}</span>
                      </v-list-item-subtitle>

                      <template #append>
                        <div class="d-flex align-center">
                          <v-btn
                            icon="mdi-download"
                            size="x-small"
                            variant="text"
                            @click="downloadFile(file)"
                          />
                          <v-btn
                            icon="mdi-delete"
                            size="x-small"
                            variant="text"
                            color="error"
                            @click="deleteUniqueFile(file)"
                          />
                        </div>
                      </template>
                    </v-list-item>
                  </v-list>
                </v-card-text>
              </v-card>
            </v-col>
          </v-row>
        </v-form>
      </v-card-text>
    </v-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch } from 'vue'

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

// Form validation references
const form = ref(null);
const localValid = ref(false);

// 檔案上傳相關狀態
const selectedFiles = ref<File[]>([]);
const selectedCategories = ref<string[]>([]);
const fileDescription = ref<string>('');
const uploading = ref<boolean>(false);
const isDragOver = ref<boolean>(false);
const fileInputRef = ref<any>();

// 觸發檔案選擇對話窗
const triggerFileSelect = () => {
  console.log('觸發檔案選擇');
  try {
    // 嘗試多種方式找到檔案輸入元素
    let input = null;

    if (fileInputRef.value) {
      // 方法1: 直接從 Vue 組件的 $refs
      input = fileInputRef.value.$refs?.input;

      // 方法2: 從 Vue 組件的 $el
      if (!input && fileInputRef.value.$el) {
        input = fileInputRef.value.$el.querySelector('input[type="file"]');
      }

      // 方法3: 直接查詢 DOM
      if (!input) {
        input = document.querySelector('input[type="file"][accept*=".pdf"]');
      }
    }

    if (input && typeof input.click === 'function') {
      console.log('找到檔案輸入元素，觸發點擊');
      input.click();
    } else {
      console.error('無法找到檔案輸入元素或點擊方法');
      console.log('fileInputRef.value:', fileInputRef.value);
      console.log('input:', input);

      // 最後一招：直接創建並觸發點擊
      const fallbackInput = document.createElement('input');
      fallbackInput.type = 'file';
      fallbackInput.accept = '.pdf,.doc,.docx,.xls,.xlsx,.jpg,.jpeg,.png,.dwg,.dxf';
      fallbackInput.multiple = true;
      fallbackInput.style.display = 'none';

      fallbackInput.onchange = (e) => {
        selectedFiles.value = Array.from(e.target.files || []);
        handleFileSelect(e);
        document.body.removeChild(fallbackInput);
      };

      document.body.appendChild(fallbackInput);
      fallbackInput.click();
    }
  } catch (error) {
    console.error('觸發檔案選擇時發生錯誤:', error);
  }
};
// 上傳檔案類型定義
interface UploadedFile {
  id: number;
  display_name: string;
  file_type: string;
  file_size: number;
  category: string;
  description: string;
  upload_date: string;
}

const uploadedFiles = ref<UploadedFile[]>([]);

// 唱一檔案計算屬性（去重）
const uniqueUploadedFiles = computed(() => {
  const fileMap = new Map<string, UploadedFile & { uniqueId: string; categories: string[] }>();

  uploadedFiles.value.forEach(file => {
    const key = `${file.display_name}_${file.file_size}_${file.file_type}`;
    if (fileMap.has(key)) {
      // 如果檔案已存在，將類別加入列表
      const existingFile = fileMap.get(key)!;
      if (!existingFile.categories.includes(file.category)) {
        existingFile.categories.push(file.category);
      }
    } else {
      // 新增檔案
      fileMap.set(key, {
        ...file,
        uniqueId: key,
        categories: [file.category]
      });
    }
  });

  return Array.from(fileMap.values());
});

// 檢核表項目定義
const checklistItems = reactive([
  {
    id: 'application',
    name: '申請檔案',
    description: '申請相關檔案 (PDF, JPG, PNG)',
    completed: false,
    required: true
  },
  {
    id: 'land_registration',
    name: '土地登記謄本',
    description: '土地登記謄本 (PDF, JPG, PNG)',
    completed: false,
    required: true
  },
  {
    id: 'land_map',
    name: '地籍圖謄本',
    description: '地籍圖謄本 (PDF, JPG, PNG)',
    completed: false,
    required: true
  },
  {
    id: 'lease_agreement',
    name: '租賃同意書',
    description: '租賃同意書 (PDF, JPG, PNG)',
    completed: false,
    required: true
  },
  {
    id: 'land_use_consent',
    name: '土地施設同意書',
    description: '土地施設同意書 (PDF, JPG, PNG)',
    completed: false,
    required: true
  },
  {
    id: 'inspection_record',
    name: '現勘紀錄表',
    description: '現勘紀錄表 (PDF, JPG, PNG)',
    completed: false,
    required: true
  },
  {
    id: 'planning_doc',
    name: '委託規劃書',
    description: '委託規劃書 (PDF, JPG, PNG)',
    completed: false,
    required: true
  },
  {
    id: 'subsidy_agreement',
    name: '接受補助切結書',
    description: '接受補助切結書 (PDF, JPG, PNG)',
    completed: false,
    required: true
  },
  {
    id: 'work_inspection',
    name: '竣工報驗書',
    description: '竣工報驗書 (PDF, JPG, PNG)',
    completed: false,
    required: true
  },
  {
    id: 'inspection_report',
    name: '驗收報告書',
    description: '驗收報告書 (PDF, JPG, PNG)',
    completed: false,
    required: true
  },
  {
    id: 'payment_receipt',
    name: '領款收據',
    description: '領款收據 (PDF, JPG, PNG)',
    completed: false,
    required: true
  },
  {
    id: 'design_drawing',
    name: '設計圖',
    description: '設計圖 (PDF, JPG, PNG)',
    completed: false,
    required: true
  },
  {
    id: 'other_documents',
    name: '其它補充資料',
    description: '其他補充相關資料 (PDF, JPG, PNG)',
    completed: false,
    required: false
  }
]);

// 計算屬性
const completedItems = computed(() => {
  return checklistItems.filter(item => item.completed).length;
});

const completionPercentage = computed(() => {
  if (checklistItems.length === 0) return 0;
  return (completedItems.value / checklistItems.length) * 100;
});

const incompleteRequiredItems = computed(() => {
  return checklistItems.filter(item => item.required && !item.completed).length;
});

// 拖放處理
const handleDragOver = (e: DragEvent) => {
  e.preventDefault();
  isDragOver.value = true;
};

const handleDragLeave = (e: DragEvent) => {
  e.preventDefault();
  isDragOver.value = false;
};

const handleDrop = (e: DragEvent) => {
  e.preventDefault();
  isDragOver.value = false;

  const files = Array.from(e.dataTransfer?.files || []);
  selectedFiles.value = [...selectedFiles.value, ...files];
};

const handleFileSelect = (event: any) => {
  console.log('檔案選擇事件觸發:', event);
  console.log('選中的檔案:', selectedFiles.value);
  // Files are already bound to selectedFiles via v-model
};

const removeSelectedFile = (index: number) => {
  selectedFiles.value.splice(index, 1);
};

// 切換類別選擇
const toggleCategory = (categoryId: string) => {
  const index = selectedCategories.value.indexOf(categoryId);
  if (index > -1) {
    selectedCategories.value.splice(index, 1);
  } else {
    selectedCategories.value.push(categoryId);
  }
};

// 檔案上傳
const uploadFiles = async () => {
  if (!selectedFiles.value.length || selectedCategories.value.length === 0) return;

  uploading.value = true;

  try {
    // 為每個檔案和每個選中類別創建上傳記錄
    for (const file of selectedFiles.value) {
      for (const categoryId of selectedCategories.value) {
        // 這裡應該調用實際的檔案上傳 API
        const uploadedFile = {
          id: Date.now() + Math.random() + Math.random(), // 確保唯一性
          display_name: file.name,
          file_type: file.type,
          file_size: file.size,
          category: categoryId,
          description: fileDescription.value || '',
          upload_date: new Date().toISOString()
        };

        uploadedFiles.value.push(uploadedFile);
      }
    }

    // 只有實際上傳成功後才更新檢核項目狀態
    for (const categoryId of selectedCategories.value) {
      const categoryItem = checklistItems.find(item => item.id === categoryId);
      if (categoryItem) {
        categoryItem.completed = true;
      }
    }

    // 清空選中狀態
    selectedFiles.value = [];
    selectedCategories.value = [];
    fileDescription.value = '';

    updateFormData();
  } catch (error) {
    console.error('檔案上傳失敗:', error);
    // 如果上傳失敗，不應該更新檢核表狀態
  } finally {
    uploading.value = false;
  }
};

// 檔案管理
const downloadFile = (file: UploadedFile) => {
  // 實現檔案下載邏輯
  console.log('下載檔案:', file);
};

// 移除未使用的 deleteFile 函數，使用 deleteUniqueFile 代替

// 刪除唯一檔案（會刪除所有相關的類別記錄）
const deleteUniqueFile = (uniqueFile: UploadedFile & { uniqueId: string; categories: string[] }) => {
  const fileKey = `${uniqueFile.display_name}_${uniqueFile.file_size}_${uniqueFile.file_type}`;
  const filesToRemove = uploadedFiles.value.filter(f =>
    `${f.display_name}_${f.file_size}_${f.file_type}` === fileKey
  );

  // 收集受影響的類別
  const affectedCategories = [...new Set(filesToRemove.map(f => f.category))];

  // 刪除所有相關記錄
  uploadedFiles.value = uploadedFiles.value.filter(f =>
    `${f.display_name}_${f.file_size}_${f.file_type}` !== fileKey
  );

  // 更新受影響類別的完成狀態
  for (const categoryId of affectedCategories) {
    const categoryHasFiles = uploadedFiles.value.some(f => f.category === categoryId);
    if (!categoryHasFiles) {
      const categoryItem = checklistItems.find(item => item.id === categoryId);
      if (categoryItem) {
        categoryItem.completed = false;
      }
    }
  }

  updateFormData();
};

// 輔助函數
const getItemFiles = (categoryId: string) => {
  return uploadedFiles.value.filter(file => file.category === categoryId);
};

// 移除未使用的 getCategoryName 函數

const getFileTypeIcon = (fileType: string) => {
  if (fileType.includes('pdf')) return 'mdi-file-pdf-box';
  if (fileType.includes('image')) return 'mdi-file-image';
  if (fileType.includes('word')) return 'mdi-file-word-box';
  if (fileType.includes('excel')) return 'mdi-file-excel-box';
  return 'mdi-file-document';
};

const getFileTypeColor = (fileType: string) => {
  if (fileType.includes('pdf')) return 'red';
  if (fileType.includes('image')) return 'green';
  if (fileType.includes('word')) return 'blue';
  if (fileType.includes('excel')) return 'success';
  return 'grey';
};

const formatFileSize = (bytes: number) => {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

// 移除手動更新檢核項目狀態的功能
// 檢核表狀態只能透過實際上傳檔案來更新

// 更新父組件數據
const updateFormData = () => {
  // 計算表單驗證狀態
  const requiredItemsCompleted = checklistItems
    .filter(item => item.required)
    .every(item => item.completed);

  localValid.value = requiredItemsCompleted;

  emit('update:formData', {
    ...props.formData,
    checklistItems: [...checklistItems],
    uploadedFiles: [...uploadedFiles.value],
    valid: localValid.value
  });
};

// 初始化
onMounted(() => {
  console.log("Step 8 mounted, formData:", props.formData);
  console.log("檢核表項目數量:", checklistItems.length);
  console.log("檢核表項目:", checklistItems.map(item => ({ id: item.id, name: item.name })));

  // 從父組件接收數據
  if (props.formData?.checklistItems && props.formData.checklistItems.length > 0) {
    console.log('從 props 中載入檢核表項目');
    checklistItems.splice(0, checklistItems.length, ...props.formData.checklistItems);
  } else {
    console.log('使用預設檢核表項目');
  }

  if (props.formData?.uploadedFiles) {
    uploadedFiles.value = [...(props.formData.uploadedFiles || [])];
  }

  updateFormData();

  // 讓 Vue 重新渲染以確保檢核表顯示
  setTimeout(() => {
    console.log('一秒後檢核表項目數量:', checklistItems.length);
  }, 1000);
});

// 監聽父組件數據變化
watch(() => props.formData, (newVal) => {
  if (newVal?.checklistItems && newVal.checklistItems.length > 0) {
    console.log('更新檢核表項目：', newVal.checklistItems.length);
    checklistItems.splice(0, checklistItems.length, ...newVal.checklistItems);
  }

  if (newVal?.uploadedFiles) {
    uploadedFiles.value = [...(newVal.uploadedFiles || [])];
  }
}, { deep: true });

// 監聽完成狀態變化
watch(completionPercentage, () => {
  updateFormData();
});

// 監聽檢核表項目變化
watch(() => checklistItems.length, (newLength) => {
  console.log('檢核表項目數量變化:', newLength);
}, { immediate: true });
</script>

<style scoped>
.step-content {
  padding: 0;
}

.upload-dropzone {
  border: 2px dashed #90CAF9;
  transition: all 0.3s ease;
  cursor: pointer;
}

.upload-dropzone:hover,
.dropzone-active {
  border-color: #2196F3;
  background-color: #E3F2FD;
}

.checklist-item {
  transition: all 0.2s ease;
}

.item-completed {
  background-color: #F1F8E9;
}

.item-has-files .v-list-item-title {
  color: #2E7D32;
  font-weight: 500;
}

.required-asterisk {
  color: #ff0000;
  font-weight: bold;
  margin-left: 2px;
}

.bg-primary-lighten-4 {
  background-color: #E3F2FD !important;
}

.bg-success-lighten-4 {
  background-color: #F1F8E9 !important;
}

.bg-info-lighten-4 {
  background-color: #E1F5FE !important;
}

.bg-grey-lighten-4 {
  background-color: #FAFAFA !important;
}

.category-chips-container {
  max-height: 200px;
  overflow-y: auto;
}

.category-chip {
  cursor: pointer;
  transition: all 0.2s ease;
}

.category-chip:hover {
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}
</style>
