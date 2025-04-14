<template>
  <v-container class="pt-0">
    <v-row>
      <v-col cols="12" md="8">
        <!-- 查詢區域 -->
        <v-card class="mb-4">
          <v-card-title class="bg-light-blue-lighten-4 d-flex align-center py-2 px-4">
            <v-icon class="me-2" size="small">mdi-magnify</v-icon>
            <span class="text-subtitle-1 font-weight-medium">重複案件查詢</span>
          </v-card-title>

          <v-card-text class="pa-3">
            <v-form @submit.prevent="searchLand">
              <!-- 查詢表單內容 -->
              <v-row dense>
                <v-col cols="12" md="2" class="d-flex align-center pt-2">
                  <span class="text-body-2 font-weight-medium">查詢類型</span>
                </v-col>
                <v-col cols="12" md="10">
                  <v-btn-toggle
                    v-model="queryType"
                    color="primary"
                    mandatory
                    density="comfortable"
                    rounded="lg"
                    class="mb-2"
                  >
                    <v-btn value="general" size="small">一般區域</v-btn>
                    <v-btn value="indigenous" size="small">原民區域</v-btn>
                  </v-btn-toggle>
                </v-col>
              </v-row>

              <v-expand-transition>
                <div v-if="queryType === 'general'">
                  <v-row dense>
                    <v-col cols="12" md="2" class="d-flex align-center">
                      <span class="text-body-2 font-weight-medium">地段</span>
                    </v-col>
                    <v-col cols="12" md="10">
                      <div class="d-flex flex-wrap">
                        <v-select
                          v-model="searchParams.county"
                          :items="counties"
                          label="縣市"
                          variant="outlined"
                          density="compact"
                          hide-details
                          class="me-2 mb-2"
                          style="width: 120px"
                          @update:model-value="onCountyChange"
                        ></v-select>

                        <v-select
                          v-model="searchParams.town"
                          :items="towns"
                          label="鄉鎮市區"
                          variant="outlined"
                          density="compact"
                          hide-details
                          class="me-2 mb-2"
                          style="width: 140px"
                          :disabled="!searchParams.county"
                          @update:model-value="onTownChange"
                        ></v-select>

                        <v-select
                          v-model="searchParams.section"
                          :items="sections"
                          label="地段"
                          variant="outlined"
                          density="compact"
                          hide-details
                          class="mb-2"
                          style="width: 140px"
                          :disabled="!searchParams.town"
                        ></v-select>
                      </div>
                    </v-col>
                  </v-row>

                  <v-row dense>
                    <v-col cols="12" md="2" class="d-flex align-center">
                      <span class="text-body-2 font-weight-medium">地號</span>
                    </v-col>
                    <v-col cols="12" md="10">
                      <div class="d-flex align-center">
                        <v-text-field
                          v-model="searchParams.landNumber"
                          label="範例：1-1 或 1"
                          variant="outlined"
                          density="compact"
                          hide-details
                          class="me-2"
                          style="max-width: 200px"
                        ></v-text-field>

                        <v-btn
                          color="primary"
                          variant="elevated"
                          size="small"
                          type="submit"
                          :loading="isLoading"
                          :disabled="!canSearch"
                        >
                          <v-icon size="small" class="me-1">mdi-magnify</v-icon>
                          查詢
                        </v-btn>
                      </div>
                    </v-col>
                  </v-row>

                  <v-row dense v-if="showAlert">
                    <v-col cols="12" md="2"></v-col>
                    <v-col cols="12" md="10">
                      <v-alert
                        type="warning"
                        variant="tonal"
                        color="red"
                        class="mt-2"
                        border="start"
                        density="compact"
                        icon="mdi-alert-circle"
                      >
                        包含農田水利署及農村發展及水土保持署之案件皆會篩選，是否重複申請。
                      </v-alert>
                    </v-col>
                  </v-row>
                </div>
              </v-expand-transition>

              <v-expand-transition>
                <div v-if="queryType === 'indigenous'">
                  <v-row dense>
                    <v-col cols="12" md="2" class="d-flex align-center">
                      <span class="text-body-2 font-weight-medium">地段</span>
                    </v-col>
                    <v-col cols="12" md="10">
                      <div class="d-flex flex-wrap align-center">
                        <v-select
                          v-model="indigenousParams.county"
                          :items="counties"
                          label="縣市"
                          variant="outlined"
                          density="compact"
                          hide-details
                          class="me-2 mb-2"
                          style="width: 120px"
                          @update:model-value="onIndigenousCountyChange"
                        ></v-select>

                        <v-select
                          v-model="indigenousParams.town"
                          :items="indigenousTowns"
                          label="鄉鎮市區"
                          variant="outlined"
                          density="compact"
                          hide-details
                          class="me-2 mb-2"
                          style="width: 140px"
                          :disabled="!indigenousParams.county"
                        ></v-select>

                        <v-btn
                          color="primary"
                          variant="elevated"
                          size="small"
                          :loading="isIndigenousLoading"
                          :disabled="!canSearchIndigenous"
                          @click="searchIndigenous"
                        >
                          <v-icon size="small" class="me-1">mdi-magnify</v-icon>
                          查詢
                        </v-btn>

                        <v-btn
                          variant="text"
                          color="primary"
                          size="small"
                          class="ms-2"
                          @click="indigenousDialog = true"
                        >
                          原民鄉清單
                        </v-btn>
                      </div>
                    </v-col>
                  </v-row>

                  <v-row dense v-if="isIndigenousAreaChecked">
                    <v-col cols="12" md="2"></v-col>
                    <v-col cols="12" md="10">
                      <div class="d-flex align-center mt-2">
                        <v-chip
                          :color="isIndigenousArea ? 'red-darken-2' : 'grey'"
                          :text-color="isIndigenousArea ? 'white' : ''"
                          size="small"
                          class="me-2"
                        >
                          {{ isIndigenousArea ? '是' : '非' }} 原民鄉
                        </v-chip>

                        <span class="text-body-2">
                          {{ indigenousParams.county || '___' }} {{ indigenousParams.town || '___' }}
                        </span>
                      </div>
                    </v-col>
                  </v-row>
                </div>
              </v-expand-transition>
            </v-form>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" md="4">
        <!-- 查詢說明區域 -->
        <v-card class="mb-4">
          <v-card-title class="bg-light-blue-lighten-4 d-flex align-center py-2 px-4">
            <v-icon class="me-2" size="small">mdi-information</v-icon>
            <span class="text-subtitle-1 font-weight-medium">查詢說明</span>
          </v-card-title>

          <v-card-text class="pa-3">
            <v-list density="compact" class="bg-transparent pa-0">
              <v-list-item prepend-icon="mdi-check-circle" class="px-1">
                <v-list-item-title class="text-body-2">查詢前請確認地段與地號資訊</v-list-item-title>
              </v-list-item>
              <v-list-item prepend-icon="mdi-check-circle" class="px-1">
                <v-list-item-title class="text-body-2">可查詢該地號是否已有補助申請紀錄</v-list-item-title>
              </v-list-item>
              <v-list-item prepend-icon="mdi-check-circle" class="px-1">
                <v-list-item-title class="text-body-2">若為原民區域請選擇原民區域查詢</v-list-item-title>
              </v-list-item>
              <v-list-item prepend-icon="mdi-check-circle" class="px-1">
                <v-list-item-title class="text-body-2">查詢結果會顯示已申請面積與剩餘可申請面積</v-list-item-title>
              </v-list-item>
            </v-list>
          </v-card-text>
        </v-card>

        <!-- 最近查詢區域 (選擇性功能) -->
        <v-card class="mb-4">
          <v-card-title class="bg-grey-lighten-3 d-flex align-center py-2 px-4">
            <v-icon class="me-2" size="small">mdi-history</v-icon>
            <span class="text-subtitle-1 font-weight-medium">最近查詢</span>
          </v-card-title>

          <v-card-text class="pa-0">
            <v-list lines="two" density="compact">
              <v-list-item
                v-for="(item, index) in recentSearches"
                :key="index"
                @click="loadRecentSearch(item)"
              >
                <v-list-item-title>
                  {{ item.county }}{{ item.town }} {{ item.landNumber || item.section }}
                </v-list-item-title>
                <v-list-item-subtitle class="text-caption">
                  {{ formatDate(item.searchTime) }}
                </v-list-item-subtitle>
              </v-list-item>

              <v-list-item v-if="recentSearches.length === 0">
                <v-list-item-title class="text-body-2 text-grey">
                  尚無查詢紀錄
                </v-list-item-title>
              </v-list-item>
            </v-list>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- 查詢結果顯示區域 -->
    <v-expand-transition>
      <v-card v-if="searchResults.length > 0 || showNoResultMessage" class="mb-4" variant="outlined">
        <v-card-title class="bg-light-blue-lighten-4 d-flex align-center py-2 px-4">
          <v-icon class="me-2" size="small">mdi-file-search</v-icon>
          <span class="text-subtitle-1 font-weight-medium">查詢結果</span>
        </v-card-title>

        <v-card-text class="pa-4">
          <!-- 有查詢結果 -->
          <v-sheet v-if="searchResults.length > 0" class="rounded pa-3 mb-4" color="blue-lighten-5">
            <div v-for="(result, index) in searchResults" :key="index" class="mb-2">
              <div class="text-body-2">
                <span class="font-weight-medium">{{ result.year }}年度</span>
                【{{ result.department }}】申請補助
                <span class="font-weight-medium">案號【{{ result.caseNumber }}】</span>
                申請人【{{ result.applicant }}】
              </div>
              <div class="d-flex justify-space-between text-body-2 mb-2">
                <div>
                  <span v-if="result.waterUsage" class="me-4">灌水設備{{ result.waterUsage }}㎡</span>
                  <span v-if="result.powerEquipment" class="me-4">動力設備{{ result.powerEquipment }}㎡</span>
                  <span v-if="result.fieldPipeline" class="me-4">田間管路{{ result.fieldPipeline }}㎡</span>
                </div>
              </div>
              <v-divider v-if="index < searchResults.length - 1" class="mb-2"></v-divider>
            </div>

            <!-- 土地面積統計區域 -->
            <v-divider class="mb-3 mt-2"></v-divider>

            <v-row dense>
              <v-col cols="12" sm="6" md="4">
                <v-card flat color="transparent" class="px-2 py-1">
                  <v-card-subtitle class="pa-0 pb-1 text-caption">設查詢地號總面積</v-card-subtitle>
                  <v-card-text class="pa-0 text-body-1 font-weight-medium">{{ landTotalArea }} ㎡</v-card-text>
                </v-card>
              </v-col>

              <v-col cols="12" sm="6" md="4">
                <v-card flat color="transparent" class="px-2 py-1">
                  <v-card-subtitle class="pa-0 pb-1 text-caption">已經補助申請設施面積</v-card-subtitle>
                  <v-card-text class="pa-0 text-body-1 font-weight-medium">{{ usedArea }} ㎡</v-card-text>
                </v-card>
              </v-col>

              <v-col cols="12" sm="6" md="4">
                <v-card flat color="transparent" class="px-2 py-1">
                  <v-card-subtitle class="pa-0 pb-1 text-caption">剩餘申請面積</v-card-subtitle>
                  <v-card-text class="pa-0 text-body-1 font-weight-medium">{{ remainingArea }} ㎡</v-card-text>
                </v-card>
              </v-col>

              <v-col cols="12" sm="6" md="4">
                <v-card flat color="transparent" class="px-2 py-1">
                  <v-card-subtitle class="pa-0 pb-1 text-caption">已經補助微灌設施面積</v-card-subtitle>
                  <v-card-text class="pa-0 text-body-1 font-weight-medium">{{ microIrrigationArea }} ㎡</v-card-text>
                </v-card>
              </v-col>

              <v-col cols="12" sm="6" md="4">
                <v-card flat color="transparent" class="px-2 py-1">
                  <v-card-subtitle class="pa-0 pb-1 text-caption">剩餘申請面積</v-card-subtitle>
                  <v-card-text class="pa-0 text-body-1 font-weight-medium">{{ remainingMicroArea }} ㎡</v-card-text>
                </v-card>
              </v-col>

              <v-col cols="12" sm="6" md="4">
                <v-card flat color="transparent" class="px-2 py-1">
                  <v-card-subtitle class="pa-0 pb-1 text-caption">已經補助噴水設施面積</v-card-subtitle>
                  <v-card-text class="pa-0 text-body-1 font-weight-medium">{{ sprinklerArea }} ㎡</v-card-text>
                </v-card>
              </v-col>

              <v-col cols="12" sm="6" md="4">
                <v-card flat color="transparent" class="px-2 py-1">
                  <v-card-subtitle class="pa-0 pb-1 text-caption">剩餘申請面積</v-card-subtitle>
                  <v-card-text class="pa-0 text-body-1 font-weight-medium">{{ remainingSprinklerArea }} ㎡</v-card-text>
                </v-card>
              </v-col>
            </v-row>
          </v-sheet>

          <!-- 無查詢結果提示 -->
          <v-alert
            v-if="showNoResultMessage"
            type="info"
            variant="tonal"
            icon="mdi-information"
          >
            <div class="d-flex align-center justify-space-between">
              <span>查詢無結果，此地號尚未有補助申請紀錄，可進行申請。</span>
              <v-btn
                variant="text"
                color="primary"
                size="small"
                to="/grants/new"
              >
                立即申請
                <v-icon end size="small">mdi-arrow-right</v-icon>
              </v-btn>
            </div>
          </v-alert>
        </v-card-text>
      </v-card>
    </v-expand-transition>

    <!-- 原民鄉對話框 -->
    <v-dialog v-model="indigenousDialog" max-width="700px">
      <v-card>
        <v-card-title class="bg-light-blue-lighten-4 py-3 px-4">
          <span class="text-subtitle-1 font-weight-medium">原民鄉清單</span>
        </v-card-title>

        <v-card-text class="pa-4">
          <div class="mb-4">
            <div class="font-weight-medium mb-2">山地鄉(30個)</div>
            <div class="text-body-2 text-wrap">
              臺灣市茂林區、臺灣市桃源區、臺灣市那瑪夏區、新北市烏來區、宜蘭縣大同鄉、
              宜蘭縣南澳鄉、桃園市復興區、新竹縣尖石鄉、新竹縣五峰鄉、苗栗縣泰安鄉、
              臺中市和平區、南投縣信義鄉、南投縣仁愛鄉、嘉義縣阿里山鄉、屏東縣三地門鄉、
              屏東縣霧臺鄉、屏東縣瑪家鄉、屏東縣泰武鄉、屏東縣來義鄉、屏東縣春日鄉、
              屏東縣獅子鄉、屏東縣牡丹鄉、花蓮縣秀林鄉、花蓮縣萬榮鄉、花蓮縣卓溪鄉、
              臺東縣延平鄉、臺東縣海端鄉、臺東縣達仁鄉、臺東縣金峰鄉、臺東縣蘭嶼鄉
            </div>
          </div>

          <div class="mb-4">
            <div class="font-weight-medium mb-2">平地鄉(25個)</div>
            <div class="text-body-2 text-wrap">
              新竹縣關西鎮、苗栗縣南庄鄉、苗栗縣獅潭鄉、南投縣魚池鄉、屏東縣滿州鄉、
              花蓮縣花蓮市、花蓮縣光復鄉、花蓮縣玉里鎮、花蓮縣新城鄉、花蓮縣吉安鄉、
              花蓮縣壽豐鄉、花蓮縣鳳林鎮、花蓮縣豐濱鄉、花蓮縣瑞穗鄉、花蓮縣富里鄉、
              臺東縣台東市、臺東縣成功鎮、臺東縣關山鎮、臺東縣東河鄉、臺東縣太麻里鄉、
              臺東縣大武鄉、臺東縣卑南鄉、臺東縣長濱鄉、臺東縣鹿野鄉、臺東縣池上鄉
            </div>
          </div>
        </v-card-text>

        <v-card-actions class="pa-4">
          <v-spacer></v-spacer>
          <v-btn
            color="primary"
            variant="elevated"
            @click="indigenousDialog = false"
          >
            確定
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup lang="ts">
import { ref, computed, watch, reactive } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();
const queryType = ref('general');

