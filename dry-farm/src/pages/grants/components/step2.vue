<template>
  <div class="step-content" ref="stepContent">
    <v-card class="mb-6 pa-0" flat>
      <v-card-text class="pb-0 pt-0">
        <!-- 設施地址區域 -->
        <v-card class="mb-4" variant="outlined">
          <v-card-title class="bg-light-blue-lighten-4 d-flex align-center py-2 px-4">
            <v-icon class="me-2" size="small">mdi-home-map-marker</v-icon>
            <span class="text-subtitle-1 font-weight-medium">設施地址</span>
          </v-card-title>

          <v-card-text class="pa-4">
            <!-- 地址選擇區域 -->
            <v-sheet class="mb-3 pa-3 rounded" color="grey-lighten-5">
              <div class="d-flex align-center mb-2">
                <v-icon size="small" class="me-2">mdi-map</v-icon>
                <span class="text-body-2 font-weight-medium">行政區域</span>
              </div>
              <v-row>
                <v-col cols="12" md="4">
                  <v-select
                    v-model="localFormData.addressCounty"
                    :items="counties"
                    label="地段"
                    variant="outlined"
                    density="comfortable"
                    :rules="[v => !!v || '請選擇縣市']"
                    @update:model-value="onCountyChange"
                  ></v-select>
                </v-col>
                <v-col cols="12" md="4">
                  <v-select
                    v-model="localFormData.addressTown"
                    :items="towns"
                    label="鄉鎮市區"
                    variant="outlined"
                    density="comfortable"
                    :rules="[v => !!v || '請選擇鄉鎮市區']"
                    :disabled="!localFormData.addressCounty"
                    @update:model-value="onTownChange"
                  ></v-select>
                </v-col>
                <v-col cols="12" md="4">
                  <v-select
                    v-model="localFormData.addressVillage"
                    :items="villages"
                    label="村里"
                    variant="outlined"
                    density="comfortable"
                    :disabled="!localFormData.addressTown"
                  ></v-select>
                </v-col>
              </v-row>
            </v-sheet>

            <!-- 地號與查詢 -->
            <v-sheet class="mb-3 pa-3 rounded" color="grey-lighten-5">
              <div class="d-flex align-center mb-2">
                <v-icon size="small" class="me-2">mdi-numeric</v-icon>
                <span class="text-body-2 font-weight-medium">地號資訊</span>
              </div>
              <v-row align="center">
                <v-col cols="12" md="4">
                  <v-text-field
                    v-model="localFormData.landNumber"
                    label="地號"
                    variant="outlined"
                    density="comfortable"
                    :rules="[v => !!v || '請輸入地號']"
                  ></v-text-field>
                </v-col>
                <v-col cols="12" md="8" class="d-flex align-center">
                  <v-btn
                    color="secondary"
                    variant="tonal"
                    class="me-2"
                  >
                    <v-icon size="small" class="me-1">mdi-magnify</v-icon>
                    查詢
                  </v-btn>
                  <div class="text-caption text-grey">
                    (若查無地號請洽中心)
                  </div>
                  <v-checkbox
                    v-model="localFormData.isAboriginalArea"
                    label="原民區"
                    hide-details
                    density="compact"
                    class="ms-auto"
                  ></v-checkbox>
                  <div class="ms-1">：否</div>
                </v-col>
              </v-row>
            </v-sheet>

            <!-- 特性選項區域 -->
            <v-sheet class="mb-3 pa-3 rounded" color="blue-grey-lighten-5">
              <div class="d-flex align-center mb-2">
                <v-icon size="small" class="me-2">mdi-gate</v-icon>
                <span class="text-body-2 font-weight-medium">土地特性</span>
              </div>
              <v-row>
                <v-col cols="12" md="4">
                  <div class="d-flex align-center">
                    <v-checkbox
                      v-model="localFormData.isIrrigationArea"
                      hide-details
                      density="compact"
                    ></v-checkbox>
                    <span class="ml-1">位於灌區內</span>
                    <span class="ml-1">：</span>
                  </div>
                </v-col>
                <v-col cols="12" md="4">
                  <div class="d-flex align-center">
                    <v-checkbox
                      v-model="localFormData.isReapplied"
                      hide-details
                      density="compact"
                    ></v-checkbox>
                    <span class="ml-1">再次申請</span>
                    <span class="ml-1">：</span>
                  </div>
                </v-col>
              </v-row>
            </v-sheet>

            <!-- 座標資訊 -->
            <v-sheet class="mb-3 pa-3 rounded" color="blue-grey-lighten-5">
              <div class="d-flex align-center mb-2">
                <v-icon size="small" class="me-2">mdi-map-marker</v-icon>
                <span class="text-body-2 font-weight-medium">座標資訊</span>
              </div>
              <v-row>
                <v-col cols="12" md="6">
                  <v-text-field
                    v-model="localFormData.longitude"
                    label="經度"
                    variant="outlined"
                    density="comfortable"
                    :rules="[v => !!v || '請輸入經度']"
                  ></v-text-field>
                </v-col>
                <v-col cols="12" md="6">
                  <v-text-field
                    v-model="localFormData.latitude"
                    label="緯度"
                    variant="outlined"
                    density="comfortable"
                    :rules="[v => !!v || '請輸入緯度']"
                  ></v-text-field>
                </v-col>
              </v-row>
            </v-sheet>

            <!-- 面積資訊 -->
            <v-sheet class="mb-3 pa-3 rounded bg-amber-lighten-5 border border-amber">
              <div class="d-flex align-center mb-2">
                <v-icon size="small" class="me-2" color="amber-darken-2">mdi-ruler-square</v-icon>
                <span class="text-body-2 font-weight-medium">面積資訊</span>
              </div>
              <v-row>
                <v-col cols="12" md="6">
                  <div class="d-flex align-center">
                    <span class="text-body-1 font-weight-medium me-2">農地面積</span>
                    <v-text-field
                      v-model="localFormData.landArea"
                      variant="outlined"
                      bg-color="yellow-lighten-3"
                      density="compact"
                      class="me-2"
                      style="width: 120px"
                      :rules="[v => !!v || '請輸入面積']"
                    ></v-text-field>
                    <div class="me-2">㎡</div>
                    <v-text-field
                      v-model="localFormData.landAreaHa"
                      variant="outlined"
                      bg-color="yellow-lighten-3"
                      density="compact"
                      style="width: 120px"
                      readonly
                    ></v-text-field>
                    <div class="ms-2">ha</div>
                  </div>
                </v-col>
                <v-col cols="12" md="6">
                  <div class="d-flex align-center">
                    <span class="text-body-1 font-weight-medium me-2">施設面積</span>
                    <v-text-field
                      v-model="localFormData.facilityArea"
                      variant="outlined"
                      bg-color="yellow-lighten-3"
                      density="compact"
                      class="me-2"
                      style="width: 120px"
                      :rules="[v => !!v || '請輸入面積']"
                    ></v-text-field>
                    <div class="me-2">㎡</div>
                    <v-text-field
                      v-model="localFormData.facilityAreaHa"
                      variant="outlined"
                      bg-color="yellow-lighten-3"
                      density="compact"
                      style="width: 120px"
                      readonly
                    ></v-text-field>
                    <div class="ms-2">ha</div>
                  </div>
                </v-col>
              </v-row>
            </v-sheet>

            <!-- 農地種植作物 -->
            <v-sheet class="mb-3 pa-3 rounded" color="green-lighten-5">
              <div class="d-flex align-center mb-2">
                <v-icon size="small" class="me-2" color="green">mdi-sprout</v-icon>
                <span class="text-body-2 font-weight-medium">農地種植作物</span>
              </div>
              <div class="d-flex align-center mb-2">
                <v-select
                  v-model="localFormData.cropCategory"
                  :items="cropCategories"
                  label="作物類別"
                  variant="outlined"
                  density="comfortable"
                  class="me-2"
                  style="width: 200px"
                  :rules="[v => !!v || '請選擇作物類別']"
                  @update:model-value="onCropCategoryChange"
                ></v-select>
                <v-select
                  v-model="localFormData.cropName"
                  :items="crops"
                  label="作物名稱"
                  variant="outlined"
                  density="comfortable"
                  class="me-2"
                  style="width: 200px"
                  :rules="[v => !!v || '請選擇作物名稱']"
                  :disabled="!localFormData.cropCategory"
                ></v-select>
                <v-btn
                  variant="tonal"
                  color="success"
                  size="small"
                  @click="addCrop"
                >
                  <v-icon size="small" class="me-1">mdi-plus</v-icon>
                  加入
                </v-btn>
              </div>

              <v-table density="compact" class="rounded border">
                <thead class="bg-grey-lighten-3">
                  <tr>
                    <th class="text-center" style="width: 50px">NO.</th>
                    <th>類別</th>
                    <th>作物</th>
                    <th class="text-center" style="width: 80px">刪除</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(crop, index) in localFormData.crops" :key="index">
                    <td class="text-center">{{ index + 1 }}</td>
                    <td>{{ crop.category }}</td>
                    <td>{{ crop.name }}</td>
                    <td class="text-center">
                      <v-btn
                        icon
                        size="x-small"
                        color="error"
                        variant="text"
                        @click="removeCrop(index)"
                      >
                        <v-icon>mdi-close</v-icon>
                      </v-btn>
                    </td>
                  </tr>
                  <tr v-if="localFormData.crops.length === 0">
                    <td colspan="4" class="text-center py-3 text-grey">
                      尚未新增任何作物，請使用上方加入按鈕新增
                    </td>
                  </tr>
                </tbody>
              </v-table>
            </v-sheet>
          </v-card-text>
        </v-card>

        <!-- 所有權人資料區域 -->
        <v-card variant="outlined">
          <v-card-title class="bg-light-blue-lighten-4 d-flex align-center py-2 px-4">
            <v-icon class="me-2" size="small">mdi-account-multiple</v-icon>
            <span class="text-subtitle-1 font-weight-medium">所有權人資料</span>
          </v-card-title>
          <v-card-text class="pa-4">
            <!-- 所有權人基本資料 -->
            <v-sheet class="mb-3 pa-3 rounded" color="grey-lighten-5">
              <div class="d-flex align-center mb-2">
                <v-icon size="small" class="me-2">mdi-account-details</v-icon>
                <span class="text-body-2 font-weight-medium">所有權人基本資料</span>
              </div>
              <v-row>
                <v-col cols="12" md="6">
                  <v-text-field
                    v-model="localFormData.ownerName"
                    label="持分人姓名"
                    variant="outlined"
                    density="comfortable"
                    :rules="[v => !!v || '請輸入持分人姓名']"
                  ></v-text-field>
                </v-col>
                <v-col cols="12" md="6">
                  <v-text-field
                    v-model="localFormData.ownerId"
                    label="持分人身分證字號"
                    variant="outlined"
                    density="comfortable"
                    :rules="[v => !!v || '請輸入身分證字號', v => /^[A-Z][12]\d{8}$/.test(v) || '身分證字號格式不正確']"
                  ></v-text-field>
                </v-col>
              </v-row>
            </v-sheet>

            <!-- 所有權人地址 -->
            <v-sheet class="mb-3 pa-3 rounded" color="grey-lighten-5">
              <div class="d-flex align-center mb-2">
                <v-icon size="small" class="me-2">mdi-home</v-icon>
                <span class="text-body-2 font-weight-medium">持分人地址</span>
              </div>
              <v-row>
                <v-col cols="12">
                  <div class="d-flex align-center flex-wrap">
                    <v-select
                      v-model="localFormData.ownerCounty"
                      :items="counties"
                      label="縣市"
                      variant="outlined"
                      density="comfortable"
                      class="me-2 mb-2"
                      style="width: 150px"
                      :rules="[v => !!v || '請選擇縣市']"
                      @update:model-value="onOwnerCountyChange"
                    ></v-select>
                    <v-select
                      v-model="localFormData.ownerTown"
                      :items="ownerTowns"
                      label="鄉鎮市區"
                      variant="outlined"
                      density="comfortable"
                      class="me-2 mb-2"
                      style="width: 150px"
                      :rules="[v => !!v || '請選擇鄉鎮市區']"
                      :disabled="!localFormData.ownerCounty"
                      @update:model-value="onOwnerTownChange"
                    ></v-select>
                    <v-select
                      v-model="localFormData.ownerVillage"
                      :items="ownerVillages"
                      label="村里"
                      variant="outlined"
                      density="comfortable"
                      class="mb-2"
                      style="width: 150px"
                      :disabled="!localFormData.ownerTown"
                    ></v-select>
                  </div>
                </v-col>
              </v-row>
            </v-sheet>

            <!-- 持分資訊 -->
            <v-sheet class="mb-3 pa-3 rounded bg-amber-lighten-5 border border-amber">
              <div class="d-flex align-center mb-2">
                <v-icon size="small" class="me-2" color="amber-darken-2">mdi-percent</v-icon>
                <span class="text-body-2 font-weight-medium">持分資訊</span>
              </div>
              <v-row align="center">
                <v-col cols="12" md="6">
                  <div class="d-flex align-center">
                    <span class="text-body-2 font-weight-medium me-2">持分比例</span>
                    <v-text-field
                      v-model="localFormData.ownerShare1"
                      variant="outlined"
                      density="compact"
                      class="me-1"
                      style="width: 80px"
                      :rules="[v => !!v || '請輸入分子']"
                    ></v-text-field>
                    <div class="mx-1">分子</div>
                    <div class="mx-1">/</div>
                    <v-text-field
                      v-model="localFormData.ownerShare2"
                      variant="outlined"
                      density="compact"
                      class="me-1"
                      style="width: 80px"
                      :rules="[v => !!v || '請輸入分母']"
                    ></v-text-field>
                    <div class="ms-1">分母</div>
                  </div>
                </v-col>
                <v-col cols="12" md="6">
                  <div class="d-flex align-center">
                    <span class="text-body-2 font-weight-medium me-2">持分面積</span>
                    <v-text-field
                      v-model="localFormData.ownerArea"
                      variant="outlined"
                      bg-color="yellow-lighten-3"
                      density="compact"
                      class="me-2"
                      style="width: 120px"
                      readonly
                    ></v-text-field>
                    <div class="me-2">㎡</div>
                    <v-btn
                      variant="tonal"
                      color="success"
                      size="small"
                      :disabled="!canAddOwner"
                      @click="addOwner"
                    >
                      <v-icon size="small" class="me-1">mdi-plus</v-icon>
                      加入
                    </v-btn>
                  </div>
                </v-col>
              </v-row>
            </v-sheet>

            <!-- 所有權人列表 -->
            <v-sheet class="pa-0">
              <v-table density="comfortable" class="rounded border">
                <thead class="bg-grey-lighten-3">
                  <tr>
                    <th class="text-center" style="width: 50px">NO.</th>
                    <th>姓名</th>
                    <th>身分證字號</th>
                    <th>地址</th>
                    <th>持分比例</th>
                    <th>持分面積㎡</th>
                    <th class="text-center" style="width: 80px">刪除</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(owner, index) in localFormData.owners" :key="index">
                    <td class="text-center">{{ index + 1 }}</td>
                    <td>{{ owner.name }}</td>
                    <td>{{ owner.id }}</td>
                    <td>{{ owner.address }}</td>
                    <td>{{ owner.share }}</td>
                    <td>{{ owner.area }}</td>
                    <td class="text-center">
                      <v-btn
                        icon
                        size="x-small"
                        color="error"
                        variant="text"
                        @click="removeOwner(index)"
                      >
                        <v-icon>mdi-close</v-icon>
                      </v-btn>
                    </td>
                  </tr>
                  <tr v-if="localFormData.owners.length === 0">
                    <td colspan="7" class="text-center py-3 text-grey">
                      尚未新增任何所有權人，請使用上方加入按鈕新增
                    </td>
                  </tr>
                </tbody>
              </v-table>
            </v-sheet>
          </v-card-text>
        </v-card>
      </v-card-text>
    </v-card>

    <v-card class="step-navigation-card ma-0 pa-0" flat>

      <div class="d-flex align-center pr-4">
        <v-spacer></v-spacer>
        <div class="navigation-buttons">
          <v-btn
            variant="outlined"
            color="grey-darken-1"
            class="me-2"
            size="large"
            :disabled="currentStep === 1"
            @click="goToPreviousStep"
            rounded="circl"
          >
            <v-icon start>mdi-arrow-left</v-icon>
            上一步
          </v-btn>

          <!-- <div class="text-caption d-none d-sm-block text-grey"> 步驟 {{ currentStep }}/8 </div> -->

          <v-btn
            color="green-darken-1"
            :disabled="!isValid"
            @click="goToNextStep"
            size="large"
            rounded="circl"
          >
            {{ currentStep === 8 ? '完成' : '下一步' }}
            <v-icon end v-if="currentStep < 8">mdi-arrow-right</v-icon>
            <v-icon end v-else>mdi-check</v-icon>
          </v-btn>
        </div>
      </div>
    </v-card>
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{
  formData: any;  // 接收父組件數據
  currentStep: number;
}>();

