<template>
  <v-container
    fluid
    class="grants-container px-6 pb-0 pt-0"
    style="background-color: white"
  >
    <!-- 標題與功能按鈕區 -->
    <v-row justify="center">
      <v-col
        cols="10"
        lg="10"
        align-self="center"
        class="pt-0"
      >
        <!-- 功能按鈕區 -->
        <div class="d-flex flex-wrap align-center pr-2">
          <v-spacer />
          <div class="d-flex gap-2">
            <!-- 批次啟用按鈕 -->
            <v-btn
              v-if="activeTab === 'existing'"
              class="action-btn mr-2"
              color="#3ea0a3"
              prepend-icon="mdi-account-check"
              variant="outlined"
              rounded="lg"
              size="large"
              :disabled="!hasSelection"
              :loading="batchProcessing"
              @click="handleBatchActivate"
            >
              批次啟用 {{ selectedCountText }}
            </v-btn>

            <!-- 批次停用按鈕 -->
            <v-btn
              v-if="activeTab === 'existing'"
              class="action-btn mr-2"
              color="warning"
              prepend-icon="mdi-account-off"
              variant="outlined"
              rounded="lg"
              size="large"
              :disabled="!hasSelection"
              :loading="batchProcessing"
              @click="handleBatchDeactivate"
            >
              批次停用 {{ selectedCountText }}
            </v-btn>

            <!-- 重新整理按鈕 -->
            <v-btn
              class="action-btn"
              color="primary"
              prepend-icon="mdi-refresh"
              variant="outlined"
              rounded="lg"
              size="large"
              :loading="store.isLoading"
              @click="handleRefresh"
            >
              重新整理
            </v-btn>
          </div>
        </div>

        <div class="section-wrapper">
          <v-card
            class="mx-auto section-card pa-4"
            variant="outlined"
            rounded="lg"
          >
            <v-card-item class="custom-title">
              <v-card-title class="text-h5 font-weight-black">
                使用者帳號列表
              </v-card-title>
            </v-card-item>

            <v-card-text>
              <!-- 錯誤訊息 -->
              <v-alert
                v-if="store.hasError"
                type="error"
                variant="outlined"
                class="mb-4"
                closable
                @click:close="store.clearError()"
              >
                {{ store.error }}
              </v-alert>

              <!-- 分頁 Tabs -->
              <v-tabs
                v-model="activeTab"
                color="primary"
                class="mb-4"
              >
                <v-tab value="existing">已有帳號</v-tab>
                <v-tab value="pending">
                  待審核帳號
                  <v-badge
                    v-if="totalPendingUsers > 0"
                    :content="totalPendingUsers"
                    color="error"
                    class="ml-2"
                    inline
                  />
                </v-tab>
              </v-tabs>

              <v-window v-model="activeTab">
                <v-window-item value="existing">
                  <!-- 篩選卡片 -->
                  <v-card
                    class="table-card mb-4"
                    rounded="lg"
                    elevation="0"
                  >
                    <div
                      class="d-flex flex-wrap align-center gap-3 pa-4"
                      style="background-color: #e3f4f4;"
                    >
                      <v-icon
                        icon="mdi-filter-variant"
                        color="#3ea0a3"
                        class="me-2"
                      />
                      <span class="text-subtitle-1 font-weight-medium">篩選條件</span>
                      <v-spacer />

                      <!-- 篩選區域 -->
                      <div class="d-flex flex-wrap">
                        <!-- 搜尋框 -->
                        <v-text-field
                          v-model="filters.search"
                          label="搜尋（帳號/姓名/Email）"
                          prepend-inner-icon="mdi-magnify"
                          density="comfortable"
                          variant="outlined"
                          hide-details
                          clearable
                          class="mr-2"
                          style="min-width: 250px;"
                          rounded="lg"
                          @update:model-value="handleSearchChange"
                        />

                        <!-- 角色篩選 -->
                        <v-select
                          v-model="filters.role"
                          :items="roleOptions"
                          item-title="title"
                          item-value="value"
                          label="角色"
                          density="comfortable"
                          variant="outlined"
                          hide-details
                          clearable
                          class="mr-2"
                          style="min-width: 150px;"
                          rounded="lg"
                          @update:model-value="handleFilterChange"
                        />

                        <!-- 單位篩選（僅 admin 可跨管理處查詢） -->
                        <v-select
                          v-if="!isManager"
                          v-model="filters.office_id"
                          :items="officeOptions"
                          item-title="title"
                          item-value="value"
                          label="單位"
                          density="comfortable"
                          variant="outlined"
                          hide-details
                          clearable
                          class="mr-2"
                          style="min-width: 150px;"
                          rounded="lg"
                          @update:model-value="handleFilterChange"
                        />

                        <!-- 狀態篩選 -->
                        <v-select
                          v-model="filters.is_active"
                          :items="statusOptions"
                          item-title="label"
                          item-value="value"
                          label="狀態"
                          density="comfortable"
                          variant="outlined"
                          hide-details
                          clearable
                          style="min-width: 120px;"
                          rounded="lg"
                          @update:model-value="handleFilterChange"
                        />

                        <!-- 清除篩選按鈕 -->
                        <v-btn
                          v-if="hasActiveFilters"
                          color="error"
                          variant="text"
                          size="small"
                          @click="clearFilters"
                        >
                          清除篩選
                        </v-btn>
                      </div>
                    </div>
                  </v-card>

                  <!-- 資料表格 -->
                  <v-data-table-server
                    v-model="selectedUsers"
                    :headers="headers"
                    :items="users"
                    :items-length="totalUsers"
                    :loading="store.isLoading"
                    :items-per-page="itemsPerPage"
                    :page="currentPage"
                    class="elevation-0"
                    item-value="id"
                    show-select
                    @update:items-per-page="handleItemsPerPageChange"
                    @update:page="handlePageChange"
                  >
                    <!-- 帳號欄位 -->
                    <template #item.username="{ item }">
                      <div class="d-flex align-center">
                        <v-icon
                          :icon="item.is_active ? 'mdi-account' : 'mdi-account-off'"
                          :color="item.is_active ? 'success' : 'grey'"
                          size="small"
                          class="mr-2"
                        />
                        <span class="font-weight-medium">{{ item.username }}</span>
                      </div>
                    </template>

                    <!-- 姓名欄位 -->
                    <template #item.full_name="{ item }">
                      {{ item.full_name || '-' }}
                    </template>

                    <!-- Email 欄位 -->
                    <template #item.email="{ item }">
                      {{ item.email || '-' }}
                    </template>

                    <!-- 角色欄位 -->
                    <template #item.role="{ item }">
                      <v-chip
                        :color="getRoleColor(item.role)"
                        size="small"
                        variant="flat"
                      >
                        {{ item.role || '一般使用者' }}
                      </v-chip>
                    </template>

                    <!-- 管理處欄位 -->
                    <template #item.office="{ item }">
                      {{ item.office?.name || '-' }}
                    </template>

                    <!-- 狀態欄位 -->
                    <template #item.is_active="{ item }">
                      <v-chip
                        :color="item.is_active ? 'success' : 'error'"
                        size="small"
                        variant="flat"
                      >
                        {{ item.is_active ? '啟用' : '停用' }}
                      </v-chip>
                    </template>

                    <!-- 最後登入欄位 -->
                    <template #item.last_login="{ item }">
                      <span class="text-caption">
                        {{ formatDate(item.last_login) }}
                      </span>
                    </template>

                    <!-- 操作欄位 -->
                    <template #item.actions="{ item }">
                      <div class="d-flex gap-1">
                        <v-btn
                          v-if="canEditUsers && !(isManager && item.role === 'admin')"
                          icon="mdi-account-group"
                          size="x-small"
                          variant="text"
                          color="teal"
                          @click="handleEditGroup(item)"
                        >
                          <v-icon size="small">mdi-account-group</v-icon>
                          <v-tooltip
                            activator="parent"
                            location="top"
                          >
                            群組設定
                          </v-tooltip>
                        </v-btn>

                        <v-btn
                          v-if="canEditUsers && !(isManager && item.role === 'admin')"
                          :icon="item.is_active ? 'mdi-account-off' : 'mdi-account-check'"
                          size="x-small"
                          variant="text"
                          :color="item.is_active ? 'warning' : 'success'"
                          @click="handleToggleActive(item)"
                        >
                          <v-icon size="small">
                            {{ item.is_active ? 'mdi-account-off' : 'mdi-account-check' }}
                          </v-icon>
                          <v-tooltip
                            activator="parent"
                            location="top"
                          >
                            {{ item.is_active ? '停用' : '啟用' }}
                          </v-tooltip>
                        </v-btn>
                      </div>
                    </template>

                    <!-- 空狀態 -->
                    <template #no-data>
                      <div class="text-center pa-6">
                        <v-icon
                          icon="mdi-account-off-outline"
                          size="64"
                          color="grey-lighten-1"
                          class="mb-4"
                        />
                        <p class="text-h6 text-grey-darken-1">
                          無符合條件的使用者
                        </p>
                        <p class="text-caption text-grey">
                          請調整篩選條件或建立新使用者
                        </p>
                      </div>
                    </template>
                  </v-data-table-server>

                  <!-- 統計資訊 -->
                  <div class="d-flex justify-space-between align-center mt-4 text-caption text-grey">
                    <div>
                      已選取 {{ selectedUsers.length }} 位使用者
                    </div>
                    <div>
                      共 {{ totalUsers }} 位使用者
                    </div>
                  </div>
                </v-window-item>

                <!-- 待審核帳號分頁 -->
                <v-window-item value="pending">
                  <v-data-table
                    :headers="pendingHeaders"
                    :items="pendingUsers"
                    :loading="store.isLoading"
                    class="elevation-0"
                    no-data-text="目前無待審核帳號申請"
                  >
                    <template #item.office_name="{ item }">
                      {{ item.office_name || '-' }}
                    </template>

                    <template #item.application_reason="{ item }">
                      <div
                        class="text-caption"
                        style="max-width: 200px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;"
                        :title="item.application_reason"
                      >
                        {{ item.application_reason || '-' }}
                      </div>
                    </template>

                    <template #item.applied_at="{ item }">
                      <span class="text-caption">{{ formatDate(item.applied_at) }}</span>
                    </template>

                    <template #item.actions="{ item }">
                      <div class="d-flex gap-1">
                        <v-btn
                          color="success"
                          size="small"
                          variant="flat"
                          @click="openApproveDialog(item)"
                        >
                          核准
                        </v-btn>
                        <v-btn
                          color="error"
                          size="small"
                          variant="outlined"
                          @click="openRejectDialog(item)"
                        >
                          駁回
                        </v-btn>
                      </div>
                    </template>
                  </v-data-table>
                </v-window-item>
              </v-window>
            </v-card-text>
          </v-card>
        </div>
      </v-col>
    </v-row>

    <!-- Snackbar 通知 -->
    <v-snackbar
      v-model="snackbar.show"
      :color="snackbar.color"
      :timeout="3000"
      location="top"
    >
      {{ snackbar.message }}
      <template #actions>
        <v-btn
          variant="text"
          @click="snackbar.show = false"
        >
          關閉
        </v-btn>
      </template>
    </v-snackbar>
    <!-- 核准確認 Dialog -->
    <v-dialog
      v-model="showApproveDialog"
      max-width="420"
      persistent
    >
      <v-card>
        <v-card-title class="text-h6 pt-5 px-6">
          確認核准帳號
        </v-card-title>
        <v-card-text class="px-6">
          確定要核准帳號 <strong>{{ pendingUserForApproval?.username }}</strong>（{{ pendingUserForApproval?.full_name }}）的申請？
          核准後系統將自動寄送通知信至 {{ pendingUserForApproval?.email }}。
        </v-card-text>
        <v-card-actions class="px-6 pb-5">
          <v-spacer />
          <v-btn
            variant="text"
            :disabled="isApproving"
            @click="showApproveDialog = false"
          >
            取消
          </v-btn>
          <v-btn
            color="success"
            variant="flat"
            :loading="isApproving"
            @click="confirmApprove"
          >
            確認核准
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- 駁回原因 Dialog -->
    <v-dialog
      v-model="showRejectDialog"
      max-width="480"
      persistent
    >
      <v-card>
        <v-card-title class="text-h6 pt-5 px-6">
          駁回帳號申請
        </v-card-title>
        <v-card-text class="px-6">
          <p class="mb-4">
            請填寫駁回帳號 <strong>{{ pendingUserForRejection?.username }}</strong>（{{ pendingUserForRejection?.full_name }}）申請的原因。
          </p>
          <v-textarea
            v-model="rejectReason"
            label="駁回原因"
            :error-messages="rejectReasonError"
            variant="outlined"
            rows="3"
            counter="500"
            maxlength="500"
            auto-grow
            @update:model-value="rejectReasonError = ''"
          />
        </v-card-text>
        <v-card-actions class="px-6 pb-5">
          <v-spacer />
          <v-btn
            variant="text"
            :disabled="isRejecting"
            @click="showRejectDialog = false"
          >
            取消
          </v-btn>
          <v-btn
            color="error"
            variant="flat"
            :loading="isRejecting"
            @click="confirmReject"
          >
            確認駁回
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
    <!-- 群組設定 Dialog -->
    <v-dialog
      v-model="showGroupDialog"
      max-width="420"
      persistent
    >
      <v-card>
        <v-card-title class="text-h6 pt-5 px-6">
          群組設定
        </v-card-title>
        <v-card-text class="px-6">
          <p class="mb-4 text-body-2">
            帳號：<strong>{{ selectedUserForGroup?.username }}</strong>（{{ selectedUserForGroup?.full_name }}）
          </p>
          <v-select
            v-model="newRole"
            :items="roleOptions"
            item-title="title"
            item-value="value"
            label="群組（角色）"
            variant="outlined"
            density="comfortable"
            hide-details
            rounded="lg"
          />
        </v-card-text>
        <v-card-actions class="px-6 pb-5">
          <v-spacer />
          <v-btn
            variant="text"
            :disabled="isUpdatingRole"
            @click="showGroupDialog = false"
          >
            取消
          </v-btn>
          <v-btn
            color="#3ea0a3"
            variant="flat"
            :loading="isUpdatingRole"
            :disabled="newRole === selectedUserForGroup?.role"
            @click="confirmRoleChange"
          >
            確認變更
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script lang="ts" setup>
import { ref, computed, onMounted } from 'vue'
import { useUserManagementStore } from '@/stores/userManagement'
import { useOfficesStore } from '@/stores/offices'
import { useUserStore } from '@/stores/users'
import type { UserListItem } from '@/types/userManagement'
import { DEFAULT_ROLES, getRoleColor } from '@/types/permissions'

