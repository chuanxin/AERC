<template>
  <!-- 篩選工具欄 -->
  <div class="filter-toolbar-container">
    <v-expansion-panels
      v-model="expandedPanel"
      class="filter-expansion-panels"
      color="surface-light"
      elevation="8"
      rounded="lg"
      variant="accordion"
    >
      <v-expansion-panel
        value="filter"
        class="filter-expansion-panel"
        rounded="lg"
      >
        <!-- 面板標題 - 包含主要篩選控制 -->
        <v-expansion-panel-title class="filter-panel-title pa-3">
          <template #default="{ expanded }">
            <div class="d-flex align-center w-100">
              <!-- 主篩選輸入框 -->
              <v-text-field
                v-model="quickFilter"
                label="快速篩選(申請人/地段/地號/案件編號)"
                prepend-inner-icon="mdi-filter-variant"
                class="filter-input me-3"
                clearable
                density="compact"
                variant="solo"
                hide-details
                single-line
                @click.stop
                @focus="onFilterFocus"
                @blur="onFilterBlur"
                @input="onQuickFilterChange"
              />

              <!-- 年度範圍指示器 - 顯示當前生效的年度範圍 -->
              <v-chip
                size="small"
                color="primary"
                variant="outlined"
                class="me-2 flex-shrink-0"
              >
                <v-icon size="small" class="me-1">mdi-calendar</v-icon>
                民國{{ props.yearRange?.current?.[0] || filterCriteria.yearStart }}~{{ props.yearRange?.current?.[1] || filterCriteria.yearEnd }}年
              </v-chip>

              <!-- 篩選狀態指示器 -->
              <v-chip
                v-if="hasActiveFilters"
                size="small"
                color="warning"
                variant="outlined"
                class="me-2 flex-shrink-0"
              >
                <v-icon size="small" class="me-1">
                  mdi-clock-outline
                </v-icon>
                待套用
              </v-chip>
            </div>
          </template>

          <!-- 自定義展開圖示 -->
          <template #actions="{ expanded }">
            <v-icon
              :icon="expanded ? 'mdi-chevron-up' : 'mdi-chevron-down'"
              color="primary"
            />
          </template>
        </v-expansion-panel-title>

        <!-- 面板內容 - 詳細篩選選項 -->
        <v-expansion-panel-text class="filter-panel-content pa-0 ma-0">
          <v-container fluid class="pa-0">
            <v-row dense>
              <!-- 詳細篩選欄位 -->
              <v-col cols="12">
                <div class="d-flex align-center mb-3">
                  <v-icon size="small" class="me-2">mdi-filter-outline</v-icon>
                  <span class="text-body-2 font-weight-medium">詳細篩選欄位</span>
                </div>
              </v-col>

              <!-- 申請人姓名 -->
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="filterCriteria.applicantName"
                  label="申請人姓名"
                  prepend-icon="mdi-account"
                  density="compact"
                  clearable
                  variant="outlined"
                  persistent-hint
                />
              </v-col>

              <!-- 地段 -->
              <v-col
                cols="12"
                md="6"
              >
                <v-text-field
                  v-model="filterCriteria.landSection"
                  label="地段"
                  prepend-icon="mdi-map-marker"
                  density="compact"
                  clearable
                  variant="outlined"
                  persistent-hint
                />
              </v-col>

              <!-- 地號 -->
              <v-col
                cols="12"
                md="6"
              >
                <v-text-field
                  v-model="filterCriteria.landNumber"
                  label="地號"
                  prepend-icon="mdi-map-marker-outline"
                  density="compact"
                  clearable
                  variant="outlined"
                  persistent-hint
                />
              </v-col>

              <!-- 案件編號 -->
              <v-col
                cols="12"
                md="6"
              >
                <v-text-field
                  v-model="filterCriteria.caseNumber"
                  label="案件編號"
                  prepend-icon="mdi-file-document"
                  density="compact"
                  clearable
                  variant="outlined"
                  persistent-hint
                />
              </v-col>

              <!-- 申請年度範圍 -->
              <v-col cols="12">
                <div class="d-flex align-center mb-6">
                  <v-icon
                    size="small"
                    class="me-2"
                  >
                    mdi-calendar-range
                  </v-icon>
                  <span class="text-body-2 font-weight-medium">申請年度範圍</span>
                </div>
                <v-row
                  dense
                  class="year-range-inputs pl-2"
                >
                  <v-col cols="5">
                    <v-text-field
                      v-model.number="filterCriteria.yearStart"
                      label="起始年度"
                      placeholder="97"
                      type="number"
                      :min="97"
                      :max="getCurrentYear()"
                      density="compact"
                      variant="outlined"
                      prefix="民國"
                      suffix="年"
                      hide-details="auto"
                      :rules="[yearStartValidation]"
                      @input="onYearInputChange"
                    />
                  </v-col>
                  <v-col
                    cols="2"
                    class="d-flex align-center justify-center"
                  >
                    <v-icon color="grey">
                      mdi-arrow-right
                    </v-icon>
                  </v-col>
                  <v-col cols="5">
                    <v-text-field
                      v-model.number="filterCriteria.yearEnd"
                      label="結束年度"
                      placeholder="114"
                      type="number"
                      :min="97"
                      :max="getCurrentYear()"
                      density="compact"
                      variant="outlined"
                      prefix="民國"
                      suffix="年"
                      hide-details="auto"
                      :rules="[yearEndValidation]"
                      @input="onYearInputChange"
                    />
                  </v-col>
                </v-row>
              </v-col>

              <v-divider class="my-3" />

              <!-- 操作按鈕 -->
              <v-row dense>
                <v-col cols="4">
                  <v-btn
                    variant="text"
                    color="primary"
                    size="large"
                    block
                    rounded="md"
                    @click="handleReset"
                  >
                    <v-icon class="me-2">
                      mdi-refresh
                    </v-icon>
                    重置
                  </v-btn>
                </v-col>

                <v-spacer />

                <v-col cols="8">
                  <v-btn
                    color="primary"
                    variant="flat"
                    size="large"
                    block
                    rounded="md"
                    :loading="loading"
                    @click="handleApply"
                  >
                    <v-icon class="me-2">
                      mdi-magnify
                    </v-icon>
                    套用篩選
                  </v-btn>
                </v-col>
              </v-row>
            </v-row>
          </v-container>
        </v-expansion-panel-text>
      </v-expansion-panel>
    </v-expansion-panels>
  </div>
