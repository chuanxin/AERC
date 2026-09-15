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
        <!-- 動作列 -->
        <div class="d-flex flex-wrap align-center pr-2">
          <v-spacer />
          <div class="d-flex gap-2">
            <v-btn
              class="action-btn mr-2"
              color="primary"
              prepend-icon="mdi-tag-multiple"
              variant="outlined"
              rounded="lg"
              size="large"
              @click="typeDialog = true"
            >
              類型維護
            </v-btn>
            <v-btn
              class="action-btn mr-2"
              color="primary"
              prepend-icon="mdi-plus"
              variant="outlined"
              rounded="lg"
              size="large"
              @click="openCreate"
            >
              新增公告
            </v-btn>
            <v-btn
              class="action-btn"
              color="primary"
              prepend-icon="mdi-refresh"
              variant="outlined"
              rounded="lg"
              size="large"
              :loading="store.loading"
              @click="reload"
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
                公告管理
              </v-card-title>
            </v-card-item>

            <v-card-text>
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

              <!-- 篩選 -->
              <v-row dense class="mb-2">
                <v-col cols="12" md="4">
                  <v-text-field
                    v-model="filters.keyword"
                    label="標題關鍵字"
                    density="comfortable"
                    variant="outlined"
                    clearable
                    prepend-inner-icon="mdi-magnify"
                    hide-details
                    @update:model-value="debouncedReload"
                  />
                </v-col>
                <v-col cols="6" md="4">
                  <v-select
                    v-model="filters.status"
                    :items="statusOptions"
                    label="狀態"
                    density="comfortable"
                    variant="outlined"
                    clearable
                    hide-details
                    @update:model-value="reload"
                  />
                </v-col>
                <v-col cols="6" md="4">
                  <v-select
                    v-model="filters.type_id"
                    :items="store.types"
                    item-title="name"
                    item-value="id"
                    label="類型"
                    density="comfortable"
                    variant="outlined"
                    clearable
                    hide-details
                    @update:model-value="reload"
                  />
                </v-col>
              </v-row>

              <v-data-table-server
                :headers="headers"
                :items="store.manageItems"
                :items-length="store.manageTotal"
                :loading="store.loading"
                :page="page"
                :items-per-page="pageSize"
                item-value="id"
                @update:options="onTableOptions"
              >
                <template #item.publish_date="{ item }">
                  {{ toRocDate(item.publish_date) }}
                </template>
                <template #item.type="{ item }">
                  <v-chip :color="item.type.color" variant="outlined" size="small" label>
                    {{ item.type.name }}
                  </v-chip>
                </template>
                <template #item.status="{ item }">
                  <v-chip :color="statusColor(item.status)" variant="flat" size="small" label>
                    {{ statusLabel(item.status) }}
                  </v-chip>
                </template>
                <template #item.is_pinned="{ item }">
                  <v-icon v-if="item.is_pinned" color="amber-darken-2">
                    mdi-pin
                  </v-icon>
                  <span v-else class="text-grey">—</span>
                </template>
                <template #item.actions="{ item }">
                  <v-btn
                    v-if="item.status !== 'published'"
                    variant="text"
                    size="small"
                    color="success"
                    @click="askPublish(item)"
                  >
                    發布
                  </v-btn>
                  <v-btn
                    v-else
                    variant="text"
                    size="small"
                    color="warning"
                    @click="doUnpublish(item)"
                  >
                    下架
                  </v-btn>
                  <v-btn variant="text" size="small" @click="openEdit(item)">
                    編輯
                  </v-btn>
                  <v-btn variant="text" size="small" color="error" @click="askDelete(item)">
                    刪除
                  </v-btn>
                </template>
                <template #no-data>
                  <div class="py-8 text-center text-grey">
                    目前沒有公告
                  </div>
                </template>
              </v-data-table-server>
            </v-card-text>
          </v-card>
        </div>
      </v-col>
    </v-row>

    <!-- ── 新增／編輯 ─────────────────────────────────────────────── -->
    <v-dialog v-model="formDialog" max-width="1100" persistent scrollable>
      <v-card rounded="lg">
        <v-card-title class="text-h6 font-weight-black">
          {{ editingId ? '編輯公告' : '新增公告' }}
        </v-card-title>
        <v-divider />
        <v-card-text>
          <v-form ref="formRef">
            <v-row dense>
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="form.title"
                  label="標題 *"
                  variant="outlined"
                  density="comfortable"
                  counter="200"
                  :rules="titleRules"
                />
              </v-col>
              <v-col cols="12" md="3">
                <v-select
                  v-model="form.type_id"
                  :items="store.types"
                  item-title="name"
                  item-value="id"
                  label="類型 *"
                  variant="outlined"
                  density="comfortable"
                  :rules="typeRules"
                />
              </v-col>
              <v-col cols="12" md="3">
                <v-text-field
                  v-model="form.publish_date"
                  label="發布日期"
                  type="date"
                  variant="outlined"
                  density="comfortable"
                  :hint="form.publish_date ? `民國 ${toRocDate(form.publish_date)}` : '留空則為今天'"
                  persistent-hint
                />
              </v-col>
            </v-row>

            <v-switch
              v-model="form.is_pinned"
              label="置頂（優先顯示於首頁與列表頁最前）"
              color="amber-darken-2"
              density="compact"
              hide-details
              class="mb-2"
            />

            <v-row dense>
              <v-col cols="12" md="6">
                <!-- 工具列緊貼其作用對象（下方輸入框），並與右欄「預覽」標題同高對齊 -->
                <div class="d-flex align-center flex-wrap mb-1 editor-toolbar">
                  <span class="text-caption text-grey-darken-1 me-auto">詳細內容</span>
                  <div class="d-flex flex-wrap">
                    <v-btn size="small" variant="text" prepend-icon="mdi-format-bold" @click="wrapSelection('**', '**')">
                      粗體
                    </v-btn>
                    <v-btn size="small" variant="text" prepend-icon="mdi-format-list-bulleted" @click="insertAtCursor('\n- 項目一\n- 項目二\n')">
                      清單
                    </v-btn>
                    <v-btn size="small" variant="text" prepend-icon="mdi-link" @click="insertAtCursor('[連結文字](https://)')">
                      連結
                    </v-btn>
                    <v-btn size="small" variant="tonal" color="primary" prepend-icon="mdi-paperclip" @click="attachDialog = true">
                      插入下載附件
                    </v-btn>
                  </div>
                </div>
                <v-textarea
                  ref="contentRef"
                  v-model="form.content_markdown"
                  variant="outlined"
                  rows="16"
                  auto-grow
                  counter="50000"
                  :rules="contentRules"
                  placeholder="純文字直接打即可"
                  hint="**粗體**、- 清單、[文字](網址) 皆可直接輸入；附件請用上方按鈕插入"
                  persistent-hint
                />
              </v-col>
              <v-col cols="12" md="6">
                <div class="d-flex align-center mb-1 editor-toolbar">
                  <span class="text-caption text-grey-darken-1">預覽（存檔後的實際樣子）</span>
                </div>
                <v-sheet
                  border
                  rounded="lg"
                  class="pa-4 preview-pane"
                >
                  <div v-if="previewHtml" class="content-text" v-html="previewHtml" />
                  <div v-else class="text-grey">
                    （內容為空）
                  </div>
                </v-sheet>
                <v-alert
                  v-if="previewNotices.length"
                  type="warning"
                  variant="tonal"
                  density="comfortable"
                  class="mt-2"
                >
                  以下內容<strong>不會被保留</strong>，存檔後將以純文字呈現或被移除：
                  <div class="mt-1">
                    <v-chip
                      v-for="n in previewNotices"
                      :key="n"
                      size="small"
                      class="mr-1 mb-1"
                      color="warning"
                      variant="outlined"
                      label
                    >
                      {{ noticeLabel(n) }}
                    </v-chip>
                  </div>
                </v-alert>
              </v-col>
            </v-row>
          </v-form>
        </v-card-text>
        <v-divider />
        <v-card-actions>
          <v-spacer />
          <v-btn variant="text" @click="formDialog = false">
            取消
          </v-btn>
          <v-btn color="primary" variant="flat" :loading="saving" @click="save">
            儲存
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- ── 插入下載附件 ───────────────────────────────────────────── -->
    <v-dialog v-model="attachDialog" max-width="620">
      <v-card rounded="lg">
        <v-card-title class="text-h6 font-weight-black">
          插入下載附件
        </v-card-title>
        <v-divider />
        <v-card-text>
          <v-form ref="attachFormRef">
            <v-text-field
              v-model="attach.url"
              label="Google Drive 分享連結 *"
              variant="outlined"
              density="comfortable"
              placeholder="https://drive.google.com/file/d/檔案ID/view?usp=sharing"
              :rules="driveUrlRules"
            />
            <v-text-field
              v-model="attach.filename"
              label="檔案顯示名稱 *"
              variant="outlined"
              density="comfortable"
              placeholder="115年管灌設施補助宣導摺頁.pdf"
              :rules="[(v: string) => !!v?.trim() || '請輸入檔案名稱']"
            />
            <div class="text-caption text-grey-darken-1">
              縮圖網址由分享連結推導，僅接受
              <code>https://drive.google.com/file/d/檔案ID/…</code> 格式。
              其他形式請直接在內容中自行輸入 Markdown。
            </div>
          </v-form>
        </v-card-text>
        <v-divider />
        <v-card-actions>
          <v-spacer />
          <v-btn variant="text" @click="attachDialog = false">
            取消
          </v-btn>
          <v-btn color="primary" variant="flat" @click="insertAttachment">
            插入
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- ── 發布日期提醒 ───────────────────────────────────────────── -->
    <v-dialog v-model="publishDialog" max-width="560">
      <v-card rounded="lg">
        <v-card-title class="text-h6 font-weight-black">
          確認發布
        </v-card-title>
        <v-divider />
        <v-card-text>
          <p class="mb-2">
            即將發布：<strong>{{ pendingPublish?.title }}</strong>
          </p>
          <v-alert v-if="publishDateStale" type="info" variant="tonal" density="comfortable">
            這則公告的發布日期是 <strong>{{ toRocDate(pendingPublish?.publish_date) }}</strong>，
            早於今天。公告依發布日期排序，維持舊日期會讓它排在較後面、首頁可能看不到。
            <v-checkbox
              v-model="updateDateOnPublish"
              label="一併更新為今天"
              density="compact"
              hide-details
              class="mt-2"
            />
          </v-alert>
        </v-card-text>
        <v-divider />
        <v-card-actions>
          <v-spacer />
          <v-btn variant="text" @click="publishDialog = false">
            取消
          </v-btn>
          <v-btn color="success" variant="flat" :loading="saving" @click="doPublish">
            發布
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- ── 刪除二次確認 ───────────────────────────────────────────── -->
    <v-dialog v-model="deleteDialog" max-width="520">
      <v-card rounded="lg">
        <v-card-title class="text-h6 font-weight-black">
          刪除公告
        </v-card-title>
        <v-divider />
        <v-card-text>
          確定要刪除「<strong>{{ pendingDelete?.title }}</strong>」嗎？
          <div class="text-error mt-2">
            此操作無法復原。
          </div>
        </v-card-text>
        <v-divider />
        <v-card-actions>
          <v-spacer />
          <v-btn variant="text" @click="deleteDialog = false">
            取消
          </v-btn>
          <v-btn color="error" variant="flat" :loading="saving" @click="doDelete">
            確定刪除
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- ── 類型維護 ───────────────────────────────────────────────── -->
    <v-dialog v-model="typeDialog" max-width="720">
      <v-card rounded="lg">
        <v-card-title class="text-h6 font-weight-black">
          公告類型維護
        </v-card-title>
        <v-divider />
        <v-card-text>
          <v-alert
            v-if="typeError"
            type="error"
            variant="tonal"
            density="comfortable"
            class="mb-3"
            closable
            @click:close="typeError = ''"
          >
            {{ typeError }}
          </v-alert>
          <v-table density="comfortable">
            <thead>
              <tr>
                <th>名稱</th><th>顏色</th><th class="text-right">
                  操作
                </th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="t in store.types" :key="t.id">
                <td>
                  <v-chip :color="t.color" variant="outlined" size="small" label>
                    {{ t.name }}
                  </v-chip>
                </td>
                <td class="text-caption text-grey-darken-1">
                  {{ t.color }}
                </td>
                <td class="text-right">
                  <v-btn size="small" variant="text" @click="startEditType(t)">
                    編輯
                  </v-btn>
                  <v-btn size="small" variant="text" color="error" @click="doDeleteType(t)">
                    刪除
                  </v-btn>
                </td>
              </tr>
            </tbody>
          </v-table>

          <v-divider class="my-3" />
          <v-form ref="typeFormRef">
            <div class="d-flex gap-2 align-start">
              <v-text-field
                v-model="typeForm.name"
                label="名稱 *"
                variant="outlined"
                density="comfortable"
                counter="20"
                :rules="typeNameRules"
              />
              <v-text-field
                v-model="typeForm.color"
                label="顏色 *"
                variant="outlined"
                density="comfortable"
                counter="30"
                hint="Vuetify 色名（blue / deep-orange）或 hex"
                :rules="typeColorRules"
              />
              <v-btn color="primary" variant="flat" class="mt-2" :loading="saving" @click="saveType">
                {{ editingTypeId ? '更新' : '新增' }}
              </v-btn>
              <v-btn v-if="editingTypeId" variant="text" class="mt-2" @click="resetTypeForm">
                取消
              </v-btn>
            </div>
          </v-form>
        </v-card-text>
        <v-divider />
        <v-card-actions>
          <v-spacer />
          <v-btn variant="text" @click="typeDialog = false">
            關閉
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-snackbar v-model="snackbar" :color="snackbarColor" :timeout="4000">
      {{ snackbarText }}
    </v-snackbar>
  </v-container>