const emit = defineEmits(['update:formData', 'validated', 'goBack']);
const localValid = ref(false);
const form = ref(null);

// 步驟指示器顏色
const getStepColor = (step: number) => {
  if (step < props.currentStep) return 'success'; // 已完成
  if (step === props.currentStep) return 'primary'; // 當前
  return 'grey'; // 未開始
};

// 上一步
const goToPreviousStep = () => {
  if (props.currentStep > 1) {
    emit('goBack');
  }
};

// 本地表單數據
const localFormData = reactive({
  // 設施地址區塊
  addressCounty: '',
  addressTown: '',
  addressVillage: '',
  landNumber: '',
  isAboriginalArea: false,
  isIrrigationArea: false,
  isReapplied: false,
  longitude: '',
  latitude: '',
  landArea: '',
  landAreaHa: '',
  facilityArea: '',
  facilityAreaHa: '',
  cropCategory: '',
  cropName: '',
  crops: [] as Array<{category: string, name: string}>,

  // 所有權人資料區塊
  ownerName: '',
  ownerId: '',
  ownerCounty: '',
  ownerTown: '',
  ownerVillage: '',
  ownerShare1: '',
  ownerShare2: '',
  ownerArea: '',
  owners: [] as Array<{
    name: string,
    id: string,
    address: string,
    share: string,
    area: string
  }>
});

