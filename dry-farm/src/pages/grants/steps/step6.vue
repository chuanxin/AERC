<template>
  <div
    ref="stepContent"
    class="step-content"
  >
    <v-card
      class="mt-4 mb-0 pa-0"
      flat
    >
      <v-card-text class="pb-0 pt-0">
        <!-- 本案設施區 -->
        <v-card-title
          class="text-subtitle-1 font-weight-bold pa-0 pb-2 d-flex align-center"
          style="color: #2d8c8f"
        >
          <v-icon
            color="#3ea0a3"
            class="me-2 mb-0 pb-0"
            size="small"
          >
            mdi-pipe
          </v-icon>
          本案設施表
        </v-card-title>

        <v-sheet
          class="mt-2 pb-4 rounded"
          color="white"
        >
          <v-table
            density="compact"
            fixed-header
            class="border-thin"
          >
            <thead>
              <tr class="bg-grey-lighten-3">
                <th class="text-start ">
                  設施項目
                </th>
                <th class="text-start">
                  說明
                </th>
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
                <th class="text-start">
                  備註
                </th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td class="font-weight-medium">
                  田間管路設施費（A）
                </td>
                <td />
                <td class="text-center">
                  <template v-if="parseInt(pipeLineTotal.replace(/,/g, '')) > 0" />
                </td>
                <td class="text-center" />
                <td class="text-center" />
                <td class="text-center font-weight-medium">
                  {{ pipeLineTotal }}
                </td>
                <td>詳如數量表</td>
              </tr>
              <tr
                v-for="(item, index) in mainPipes"
                :key="`main-${index}`"
              >
                <td class="pl-6">
                  田間主管(L{{ index + 1 }})
                </td>
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
                <td class="pl-6">
                  {{ item.name }}
                </td>
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
                <td />
              </tr>
              <!-- 田間管路工作費（當 workFee > 0 時顯示） -->
              <tr v-if="workFee > 0">
                <td class="pl-6">
                  田間管路工作費
                </td>
                <td />
                <td class="text-center" />
                <td class="text-center" />
                <td class="text-center" />
                <td class="text-center">
                  {{ workFee.toLocaleString() }}
                </td>
                <td />
              </tr>
              <tr>
                <td class="font-weight-medium">
                  灌溉調控設施費
                </td>
                <td>
                  <template v-if="controlFacilities.length > 0">
                    依計畫補助標準
                  </template>
                </td>
                <td class="text-center">
                  <template v-if="controlFacilities.length > 0" />
                </td>
                <td class="text-center" />
                <td class="text-center" />
                <td class="text-center font-weight-medium">
                  {{ controlFacilities.reduce((sum, f) => sum + (parseInt(f.totalPrice?.toString().replace(/,/g, '') || '0')), 0).toLocaleString() }}
                </td>
                <td />
              </tr>
              <tr
                v-for="(item, index) in controlFacilities"
                :key="`control-${index}`"
              >
                <td class="pl-6">
                  {{ item.name }}（{{ item.specification }}）
                </td>
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
                  規劃設計費（B）
                </td>
                <td>
                  <template v-if="designFee > 0">
                    A*2.0%
                  </template>
                </td>
                <td class="text-center" />
                <td class="text-center" />
                <td class="text-center" />
                <td class="text-center font-weight-medium">
                  {{ designFee }}
                </td>
                <td />
              </tr>
              <tr class="bg-grey-lighten-4">
                <td
                  colspan="5"
                  class="text-end font-weight-bold"
                >
                  合計
                </td>
                <td class="text-center font-weight-bold">
                  {{ totalBudget }}
                </td>
                <td class="text-no-wrap">
                  新臺幣 {{ amountInWords }}元整 {{ isAboriginalAreaText }}
                </td>
              </tr>
            </tbody>
          </v-table>
        </v-sheet>

        <!-- 農戶補助明細區 -->
        <v-card-title
          class="text-subtitle-1 font-weight-bold pa-0 pb-2 d-flex align-center"
          style="color: #2d8c8f"
        >
          <v-icon
            color="#3ea0a3"
            class="me-2"
            size="small"
          >
            mdi-calculator
          </v-icon>
          農戶補助明細
        </v-card-title>

        <v-sheet
          class="mt-2 pb-4 rounded"
          color="white"
        >
          <v-table
            density="compact"
            class="border-thin"
          >
            <colgroup>
              <col style="width: 20%;">
              <col style="width: 20%;">
              <col style="width: 60%;">
            </colgroup>
            <tbody>
              <!-- 農戶配合款 -->
              <tr>
                <td
                  colspan="2"
                  class="font-weight-medium text-center"
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
                  rowspan="3"
                  class="font-weight-medium text-center align-center"
                >
                  政府<br>補助款
                </td>
                <td
                  rowspan="2"
                  class="font-weight-medium text-center align-center"
                >
                  農戶<br>請領款
                </td>
                <td class="text-center">
                  田間管路設施補助費：{{ pipeLineSubsidy }}
                </td>
              </tr>
              <tr>
                <td class="text-center">
                  灌溉調控設施補助費：{{ facilitySubsidy }}
                </td>
              </tr>
              <tr>
                <td class="font-weight-medium text-center">
                  規劃設計費
                </td>
                <td class="text-center">
                  {{ actualSubsidizedDesignFee }}
                </td>
              </tr>

              <!-- 總計 -->
              <tr class="bg-amber-lighten-4">
                <td
                  colspan="2"
                  class="font-weight-medium text-center"
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

        <!-- 報表列印區 -->
        <v-card-title
          class="text-subtitle-1 font-weight-bold pa-0 pb-3 d-flex align-center"
          style="color: #2d8c8f"
        >
          <v-icon
            color="#3ea0a3"
            class="me-2"
            size="small"
          >
            mdi-printer
          </v-icon>
          報表列印
        </v-card-title>

        <!-- 文件列印卡片 -->
        <div class="d-flex flex-column ga-2 pb-4">
          <v-card
            v-for="doc in printDocuments"
            :key="doc.type"
            rounded="lg"
            variant="text"
            :ripple="false"
            @click.stop="printDocument(doc.type)"
          >
            <div class="d-flex align-center pa-3">
              <!-- 左側：圖標和檔名 -->
              <div
                class="d-flex align-center"
                style="min-width: 150px;"
              >
                <v-icon
                  :color="doc.color"
                  size="24"
                  class="me-3"
                >
                  {{ doc.icon }}
                </v-icon>
                <div>
                  <div class="text-body-2 font-weight-medium">
                    {{ doc.title }}
                  </div>
                  <div class="text-caption text-grey">
                    {{ doc.subtitle }}
                  </div>
                </div>
              </div>

              <!-- 右側：下載區域（佔據剩餘空間） -->
              <div class="flex-grow-1 d-flex align-center">
                <!-- 下載中：進度條置中 -->
                <template v-if="doc.downloadStatus === 'downloading'">
                  <div class="flex-grow-1 d-flex align-center justify-center gap-2">
                    <v-progress-linear
                      :model-value="doc.progress"
                      :color="doc.color"
                      height="6"
                      rounded
                      style="max-width: 400px;"
                      stream
                    />
                    <span class="text-caption text-grey ml-4" style="min-width: 40px;">
                      {{ Math.round(doc.progress) }}%
                    </span>
                  </div>
                </template>

                <!-- 下載完成：訊息置中，按鈕靠右 -->
                <template v-else-if="doc.downloadStatus === 'success' || doc.downloadStatus === 'error'">
                  <div class="flex-grow-1 d-flex align-center justify-end with-gap-2 me-4">
                    <span
                      class="text-caption font-weight-medium"
                      :class="doc.downloadStatus === 'success' ? 'text-success' : 'text-error'"
                    >
                      <span v-if="doc.downloadStatus === 'success'">✓ 下載成功</span>
                      <span v-else-if="doc.downloadStatus === 'error'">✗ 下載失敗</span>
                    </span>
                  </div>
                  <v-btn
                    size="small"
                    variant="outlined"
                    color="primary"
                    prepend-icon="mdi-refresh"
                    @click.stop="printDocument(doc.type)"
                  >
                    重新下載
                  </v-btn>
                </template>

                <!-- 初始狀態：按鈕靠右 -->
                <template v-else>
                  <div class="flex-grow-1" />
                  <v-btn
                    size="small"
                    variant="outlined"
                    prepend-icon="mdi-download"
                    @click.stop="printDocument(doc.type)"
                  >
                    下載
                  </v-btn>
                </template>
              </div>
            </div>
          </v-card>
        </div>
      </v-card-text>
    </v-card>
  </div>
