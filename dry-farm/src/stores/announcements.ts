/**
 * 040 公告（最新消息）狀態管理。
 *
 * ⚠️ 本 store 的寫入動作**刻意不使用 `wrapAsync`**。
 *
 * `wrapAsync` 失敗時不 rethrow，而是把訊息寫入 errorRef、回傳 `null`
 * （utils/asyncHelpers.ts:54-68）。呼叫端若寫成 `await store.action()` 後接
 * 無條件成功訊息、再用 `} catch {}` 兜底，catch 永遠不會執行，失敗會顯示成
 * 成功——CLAUDE.md TD-027 記載此模式在 `config/accounts.vue` 已造成 3 處
 * 「假成功」缺陷。公告的寫入動作（發布、下架、刪除）若靜默失敗，操作者會
 * 以為公告已上線而實際沒有，因此這裡讓例外**往外拋**，由呼叫端明確處理。
 *
 * 唯讀查詢仍用 `wrapAsync`：失敗時頁面靠 `error` 橫幅呈現，是既有的正規機制。
 */

import { defineStore } from 'pinia'
import { computed, ref } from 'vue'

import { announcementsService } from '@/services/announcementsService'
import { wrapAsync } from '@/utils/asyncHelpers'
import type {
  AnnouncementCreatePayload,
  AnnouncementListItem,
  AnnouncementManageDetail,
  AnnouncementManageListItem,
  AnnouncementPublicDetail,
  AnnouncementType,
  AnnouncementTypePayload,
  AnnouncementUpdatePayload,
  ManageListParams,
  PreviewResponse,
} from '@/types/announcements'

export const useAnnouncementsStore = defineStore('announcements', () => {
  // ── 狀態 ──────────────────────────────────────────────────────────
  const publicItems = ref<AnnouncementListItem[]>([])
  const publicTotal = ref(0)
  const publicPage = ref(1)
  const publicTotalPages = ref(1)
  const detail = ref<AnnouncementPublicDetail | null>(null)

  const manageItems = ref<AnnouncementManageListItem[]>([])
  const manageTotal = ref(0)
  const manageTotalPages = ref(1)
  const manageDetail = ref<AnnouncementManageDetail | null>(null)

  const types = ref<AnnouncementType[]>([])

  const loading = ref(false)
  const error = ref<string | null>(null)

  const hasError = computed(() => error.value !== null)
  const isEmpty = computed(() => publicItems.value.length === 0)

  // ── 唯讀查詢（wrapAsync：失敗回 null，頁面以 error 橫幅呈現）──────────
  const fetchLatest = wrapAsync(async (limit: number = 5) => {
    const res = await announcementsService.fetchLatest(limit)
    publicItems.value = res.items
    publicTotal.value = res.total
    return res
  }, { loadingRef: loading, errorRef: error })

  const fetchPublished = wrapAsync(async (page: number = 1, pageSize: number = 20) => {
    const res = await announcementsService.fetchPublished(page, pageSize)
    publicItems.value = res.items
    publicTotal.value = res.total
    publicPage.value = res.page
    publicTotalPages.value = res.total_pages
    return res
  }, { loadingRef: loading, errorRef: error })

  const fetchDetail = wrapAsync(async (id: number) => {
    detail.value = await announcementsService.fetchDetail(id)
    return detail.value
  }, { loadingRef: loading, errorRef: error })

  const fetchManageList = wrapAsync(async (params: ManageListParams = {}) => {
    const res = await announcementsService.fetchManageList(params)
    manageItems.value = res.items
    manageTotal.value = res.total
    manageTotalPages.value = res.total_pages
    return res
  }, { loadingRef: loading, errorRef: error })

  const fetchManageDetail = wrapAsync(async (id: number) => {
    manageDetail.value = await announcementsService.fetchManageDetail(id)
    return manageDetail.value
  }, { loadingRef: loading, errorRef: error })

  const fetchTypes = wrapAsync(async () => {
    types.value = await announcementsService.fetchTypes()
    return types.value
  }, { loadingRef: loading, errorRef: error })

  // ── 寫入動作（例外往外拋，呼叫端必須明確處理）─────────────────────
  async function create (payload: AnnouncementCreatePayload) {
    return announcementsService.create(payload)
  }

  async function update (id: number, payload: AnnouncementUpdatePayload) {
    return announcementsService.update(id, payload)
  }

  async function publish (id: number) {
    return announcementsService.publish(id)
  }

  async function unpublish (id: number) {
    return announcementsService.unpublish(id)
  }

  async function remove (id: number) {
    return announcementsService.remove(id)
  }

  async function createType (payload: AnnouncementTypePayload) {
    return announcementsService.createType(payload)
  }

  async function updateType (id: number, payload: AnnouncementTypePayload) {
    return announcementsService.updateType(id, payload)
  }

  async function removeType (id: number) {
    return announcementsService.deleteType(id)
  }

  /** 編輯期預覽——失敗不阻擋編輯，回傳 null 由呼叫端決定是否提示 */
  async function preview (contentMarkdown: string): Promise<PreviewResponse | null> {
    try {
      return await announcementsService.preview(contentMarkdown)
    } catch {
      return null
    }
  }

  function clearError () {
    error.value = null
  }

  return {
    publicItems, publicTotal, publicPage, publicTotalPages, detail,
    manageItems, manageTotal, manageTotalPages, manageDetail,
    types, loading, error, hasError, isEmpty,
    fetchLatest, fetchPublished, fetchDetail,
    fetchManageList, fetchManageDetail, fetchTypes,
    create, update, publish, unpublish, remove,
    createType, updateType, removeType,
    preview, clearError,
  }
})
