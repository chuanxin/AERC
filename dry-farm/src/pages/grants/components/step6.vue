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

const props = defineProps<{
  formData: any;  // 接收父组件数据
  currentStep: number;
}>();

const emit = defineEmits(['update:formData', 'validated', 'goBack']);
const localValid = ref(true); // 这个页面主要是预览，默认为有效
const form = ref(null);

// 本地表单数据
const localFormData = reactive({
  applicationYear: '',  // 申请年度
  caseNumber: '',       // 案号
  applicantName: '',    // 农户姓名
  applicantAddress: '', // 农户住址
  facilityLocation: '', // 设施地段
  facilityNumber: '',   // 设施地号
  facilityArea: '',     // 设施面积
  facilityType: '',     // 设施型式

  // 经费相关
  pipeLineSubsidy: '8,704', // A项补助费
  facilitySubsidy: '4,500', // B项补助费
  designFee: '174',         // 规划设计费
  totalBudget: '13,378',    // 总预算

  // 是否为原民区
  isAboriginalArea: false,
});

// 将金额转换为中文大写
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

// 原民区加成文字
const isAboriginalAreaText = computed(() => {
  return localFormData.isAboriginalArea ? '(原民地+10%)' : '';
});

// 設施資料（可从父组件传入或在这里生成示例数据）
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

// 末端设施
const endDevices = ref([
  { name: '單口噴頭-塑鋼', specification: '1/2" *104', quantity: 1, unitPrice: '', totalPrice: '4,481', unit: '只' }
]);

// 灌溉调控设施
const controlFacilities = ref([
  { name: '動力設施', specification: '', quantity: 1, unitPrice: '4500', totalPrice: '4,500', unit: '台', remark: '馬達+抽水機*1' },
  { name: '調蓄設施', specification: '', quantity: '', unitPrice: '', totalPrice: '', unit: '座', remark: '' },
  { name: '調節控制設施', specification: '', quantity: '', unitPrice: '', totalPrice: '', unit: '台', remark: '' }
]);

// 打印文档
const printDocument = (documentType: string) => {
  console.log(`列印檔案: ${documentType}`);
  // 这里可以实现打印逻辑
};

// 上一步
const goToPreviousStep = () => {
  emit('goBack');
};

// 下一步
const goToNextStep = () => {
  emit('validated', { valid: true, step: 6 });
};

// 更新父组件数据
const updateFormData = () => {
  emit('update:formData', {
    ...props.formData,
    ...localFormData,
    valid: localValid.value
  });
};

// 初始化数据
onMounted(() => {
  // 从父组件获取并初始化数据
  if (props.formData) {
    // 基本信息
    localFormData.applicationYear = props.formData.applicationYear || '113';
    localFormData.caseNumber = props.formData.caseNumber || '113010001';
    localFormData.applicantName = props.formData.name || props.formData.applicantName || '林嘉寶';

    // 拼接完整地址
    if (props.formData.address) {
      localFormData.applicantAddress = props.formData.address;
    } else {
      // 尝试从步骤1获取地址信息
      const county = props.formData.county || '';
      const town = props.formData.town || '';
      const village = props.formData.village || '';
      const detailAddress = props.formData.address || '';
      localFormData.applicantAddress = `${county}${town}${village}${detailAddress}`;
    }

    // 设施信息
    if (props.formData.step2) {
      localFormData.facilityLocation = props.formData.step2.addressCounty + props.formData.step2.addressTown + '瓦厝埔段';
      localFormData.facilityNumber = props.formData.step2.landNumber || '0966-0001';
      localFormData.facilityArea = props.formData.step2.landAreaHa || '0.8455';
      localFormData.isAboriginalArea = props.formData.step2.isAboriginalArea || false;
    } else {
      // 使用默认值
      localFormData.facilityLocation = '嘉義縣竹崎鄉瓦厝埔段';
      localFormData.facilityNumber = '0966-0001';
      localFormData.facilityArea = '0.8455';
    }

    // 设施类型
    if (props.formData.step4) {
      const installationType = props.formData.step4.installationType || '';
      const irrigationType = props.formData.step4.irrigationType || '';
      localFormData.facilityType = `${installationType}${irrigationType}系統`;
    } else {
      localFormData.facilityType = '地表定置式噴頭式系統';
    }

    // 从父组件获取设施明细数据
    if (props.formData.pipes && props.formData.pipes.length > 0) {
      const pipeData = props.formData.pipes;

      // 分类整理数据
      mainPipes.value = pipeData.filter(p => p.type === 'main').map(p => ({
        name: '田間主管',
        length: p.length || '164',
        quantity: p.quantity || 0,
        unitPrice: p.unitPrice || 0,
        totalPrice: p.totalPrice.toLocaleString() || '',
        unit: p.specification?.includes('支') ? '支' : '個'
      }));

      branchPipes.value = pipeData.filter(p => p.type === 'branch').map(p => ({
        name: p.name || 'PVC',
        specification: p.specification || '',
        quantity: p.quantity || 0,
        unitPrice: p.unitPrice || 0,
        totalPrice: p.totalPrice.toLocaleString() || '',
        unit: p.specification?.includes('只') ? '只' : '支'
      }));

      endDevices.value = pipeData.filter(p => p.type === 'end').map(p => ({
        name: p.name || '',
        specification: p.specification || '',
        quantity: p.quantity || 0,
        unitPrice: p.unitPrice || 0,
        totalPrice: p.totalPrice.toLocaleString() || '',
        unit: p.specification?.includes('只') ? '只' : '个'
      }));
    }

    // 获取控制设施数据
    if (props.formData.facilities && props.formData.facilities.length > 0) {
      controlFacilities.value = props.formData.facilities.map(f => ({
        name: f.typeLabel || '',
        specification: '',
        quantity: f.quantity || 0,
        unitPrice: f.unitPrice?.toLocaleString() || '',
        totalPrice: f.totalPrice?.toLocaleString() || '',
        unit: f.type === 'power' ? '台' : (f.type === 'storage' ? '座' : '台'),
        remark: f.remark || f.name
      }));
    }

    // 计算总费用
    // 这里可以根据实际情况对补助费用进行计算
    // 但通常这些值会从父组件传入
    localFormData.pipeLineSubsidy = props.formData.pipeLineSubsidy || '8,704';
    localFormData.facilitySubsidy = props.formData.facilitySubsidy || '4,500';
    localFormData.designFee = props.formData.designFee || '174';

    // 计算总预算
    const pipeLineValue = parseInt(localFormData.pipeLineSubsidy.replace(/,/g, '')) || 0;
    const facilityValue = parseInt(localFormData.facilitySubsidy.replace(/,/g, '')) || 0;
    const designValue = parseInt(localFormData.designFee.replace(/,/g, '')) || 0;

    const total = pipeLineValue + facilityValue + designValue;
    localFormData.totalBudget = total.toLocaleString();
  }

  // 确保数据可用
  updateFormData();
});

// 监听父组件数据变化
watch(() => props.formData, (newVal) => {
  if (newVal) {
    // 数据更新逻辑
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
