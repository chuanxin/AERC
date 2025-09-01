<template>
  <div
    ref="stepContent"
    class="step-content"
  >
    <!-- 設施明細區 -->
    <v-card
      class="mb-4"
      flat
    >
      <v-card-text class="pt-4 pb-0">
        <v-card variant="outlined">
          <v-card-title class="bg-light-blue-lighten-4 d-flex align-center py-2 px-4">
            <v-icon
              class="me-2"
              size="small"
            >
              mdi-pipe
            </v-icon>
            <span class="text-subtitle-1 font-weight-medium">本案設施</span>
          </v-card-title>

          <v-card-text class="pa-4">
            <div class="facility-table-container">
              <v-table
                class="facility-table border"
                density="compact"
              >
                <thead class="bg-grey-lighten-3">
                  <tr>
                    <th>設施項目</th>
                    <th>說明</th>
                    <th class="text-center">
                      單位
                    </th>
                    <th class="text-center">
                      數量
                    </th>
                    <th class="text-center">
                      單價
                    </th>
                    <th class="text-center">
                      總價
                    </th>
                    <th>備註</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td class="font-weight-medium">
                      A.田間管路設施費
                    </td>
                    <td />
                    <td class="text-center">
                      全
                    </td>
                    <td class="text-center" />
                    <td class="text-center" />
                    <td class="text-center">
                      {{ pipeLineTotal }}
                    </td>
                    <td />
                  </tr>
                  <tr
                    v-for="(item, index) in mainPipes"
                    :key="`main-${index}`"
                  >
                    <td>  田間主管(L{{ index + 1 }})</td>
                    <td />
                    <td class="text-center">
                      {{ item.unit }}
                    </td>
                    <td class="text-center">
                      {{ item.quantity }}
                    </td>
                    <td class="text-center">
                      {{ item.unitPrice }}
                    </td>
                    <td class="text-center">
                      {{ item.totalPrice }}
                    </td>
                    <td>{{ item.remark }}</td>
                  </tr>
                  <tr
                    v-for="(item, index) in irrigationSystem"
                    :key="`irrigation-${index}`"
                  >
                    <td>{{ item.name }}</td>
                    <td />
                    <td class="text-center">
                      {{ item.unit }}
                    </td>
                    <td class="text-center">
                      {{ item.quantity }}
                    </td>
                    <td class="text-center">
                      {{ item.unitPrice }}
                    </td>
                    <td class="text-center">
                      {{ item.totalPrice }}
                    </td>
                    <td>
                      詳如數量表
                    <!-- <v-table density="compact" style="background-color: transparent">
                      <thead>
                      </thead>
                      <tbody>
                      </tbody>
                    </v-table> -->
                    </td>
                  </tr>
                  <tr>
                    <td class="font-weight-medium">
                      B.灌溉調控設施
                    </td>
                    <td>依計畫補助標準</td>
                    <td class="text-center" />
                    <td class="text-center" />
                    <td class="text-center" />
                    <td class="text-center" />
                    <td />
                  </tr>
                  <tr
                    v-for="(item, index) in controlFacilities"
                    :key="`control-${index}`"
                  >
                    <td>  {{ item.name }}</td>
                    <td>{{ item.facilityName }}</td>
                    <td class="text-center">
                      {{ item.unit }}
                    </td>
                    <td class="text-center">
                      {{ item.quantity }}
                    </td>
                    <td class="text-center">
                      {{ item.unitPrice }}
                    </td>
                    <td class="text-center">
                      {{ item.totalPrice }}
                    </td>
                    <td>{{ item.remark }}</td>
                  </tr>
                  <tr>
                    <td class="font-weight-medium">
                      C.規劃設計費
                    </td>
                    <td>A*2.0%</td>
                    <td class="text-center" />
                    <td class="text-center">
                      1
                    </td>
                    <td class="text-center" />
                    <td class="text-center">
                      {{ designFee }}
                    </td>
                    <td />
                  </tr>
                  <tr class="bg-grey-lighten-4">
                    <td
                      colspan="5"
                      class="text-right font-weight-bold"
                    >
                      合計
                    </td>
                    <td class="text-center font-weight-bold">
                      {{ totalBudget }}
                    </td>
                    <td class="amount-in-words">
                      <span class="nowrap-text">新臺幣 {{ amountInWords }}元整 {{ isAboriginalAreaText }}</span>
                    </td>
                  </tr>
                </tbody>
              </v-table>
            </div>
          </v-card-text>
        </v-card>
      </v-card-text>
    </v-card>

    <v-card
      class="mb-0 pa-0"
      flat
    >
      <v-card-text class="pb-0 pt-0">
        <v-form
          ref="form"
          v-model="localValid"
          @submit.prevent
        >
          <!-- 補助申請基本資訊區 -->
          <!-- <v-card
            class="mb-4"
            variant="outlined"
          >
            <v-card-title class="bg-light-blue-lighten-4 d-flex align-center py-2 px-4">
              <v-icon
                class="me-2"
                size="small"
              >
                mdi-file-document
              </v-icon>
              <span class="text-subtitle-1 font-weight-medium">
                補助申請資料預覽
              </span>
            </v-card-title>

            <v-card-text class="pa-4">
              <v-sheet
                class="pa-3 rounded"
                color="bg-amber-lighten-5 border border-amber"
              >
                <v-table
                  class="preview-table"
                  style="background-color: transparent"
                  density="compact"
                >
                  <tbody>
                    <tr>
                      <td
                        class="font-weight-medium text-center"
                        style="width: 15%"
                      >
                        申請年度
                      </td>
                      <td style="width: 35%">
                        {{ displayApplicationYear }}
                      </td>
                      <td
                        class="font-weight-medium text-center"
                        style="width: 15%"
                      >
                        案號
                      </td>
                      <td style="width: 35%">
                        {{ displayCaseNumber }}
                      </td>
                    </tr>
                    <tr>
                      <td class="font-weight-medium text-center">
                        農戶姓名
                      </td>
                      <td>
                        {{ displayApplicantName }}
                      </td>
                      <td class="font-weight-medium text-center">
                        農戶住址
                      </td>
                      <td>
                        {{ displayApplicantAddress }}
                      </td>
                    </tr>
                    <tr>
                      <td class="font-weight-medium text-center">
                        設施地段
                      </td>
                      <td>
                        {{ displayFacilityLocation }}
                      </td>
                      <td class="font-weight-medium text-center">
                        設施地號
                      </td>
                      <td>
                        {{ displayFacilityNumber }}
                      </td>
                    </tr>
                    <tr>
                      <td class="font-weight-medium text-center">
                        設施面積
                      </td>
                      <td>
                        {{ displayFacilityArea }}公頃
                      </td>
                      <td class="font-weight-medium text-center">
                        設施型式
                      </td>
                      <td>
                        {{ displayFacilityType }}
                      </td>
                    </tr>
                  </tbody>
                </v-table>
              </v-sheet>
            </v-card-text>
          </v-card> -->

          <!-- 農戶補助明細區 -->
          <v-card
            class="mb-4"
            variant="outlined"
          >
            <v-card-title class="bg-light-blue-lighten-4 d-flex align-center py-2 px-4">
              <v-icon
                class="me-2"
                size="small"
              >
                mdi-calculator
              </v-icon>
              <span class="text-subtitle-1 font-weight-medium">農戶補助明細</span>
            </v-card-title>

            <v-card-text class="pa-4">
              <v-sheet
                class="pa-3 rounded"
                color="bg-amber-lighten-5 border border-amber"
              >
                <v-table
                  class="budget-table"
                  style="background-color: transparent"
                  density="compact"
                >
                  <tbody>
                    <!-- 農戶配合款 -->
                    <tr>
                      <td
                        class="font-weight-medium text-center"
                        colspan="2"
                        style="width: 25%"
                      >
                        農戶配合款
                      </td>
                      <td class="text-center">
                        {{ displayFarmerContribution }}
                      </td>
                    </tr>

                    <!-- 政府補助款 -->
                    <tr>
                      <td
                        class="font-weight-medium text-center"
                        rowspan="3"
                        style="vertical-align: middle"
                      >
                        政府<br>補助款
                      </td>
                      <td
                        class="font-weight-medium text-center"
                        rowspan="2"
                        style="vertical-align: middle"
                      >
                        農戶<br>請領款
                      </td>
                      <td class="text-center">
                        A項補助費：{{ pipeLineSubsidy }}
                      </td>
                    </tr>
                    <tr>
                      <td class="text-center">
                        B項補助費：{{ facilitySubsidy }}
                      </td>
                    </tr>
                    <tr>
                      <td class="font-weight-medium text-center">
                        規劃設計費
                      </td>
                      <td class="text-center">
                        {{ designFee }}
                      </td>
                    </tr>

                    <!-- 總計 -->
                    <tr class="total-row">
                      <td
                        class="font-weight-medium text-center"
                        colspan="2"
                      >
                        本設施預算總計
                      </td>
                      <td class="text-center font-weight-medium">
                        {{ totalBudget }}
                      </td>
                    </tr>
                  </tbody>
                </v-table>
              </v-sheet>
            </v-card-text>
          </v-card>

          <!-- 報表列印區 -->
          <v-card variant="outlined">
            <v-card-title class="bg-light-blue-lighten-4 d-flex align-center py-2 px-4">
              <v-icon
                class="me-2"
                size="small"
              >
                mdi-printer
              </v-icon>
              <span class="text-subtitle-1 font-weight-medium">報表列印</span>
            </v-card-title>

            <v-card-text class="pa-4">
              <v-sheet
                class="pa-3 rounded"
                color="grey-lighten-5"
              >
                <v-row
                  no-gutters
                  align-content="space-between"
                >
                  <v-col
                    class="me-auto"
                    cols="auto"
                  >
                    <v-btn
                      variant="outlined"
                      color="primary"
                      prepend-icon="mdi-file-document-outline"
                      class="ml-4 mr-4 mb-2"
                      @click="printDocument('application')"
                    >
                      灌溉系統設計標準
                    </v-btn>
                  </v-col>
                  <v-col
                    class="me-auto"
                    cols="auto"
                  >
                    <v-btn
                      variant="outlined"
                      color="primary"
                      prepend-icon="mdi-file-document-outline"
                      class="ml-4 mr-4 mb-2"
                      @click="printDocument('completion')"
                    >
                      結案申報書
                    </v-btn>
                  </v-col>
                  <v-col
                    class="me-auto"
                    cols="auto"
                  >
                    <v-btn
                      variant="outlined"
                      color="primary"
                      prepend-icon="mdi-file-document-outline"
                      class="ml-4 mr-4 mb-2"
                      @click="printDocument('pledge')"
                    >
                      補助切結書
                    </v-btn>
                  </v-col>
                  <v-col
                    class="me-auto"
                    cols="auto"
                  >
                    <v-btn
                      variant="outlined"
                      color="primary"
                      prepend-icon="mdi-file-document-outline"
                      class="ml-4 mr-4 mb-2"
                      @click="printDocument('planning')"
                    >
                      規劃委託書
                    </v-btn>
                  </v-col>
                  <v-col
                    class="me-auto"
                    cols="auto"
                  >
                    <v-btn
                      variant="outlined"
                      color="primary"
                      prepend-icon="mdi-file-document-outline"
                      class="ml-4 mr-4 mb-2"
                      @click="printDocument('budget')"
                    >
                      工程預算書
                    </v-btn>
                  </v-col>
                  <v-spacer />
                </v-row>
              </v-sheet>
            </v-card-text>
          </v-card>
        </v-form>
      </v-card-text>
    </v-card>
  </div>
