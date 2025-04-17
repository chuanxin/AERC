<template>
  <v-container
    fluid
    class="px-6 py-4 bg-white"
  >
    <!-- 最新消息區塊 -->
    <v-row>
      <v-col cols="12">
        <h2 class="section-title mb-4">
          最新消息
        </h2>

        <div class="announcement-list ma-0 pa-0">
          <v-hover
            v-for="(item, index) in announcements"
            :key="index"
            v-slot="{ isHovering, props }"
          >
            <v-card
              v-bind="props"
              variant="outlined"
              class="announcement-item mt-4 mb-0 rounded"
              :elevation="isHovering ? 0 : 0"
              :style="getCardStyles(!!isHovering)"
              @click="viewAnnouncementDetail(item)"
            >
              <div class="d-flex align-center pa-3">
                <!-- 左側標籤 -->
                <v-icon icon="mdi-water-opacity" class="me-2 announcement-icon"/>
                <v-chip
                  :color="isHovering ? getHoverTagColor(item.type) : getTagColor(item.type)"
                  :variant="isHovering ? 'text' : 'outlined'"
                  :class="{'chip-hover': isHovering}"
                  size="large"
                  rounded="lg"
                >
                  <strong>{{ item.title }}</strong>
                </v-chip>

                <!-- 中間內容 -->
                <div
                  class="announcement-content flex-grow-1 mx-3 font-weight-500"
                  :style="isHovering ? 'color: #006064' : ''"
                >
                  {{ item.content }}
                </div>

                <!-- 右側發布時間 -->
                <div
                  class="announcement-time text-right font-weight-500"
                  :style="isHovering ? 'color: #006064;' : ''"
                >
                  <span>發布時間：{{ item.publishDate }}</span>
                </div>
              </div>
            </v-card>
          </v-hover>
        </div>

        <!-- 更多連結 -->
        <div class="d-flex justify-end pa-0 ma-0">
          <v-btn
            class="more-btn"
            variant="plain"
            color="black"
            to="/announcements"
            size="x-large"
            append-icon="mdi-chevron-right-circle"
          >
            更多
          </v-btn>
        </div>
      </v-col>
    </v-row>

    <!-- 文件下載與預算執行區塊 -->
    <v-row>
      <!-- 文件下載區塊 -->
      <v-col cols="12" md="6">
        <h2 class="section-title mb-4">文件下載</h2>

        <v-card
          variant="flat"
          class="mb-6"
        >
          <v-list>
            <v-list-item
              v-for="(doc, index) in documents"
              :key="index"
              class="document-item"
              lines="one"
              @click="downloadFile(doc.id, 'pdf')"
            >
              <template #prepend>
                <v-chip
                  color="amber-lighten-5"
                  rounded="lg"
                  variant="flat"
                  class="document-date text-amber-darken-5 font-weight-medium"
                >
                  {{ doc.date }}
                </v-chip>
              </template>

              <v-list-item-title class="document-name">
                {{ doc.name }}
              </v-list-item-title>

              <template #append>
                <div class="d-flex align-center">
                  <v-btn
                    icon="mdi-download"
                    size="small"
                    color="primary"
                    density="comfortable"
                    variant="text"
                    @click.stop="downloadFile(doc.id, 'pdf')"
                  />
                  <v-icon
                    size="small"
                    color="grey-darken-1"
                    class="ms-1"
                  >
                    mdi-file-document-outline
                  </v-icon>
                </div>
              </template>
            </v-list-item>
          </v-list>
        </v-card>
      </v-col>

      <!-- 預算執行區塊 -->
      <v-col cols="12" md="6">
        <h2 class="section-title mb-4">預算</h2>

        <v-card
          variant="flat"
          class="mb-6"
        >
          <v-list>
            <v-list-item
              v-for="(budget, index) in budgets"
              :key="index"
              class="budget-item"
              :class="index === budgets.length - 1 ? 'mb-0' : ''"
              lines="one"
            >
              <template #prepend>
                <v-chip
                  :color="budget.color"
                  size="x-large"
                  rounded="lg"
                  variant="flat"
                  link
                  class="budget-year text-medium-emphasis font-weight-medium"
                >
                  {{ budget.year }}年預算
                </v-chip>
              </template>

              <v-list-item-title class="budget-name">
                <!-- {{ budget.name }} -->
              </v-list-item-title>

              <!-- <template #append>
                <v-btn
                  color="primary"
                  variant="tonal"
                  size="small"
                  class="me-2"
                  :to="budget.link"
                >
                  查看
                </v-btn>
              </template> -->
            </v-list-item>
          </v-list>
          <!-- <v-card-text class="pa-4"> -->
            <!-- 預算執行率摘要 -->
            <!-- <v-sheet class="pa-3 rounded mb-4" color="green-lighten-5">
              <div class="d-flex align-center flex-wrap">
                <div class="me-4 mb-2">
                  <div class="text-caption text-medium-emphasis mb-1">執行率</div>
                  <div class="text-green-darken-3 text-h4 font-weight-bold">90%</div>
                </div>
                <v-divider vertical class="mx-3 d-none d-sm-block"></v-divider>
                <div class="me-4 mb-2">
                  <div class="text-caption text-medium-emphasis mb-1">已動支金額</div>
                  <div class="text-green-darken-3 text-h6 font-weight-medium">NT$26,442.00</div>
                </div>
                <v-divider vertical class="mx-3 d-none d-sm-block"></v-divider>
                <div class="me-4 mb-2">
                  <div class="text-caption text-medium-emphasis mb-1">尚餘金額</div>
                  <div class="text-h6 font-weight-medium">NT$2,938.00</div>
                </div>
                <v-spacer class="d-none d-md-block"></v-spacer>
                <div>
                  <div class="text-caption text-medium-emphasis mb-1">年度編列預算</div>
                  <div class="text-h6 font-weight-medium">NT$29,380.00</div>
                </div>
              </div>
            </v-sheet> -->

            <!-- 預算執行進度條 -->
            <!-- <div class="position-relative mb-4">
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
            </div> -->

            <!-- 查看詳細預算資訊按鈕 -->
            <!-- <v-sheet class="text-center mt-6">
              <v-btn
                color="green-darken-1"
                variant="tonal"
                block
                class="py-3"
                prepend-icon="mdi-clipboard-text-outline"
                to="/budget"
              >
                <span class="font-weight-medium">查看預算執行詳細資訊</span>
              </v-btn>
            </v-sheet>
          </v-card-text> -->
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
const router = useRouter();

