/**
 * 040 公告（最新消息）系統化管理的型別定義。
 *
 * 內容欄位有兩種形式，用途不同：
 * - `contentMarkdown`：作者原文，唯一儲存形式，僅管理端回傳（供編輯器載入）
 * - `content`：後端於本次請求渲染 + 消毒的 HTML，供 `v-html` 直接呈現
 */

export type AnnouncementStatus = 'draft' | 'published' | 'archived'

export interface AnnouncementType {
  id: number
  name: string
  /** Vuetify 色名或 hex，用於列表標籤 */
  color: string
}

/** 列表項目——不含內容 */
export interface AnnouncementListItem {
  id: number
  title: string
  type: AnnouncementType
  /** ISO YYYY-MM-DD；民國格式化是前端呈現層的事（utils/rocDate.ts） */
  publish_date: string
  is_pinned: boolean
}

/** 公開明細——content 為渲染後 HTML，不含作者原文 */
export interface AnnouncementPublicDetail extends AnnouncementListItem {
  content: string
  status: AnnouncementStatus
  published_at: string | null
}

export interface AnnouncementManageListItem extends AnnouncementListItem {
  status: AnnouncementStatus
  created_by_username: string | null
  published_at: string | null
  created_at: string
  updated_at: string
}

/** 管理明細——唯一同時回傳作者原文與渲染結果的回應 */
export interface AnnouncementManageDetail extends AnnouncementManageListItem {
  content_markdown: string | null
  content: string
}

export interface AnnouncementCreatePayload {
  title: string
  type_id: number
  content_markdown?: string | null
  /** 選填；未提供時後端填入建立當日 */
  publish_date?: string | null
  is_pinned?: boolean
}

export type AnnouncementUpdatePayload = AnnouncementCreatePayload

export interface AnnouncementTypePayload {
  name: string
  color: string
}

/** 預覽回應：content 供直接呈現，notices 為給人看的提示（不參與安全判定） */
export interface PreviewResponse {
  content: string
  changed: boolean
  notices: string[]
}

export interface Paginated<T> {
  items: T[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

export interface ManageListParams {
  page?: number
  page_size?: number
  status?: AnnouncementStatus
  type_id?: number
  keyword?: string
}