// 控制載入狀態
const isLoading = ref(false);
const isIndigenousLoading = ref(false);
const showAlert = ref(true);
const indigenousDialog = ref(false);
const isIndigenousAreaChecked = ref(false);
const showNoResultMessage = ref(false);

// 地段查詢參數
const searchParams = reactive({
  county: '',
  town: '',
  section: '',
  landNumber: ''
});

// 原民區域查詢參數
const indigenousParams = reactive({
  county: '',
  town: ''
});

// 最近查詢紀錄
const recentSearches = ref([
  {
    county: '嘉義縣',
    town: '竹崎鄉',
    section: '瓦厝埔段',
    landNumber: '1-1',
    searchTime: new Date(2025, 2, 8, 15, 30)
  },
  {
    county: '高雄市',
    town: '美濃區',
    landNumber: '996-1',
    searchTime: new Date(2025, 2, 7, 10, 15)
  },
  {
    county: '屏東縣',
    town: '春日鄉',
    searchTime: new Date(2025, 2, 6, 14, 45)
  }
]);

// 是否可以查詢
const canSearch = computed(() => {
  return !!searchParams.county && !!searchParams.town && !!searchParams.landNumber;
});

// 是否可以進行原民區域查詢
const canSearchIndigenous = computed(() => {
  return !!indigenousParams.county && !!indigenousParams.town;
});

