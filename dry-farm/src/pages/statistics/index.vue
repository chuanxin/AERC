<template>
  <v-container
    fluid
    class="material-container px-6 pb-0 pt-0"
    style="background-color: white"
  >
    <v-row justify="center">
      <v-col
        cols="12"
        md="3"
        align-self="center"
        class="pt-0"
      >
        <div class="d-flex flex-wrap align-center pr-2 pt-11" />

        <div class="section-wrapper">
          <!-- 左側查詢條件面板 -->
          <v-card class="mb-4 section-card">
            <v-card-title class="custom-title d-flex align-center py-2 px-4">
              <v-icon
                class="me-2"
                size="small"
              >
                mdi-file-document-multiple
              </v-icon>
              <span class="text-h5 font-weight-black">統計報表查詢</span>
            </v-card-title>

            <v-card-text class="pa-3">
              <v-tabs
                v-model="activeTab"
                color="primary"
                density="compact"
                class="mb-3"
              >
                <v-tab value="category">
                  表單種類查詢
                </v-tab>
                <v-tab value="detail">
                  案件查詢
                </v-tab>
              </v-tabs>

              <v-window v-model="activeTab">
                <!-- 表單種類查詢標籤內容 -->
                <v-window-item value="category">
                  <div class="py-2">
                    <div class="text-body-2 font-weight-medium mb-2">
                      表單種類
                    </div>
                    <v-select
                      v-model="formCategory"
                      :items="formCategories"
                      label="請選擇表單種類"
                      variant="outlined"
                      density="compact"
                      hide-details
                      class="mb-3"
                    />

                    <div class="text-body-2 font-weight-medium mb-2">
                      關鍵字
                    </div>
                    <div class="d-flex mb-3">
                      <v-text-field
                        v-model="keyword"
                        label="請輸入"
                        variant="outlined"
                        density="compact"
                        hide-details
                        class="flex-grow-1"
                      />
                    </div>

                    <div class="text-body-2 font-weight-medium mb-2">
                      選擇報表格式
                    </div>
                    <v-select
                      v-model="exportFormat"
                      :items="getExportFormats"
                      label="請選擇"
                      variant="outlined"
                      density="compact"
                      hide-details
                      class="mb-3"
                    />

                    <div class="d-flex mt-4">
                      <v-btn
                        color="grey-lighten-1"
                        variant="tonal"
                        size="small"
                        class="me-2"
                        @click="resetForm"
                      >
                        清除全部
                      </v-btn>
                      <v-btn
                        color="primary"
                        variant="elevated"
                        size="small"
                        :loading="isLoading"
                        @click="search"
                      >
                        查詢
                      </v-btn>
                    </div>
                  </div>
                </v-window-item>

                <!-- 案件查詢標籤內容 -->
                <v-window-item value="detail">
                  <div class="py-2">
                    <div class="text-body-2 font-weight-medium mb-2">
                      案件關鍵字
                    </div>
                    <div class="d-flex mb-3">
                      <v-text-field
                        v-model="caseKeyword"
                        label="請輸入案號或申請人姓名"
                        variant="outlined"
                        density="compact"
                        hide-details
                        class="flex-grow-1"
                      />
                    </div>

                    <div class="text-body-2 font-weight-medium mb-2">
                      申請日期範圍
                    </div>
                    <div class="d-flex align-center mb-3">
                      <v-text-field
                        v-model="dateFrom"
                        label="起始日期"
                        type="date"
                        variant="outlined"
                        density="compact"
                        hide-details
                        class="me-2"
                      />
                      <span class="mx-2">～</span>
                      <v-text-field
                        v-model="dateTo"
                        label="結束日期"
                        type="date"
                        variant="outlined"
                        density="compact"
                        hide-details
                      />
                    </div>

                    <div class="text-body-2 font-weight-medium mb-2">
                      案件狀態
                    </div>
                    <v-select
                      v-model="caseStatus"
                      :items="caseStatuses"
                      label="請選擇"
                      variant="outlined"
                      density="compact"
                      hide-details
                      class="mb-3"
                    />

                    <div class="d-flex mt-4">
                      <v-btn
                        color="grey-lighten-1"
                        variant="tonal"
                        size="small"
                        class="me-2"
                        @click="resetCaseForm"
                      >
                        清除全部
                      </v-btn>
                      <v-btn
                        color="primary"
                        variant="elevated"
                        size="small"
                        :loading="isCaseLoading"
                        @click="searchCase"
                      >
                        查詢
                      </v-btn>
                    </div>
                  </div>
                </v-window-item>
              </v-window>
            </v-card-text>
          </v-card>
        </div>
      </v-col>

      <v-col
        cols="12"
        md="9"
      >
        <div class="section-wrapper">
          <!-- 右側查詢結果面板 -->
          <v-card class="mb-4 section-card">
            <v-card-text
              v-if="!selectedReport"
              class="pa-0"
            >
              <div
                class="d-flex flex-column align-center justify-center"
                style="height: 300px;"
              >
                <v-img

                  width="120"
                  class="mb-3"
                />
                <div class="text-body-1 text-grey-darken-1">
                  請點選左側查詢條件
                </div>
                <div class="text-body-2 text-grey">
                  並按下查詢按鈕!
                </div>
              </div>
            </v-card-text>

            <template v-if="selectedReport">
              <v-card-title class="custom-title bg-light-blue-lighten-4 d-flex align-center justify-space-between py-2 px-4">
                <div class="d-flex align-center">
                  <v-icon
                    class="me-2"
                    size="small"
                  >
                    mdi-file-chart
                  </v-icon>
                  <span class="text-subtitle-1 font-weight-medium">{{ selectedReport.title }}</span>
                  <v-icon
                    v-if="selectedReport.dropdown"
                    class="ms-1"
                    size="small"
                  >
                    mdi-chevron-down
                  </v-icon>
                </div>

                <v-btn
                  v-if="selectedReport.canExport"
                  color="primary"
                  variant="text"
                  size="small"
                  prepend-icon="mdi-download"
                  @click="exportToExcel"
                >
                  下載此報表(PDF/Excel)
                </v-btn>
              </v-card-title>

              <v-card-text
                v-if="selectedReport.hasQueryForm"
                class="pa-3"
              >
                <div class="bg-yellow-lighten-5 pa-3 rounded mb-3">
                  <div class="d-flex flex-wrap align-center">
                    <span class="text-body-2 font-weight-medium me-2">年份：</span>
                    <v-select
                      v-model="reportYear"
                      :items="yearOptions"
                      label="年份"
                      variant="outlined"
                      density="compact"
                      hide-details
                      class="me-4"
                      style="width: 120px"
                    />

                    <span class="text-body-2 font-weight-medium me-2">縣市：</span>
                    <v-select
                      v-model="reportCounty"
                      :items="counties"
                      label="縣市"
                      variant="outlined"
                      density="compact"
                      hide-details
                      class="me-4"
                      style="width: 120px"
                    />

                    <v-btn
                      color="primary"
                      variant="elevated"
                      size="small"
                      :loading="isReportLoading"
                      @click="searchReport"
                    >
                      <v-icon
                        size="small"
                        class="me-1"
                      >
                        mdi-magnify
                      </v-icon>
                      查詢
                    </v-btn>
                  </div>
                </div>

                <div
                  v-if="selectedReport.hasRangeQuery"
                  class="bg-yellow-lighten-5 pa-3 rounded mb-3"
                >
                  <div class="d-flex flex-wrap align-center">
                    <span class="text-body-2 font-weight-medium me-2">申請月份：</span>
                    <div class="d-flex align-center">
                      <v-text-field
                        v-model="reportParameters.startMonth"
                        label="起始月份"
                        variant="outlined"
                        density="compact"
                        hide-details
                        class="me-2"
                        style="width: 100px"
                      />
                      <span class="mx-1">～</span>
                      <v-text-field
                        v-model="reportParameters.endMonth"
                        label="結束月份"
                        variant="outlined"
                        density="compact"
                        hide-details
                        style="width: 100px"
                      />
                    </div>
                  </div>
                </div>
              </v-card-text>

              <v-tabs
                v-if="selectedReport.hasTabs"
                v-model="reportTab"
                density="compact"
                class="px-3"
                color="primary"
              >
                <v-tab
                  v-for="(tab, index) in selectedReport.tabs"
                  :key="index"
                  :value="tab.value"
                >
                  {{ tab.label }}
                  <v-icon
                    v-if="tab.icon"
                    size="small"
                    :class="tab.icon === 'up' ? 'ms-1' : 'ms-1'"
                  >
                    {{ tab.icon === 'up' ? 'mdi-chevron-up' : 'mdi-chevron-down' }}
                  </v-icon>
                </v-tab>
              </v-tabs>

              <v-divider v-if="selectedReport.hasTabs" />

              <v-window
                v-if="selectedReport.hasTabs"
                v-model="reportTab"
              >
                <v-window-item
                  v-for="(tab, index) in selectedReport.tabs"
                  :key="index"
                  :value="tab.value"
                >
                  <div
                    v-if="tab.value === 'table1'"
                    class="pa-3"
                  >
                    <v-table
                      class="mb-3 elevation-1"
                      density="compact"
                    >
                      <thead>
                        <tr>
                          <th
                            class="text-center"
                            style="width: 80px"
                          >
                            申請年度
                          </th>
                          <th class="text-center">
                            案號
                          </th>
                          <th>申請人姓名</th>
                          <th>案件狀態</th>
                          <th>總計</th>
                        </tr>
                      </thead>
                      <tbody>
                        <tr>
                          <td class="text-center">
                            113
                          </td>
                          <td class="text-center">
                            11310100001
                          </td>
                          <td>王家一</td>
                          <td>完成</td>
                          <td>1</td>
                        </tr>
                      </tbody>
                    </v-table>
                  </div>

                  <div
                    v-if="tab.value === 'table2'"
                    class="pa-3"
                  >
                    <v-table
                      class="mb-3 elevation-1"
                      density="compact"
                    >
                      <thead>
                        <tr>
                          <th
                            class="text-center"
                            style="width: 80px"
                          >
                            年度
                          </th>
                          <th class="text-center">
                            期間
                          </th>
                          <th>累計件數</th>
                          <th>核准件數</th>
                          <th>駁回件數</th>
                        </tr>
                      </thead>
                      <tbody>
                        <tr>
                          <td class="text-center">
                            113
                          </td>
                          <td class="text-center">
                            1月-3月
                          </td>
                          <td>10</td>
                          <td>8</td>
                          <td>2</td>
                        </tr>
                        <tr>
                          <td class="text-center">
                            113
                          </td>
                          <td class="text-center">
                            4月-6月
                          </td>
                          <td>15</td>
                          <td>12</td>
                          <td>3</td>
                        </tr>
                      </tbody>
                    </v-table>
                  </div>

                  <div
                    v-for="(list, listIndex) in selectedReport.lists"
                    v-if="tab.value === `list${listIndex+1}`"
                    :key="`list-${listIndex}`"
                    class="pa-2"
                  >
                    <v-list
                      density="compact"
                      class="pa-0 elevation-1"
                    >
                      <v-list-item
                        v-for="(item, i) in list.items"
                        :key="`item-${i}`"
                        :class="{'bg-yellow-lighten-5': i % 2 === 0}"
                        density="compact"
                        @click="selectReportItem(item)"
                      >
                        <v-list-item-title class="text-body-2">
                          {{ `${i+1}. ${item.title}` }}
                        </v-list-item-title>
                      </v-list-item>
                    </v-list>
                  </div>
                </v-window-item>
              </v-window>

              <v-card-text
                v-if="!selectedReport.hasTabs && selectedReport.content"
                class="pa-3"
              >
                <!-- 報表內容 -->
                <component :is="selectedReport.content" />
              </v-card-text>
            </template>
          </v-card>
        </div>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch } from 'vue';

