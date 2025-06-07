<template>
  <div class="version-comparison">
    <!-- 比較結果對話框 -->
    <div v-if="showComparison" class="modal-overlay" @click="closeComparison">
      <div class="modal-content comparison-modal" @click.stop>
        <div class="modal-header">
          <h3>版本比較結果</h3>
          <button @click="closeComparison" class="close-btn">&times;</button>
        </div>
        
        <div class="modal-body">
          <div v-if="comparisonResult" class="comparison-content">
            <!-- 版本資訊 -->
            <div class="version-info-section">
              <div class="version-header-row">
                <div class="version-info-card version-a">
                  <h4>版本 A</h4>
                  <div class="version-details">
                    <span class="version-number">v{{ comparisonResult.version_a.version }}</span>
                    <span class="version-date">{{ formatDate(comparisonResult.version_a.created_at) }}</span>
                  </div>
                  <div class="version-comment">
                    {{ comparisonResult.version_a.comment || '無註解' }}
                  </div>
                </div>
                
                <div class="vs-divider">
                  <span>VS</span>
                </div>
                
                <div class="version-info-card version-b">
                  <h4>版本 B</h4>
                  <div class="version-details">
                    <span class="version-number">v{{ comparisonResult.version_b.version }}</span>
                    <span class="version-date">{{ formatDate(comparisonResult.version_b.created_at) }}</span>
                  </div>
                  <div class="version-comment">
                    {{ comparisonResult.version_b.comment || '無註解' }}
                  </div>
                </div>
              </div>
            </div>

            <!-- 差異統計 -->
            <div class="differences-summary">
              <h4>差異統計</h4>
              <div class="summary-stats">
                <div class="stat-item added">
                  <span class="stat-icon">➕</span>
                  <span class="stat-label">新增</span>
                  <span class="stat-count">{{ Object.keys(comparisonResult.differences.added).length }}</span>
                </div>
                <div class="stat-item removed">
                  <span class="stat-icon">➖</span>
                  <span class="stat-label">刪除</span>
                  <span class="stat-count">{{ Object.keys(comparisonResult.differences.removed).length }}</span>
                </div>
                <div class="stat-item modified">
                  <span class="stat-icon">✏️</span>
                  <span class="stat-label">修改</span>
                  <span class="stat-count">{{ Object.keys(comparisonResult.differences.modified).length }}</span>
                </div>
                <div class="stat-item unchanged">
                  <span class="stat-icon">✅</span>
                  <span class="stat-label">未變更</span>
                  <span class="stat-count">{{ Object.keys(comparisonResult.differences.unchanged).length }}</span>
                </div>
              </div>
            </div>

            <!-- 詳細差異 -->
            <div class="differences-details">
              <!-- 新增的項目 -->
              <div v-if="Object.keys(comparisonResult.differences.added).length > 0" class="diff-section added-section">
                <h5 class="diff-title">➕ 新增項目</h5>
                <div class="diff-items">
                  <div v-for="(value, key) in comparisonResult.differences.added" :key="key" class="diff-item">
                    <div class="diff-key">{{ formatFieldName(key) }}</div>
                    <div class="diff-value added-value">{{ formatValue(value) }}</div>
                  </div>
                </div>
              </div>

              <!-- 刪除的項目 -->
              <div v-if="Object.keys(comparisonResult.differences.removed).length > 0" class="diff-section removed-section">
                <h5 class="diff-title">➖ 刪除項目</h5>
                <div class="diff-items">
                  <div v-for="(value, key) in comparisonResult.differences.removed" :key="key" class="diff-item">
                    <div class="diff-key">{{ formatFieldName(key) }}</div>
                    <div class="diff-value removed-value">{{ formatValue(value) }}</div>
                  </div>
                </div>
              </div>

              <!-- 修改的項目 -->
              <div v-if="Object.keys(comparisonResult.differences.modified).length > 0" class="diff-section modified-section">
                <h5 class="diff-title">✏️ 修改項目</h5>
                <div class="diff-items">
                  <div v-for="(change, key) in comparisonResult.differences.modified" :key="key" class="diff-item">
                    <div class="diff-key">{{ formatFieldName(key) }}</div>
                    <div class="diff-change">
                      <div class="old-value">
                        <span class="change-label">原值：</span>
                        <span class="value">{{ formatValue(change.old_value) }}</span>
                      </div>
                      <div class="arrow">→</div>
                      <div class="new-value">
                        <span class="change-label">新值：</span>
                        <span class="value">{{ formatValue(change.new_value) }}</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- 如果沒有差異 -->
              <div v-if="!hasDifferences" class="no-differences">
                <div class="no-diff-icon">✅</div>
                <h4>無差異</h4>
                <p>這兩個版本的資料完全相同</p>
              </div>
            </div>
          </div>
          
          <!-- 載入中 -->
          <div v-else-if="isLoading" class="loading-state">
            <LoadingSpinner size="lg" />
            <p>正在比較版本...</p>
          </div>
          
          <!-- 錯誤狀態 -->
          <div v-else class="error-state">
            <span class="error-icon">⚠️</span>
            <p>載入比較結果失敗</p>
          </div>
        </div>
        
        <div class="modal-footer">
          <button @click="closeComparison" class="btn btn-primary">
            關閉
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import type { GrantVersionCompareResult } from '@/services/grantVersionsService'
import LoadingSpinner from '@/components/ui/LoadingSpinner.vue'

