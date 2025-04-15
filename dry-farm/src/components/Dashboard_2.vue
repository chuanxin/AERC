<template>
  <v-container class="px-6 py-4">
    <!-- 最新消息區塊 -->
    <v-card class="mb-6">
      <v-card-title class="bg-light-blue-lighten-4 d-flex align-center py-2 px-4">
        <v-icon class="me-2" size="small">mdi-newspaper</v-icon>
        <span class="text-subtitle-1 font-weight-medium">最新消息</span>
      </v-card-title>

      <v-card-text class="pa-0">
        <v-table density="comfortable">
          <thead>
            <tr>
              <th class="text-center" width="15%">公告</th>
              <th>內容</th>
              <th class="text-center" width="15%">發布時間</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(item, index) in announcements" :key="index">
              <td class="text-center">{{ item.title }}</td>
              <td>{{ item.content }}</td>
              <td class="text-center">{{ item.publishDate }}</td>
            </tr>
          </tbody>
        </v-table>
      </v-card-text>
    </v-card>

    <!-- 文件下載區塊 -->
    <v-card class="mb-6">
      <v-card-title class="bg-light-blue-lighten-4 d-flex align-center py-2 px-4">
        <v-icon class="me-2" size="small">mdi-download</v-icon>
        <span class="text-subtitle-1 font-weight-medium">文件下載</span>
      </v-card-title>

      <v-card-text class="pa-0">
        <v-table density="comfortable">
          <thead>
            <tr>
              <th>名稱</th>
              <th class="text-center" width="15%">檔案</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(doc, index) in documents" :key="index">
              <td>{{ doc.name }}</td>
              <td class="text-center">
                <div class="d-flex justify-center gap-2">
                  <v-btn size="small" density="comfortable" color="primary" variant="text" class="text-none" @click="downloadFile(doc.id, 'odt')">
                    (odt)
                  </v-btn>
                  <span>/</span>
                  <v-btn size="small" density="comfortable" color="primary" variant="text" class="text-none" @click="downloadFile(doc.id, 'pdf')">
                    (pdf)
                  </v-btn>
                </div>
              </td>
            </tr>
          </tbody>
        </v-table>
      </v-card-text>
    </v-card>

    <!-- 預算執行狀況區塊 -->
    <v-sheet>
    <v-card class="mb-6">
      <v-card-title class="bg-light-blue-lighten-4 d-flex align-center py-2 px-4">
        <v-icon class="me-2" size="small">mdi-currency-usd</v-icon>
        <span class="text-subtitle-1 font-weight-medium">預算執行</span>
      </v-card-title>

      <v-card-text class="pa-4">
        <!-- 預算執行率摘要 -->
        <v-sheet class="pa-3 rounded mb-4" color="green-lighten-5">
          <div class="d-flex align-center">
            <div class="me-4">
              <div class="text-caption text-medium-emphasis mb-1">執行率</div>
              <div class="text-green-darken-3 text-h4 font-weight-bold">90%</div>
            </div>
            <v-divider vertical class="mx-3 h-100"></v-divider>
            <div class="me-4">
              <div class="text-caption text-medium-emphasis mb-1">已動支金額</div>
              <div class="text-green-darken-3 text-h6 font-weight-medium">NT$26,442.00</div>
            </div>
            <v-divider vertical class="mx-3 h-100"></v-divider>
            <div>
              <div class="text-caption text-medium-emphasis mb-1">尚餘金額</div>
              <div class="text-h6 font-weight-medium">NT$2,938.00</div>
            </div>
            <v-spacer></v-spacer>
            <div class="text-right">
              <div class="text-caption text-medium-emphasis mb-1">年度編列預算</div>
              <div class="text-h6 font-weight-medium">NT$29,380.00</div>
            </div>
          </div>
        </v-sheet>

        <!-- 預算執行進度條 -->
        <div class="position-relative mb-4">
          <div
            :style="`right: calc(100% - ${budgetStats.executionRate}%)`"
            class="position-absolute"
            style="top: -24px"
          >
            <v-chip color="green-darken-3" size="small" label>已驗收</v-chip>
          </div>
          <v-progress-linear
            color="green-darken-3"
            height="22"
            :model-value="budgetStats.executionRate"
            rounded="lg"
          >
            <v-badge
              :style="`right: ${100 - budgetStats.executionRate}%`"
              class="position-absolute"
              color="white"
              dot
              inline
            />
          </v-progress-linear>
        </div>

        <!-- 查看詳細預算資訊按鈕 -->
        <v-sheet class="text-center mt-6">
          <v-btn
            color="green-darken-1"
            variant="outlined"
            block
            class="py-3"
            prepend-icon="mdi-clipboard-text-outline"
            to="/budget"
          >
            <span class="font-weight-medium">查看預算執行詳細資訊</span>
          </v-btn>
        </v-sheet>
      </v-card-text>
    </v-card>
  </v-sheet>

    <!-- 補助申請快捷按鈕 -->
    <!-- <v-card class="mb-6" variant="outlined">
      <v-card-title class="bg-light-blue-lighten-4 d-flex align-center py-2 px-4">
        <v-icon class="me-2" size="small">mdi-file-document-edit</v-icon>
        <span class="text-subtitle-1 font-weight-medium">補助申請</span>
      </v-card-title>

      <v-card-text class="pa-4">
        <v-row>
          <v-col cols="12" md="6">
            <v-card
              class="mb-4"
              variant="outlined"
              height="160"
              hover
              @click="navigateTo('/grants/new')"
            >
              <v-card-text class="d-flex flex-column align-center justify-center h-100">
                <v-icon
                  color="primary"
                  icon="mdi-file-plus"
                  size="x-large"
                  class="mb-2"
                ></v-icon>
                <div class="text-h6 font-weight-medium">建立新申請案</div>
                <div class="text-caption text-medium-emphasis">建立新的補助申請專案</div>
              </v-card-text>
            </v-card>
          </v-col>
          <v-col cols="12" md="6">
            <v-card
              class="mb-4"
              variant="outlined"
              height="160"
              hover
              @click="navigateTo('/grants')"
            >
              <v-card-text class="d-flex flex-column align-center justify-center h-100">
                <v-icon
                  color="primary"
                  icon="mdi-format-list-bulleted"
                  size="x-large"
                  class="mb-2"
                ></v-icon>
                <div class="text-h6 font-weight-medium">查看申請案件</div>
                <div class="text-caption text-medium-emphasis">查看所有補助申請專案</div>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>
      </v-card-text>
    </v-card> -->
  </v-container>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();

