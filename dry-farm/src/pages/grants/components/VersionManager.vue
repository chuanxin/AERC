<template>
  <div class="version-manager">
    <!-- 版本摘要區域 -->
    <div class="version-summary-card">
      <div class="version-header">
        <h3 class="version-title">版本管理</h3>
        <div class="version-badge">
          <span v-if="hasVersions" class="badge success">
            共 {{ totalVersions }} 個版本
          </span>
          <span v-else class="badge info">
            尚無版本
          </span>
        </div>
      </div>

      <!-- 目前模式指示 -->
      <div class="current-mode">
        <div class="mode-indicator">
          <span class="mode-label">目前模式：</span>
          <span :class="['mode-badge', currentVersionMode]">
            {{ currentVersionMode === 'local' ? '本地編輯' : '版本檢視' }}
          </span>
        </div>
        
        <!-- 現行版本資訊 -->
        <div v-if="activeVersionNumber > 0" class="active-version-info">
          <span class="active-label">現行版本：</span>
          <span class="version-number">v{{ activeVersionNumber }}</span>
        </div>
      </div>

      <!-- 快捷操作按鈕 -->
      <div class="quick-actions">
        <button 
          @click="handleCreateVersion"
          :disabled="isSaving || isVersionLoading"
          class="btn btn-primary"
        >
          <LoadingSpinner v-if="isSaving" size="sm" />
          <span v-else>💾</span>
          建立新版本
        </button>

        <button 
          v-if="currentVersionMode === 'database'"
          @click="switchToLocalMode"
          :disabled="isLoading"
          class="btn btn-secondary"
        >
          📝 切換到編輯模式
        </button>

        <button 
          v-else-if="hasVersions"
          @click="loadVersionManagement"
          :disabled="isVersionLoading"
          class="btn btn-secondary"
        >
          <LoadingSpinner v-if="isVersionLoading" size="sm" />
          <span v-else>📋</span>
          檢視版本列表
        </button>
      </div>

      <!-- 錯誤訊息 -->
      <div v-if="versionError" class="error-message">
        <span class="error-icon">⚠️</span>
        {{ versionError }}
      </div>
    </div>

    <!-- 版本詳細管理 -->
    <div v-if="showVersionDetails" class="version-details">
      <!-- 版本列表 -->
      <div class="version-list">
        <h4>版本歷史</h4>
        <div v-if="versionSummary?.versions_list" class="versions">
          <div 
            v-for="version in versionSummary.versions_list" 
            :key="version.id"
            :class="['version-item', { 
              'active': version.id === activeVersion?.id,
              'current': currentVersionMode === 'database' && version.id === activeVersion?.id 
            }]"
          >
            <div class="version-info">
              <div class="version-meta">
                <span class="version-number">v{{ version.version }}</span>
                <span class="version-date">{{ formatDate(version.created_at) }}</span>
              </div>
              <div class="version-comment">
                {{ version.comment || '無註解' }}
              </div>
              <div class="version-author">
                建立者：{{ version.created_by_name || '未知' }}
              </div>
            </div>
            
            <div class="version-actions">
              <button 
                @click="handleSwitchToVersion(version.id)"
                :disabled="isVersionLoading"
                class="btn btn-sm btn-outline"
              >
                檢視
              </button>
              
              <button 
                v-if="version.id !== activeVersion?.id"
                @click="handleSetActive(version.id)"
                :disabled="isSaving"
                class="btn btn-sm btn-primary"
              >
                設為現行
              </button>
              
              <span v-else class="active-tag">現行版本</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 版本比較 -->
      <div class="version-compare">
        <h4>版本比較</h4>
        <div class="compare-controls">
          <select v-model="compareVersionA" class="version-select">
            <option value="">選擇版本 A</option>
            <option 
              v-for="version in versionSummary?.versions_list" 
              :key="version.id"
              :value="version.id"
            >
              v{{ version.version }} - {{ version.comment || '無註解' }}
            </option>
          </select>
          
          <span class="compare-vs">vs</span>
          
          <select v-model="compareVersionB" class="version-select">
            <option value="">選擇版本 B</option>
            <option 
              v-for="version in versionSummary?.versions_list" 
              :key="version.id"
              :value="version.id"
            >
              v{{ version.version }} - {{ version.comment || '無註解' }}
            </option>
          </select>
          
          <button 
            @click="handleCompareVersions"
            :disabled="!compareVersionA || !compareVersionB || isVersionLoading"
            class="btn btn-secondary"
          >
            比較
          </button>
        </div>
      </div>
    </div>

    <!-- 建立版本對話框 -->
    <div v-if="showCreateVersionDialog" class="modal-overlay" @click="closeCreateVersionDialog">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>建立新版本</h3>
          <button @click="closeCreateVersionDialog" class="close-btn">&times;</button>
        </div>
        
        <div class="modal-body">
          <div class="form-group">
            <label for="version-comment">版本說明：</label>
            <textarea 
              id="version-comment"
              v-model="newVersionComment"
              placeholder="請輸入版本說明（選填）"
              rows="3"
              class="form-control"
            ></textarea>
          </div>
          
          <div class="version-preview">
            <p class="preview-title">將包含以下資料：</p>
            <ul class="data-list">
              <li v-for="step in getStepsWithData()" :key="step">
                步驟 {{ step }} 的資料
              </li>
            </ul>
          </div>
        </div>
        
        <div class="modal-footer">
          <button @click="closeCreateVersionDialog" class="btn btn-secondary">
            取消
          </button>
          <button 
            @click="confirmCreateVersion"
            :disabled="isSaving"
            class="btn btn-primary"
          >
            <LoadingSpinner v-if="isSaving" size="sm" />
            確認建立
          </button>
        </div>
      </div>
    </div>

    <!-- 載入中覆蓋層 -->
    <div v-if="isVersionLoading" class="loading-overlay">
      <LoadingSpinner size="lg" />
      <p>處理版本資料中...</p>
    </div>

    <!-- 版本比較結果 -->
    <VersionComparison 
      v-model="showComparisonDialog"
      :comparison-result="comparisonResult"
      :is-loading="isComparingVersions"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { storeToRefs } from 'pinia'