interface PendingUser {
  user_id: number
  registration_id: number
  username: string
  full_name?: string
  email: string
  office_name?: string
  application_reason?: string
  applied_at?: string
}

// ============================================================================
// Stores
// ============================================================================

const store = useUserManagementStore()
const officesStore = useOfficesStore()
const userStore = useUserStore()

// ============================================================================
// State
// ============================================================================

const selectedUsers = ref<number[]>([])
const batchProcessing = ref(false)
const currentPage = ref(1)
const itemsPerPage = ref(20)

// 篩選條件
const filters = ref({
  search: '',
  role: null as string | null,
  office_id: null as number | null,
  is_active: null as boolean | null
})

// Snackbar
const snackbar = ref({
  show: false,
  message: '',
  color: 'success'
})

// 搜尋防抖
let searchTimeout: ReturnType<typeof setTimeout> | null = null

// 待審核分頁
const activeTab = ref<'existing' | 'pending'>('existing')

// 群組設定對話框
const showGroupDialog = ref(false)
const selectedUserForGroup = ref<UserListItem | null>(null)
const newRole = ref('')
const isUpdatingRole = ref(false)

// 核准對話框
const showApproveDialog = ref(false)
const pendingUserForApproval = ref<PendingUser | null>(null)
const isApproving = ref(false)

