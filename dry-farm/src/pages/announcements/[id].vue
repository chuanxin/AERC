<template>
  <v-container
    fluid
    class="grants-container px-6 pb-0 pt-0"
    style="background-color: white"
  >
    <v-row justify="center">
      <v-col cols="10" lg="10" align-self="center" class="pt-4">
        <div class="d-flex align-center pr-2 mb-2">
          <v-btn
            variant="text"
            prepend-icon="mdi-arrow-left"
            color="primary"
            @click="goBack"
          >
            返回
          </v-btn>
          <v-spacer />
        </div>

        <div class="section-wrapper">
          <v-card
            class="mx-auto section-card pa-4"
            variant="outlined"
            rounded="lg"
          >
            <!-- 載入中 -->
            <v-card-text v-if="loading" class="py-16 text-center">
              <v-progress-circular indeterminate color="primary" size="48" />
            </v-card-text>

            <!-- 找不到（不存在、已刪除、或無權讀取的草稿／已下架）-->
            <v-card-text v-else-if="!announcement" class="py-8">
              <v-empty-state
                headline="找不到此公告"
                title="這則公告不存在或已下架"
                text="請返回最新消息列表查看其他公告。"
                icon="mdi-bullhorn-outline"
                min-height="280"
              />
            </v-card-text>

            <template v-else>
              <v-card-item class="custom-title">
                <v-card-title class="text-h5 font-weight-black text-wrap">
                  {{ announcement.title }}
                </v-card-title>
              </v-card-item>

              <v-card-text>
                <div class="d-flex align-center flex-wrap mb-4">
                  <v-chip
                    :color="announcement.type.color"
                    variant="outlined"
                    size="small"
                    label
                    class="mr-3"
                  >
                    {{ announcement.type.name }}
                  </v-chip>
                  <span class="text-subtitle-2 text-grey-darken-1">
                    發布日期：{{ toRocDate(announcement.publish_date) }}
                  </span>
                  <v-chip
                    v-if="announcement.status !== 'published'"
                    color="warning"
                    variant="flat"
                    size="small"
                    label
                    class="ml-3"
                  >
                    預覽（{{ announcement.status === 'draft' ? '草稿' : '已下架' }}）
                  </v-chip>
                </div>

                <v-divider class="mb-4" />

                <!--
                  content 是後端於本次請求渲染並消毒的 HTML。
                  刻意不設 white-space: pre-wrap——換行與段落已由 Markdown
                  轉為 <br>／<p>，再加 pre-wrap 會讓標籤之間的排版空白也被
                  渲染出多餘空行。
                -->
                <div
                  v-if="announcement.content"
                  class="content-text text-body-1"
                  v-html="announcement.content"
                />
                <div v-else class="text-grey">
                  （本則公告沒有詳細內容）
                </div>
              </v-card-text>
            </template>
          </v-card>
        </div>
      </v-col>
    </v-row>
  </v-container>
</template>

<script lang="ts" setup>
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { announcementsService } from '@/services/announcementsService'
import { toRocDate } from '@/utils/rocDate'
import type { AnnouncementPublicDetail } from '@/types/announcements'

const route = useRoute()
const router = useRouter()

const announcement = ref<AnnouncementPublicDetail | null>(null)
const loading = ref(true)

function goBack () {
  // 有瀏覽歷史就回上一頁（可能是首頁或列表頁），否則回首頁
  if (window.history.length > 1) router.back()
  else router.push('/')
}

onMounted(async () => {
  // typed-router 的 params 型別為聯集，先取出再轉數字
  const rawId = (route.params as { id?: string }).id
  const id = Number(rawId)
  if (!Number.isInteger(id) || id <= 0) {
    loading.value = false
    return
  }
  try {
    announcement.value = await announcementsService.fetchDetail(id)
  } catch {
    // 不存在、已刪除、或一般使用者存取非 published——三者回應相同，
    // 一律呈現「找不到此公告」，不呈現空白頁或系統錯誤訊息（FR-017）
    announcement.value = null
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.section-wrapper {
  margin-top: 8px;
}

/*
  公告內容的外觀——**樣式規則的唯一來源**。
  內容本身不攜帶任何 style 或 class（消毒時已移除），外觀一律由此處
  對元素統一設定，因此前後端沒有任何清單需要鎖步同步。

  數值逐項取自既有公告的行內樣式，使移轉後的視覺呈現與移轉前一致。
  不保留原 transition: .3s——滑鼠移入變淡的行為已不支援，那會是永遠
  不觸發的死樣式。
*/
.content-text :deep(img) {
  border: 1px solid #ddd;
  border-radius: 4px;
  cursor: pointer;
  margin: 15px 0;
  display: block;
  max-width: 100%;
}

.content-text :deep(a) {
  color: #2c3e50;
  text-decoration: underline;
  font-weight: bold;
}

.content-text :deep(p) {
  margin-bottom: 12px;
}

.content-text :deep(ul),
.content-text :deep(ol) {
  padding-left: 24px;
  margin-bottom: 12px;
}
</style>