// 查詢相關
const activeTab = ref('category');
const formCategory = ref<number | ''>('');
const keyword = ref('');
const exportFormat = ref('');
const caseKeyword = ref('');
const dateFrom = ref('');
const dateTo = ref('');
const caseStatus = ref('');
const isLoading = ref(false);
const isCaseLoading = ref(false);

// 報表相關
const selectedReport = ref<null | Record<string, any>>(null);
const reportTab = ref('table1');
const reportYear = ref('113年');
const reportCounty = ref('');
const isReportLoading = ref(false);

// 報表查詢參數
const reportParameters = reactive({
  startMonth: '',
  endMonth: ''
});

// 表單種類選項
const formCategories = [
  { title: '公告資訊 / 執行進度一覽', value: 0 },
  { title: '年度 / 月份統計報表', value: 1 },
  { title: '原民區域之統計', value: 2 },
  // { title: '歷年統計查詢', value: '歷年統計查詢' },
  // { title: '其他表單', value: '其他表單' },
];

// 動態報表格式選項 - 根據 formCategory 的值變化
const getExportFormats = computed(() => {
  switch (formCategory.value) {
    default: // 公告資訊 / 執行進度一覽
      return [
        { title: '年度管理處辦理情形(本年度執行進度表)', value: 'yearly-management-progress' },
        { title: '各受理單位經費統計表 (113年)', value: 'unit-budget-stats-113' },
        { title: '各補助款經費來源(農水署、七星及瑠公)分別列出統計表', value: 'funding-sources-detailed' },
        { title: '工程決算表(農田水利設施更新改善計畫)', value: 'engineering-settlement-plan' },
        { title: '成果統計表', value: 'achievement-stats' },
        { title: '全國歷年成果統計表', value: 'national-historical-achievements' },
        { title: '管理處歷年統計表', value: 'management-historical-stats' }
      ];
    case 1: // 年度 / 月份統計報表
      return [
        { title: '管理處灌區內外推動統計表', value: 'management-irrigation-promotion' },
        { title: '縣市灌區內外統計表', value: 'county-irrigation-stats' },
        { title: '農田水利灌溉服務區域內外統計表 -- 100~113年農田水利灌溉服務區域內外統計表9月(最新)', value: 'irrigation-service-area-stats' },
        { title: '農作物統計表', value: 'crop-statistics' },
        { title: '鄉鎮經費統計表(113年到現在為止，共產出50頁)', value: 'township-budget-stats-113' },
        { title: '設施面積及補助金額統計表', value: 'facility-area-subsidy-stats' },
        { title: '鄉鎮設施面積及補助金額統計表', value: 'township-facility-area-subsidy' },
        { title: '縣市設施面積及補助金額統計表', value: 'county-facility-area-subsidy' }
      ];
    case 2: // 原民區域之統計
      return [
        { title: '年度原民鄉鎮區域補助情形', value: 'indigenous-township-subsidy-status' },
        { title: '年度原民區域補助管理處辦理情形', value: 'indigenous-management-subsidy-status' },
        { title: '原民區域統計', value: 'indigenous-area-statistics' }
      ];
  }
});

