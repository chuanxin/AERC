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
                    {{ localFormData.pipeLineTotal }}
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
                    {{ localFormData.designFee }}
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
                    {{ localFormData.totalBudget }}
                  </td>
                  <td>新臺幣 {{ amountInWords }}元整 {{ isAboriginalAreaText }}</td>
                </tr>
              </tbody>
            </v-table>
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
                        {{ localFormData.applicationYear }}
                      </td>
                      <td
                        class="font-weight-medium text-center"
                        style="width: 15%"
                      >
                        案號
                      </td>
                      <td style="width: 35%">
                        {{ localFormData.caseNumber }}
                      </td>
                    </tr>
                    <tr>
                      <td class="font-weight-medium text-center">
                        農戶姓名
                      </td>
                      <td>
                        {{ localFormData.applicantName }}
                      </td>
                      <td class="font-weight-medium text-center">
                        農戶住址
                      </td>
                      <td>
                        {{ localFormData.applicantAddress }}
                      </td>
                    </tr>
                    <tr>
                      <td class="font-weight-medium text-center">
                        設施地段
                      </td>
                      <td>
                        {{ localFormData.facilityLocation }}
                      </td>
                      <td class="font-weight-medium text-center">
                        設施地號
                      </td>
                      <td>
                        {{ localFormData.facilityNumber }}
                      </td>
                    </tr>
                    <tr>
                      <td class="font-weight-medium text-center">
                        設施面積
                      </td>
                      <td>
                        {{ localFormData.facilityArea }}公頃
                      </td>
                      <td class="font-weight-medium text-center">
                        設施型式
                      </td>
                      <td>
                        {{ localFormData.facilityType }}
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
                        {{ localFormData.farmerContribution || '0' }}
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
                        A項補助費：{{ localFormData.pipeLineSubsidy }}
                      </td>
                    </tr>
                    <tr>
                      <td class="text-center">
                        B項補助費：{{ localFormData.facilitySubsidy }}
                      </td>
                    </tr>
                    <tr>
                      <td class="font-weight-medium text-center">
                        規劃設計費
                      </td>
                      <td class="text-center">
                        {{ localFormData.designFee }}
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
                        {{ localFormData.totalBudget }}
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
import type { PropType } from 'vue';

// Define types for better TypeScript support
interface MainPipe {
  name: string;
  quantity: string | number;
  unitPrice: string | number;
  totalPrice: string;
  unit: string;
  remark: string;
}

interface IrrigationSystemItem {
  name: string;
  quantity: string | number;
  unitPrice: string | number;
  totalPrice: string;
  unit: string;
  remark: any;
}

interface ControlFacility {
  name: string;
  specification: string;
  quantity: string | number;
  unitPrice: string | number;
  totalPrice: string;
  unit: string;
  remark: string;
}

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

// Use the grants store
const grantsStore = useGrantsStore();

// Form ref and validation state
const form = ref<any>(null);
const localValid = ref(true);

// 本地表單數據
const localFormData = reactive<Record<string, any>>({
  applicationYear: '',  // 申請年度
  caseNumber: '',       // 案號
  applicantName: '',    // 農戶姓名
  applicantAddress: '', // 農戶地址
  facilityLocation: '', // 設施地段
  facilityNumber: '',   // 設施地號
  facilityArea: '',     // 設施面積
  facilityType: '',     // 設施型式

  pipeLineTotal: '',    // 管路總價
  pipeLineSubsidy: '',
  facilitySubsidy: '',
  designFee: '',
  totalBudget: '',
  farmerContribution: '', // 農戶配合款

  isAboriginalArea: false,

  // Always valid for seamless navigation
  valid: true
});

// 設施資料
// 主管
const mainPipes = ref<MainPipe[]>([
  { name: '田間主管1', remark: '-', quantity: '-', unitPrice: '-', totalPrice: '-', unit: '-' },
  { name: '田間主管2', remark: '-', quantity: '-', unitPrice: '-', totalPrice: '-', unit: '-' }
]);