// 地區資料
const counties = [
  '臺北市', '新北市', '基隆市', '桃園市', '新竹市', '新竹縣', '苗栗縣',
  '臺中市', '彰化縣', '南投縣', '雲林縣', '嘉義市', '嘉義縣', '臺南市',
  '高雄市', '屏東縣', '宜蘭縣', '花蓮縣', '臺東縣', '澎湖縣', '金門縣', '連江縣'
];

// 鄉鎮市區資料 (這裡僅做示範，實際應該根據選擇的縣市動態獲取)
const townsMap = {
  '嘉義縣': ['太保市', '朴子市', '布袋鎮', '大林鎮', '民雄鄉', '溪口鄉', '新港鄉', '六腳鄉', '東石鄉', '義竹鄉', '鹿草鄉', '水上鄉', '中埔鄉', '竹崎鄉', '梅山鄉', '番路鄉', '大埔鄉', '阿里山鄉'],
  '高雄市': ['楠梓區', '左營區', '鼓山區', '三民區', '鹽埕區', '前金區', '新興區', '苓雅區', '前鎮區', '旗津區', '小港區', '鳳山區', '大寮區', '鳥松區', '林園區', '仁武區', '大樹區', '大社區', '岡山區', '路竹區', '橋頭區', '梓官區', '彌陀區', '永安區', '燕巢區', '田寮區', '阿蓮區', '茄萣區', '湖內區', '旗山區', '美濃區', '內門區', '杉林區', '甲仙區', '六龜區', '茂林區', '桃源區', '那瑪夏區'],
  '屏東縣': ['屏東市', '潮州鎮', '東港鎮', '恆春鎮', '萬丹鄉', '長治鄉', '麟洛鄉', '九如鄉', '里港鄉', '鹽埔鄉', '高樹鄉', '萬巒鄉', '內埔鄉', '竹田鄉', '新埤鄉', '枋寮鄉', '新園鄉', '崁頂鄉', '林邊鄉', '南州鄉', '佳冬鄉', '琉球鄉', '車城鄉', '滿州鄉', '枋山鄉', '霧臺鄉', '瑪家鄉', '泰武鄉', '來義鄉', '春日鄉', '獅子鄉', '牡丹鄉', '三地門鄉']
  // 其他縣市資料...
};