</template>

<script setup lang="ts">
import { getInitialOverlayLoadingParams } from '@/utils/frontendFilters';
import type { FilterCriteria } from '@/utils/frontendFilters';

// 組件的props定義
const props = defineProps<{
  loading?: boolean;
  yearRange?: { current: [number, number]; min: number; max: number };
}>();

// 組件的事件
const emit = defineEmits<{
  'quick-filter-change': [value: string];
  'filter-apply': [criteria: FilterCriteria];
  'filter-reset': [];
  'update:yearRange': [range: [number, number]];
}>();

// 篩選工具欄狀態
const expandedPanel = ref<string[]>([]);
const quickFilter = ref('');

// 獲取當前年度（民國年）
const getCurrentYear = () => {
  return new Date().getFullYear() - 1911;
};

// 初始化篩選條件
const initialParams = getInitialOverlayLoadingParams();
const filterCriteria = ref<FilterCriteria>({
  applicantName: '',
  landSection: '',
  landNumber: '',
  caseNumber: '',
  sourceSystem: null,
  yearStart: initialParams.apply_year_min!,
  yearEnd: initialParams.apply_year_max!
});

// 年度輸入驗證規則
const yearStartValidation = (value: number) => {
  if (!value) return '請輸入起始年度';
  if (value < 97) return '年度不可小於民國97年';
  if (value > getCurrentYear()) return `年度不可大於民國${getCurrentYear()}年`;
  if (filterCriteria.value.yearEnd && value > filterCriteria.value.yearEnd) {
    return '起始年度不可大於結束年度';
  }
  return true;
};