</template>

<script lang="ts" setup>
import { computed, nextTick, onMounted, ref, watch } from 'vue'

import { useAnnouncementsStore } from '@/stores/announcements'
import { toRocDate } from '@/utils/rocDate'
import type {
  AnnouncementManageListItem,
  AnnouncementStatus,
  AnnouncementType,
} from '@/types/announcements'

const store = useAnnouncementsStore()

// ── 列表 ──────────────────────────────────────────────────────────────
const page = ref(1)
const pageSize = ref(20)
const filters = ref<{ keyword: string | null, status: AnnouncementStatus | null, type_id: number | null }>({
  keyword: null, status: null, type_id: null,
})

const headers = [
  { title: '發布日期', key: 'publish_date', sortable: false, width: 120 },
  { title: '類型', key: 'type', sortable: false, width: 120 },
  { title: '標題', key: 'title', sortable: false },
  { title: '狀態', key: 'status', sortable: false, width: 100 },
  { title: '置頂', key: 'is_pinned', sortable: false, width: 70, align: 'center' as const },
  { title: '建立者', key: 'created_by_username', sortable: false, width: 110 },
  { title: '操作', key: 'actions', sortable: false, width: 210, align: 'end' as const },
]

const statusOptions = [
  { title: '草稿', value: 'draft' },
  { title: '已發布', value: 'published' },
  { title: '已下架', value: 'archived' },
]