// 地段資料 (示範用)
const sectionsMap = {
  '竹崎鄉': ['瓦厝埔段', '龍山段', '灣橋段'],
  // 其他地段資料...
};

// 動態獲取鄉鎮選項
const towns = computed(() => {
  if (!searchParams.county) return [];
  return townsMap[searchParams.county] || [];
});

// 動態獲取地段選項
const sections = computed(() => {
  if (!searchParams.town) return [];
  return sectionsMap[searchParams.town] || [];
});

// 動態獲取原民區查詢的鄉鎮選項
const indigenousTowns = computed(() => {
  if (!indigenousParams.county) return [];
  return townsMap[indigenousParams.county] || [];
});

// 是否為原民區域
const isIndigenousArea = ref(false);

// 模擬查詢結果
const searchResults = ref([]);

// 模擬土地面積統計資料
const landTotalArea = ref('2370');
const usedArea = ref('2370');
const remainingArea = ref('0');
const microIrrigationArea = ref('2370');
const remainingMicroArea = ref('0');
const sprinklerArea = ref('1580');
const remainingSprinklerArea = ref('790');

// 格式化日期
const formatDate = (date: Date): string => {
  if (!date) return '';

  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  const hours = String(date.getHours()).padStart(2, '0');
  const minutes = String(date.getMinutes()).padStart(2, '0');

  return `${year}/${month}/${day} ${hours}:${minutes}`;
};