</template>

<script setup lang="ts">
/* eslint-disable @typescript-eslint/no-explicit-any */
import { useGrantsStore } from '@/stores/grants';
import { useRoute } from 'vue-router';
import type { PropType } from 'vue';

// Step6 不再維護本地設施資料，所有資料都直接從 computed 讀取

// Props definition
const props = defineProps({
  formData: {
    type: Object as PropType<Record<string, any>>,
    required: true,
    default: () => ({})
  },
  currentStep: {
    type: Number,
    required: true
  }
});

// Event emitters
const emit = defineEmits(['update:formData', 'validated', 'go-back']);

// Use the grants store and route
const grantsStore = useGrantsStore();
const route = useRoute();

// Form ref and validation state
const form = ref<any>(null);
const localValid = ref(true);

// Computed property for farmer contribution - 從 grantsStore 讀取
const displayFarmerContribution = computed(() => {
  const step6Data = getStepDataSafely(6);
  return step6Data?.farmerContribution || '0';
});

// 本地表單數據 - 僅保留必要的表單欄位
const localFormData = reactive<Record<string, any>>({
  valid: true // Always valid for seamless navigation
});

// 智慧資料來源選擇器：透過案件號比對確保 formData 歸屬正確
const getStepDataSafely = (step: number) => {
  const currentCaseNumber = route.query.id as string;
  
  // 確保只處理當前案件的資料
  if (!currentCaseNumber || grantsStore.caseNumber !== currentCaseNumber) {
    return null;
  }
  
  const formData = grantsStore.formData[step];
  const allStepsData = (grantsStore.currentGrant?.active_version as any)?.all_steps_data?.steps?.[step.toString()];
  
  // 檢查 formData 是否屬於當前案件（透過 _caseNumber 欄位比對）
  const formDataCaseNumber = formData?._caseNumber;
  const isFormDataValid = formDataCaseNumber === currentCaseNumber;
  
  if (isFormDataValid && formData && Object.keys(formData).length > 1) { // >1 因為至少有 _caseNumber
    console.log(`✅ Step6: Using formData for step ${step} (case: ${formDataCaseNumber})`);
    return formData; // 使用 formData（即時同步）
  }
  
  // 否則使用 all_steps_data（持久化資料）
  if (allStepsData && Object.keys(allStepsData).length > 0) {
    console.log(`📚 Step6: Using all_steps_data for step ${step} (formData case: ${formDataCaseNumber}, current: ${currentCaseNumber})`);
    return allStepsData;
  }
  
  return null;
};

