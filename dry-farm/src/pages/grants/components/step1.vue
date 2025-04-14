<template>
  <div class="step-content" ref="stepContent">
    <v-card class="mb-6 pa-0" flat>
      <v-card-text class="pb-0 pt-0">
        <v-form ref="form" v-model="localValid" @submit.prevent>
          <!-- 系統資訊區塊 -->
          <v-card class="mb-4" variant="outlined">
            <v-card-title class="bg-light-blue-lighten-4 d-flex align-center py-2 px-4">
              <v-icon class="me-2" size="small">mdi-information</v-icon>
              <span class="text-subtitle-1 font-weight-medium">申請基本資訊</span>
            </v-card-title>

            <v-card-text class="pa-4">
              <v-sheet class="pa-3 rounded" color="grey-lighten-5">
                <v-row>
                  <v-col cols="12" md="4">
                    <v-text-field
                      v-model="localFormData.caseNumber"
                      label="案件編號"
                      readonly
                      variant="outlined"
                      density="comfortable"
                      bg-color="grey-lighten-4"
                    ></v-text-field>
                  </v-col>
                  <v-col cols="12" md="4">
                    <v-text-field
                      v-model="localFormData.receivedDate"
                      label="收件日期"
                      readonly
                      variant="outlined"
                      density="comfortable"
                      bg-color="grey-lighten-4"
                    ></v-text-field>
                  </v-col>
                  <v-col cols="12" md="4">
                    <v-text-field
                      v-model="localFormData.receivedTime"
                      label="時間"
                      readonly
                      variant="outlined"
                      density="comfortable"
                      bg-color="grey-lighten-4"
                    ></v-text-field>
                  </v-col>
                </v-row>
              </v-sheet>
            </v-card-text>
          </v-card>

          <!-- 申請人基本資料區塊 -->
          <v-card class="mb-4" variant="outlined">
            <v-card-title class="bg-light-blue-lighten-4 d-flex align-center py-2 px-4">
              <v-icon class="me-2" size="small">mdi-account-details</v-icon>
              <span class="text-subtitle-1 font-weight-medium">申請人基本資料</span>
            </v-card-title>

            <v-card-text class="pa-4">
              <!-- 姓名與身分證區塊 -->
              <v-sheet class="mb-3 pa-3 rounded" color="blue-grey-lighten-5">
                <div class="d-flex align-center mb-2">
                  <v-icon size="small" class="me-2">mdi-card-account-details</v-icon>
                  <span class="text-body-2 font-weight-medium">身分資訊</span>
                </div>
                <v-row>
                  <v-col cols="12" md="6">
                    <v-text-field
                      v-model="localFormData.name"
                      label="申請人"
                      variant="outlined"
                      density="comfortable"
                      :rules="nameRules"
                      @update:model-value="updateFormData"
                    ></v-text-field>
                  </v-col>
                  <v-col cols="12" md="6">
                    <v-text-field
                      v-model="localFormData.id"
                      label="身分證字號"
                      variant="outlined"
                      density="comfortable"
                      :rules="idRules"
                      @update:model-value="updateFormData"
                    ></v-text-field>
                  </v-col>
                </v-row>
              </v-sheet>

              <!-- 聯絡資訊區塊 -->
              <v-sheet class="mb-3 pa-3 rounded" color="blue-grey-lighten-5">
                <div class="d-flex align-center mb-2">
                  <v-icon size="small" class="me-2">mdi-phone</v-icon>
                  <span class="text-body-2 font-weight-medium">聯絡資訊</span>
                </div>
                <v-row>
                  <v-col cols="12">
                    <v-text-field
                      v-model="localFormData.phone"
                      label="連絡電話"
                      variant="outlined"
                      density="comfortable"
                      :rules="phoneRules"
                      @update:model-value="updateFormData"
                      placeholder="請輸入手機號碼"
                    ></v-text-field>
                  </v-col>
                </v-row>
              </v-sheet>

              <!-- 地址資訊區塊 -->
              <v-sheet class="mb-3 pa-3 rounded" color="blue-grey-lighten-5">
                <div class="d-flex align-center mb-2">
                  <v-icon size="small" class="me-2">mdi-home</v-icon>
                  <span class="text-body-2 font-weight-medium">通訊地址</span>
                </div>
                <v-row>
                  <v-col cols="12" md="4">
                    <v-select
                      v-model="localFormData.county"
                      label="縣市"
                      :items="counties"
                      variant="outlined"
                      density="comfortable"
                      :rules="[v => !!v || '請選擇縣市']"
                      @update:model-value="onCountyChange"
                    ></v-select>
                  </v-col>
                  <v-col cols="12" md="4">
                    <v-select
                      v-model="localFormData.town"
                      label="鄉鎮市區"
                      :items="towns"
                      variant="outlined"
                      density="comfortable"
                      :rules="[v => !!v || '請選擇鄉鎮市區']"
                      :disabled="!localFormData.county"
                      @update:model-value="onTownChange"
                    ></v-select>
                  </v-col>
                  <v-col cols="12" md="4">
                    <v-select
                      v-model="localFormData.village"
                      label="村里"
                      :items="villages"
                      variant="outlined"
                      density="comfortable"
                      :rules="[v => !!v || '請選擇村里']"
                      :disabled="!localFormData.town"
                    ></v-select>
                  </v-col>
                </v-row>
                <v-row>
                  <v-col cols="12">
                    <v-text-field
                      v-model="localFormData.address"
                      label="詳細地址"
                      variant="outlined"
                      density="comfortable"
                      :rules="[v => !!v || '請輸入詳細地址']"
                      @update:model-value="updateFormData"
                      placeholder="請輸入門牌號碼及其他地址資訊"
                    ></v-text-field>
                  </v-col>
                </v-row>
              </v-sheet>
            </v-card-text>
          </v-card>

          <!-- 承辦資訊區塊 -->
          <v-card variant="outlined">
            <v-card-title class="bg-light-blue-lighten-4 d-flex align-center py-2 px-4">
              <v-icon class="me-2" size="small">mdi-account-tie</v-icon>
              <span class="text-subtitle-1 font-weight-medium">承辦資訊</span>
            </v-card-title>

            <v-card-text class="pa-4">
              <v-sheet class="pa-3 rounded" color="grey-lighten-5">
                <v-row>
                  <v-col cols="12" md="6">
                    <v-text-field
                      v-model="localFormData.manager"
                      label="承辦人"
                      variant="outlined"
                      density="comfortable"
                      readonly
                      bg-color="grey-lighten-4"
                    ></v-text-field>
                  </v-col>
                  <v-col cols="12" md="6">
                    <v-text-field
                      v-model="localFormData.department"
                      label="管理處"
                      variant="outlined"
                      density="comfortable"
                      readonly
                      bg-color="grey-lighten-4"
                    ></v-text-field>
                  </v-col>
                </v-row>
              </v-sheet>
            </v-card-text>
          </v-card>
        </v-form>
      </v-card-text>
    </v-card>

    <v-card class="step-navigation-card ma-0 pa-0" flat>

      <div class="d-flex align-center pr-4">
        <v-spacer></v-spacer>
        <div class="navigation-buttons">
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
import { ref, reactive, onMounted, watch, computed } from 'vue';