// 縣市變更事件處理
const onCountyChange = () => {
  searchParams.town = '';
  searchParams.section = '';
};

// 鄉鎮變更事件處理
const onTownChange = () => {
  searchParams.section = '';
};

// 原民區縣市變更事件處理
const onIndigenousCountyChange = () => {
  indigenousParams.town = '';
  isIndigenousArea.value = false;
  isIndigenousAreaChecked.value = false;
};

// 載入最近查詢記錄
const loadRecentSearch = (item: any) => {
  if (item.section) {
    // 一般區域查詢
    queryType.value = 'general';
    searchParams.county = item.county;
    searchParams.town = item.town;
    searchParams.section = item.section;
    searchParams.landNumber = item.landNumber || '';
  } else if (item.landNumber) {
    // 一般區域查詢，但沒有地段
    queryType.value = 'general';
    searchParams.county = item.county;
    searchParams.town = item.town;
    searchParams.landNumber = item.landNumber;
  } else {
    // 原民區域查詢
    queryType.value = 'indigenous';
    indigenousParams.county = item.county;
    indigenousParams.town = item.town;
  }
};

// 地段查詢方法
const searchLand = async () => {
  // 檢查必填欄位
  if (!canSearch.value) {
    return;
  }

  isLoading.value = true;
  showNoResultMessage.value = false;
  searchResults.value = [];

  try {
    // 模擬 API 請求
    await new Promise(resolve => setTimeout(resolve, 800));

    // 判斷是否有查詢結果 (隨機模擬)
    const hasResults = Math.random() > 0.3; // 70% 機率有結果

    if (hasResults) {
      // 模擬查詢結果
      searchResults.value = [
        {
          year: '111',
          department: '農業部農田水利署林管理處',
          caseNumber: '1111158',
          applicant: '張樣會',
          waterUsage: '2370',
          powerEquipment: null,
          fieldPipeline: null
        },
        {
          year: '111',
          department: '農業部農田水利署林管理處',
          caseNumber: '1111157',
          applicant: '張樣會',
          waterUsage: null,
          powerEquipment: null,
          fieldPipeline: '790'
        },
        {
          year: '111',
          department: '農業部農田水利署林管理處',
          caseNumber: '1111156',
          applicant: '張樣會',
          waterUsage: null,
          powerEquipment: '1580',
          fieldPipeline: '1580'
        }
      ];

      // 更新面積統計資料 (在實際應用中，這些數據應該從 API 返回)
      landTotalArea.value = '2370';
      usedArea.value = '2370';
      remainingArea.value = '0';
      microIrrigationArea.value = '2370';
      remainingMicroArea.value = '0';
      sprinklerArea.value = '1580';
      remainingSprinklerArea.value = '790';

      // 添加到最近查詢記錄
      addToRecentSearches({
        county: searchParams.county,
        town: searchParams.town,
        section: searchParams.section,
        landNumber: searchParams.landNumber,
        searchTime: new Date()
      });
    } else {
      // 清空查詢結果
      searchResults.value = [];
      // 顯示無結果提示
      showNoResultMessage.value = true;

      // 仍然添加到最近查詢記錄
      addToRecentSearches({
        county: searchParams.county,
        town: searchParams.town,
        section: searchParams.section,
        landNumber: searchParams.landNumber,
        searchTime: new Date()
      });
    }
  } catch (error) {
    console.error('查詢失敗:', error);
  } finally {
    isLoading.value = false;
  }
};