</template>

<script setup lang="ts">
/* eslint-disable @typescript-eslint/no-explicit-any */
import { useGrantsStore } from '@/stores/grants';
import { useRoute } from 'vue-router';
import type { PropType } from 'vue';
import downloadsService from '@/services/downloadsService';
import { generateCompletionStatement, generateDeclaration, generateAuthorization, generateBudgetStatement, downloadPdfBlob } from '@/services/grantsService';
import { formatCaseNumber } from '@/utils/frontendFilters';

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

// 文件列印資料定義
const printDocuments = reactive([
  {
    type: 'application',
    title: '灌溉系統設計標準',
    subtitle: '系統設計規格書',
    icon: 'mdi-file-excel',
    color: '#217346',
    downloading: false,
    progress: 0,
    downloadStatus: 'idle' // 'idle' | 'downloading' | 'success' | 'error'
  },
  {
    type: 'statement',
    title: '結案申報書',
    subtitle: '工程完工申報',
    icon: 'mdi-file-pdf-box',
    color: '#D32F2F',
    downloading: false,
    progress: 0,
    downloadStatus: 'idle'
  },
  {
    type: 'declaration',
    title: '補助切結書',
    subtitle: '補助申請切結文件',
    icon: 'mdi-file-pdf-box',
    color: '#D32F2F',
    downloading: false,
    progress: 0,
    downloadStatus: 'idle'
  },
  {
    type: 'authorization',
    title: '規劃委託書',
    subtitle: '規劃設計委託文件',
    icon: 'mdi-file-pdf-box',
    color: '#D32F2F',
    downloading: false,
    progress: 0,
    downloadStatus: 'idle'
  },
  {
    type: 'budget',
    title: '工程預算書',
    subtitle: '工程成本明細表',
    icon: 'mdi-file-pdf-box',
    color: '#D32F2F',
    downloading: false,
    progress: 0,
    downloadStatus: 'idle'
  }
]);

