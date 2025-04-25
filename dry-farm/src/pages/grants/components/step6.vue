<template>
  <div class="step-content" ref="stepContent">
    <v-card class="mb-6 pa-0" flat>
      <v-card-text class="pb-0 pt-0">
        <v-form ref="form" v-model="localValid" @submit.prevent>
          <!-- 補助申請基本資訊區 -->
          <v-card class="mb-4" variant="outlined">
            <v-card-title class="bg-light-blue-lighten-4 d-flex align-center py-2 px-4">
              <v-icon class="me-2" size="small">mdi-file-document</v-icon>
              <span class="text-subtitle-1 font-weight-medium">補助申請資料預覽</span>
            </v-card-title>

            <v-card-text class="pa-4">
              <v-sheet class="pa-3 rounded" color="bg-amber-lighten-5 border border-amber">
                <v-table class="preview-table" style="background-color: transparent" density="compact">
                  <tbody>
                    <tr>
                      <td class="font-weight-medium text-center" style="width: 15%">申請年度</td>
                      <td style="width: 35%">{{ localFormData.applicationYear }}</td>
                      <td class="font-weight-medium text-center" style="width: 15%">案號</td>
                      <td style="width: 35%">{{ localFormData.caseNumber }}</td>
                    </tr>
                    <tr>
                      <td class="font-weight-medium text-center">農戶姓名</td>
                      <td>{{ localFormData.applicantName }}</td>
                      <td class="font-weight-medium text-center">農戶住址</td>
                      <td>{{ localFormData.applicantAddress }}</td>
                    </tr>
                    <tr>
                      <td class="font-weight-medium text-center">設施地段</td>
                      <td>{{ localFormData.facilityLocation }}</td>
                      <td class="font-weight-medium text-center">設施地號</td>
                      <td>{{ localFormData.facilityNumber }}</td>
                    </tr>
                    <tr>
                      <td class="font-weight-medium text-center">設施面積</td>
                      <td>{{ localFormData.facilityArea }}公頃</td>
                      <td class="font-weight-medium text-center">設施型式</td>
                      <td>{{ localFormData.facilityType }}</td>
                    </tr>
                  </tbody>
                </v-table>
              </v-sheet>
            </v-card-text>
          </v-card>

          <!-- 農戶補助明細區 -->
          <v-card class="mb-4" variant="outlined">
            <v-card-title class="bg-light-blue-lighten-4 d-flex align-center py-2 px-4">
              <v-icon class="me-2" size="small">mdi-calculator</v-icon>
              <span class="text-subtitle-1 font-weight-medium">農戶補助明細</span>
            </v-card-title>

            <v-card-text class="pa-4">
              <v-sheet class="pa-3 rounded" color="bg-amber-lighten-5 border border-amber">
                <v-table class="budget-table" style="background-color: transparent" density="compact">
                  <tbody>
                    <!-- 農戶配合款 -->
                    <tr>
                      <td class="font-weight-medium text-center" colspan="2" style="width: 25%" >農戶配合款</td>
                      <td class="text-center" >{{ localFormData.farmerContribution || '0' }}</td>
                    </tr>

                    <!-- 政府補助款 -->
                    <tr>
                      <td class="font-weight-medium text-center" rowspan="3" style="vertical-align: middle">
                        政府<br>補助款
                      </td>
                      <td class="font-weight-medium text-center" rowspan="2" style="vertical-align: middle">
                        農戶<br>請領款
                      </td>
                      <td class="text-center">A項補助費：{{ localFormData.pipeLineSubsidy }}</td>
                    </tr>
                    <tr>
                      <td class="text-center">B項補助費：{{ localFormData.facilitySubsidy }}</td>
                    </tr>
                    <tr>
                      <td class="font-weight-medium text-center">規劃設計費</td>
                      <td class="text-center">{{ localFormData.designFee }}</td>
                    </tr>

                    <!-- 總計 -->
                    <tr class="total-row">
                      <td class="font-weight-medium text-center" colspan="2">本設施預算總計</td>
                      <td class="text-center font-weight-medium">{{ localFormData.totalBudget }}</td>
                    </tr>
                  </tbody>
                </v-table>
              </v-sheet>
            </v-card-text>
          </v-card>

          <!-- 報表列印區 -->
          <v-card variant="outlined">
            <v-card-title class="bg-light-blue-lighten-4 d-flex align-center py-2 px-4">
              <v-icon class="me-2" size="small">mdi-printer</v-icon>
              <span class="text-subtitle-1 font-weight-medium">報表列印</span>
            </v-card-title>

            <v-card-text class="pa-4">
              <v-sheet class="pa-3 rounded" color="grey-lighten-5">
                <v-row no-gutters align-content="space-between">

                  <v-col class="me-auto" cols="auto">
                    <v-btn
                      variant="outlined"
                      color="primary"
                      prepend-icon="mdi-file-document-outline"
                      @click="printDocument('application')"
                      class="ml-4 mr-4"
                    >
                      灌溉系統設計標準
                    </v-btn>
                  </v-col>
                  <v-col class="me-auto" cols="auto">
                    <v-btn
                      variant="outlined"
                      color="primary"
                      prepend-icon="mdi-file-document-outline"
                      @click="printDocument('completion')"
                      class="ml-4 mr-4"
                    >
                      結案申報書
                    </v-btn>
                  </v-col>
                  <v-col class="me-auto" cols="auto">
                    <v-btn
                      variant="outlined"
                      color="primary"
                      prepend-icon="mdi-file-document-outline"
                      @click="printDocument('pledge')"
                      class="ml-4 mr-4"
                    >
                      補助切結書
                    </v-btn>
                  </v-col>
                  <v-col class="me-auto" cols="auto">
                    <v-btn
                      variant="outlined"
                      color="primary"
                      prepend-icon="mdi-file-document-outline"
                      @click="printDocument('planning')"
                      class="ml-4 mr-4"
                    >
                      規劃委託書
                    </v-btn>
                  </v-col>
                  <v-col class="me-auto" cols="auto">
                    <v-btn
                      variant="outlined"
                      color="primary"
                      prepend-icon="mdi-file-document-outline"
                      @click="printDocument('budget')"
                      class="ml-4 mr-4"
                    >
                      工程預算書
                    </v-btn>
                  </v-col>
                  <v-spacer></v-spacer>
                </v-row>
              </v-sheet>
            </v-card-text>
          </v-card>
        </v-form>
      </v-card-text>
    </v-card>

    <!-- 設施明細區 -->
    <v-card class="mb-6 pa-0" flat>
      <v-card-text class="pb-0 pt-0">
        <v-card variant="outlined">
          <v-card-title class="bg-light-blue-lighten-4 d-flex align-center py-2 px-4">
            <v-icon class="me-2" size="small">mdi-pipe</v-icon>
            <span class="text-subtitle-1 font-weight-medium">本案設施</span>
          </v-card-title>

          <v-card-text class="pa-4">
            <v-table class="facility-table border" density="compact">
              <thead class="bg-grey-lighten-3">
                <tr>
                  <th>設施項目</th>
                  <th>說明</th>
                  <th class="text-center">單位</th>
                  <th class="text-center">數量</th>
                  <th class="text-center">單價</th>
                  <th class="text-center">總價</th>
                  <th>備註</th>
                </tr>
              </thead>
              <tbody>

                <tr>
                  <td class="font-weight-medium">A.田間管路設施費</td>
                  <td></td>
                  <td class="text-center">全</td>
                  <td class="text-center"></td>
                  <td class="text-center"></td>
                  <td class="text-center">{{ localFormData.pipeLineSubsidy }}</td>
                  <td></td>
                </tr>
                <tr v-for="(item, index) in mainPipes" :key="`main-${index}`">
                  <td>  田間主管(L{{ index + 1 }})</td>
                  <td></td>
                  <td class="text-center">{{ item.unit }}</td>
                  <td class="text-center">{{ item.quantity }}</td>
                  <td class="text-center">{{ item.unitPrice }}</td>
                  <td class="text-center">{{ item.totalPrice }}</td>
                  <td>{{ item.remark }}</td>
                </tr>
                <tr v-for="(item, index) in irrigationSystem" :key="`irrigation-${index}`">
                  <td>{{ item.name }}</td>
                  <td></td>
                  <td class="text-center">{{ item.unit }}</td>
                  <td class="text-center">{{ item.quantity }}</td>
                  <td class="text-center">{{ item.unitPrice }}</td>
                  <td class="text-center">{{ item.totalPrice }}</td>
                  <td>
                    <v-table density="compact" style="background-color: transparent">
                      <thead>
                        <tr>
                          <th style="width: 65px">項目</th>
                          <th style="width: 100px">材料名稱</th>
                          <th style="width: 30px">規格</th>
                          <th style="width: 30px">數量</th>
                        </tr>
                      </thead>
                      <tbody>
                        <tr>
                          <td colspan="4" class="font-weight-medium pa-0">1. 主管组</td>
                        </tr>
                        <tr v-for="item in irrigationSystem[index].remark.mainGroup" :key="item.id">
                          <td>{{ item.id }}</td>
                          <td>{{ item.name }}</td>
                          <td>{{ item.specification }}</td>
                          <td>{{ item.quantity }}</td>
                        </tr>
                        <tr>
                          <td colspan="4" class="font-weight-medium pa-0">2. 支管组</td>
                        </tr>
                        <tr v-for="item in irrigationSystem[index].remark.branchGroup" :key="item.id">
                          <td>{{ item.id }}</td>
                          <td>{{ item.name }}</td>
                          <td>{{ item.specification }}</td>
                          <td>{{ item.quantity }}</td>
                        </tr>
                        <tr>
                          <td colspan="4" class="font-weight-medium pa-0">3. 末端设施</td>
                        </tr>
                        <tr v-for="item in irrigationSystem[index].remark.endDevices" :key="item.id">
                          <td>{{ item.id }}</td>
                          <td>{{ item.name }}</td>
                          <td>{{ item.specification }}</td>
                          <td>{{ item.quantity }}</td>
                        </tr>
                      </tbody>
                    </v-table>
                  </td>
                </tr>
                <tr>
                  <td class="font-weight-medium">B.灌溉調控設施</td>
                  <td>依計畫補助標準</td>
                  <td class="text-center"></td>
                  <td class="text-center"></td>
                  <td class="text-center"></td>
                  <td class="text-center"></td>
                  <td></td>
                </tr>
                <tr v-for="(item, index) in controlFacilities" :key="`control-${index}`">
                  <td>  {{ item.name }}</td>
                  <td></td>
                  <td class="text-center">{{ item.unit }}</td>
                  <td class="text-center">{{ item.quantity }}</td>
                  <td class="text-center">{{ item.unitPrice }}</td>
                  <td class="text-center">{{ item.totalPrice }}</td>
                  <td>{{ item.remark }}</td>
                </tr>
                <tr>
                  <td class="font-weight-medium">C.規劃設計費</td>
                  <td>A*2.0%</td>
                  <td class="text-center"></td>
                  <td class="text-center">1</td>
                  <td class="text-center"></td>
                  <td class="text-center">{{ localFormData.designFee }}</td>
                  <td></td>
                </tr>
                <tr class="bg-grey-lighten-4">
                  <td colspan="5" class="text-right font-weight-bold">合計</td>
                  <td class="text-center font-weight-bold">{{ localFormData.totalBudget }}</td>
                  <td>新臺幣 {{ amountInWords }}元整 {{ isAboriginalAreaText }}</td>
                </tr>
              </tbody>
            </v-table>
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
            @click="goToPreviousStep"
            rounded="pill"
          >
            <v-icon start>mdi-arrow-left</v-icon>
            上一步
          </v-btn>

          <v-btn
            color="green-darken-1"
            @click="goToNextStep"
            size="large"
            rounded="pill"
          >
            下一步
            <v-icon end>mdi-arrow-right</v-icon>
          </v-btn>
        </div>
      </div>
    </v-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, watch, computed } from 'vue';