// 地址相關數據
const counties = [
  '嘉義縣', '臺北市', '新北市', '桃園市', '臺中市', '臺南市', '高雄市', '新竹縣', '新竹市', '苗栗縣',
  '彰化縣', '南投縣', '雲林縣', '嘉義市', '屏東縣', '宜蘭縣', '花蓮縣', '臺東縣', '澎湖縣', '金門縣', '連江縣'
];

const townsMap = reactive<Record<string, string[]>>({
  '嘉義縣': ['竹崎鄉', '太保市', '朴子市', '布袋鎮', '大林鎮', '民雄鄉'],
  // 其他縣市鄉鎮
});

const villagesMap = reactive<Record<string, Record<string, string[]>>>({
  '嘉義縣': {
    '竹崎鄉': ['龍山村', '灣橋村', '瓦厝埔段'],
    // 其他鄉鎮村里
  }
});

// 作物相關數據
const cropCategoriesData = {
  '糧食作物': ['稻米', '小麥', '玉米', '大豆'],
  '特用作物': ['茶葉', '咖啡', '香蕉'],
  '果樹作物': ['橘', '香蕉', '芒果', '鳳梨'],
  '蔬菜作物': ['番茄', '青椒', '茄子', '胡蘿蔔'],
  '景觀花卉作物': ['玫瑰', '百合', '康乃馨'],
  '其他作物': ['其他']
};

