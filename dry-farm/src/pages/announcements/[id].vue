<template>
  <v-container>
    <v-row v-if="loading" justify="center">
      <v-col cols="12" class="text-center mt-10">
        <v-progress-circular indeterminate color="primary"></v-progress-circular>
        <p class="mt-2 text-grey">正在讀取公告資料...</p>
      </v-col>
    </v-row>

    <v-row v-else-if="!announcement" justify="center">
      <v-col cols="10" lg="8" class="text-center mt-10">
        <v-icon icon="mdi-alert-circle-outline" size="64" color="grey"></v-icon>
        <h3 class="text-h5 mt-4 text-grey">找不到此公告</h3>
        <p>您查詢的公告 ID 不存在或已被移除。</p>
        <v-btn color="primary" variant="outlined" class="mt-4" @click="router.go(-1)">
          返回上一頁
        </v-btn>
      </v-col>
    </v-row>

    <v-row v-else justify="center">
      <v-col cols="10" lg="8">
        <v-card class="pa-6 mt-10" elevation="2">
          <v-card-title class="text-h4 font-weight-bold mb-4 text-wrap">
            {{ announcement.content }}
          </v-card-title>

          <v-card-subtitle class="text-subtitle-1 text-grey mb-4 d-flex align-center flex-wrap">
            <span class="mr-2">發布日期: {{ announcement.date }}</span>
            <span class="d-none d-sm-inline mr-2">|</span>
            <span>類型:</span>
            <v-chip
              :color="getTypeColor(announcement.type)"
              variant="outlined"
              size="small"
              label
              class="ml-2 font-weight-medium text-subtitle-1"
            >
              {{ announcement.type }}
            </v-chip>
          </v-card-subtitle>

          <v-divider class="mb-4"></v-divider>

          <v-card-text>
            <div v-if="announcement.fullContent" class="content-text text-body-1">
              {{ announcement.fullContent }}
            </div>
            <div v-else class="text-body-1 text-grey">
              (此公告暫無詳細內容)
            </div>

            <v-alert
              type="info"
              variant="tonal"
              class="mt-6"
              density="compact"
              icon="mdi-information"
            >
              更多相關資訊請聯繫農工中心。
            </v-alert>
          </v-card-text>

          <v-card-actions class="mt-4">
            <v-spacer></v-spacer>
            <v-btn
              color="#3ea0a3"
              variant="outlined"
              size="large"
              prepend-icon="mdi-arrow-left"
              @click="router.go(-1)"
            >
              返回列表
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';

// 1. 引入共用資料與介面
// 請確認你的檔案名稱是 announcement.ts 還是 announcements.ts (有無 s)
// 如果上一部你改成了 announcements.ts，這裡請改成 '@/data/announcements'
import { announcementsData, type Announcement } from '@/data/announcement';

const route = useRoute();
const router = useRouter();

const announcement = ref<Announcement | null>(null);
const loading = ref(false);

// ==========================================
// 模擬 API 請求函數
// ==========================================
const fetchAnnouncementFromAPI = async (id: number): Promise<Announcement | undefined> => {
  // 模擬網路延遲
  await new Promise(resolve => setTimeout(resolve, 300));

  // 從共用的 announcementsData 裡面找
  return announcementsData.find(item => item.id === id);
};

// ==========================================
// 主要邏輯
// ==========================================
const loadData = async () => {
  const id = Number(route.params.id);
  
  if (!id || isNaN(id)) {
    console.error("無效的 ID");
    return;
  }

  loading.value = true;
  announcement.value = null; // 清空舊資料

  try {
    const data = await fetchAnnouncementFromAPI(id);
    if (data) {
      announcement.value = data;
    } else {
      console.warn("找不到資料");
    }
  } catch (error) {
    console.error("API 錯誤", error);
  } finally {
    loading.value = false;
  }
};

// 畫面掛載時執行
onMounted(() => {
  loadData();
});

// 監聽路由變化 (解決：如果在同一頁面切換不同 ID 時不重整的問題)
watch(() => route.params.id, () => {
  loadData();
});

// 輔助樣式函數
const getTypeColor = (type: string) => {
  switch (type) {
    case '系統公告': return 'blue-darken-1';
    case '停機公告': return 'deep-orange-darken-1';
    default: return 'grey-darken-1';
  }
};
</script>

<style scoped>
/* 讓後端傳來的換行符號 (\n) 能正確顯示 */
.content-text {
  white-space: pre-wrap;
  line-height: 1.8;
  color: #333;
}
</style>