const yearEndValidation = (value: number) => {
  if (!value) return '請輸入結束年度';
  if (value < 97) return '年度不可小於民國97年';
  if (value > getCurrentYear()) return `年度不可大於民國${getCurrentYear()}年`;
  if (filterCriteria.value.yearStart && value < filterCriteria.value.yearStart) {
    return '結束年度不可小於起始年度';
  }
  return true;
};

// 檢查是否有尚未套用的篩選條件變更
const hasActiveFilters = computed(() => {
  // 檢查是否有文字篩選條件
  const hasTextFilters = !!(
    quickFilter.value ||
    filterCriteria.value.applicantName ||
    filterCriteria.value.landSection ||
    filterCriteria.value.landNumber ||
    filterCriteria.value.caseNumber ||
    filterCriteria.value.sourceSystem
  );

  // 檢查年度範圍是否與當前生效的年度範圍不同
  const currentYearStart = props.yearRange?.current?.[0] || initialParams.apply_year_min;
  const currentYearEnd = props.yearRange?.current?.[1] || initialParams.apply_year_max;
  const hasYearChanges =
    filterCriteria.value.yearStart !== currentYearStart ||
    filterCriteria.value.yearEnd !== currentYearEnd;

  return hasTextFilters || hasYearChanges;
});

// 防抖計時器
let filterTimeout: ReturnType<typeof setTimeout>;

// 篩選工具欄 Focus 事件
const onFilterFocus = () => {
  // 當快速篩選獲得焦點時，自動展開面板
  if (!expandedPanel.value.includes('filter')) {
    expandedPanel.value = ['filter'];
  }
};

// 篩選工具欄 Blur 事件
const onFilterBlur = () => {
  // 不自動收合，讓用戶手動控制
};

// 快速篩選變更處理
const onQuickFilterChange = () => {
  clearTimeout(filterTimeout);
  filterTimeout = setTimeout(() => {
    emit('quick-filter-change', quickFilter.value);
  }, 300);
};

// 年度輸入變更處理
const onYearInputChange = () => {
  // 確保年度值是有效的數字
  if (filterCriteria.value.yearStart && filterCriteria.value.yearEnd) {
    // 如果起始年度大於結束年度，自動調整結束年度
    if (filterCriteria.value.yearStart > filterCriteria.value.yearEnd) {
      filterCriteria.value.yearEnd = filterCriteria.value.yearStart;
    }
  }

  // 確保年度值在有效範圍內
  const currentYear = getCurrentYear();
  if (filterCriteria.value.yearStart) {
    filterCriteria.value.yearStart = Math.max(97, Math.min(currentYear, filterCriteria.value.yearStart));
  }
  if (filterCriteria.value.yearEnd) {
    filterCriteria.value.yearEnd = Math.max(97, Math.min(currentYear, filterCriteria.value.yearEnd));
  }

  // 移除立即發送年度範圍更新事件 - 改為在套用篩選時才發送
  // emit('update:yearRange', [filterCriteria.value.yearStart, filterCriteria.value.yearEnd]);
};

// 套用篩選
const handleApply = () => {
  // 發送年度範圍更新事件
  emit('update:yearRange', [filterCriteria.value.yearStart, filterCriteria.value.yearEnd]);

  // 發送篩選條件
  emit('filter-apply', { ...filterCriteria.value });
};

// 重置篩選條件
const handleReset = () => {
  // 獲取統一的初始載入條件參數
  const initialParams = getInitialOverlayLoadingParams();

  // 重置所有篩選條件到初始載入條件
  quickFilter.value = '';
  filterCriteria.value = {
    applicantName: '',
    landSection: '',
    landNumber: '',
    caseNumber: '',
    sourceSystem: initialParams.source_system || null,
    yearStart: initialParams.apply_year_min!,
    yearEnd: initialParams.apply_year_max!
  };

  // 發送年度範圍更新事件
  emit('update:yearRange', [initialParams.apply_year_min!, initialParams.apply_year_max!]);

  // 發送重置事件
  emit('filter-reset');
};