// 駁回對話框
const showRejectDialog = ref(false)
const pendingUserForRejection = ref<PendingUser | null>(null)
const rejectReason = ref('')
const rejectReasonError = ref('')
const isRejecting = ref(false)

// ============================================================================
// Computed
// ============================================================================

const users = computed(() => store.users?.users || [])
const totalUsers = computed(() => store.users?.total || 0)

const pendingUsers = computed(() => (store.pendingUsers?.users || []) as unknown as PendingUser[])
const totalPendingUsers = computed(() => store.pendingUsers?.total || 0)

const hasSelection = computed(() => selectedUsers.value.length > 0)

const selectedCountText = computed(() =>
  hasSelection.value ? `(${selectedUsers.value.length})` : ''
)

const hasActiveFilters = computed(() =>
  !!(filters.value.search || filters.value.role || filters.value.office_id || filters.value.is_active !== null)
)

// 角色選項（manager 不可將帳號提升為 admin）
const isManager = computed(() => userStore.currentUser?.role === 'manager')
const canEditUsers = computed(() => userStore.can('users', 'edit'))
const roleOptions = computed(() =>
  isManager.value ? DEFAULT_ROLES.filter(r => r.value !== 'admin') : [...DEFAULT_ROLES]
)

// 單位選項
const officeOptions = computed(() => (officesStore.managementOffices || []).filter(o => o.value > 0))