function statusLabel (s: AnnouncementStatus) {
  return { draft: '草稿', published: '已發布', archived: '已下架' }[s] ?? s
}
function statusColor (s: AnnouncementStatus) {
  return { draft: 'grey', published: 'success', archived: 'error' }[s] ?? 'grey'
}

async function reload () {
  await store.fetchManageList({
    page: page.value,
    page_size: pageSize.value,
    keyword: filters.value.keyword || undefined,
    status: filters.value.status || undefined,
    type_id: filters.value.type_id || undefined,
  })
}

let keywordTimer: ReturnType<typeof setTimeout> | null = null
function debouncedReload () {
  if (keywordTimer) clearTimeout(keywordTimer)
  keywordTimer = setTimeout(() => { page.value = 1; reload() }, 400)
}

function onTableOptions (opts: { page: number, itemsPerPage: number }) {
  page.value = opts.page
  pageSize.value = opts.itemsPerPage
  reload()
}

// ── 提示 ──────────────────────────────────────────────────────────────
const snackbar = ref(false)
const snackbarText = ref('')
const snackbarColor = ref('success')
function notify (text: string, color = 'success') {
  snackbarText.value = text
  snackbarColor.value = color
  snackbar.value = true
}

/** 從錯誤物件取出可讀訊息；detail 可能是字串或物件 */
function errText (e: unknown, fallback: string): string {
  const detail = (e as { response?: { data?: { detail?: unknown } } })?.response?.data?.detail
  if (typeof detail === 'string') return detail
  if (detail && typeof detail === 'object' && 'message' in detail) {
    return String((detail as { message: unknown }).message)
  }
  return fallback
}