// 原民區域查詢方法
const searchIndigenous = async () => {
  // 檢查必填欄位
  if (!canSearchIndigenous.value) {
    return;
  }

  isIndigenousLoading.value = true;
  searchResults.value = [];
  showNoResultMessage.value = false;

  try {
    // 模擬 API 請求
    await new Promise(resolve => setTimeout(resolve, 800));

    // 檢查是否為原民鄉 (這裡只是示範，實際應該從 API 獲取)
    const indigenousTowns = [
      // 山地鄉
      '茂林區', '桃源區', '那瑪夏區', '烏來區', '大同鄉', '南澳鄉', '復興區', '尖石鄉', '五峰鄉', '泰安鄉',
      '和平區', '信義鄉', '仁愛鄉', '阿里山鄉', '三地門鄉', '霧臺鄉', '瑪家鄉', '泰武鄉', '來義鄉', '春日鄉',
      '獅子鄉', '牡丹鄉', '秀林鄉', '萬榮鄉', '卓溪鄉', '延平鄉', '海端鄉', '達仁鄉', '金峰鄉', '蘭嶼鄉',
      // 平地鄉
      '關西鎮', '南庄鄉', '獅潭鄉', '魚池鄉', '滿州鄉', '花蓮市', '光復鄉', '玉里鎮', '新城鄉', '吉安鄉',
      '壽豐鄉', '鳳林鎮', '豐濱鄉', '瑞穗鄉', '富里鄉', '台東市', '成功鎮', '關山鎮', '東河鄉', '太麻里鄉',
      '大武鄉', '卑南鄉', '長濱鄉', '鹿野鄉', '池上鄉'
    ];

    isIndigenousArea.value = indigenousTowns.includes(indigenousParams.town);
    isIndigenousAreaChecked.value = true;

    // 添加到最近查詢記錄
    addToRecentSearches({
      county: indigenousParams.county,
      town: indigenousParams.town,
      searchTime: new Date()
    });

  } catch (error) {
    console.error('查詢失敗:', error);
  } finally {
    isIndigenousLoading.value = false;
  }
};