import { useGrantsStore } from '@/stores/grants'
import { GrantStorage } from '@/utils/grant-storage'
import LoadingSpinner from '@/components/ui/LoadingSpinner.vue'
import VersionComparison from './VersionComparison.vue'
import type { GrantVersionCompareResult } from '@/services/grantVersionsService'

// Store
const grantsStore = useGrantsStore()

// Local state
const showVersionDetails = ref(false)
const showCreateVersionDialog = ref(false)
const newVersionComment = ref('')
const compareVersionA = ref<number | ''>('')
const compareVersionB = ref<number | ''>('')
const showComparisonDialog = ref(false)
const comparisonResult = ref<GrantVersionCompareResult | null>(null)
const isComparingVersions = ref(false)

// Computed properties from store
const {
  currentGrant,
  versionSummary,
  activeVersion,
  isVersionLoading,
  currentVersionMode,
  versionError,
  hasVersions,
  totalVersions,
  activeVersionNumber,
  isSaving,
  isLoading,
  formData
} = storeToRefs(grantsStore)

// Methods from store
const {
  loadVersionSummary,
  createVersionFromLocalData,
  loadActiveVersion,
  switchToVersionMode,
  switchToLocalMode,
  makeVersionActive
} = grantsStore

// Local methods
const loadVersionManagement = async () => {
  showVersionDetails.value = true
  await Promise.all([
    loadVersionSummary(),
    loadActiveVersion()
  ])
}

const handleCreateVersion = () => {
  showCreateVersionDialog.value = true
  newVersionComment.value = `版本建立於 ${new Date().toLocaleString()}`
}

const closeCreateVersionDialog = () => {
  showCreateVersionDialog.value = false
  newVersionComment.value = ''
}

const confirmCreateVersion = async () => {
  try {
    const result = await createVersionFromLocalData(newVersionComment.value || undefined)
    if (result) {
      closeCreateVersionDialog()
      // 如果正在顯示版本詳情，重新載入
      if (showVersionDetails.value) {
        await loadVersionSummary()
      }
    }
  } catch (error) {
    console.error('建立版本失敗:', error)
  }
}

const handleSwitchToVersion = async (versionId: number) => {
  await switchToVersionMode(versionId)
}

const handleSetActive = async (versionId: number) => {
  const success = await makeVersionActive(versionId)
  if (success && showVersionDetails.value) {
    await loadVersionSummary()
  }
}

const handleCompareVersions = async () => {
  if (compareVersionA.value && compareVersionB.value) {
    try {
      isComparingVersions.value = true
      const result = await grantsStore.compareVersions(
        Number(compareVersionA.value), 
        Number(compareVersionB.value)
      )
      if (result) {
        comparisonResult.value = result
        showComparisonDialog.value = true
        console.log('版本比較結果:', result)
      }
    } catch (error) {
      console.error('版本比較失敗:', error)
    } finally {
      isComparingVersions.value = false
    }
  }
}