const props = defineProps({
  formData: {
    type: Object,
    default: () => ({})
  },
  currentStep: {
    type: Number,
    required: true
  }
});

// Use correct event name `go-back` to match edit.vue
const emit = defineEmits(['update:formData', 'validated', 'go-back']);

// Set default valid state to true for demo
const localValid = ref(true);
const form = ref(null);

// Create isValid computed property that always returns true for demo
const isValid = computed(() => true);

// 本地表单数据
const localFormData = reactive({
  applicationYear: '',  // 申請年度
  caseNumber: '',       // 案號
  applicantName: '',    // 農戶姓名
  applicantAddress: '', // 農戶地址
  facilityLocation: '', // 設施地段
  facilityNumber: '',   // 設施地號
  facilityArea: '',     // 設施面積
  facilityType: '',     // 設施型式

  pipeLineSubsidy: '8,704',
  facilitySubsidy: '4,500',
  designFee: '174',
  totalBudget: '13,378',

  isAboriginalArea: false,

  // Always set to true for demo
  valid: true
});

// 將金額轉換為中文大寫
const amountInWords = computed(() => {
  const amount = parseInt(localFormData.totalBudget.replace(/,/g, ''));
  if (isNaN(amount)) return '零';

  const digits = ['零', '壹', '贰', '参', '肆', '伍', '陸', '柒', '捌', '玖'];
  const units = ['', '拾', '佰', '仟', '萬', '拾', '佰', '仟', '億'];

  let result = '';
  const amountStr = amount.toString();

  for (let i = 0; i < amountStr.length; i++) {
    const digit = parseInt(amountStr[i]);
    const unit = units[amountStr.length - 1 - i];

    if (digit === 0) {
      if (i === amountStr.length - 1 || amountStr[i + 1] !== '0') {
        result += digits[digit];
      }
    } else {
      result += digits[digit] + unit;
    }
  }

  return result;
});