// Computed properties for facility data - 直接從 grantsStore 讀取資料，不維護本地副本
const mainPipes = computed(() => {
  const step4Data = getStepDataSafely(4);
  if (!step4Data || Object.keys(step4Data).length === 0) return [];

  const mainPipeData = [];

  // Main pipe 1
  if (step4Data.mainPipeQuantity && parseInt(step4Data.mainPipeQuantity as string) > 0) {
    const mainPipe1Total = parseInt(step4Data.mainPipeQuantity as string || '0') *
                          parseFloat(step4Data.mainPipeUnitPrice as string || '0');
    mainPipeData.push({
      name: '田間主管1',
      quantity: step4Data.mainPipeQuantity as string,
      unitPrice: step4Data.mainPipeUnitPrice ? parseFloat(step4Data.mainPipeUnitPrice as string).toLocaleString() : '-',
      totalPrice: mainPipe1Total > 0 ? mainPipe1Total.toLocaleString() : '-',
      unit: '支',
      remark: step4Data.mainPipeMaterialId ? `管材長度: ${step4Data.mainPipeLength} 公尺` : '-'
    });
  }

  // Main pipe 2
  if (step4Data.mainPipe2Enabled && step4Data.mainPipe2Quantity && parseInt(step4Data.mainPipe2Quantity as string) > 0) {
    const mainPipe2Total = parseInt(step4Data.mainPipe2Quantity as string || '0') *
                          parseFloat(step4Data.mainPipe2UnitPrice as string || '0');
    mainPipeData.push({
      name: '田間主管2',
      quantity: step4Data.mainPipe2Quantity as string,
      unitPrice: step4Data.mainPipe2UnitPrice ? parseFloat(step4Data.mainPipe2UnitPrice as string).toLocaleString() : '-',
      totalPrice: mainPipe2Total > 0 ? mainPipe2Total.toLocaleString() : '-',
      unit: '支',
      remark: step4Data.mainPipe2MaterialId ? `管材長度: ${step4Data.mainPipe2Length} 公尺` : '-'
    });
  }

  // Legacy pipes support
  if (mainPipeData.length === 0 && step4Data.pipes && Array.isArray(step4Data.pipes)) {
    const legacyMainPipes = step4Data.pipes.filter((p: any) => p.type === 'main' || (p.groupId === 1 && p.module === '主管'));
    return legacyMainPipes.map((p: any) => ({
      name: p.name || '田間主管',
      quantity: p.quantity,
      unitPrice: p.unitPrice,
      totalPrice: typeof p.totalPrice === 'number' ? p.totalPrice.toLocaleString() : p.totalPrice,
      unit: '支',
      remark: p.specification || '-'
    }));
  }

  return mainPipeData;
});