// 案件狀態選項
const caseStatuses = [
  { title: '已送出', value: 'submitted' },
  { title: '審核中', value: 'reviewing' },
  { title: '已核准', value: 'approved' },
  { title: '已駁回', value: 'rejected' }
];

// 年份選項
const yearOptions = [
  '113年', '112年', '111年', '110年'
];

// 縣市選項
const counties = [
  '臺北市', '新北市', '基隆市', '桃園市', '新竹市', '新竹縣', '苗栗縣',
  '臺中市', '彰化縣', '南投縣', '雲林縣', '嘉義市', '嘉義縣', '臺南市',
  '高雄市', '屏東縣', '宜蘭縣', '花蓮縣', '臺東縣', '澎湖縣', '金門縣', '連江縣'
];

// 報表清單資料 - 根據圖片內容處理
const reportGroups = reactive([
  {
    title: '公告資訊',
    dropdown: true,
    canExport: true,
    hasQueryForm: false,
    hasTabs: false,
    lists: []
  },
  {
    title: '年度月份統計報表',
    dropdown: true,
    canExport: true,
    hasQueryForm: true,
    hasTabs: true,
    tabs: [
      { label: '各報表格式', value: 'list1', icon: 'down' }
    ],
    lists: [
      {
        items: [
          { title: '公告資訊', value: 'announcement' },
          { title: '年度月份統計報表', value: 'monthly-stats' },
          { title: '年度管理成與理財預期(各年度執行進度表)', value: 'yearly-financial' },
          { title: '113年度辦理補助設施調查統計', value: 'facility-113' },
          { title: '各管理單位經費統計表 (113年)', value: 'unit-stats-113' },
          { title: '各補助款經費來源(農水署、七星及瑠公)', value: 'funding-sources' },
          { title: '附件統計表 (113年到現在為止，共處理40筆)', value: 'attachment-stats-113' },
          { title: '工程決算表 (農田水利設施更新改善計劃)', value: 'engineering-settlement' },
          { title: '預算統計表', value: 'budget-stats' },
          { title: '管理處歷年統計表', value: 'historical-stats' }
        ]
      }
    ]
  },
  {
    title: '年度月份統計報表',
    dropdown: true,
    canExport: true,
    hasQueryForm: true,
    hasRangeQuery: true,
    hasTabs: true,
    tabs: [
      { label: '一、年度原民區補助調整報表', value: 'table1', icon: 'down' },
      { label: '二、年度原民區轄內處理或調理情形', value: 'table2', icon: 'down' }
    ]
  },
  {
    title: '附件表單之獨立下載',
    dropdown: true,
    canExport: true,
    hasQueryForm: false,
    hasTabs: true,
    tabs: [
      { label: '四、填妥簽章', value: 'list2', icon: 'down' }
    ],
    lists: [
      {
        items: [
          { title: '農田水灌溉設施輔導申請書 (113年到現在為止，共處理40筆)', value: 'irrigation-application' },
          { title: '其他報表示例', value: 'other-reports' }
        ]
      }
    ]
  },
  {
    title: '歷年統計查詢',
    dropdown: true,
    canExport: true,
    hasQueryForm: false,
    hasTabs: true,
    tabs: [
      { label: '五、歷年統計查詢', value: 'list3', icon: 'down' }
    ],
    lists: [
      {
        items: [
          { title: '4.灌溉區域土地補助統計表', value: 'irrigation-land-stats' },
          { title: '5.都市區域內外統計表', value: 'urban-rural-stats' },
          { title: '6.55限民團統計', value: 'limit-55-stats' },
          { title: '7.農田水利灌溉設備補助件數外移共計 - 100~113年農田水利灌諜設備離場外統計表99筆(農測)', value: 'irrigation-equipment-stats' },
          { title: '28. 農作物統計表', value: 'crop-stats' }
        ]
      }
    ]
  }
]);