// 狀態選項
const statusOptions = [
  { label: '啟用', value: true },
  { label: '停用', value: false }
]

// ============================================================================
// Table Headers
// ============================================================================

const headers = [
  { title: '帳號', key: 'username', sortable: false },
  { title: '姓名', key: 'full_name', sortable: false },
  { title: 'Email', key: 'email', sortable: false },
  { title: '角色', key: 'role', sortable: false },
  { title: '管理處', key: 'office', sortable: false },
  { title: '狀態', key: 'is_active', sortable: false },
  { title: '最後登入', key: 'last_login', sortable: false },
  { title: '操作', key: 'actions', sortable: false, align: 'center' as const }
]

const pendingHeaders = [
  { title: '申請帳號', key: 'username', sortable: false },
  { title: '姓名', key: 'full_name', sortable: false },
  { title: 'Email', key: 'email', sortable: false },
  { title: '所屬管理處', key: 'office_name', sortable: false },
  { title: '申請原因', key: 'application_reason', sortable: false },
  { title: '申請時間', key: 'applied_at', sortable: false },
  { title: '操作', key: 'actions', sortable: false, align: 'center' as const }
]

// ============================================================================
// Methods
// ============================================================================

/**
 * 載入使用者列表
 */
async function loadUsers() {
  await store.fetchUsers({
    page: currentPage.value,
    page_size: itemsPerPage.value,
    search: filters.value.search || undefined,
    role: filters.value.role || undefined,
    office_id: filters.value.office_id || undefined,
    is_active: filters.value.is_active ?? undefined
  })
}