const irrigationSystem = computed(() => {
  const step4Data = getStepDataSafely(4);
  if (!step4Data?.pipes || !Array.isArray(step4Data.pipes)) return [];

  const pipes = step4Data.pipes as any[];

  // 建立灌溉系統組件
  const irrigationComponents = {
    mainGroup: [] as Array<{id: string, name: string, specification: string, quantity: string}>,
    branchGroup: [] as Array<{id: string, name: string, specification: string, quantity: string}>,
    endDevices: [] as Array<{id: string, name: string, specification: string, quantity: string}>
  };

  pipes.forEach((pipe: any, index: number) => {
    const component = {
      id: `${pipe.groupId}-${index}`,
      name: pipe.matname || pipe.name || '未知組件',
      specification: pipe.specification || `${pipe.spec1 || ''} ${pipe.spec2 || ''} ${pipe.spec3 || ''}`.trim() || '-',
      quantity: `*${pipe.matamount || pipe.quantity || 0}`
    };

    if (pipe.groupId === 1 && pipe.module !== '主管') {
      irrigationComponents.mainGroup.push(component);
    } else if (pipe.groupId === 2) {
      irrigationComponents.branchGroup.push(component);
    } else if ([3, 4, 5, 6, 7, 8].includes(pipe.groupId)) {
      irrigationComponents.endDevices.push(component);
    }
  });

  // 計算灌溉系統總價
  const irrigationTotal = pipes
    .filter((p: any) => {
      if ([2, 3, 4, 5, 6, 7, 8].includes(p.groupId)) return true;
      if (p.groupId === 1) return p.module !== '主管';
      return false;
    })
    .reduce((sum: number, pipe: any) => {
      return sum + (typeof pipe.totalPrice === 'number'
                   ? pipe.totalPrice
                   : parseInt(pipe.totalPrice || '0'));
    }, 0);

  if (irrigationComponents.mainGroup.length > 0 ||
      irrigationComponents.branchGroup.length > 0 ||
      irrigationComponents.endDevices.length > 0) {
    return [{
      name: '灌溉系統',
      quantity: '全',
      unitPrice: '-',
      totalPrice: irrigationTotal > 0 ? irrigationTotal.toLocaleString() : '-',
      unit: '式',
      remark: irrigationComponents
    }];
  }

  return [];
});

