<template>
  <v-container
    fluid
    class="px-6 py-4 dashboard-container"
    style="background-color: white"
  >
    <!-- 最新消息區塊 -->
    <v-row justify="center">
      <v-col
        cols="10"
        lg="10"
        align-self="center"
        class="pt-10"
      >
        <div class="section-wrapper">
          <v-card
            class="mx-auto section-card pa-4 pb-0"
            variant="outlined"
            rounded="lg"
          >
            <v-card-item
              class="custom-title"
              color="#3ea0a3"
            >
              <v-card-title class="text-h5 font-weight-black">
                最新消息
              </v-card-title>
            </v-card-item>
            <v-card-text>
              <v-card
                class="table-card mb-4"

                elevation="0"
              >
                <v-table
                  class="news-table rounded-table pt-4 pb-0"
                  hover
                >
                  <thead class="table-header-bold">
                    <tr>
                      <th class="text-left px-2 text-center font-weight-black">
                        發布日期
                      </th>
                      <th class="text-left text-center font-weight-black">
                        類型
                      </th>
                      <th class="text-left text-center font-weight-black">
                        標題
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr
                      v-for="(item, index) in announcements"
                      :key="index"
                      class="news-row text-subtitle-1"
                      :style="index % 2 === 1 ? { backgroundColor: '#62b7bb30' } : {}"
                      @click="viewAnnouncementDetail(item)"
                    >
                      <td class="date-cell text-left py-3 px-3 text-grey text-subtitle-1 text-center">
                        <v-chip
                          color="#FFF8DE"
                          variant="elevated"
                          elevation="0"
                          rounded="lg"
                          class="date-chip"
                          density="comfortable"
                        >
                          {{ item.date }}
                        </v-chip>
                      </td>
                      <td class="type-cell text-center">
                        <v-chip
                          :color="getTypeColor(item.type)"
                          variant="outlined"
                          size="small"
                          label
                          class="font-weight-medium text-subtitle-1"
                        >
                          {{ item.type }}
                        </v-chip>
                      </td>
                      <td
                        class="content-cell px-2"
                      >
                        {{ item.content }}
                      </td>
                    </tr>
                  </tbody>
                </v-table>
              </v-card>

              <!-- 更多連結 -->
              <div class="d-flex justify-end pa-0 ma-0">
                <v-btn
                  class="more-btn"
                  variant="outlined"
                  rounded="lg"
                  color="#3ea0a3"
                  to="/announcements"
                  size="large"
                  append-icon="mdi-chevron-right-circle"
                >
                  更多
                </v-btn>
              </div>
            </v-card-text>
          </v-card>
        </div>
      </v-col>
    </v-row>

    <!-- 預算執行區塊 -->
    <v-row justify="center">
      <v-col
        cols="10"
        lg="10"
        align-self="center"
      >
        <div class="section-wrapper">
          <v-card
            class="mx-auto section-card pa-4 pb-0"
            variant="outlined"
            rounded="lg"
            color="#3ea0a3"
          >
            <v-card-item class="custom-title">
              <v-card-title class="text-h5 font-weight-black">
                預算
              </v-card-title>
            </v-card-item>
            <v-card-text>
              <v-card
                class="table-card mb-4"
                rounded="lg"
                elevation="0"
              >
                <!-- 預算執行率摘要 -->
                <v-sheet
                  class="pa-4 rounded-lg"
                  color="#e3f4f4"
                >
                  <div class="d-flex align-center flex-wrap">
                    <div class="budget-data-group me-4 mb-2">
                      <div class="text-caption text-medium-emphasis mb-1">
                        執行率
                      </div>
                      <div
                        class="text-h4 font-weight-bold"
                        style="color: #3ea0a3;"
                      >
                        90%
                      </div>
                    </div>
                    <v-divider
                      vertical
                      class="mx-3 d-none d-sm-block"
                      style="height: 50px;"
                    />
                    <div class="budget-data-group me-4 mb-2">
                      <div class="text-caption text-medium-emphasis mb-1">
                        已動支金額
                      </div>
                      <div
                        class="text-h6 font-weight-medium"
                        style="color: #3ea0a3;"
                      >
                        NT$26,442.00
                      </div>
                    </div>
                    <v-divider
                      vertical
                      class="mx-3 d-none d-sm-block"
                      style="height: 50px;"
                    />
                    <div class="budget-data-group me-4 mb-2">
                      <div class="text-caption text-medium-emphasis mb-1">
                        尚餘金額
                      </div>
                      <div class="text-h6 font-weight-medium">
                        NT$2,938.00
                      </div>
                    </div>
                    <v-spacer
                      class="d-none d-md-block"
                    />
                    <div class="budget-data-group text-right">
                      <div class="text-caption text-medium-emphasis mb-1">
                        年度編列預算
                      </div>
                      <div class="text-h6 font-weight-medium">
                        NT$29,380.00
                      </div>
                    </div>
                  </div>
                </v-sheet>

                <!-- 預算執行進度條 -->
                <div class="position-relative my-5 px-4 pb-0">
                  <div
                    :style="`right: calc(100% - ${budgetStats.executionRate}%)`"
                    class="position-absolute"
                    style="top: -24px"
                  >
                    <v-chip
                      color="#3ea0a3"
                      size="small"
                      label
                      class="font-weight-medium"
                    >
                      已驗收
                    </v-chip>
                  </div>
                  <v-progress-linear
                    color="#3ea0a3"
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

                <!-- 預算詳細資訊 -->
                <!-- <div class="pa-4 pt-0">
                  <v-expansion-panels variant="accordion" class="budget-panels">
                    <v-expansion-panel elevation="0" class="budget-panel">
                      <v-expansion-panel-title class="py-2">
                        <div class="d-flex align-center">
                          <v-icon icon="mdi-currency-usd" class="me-2" color="#3ea0a3"></v-icon>
                          <span class="font-weight-medium">預算項目明細</span>
                        </div>
                      </v-expansion-panel-title>
                      <v-expansion-panel-text>
                        <v-table density="compact" class="budget-table">
                          <thead>
                            <tr>
                              <th class="text-left">項目</th>
                              <th class="text-right">金額</th>
                              <th class="text-right">執行率</th>
                            </tr>
                          </thead>
                          <tbody>
                            <tr>
                              <td>灌溉系統設備</td>
                              <td class="text-right">NT$15,680.00</td>
                              <td class="text-right">95%</td>
                            </tr>
                            <tr>
                              <td>管線鋪設工程</td>
                              <td class="text-right">NT$8,762.00</td>
                              <td class="text-right">82%</td>
                            </tr>
                            <tr>
                              <td>水質監測設備</td>
                              <td class="text-right">NT$2,000.00</td>
                              <td class="text-right">100%</td>
                            </tr>
                          </tbody>
                        </v-table>
                      </v-expansion-panel-text>
                    </v-expansion-panel>
                  </v-expansion-panels>
                </div> -->
              </v-card>

              <!-- 查看詳細預算資訊按鈕 -->
              <div class="d-flex justify-end pa-0 ma-0">
                <v-btn
                  class="more-btn"
                  variant="outlined"
                  rounded="lg"
                  color="#3ea0a3"
                  to="/budget"
                  size="large"
                  append-icon="mdi-chevron-right-circle"
                >
                  查看詳細資訊
                </v-btn>
              </div>
            </v-card-text>
          </v-card>
        </div>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