const cropCategories = Object.keys(cropCategoriesData);

// 計算屬性
const towns = computed(() => {
  return localFormData.addressCounty ? (townsMap[localFormData.addressCounty] || []) : [];
});

const villages = computed(() => {
  if (!localFormData.addressCounty || !localFormData.addressTown) return [];
  return (villagesMap[localFormData.addressCounty]?.[localFormData.addressTown]) || [];
});

const ownerTowns = computed(() => {
  return localFormData.ownerCounty ? (townsMap[localFormData.ownerCounty] || []) : [];
});

const ownerVillages = computed(() => {
  if (!localFormData.ownerCounty || !localFormData.ownerTown) return [];
  return (villagesMap[localFormData.ownerCounty]?.[localFormData.ownerTown]) || [];
});

const crops = computed(() => {
  return localFormData.cropCategory ? (cropCategoriesData[localFormData.cropCategory as keyof typeof cropCategoriesData] || []) : [];
});

const canAddOwner = computed(() => {
  return !!localFormData.ownerName &&
         !!localFormData.ownerId &&
         !!localFormData.ownerShare1 &&
         !!localFormData.ownerShare2 &&
         !!localFormData.ownerArea;
});

// 方法
const onCountyChange = () => {
  localFormData.addressTown = '';
  localFormData.addressVillage = '';
  updateFormData();
};