// 灌溉系統
const irrigationSystem = ref<IrrigationSystemItem[]>([
  { name: '灌溉系統', quantity: '-', unitPrice: '-', totalPrice: '-', unit: '-', remark: {
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

// 灌溉調控設施
const controlFacilities = ref<ControlFacility[]>([
  { name: '動力設施', specification: '', quantity: '', unitPrice: '', totalPrice: '', unit: '台', remark: '' },
  { name: '調蓄設施', specification: '', quantity: '', unitPrice: '', totalPrice: '', unit: '座', remark: '' },
  { name: '調節控制設施', specification: '', quantity: '', unitPrice: '', totalPrice: '', unit: '台', remark: '' }
]);

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

// 文件列印
const printDocument = (documentType: string) => {
  console.log(`列印檔案: ${documentType}`);
  // Mock print logic for demo
};

// 更新父組件數據
const updateFormData = () => {
  emit('update:formData', {
    ...props.formData,
    ...localFormData,
    mainPipes: mainPipes.value,
    irrigationSystem: irrigationSystem.value,
    controlFacilities: controlFacilities.value,
    valid: true // Always true for seamless navigation
  });
};

// 初始化數據
onMounted(() => {
  console.log("Step 6 mounted, formData:", props.formData);

  // 從父組件接收數據
  if (props.formData) {
    // Set basic properties
    Object.keys(localFormData).forEach(key => {
      if (props.formData[key] !== undefined) {
        localFormData[key] = props.formData[key];
      }
    });

    // Load facility data if available
    if (props.formData.mainPipes) {
      mainPipes.value = [...props.formData.mainPipes];
    }

    if (props.formData.irrigationSystem) {
      irrigationSystem.value = [...props.formData.irrigationSystem];
    }

    if (props.formData.controlFacilities) {
      controlFacilities.value = [...props.formData.controlFacilities];
    }
  }

  // Set case number and applicant name from Grant store if available
  if (grantsStore.caseNumber && !localFormData.caseNumber) {
    localFormData.caseNumber = grantsStore.caseNumber;
  }

  // Try to get applicant name from step 1
  if (grantsStore.formData[1]?.name && !localFormData.applicantName) {
    localFormData.applicantName = grantsStore.formData[1].name;
  }

  // Try to set address from step 1
  if (!localFormData.applicantAddress) {
    const step1Data = grantsStore.formData[1];
    if (step1Data) {
      const county = step1Data.county || '';
      const town = step1Data.town || '';
      const village = step1Data.village || '';
      const address = step1Data.address || '';

      if (county || town || village || address) {
        localFormData.applicantAddress = `${county}${town}${village}${address}`;
      }
    }
  }

  // Try to set facility location from step 2
  if (!localFormData.facilityLocation) {
    const step2Data = grantsStore.formData[2];
    if (step2Data) {
      const county = step2Data.addressCounty || '';
      const town = step2Data.addressTown || '';
      const village = step2Data.addressVillage || '';

      if (county || town || village) {
        localFormData.facilityLocation = `${county}${town}${village}`;
      }
    }
  }

  // Try to set facility number from step 2
  if (!localFormData.facilityNumber && grantsStore.formData[2]?.landNumber) {
    localFormData.facilityNumber = grantsStore.formData[2].landNumber;
  }

  // Try to set facility area (施作面積) from step 2
  if (!localFormData.facilityArea && grantsStore.formData[2]?.facilityAreaHa) { // Changed from landAreaHa
    localFormData.facilityArea = grantsStore.formData[2].facilityAreaHa;
  }

  // Try to set aboriginal area flag from step 2
  if (localFormData.isAboriginalArea === undefined &&
      grantsStore.formData[2]?.isAboriginalArea !== undefined) {
    localFormData.isAboriginalArea = grantsStore.formData[2].isAboriginalArea;
  }

  // Try to set facility type from step 4
  if (!localFormData.facilityType) {
    const step4Data = grantsStore.formData[4];
    if (step4Data) {
      const installation = step4Data.installationType || '';
      const irrigation = step4Data.irrigationType || '';

      if (installation || irrigation) {
        localFormData.facilityType = `${installation}${irrigation}系統`;
      }
    }
  }

  // Set application year if not set
  if (!localFormData.applicationYear) {
    // First try to extract year from case number if it's in a format like "112-XXX-XXX"
    if (grantsStore.caseNumber && grantsStore.caseNumber.includes('-')) {
      const yearPart = grantsStore.caseNumber.split('-')[0];
      if (!isNaN(parseInt(yearPart)) && yearPart.length <= 3) {
        localFormData.applicationYear = yearPart;
      }
    }
    // If still not set, try to get from step1's received date
    if (!localFormData.applicationYear && grantsStore.formData[1]?.receivedDate) {
      const receivedDate = grantsStore.formData[1].receivedDate;
      try {
        // Check if it's in YYYY-MM-DD format
        if (receivedDate.includes('-')) {
          const year = parseInt(receivedDate.split('-')[0]);
          if (!isNaN(year)) {
            localFormData.applicationYear = `${year - 1911}`;
          }
        }
      } catch (error) {
        console.error('Error parsing received date:', error);
      }
    }

    // As a last resort, use current year
    if (!localFormData.applicationYear) {
      const currentYear = new Date().getFullYear() - 1911; // Taiwan calendar year
      localFormData.applicationYear = `${currentYear}`;
    }
  }

  // Try to calculate subsidy amounts from previous steps
  try {
    let pipelineTotal = 0;
    let irrigationTotal = 0;
    let facilityTotal = 0;

    // Calculate from pipes in step 4 using the synchronized field names
    const step4Data = grantsStore.formData[4];
    if (step4Data) {
      // Calculate total from both main pipes
      let mainPipe1Total = 0;
      let mainPipe2Total = 0;

      // Main pipe 1 calculation
      if (step4Data.mainPipeQuantity && step4Data.mainPipeUnitPrice) {
        mainPipe1Total = parseInt(step4Data.mainPipeQuantity || '0') *
                        parseFloat(step4Data.mainPipeUnitPrice || '0');
      }

      // Main pipe 2 calculation (if enabled)
      if (step4Data.mainPipe2Enabled && step4Data.mainPipe2Quantity && step4Data.mainPipe2UnitPrice) {
        mainPipe2Total = parseInt(step4Data.mainPipe2Quantity || '0') *
                        parseFloat(step4Data.mainPipe2UnitPrice || '0');
      }

      pipelineTotal = mainPipe1Total + mainPipe2Total;

      // Update main pipes data with synchronized field names
      const mainPipeData = [];

      // Main pipe 1 data
      if (step4Data.mainPipeQuantity && parseInt(step4Data.mainPipeQuantity) > 0) {
        mainPipeData.push({
          name: '田間主管1',
          quantity: step4Data.mainPipeQuantity,
          unitPrice: step4Data.mainPipeUnitPrice ? parseFloat(step4Data.mainPipeUnitPrice).toLocaleString() : '-',
          totalPrice: mainPipe1Total > 0 ? mainPipe1Total.toLocaleString() : '-',
          unit: '支',
          remark: step4Data.mainPipeMaterialId ? `管材長度: ${step4Data.mainPipeLength} 公尺` : '-'
        });
      }

      // Main pipe 2 data (if enabled)
      if (step4Data.mainPipe2Enabled && step4Data.mainPipe2Quantity && parseInt(step4Data.mainPipe2Quantity) > 0) {
        mainPipeData.push({
          name: '田間主管2',
          quantity: step4Data.mainPipe2Quantity,
          unitPrice: step4Data.mainPipe2UnitPrice ? parseFloat(step4Data.mainPipe2UnitPrice).toLocaleString() : '-',
          totalPrice: mainPipe2Total > 0 ? mainPipe2Total.toLocaleString() : '-',
          unit: '支',
          remark: step4Data.mainPipe2MaterialId ? `管材長度: ${step4Data.mainPipe2Length} 公尺` : '-'
        });
      }

      if (mainPipeData.length > 0) {
        mainPipes.value = mainPipeData;
      }

      // Synchronize irrigation system from pipes array
      if (step4Data.pipes && step4Data.pipes.length > 0) {
        const pipes = step4Data.pipes;

        // Calculate legacy pipeline total for fallback
        const legacyPipelineTotal = pipes.reduce((sum: number, pipe: any) => {
          return sum + (typeof pipe.totalPrice === 'number'
                        ? pipe.totalPrice
                        : parseInt(pipe.totalPrice || '0'));
        }, 0);

        // Use legacy total if current calculation is 0
        if (pipelineTotal === 0) {
          pipelineTotal = legacyPipelineTotal;
        }

        // Update main pipes data from legacy format if current data is empty
        if (mainPipes.value.length === 0) {
          const legacyMainPipeData = pipes.filter((p: any) => p.type === 'main').map((p: any) => ({
            name: p.name || '田間主管',
            quantity: p.quantity,
            unitPrice: p.unitPrice,
            totalPrice: typeof p.totalPrice === 'number'
                        ? p.totalPrice.toLocaleString()
                        : p.totalPrice,
            unit: '支',
            remark: `${p.specification || ''}`
          }));

          if (legacyMainPipeData.length > 0) {
            mainPipes.value = legacyMainPipeData;
          }
        }

        // Build irrigation system from pipes array
        const irrigationComponents = {
          mainGroup: [] as Array<{id: string, name: string, specification: string, quantity: string}>,
          branchGroup: [] as Array<{id: string, name: string, specification: string, quantity: string}>,
          endDevices: [] as Array<{id: string, name: string, specification: string, quantity: string}>
        };

        // Group components by groupId
        // Group 1: 主管組 -> mainGroup
        // Group 2: 支管組 -> branchGroup
        // Group 3,4,5,6,7,8: Various end devices and terminal components -> endDevices
        pipes.forEach((pipe: any, index: number) => {
          const component = {
            id: `${pipe.groupId}-${index}`,
            name: pipe.matname || pipe.name || '未知組件',
            specification: pipe.specification || `${pipe.spec1 || ''} ${pipe.spec2 || ''} ${pipe.spec3 || ''}`.trim() || '-',
            quantity: `*${pipe.matamount || pipe.quantity || 0}`
          };

          if (pipe.groupId === 1) {
            // 主管組 - but exclude main pipes that are already shown separately
            if (!pipe.matname?.includes('主管') || pipe.description?.includes('配件')) {
              irrigationComponents.mainGroup.push(component);
            }
          } else if (pipe.groupId === 2) {
            // 支管組
            irrigationComponents.branchGroup.push(component);
          } else if ([3, 4, 5, 6, 7, 8].includes(pipe.groupId)) {
            // 穿孔管組(3), 滴水管組(4), 豎管組(5), 固定設施組(6), 消耗性材料(7), 末端設施(8)
            irrigationComponents.endDevices.push(component);
          }
        });

        // Calculate irrigation system total
        irrigationTotal = pipes
          .filter((p: any) => [2, 3, 4, 5, 6, 7, 8].includes(p.groupId)) // Exclude main pipe group
          .reduce((sum: number, pipe: any) => {
            return sum + (typeof pipe.totalPrice === 'number'
                          ? pipe.totalPrice
                          : parseInt(pipe.totalPrice || '0'));
          }, 0);

        // Update irrigation system if we have components
        if (irrigationComponents.mainGroup.length > 0 ||
            irrigationComponents.branchGroup.length > 0 ||
            irrigationComponents.endDevices.length > 0) {

          irrigationSystem.value = [{
            name: '灌溉系統',
            quantity: '全',
            unitPrice: '-',
            totalPrice: irrigationTotal > 0 ? irrigationTotal.toLocaleString() : '-',
            unit: '式',
            remark: irrigationComponents
          }];
        }
      }

      // Calculate and set pipeLineTotal (mainPipes + irrigationSystem)
      // This calculation should ALWAYS happen, regardless of pipes array existence
      const totalPipelineAmount = pipelineTotal + irrigationTotal;
      localFormData.pipeLineTotal = totalPipelineAmount.toLocaleString();
      // localFormData.totalPipelineAmount = totalPipelineAmount.toLocaleString();
    }

    // Calculate from facilities in step 3
    if (grantsStore.formData[3]?.facilities) {
      const facilities = grantsStore.formData[3].facilities;
      facilityTotal = facilities.reduce((sum: number, facility: any) => {
        return sum + (typeof facility.totalPrice === 'number'
                     ? facility.totalPrice
                     : parseInt(facility.totalPrice || '0'));
      }, 0);

      // Update control facilities data
      const controlData = facilities.map((f: any) => ({
        name: f.typeLabel || f.name,
        specification: '',
        quantity: f.quantity,
        unitPrice: typeof f.unitPrice === 'number'
                   ? f.unitPrice.toLocaleString()
                   : f.unitPrice,
        totalPrice: typeof f.totalPrice === 'number'
                    ? f.totalPrice.toLocaleString()
                    : f.totalPrice,
        unit: f.type === 'power' ? '台' : (f.type === 'storage' ? '座' : '台'),
        remark: f.remark || f.name
      }));

      if (controlData.length > 0) {
        controlFacilities.value = controlData;
      }
    }

    // Update subsidy amounts if we calculated valid values
    const totalPipelineSubsidy = pipelineTotal + irrigationTotal;
    if (totalPipelineSubsidy > 0) {
      localFormData.pipeLineSubsidy = totalPipelineSubsidy.toLocaleString();
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
    localFormData.totalBudget = (pipelineValue + facilityValue + designValue).toLocaleString();
  } catch (error) {
    console.error('Error calculating subsidies:', error);
  }

  // Initial update to parent
  updateFormData();
});

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

    // Update facility arrays
    if (newData.mainPipes &&
        JSON.stringify(newData.mainPipes) !== JSON.stringify(mainPipes.value)) {
      mainPipes.value = [...newData.mainPipes];
    }

    if (newData.irrigationSystem &&
        JSON.stringify(newData.irrigationSystem) !== JSON.stringify(irrigationSystem.value)) {
      irrigationSystem.value = [...newData.irrigationSystem];
    }

    if (newData.controlFacilities &&
        JSON.stringify(newData.controlFacilities) !== JSON.stringify(controlFacilities.value)) {
      controlFacilities.value = [...newData.controlFacilities];
    }
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
</style>