const getStepsWithData = (): number[] => {
  if (!currentGrant.value?.case_number) return []
  
  const steps: number[] = []
  const caseNumber = currentGrant.value.case_number
  
  for (let i = 1; i <= 8; i++) {
    // 首先檢查 formData
    if (formData.value[i] && Object.keys(formData.value[i]).length > 1) {
      steps.push(i)
      continue
    }
    
    // 如果 formData 沒有資料，檢查 localStorage
    const stepData = GrantStorage.getStepData(caseNumber, i)
    if (stepData && Object.keys(stepData).length > 1) {
      steps.push(i)
    }
  }
  return steps
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

// 監聽案件變更
watch(() => currentGrant.value?.case_number, async (newCaseNumber) => {
  if (newCaseNumber) {
    await loadVersionSummary()
  }
}, { immediate: true })

// 組件載入時初始化
onMounted(async () => {
  if (currentGrant.value?.case_number) {
    await loadVersionSummary()
  }
})
</script>

<style scoped>
.version-manager {
  @apply space-y-4;
}

.version-summary-card {
  @apply bg-white rounded-lg shadow p-6 border;
}

.version-header {
  @apply flex items-center justify-between mb-4;
}

.version-title {
  @apply text-lg font-semibold text-gray-800;
}

.version-badge .badge {
  @apply px-3 py-1 rounded-full text-sm font-medium;
}

.badge.success {
  @apply bg-green-100 text-green-800;
}

.badge.info {
  @apply bg-blue-100 text-blue-800;
}

.current-mode {
  @apply flex items-center justify-between mb-4 p-3 bg-gray-50 rounded;
}

.mode-indicator {
  @apply flex items-center gap-2;
}

.mode-label {
  @apply text-sm text-gray-600;
}

.mode-badge {
  @apply px-2 py-1 rounded text-xs font-medium;
}

.mode-badge.local {
  @apply bg-blue-100 text-blue-800;
}

.mode-badge.database {
  @apply bg-purple-100 text-purple-800;
}

.active-version-info {
  @apply flex items-center gap-2;
}

.active-label {
  @apply text-sm text-gray-600;
}

.version-number {
  @apply px-2 py-1 bg-green-100 text-green-800 rounded text-xs font-medium;
}

.quick-actions {
  @apply flex gap-3 mb-4;
}

.btn {
  @apply px-4 py-2 rounded font-medium transition-colors flex items-center gap-2;
}

.btn-primary {
  @apply bg-blue-600 text-white hover:bg-blue-700 disabled:bg-gray-400;
}

.btn-secondary {
  @apply bg-gray-200 text-gray-800 hover:bg-gray-300 disabled:bg-gray-100;
}

.btn-outline {
  @apply border border-gray-300 text-gray-700 hover:bg-gray-50;
}

.btn-sm {
  @apply px-2 py-1 text-sm;
}

.error-message {
  @apply flex items-center gap-2 p-3 bg-red-50 text-red-700 rounded border border-red-200;
}

.version-details {
  @apply bg-white rounded-lg shadow p-6 border space-y-6;
}

.version-list h4,
.version-compare h4 {
  @apply text-md font-semibold text-gray-800 mb-3;
}

.versions {
  @apply space-y-3;
}

.version-item {
  @apply flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50;
}

.version-item.active {
  @apply border-green-500 bg-green-50;
}

.version-item.current {
  @apply border-purple-500 bg-purple-50;
}

.version-info {
  @apply flex-1;
}

.version-meta {
  @apply flex items-center gap-3 mb-1;
}

.version-number {
  @apply px-2 py-1 bg-gray-100 text-gray-800 rounded text-sm font-medium;
}

.version-date {
  @apply text-sm text-gray-500;
}

.version-comment {
  @apply text-sm text-gray-700 mb-1;
}

.version-author {
  @apply text-xs text-gray-500;
}

.version-actions {
  @apply flex items-center gap-2;
}

.active-tag {
  @apply px-2 py-1 bg-green-100 text-green-800 rounded text-xs font-medium;
}

.compare-controls {
  @apply flex items-center gap-3;
}

.version-select {
  @apply border border-gray-300 rounded px-3 py-2 text-sm min-w-48;
}

.compare-vs {
  @apply text-gray-500 font-medium;
}

.modal-overlay {
  @apply fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50;
}

.modal-content {
  @apply bg-white rounded-lg shadow-xl max-w-md w-full mx-4;
}

.modal-header {
  @apply flex items-center justify-between p-4 border-b;
}

.modal-header h3 {
  @apply text-lg font-semibold;
}

.close-btn {
  @apply text-gray-400 hover:text-gray-600 text-xl;
}

.modal-body {
  @apply p-4 space-y-4;
}

.form-group label {
  @apply block text-sm font-medium text-gray-700 mb-1;
}

.form-control {
  @apply w-full border border-gray-300 rounded px-3 py-2 text-sm;
}

.version-preview {
  @apply border-t pt-4;
}

.preview-title {
  @apply text-sm font-medium text-gray-700 mb-2;
}

.data-list {
  @apply text-sm text-gray-600 space-y-1;
}

.modal-footer {
  @apply flex items-center justify-end gap-3 p-4 border-t;
}

.loading-overlay {
  @apply fixed inset-0 bg-white bg-opacity-75 flex flex-col items-center justify-center z-40;
}

.loading-overlay p {
  @apply mt-4 text-gray-600;
}
</style>