const isAboriginalAreaText = computed(() => {
  return localFormData.isAboriginalArea ? '(原民地+10%)' : '';
});

// 設施資料
// 主管
const mainPipes = ref([
  { name: '田間主管1', remark: '164公尺', quantity: 41, unitPrice: 103, totalPrice: '4,223', unit: '支' },
  { name: '田間主管2', remark: '-', quantity: '-', unitPrice: '-', totalPrice: '-', unit: '-' }
]);

// 灌溉系統
const irrigationSystem = ref([
  { name: '灌溉系統', quantity: 1, unitPrice: '-', totalPrice: '4,481', unit: '套', remark: {
    mainGroup: [
      { id: '1-1', name: '塞口', specification: '1/2"', quantity: '*1' }
    ],
    branchGroup: [
      { id: '2-1', name: 'PVC', specification: '1"', quantity: '*4' },
      { id: '2-2', name: '制水閥', specification: '1"', quantity: '*4' },
      { id: '2-3', name: '塞口', specification: '1"', quantity: '*4' }
    ],
    endDevices: [
      { id: '3-1', name: '單口噴頭-塑鋼', specification: '1/2"', quantity: '*104' }
    ]
  }},
]);

// 支管组
const branchPipes = ref([
  { name: 'PVC', specification: '1" *4', quantity: 1, unitPrice: '', totalPrice: '', unit: '支' },
  { name: '制水閥', specification: '1" *4', quantity: 1, unitPrice: '', totalPrice: '', unit: '只' },
  { name: '塞口', specification: '1" *4', quantity: 1, unitPrice: '', totalPrice: '', unit: '只' }
]);