// Computed property for farmer contribution - step3 和 step4 的自備款總和
const displayFarmerContribution = computed(() => {
  const step3Data = getStepDataSafely(4);  // step3.vue → formData[4]
  const step4Data = getStepDataSafely(5);  // step4.vue → formData[5]

  // step3 自備款
  const step3SelfPaid = step3Data?.facilities?.reduce((sum: number, facility: any) => {
    return sum + (facility.selfPaidAmount || 0);
  }, 0) || 0;

  // step4 自備款
  const step4SelfPaid = step4Data?.selfPaidAmount || 0;

  const total = step3SelfPaid + step4SelfPaid;
  return total.toLocaleString();
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
  const step4Data = getStepDataSafely(5);  // step4.vue → formData[5]
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
  const step4Data = getStepDataSafely(5);  // step4.vue → formData[5]
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
  const step3Data = getStepDataSafely(4);  // step3.vue → formData[4]
  if (!step3Data?.facilities || !Array.isArray(step3Data.facilities)) return [];

  const facilities = step3Data.facilities as any[];

  // 映射 name 到 specification 並排序
  const specificationOrder = { 'C': 1, 'D': 2, 'E': 3 };

  return facilities.map((f: any) => {
    const name = f.typeLabel || f.name;
    let specification = '';

    // 根據 name 設定 specification
    if (name === '動力設備') {
      specification = 'D';
    } else if (name === '調蓄設施') {
      specification = 'E';
    } else if (name === '調節控制設施') {
      specification = 'C';
    }

    return {
      name,
      facilityName: f.name, // 真正的設施名稱
      specification,
      quantity: f.quantity,
      unitPrice: typeof f.unitPrice === 'number' ? f.unitPrice.toLocaleString() : f.unitPrice,
      totalPrice: typeof f.totalPrice === 'number' ? f.totalPrice.toLocaleString() : f.totalPrice,
      unit: f.type === 'power' ? '臺' : (f.type === 'storage' ? '座' : '組'),
      remark: f.remark || f.name
    };
  }).sort((a, b) => {
    // 依照 C-D-E 順序排序
    const orderA = specificationOrder[a.specification as keyof typeof specificationOrder] || 999;
    const orderB = specificationOrder[b.specification as keyof typeof specificationOrder] || 999;
    return orderA - orderB;
  });
});

