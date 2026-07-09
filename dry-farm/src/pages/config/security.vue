<template>
  <v-container
    fluid
    class="grants-container px-6 pb-0 pt-0"
    style="background-color: white"
  >
    <v-row justify="center">
      <v-col
        cols="10"
        lg="10"
        align-self="center"
        class="pt-0"
      >
        <div class="d-flex flex-wrap align-center pr-2">
          <v-spacer />
          <div class="d-flex gap-2">
            <v-btn
              class="action-btn mr-2"
              color="primary"
              prepend-icon="mdi-plus"
              variant="outlined"
              rounded="lg"
              size="large"
              @click="openCreateDialog"
            >
              新增網段
            </v-btn>
            <v-btn
              class="action-btn"
              color="primary"
              prepend-icon="mdi-refresh"
              variant="outlined"
              rounded="lg"
              size="large"
              :loading="isLoading"
              @click="fetchEntries"
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
                IP 白名單網段列表
              </v-card-title>
            </v-card-item>

            <v-card-text>
              <v-alert
                v-if="errorMessage"
                type="error"
                variant="outlined"
                class="mb-4"
                closable
                @click:close="errorMessage = ''"
              >
                {{ errorMessage }}
              </v-alert>

              <v-data-table
                :headers="headers"
                :items="entries"
                :loading="isLoading"
                item-value="id"
              >
                <template #item.is_active="{ item }">
                  <v-chip
                    :color="item.is_archived ? 'default' : (item.is_active ? 'success' : 'default')"
                    size="small"
                    variant="flat"
                  >
                    {{ item.is_archived ? '已封存' : (item.is_active ? '啟用中' : '已停用') }}
                  </v-chip>
                </template>

                <template #item.created_at="{ item }">
                  {{ formatDateTime(item.created_at) }}
                </template>

                <template #item.actions="{ item }">
                  <div
                    v-if="item.is_archived"
                    class="d-flex align-center"
                  >
                    <v-btn
                      variant="text"
                      size="small"
                      color="primary"
                      :loading="archivingId === item.id"
                      @click="unarchiveEntry(item)"
                    >
                      取消封存
                    </v-btn>
                  </div>
                  <div
                    v-else
                    class="d-flex align-center gap-2"
                  >
                    <v-switch
                      :model-value="item.is_active"
                      color="primary"
                      density="compact"
                      hide-details
                      :loading="togglingId === item.id"
                      @update:model-value="(val: boolean | null) => { toggleActive(item, !!val) }"
                    />
                    <v-tooltip :text="item.is_active ? '請先停用才能封存' : '封存（封存後移出列表，但保留歷史紀錄）'">
                      <template #activator="{ props: tooltipProps }">
                        <v-btn
                          v-bind="tooltipProps"
                          icon="mdi-archive-outline"
                          variant="text"
                          size="small"
                          :disabled="item.is_active"
                          :loading="archivingId === item.id"
                          @click="archiveEntry(item)"
                        />
                      </template>
                    </v-tooltip>
                  </div>
                </template>
              </v-data-table>
            </v-card-text>
          </v-card>
        </div>
      </v-col>
    </v-row>

    <!-- 新增網段對話框 -->
    <v-dialog
      v-model="createDialog"
      max-width="480"
    >
      <v-card>
        <v-card-title>新增 IP 白名單網段</v-card-title>
        <v-card-text>
          <v-text-field
            v-model="createForm.cidr"
            label="CIDR 網段"
            placeholder="例如：192.168.1.0/24"
            variant="outlined"
            density="comfortable"
            hint="僅支援 IPv4 CIDR 格式"
            persistent-hint
            class="mb-2"
          />
          <v-text-field
            v-model="createForm.name"
            label="說明名稱"
            placeholder="例如：台中管理處辦公室"
            variant="outlined"
            density="comfortable"
          />
          <v-alert
            v-if="createError"
            type="error"
            variant="tonal"
            density="compact"
            class="mt-2"
          >
            {{ createError }}
          </v-alert>
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn
            variant="text"
            @click="createDialog = false"
          >
            取消
          </v-btn>
          <v-btn
            color="primary"
            :loading="isCreating"
            @click="submitCreate"
          >
            新增
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script lang="ts" setup>
import { apiService } from '@/services/api/http'
import { SECURITY } from '@/services/api/endpoints'