const controlFacilities = computed(() => {
  const step3Data = getStepDataSafely(3);
  if (!step3Data?.facilities || !Array.isArray(step3Data.facilities)) return [];

  const facilities = step3Data.facilities as any[];
  return facilities.map((f: any) => ({
    name: f.typeLabel || f.name,
    facilityName: f.name, // 真正的設施名稱
    specification: '',
    quantity: f.quantity,
    unitPrice: typeof f.unitPrice === 'number' ? f.unitPrice.toLocaleString() : f.unitPrice,
    totalPrice: typeof f.totalPrice === 'number' ? f.totalPrice.toLocaleString() : f.totalPrice,
    unit: f.type === 'power' ? '台' : (f.type === 'storage' ? '座' : '台'),
    remark: f.remark || f.name
  }));
});

// Computed properties for calculated values
const pipeLineTotal = computed(() => {
  const step4Data = getStepDataSafely(4);
  if (!step4Data || Object.keys(step4Data).length === 0) return '0';

  let pipelineTotal = 0;
  let irrigationTotal = 0;

  // Main pipe calculation
  if (step4Data.mainPipeQuantity && step4Data.mainPipeUnitPrice) {
    pipelineTotal += parseInt(step4Data.mainPipeQuantity as string || '0') *
                    parseFloat(step4Data.mainPipeUnitPrice as string || '0');
  }

  if (step4Data.mainPipe2Enabled && step4Data.mainPipe2Quantity && step4Data.mainPipe2UnitPrice) {
    pipelineTotal += parseInt(step4Data.mainPipe2Quantity as string || '0') *
                    parseFloat(step4Data.mainPipe2UnitPrice as string || '0');
  }

  // Irrigation system calculation
  if (step4Data.pipes && Array.isArray(step4Data.pipes)) {
    irrigationTotal = step4Data.pipes
      .filter((p: any) => {
        if ([2, 3, 4, 5, 6, 7, 8].includes(p.groupId)) return true;
        if (p.groupId === 1) return p.module !== '主管';
        return false;
      })
      .reduce((sum: number, pipe: any) => {
        return sum + (typeof pipe.totalPrice === 'number'
                     ? pipe.totalPrice
                     : parseInt(pipe.totalPrice || '0'));
      }, 0);
  }

  return (pipelineTotal + irrigationTotal).toLocaleString();
});