/**
 * 處理頁碼變更
 */
function handlePageChange(page: number) {
  currentPage.value = page
  loadUsers()
}

/**
 * 處理每頁筆數變更
 */
function handleItemsPerPageChange(perPage: number) {
  itemsPerPage.value = perPage
  currentPage.value = 1 // 重置到第一頁
  loadUsers()
}

/**
 * 處理搜尋變更（防抖）
 */
function handleSearchChange() {
  if (searchTimeout) {
    clearTimeout(searchTimeout)
  }

  searchTimeout = setTimeout(() => {
    currentPage.value = 1 // 搜尋時重置到第一頁
    loadUsers()
  }, 500) // 500ms 防抖
}

/**
 * 處理篩選變更
 */
function handleFilterChange() {
  currentPage.value = 1 // 篩選時重置到第一頁
  loadUsers()
}

/**
 * 清除篩選
 */
function clearFilters() {
  filters.value = {
    search: '',
    role: null,
    office_id: null,
    is_active: null
  }
  currentPage.value = 1
  loadUsers()
}

/**
 * 重新整理
 */
function handleRefresh() {
  selectedUsers.value = []
  loadUsers()
}

/**
 * 批次啟用
 */
async function handleBatchActivate() {
  if (!hasSelection.value) return

  batchProcessing.value = true
  try {
    const result = await store.batchActivateUsers(selectedUsers.value)
    if (result) {
      showSnackbar(`成功啟用 ${result.success} 位使用者`, 'success')
      selectedUsers.value = []
      await loadUsers()
    }
  } catch (error) {
    showSnackbar('批次啟用失敗', 'error')
  } finally {
    batchProcessing.value = false
  }
}