// 最新消息資料
const announcements = ref([
  {
    title: '停機公告',
    content: '將於113/09/30 14:00~18:00 暫停使用',
    publishDate: '113/9/26'
  },
  {
    title: '停機公告',
    content: '將於113/08/30 14:00~18:00 暫停使用',
    publishDate: '113/8/26'
  },
  {
    title: '系統更新',
    content: '系統已更新至v1.2.0版本，新增多項功能',
    publishDate: '113/8/15'
  }
]);

// 文件下載資料
const documents = ref([
  {
    id: 1,
    name: '農業部農田水利署推廣管路灌溉作業要點',
  },
  {
    id: 2,
    name: '補助宣導摺頁',
  },
  {
    id: 3,
    name: '管路灌溉補助申請表格',
  }
]);

// 預算執行狀況
const budgetStats = reactive({
  executionRate: 90, // 執行率 90%
  budget: 29380, // 年度預算 29,380元
  spent: 26442, // 已動支金額 26,442元
  remaining: 2938, // 尚餘 2,938元
});

// 下載檔案
const downloadFile = (id: number, format: string) => {
  // 實際應用中應該調用API下載檔案
  console.log(`下載檔案ID: ${id}, 格式: ${format}`);
  // 可以使用window.open或其他方式觸發下載
};

// 路由導航
const navigateTo = (path: string) => {
  router.push(path);
};

onMounted(() => {
  // 這裡可以放初始化邏輯，例如從API獲取最新公告、預算資訊等
});
</script>

<style scoped>
.bg-light-blue-lighten-4 {
  background-color: #B3E5FC !important;
}

.position-relative {
  position: relative;
}

.position-absolute {
  position: absolute;
}

/* 讓卡片變得可點擊 */
.v-card.hover {
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}

.v-card.hover:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1) !important;
}
</style>
