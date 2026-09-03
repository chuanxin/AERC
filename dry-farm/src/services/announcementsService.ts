/**
 * 040 公告（最新消息）系統化管理的 API 封裝。
 *
 * 新增端點必經三處，缺一不可（CLAUDE.md 記載同一個坑已踩過兩次）：
 *   1. services/api/endpoints.ts  — 前端路徑常數
 *   2. services/api/mapping.ts    — BACKEND_PATHS + API_MAPPING／DYNAMIC_PATH_PATTERNS
 *   3. 本檔                        — 呼叫端
 * 漏掉第 2 處不會有任何靜態訊號，只有實際發請求才 404。
 */

import { ANNOUNCEMENTS } from './api/endpoints'
import { apiService } from './api/http'
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
  Paginated,
  PreviewResponse,
} from '@/types/announcements'

export const announcementsService = {
  // ── 公開讀取 ────────────────────────────────────────────────────────
  /** 首頁用：傳 limit 取最新數則（與分頁參數互斥） */
  async fetchLatest (limit: number): Promise<Paginated<AnnouncementListItem>> {
    return apiService.get(ANNOUNCEMENTS.LIST, { params: { limit } })
  },

  /** 列表頁用：分頁 */
  async fetchPublished (page = 1, pageSize = 20): Promise<Paginated<AnnouncementListItem>> {
    return apiService.get(ANNOUNCEMENTS.LIST, { params: { page, page_size: pageSize } })
  },

  async fetchDetail (id: number): Promise<AnnouncementPublicDetail> {
    return apiService.get(ANNOUNCEMENTS.DETAIL(id))
  },

  // ── 公告類型（權限 VIEW）────────────────────────────────────────────
  async fetchTypes (): Promise<AnnouncementType[]> {
    return apiService.get(ANNOUNCEMENTS.TYPES)
  },

  async createType (payload: AnnouncementTypePayload): Promise<AnnouncementType> {
    return apiService.post(ANNOUNCEMENTS.TYPES, payload)
  },

  async updateType (id: number, payload: AnnouncementTypePayload): Promise<AnnouncementType> {
    return apiService.put(ANNOUNCEMENTS.TYPE_DETAIL(id), payload)
  },

  async deleteType (id: number): Promise<void> {
    return apiService.delete(ANNOUNCEMENTS.TYPE_DETAIL(id))
  },

  // ── 管理 ────────────────────────────────────────────────────────────
  async fetchManageList (params: ManageListParams = {}): Promise<Paginated<AnnouncementManageListItem>> {
    return apiService.get(ANNOUNCEMENTS.MANAGE_LIST, { params: params as Record<string, unknown> })
  },

  async fetchManageDetail (id: number): Promise<AnnouncementManageDetail> {
    return apiService.get(ANNOUNCEMENTS.MANAGE_DETAIL(id))
  },

  async create (payload: AnnouncementCreatePayload): Promise<AnnouncementManageDetail> {
    return apiService.post(ANNOUNCEMENTS.CREATE, payload)
  },

  async update (id: number, payload: AnnouncementUpdatePayload): Promise<AnnouncementManageDetail> {
    return apiService.put(ANNOUNCEMENTS.MANAGE_DETAIL(id), payload)
  },

  async publish (id: number): Promise<AnnouncementManageDetail> {
    return apiService.patch(ANNOUNCEMENTS.MANAGE_PUBLISH(id))
  },

  async unpublish (id: number): Promise<AnnouncementManageDetail> {
    return apiService.patch(ANNOUNCEMENTS.MANAGE_UNPUBLISH(id))
  },

  async remove (id: number): Promise<void> {
    return apiService.delete(ANNOUNCEMENTS.MANAGE_DETAIL(id))
  },

  /** 編輯期即時預覽：回傳可直接呈現的 HTML 與被移除項目的提示 */
  async preview (contentMarkdown: string): Promise<PreviewResponse> {
    return apiService.post(ANNOUNCEMENTS.PREVIEW, { content_markdown: contentMarkdown })
  },
}
