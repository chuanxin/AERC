<template>
  <!-- 篩選工具欄容器 -->
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
          <template #default>
            <div class="d-flex align-center w-100">
              <!-- 主篩選輸入框 -->
              <v-text-field
                v-model="quickFilter"
                label="快速篩選（申請人/地段/地號/案件編號）"
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

              <!-- 年度範圍指示器 -->
              <v-chip
                size="small"
                color="primary"
                variant="outlined"
                class="me-2 flex-shrink-0"
              >
                <v-icon
                  size="small"
                  class="me-1"
                >
                  mdi-calendar
                </v-icon>
                民國{{ filterCriteria.yearStart }}~{{ filterCriteria.yearEnd }}年
              </v-chip>

              <!-- 篩選狀態指示器 -->
              <v-chip
                v-if="hasActiveFilters"
                size="small"
                color="success"
                variant="outlined"
                class="me-2 flex-shrink-0"
              >
                <v-icon
                  size="small"
                  class="me-1"
                >
                  mdi-filter-check
                </v-icon>
                已篩選
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
          <v-container
            fluid
            class="pa-0"
          >
            <v-row dense>
              <!-- 詳細篩選欄位 -->
              <v-col cols="12">
                <div class="d-flex align-center mb-3">
                  <v-icon
                    size="small"
                    class="me-2"
                  >
                    mdi-filter-outline
                  </v-icon>
                  <span class="text-body-2 font-weight-medium">詳細篩選欄位</span>
                </div>
              </v-col>

              <!-- 申請人姓名 -->
              <v-col
                cols="12"
                md="6"
              >
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
                    @click="resetFilters"
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
                    @click="applyFilters"
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
import { ref, computed, watch } from 'vue'
import type { GeoJsonFeature, GisStatistics } from '../../types/gis'
import {
  applyFrontendFilters,
  type FilterCriteria
} from '../../utils/frontendFilters'

// Props 定義
interface FilterToolbarProps {
  allFeatures: GeoJsonFeature[]
  statistics: GisStatistics | null
  loading: boolean
  initialCriteria?: FilterCriteria | null
  initialExpanded?: boolean
}

const props = withDefaults(defineProps<FilterToolbarProps>(), {
  loading: false,
  initialExpanded: false,
  initialCriteria: null
})

// Emits 定義
interface FilterChangeEvent {
  criteria: FilterCriteria
  results: GeoJsonFeature[]
  resultCount: number
}

const emit = defineEmits<{
  'filter-change': [event: FilterChangeEvent]
  'expanded-change': [expanded: boolean]
  'criteria-reset': []
}>()

// 內部狀態
const expandedPanel = ref<string[]>(props.initialExpanded ? ['filter'] : [])
const quickFilter = ref('')

// 獲取當前年度（民國年）
const getCurrentYear = () => {
  return new Date().getFullYear() - 1911
}

// 篩選條件
const filterCriteria = ref<FilterCriteria>({
  applicantName: '',
  landSection: '',
  landNumber: '',
  caseNumber: '',
  sourceSystem: null,
  yearStart: getCurrentYear(),
  yearEnd: getCurrentYear(),
  ...(props.initialCriteria || {})
})

// 年度輸入驗證規則
const yearStartValidation = (value: number) => {
  if (!value) return '請輸入起始年度'
  if (value < 97) return '年度不可小於民國97年'
  if (value > getCurrentYear()) return `年度不可大於民國${getCurrentYear()}年`
  if (filterCriteria.value.yearEnd && value > filterCriteria.value.yearEnd) {
    return '起始年度不可大於結束年度'
  }
  return true
}

const yearEndValidation = (value: number) => {
  if (!value) return '請輸入結束年度'
  if (value < 97) return '年度不可小於民國97年'
  if (value > getCurrentYear()) return `年度不可大於民國${getCurrentYear()}年`
  if (filterCriteria.value.yearStart && value < filterCriteria.value.yearStart) {
    return '結束年度不可小於起始年度'
  }
  return true
}

// 檢查是否有啟用的篩選條件
const hasActiveFilters = computed(() => {
  return (
    filterCriteria.value.applicantName ||
    filterCriteria.value.landSection ||
    filterCriteria.value.landNumber ||
    filterCriteria.value.caseNumber ||
    filterCriteria.value.sourceSystem ||
    quickFilter.value ||
    filterCriteria.value.yearStart !== getCurrentYear() ||
    filterCriteria.value.yearEnd !== getCurrentYear()
  )
})