// ── 表單 ──────────────────────────────────────────────────────────────
const formDialog = ref(false)
const formRef = ref()
const contentRef = ref()
const saving = ref(false)
const editingId = ref<number | null>(null)
const form = ref<{ title: string, type_id: number | null, content_markdown: string, publish_date: string, is_pinned: boolean }>({
  title: '', type_id: null, content_markdown: '', publish_date: '', is_pinned: false,
})

const titleRules = [
  (v: string) => !!v?.trim() || '請輸入標題',
  (v: string) => (v?.length ?? 0) <= 200 || '標題不得超過 200 字',
]
const typeRules = [(v: number | null) => !!v || '請選擇類型']
const contentRules = [(v: string) => (v?.length ?? 0) <= 50000 || '內容不得超過 50000 字']

function openCreate () {
  editingId.value = null
  form.value = { title: '', type_id: store.types[0]?.id ?? null, content_markdown: '', publish_date: '', is_pinned: false }
  previewHtml.value = ''
  previewNotices.value = []
  formDialog.value = true
}

async function openEdit (item: AnnouncementManageListItem) {
  const detail = await store.fetchManageDetail(item.id)
  if (!detail) { notify(store.error ?? '無法載入公告內容', 'error'); return }
  editingId.value = detail.id
  form.value = {
    title: detail.title,
    type_id: detail.type.id,
    content_markdown: detail.content_markdown ?? '',
    publish_date: detail.publish_date,
    is_pinned: detail.is_pinned,
  }
  previewHtml.value = detail.content
  previewNotices.value = []
  formDialog.value = true
  refreshPreview()
}