const pipeLineSubsidy = computed(() => pipeLineTotal.value);

const facilitySubsidy = computed(() => {
  const step3Data = getStepDataSafely(3);
  if (!step3Data || Object.keys(step3Data).length === 0 || !step3Data?.facilities || !Array.isArray(step3Data.facilities)) return '0';

  const total = step3Data.facilities.reduce((sum: number, facility: any) => {
    return sum + (typeof facility.totalPrice === 'number'
                 ? facility.totalPrice
                 : parseInt(facility.totalPrice || '0'));
  }, 0);

  return total.toLocaleString();
});

const designFee = computed(() => {
  const pipelineValue = parseInt(pipeLineSubsidy.value.replace(/,/g, '')) || 0;
  return Math.round(pipelineValue * 0.02).toLocaleString();
});

const totalBudget = computed(() => {
  const pipelineValue = parseInt(pipeLineSubsidy.value.replace(/,/g, '')) || 0;
  const facilityValue = parseInt(facilitySubsidy.value.replace(/,/g, '')) || 0;
  const designValue = parseInt(designFee.value.replace(/,/g, '')) || 0;
  return (pipelineValue + facilityValue + designValue).toLocaleString();
});

// 將金額轉換為中文大寫
const amountInWords = computed(() => {
  const amount = parseInt(totalBudget.value.replace(/,/g, ''));
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
  // 優先從 currentGrant.all_steps_data 讀取，fallback 到 formData
  const step2Data = (grantsStore.currentGrant?.active_version as any)?.all_steps_data?.steps?.['2'] || grantsStore.formData[2];
  return step2Data?.isAboriginalArea ? '(原民地+10%)' : '';
});

// 文件列印
const printDocument = (documentType: string) => {
  console.log(`列印檔案: ${documentType}`);
  // Mock print logic for demo
};

// Computed properties for display data - 直接從 grantsStore 讀取，不維護本地副本
const displayCaseNumber = computed(() => {
  const currentCaseNumber = route.query.id as string;
  if (!currentCaseNumber || grantsStore.caseNumber !== currentCaseNumber) {
    return '';
  }
  return grantsStore.caseNumber || '';
});

const displayApplicantName = computed(() => {
  const step1Data = getStepDataSafely(1);
  return step1Data?.name || '';
});

const displayApplicantAddress = computed(() => {
  const step1Data = getStepDataSafely(1);
  if (!step1Data) return '';
  return [step1Data.county, step1Data.town, step1Data.village, step1Data.address]
    .filter(Boolean).join('');
});

const displayFacilityLocation = computed(() => {
  const step2Data = getStepDataSafely(2);
  if (!step2Data) return '';
  return [step2Data.addressCounty, step2Data.addressTown, step2Data.addressVillage]
    .filter(Boolean).join('');
});

const displayFacilityNumber = computed(() => {
  const step2Data = getStepDataSafely(2);
  return step2Data?.landNumber || '';
});

const displayFacilityArea = computed(() => {
  const step2Data = getStepDataSafely(2);
  return step2Data?.totalFacilityAreaHa || '';
});