// 末端設施
const endDevices = ref([
  { name: '單口噴頭-塑鋼', specification: '1/2" *104', quantity: 1, unitPrice: '', totalPrice: '4,481', unit: '只' }
]);

// 灌溉調控設施
const controlFacilities = ref([
  { name: '動力設施', specification: '', quantity: 1, unitPrice: '4500', totalPrice: '4,500', unit: '台', remark: '馬達+抽水機*1' },
  { name: '調蓄設施', specification: '', quantity: '', unitPrice: '', totalPrice: '', unit: '座', remark: '' },
  { name: '調節控制設施', specification: '', quantity: '', unitPrice: '', totalPrice: '', unit: '台', remark: '' }
]);

// 文件列印
const printDocument = (documentType: string) => {
  console.log(`列印檔案: ${documentType}`);
  // Mock print logic for demo
};

// 上一步 - Modified to use 'go-back' to match edit.vue
const goToPreviousStep = () => {
  // Always update data before going back
  updateFormData();

  console.log('Going back from step 6');
  emit('go-back');
};

// 下一步 - Simplified for localStorage demo
const goToNextStep = () => {
  // Always update data before moving forward
  updateFormData();

  console.log('Emitting validated event for step 6');
  emit('validated', { valid: true, step: 6 });
};

// 更新父組件資料 - Modified to always set valid: true for demo
const updateFormData = () => {
  emit('update:formData', {
    ...props.formData,
    ...localFormData,
    valid: true // Always set to true for demo
  });
};