/**
 * 批次停用
 */
async function handleBatchDeactivate() {
  if (!hasSelection.value) return

  batchProcessing.value = true
  try {
    const result = await store.batchDeactivateUsers(selectedUsers.value)
    if (result) {
      showSnackbar(`成功停用 ${result.success} 位使用者`, 'success')
      selectedUsers.value = []
      await loadUsers()
    }
  } catch (error) {
    showSnackbar('批次停用失敗', 'error')
  } finally {
    batchProcessing.value = false
  }
}

/**
 * 開啟群組設定對話框
 */
function handleEditGroup(user: UserListItem) {
  selectedUserForGroup.value = user
  newRole.value = user.role || 'user'
  showGroupDialog.value = true
}

/**
 * 確認變更群組
 */
async function confirmRoleChange() {
  if (!selectedUserForGroup.value || !newRole.value) return
  isUpdatingRole.value = true
  try {
    await store.updateUserRole(selectedUserForGroup.value.id, newRole.value)
    const roleLabel = roleOptions.value.find(r => r.value === newRole.value)?.title ?? newRole.value
    showSnackbar(`已將 ${selectedUserForGroup.value.username} 的群組更改為「${roleLabel}」`, 'success')
    showGroupDialog.value = false
    await loadUsers()
  } catch {
    showSnackbar('群組設定失敗，請稍後再試', 'error')
  } finally {
    isUpdatingRole.value = false
  }
}

/**
 * 切換啟用狀態
 */
async function handleToggleActive(user: UserListItem) {
  const action = user.is_active ? '停用' : '啟用'

  try {
    if (user.is_active) {
      await store.batchDeactivateUsers([user.id])
    } else {
      await store.batchActivateUsers([user.id])
    }
    showSnackbar(`${action}成功`, 'success')
    await loadUsers()
  } catch (error) {
    showSnackbar(`${action}失敗`, 'error')
  }
}

/**
 * 載入待審核帳號列表
 */
async function loadPendingUsers() {
  await store.fetchPendingApprovalUsers(1)
}

/**
 * 開啟核准確認 Dialog
 */
function openApproveDialog(user: PendingUser) {
  pendingUserForApproval.value = user
  showApproveDialog.value = true
}

/**
 * 確認核准
 */
async function confirmApprove() {
  if (!pendingUserForApproval.value) return
  isApproving.value = true
  try {
    await store.approveUser(pendingUserForApproval.value.user_id)
    showSnackbar(`帳號 ${pendingUserForApproval.value.username} 已核准`, 'success')
    showApproveDialog.value = false
    await loadPendingUsers()
  } catch (error: any) {
    showSnackbar(error?.response?.data?.detail || '核准失敗，請稍後再試', 'error')
  } finally {
    isApproving.value = false
  }
}

/**
 * 開啟駁回原因 Dialog
 */
function openRejectDialog(user: PendingUser) {
  pendingUserForRejection.value = user
  rejectReason.value = ''
  rejectReasonError.value = ''
  showRejectDialog.value = true
}