const props = defineProps<{
  formData: any;  // 接收父組件數據
}>();

const emit = defineEmits(['update:formData', 'validated']);
const localValid = ref(false);
const form = ref(null);

// 本地表單數據
const localFormData = reactive({
  caseNumber: '',
  receivedDate: '',
  receivedTime: '',
  name: '',
  id: '',
  phone: '',
  county: '',
  town: '',
  village: '',
  address: '',
  manager: '',
  department: ''
});

// 驗證規則
const nameRules = [
  (v: string) => !!v || '請填寫申請人姓名',
  (v: string) => (v && v.length <= 20) || '姓名不可超過20個字'
];

const idRules = [
  (v: string) => !!v || '請填寫身分證字號',
  (v: string) => /^[A-Z][12]\d{8}$/.test(v) || '身分證字號格式不正確'
];

const phoneRules = [
  (v: string) => !!v || '請填寫連絡電話',
  (v: string) => /^09\d{8}$/.test(v) || '手機號碼格式不正確'
];

// 地址相關數據
const counties = [
  '臺北市', '新北市', '基隆市', '桃園市', '新竹市', '新竹縣', '苗栗縣',
  '臺中市', '彰化縣', '南投縣', '雲林縣', '嘉義市', '嘉義縣', '臺南市',
  '高雄市', '屏東縣', '宜蘭縣', '花蓮縣', '臺東縣', '澎湖縣', '金門縣', '連江縣'
];

const townsMap = reactive<Record<string, string[]>>({
  '嘉義縣': ['太保市', '朴子市', '布袋鎮', '大林鎮', '民雄鄉', '溪口鄉', '新港鄉', '六腳鄉', '東石鄉', '義竹鄉', '鹿草鄉', '水上鄉', '中埔鄉', '竹崎鄉', '梅山鄉', '番路鄉', '大埔鄉', '阿里山鄉'],
  // 其他縣市的鄉鎮區資料可以根據需要添加
});

const villagesMap = reactive<Record<string, Record<string, string[]>>>({
  '嘉義縣': {
    '竹崎鄉': ['龍山村', '灣橋村', '義仁村', '和平村', '塘興村', '光華村', '白杞村', '中和村', '鹿滿村']
    // 其他鄉鎮的村里資料
  }
});

const towns = computed(() => {
  return localFormData.county ? (townsMap[localFormData.county] || []) : [];
});

const villages = computed(() => {
  if (!localFormData.county || !localFormData.town) return [];
  return (villagesMap[localFormData.county]?.[localFormData.town]) || [];
});

// 處理縣市變化
const onCountyChange = () => {
  localFormData.town = '';
  localFormData.village = '';
  updateFormData();
};

// 處理鄉鎮變化
const onTownChange = () => {
  localFormData.village = '';
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
  emit('validated', { valid, step: 1 });
};

// 初始化數據
onMounted(() => {
  // 設置初始數據
  if (props.formData) {
    Object.keys(localFormData).forEach(key => {
      if (props.formData[key] !== undefined) {
        localFormData[key] = props.formData[key];
      }
    });
  }

  // 設置只讀欄位的模擬數據
  if (!localFormData.caseNumber) {
    localFormData.caseNumber = '113010001';
  }
  if (!localFormData.receivedDate) {
    localFormData.receivedDate = '113/01/16';
  }
  if (!localFormData.receivedTime) {
    localFormData.receivedTime = '14:00';
  }
  if (!localFormData.manager) {
    localFormData.manager = '陳柔蒨';
  }
  if (!localFormData.department) {
    localFormData.department = '嘉南管理處';
  }
});

// 監聽父組件數據變化
watch(() => props.formData, (newVal) => {
  if (newVal) {
    Object.keys(localFormData).forEach(key => {
      if (newVal[key] !== undefined && newVal[key] !== localFormData[key]) {
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

.bg-light-blue-lighten-4 {
  background-color: #B3E5FC !important;
}

.bg-light-blue-lighten-5 {
  background-color: #e3f2fd !important;
}
</style>