const onTownChange = () => {
  localFormData.addressVillage = '';
  updateFormData();
};

const onOwnerCountyChange = () => {
  localFormData.ownerTown = '';
  localFormData.ownerVillage = '';
  updateFormData();
};

const onOwnerTownChange = () => {
  localFormData.ownerVillage = '';
  updateFormData();
};

const onCropCategoryChange = () => {
  localFormData.cropName = '';
  updateFormData();
};

// 面積計算
watch(() => localFormData.landArea, (newVal) => {
  if (newVal) {
    const area = parseFloat(newVal);
    if (!isNaN(area)) {
      localFormData.landAreaHa = (area / 10000).toFixed(4);
    }
  } else {
    localFormData.landAreaHa = '';
  }
});

watch(() => localFormData.facilityArea, (newVal) => {
  if (newVal) {
    const area = parseFloat(newVal);
    if (!isNaN(area)) {
      localFormData.facilityAreaHa = (area / 10000).toFixed(4);
    }
  } else {
    localFormData.facilityAreaHa = '';
  }
});

// 計算持分面積
watch([() => localFormData.landArea, () => localFormData.ownerShare1, () => localFormData.ownerShare2], () => {
  if (localFormData.landArea && localFormData.ownerShare1 && localFormData.ownerShare2) {
    const landArea = parseFloat(localFormData.landArea);
    const share1 = parseFloat(localFormData.ownerShare1);
    const share2 = parseFloat(localFormData.ownerShare2);

    if (!isNaN(landArea) && !isNaN(share1) && !isNaN(share2) && share2 !== 0) {
      localFormData.ownerArea = ((landArea * share1) / share2).toFixed(1);
    }
  } else {
    localFormData.ownerArea = '';
  }
});