// 資料初始化 - Enhanced for better demo experience
onMounted(() => {
  // 從父組件獲取初始化資料
  if (props.formData) {
    // 基本資訊
    Object.keys(localFormData).forEach(key => {
      if (props.formData[key] !== undefined) {
        localFormData[key] = props.formData[key];
      }
    });

    // Special handling for nested properties
    if (props.formData.isAboriginalArea !== undefined) {
      localFormData.isAboriginalArea = props.formData.isAboriginalArea;
    }
  }

  // Set default values if not already set
  if (!localFormData.applicationYear) {
    localFormData.applicationYear = new Date().getFullYear().toString();
  }

  if (!localFormData.caseNumber) {
    // Use the case number from URL or generate a dummy one
    const urlParams = new URLSearchParams(window.location.search);
    const idParam = urlParams.get('id');
    localFormData.caseNumber = idParam || '113010001';
  }

  if (!localFormData.applicantName) {
    // Try to get from other steps or use default
    localFormData.applicantName = props.formData.name || '林嘉寶';
  }

  // 拼接完整地址
  if (!localFormData.applicantAddress) {
    if (props.formData.address) {
      localFormData.applicantAddress = props.formData.address;
    } else {
      // 嘗試從步驟1獲取地址
      const county = props.formData.county || '';
      const town = props.formData.town || '';
      const village = props.formData.village || '';
      const detailAddress = props.formData.address || '';
      localFormData.applicantAddress = `${county}${town}${village}${detailAddress}`;

      // If still empty, use default
      if (!localFormData.applicantAddress) {
        localFormData.applicantAddress = '嘉義縣竹崎鄉瓦厝埔段123號';
      }
    }
  }

  // 設施資訊 - Try to get from step2 or use defaults
  if (!localFormData.facilityLocation) {
    if (props.formData.step2) {
      const county = props.formData.step2.addressCounty || '';
      const town = props.formData.step2.addressTown || '';
      localFormData.facilityLocation = `${county}${town}瓦厝埔段`;
    } else if (props.formData.addressCounty && props.formData.addressTown) {
      localFormData.facilityLocation = `${props.formData.addressCounty}${props.formData.addressTown}瓦厝埔段`;
    } else {
      localFormData.facilityLocation = '嘉義縣竹崎鄉瓦厝埔段';
    }
  }

  if (!localFormData.facilityNumber) {
    localFormData.facilityNumber = props.formData.landNumber || props.formData.step2?.landNumber || '0966-0001';
  }

  if (!localFormData.facilityArea) {
    localFormData.facilityArea = props.formData.landAreaHa || props.formData.step2?.landAreaHa || '0.8455';
  }

  if (!localFormData.facilityType) {
    // Try to construct from step4 data or use default
    if (props.formData.step4) {
      const installation = props.formData.step4.installationType || '';
      const irrigation = props.formData.step4.irrigationType || '';
      localFormData.facilityType = `${installation}${irrigation}系統`;
    } else if (props.formData.installationType && props.formData.irrigationType) {
      localFormData.facilityType = `${props.formData.installationType}${props.formData.irrigationType}系統`;
    } else {
      localFormData.facilityType = '地表定置式噴頭式系統';
    }
  }

  // 從父組件獲取設施細節 (pipes from step4)
  if (props.formData.pipes && props.formData.pipes.length > 0) {
    try {
      const pipeData = props.formData.pipes;

      // 分類整理資料
      mainPipes.value = pipeData.filter(p => p.type === 'main').map(p => ({
        name: '田間主管',
        length: p.length || '164',
        quantity: p.quantity || 0,
        unitPrice: p.unitPrice || 0,
        totalPrice: (typeof p.totalPrice === 'number' ? p.totalPrice.toLocaleString() : p.totalPrice) || '',
        unit: p.specification?.includes('支') ? '支' : '個'
      }));

      if (mainPipes.value.length === 0) {
        // Keep default if no data
        mainPipes.value = [
          { name: '田間主管1', remark: '164公尺', quantity: 41, unitPrice: 103, totalPrice: '4,223', unit: '支' }
        ];
      }

      branchPipes.value = pipeData.filter(p => p.type === 'branch').map(p => ({
        name: p.name || 'PVC',
        specification: p.specification || '',
        quantity: p.quantity || 0,
        unitPrice: p.unitPrice || 0,
        totalPrice: (typeof p.totalPrice === 'number' ? p.totalPrice.toLocaleString() : p.totalPrice) || '',
        unit: p.specification?.includes('只') ? '只' : '支'
      }));

      endDevices.value = pipeData.filter(p => p.type === 'end').map(p => ({
        name: p.name || '',
        specification: p.specification || '',
        quantity: p.quantity || 0,
        unitPrice: p.unitPrice || 0,
        totalPrice: (typeof p.totalPrice === 'number' ? p.totalPrice.toLocaleString() : p.totalPrice) || '',
        unit: p.specification?.includes('只') ? '只' : '个'
      }));
    } catch (error) {
      console.error('Error processing pipe data:', error);
    }
  }

  // 獲取控制設施資料 (facilities from step3)
  if (props.formData.facilities && props.formData.facilities.length > 0) {
    try {
      controlFacilities.value = props.formData.facilities.map(f => ({
        name: f.typeLabel || '',
        specification: '',
        quantity: f.quantity || 0,
        unitPrice: (typeof f.unitPrice === 'number' ? f.unitPrice.toLocaleString() : f.unitPrice) || '',
        totalPrice: (typeof f.totalPrice === 'number' ? f.totalPrice.toLocaleString() : f.totalPrice) || '',
        unit: f.type === 'power' ? '台' : (f.type === 'storage' ? '座' : '台'),
        remark: f.remark || f.name
      }));
    } catch (error) {
      console.error('Error processing facility data:', error);
    }
  }

  // Calculate subsidy amounts based on previous step data
  // This is a simplified calculation for demo purposes
  try {
    let pipelineTotal = 0;
    let facilityTotal = 0;

    // Sum pipeline costs from pipes array
    if (props.formData.pipes) {
      pipelineTotal = props.formData.pipes.reduce((sum, pipe) =>
        sum + (typeof pipe.totalPrice === 'number' ? pipe.totalPrice : 0), 0);
    }

    // Sum facility costs from facilities array
    if (props.formData.facilities) {
      facilityTotal = props.formData.facilities.reduce((sum, facility) =>
        sum + (typeof facility.totalPrice === 'number' ? facility.totalPrice : 0), 0);
    }

    // Update values if we have valid data
    if (pipelineTotal > 0) {
      localFormData.pipeLineSubsidy = pipelineTotal.toLocaleString();
    }

    if (facilityTotal > 0) {
      localFormData.facilitySubsidy = facilityTotal.toLocaleString();
    }

    // Calculate design fee (2% of pipeline subsidy)
    const pipelineValue = parseInt(localFormData.pipeLineSubsidy.replace(/,/g, '')) || 0;
    localFormData.designFee = Math.round(pipelineValue * 0.02).toLocaleString();

    // Calculate total budget
    const facilityValue = parseInt(localFormData.facilitySubsidy.replace(/,/g, '')) || 0;
    const designValue = parseInt(localFormData.designFee.replace(/,/g, '')) || 0;
    const total = pipelineValue + facilityValue + designValue;

    if (total > 0) {
      localFormData.totalBudget = total.toLocaleString();
    }
  } catch (error) {
    console.error('Error calculating subsidies:', error);
  }

  // Initial update to parent
  updateFormData();
});