/**
 * 確認駁回
 */
async function confirmReject() {
  if (!pendingUserForRejection.value) return
  if (!rejectReason.value.trim()) {
    rejectReasonError.value = '請輸入駁回原因'
    return
  }
  isRejecting.value = true
  try {
    await store.rejectUser(pendingUserForRejection.value.user_id, rejectReason.value.trim())
    showSnackbar(`帳號 ${pendingUserForRejection.value.username} 申請已駁回`, 'warning')
    showRejectDialog.value = false
    await loadPendingUsers()
  } catch (error: any) {
    showSnackbar(error?.response?.data?.detail || '駁回失敗，請稍後再試', 'error')
  } finally {
    isRejecting.value = false
  }
}


/**
 * 格式化日期
 */
function formatDate(dateString?: string): string {
  if (!dateString) return '-'

  try {
    const date = new Date(dateString)
    return date.toLocaleDateString('zh-TW', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    })
  } catch {
    return '-'
  }
}

/**
 * 顯示 Snackbar
 */
function showSnackbar(message: string, color: string = 'success') {
  snackbar.value = {
    show: true,
    message,
    color
  }
}

// ============================================================================
// Lifecycle
// ============================================================================

onMounted(async () => {
  // 載入管理處列表
  await officesStore.fetchOffices()

  // 並行載入：使用者列表 + 待審核帳號
  await Promise.all([loadUsers(), loadPendingUsers()])
})
</script>

<style scoped>
/* 添加背景圖片樣式 */
.grants-container {
  background-image: url('@/assets/bg_index.svg');
  background-size: cover;
  background-position: center bottom;
  background-repeat: no-repeat;
  background-attachment: fixed;
  /* min-height: 100vh; */
}
/*
.grants-container {
  min-height: 100vh;
} */

.section-wrapper {
  /* padding-top: 20px; */
  padding: 8px 4px 0px 4px;
}

/* 卡片與標題樣式 */
.section-card {
  position: relative;
  margin: 24px 0;
  overflow: visible !important;
  border-top-left-radius: 0 !important;
  transition: all 0.3s ease;

  /* 毛玻璃效果 */
  background-color: rgba(255, 255, 255, 0.6) !important; /* 半透明白色背景 */
  backdrop-filter: blur(10px) !important; /* 背景模糊效果 */
  -webkit-backdrop-filter: blur(10px) !important; /* Safari 支持 */
  border: 1px solid rgba(255, 255, 255, 0.25) !important; /* 細微邊框增強玻璃感 */
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.05) !important; /* 柔和陰影增強玻璃感 */
}

/* .section-card {
  border: 2px solid #e3f4f4;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
} */

.section-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08) !important;
  background-color: rgba(255, 255, 255, 0.85) !important; /* 懸停時略微增加不透明度 */
}

.section-card:hover .custom-title {
  background-color: #2d8c8f !important;
  box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.08);
}

.custom-title {
  position: absolute;
  top: -50px;
  left: -1px;
  width: auto !important;
  min-width: 130px;
  height: 50px;
  /* padding: 0 16px !important; */
  background-color: #3ea0a3 !important;
  border-radius: 8px 8px 0 0;
  z-index: 1;
  transition: all 0.3s ease;
}

/* .custom-title {
  background: linear-gradient(135deg, #3ea0a3 0%, #2d7a7c 100%);
  color: white;
  border-radius: 8px 8px 0 0;
  margin: -16px -16px 16px -16px;
} */

.v-card-title {
  color: white !important;
  display: flex;
  justify-content: flex-start;
  align-items: center;
  width: 100%;
  height: 100%;
  /* padding-left: 16px; */
}

/* 表格區域樣式 */
.table-card {
  border-radius: 12px;
  overflow: hidden;
}



.action-btn {
  font-weight: 600;
  text-transform: none;
  letter-spacing: 0.5px;
}

.filter-select {
  background-color: white;
}

.table-card {
  border: 1px solid #e3f4f4;
}
</style>