// 監聽 formCategory 變更，清空 exportFormat
watch(formCategory, () => {
  exportFormat.value = '';
});

// 清空查詢表單
const resetForm = () => {
  formCategory.value = '';
  keyword.value = '';
  exportFormat.value = '';
};

// 清空案件查詢表單
const resetCaseForm = () => {
  caseKeyword.value = '';
  dateFrom.value = '';
  dateTo.value = '';
  caseStatus.value = '';
};

// 執行表單種類查詢
const search = async () => {
  isLoading.value = true;

  try {
    // 模擬 API 請求延遲
    await new Promise(resolve => setTimeout(resolve, 800));

    // 根據選擇的表單種類設置結果
    if (formCategory.value !== '') {
      // 根據 formCategory 的 value 找到對應的 reportGroup
      const selectedCategory = formCategories.find(cat => cat.value === formCategory.value);
      if (selectedCategory) {
        const reportGroup = reportGroups.find(group => group.title === selectedCategory.title);
        if (reportGroup) {
          selectedReport.value = reportGroup;

          // 如果有標籤頁，則設置默認標籤頁
          if (reportGroup.hasTabs && reportGroup.tabs && reportGroup.tabs.length) {
            reportTab.value = reportGroup.tabs[0].value;
          }
        }
      }
    }

  } catch (error) {
    console.error('查詢失敗:', error);
  } finally {
    isLoading.value = false;
  }
};