// Props
interface Props {
  modelValue: boolean
  comparisonResult?: GrantVersionCompareResult | null
  isLoading?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  comparisonResult: null,
  isLoading: false
})

// Emits
const emit = defineEmits<{
  'update:modelValue': [value: boolean]
}>()

// Computed
const showComparison = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

const hasDifferences = computed(() => {
  if (!props.comparisonResult) return false
  
  const { added, removed, modified } = props.comparisonResult.differences
  return Object.keys(added).length > 0 || 
         Object.keys(removed).length > 0 || 
         Object.keys(modified).length > 0
})

// Methods
const closeComparison = () => {
  showComparison.value = false
}

const formatDate = (dateString: string): string => {
  return new Date(dateString).toLocaleDateString('zh-TW', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const formatFieldName = (key: string): string => {
  // 將欄位名稱轉換為更易讀的格式
  const fieldNames: Record<string, string> = {
    '1': '步驟1 - 申請人資料',
    '2': '步驟2 - 土地資料',
    '3': '步驟3 - 灌溉調控設施',
    '4': '步驟4 - 田間管路',
    '5': '步驟5 - 現場勘查',
    '6': '步驟6 - 補助申請資料',
    '7': '步驟7 - 變更設計及結案申報',
    '8': '步驟8 - 佐證及相關文件',
    'metadata': '案件基本資料'
  }
  
  return fieldNames[key] || key
}

const formatValue = (value: any): string => {
  if (value === null || value === undefined) {
    return '(空值)'
  }
  
  if (typeof value === 'object') {
    if (Array.isArray(value)) {
      return `[陣列 - ${value.length} 項目]`
    }
    return `{物件 - ${Object.keys(value).length} 屬性}`
  }
  
  if (typeof value === 'boolean') {
    return value ? '是' : '否'
  }
  
  if (typeof value === 'number') {
    return value.toString()
  }
  
  return String(value)
}
</script>

<style scoped>
.version-comparison {
  @apply relative;
}

.modal-overlay {
  @apply fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50;
}

.comparison-modal {
  @apply bg-white rounded-lg shadow-xl w-full max-w-4xl max-h-[90vh] mx-4 flex flex-col;
}

.modal-header {
  @apply flex items-center justify-between p-6 border-b;
}

.modal-header h3 {
  @apply text-xl font-semibold;
}

.close-btn {
  @apply text-gray-400 hover:text-gray-600 text-2xl;
}

.modal-body {
  @apply flex-1 overflow-y-auto p-6;
}

.version-info-section {
  @apply mb-6;
}

.version-header-row {
  @apply flex items-center gap-4;
}

.version-info-card {
  @apply flex-1 p-4 border rounded-lg;
}

.version-info-card.version-a {
  @apply border-blue-200 bg-blue-50;
}

.version-info-card.version-b {
  @apply border-green-200 bg-green-50;
}

.version-info-card h4 {
  @apply text-lg font-semibold mb-2;
}

.version-details {
  @apply flex items-center gap-3 mb-2;
}

.version-number {
  @apply px-2 py-1 bg-gray-100 text-gray-800 rounded text-sm font-medium;
}

.version-date {
  @apply text-sm text-gray-500;
}

.version-comment {
  @apply text-sm text-gray-700;
}

.vs-divider {
  @apply flex items-center justify-center w-16 h-16 bg-gray-100 rounded-full;
}

.vs-divider span {
  @apply text-sm font-bold text-gray-600;
}

.differences-summary {
  @apply mb-6;
}

.differences-summary h4 {
  @apply text-lg font-semibold mb-3;
}

.summary-stats {
  @apply flex gap-4;
}

.stat-item {
  @apply flex items-center gap-2 px-3 py-2 rounded-lg;
}

.stat-item.added {
  @apply bg-green-100 text-green-800;
}

.stat-item.removed {
  @apply bg-red-100 text-red-800;
}

.stat-item.modified {
  @apply bg-yellow-100 text-yellow-800;
}

.stat-item.unchanged {
  @apply bg-gray-100 text-gray-600;
}

.stat-icon {
  @apply text-lg;
}

.stat-label {
  @apply text-sm font-medium;
}

.stat-count {
  @apply text-sm font-bold;
}

.differences-details {
  @apply space-y-6;
}

.diff-section {
  @apply border rounded-lg p-4;
}

.diff-section.added-section {
  @apply border-green-200 bg-green-50;
}

.diff-section.removed-section {
  @apply border-red-200 bg-red-50;
}

.diff-section.modified-section {
  @apply border-yellow-200 bg-yellow-50;
}

.diff-title {
  @apply text-md font-semibold mb-3;
}

.diff-items {
  @apply space-y-3;
}

.diff-item {
  @apply bg-white rounded p-3 border;
}

.diff-key {
  @apply font-medium text-gray-800 mb-2;
}

.diff-value {
  @apply text-sm;
}

.diff-value.added-value {
  @apply text-green-700 bg-green-100 px-2 py-1 rounded;
}

.diff-value.removed-value {
  @apply text-red-700 bg-red-100 px-2 py-1 rounded;
}

.diff-change {
  @apply flex items-center gap-3;
}

.old-value,
.new-value {
  @apply flex-1;
}

.change-label {
  @apply text-xs text-gray-500 block mb-1;
}

.old-value .value {
  @apply text-red-700 bg-red-100 px-2 py-1 rounded text-sm;
}

.new-value .value {
  @apply text-green-700 bg-green-100 px-2 py-1 rounded text-sm;
}

.arrow {
  @apply text-gray-400 font-bold;
}

.no-differences {
  @apply text-center py-8;
}

.no-diff-icon {
  @apply text-4xl mb-4;
}

.no-differences h4 {
  @apply text-lg font-semibold text-gray-800 mb-2;
}

.no-differences p {
  @apply text-gray-600;
}

.loading-state,
.error-state {
  @apply text-center py-8;
}

.loading-state p,
.error-state p {
  @apply mt-4 text-gray-600;
}

.error-icon {
  @apply text-2xl;
}

.modal-footer {
  @apply flex items-center justify-end gap-3 p-6 border-t;
}

.btn {
  @apply px-4 py-2 rounded font-medium transition-colors;
}

.btn-primary {
  @apply bg-blue-600 text-white hover:bg-blue-700;
}
</style>