async function save () {
  const { valid } = await formRef.value.validate()
  if (!valid) return
  saving.value = true
  try {
    const payload = {
      title: form.value.title.trim(),
      type_id: form.value.type_id as number,
      content_markdown: form.value.content_markdown || null,
      publish_date: form.value.publish_date || null,
      is_pinned: form.value.is_pinned,
    }
    if (editingId.value) {
      await store.update(editingId.value, payload)
      notify('公告已更新')
    } else {
      await store.create(payload)
      notify('公告已建立為草稿')
    }
    formDialog.value = false
    await reload()
  } catch (e) {
    notify(errText(e, '儲存失敗'), 'error')
  } finally {
    saving.value = false
  }
}

// ── 預覽（去抖動）──────────────────────────────────────────────────────
const previewHtml = ref('')
const previewNotices = ref<string[]>([])
let previewTimer: ReturnType<typeof setTimeout> | null = null

function noticeLabel (n: string) {
  if (n === 'style' || n === 'class') return `樣式設定（${n}）`
  if (n.startsWith('on')) return `事件屬性（${n}）`
  if (['javascript', 'data', 'vbscript'].includes(n)) return `連結協定（${n}:）`
  return `網頁標籤（<${n}>）`
}

async function refreshPreview () {
  const res = await store.preview(form.value.content_markdown ?? '')
  if (!res) return
  previewHtml.value = res.content
  previewNotices.value = res.notices
}