// Computed properties for calculated values
const pipeLineTotal = computed(() => {
  const step4Data = getStepDataSafely(5);  // step4.vue → formData[5]
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

  // Work fee calculation
  const workFeeValue = step4Data.workFee || 0;
  const workFeeAmount = typeof workFeeValue === 'number' ? workFeeValue : parseInt(workFeeValue) || 0;

  return (pipelineTotal + irrigationTotal + workFeeAmount).toLocaleString();
});

// A項補助費：step4 的補助款總額（扣除設計費）
const pipeLineSubsidy = computed(() => {
  const step4Data = getStepDataSafely(5);  // step4.vue → formData[5]
  if (!step4Data) return '0';

  const subsidyAmount = step4Data.subsidyAmount || 0;
  const designFeeAmount = step4Data.designFee || 0;

  // A項補助費 = 總補助 - 設計費
  const pipelineSubsidyOnly = Math.max(0, subsidyAmount - designFeeAmount);
  return pipelineSubsidyOnly.toLocaleString();
});

// B項補助費：step3 的補助款總額
const facilitySubsidy = computed(() => {
  const step3Data = getStepDataSafely(4);  // step3.vue → formData[4]
  if (!step3Data || Object.keys(step3Data).length === 0 || !step3Data?.facilities || !Array.isArray(step3Data.facilities)) return '0';

  const total = step3Data.facilities.reduce((sum: number, facility: any) => {
    return sum + (facility.subsidyAmount || 0);
  }, 0);

  return total.toLocaleString();
});

// 規劃設計費：直接從 step4 讀取（用於本案設施表顯示真實設計費）
const designFee = computed(() => {
  const step4Data = getStepDataSafely(5);  // step4.vue → formData[5]
  if (!step4Data) return '0';

  const designFeeAmount = step4Data.designFee || 0;
  return designFeeAmount.toLocaleString();
});

// 實際獲得補助的規劃設計費（用於農戶補助明細）
const actualSubsidizedDesignFee = computed(() => {
  const step4Data = getStepDataSafely(5);  // step4.vue → formData[5]
  if (!step4Data) return '0';

  const designFeeAmount = step4Data.designFee || 0;
  const subsidyAmount = step4Data.subsidyAmount || 0;

  // 當補助額度小於設計費時，顯示實際獲得的補助額度
  const actualSubsidy = Math.min(subsidyAmount, designFeeAmount);

  return actualSubsidy.toLocaleString();
});

const totalBudget = computed(() => {
  const farmerContribution = parseInt(displayFarmerContribution.value.replace(/,/g, '')) || 0;
  const pipelineSubsidyValue = parseInt(pipeLineSubsidy.value.replace(/,/g, '')) || 0;
  const facilitySubsidyValue = parseInt(facilitySubsidy.value.replace(/,/g, '')) || 0;
  const actualDesignFeeValue = parseInt(actualSubsidizedDesignFee.value.replace(/,/g, '')) || 0;
  return (farmerContribution + pipelineSubsidyValue + facilitySubsidyValue + actualDesignFeeValue).toLocaleString();
});