// 執行案件查詢
const searchCase = async () => {
  isCaseLoading.value = true;

  try {
    // 模擬 API 請求延遲
    await new Promise(resolve => setTimeout(resolve, 800));

    // 實際應用中，這裡應該進行真實的案件查詢
    selectedReport.value = {
      title: '案件查詢結果',
      canExport: true,
      hasQueryForm: false,
      hasTabs: true,
      tabs: [
        { label: '查詢結果', value: 'table1' }
      ]
    };

    reportTab.value = 'table1';

  } catch (error) {
    console.error('查詢失敗:', error);
  } finally {
    isCaseLoading.value = false;
  }
};

// 執行報表內部查詢
const searchReport = async () => {
  isReportLoading.value = true;

  try {
    // 模擬 API 請求延遲
    await new Promise(resolve => setTimeout(resolve, 800));

    // 實際應用中，這裡應該根據報表的不同參數進行查詢
    // 查詢成功後會自動顯示結果，此處模擬已顯示結果

  } catch (error) {
    console.error('報表查詢失敗:', error);
  } finally {
    isReportLoading.value = false;
  }
};

// 選擇報表項目
const selectReportItem = (item: Record<string, any>) => {
  // 根據選擇的報表項目進行處理
  console.log('選擇報表項目:', item);
};