// 監聽父組件資料變化 - Simplified for demo
watch(() => props.formData, (newVal) => {
  if (newVal) {
    // Update local data without complex logic for demo
    updateFormData();
  }
}, { deep: true });
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

.bg-amber-lighten-5 {
  background-color: #FFF8E1 !important;
}

.border-amber {
  border-color: #FFD54F !important;
  border-width: 1px;
  border-style: solid;
}

.bg-yellow-lighten-3 {
  background-color: #FFF59D !important;
}

.v-table {
  background-color: white;
}

.v-table th {
  font-weight: 600;
  color: rgba(0, 0, 0, 0.7);
}

.inner-table {
  border: none !important;
  font-size: 0.875rem;
}

.inner-table th,
.inner-table td {
  padding: 2px 4px !important;
  border-bottom: 1px solid rgba(0, 0, 0, 0.12) !important;
}

.inner-table th {
  background-color: rgba(0, 0, 0, 0.03);
  font-weight: 500;
  font-size: 0.8rem;
}

.inner-table tr:last-child td {
  border-bottom: none !important;
}

.report-table {
  width: 100%;
  border-collapse: collapse;
}

.report-table td {
  border: 1px solid rgba(0, 0, 0, 0.12);
  padding: 10px;
}

.report-btn {
  min-width: 150px;
  flex: 1;
  max-width: 30%;
}.preview-table {
  width: 100%;
  border-collapse: collapse;
}