interface IPWhitelistEntry {
  id: number
  cidr: string
  name: string
  is_active: boolean
  is_archived: boolean
  created_by: string | null
  created_at: string
}

const entries = ref<IPWhitelistEntry[]>([])
const isLoading = ref(false)
const errorMessage = ref('')
const togglingId = ref<number | null>(null)
const archivingId = ref<number | null>(null)
const showArchived = ref(false)

const createDialog = ref(false)
const isCreating = ref(false)
const createError = ref('')
const createForm = ref({ cidr: '', name: '' })

const headers = [
  { title: 'CIDR 網段', key: 'cidr' },
  { title: '說明名稱', key: 'name' },
  { title: '狀態', key: 'is_active' },
  { title: '建立者', key: 'created_by' },
  { title: '建立時間', key: 'created_at' },
  { title: '操作', key: 'actions', sortable: false },
]

function formatDateTime(iso: string): string {
  return new Date(iso).toLocaleString('zh-TW', { hour12: false })
}

function extractErrorMessage(error: any, fallback: string): string {
  const detail = error?.response?.data?.detail
  if (typeof detail === 'string') return detail
  if (detail?.message) return detail.message
  return error?.message || fallback
}

async function fetchEntries() {
  isLoading.value = true
  errorMessage.value = ''
  try {
    entries.value = await apiService.get<IPWhitelistEntry[]>(SECURITY.IP_WHITELIST_LIST, {
      params: { include_archived: showArchived.value },
    })
  } catch (error: any) {
    errorMessage.value = extractErrorMessage(error, '載入白名單清單失敗')
  } finally {
    isLoading.value = false
  }
}

function openCreateDialog() {
  createForm.value = { cidr: '', name: '' }
  createError.value = ''
  createDialog.value = true
}

async function submitCreate() {
  isCreating.value = true
  createError.value = ''
  try {
    const created = await apiService.post<IPWhitelistEntry>(SECURITY.IP_WHITELIST_CREATE, {
      cidr: createForm.value.cidr,
      name: createForm.value.name,
    })
    entries.value = [created, ...entries.value]
    createDialog.value = false
  } catch (error: any) {
    createError.value = extractErrorMessage(error, '新增網段失敗')
  } finally {
    isCreating.value = false
  }
}

async function toggleActive(item: IPWhitelistEntry, nextValue: boolean) {
  togglingId.value = item.id
  errorMessage.value = ''
  try {
    const updated = await apiService.patch<IPWhitelistEntry>(SECURITY.IP_WHITELIST_UPDATE(item.id), {
      is_active: nextValue,
    })
    const index = entries.value.findIndex(e => e.id === item.id)
    if (index !== -1) {
      entries.value[index] = updated
    }
  } catch (error: any) {
    errorMessage.value = extractErrorMessage(error, '更新網段狀態失敗')
  } finally {
    togglingId.value = null
  }
}

async function archiveEntry(item: IPWhitelistEntry) {
  if (!window.confirm(`確定要封存「${item.name}」（${item.cidr}）嗎？\n封存後，網段規則會從列表中移除，但紀錄不會被刪除。`)) {
    return
  }
  archivingId.value = item.id
  errorMessage.value = ''
  try {
    await apiService.patch<IPWhitelistEntry>(SECURITY.IP_WHITELIST_UPDATE(item.id), { is_archived: true })
    await fetchEntries()
  } catch (error: any) {
    errorMessage.value = extractErrorMessage(error, '封存網段失敗')
  } finally {
    archivingId.value = null
  }
}

async function unarchiveEntry(item: IPWhitelistEntry) {
  archivingId.value = item.id
  errorMessage.value = ''
  try {
    await apiService.patch<IPWhitelistEntry>(SECURITY.IP_WHITELIST_UPDATE(item.id), { is_archived: false })
    await fetchEntries()
  } catch (error: any) {
    errorMessage.value = extractErrorMessage(error, '取消封存失敗')
  } finally {
    archivingId.value = null
  }
}

onMounted(() => {
  fetchEntries()
})
</script>

<style scoped>
.section-wrapper {
  margin-top: 16px;
}
</style>