// 添加作物
const addCrop = () => {
  if (localFormData.cropCategory && localFormData.cropName) {
    const crop = {
      category: localFormData.cropCategory,
      name: localFormData.cropName
    };

    // 檢查是否已存在
    const exists = localFormData.crops.some(c =>
      c.category === crop.category && c.name === crop.name
    );

    if (!exists) {
      localFormData.crops.push(crop);
      // 清空選擇
      localFormData.cropName = '';
    }

    updateFormData();
  }
};

// 移除作物
const removeCrop = (index: number) => {
  localFormData.crops.splice(index, 1);
  updateFormData();
};

// 添加所有權人
const addOwner = () => {
  if (localFormData.ownerName && localFormData.ownerId &&
      localFormData.ownerShare1 && localFormData.ownerShare2 && localFormData.ownerArea) {
    const ownerAddress = [
      localFormData.ownerCounty,
      localFormData.ownerTown,
      localFormData.ownerVillage
    ].filter(Boolean).join('');

    const owner = {
      name: localFormData.ownerName,
      id: localFormData.ownerId,
      address: ownerAddress || 'XX',
      share: `${localFormData.ownerShare1}/${localFormData.ownerShare2}`,
      area: localFormData.ownerArea
    };

    localFormData.owners.push(owner);

    // 清空輸入
    localFormData.ownerName = '';
    localFormData.ownerId = '';
    // 保留地址信息
    localFormData.ownerShare1 = '';
    localFormData.ownerShare2 = '';
    localFormData.ownerArea = '';

    updateFormData();
  }
};