const displayFacilityType = computed(() => {
  const step4Data = getStepDataSafely(4);
  if (!step4Data) return '';
  const parts = [step4Data.installationType, step4Data.irrigationType].filter(Boolean);
  return parts.length > 0 ? `${parts.join('')}系統` : '';
});
const displayApplicationYear = computed(() => {
  const currentCaseNumber = route.query.id as string;
  if (!currentCaseNumber || grantsStore.caseNumber !== currentCaseNumber) {
    return '';
  }
  
  // 從案號提取年度
  if (grantsStore.caseNumber?.includes('-')) {
    const yearPart = grantsStore.caseNumber.split('-')[0];
    if (/^\d{1,3}$/.test(yearPart)) return yearPart;
  }
  // 從收件日期提取年度
  const step1Data = getStepDataSafely(1);
  const receivedDate = step1Data?.receivedDate;
  if (receivedDate && typeof receivedDate === 'string') {
    const match = receivedDate.match(/^(\d{4})-/);
    if (match) {
      const westernYear = parseInt(match[1]);
      if (westernYear > 1911) return `${westernYear - 1911}`;
    }
  }
  // 使用當前年度作為備用
  return `${new Date().getFullYear() - 1911}`;
});

// 更新父組件數據 - Step6 只傳遞本地表單資料，不傳遞計算結果
const updateFormData = () => {
  emit('update:formData', {
    ...props.formData,
    ...localFormData,
    valid: true // Always true for seamless navigation
  });
};

// 案件切換監控 - 清理跨案件資料污染
watch(() => route.query.id, async (newCaseNumber, oldCaseNumber) => {
  if (newCaseNumber && newCaseNumber !== oldCaseNumber) {
    console.log('🔄 Step6: 案件切換偵測', { from: oldCaseNumber, to: newCaseNumber });
    
    // 清理本地表單資料
    Object.keys(localFormData).forEach(key => {
      if (key !== 'valid') {
        delete localFormData[key];
      }
    });
    
    // 載入新案件資料
    const caseNumberStr = newCaseNumber as string;
    if (grantsStore.caseNumber !== caseNumberStr) {
      await grantsStore.loadGrant(caseNumberStr);
    }
    
    // 載入必要的步驟資料
    await Promise.all([
      grantsStore.loadStepData(caseNumberStr, 1),
      grantsStore.loadStepData(caseNumberStr, 2),
      grantsStore.loadStepData(caseNumberStr, 3),
      grantsStore.loadStepData(caseNumberStr, 4),
      grantsStore.loadStepData(caseNumberStr, 6)
    ]);
    
    console.log('✅ Step6: 案件切換完成，已清理舊資料並載入新案件資料');
  }
}, { immediate: false });

// 初始化數據 - 總是載入資料庫資料，確保資料最新
onMounted(async () => {
  console.log("Step 6 mounted, formData:", props.formData);

  const caseNumberFromRoute = route.query.id as string;

  if (caseNumberFromRoute) {
    console.log('🔄 Step6: 載入案件資料...', caseNumberFromRoute);
    try {
      // 總是載入案件基本資料
      if (grantsStore.caseNumber !== caseNumberFromRoute) {
        await grantsStore.loadGrant(caseNumberFromRoute);
      }

      // 總是載入必要的步驟資料，不進行條件判斷
      await Promise.all([
        grantsStore.loadStepData(caseNumberFromRoute, 1),
        grantsStore.loadStepData(caseNumberFromRoute, 2),
        grantsStore.loadStepData(caseNumberFromRoute, 3),
        grantsStore.loadStepData(caseNumberFromRoute, 4),
        grantsStore.loadStepData(caseNumberFromRoute, 6)  // 載入 step6 本身的資料
      ]);

      console.log('✅ Step6: 案件資料載入完成');

      // 詳細檢查載入的資料
      console.log('🔍 Step6: 檢查載入的資料狀態:', {
        formData: {
          step1Keys: Object.keys(grantsStore.formData[1] || {}),
          step2Keys: Object.keys(grantsStore.formData[2] || {}),
          step3Keys: Object.keys(grantsStore.formData[3] || {}),
          step4Keys: Object.keys(grantsStore.formData[4] || {}),
          step6Keys: Object.keys(grantsStore.formData[6] || {}),
        },
        currentGrant_allStepsData: {
          step2Keys: Object.keys((grantsStore.currentGrant?.active_version as any)?.all_steps_data?.steps?.['2'] || {}),
          step3Keys: Object.keys((grantsStore.currentGrant?.active_version as any)?.all_steps_data?.steps?.['3'] || {}),
          step4Keys: Object.keys((grantsStore.currentGrant?.active_version as any)?.all_steps_data?.steps?.['4'] || {}),
          step4HasPipes: !!((grantsStore.currentGrant?.active_version as any)?.all_steps_data?.steps?.['4']?.pipes),
          step4HasMainPipe: !!((grantsStore.currentGrant?.active_version as any)?.all_steps_data?.steps?.['4']?.mainPipeQuantity),
        }
      });

      // 觸發 computed 屬性重新計算
      await nextTick();

      console.log('✅ Step6: computed properties 已觸發重新計算', {
        pipeLineTotal: pipeLineTotal.value,
        facilitySubsidy: facilitySubsidy.value,
        totalBudget: totalBudget.value
      });
    } catch (error) {
      console.error('❌ Step6: 載入案件資料失敗', error);
    }
  }

  // 從父組件接收的基本資料並初始化 farmerContribution
  if (props.formData) {
    Object.keys(localFormData).forEach(key => {
      if (props.formData[key] !== undefined) {
        localFormData[key] = props.formData[key];
      }
    });

    // 初始化或更新 farmerContribution 到 grantsStore
    if (props.formData.farmerContribution !== undefined) {
      if (!grantsStore.formData[6]) {
        grantsStore.formData[6] = {};
      }
      grantsStore.formData[6].farmerContribution = props.formData.farmerContribution;
    }
  }

  console.log('✅ Step6: 使用 computed properties 從 grantsStore 直接讀取資料，不維護本地副本');

  // 初始更新父組件
  updateFormData();
});