// 最新消息資料
const announcements = ref([
  {
    title: '系統公告',
    type: 'system',
    content: '承辦窗口資訊',
    publishDate: '114/04/05 14:00'
  },
  {
    title: '停機公告',
    type: 'maintenance',
    content: '2025/04/30 14:00~18:00系統更新，請暫停使用',
    publishDate: '114/04/05 14:00'
  },
  {
    title: '停機公告',
    type: 'maintenance',
    content: '2025/04/30 14:00~18:00系統更新，請暫停使用',
    publishDate: '114/04/05 14:00'
  }
]);

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
    icon: 'mdi-file-document-outline'
  },
  {
    id: 3,
    name: '管路灌溉補助申請表格',
    date: '114.01.15',
    icon: 'mdi-file-document-outline'
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

// 根據公告類型返回對應的CSS類別
// const getTagClass = (type: string) => {
//   switch (type) {
//     case 'system':
//       return 'tag-system';
//     case 'maintenance':
//       return 'tag-maintenance';
//     default:
//       return '';
//   }
// };

// 根據公告類型返回一般狀態的顏色
const getTagColor = (type: string) => {
  switch (type) {
    case 'system':
      return 'light-blue';
    case 'maintenance':
      return 'deep-orange';
    default:
      return 'grey';
  }
};

// 根據公告類型返回懸停狀態的顏色
const getHoverTagColor = (type: string) => {
  switch (type) {
    case 'system':
      return 'light-blue-darken-2';
    case 'maintenance':
      return 'deep-orange-darken-2';
    default:
      return 'grey-darken-2';
  }
};

// 獲取卡片懸停樣式
const getCardStyles = (isHovering: boolean) => {
  if (isHovering) {
    return {
      backgroundColor: '#E0F2F1',
      color: '#03A9F4',
      borderLeft: '3px solid #2a8a89',
      borderColor: '#E0F2F1',
      cursor: 'pointer'
    };
  }
  return {
    borderColor: '#5BC2C1',
    cursor: 'pointer'
  };
};

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
/* 添加特定樣式以處理懸停時的標籤 */
.chip-hover {
  background-color: white !important;
  border: thin solid currentColor !important;
}

.section-title {
  color: #2F4D7B;
  font-weight: 900;
  font-size: 28px;
  position: relative;
  padding-bottom: 8px;
  margin-bottom: 16px;
  letter-spacing: -0.5px;
}

.section-title:after {
  content: '';
  position: absolute;
  left: 0;
  bottom: 0;
  height: 4px;
  width: 60px;
  background-color: #5BC2C1;
  border-radius: 2px;
}

.position-relative {
  position: relative;
}

.position-absolute {
  position: absolute;
}

/* 公告項目樣式 */
.announcement-list {
  padding: 10px 0;
}

.announcement-item {
  transition: all 0.2s ease;
  margin-bottom: 10px;
}

.announcement-time {
  min-width: 200px;
  font-size: 20px;
  font-weight: 500;
  transition: color 0.2s ease;
}

.announcement-content {
  font-size: 20px;
  font-weight: 500;
  transition: color 0.2s ease;
}

.announcement-icon {
  opacity: 0;
  transform: translateX(-10px);
  transition: all 0.3s ease;
}

.announcement-item:hover .announcement-icon {
  opacity: 1;
  transform: translateX(0);
}

.more-btn {
  font-weight: 500;
}

/* 文件項目樣式 */
.document-item {
  border-bottom: 1px solid rgba(0, 0, 0, 0.08);
  transition: background-color 0.2s ease;
  padding: 12px;
}

/* .document-item:hover {
  background-color: #f5f5f5;
  cursor: pointer;
} */

.document-item:last-child {
  border-bottom: none;
}

.document-date {
  min-width: 80px;
  font-size: 16px;
  margin-right: 12px;
}

.document-name {
  font-size: 18px;
  font-weight: 500;
}

/* 預算項目樣式 */
.budget-item {
  /* border-bottom: 1px solid rgba(0, 0, 0, 0.08); */
  transition: background-color 0.2s ease;
  padding: 12px;
}

/* .budget-item:hover {
  background-color: #f5f5f5;
  cursor: pointer;
} */

.budget-item:last-child {
  border-bottom: none;
}

.budget-year {
  min-width: 95px;
  font-size: 16px;
  margin-right: 12px;
}

.budget-name {
  font-size: 18px;
  font-weight: 500;
}
</style>