// 匯出報表
const exportToExcel = () => {
  // 實際應用中，這裡應該實現匯出功能
  console.log('匯出報表');
};

// 頁面初始化
onMounted(() => {
  // 如果需要，可以在頁面載入時進行初始化操作
});
</script>

<style scoped>
/* 添加背景圖片樣式 */
.material-container {
  background-image: url('@/assets/bg_index.svg');
  background-size: cover;
  background-position: center bottom;
  background-repeat: no-repeat;
  background-attachment: fixed;
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
  background-color: rgba(255, 255, 255, 0.6) !important;
  backdrop-filter: blur(10px) !important;
  -webkit-backdrop-filter: blur(10px) !important;
  border: 1px solid rgba(255, 255, 255, 0.25) !important;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.05) !important;
}

.section-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08) !important;
  background-color: rgba(255, 255, 255, 0.85) !important;
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
  min-width: 200px;
  height: 50px;
  background-color: #3ea0a3 !important;
  border-radius: 8px 8px 0 0;
  z-index: 1;
  transition: all 0.3s ease;
  color: white !important;
  display: flex;
  justify-content: flex-start;
  align-items: center;
}

.custom-title .text-subtitle-1 {
  color: white !important;
}

/* 原有樣式保持 */
.bg-light-blue-lighten-4 {
  background-color: #B3E5FC !important; /* 使用與補助申請頁面一致的顏色 */
}

.bg-yellow-lighten-5 {
  background-color: #FFFDE7 !important;
}

.font-weight-medium {
  font-weight: 500 !important;
}

.font-weight-bold {
  font-weight: 700 !important;
}

/* 表單與卡片間距調整 */
.v-card-text {
  padding: 16px !important;
}

/* 統一表格樣式 */
.v-table {
  border: 1px solid rgba(0, 0, 0, 0.12);
}

.v-table th {
  font-weight: 600;
  color: rgba(0, 0, 0, 0.7);
  background-color: #f5f5f5;
}

/* 清單項目樣式 */
.v-list-item {
  border-bottom: 1px solid rgba(0, 0, 0, 0.12);
}

.v-list-item:last-child {
  border-bottom: none;
}

.v-list-item:hover {
  background-color: #f5f5f5;
  cursor: pointer;
}

/* 報表查詢表單樣式 */
.bg-yellow-lighten-5 {
  border-radius: 4px;
  border: 1px solid rgba(255, 193, 7, 0.12);
}
</style>