// 篩選工具欄事件處理
const onFilterFocus = () => {
  // 當快速篩選獲得焦點時，自動展開面板
  if (!expandedPanel.value.includes('filter')) {
    expandedPanel.value = ['filter']
  }
}

const onFilterBlur = () => {
  // Focus 離開時的處理邏輯（如果需要）
}

// 快速篩選變更處理
const onQuickFilterChange = () => {
  // 執行前端篩選
  performFrontendFilter()
}

// 前端篩選處理函數
const performFrontendFilter = () => {
  if (!props.allFeatures.length) return

  // 準備篩選條件
  const criteria = {
    ...filterCriteria.value,
    quickFilter: quickFilter.value
  }

  // 執行前端篩選
  const filteredResults = applyFrontendFilters(props.allFeatures, quickFilter.value, criteria)

  // 發送篩選變更事件
  emit('filter-change', {
    criteria,
    results: filteredResults,
    resultCount: filteredResults.length
  })
}

// 套用篩選
const applyFilters = async () => {
  performFrontendFilter()
}

// 重置篩選條件
const resetFilters = () => {
  const currentYear = getCurrentYear()

  // 重置所有篩選條件到初始載入條件
  filterCriteria.value = {
    applicantName: '',
    landSection: '',
    landNumber: '',
    caseNumber: '',
    sourceSystem: null,
    yearStart: currentYear,
    yearEnd: currentYear
  }

  quickFilter.value = ''

  // 發送重置事件
  emit('criteria-reset')

  // 套用重置後的篩選
  performFrontendFilter()
}

// 監聽面板展開狀態變化
watch(expandedPanel, (newValue) => {
  const isExpanded = newValue.includes('filter')
  emit('expanded-change', isExpanded)
}, { deep: true })

// 監聽 props 變化
watch(() => props.allFeatures, () => {
  if (props.allFeatures.length > 0) {
    performFrontendFilter()
  }
}, { deep: true })
</script>

<style scoped>
/* 篩選工具欄樣式 - 從原組件複製 */
.filter-toolbar-container {
  position: absolute;
  top: 20px;
  left: 20px;
  z-index: 1200;
  max-width: 600px;
  width: auto;
  min-width: 450px;
}

.filter-expansion-panels {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 12px !important;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.filter-expansion-panel {
  margin-bottom: 0 !important;
  background: transparent !important;
}

.filter-expansion-panel .v-expansion-panel-title {
  min-height: auto !important;
  padding: 12px 16px !important;
}

.filter-expansion-panel .v-expansion-panel-text {
  max-height: 400px;
  overflow-y: auto;
}

.filter-panel-title {
  background: rgba(255, 255, 255, 0.9);
  border-radius: 12px 12px 0 0;
  transition: all 0.3s ease;
}

.filter-panel-title:hover {
  background: rgba(255, 255, 255, 1);
}

.filter-panel-title .d-flex {
  gap: 8px;
  align-items: center;
  width: 100%;
  flex-wrap: wrap;
}

.filter-input {
  flex: 1;
  min-width: 200px;
}

.filter-input :deep(.v-field__input) {
  font-size: 14px;
  min-height: 32px;
}

.filter-panel-content .v-container {
  padding: 16px !important;
  background: rgba(248, 249, 250, 0.9);
}

.year-range-inputs {
  background: rgba(255, 255, 255, 0.7);
  border-radius: 8px;
  padding: 12px;
  margin: 8px 0;
}

/* 響應式設計 */
@media (max-width: 768px) {
  .filter-toolbar-container {
    left: 10px;
    right: 10px;
    max-width: none;
    min-width: auto;
    width: calc(100% - 20px);
  }

  .filter-panel-title .v-chip {
    font-size: 11px;
    height: 24px;
  }
}

@media (max-width: 480px) {
  .filter-toolbar-container {
    left: 5px;
    right: 5px;
    width: calc(100% - 10px);
    min-width: auto;
  }
}

.filter-expansion-panels .v-expansion-panel-title__icon {
  margin-left: 8px !important;
}

.filter-panel-content::-webkit-scrollbar {
  width: 6px;
}

.filter-panel-content::-webkit-scrollbar-track {
  background: rgba(0, 0, 0, 0.05);
  border-radius: 3px;
}

.filter-panel-content::-webkit-scrollbar-thumb {
  background: rgba(0, 0, 0, 0.2);
  border-radius: 3px;
}

.filter-panel-content::-webkit-scrollbar-thumb:hover {
  background: rgba(0, 0, 0, 0.3);
}
</style>