.preview-table td {
  border: 1px solid rgba(0, 0, 0, 0.12);
  padding: 10px;
}

.preview-table td.font-weight-medium {
  background-color: rgba(255, 224, 130, 0.15);
}

.budget-table {
  width: 100%;
  border-collapse: collapse;
}

.budget-table td {
  border: 1px solid rgba(0, 0, 0, 0.12);
  padding: 8px;
}

.budget-table .total-row {
  background-color: rgba(255, 224, 130, 0.3);
}

.facility-table {
  width: 100%;
  border-collapse: collapse;
}

.facility-table th,
.facility-table td {
  border: 1px solid rgba(0, 0, 0, 0.12);
}

.facility-table th {
  background-color: rgba(0, 0, 0, 0.05);
  font-weight: 600;
  padding: 10px;
}

.facility-table td {
  padding: 8px;
}.report-table {
  width: 100%;
  border-collapse: collapse;
}

.report-table td {
  border: 1px solid rgba(0, 0, 0, 0.12);
  padding: 10px;
}

.report-btn {
  min-width: 150px;
  flex: 1;
  max-width: 30%;
}.preview-table {
  width: 100%;
  border-collapse: collapse;
}

.preview-table td {
  border: 1px solid rgba(0, 0, 0, 0.12);
  padding: 10px;
}

.preview-table td.font-weight-medium {
  background-color: rgba(255, 224, 130, 0.15);
}
</style>