// 監聽外部傳入的年度範圍變化
watch(() => props.yearRange?.current, (newRange) => {
  if (newRange && newRange.length === 2) {
    filterCriteria.value.yearStart = newRange[0];
    filterCriteria.value.yearEnd = newRange[1];
  }
}, { immediate: true, deep: true });
</script>

<style scoped>
/* 篩選工具欄樣式 */
.filter-toolbar-container {
  position: absolute;
  top: 10px;
  left: 10px;
  z-index: 1002;
  width: 480px; /* 固定寬度，不會因展開而改變 */
  max-width: calc(100vw - 120px); /* 確保不會與右側控制面板重疊 */
}

/* v-expansion-panels 主體樣式 */
.filter-expansion-panels {
  border: 1px solid rgba(0, 0, 0, 0.1) !important;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15) !important;
  border-radius: 12px !important; /* lg 圓角 */
  overflow: hidden; /* 確保內容不會超出圓角 */
  width: 100% !important; /* 繼承容器固定寬度 */
  max-width: 100% !important; /* 防止內容撐大 */
}

/* v-expansion-panel 個別面板樣式 */
.filter-expansion-panel {
  width: 100% !important; /* 確保與父容器同寬 */
  max-width: 100% !important; /* 防止內容撐大 */
}

/* 確保面板標題與主容器同寬 */
.filter-expansion-panel .v-expansion-panel-title {
  width: 100% !important;
}

/* 確保面板內容與主容器同寬 */
.filter-expansion-panel .v-expansion-panel-text {
  width: 100% !important;
}

/* 面板標題樣式 */
.filter-panel-title {
  min-height: auto !important;
  width: 100% !important;
  max-width: 100% !important;
  overflow: hidden; /* 防止內容溢出 */
}

/* 面板標題內容區域 */
.filter-panel-title .d-flex {
  width: 100% !important;
  max-width: 100% !important;
  overflow: hidden; /* 防止內容溢出 */
}

/* 主篩選輸入框樣式 */
.filter-input {
  min-width: 200px;
  max-width: 260px; /* 減少最大寬度以適應固定容器 */
}

/* 內容區域的容器樣式 */
.filter-panel-content .v-container {
  max-width: 100% !important;
  width: 100% !important;
}

/* 年度範圍輸入框樣式 */
.year-range-inputs {
  margin: 0 !important;
}

.year-range-inputs .v-col {
  padding: 0 4px !important;
}

.year-range-inputs .v-text-field {
  font-size: 0.875rem;
}

.year-range-inputs .v-field__prefix,
.year-range-inputs .v-field__suffix {
  font-size: 0.8rem;
  color: rgba(0, 0, 0, 0.6);
  font-weight: 500;
}

/* 年度輸入框焦點樣式 */
.year-range-inputs .v-text-field .v-field--focused {
  box-shadow: 0 0 0 2px rgba(25, 118, 210, 0.2);
}

/* 確保數字輸入框樣式一致 */
.year-range-inputs input[type="number"] {
  text-align: center;
  font-weight: 500;
}

/* 移除 Chrome 的數字輸入框箭頭 */
.year-range-inputs input[type="number"]::-webkit-outer-spin-button,
.year-range-inputs input[type="number"]::-webkit-inner-spin-button {
  -webkit-appearance: none;
  margin: 0;
}

/* 行動版時進一步優化 */
@media (max-width: 768px) {
  /* 行動版年度輸入框優化 */
  .year-range-inputs .v-text-field {
    font-size: 0.8rem;
  }

  .year-range-inputs .v-field__prefix,
  .year-range-inputs .v-field__suffix {
    font-size: 0.75rem;
  }
}

@media (max-width: 480px) {
  .filter-toolbar-container {
    width: calc(100vw - 16px) !important;
    max-width: 100%;
  }

  .filter-input {
    min-width: 120px;
    max-width: 150px;
  }

  /* 小屏幕時隱藏部分 chips 或使用更小的樣式 */
  .filter-panel-title .v-chip {
    font-size: 0.7rem;
    height: 20px;
    padding: 0 8px;
  }
}
</style>