watch(() => form.value.content_markdown, () => {
  if (previewTimer) clearTimeout(previewTimer)
  previewTimer = setTimeout(refreshPreview, 500)
})

// ── 插入操作 ──────────────────────────────────────────────────────────
function textareaEl (): HTMLTextAreaElement | null {
  return contentRef.value?.$el?.querySelector('textarea') ?? null
}

function insertAtCursor (text: string) {
  const el = textareaEl()
  const cur = form.value.content_markdown ?? ''
  if (!el) { form.value.content_markdown = cur + text; return }
  const s = el.selectionStart ?? cur.length
  const e = el.selectionEnd ?? cur.length
  form.value.content_markdown = cur.slice(0, s) + text + cur.slice(e)
  nextTick(() => { el.focus(); el.selectionStart = el.selectionEnd = s + text.length })
}

function wrapSelection (before: string, after: string) {
  const el = textareaEl()
  const cur = form.value.content_markdown ?? ''
  if (!el) { form.value.content_markdown = cur + before + '文字' + after; return }
  const s = el.selectionStart ?? 0
  const e = el.selectionEnd ?? 0
  const sel = cur.slice(s, e) || '文字'
  form.value.content_markdown = cur.slice(0, s) + before + sel + after + cur.slice(e)
}

// 插入下載附件
const attachDialog = ref(false)
const attachFormRef = ref()
const attach = ref({ url: '', filename: '' })

/** 只認 file/d/{ID}/ 形式——不做多變體猜測解析：猜錯會產出壞掉的縮圖，
 *  比直接說「認不得這個連結」更糟（歸因與誠實原則）。 */
const DRIVE_FILE_ID = /drive\.google\.com\/file\/d\/([A-Za-z0-9_-]+)/

const driveUrlRules = [
  (v: string) => !!v?.trim() || '請輸入 Google Drive 分享連結',
  (v: string) => DRIVE_FILE_ID.test(v ?? '')
    || '無法從此連結取得檔案 ID。預期格式：https://drive.google.com/file/d/檔案ID/view',
]

async function insertAttachment () {
  const { valid } = await attachFormRef.value.validate()
  if (!valid) return
  const id = DRIVE_FILE_ID.exec(attach.value.url)?.[1]
  if (!id) return
  const name = attach.value.filename.trim()
  const link = `https://drive.google.com/file/d/${id}/view?usp=sharing`
  const thumb = `https://drive.google.com/thumbnail?id=${id}&sz=w300`
  insertAtCursor(`\n\n[![${name}](${thumb})](${link})\n\n[👉 點此下載：${name}](${link})\n`)
  attachDialog.value = false
  attach.value = { url: '', filename: '' }
}

// ── 發布 / 下架 ───────────────────────────────────────────────────────
const publishDialog = ref(false)
const pendingPublish = ref<AnnouncementManageListItem | null>(null)
const updateDateOnPublish = ref(false)

const publishDateStale = computed(() => {
  const d = pendingPublish.value?.publish_date
  if (!d) return false
  return d < new Date().toISOString().slice(0, 10)
})

function askPublish (item: AnnouncementManageListItem) {
  pendingPublish.value = item
  updateDateOnPublish.value = false
  publishDialog.value = true
}

async function doPublish () {
  const item = pendingPublish.value
  if (!item) return
  saving.value = true
  try {
    // 系統不自動改日期——自動改會讓「刻意保留較早日期」（補登過去公告、
    // 依公文日期標示）無法達成。只有操作者明示勾選才更新。
    if (updateDateOnPublish.value) {
      const detail = await store.fetchManageDetail(item.id)
      if (!detail) throw new Error('無法載入公告內容')
      await store.update(item.id, {
        title: detail.title,
        type_id: detail.type.id,
        content_markdown: detail.content_markdown,
        publish_date: new Date().toISOString().slice(0, 10),
        is_pinned: detail.is_pinned,
      })
    }
    await store.publish(item.id)
    notify('公告已發布')
    publishDialog.value = false
    await reload()
  } catch (e) {
    notify(errText(e, '發布失敗'), 'error')
  } finally {
    saving.value = false
  }
}