// 移除所有權人
const removeOwner = (index: number) => {
  localFormData.owners.splice(index, 1);
  updateFormData();
};

// 更新父組件數據
const updateFormData = () => {
  emit('update:formData', {
    ...props.formData,
    ...localFormData,
    valid: localValid.value
  });
};

// 表單驗證
const validate = async () => {
  const { valid } = await form.value.validate();
  if (valid) {
    updateFormData();
  }
  emit('validated', { valid, step: 2 });
};

// 初始化數據
onMounted(() => {
  // 設置預設數據
  if (props.formData) {
    Object.keys(localFormData).forEach(key => {
      if (props.formData[key] !== undefined) {
        localFormData[key] = props.formData[key];
      }
    });
  }

  // 設置模擬數據
  if (!localFormData.landNumber) {
    localFormData.landNumber = '996-1';
  }
  if (!localFormData.longitude) {
    localFormData.longitude = '120.5734';
  }
  if (!localFormData.latitude) {
    localFormData.latitude = '23.5155';
  }
  if (!localFormData.landArea) {
    localFormData.landArea = '8455';
    localFormData.landAreaHa = '0.8455';
  }
  if (!localFormData.facilityArea) {
    localFormData.facilityArea = '8455';
    localFormData.facilityAreaHa = '0.8455';
  }

  // 設置一個範例作物
  if (localFormData.crops.length === 0) {
    localFormData.crops.push({
      category: '果樹作物',
      name: '橘'
    });
  }

  // 設置一個範例所有權人
  if (localFormData.owners.length === 0) {
    localFormData.owners.push({
      name: '王三三',
      id: 'A123456789',
      address: 'XX',
      share: '1/2',
      area: '4227.5'
    });
  }
});

// 監聽父組件數據變化
watch(() => props.formData, (newVal) => {
  if (newVal) {
    Object.keys(localFormData).forEach(key => {
      if (newVal[key] !== undefined &&
          JSON.stringify(newVal[key]) !== JSON.stringify(localFormData[key])) {
        localFormData[key] = newVal[key];
      }
    });
  }
}, { deep: true });

// 監聽本地數據變化，更新父組件
watch(localFormData, () => {
  updateFormData();
}, { deep: true });

// 監聽本地表單驗證狀態
watch(localValid, (newVal) => {
  if (props.formData?.valid !== newVal) {
    updateFormData();
  }
});
</script>

<style scoped>
.step-content {
  padding: 0;
}

.v-card-title {
  color: rgba(0, 0, 0, 0.87);
  font-size: 1.25rem;
  font-weight: 500;
  padding: 16px;
}

.bg-primary {
  background-color: #1976D2 !important;
}

.bg-light-blue-lighten-4 {
  background-color: #B3E5FC !important;
}

.bg-amber-lighten-5 {
  background-color: #FFF8E1 !important;
}

.border-amber {
  border-color: #FFD54F !important;
  border-width: 1px;
  border-style: solid;
}

/* 黃色背景輸入框 */
.v-text-field.bg-yellow-lighten-3 :deep(.v-field__input) {
  background-color: #fff9c4;
}

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
</style>