// Watch for changes in grantsStore.currentGrant to ensure reactivity
watch(() => grantsStore.currentGrant?.active_version, (newVersion, oldVersion) => {
  if (newVersion && newVersion !== oldVersion) {
    console.log('🔄 Step6: grantsStore.currentGrant.active_version changed, triggering computed properties recalculation');
    // 使用 nextTick 確保響應性更新
    nextTick(() => {
      console.log('✅ Step6: Computed properties values after currentGrant change:', {
        pipeLineTotal: pipeLineTotal.value,
        facilitySubsidy: facilitySubsidy.value,
        totalBudget: totalBudget.value,
        mainPipesCount: mainPipes.value.length,
        irrigationSystemCount: irrigationSystem.value.length
      });
    });
  }
}, { deep: true });

// Watch for props changes
watch(() => props.formData, (newData) => {
  if (newData) {
    // Update basic properties
    Object.keys(localFormData).forEach(key => {
      if (newData[key] !== undefined &&
          JSON.stringify(newData[key]) !== JSON.stringify(localFormData[key])) {
        localFormData[key] = newData[key];
      }
    });

    // 不再同步設施陣列，改用 computed 直接讀取 grantsStore
  }
}, { deep: true });

// Watch for validation status changes
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
}

.preview-table {
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
}

/* 確保國字大寫金額在一行顯示 */
.amount-in-words {
  white-space: nowrap !important;
  overflow: visible; /* 允許內容溢出而不是隱藏 */
  min-width: 250px; /* 增加最小寬度 */
  width: auto; /* 允許自動調整寬度 */
  max-width: none; /* 移除最大寬度限制 */
}

.nowrap-text {
  white-space: nowrap !important;
  display: inline-block;
  font-size: 0.875rem; /* 稍微縮小字體以適應更長的文字 */
  font-weight: 500;
  letter-spacing: -0.01em; /* 稍微縮小字間距 */
}

/* 表格容器允許水平滾動 */
.facility-table-container {
  overflow-x: auto;
  width: 100%;
}

/* 確保表格最小寬度足夠容納所有內容 */
.facility-table {
  min-width: 800px; /* 設定表格最小寬度 */
}

/* 在小螢幕上調整字體大小但保持不換行 */
@media (max-width: 768px) {
  .facility-table {
    font-size: 0.8rem;
    min-width: 800px; /* 在小螢幕上稍微縮小但仍保持足夠寬度 */
  }

  .nowrap-text {
    font-size: 0.75rem;
    letter-spacing: -0.02em; /* 進一步縮小字間距 */
  }

  .amount-in-words {
    min-width: 200px;
  }
}

/* 確保表格在小螢幕上可以水平滾動 */
.v-table {
  overflow-x: auto;
}
</style>