// 將金額轉換為中文大寫
const amountInWords = computed(() => {
  const amount = parseInt(totalBudget.value.replace(/,/g, ''));
  if (isNaN(amount)) return '零';

  const digits = ['零', '壹', '貳', '參', '肆', '伍', '陸', '柒', '捌', '玖'];
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

// 田間管路工作費（從 step5 取得）
const workFee = computed(() => {
  const step4Data = getStepDataSafely(5);  // step4.vue → formData[5]
  if (!step4Data) return 0;

  const fee = step4Data.workFee || 0;
  return typeof fee === 'number' ? fee : parseInt(fee) || 0;
});

// 文件列印
const printDocument = async (documentType: string) => {
  console.log(`下載檔案: ${documentType}`);

  // 找到對應的文件
  const doc = printDocuments.find(d => d.type === documentType);
  if (!doc) return;

  // 設置下載中狀態
  doc.downloading = true;
  doc.downloadStatus = 'downloading';
  doc.progress = 0;

  try {
    // 🔥 灌溉系統設計標準 - 下載靜態 Excel 檔案
    if (documentType === 'application') {
      const targetBaseName = 'DesignStandard-田間管路灌溉型式';

      // 階段 1: 查詢檔案列表取得正確的 file_id
      doc.progress = 20;
      console.log('正在查詢檔案...');
      await new Promise(resolve => setTimeout(resolve, 300));

      const filesList = await downloadsService.getStaticFilesList({
        search_keyword: targetBaseName
      });

      // 找到目標檔案
      const targetFileGroup = filesList.file_groups.find(
        group => group.base_name === targetBaseName
      );

      if (!targetFileGroup || targetFileGroup.formats.length === 0) {
        throw new Error(`找不到檔案: ${targetBaseName}`);
      }

      // 取得 xlsx 格式的檔案（優先）或第一個檔案
      const targetFile = targetFileGroup.formats.find(f => f.format === 'xlsx')
                        || targetFileGroup.formats[0];

      const fileId = targetFile.id;
      const filename = targetFile.filename;

      // 階段 2-3: 準備下載
      doc.progress = 40;
      console.log('建立下載連線...');
      await new Promise(resolve => setTimeout(resolve, 300));

      doc.progress = 60;
      console.log(`正在下載 ${filename}...`);
      await new Promise(resolve => setTimeout(resolve, 200));

      // 階段 4: 實際下載檔案
      await downloadsService.downloadStaticFile(fileId, filename);

      // 階段 5: 下載完成
      doc.progress = 90;
      console.log('檔案已生成，正在啟動下載...');
      await new Promise(resolve => setTimeout(resolve, 500));

      doc.progress = 100;
      doc.downloadStatus = 'success';
      doc.downloading = false;
      console.log('檔案已送出，請查看瀏覽器的下載紀錄');
    }
    // 🔥 結案申報書 - 生成 PDF
    else if (documentType === 'statement') {
      const caseNumber = grantsStore.caseNumber;
      if (!caseNumber) {
        console.error('案號不存在');
        doc.downloading = false;
        doc.downloadStatus = 'error';
        // 失敗時保持當前進度，不到達 100%
        return;
      }

      // 階段式進度更新
      const progressStages = [
        { progress: 20, message: '正在準備資料...', delay: 200 },
        { progress: 40, message: '正在生成 PDF...', delay: 300 },
        { progress: 60, message: '正在處理文件...', delay: 200 },
      ];

      for (const stage of progressStages) {
        doc.progress = stage.progress;
        console.log(stage.message);
        await new Promise(resolve => setTimeout(resolve, stage.delay));
      }

      // 實際生成結案申報書
      const pdfBlob = await generateCompletionStatement(caseNumber);

      // 下載完成
      doc.progress = 90;
      console.log('結案申報書已生成，正在啟動下載...');
      await new Promise(resolve => setTimeout(resolve, 300));

      // 使用 grantsService 的下載函數
      const year = grantsStore.currentGrant?.year || new Date().getFullYear() - 1911;
      const applicantName = grantsStore.currentGrant?.applicant_name || '未知';
      const displayCaseNumber = formatCaseNumber(caseNumber);
      const filename = `${year}-${displayCaseNumber}-${applicantName} - 結案申報書.pdf`;
      downloadPdfBlob(pdfBlob, filename);

      doc.progress = 100;
      doc.downloadStatus = 'success';
      doc.downloading = false;
      console.log('結案申報書下載完成');
    }
    // 🔥 補助切結書 - 生成 PDF
    else if (documentType === 'declaration') {
      const caseNumber = grantsStore.caseNumber;
      if (!caseNumber) {
        console.error('案號不存在');
        doc.downloading = false;
        doc.downloadStatus = 'error';
        // 失敗時保持當前進度，不到達 100%
        return;
      }

      // 階段式進度更新
      const progressStages = [
        { progress: 20, message: '正在準備資料...', delay: 200 },
        { progress: 40, message: '正在生成切結書...', delay: 300 },
        { progress: 60, message: '正在處理文件...', delay: 200 },
      ];

      for (const stage of progressStages) {
        doc.progress = stage.progress;
        console.log(stage.message);
        await new Promise(resolve => setTimeout(resolve, stage.delay));
      }

      // 實際生成切結書
      const pdfBlob = await generateDeclaration(caseNumber);

      // 下載完成
      doc.progress = 90;
      console.log('切結書已生成，正在啟動下載...');
      await new Promise(resolve => setTimeout(resolve, 300));

      // 使用 grantsService 的下載函數
      const year = grantsStore.currentGrant?.year || new Date().getFullYear() - 1911;
      const applicantName = grantsStore.currentGrant?.applicant_name || '未知';
      const displayCaseNumber = formatCaseNumber(caseNumber);
      const filename = `${year}-${displayCaseNumber}-${applicantName} - 切結書.pdf`;
      downloadPdfBlob(pdfBlob, filename);

      doc.progress = 100;
      doc.downloadStatus = 'success';
      doc.downloading = false;
      console.log('切結書下載完成');
    }
    // 🔥 規劃委託書 - 生成 PDF
    else if (documentType === 'authorization') {
      const caseNumber = grantsStore.caseNumber;
      if (!caseNumber) {
        console.error('案號不存在');
        doc.downloading = false;
        doc.downloadStatus = 'error';
        // 失敗時保持當前進度，不到達 100%
        return;
      }

      // 階段式進度更新
      const progressStages = [
        { progress: 20, message: '正在準備資料...', delay: 200 },
        { progress: 40, message: '正在生成規劃委託書...', delay: 300 },
        { progress: 60, message: '正在處理文件...', delay: 200 },
      ];

      for (const stage of progressStages) {
        doc.progress = stage.progress;
        console.log(stage.message);
        await new Promise(resolve => setTimeout(resolve, stage.delay));
      }

      // 實際生成規劃委託書
      const pdfBlob = await generateAuthorization(caseNumber);

      // 下載完成
      doc.progress = 90;
      console.log('規劃委託書已生成，正在啟動下載...');
      await new Promise(resolve => setTimeout(resolve, 300));

      // 使用 grantsService 的下載函數
      const year = grantsStore.currentGrant?.year || new Date().getFullYear() - 1911;
      const applicantName = grantsStore.currentGrant?.applicant_name || '未知';
      const displayCaseNumber = formatCaseNumber(caseNumber);
      const filename = `${year}-${displayCaseNumber}-${applicantName} - 規劃委託書.pdf`;
      downloadPdfBlob(pdfBlob, filename);

      doc.progress = 100;
      doc.downloadStatus = 'success';
      doc.downloading = false;
      console.log('規劃委託書下載完成');
    }
    // 🔥 工程預算書 - 生成 PDF
    else if (documentType === 'budget') {
      const caseNumber = grantsStore.caseNumber;
      if (!caseNumber) {
        console.error('案號不存在');
        doc.downloading = false;
        doc.downloadStatus = 'error';
        // 失敗時保持當前進度，不到達 100%
        return;
      }

      // 階段式進度更新
      const progressStages = [
        { progress: 20, message: '正在準備資料...', delay: 200 },
        { progress: 40, message: '正在生成工程預算書...', delay: 300 },
        { progress: 60, message: '正在處理文件...', delay: 200 },
      ];

      for (const stage of progressStages) {
        doc.progress = stage.progress;
        console.log(stage.message);
        await new Promise(resolve => setTimeout(resolve, stage.delay));
      }

      // 實際生成工程預算書
      const pdfBlob = await generateBudgetStatement(caseNumber);

      // 下載完成
      doc.progress = 90;
      console.log('工程預算書已生成，正在啟動下載...');
      await new Promise(resolve => setTimeout(resolve, 300));

      // 使用 grantsService 的下載函數
      const year = grantsStore.currentGrant?.year || new Date().getFullYear() - 1911;
      const applicantName = grantsStore.currentGrant?.applicant_name || '未知';
      const displayCaseNumber = formatCaseNumber(caseNumber);
      const filename = `${year}-${displayCaseNumber}-${applicantName} - 工程預算書.pdf`;
      downloadPdfBlob(pdfBlob, filename);

      doc.progress = 100;
      doc.downloadStatus = 'success';
      doc.downloading = false;
      console.log('工程預算書下載完成');
    }
    // TODO: 其他文件類型的下載邏輯（PDF 報表生成）
    else {
      // TODO: 實際的文件下載邏輯
      // 例如: await apiService.downloadDocument(documentType);
    }
  } catch (error) {
    console.error(`下載 ${documentType} 失敗:`, error);
    doc.downloading = false;
    doc.downloadStatus = 'error';
    // 失敗時保持當前進度，不強制設為 100%
    // 可選：顯示錯誤訊息給用戶
  }
};

// Computed properties for display data - 直接從 grantsStore 讀取，不維護本地副本
// NOTE: 以下 computed 屬性目前未使用，但保留以備將來使用
/*
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
  const step4Data = getStepDataSafely(5);  // step4.vue → formData[5]
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
*/

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
    // 🔥 統一架構 (2025-11-04): step3.vue → formData[4], step4.vue → formData[5]
    await Promise.all([
      grantsStore.loadStepData(caseNumberStr, 1),
      grantsStore.loadStepData(caseNumberStr, 2),
      grantsStore.loadStepData(caseNumberStr, 4),  // step3.vue
      grantsStore.loadStepData(caseNumberStr, 5),  // step4.vue
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
      // 🔥 統一架構 (2025-11-04): step3.vue → formData[4], step4.vue → formData[5]
      await Promise.all([
        grantsStore.loadStepData(caseNumberFromRoute, 1),
        grantsStore.loadStepData(caseNumberFromRoute, 2),
        grantsStore.loadStepData(caseNumberFromRoute, 4),  // step3.vue
        grantsStore.loadStepData(caseNumberFromRoute, 5),  // step4.vue
        grantsStore.loadStepData(caseNumberFromRoute, 6)   // step6.vue 本身的資料
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

/* 表格邊框 - 使用 Vuetify 樣式添加垂直和水平邊框 */
:deep() .v-table .v-table__wrapper > table > thead > tr > th:not(:last-child) {
  border-right: thin solid rgba(var(--v-border-color), var(--v-border-opacity));
}
:deep() .v-table .v-table__wrapper > table > tbody > tr > td:not(:last-child), .v-table .v-table__wrapper > table > tbody > tr > th:not(:last-child) {
  border-right: thin solid rgba(var(--v-border-color), var(--v-border-opacity));
}
</style>