const router = useRouter();

// 最新消息資料
const announcements = ref([
  {
    date: '114.01.15',
    type: '系統公告',
    content: '承辦窗口資訊',
    id: 1
  },
  {
    date: '114.01.15',
    type: '停機公告',
    content: '2025/04/30 14:00~18:00系統更新，請暫停使用',
    id: 2
  },
  {
    date: '114.01.15',
    type: '系統公告',
    content: '管路灌溉補助申請表格',
    id: 3
  }
])

// 文件下載資料
const documents = ref([
  {
    id: 1,
    name: '農業部農田水利署推廣管路灌溉作業要點',
    date: '114.01.15',
    icon: 'mdi-file-document-outline'
  },
  {
    id: 2,
    name: '補助宣導摺頁',
    date: '114.01.15',
    icon: 'mdi-file-word-outline'
  },
  {
    id: 3,
    name: '管路灌溉補助申請表格',
    date: '114.01.15',
    icon: 'mdi-file-pdf-outline'
  }
]);

// 預算資料
const budgets = ref([
  {
    year: "114",
    name: "推廣管路灌溉補助",
    color: "blue-grey-lighten-5",
    link: "/budget/114"
  },
  {
    year: "113",
    name: "推廣管路灌溉補助",
    color: "blue-grey-lighten-5",
    link: "/budget/113"
  }
]);