async function doUnpublish (item: AnnouncementManageListItem) {
  saving.value = true
  try {
    await store.unpublish(item.id)
    notify('公告已下架')
    await reload()
  } catch (e) {
    notify(errText(e, '下架失敗'), 'error')
  } finally {
    saving.value = false
  }
}

// ── 刪除 ──────────────────────────────────────────────────────────────
const deleteDialog = ref(false)
const pendingDelete = ref<AnnouncementManageListItem | null>(null)

function askDelete (item: AnnouncementManageListItem) {
  pendingDelete.value = item
  deleteDialog.value = true
}

async function doDelete () {
  const item = pendingDelete.value
  if (!item) return
  saving.value = true
  try {
    await store.remove(item.id)
    notify('公告已刪除')
    deleteDialog.value = false
    await reload()
  } catch (e) {
    notify(errText(e, '刪除失敗'), 'error')
  } finally {
    saving.value = false
  }
}

// ── 類型維護 ──────────────────────────────────────────────────────────
const typeDialog = ref(false)
const typeFormRef = ref()
const typeError = ref('')
const editingTypeId = ref<number | null>(null)
const typeForm = ref({ name: '', color: '' })

const typeNameRules = [
  (v: string) => !!v?.trim() || '請輸入名稱',
  (v: string) => (v?.length ?? 0) <= 20 || '名稱不得超過 20 字',
]
const typeColorRules = [
  (v: string) => !!v?.trim() || '請輸入顏色',
  (v: string) => (v?.length ?? 0) <= 30 || '顏色不得超過 30 字',
]

function resetTypeForm () {
  editingTypeId.value = null
  typeForm.value = { name: '', color: '' }
  typeFormRef.value?.resetValidation()
}

function startEditType (t: AnnouncementType) {
  editingTypeId.value = t.id
  typeForm.value = { name: t.name, color: t.color }
}

async function saveType () {
  const { valid } = await typeFormRef.value.validate()
  if (!valid) return
  saving.value = true
  typeError.value = ''
  try {
    const payload = { name: typeForm.value.name.trim(), color: typeForm.value.color.trim() }
    if (editingTypeId.value) {
      await store.updateType(editingTypeId.value, payload)
      notify('類型已更新')
    } else {
      await store.createType(payload)
      notify('類型已新增')
    }
    resetTypeForm()
    await store.fetchTypes()
    await reload()
  } catch (e) {
    typeError.value = errText(e, '類型儲存失敗')
  } finally {
    saving.value = false
  }
}

async function doDeleteType (t: AnnouncementType) {
  saving.value = true
  typeError.value = ''
  try {
    await store.removeType(t.id)
    notify('類型已刪除')
    await store.fetchTypes()
  } catch (e) {
    // 使用中的類型不可刪——後端回傳含使用數量的訊息，原樣呈現
    typeError.value = errText(e, '類型刪除失敗')
  } finally {
    saving.value = false
  }
}

onMounted(async () => {
  await store.fetchTypes()
  await reload()
})
</script>

<style scoped>
.section-wrapper {
  margin-top: 16px;
}

/* 左欄工具列與右欄預覽標題同高，使輸入框與預覽窗格上緣對齊 */
.editor-toolbar {
  min-height: 36px;
}

.preview-pane {
  min-height: 320px;
  max-height: 460px;
  overflow-y: auto;
  background-color: #fafafa;
}

/* 預覽窗格套用與公告明細頁相同的內容樣式，使管理者所見即所得 */
.preview-pane :deep(.content-text img) {
  border: 1px solid #ddd;
  border-radius: 4px;
  cursor: pointer;
  margin: 15px 0;
  display: block;
  max-width: 100%;
}

.preview-pane :deep(.content-text a) {
  color: #2c3e50;
  text-decoration: underline;
  font-weight: bold;
}
</style>