// 添加到最近查詢記錄
const addToRecentSearches = (search: any) => {
  // 檢查是否已存在相同查詢
  const existingIndex = recentSearches.value.findIndex(item =>
    item.county === search.county &&
    item.town === search.town &&
    (item.section === search.section || (!item.section && !search.section)) &&
    (item.landNumber === search.landNumber || (!item.landNumber && !search.landNumber))
  );

  // 如果已存在，則移除舊記錄
  if (existingIndex !== -1) {
    recentSearches.value.splice(existingIndex, 1);
  }

  // 添加到最近查詢列表的開頭
  recentSearches.value.unshift(search);

  // 限制列表最多顯示5筆
  if (recentSearches.value.length > 5) {
    recentSearches.value = recentSearches.value.slice(0, 5);
  }
};

// 切換標籤頁時清除查詢結果
watch(queryType, () => {
  searchResults.value = [];
  showNoResultMessage.value = false;
});
</script>

<style scoped>
.bg-light-blue-lighten-4 {
  background-color: #B3E5FC !important; /* 使用與補助申請頁面一致的顏色 */
}

.font-weight-medium {
  font-weight: 500 !important;
}

.font-weight-bold {
  font-weight: 700 !important;
}

.text-wrap {
  white-space: normal;
  word-wrap: break-word;
}

/* 表單與卡片間距調整 */
.v-card-text {
  padding: 16px !important;
}

.v-sheet {
  padding: 12px !important;
}

/* 查詢結果樣式 */
.v-card .v-card-title {
  line-height: 1.5;
}

.v-table {
  background-color: white;
}

.v-table th {
  font-weight: 600;
  color: rgba(0, 0, 0, 0.7);
}

/* 最近查詢項目樣式 */
.v-list-item:hover {
  background-color: #f5f5f5;
  cursor: pointer;
}

/* 查詢說明列表樣式 */
.v-list .v-list-item {
  min-height: 32px;
}

.v-list .v-list-item .v-list-item-title {
  font-size: 0.875rem;
}

.v-list .v-list-item .v-icon {
  color: #2196F3;
  font-size: 18px;
}

/* 查詢結果統計數據樣式 */
.v-card-subtitle.text-caption {
  color: rgba(0, 0, 0, 0.6);
  font-size: 0.75rem;
}

.v-card-text.text-body-1 {
  color: rgba(0, 0, 0, 0.87);
  font-size: 0.9375rem;
}

/* 讓表單元素在小螢幕上也能維持更緊湊的布局 */
@media (max-width: 960px) {
  .v-col {
    padding: 6px 12px !important;
  }

  .d-flex.flex-wrap > * {
    margin-bottom: 8px !important;
  }
}
</style>