// 根據公告類型返回對應的顏色
const getTypeColor = (type: string) => {
  switch (type) {
    case '系統公告':
      return 'blue';
    case '停機公告':
      return 'deep-orange';
    default:
      return 'grey';
  }
}

// 查看公告詳細內容
const viewAnnouncementDetail = (item) => {
  // 實際應用中，這裡可以導航到詳細頁面
  console.log('查看公告詳情:', item);
  // router.push({ path: '/announcements/detail', query: { id: item.id } });
};

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
/* 添加背景圖片樣式 */
.dashboard-container {
  background-image: url('@/assets/bg_index.png');
  background-size: cover;
  background-position: center bottom;
  background-repeat: no-repeat;
  background-attachment: fixed;
  min-height: 100vh;
}

/* 區塊共通容器 */
.section-wrapper {
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
  padding: 0 0px !important;
  background-color: #3ea0a3 !important;
  border-radius: 8px 8px 0 0;
  z-index: 1;
  transition: all 0.3s ease;
}

.custom-title:not(.full-width-title) .v-card-title {
  justify-content: center;
}

.v-card-title {
  color: white !important;
  display: flex;
  justify-content: flex-start;
  align-items: center;
  width: 100%;
  height: 100%;
  padding-left: 0px;
}

/* 表格樣式 */
.news-table, .files-table {
  /* border-collapse: separate; */
  /* border-spacing: 0; */
}

.table-card, .rounded-table {
  border-radius: 6px;
  overflow: hidden;
}

/* 表頭樣式 */
.table-header-bold th {
  font-weight: 900 !important;
  background-color: #62b7bb30 !important;
  padding-top: 8px !important;
  padding-bottom: 8px !important;
  line-height: 2 !important;
  height: 40px !important;
}

/* 表格單元格樣式 */
.news-row td, .file-row td {
  padding-top: 8px;
  padding-bottom: 8px;
}

.news-table thead tr th {
  font-size: 1.1rem !important;
}

.news-row, .file-row {
  cursor: pointer;
  transition: background-color 0.2s;
}

.news-table tbody tr:hover {
  background-color: rgba(98, 183, 187, 0.2) !important;
}

/* 日期chip專用樣式 */
.date-chip {
  font-weight: 500 !important;
  color: #6b5e2e !important;
  min-width: 85px;
  justify-content: center;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.08) !important;
  /* border: 1px solid rgba(232, 218, 157, 0.5) !important; */
}

/* 日期單元格樣式 */
.date-cell {
  width: 200px;
  white-space: nowrap;
  background-color: transparent !important;
  padding: 8px 12px !important;
  position: relative;
  z-index: 1;
}

.type-cell {
  width: 200px;
  padding-right: 10px;
}

.content-cell, .name-cell {
  font-weight: 500;
}

/* 按鈕樣式 */
.more-btn {
  font-weight: 500;
  /* margin: 8px 0 12px 0; */
  transition: all 0.2s ease;
}

.more-btn:hover {
  background-color: #3ea0a3 !important;
  color: white !important;
}

/* 預算區塊樣式 */
.budget-data-group {
  min-width: 120px;
}

.budget-panels {
  border: 1px solid rgba(62, 160, 163, 0.15);
  border-radius: 8px;
}

.budget-panel :deep(.v-expansion-panel-title) {
  min-height: 48px;
}

.budget-panel :deep(.v-expansion-panel-title:hover) {
  background-color: rgba(62, 160, 163, 0.05);
}

.budget-table {
  margin-top: 8px;
}

.budget-table th {
  color: #3ea0a3;
  font-weight: 700;
  background-color: rgba(62, 160, 163, 0.08);
}

/* 輔助樣式 */
.position-relative {
  position: relative;
}

.position-absolute {
  position: absolute;
}
</style>
