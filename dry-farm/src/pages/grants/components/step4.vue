<template>
  <div
    ref="stepContent"
    class="step-content"
  >
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
          <!-- 補助來源區域 -->
          <v-card
            class="mb-4"
            variant="outlined"
          >
            <v-card-title class="bg-light-blue-lighten-4 d-flex align-center py-2 px-4">
              <v-icon
                class="me-2"
                size="small"
              >
                mdi-currency-usd
              </v-icon>
              <span class="text-subtitle-1 font-weight-medium">補助來源</span>
            </v-card-title>

            <v-card-text class="pa-4">
              <v-sheet
                class="pa-3 rounded"
                color="rgb(255, 243, 205)"
              >
                <v-select
                  v-model="localFormData.fundingSource"
                  :items="fundingSourceOptions"
                  label="補助來源"
                  variant="outlined"
                  density="comfortable"
                  style="max-width: 400px"
                  :rules="[v => !!v || '請選擇補助來源']"
                  @update:model-value="updateFormData"
                />
              </v-sheet>
            </v-card-text>
          </v-card>

          <!-- 主管區域 -->
          <v-card
            class="mb-4"
            variant="outlined"
          >
            <v-card-title class="bg-light-blue-lighten-4 d-flex align-center py-2 px-4">
              <v-icon class="me-2" size="small">mdi-pipe</v-icon>
              <span class="text-subtitle-1 font-weight-medium">主管</span>
            </v-card-title>

            <v-card-text class="pa-4">
              <v-sheet class="pa-3 rounded" color="grey-lighten-5">
                <div class="d-flex align-center flex-wrap">
                  <v-text-field
                    v-model="localFormData.mainPipeLength"
                    label="長度(M)"
                    variant="outlined"
                    density="comfortable"
                    class="me-2 mb-2"
                    style="width: 120px"
                    :rules="[v => !!v || '請輸入長度']"
                    @update:model-value="updateFormData"
                  />

                  <v-select
                    v-model="localFormData.mainPipeDiameter"
                    :items="pipeDiameterOptions"
                    label="管徑(吋)"
                    variant="outlined"
                    density="comfortable"
                    class="me-2 mb-2"
                    style="width: 120px"
                    :rules="[v => !!v || '請選擇管徑']"
                    @update:model-value="updateFormData"
                  />

                  <v-select
                    v-model="localFormData.mainPipeMaterial"
                    :items="pipeMaterialOptions"
                    label="材質"
                    variant="outlined"
                    density="comfortable"
                    class="me-2 mb-2"
                    style="width: 120px"
                    :rules="[v => !!v || '請選擇材質']"
                    @update:model-value="updateFormData"
                  />

                  <v-text-field
                    v-model="localFormData.mainPipeUnitPrice"
                    label="單價"
                    variant="outlined"
                    density="comfortable"
                    class="me-2 mb-2"
                    style="width: 100px"
                    :rules="[v => !!v || '請輸入單價']"
                    @update:model-value="updateFormData"
                  />

                  <v-text-field
                    v-model="localFormData.mainPipeQuantity"
                    label="數量"
                    variant="outlined"
                    density="comfortable"
                    class="me-2 mb-2"
                    style="width: 80px"
                    :rules="[v => !!v || '請輸入數量']"
                    @update:model-value="updateFormData"
                  />

                  <v-text-field
                    v-model="mainPipeTotalPrice"
                    label="總價"
                    variant="outlined"
                    density="comfortable"
                    class="me-2 mb-2"
                    style="width: 120px"
                    readonly
                    bg-color="grey-lighten-4"
                  />
                </div>

                <div class="d-flex justify-end">
                  <v-btn
                    color="primary"
                    size="small"
                    @click="addMainPipe"
                    :disabled="!canAddMainPipe"
                  >
                    <v-icon start size="small">mdi-plus</v-icon>
                    新增主管
                  </v-btn>
                </div>
              </v-sheet>
            </v-card-text>
          </v-card>

          <!-- 支管布置區域 -->
          <v-card class="mb-4" variant="outlined">
            <v-card-title class="bg-light-blue-lighten-4 d-flex align-center py-2 px-4">
              <v-icon class="me-2" size="small">mdi-pipe-disconnected</v-icon>
              <span class="text-subtitle-1 font-weight-medium">支管</span>
            </v-card-title>

            <v-card-text class="pa-4">
              <v-sheet class="pa-3 rounded" color="grey-lighten-5">
                <div class="d-flex align-center mb-3">
                  <div class="d-flex align-center flex-wrap">
                    <div class="me-3 mb-2">
                      <div class="text-body-2">支管行距(SL)</div>
                      <div class="d-flex align-center">
                        <v-text-field
                          v-model="localFormData.branchPipeSpacing"
                          variant="outlined"
                          density="comfortable"
                          style="width: 80px"
                          class="me-1"
                        />
                        <span>M</span>
                      </div>
                    </div>

                    <div class="me-3 mb-2">
                      <div class="text-body-2">噴頭間距(SL)</div>
                      <div class="d-flex align-center">
                        <v-text-field
                          v-model="localFormData.sprinklerSpacing"
                          variant="outlined"
                          density="comfortable"
                          style="width: 80px"
                          class="me-1"
                        />
                        <span>M</span>
                      </div>
                    </div>

                    <div class="me-3 mb-2">
                      <div class="text-body-2">豎管高(H)</div>
                      <div class="d-flex align-center">
                        <v-text-field
                          v-model="localFormData.riserHeight"
                          variant="outlined"
                          density="comfortable"
                          style="width: 80px"
                          class="me-1"
                        />
                        <span>M</span>
                      </div>
                    </div>

                    <div class="mb-2">
                      <v-select
                        v-model="localFormData.variantType"
                        :items="variantTypeOptions"
                        label="變徑"
                        variant="outlined"
                        density="comfortable"
                        style="width: 150px"
                      />
                    </div>
                  </div>
                </div>

                <div class="d-flex align-center flex-wrap">
                  <v-text-field
                    v-model="localFormData.branchPipeLength"
                    label="長度(M)"
                    variant="outlined"
                    density="comfortable"
                    class="me-2 mb-2"
                    style="width: 120px"
                    @update:model-value="updateFormData"
                  />

                  <v-select
                    v-model="localFormData.branchPipeDiameter"
                    :items="pipeDiameterOptions"
                    label="管徑(吋)"
                    variant="outlined"
                    density="comfortable"
                    class="me-2 mb-2"
                    style="width: 120px"
                    @update:model-value="updateFormData"
                  />

                  <v-select
                    v-model="localFormData.branchPipeMaterial"
                    :items="pipeMaterialOptions"
                    label="材質"
                    variant="outlined"
                    density="comfortable"
                    class="me-2 mb-2"
                    style="width: 120px"
                    @update:model-value="updateFormData"
                  />

                  <v-text-field
                    v-model="localFormData.branchPipeUnitPrice"
                    label="單價"
                    variant="outlined"
                    density="comfortable"
                    class="me-2 mb-2"
                    style="width: 100px"
                    @update:model-value="updateFormData"
                  />

                  <v-text-field
                    v-model="localFormData.branchPipeQuantity"
                    label="數量"
                    variant="outlined"
                    density="comfortable"
                    class="me-2 mb-2"
                    style="width: 80px"
                    @update:model-value="updateFormData"
                  />

                  <v-text-field
                    v-model="branchPipeTotalPrice"
                    label="總價"
                    variant="outlined"
                    density="comfortable"
                    class="me-2 mb-2"
                    style="width: 120px"
                    readonly
                    bg-color="grey-lighten-4"
                  />
                </div>

                <div class="d-flex justify-end">
                  <v-btn
                    color="primary"
                    size="small"
                    @click="addBranchPipe"
                    :disabled="!canAddBranchPipe"
                  >
                    <v-icon start size="small">mdi-plus</v-icon>
                    新增支管
                  </v-btn>
                </div>
              </v-sheet>
            </v-card-text>
          </v-card>

          <!-- 末端設施區域 -->
          <v-card class="mb-4" variant="outlined">
            <v-card-title class="bg-light-blue-lighten-4 d-flex align-center py-2 px-4">
              <v-icon class="me-2" size="small">mdi-sprinkler</v-icon>
              <span class="text-subtitle-1 font-weight-medium">末端設施</span>
            </v-card-title>

            <v-card-text class="pa-4">
              <v-sheet class="pa-3 rounded" color="grey-lighten-5">
                <div class="d-flex align-center flex-wrap mb-2">
                  <v-select
                    v-model="localFormData.irrigationType"
                    :items="irrigationTypeOptions"
                    label="灌溉型式"
                    variant="outlined"
                    density="comfortable"
                    class="me-2 mb-2"
                    style="width: 160px"
                    @update:model-value="onIrrigationTypeChange"
                  />

                  <v-select
                    v-model="localFormData.installationType"
                    :items="installationTypeOptions"
                    label="設施型式"
                    variant="outlined"
                    density="comfortable"
                    class="me-2 mb-2"
                    style="width: 160px"
                    @update:model-value="onInstallationTypeChange"
                  />

                  <v-select
                    v-model="localFormData.waterSource"
                    :items="waterSourceOptions"
                    label="灌溉水源"
                    variant="outlined"
                    density="comfortable"
                    class="me-2 mb-2"
                    style="width: 160px"
                    @update:model-value="updateFormData"
                  />
                </div>

                <div class="d-flex align-center flex-wrap">
                  <v-select
                    v-model="localFormData.endFacilityType"
                    :items="endFacilityOptions"
                    label="末端設施"
                    variant="outlined"
                    density="comfortable"
                    class="me-2 mb-2"
                    style="width: 180px"
                    @update:model-value="updateFormData"
                  />

                  <v-select
                    v-model="localFormData.endFacilityDiameter"
                    :items="pipeDiameterOptions"
                    label="管徑(吋)"
                    variant="outlined"
                    density="comfortable"
                    class="me-2 mb-2"
                    style="width: 120px"
                    @update:model-value="updateFormData"
                  />

                  <v-select
                    v-model="localFormData.endFacilityMaterial"
                    :items="pipeMaterialOptions"
                    label="材質"
                    variant="outlined"
                    density="comfortable"
                    class="me-2 mb-2"
                    style="width: 120px"
                    @update:model-value="updateFormData"
                  />

                  <v-text-field
                    v-model="localFormData.endFacilityUnitPrice"
                    label="單價"
                    variant="outlined"
                    density="comfortable"
                    class="me-2 mb-2"
                    style="width: 100px"
                    @update:model-value="updateFormData"
                  />

                  <v-text-field
                    v-model="localFormData.endFacilityQuantity"
                    label="數量"
                    variant="outlined"
                    density="comfortable"
                    class="me-2 mb-2"
                    style="width: 80px"
                    @update:model-value="updateFormData"
                  />

                  <v-text-field
                    v-model="endFacilityTotalPrice"
                    label="總價"
                    variant="outlined"
                    density="comfortable"
                    class="me-2 mb-2"
                    style="width: 120px"
                    readonly
                    bg-color="grey-lighten-4"
                  />
                </div>

                <div class="d-flex justify-end">
                  <v-btn
                    color="primary"
                    size="small"
                    @click="addEndFacility"
                    :disabled="!canAddEndFacility"
                  >
                    <v-icon start size="small">mdi-plus</v-icon>
                    新增末端設施
                  </v-btn>
                </div>
              </v-sheet>
            </v-card-text>
          </v-card>

          <!-- 管路設施列表 -->
          <v-card variant="outlined">
            <v-card-title class="bg-light-blue-lighten-4 d-flex align-center py-2 px-4">
              <v-icon class="me-2" size="small">mdi-format-list-bulleted</v-icon>
              <span class="text-subtitle-1 font-weight-medium">已新增管路設施列表</span>
            </v-card-title>

            <v-card-text class="pa-4">
              <v-table class="rounded border">
                <thead class="bg-grey-lighten-3">
                  <tr>
                    <th class="text-center" style="width: 50px">NO.</th>
                    <th>補助來源</th>
                    <th>類別</th>
                    <th>名稱</th>
                    <th>規格/單位</th>
                    <th class="text-center">單價</th>
                    <th class="text-center">數量</th>
                    <th class="text-center">總價</th>
                    <th class="text-center" style="width: 50px">排序</th>
                    <th class="text-center" style="width: 80px">刪除</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(pipe, index) in localFormData.pipes" :key="index">
                    <td class="text-center">{{ index + 1 }}</td>
                    <td>{{ pipe.source }}</td>
                    <td>{{ pipe.typeLabel }}</td>
                    <td>{{ pipe.name }}</td>
                    <td>{{ pipe.specification }}</td>
                    <td class="text-center">{{ pipe.unitPrice }}</td>
                    <td class="text-center">{{ pipe.quantity }}</td>
                    <td class="text-center">{{ pipe.totalPrice }}</td>
                    <td class="text-center">
                      <div class="d-flex flex-column align-center">
                        <v-btn
                          icon
                          size="x-small"
                          color="primary"
                          variant="text"
                          :disabled="index === 0"
                          @click="movePipeUp(index)"
                        >
                          <v-icon size="small">mdi-chevron-up</v-icon>
                        </v-btn>
                        <v-btn
                          icon
                          size="x-small"
                          color="primary"
                          variant="text"
                          :disabled="index === localFormData.pipes.length - 1"
                          @click="movePipeDown(index)"
                        >
                          <v-icon size="small">mdi-chevron-down</v-icon>
                        </v-btn>
                      </div>
                    </td>
                    <td class="text-center">
                      <v-btn
                        icon
                        size="x-small"
                        color="error"
                        variant="text"
                        @click="removePipe(index)"
                      >
                        <v-icon>mdi-close</v-icon>
                      </v-btn>
                    </td>
                  </tr>
                  <tr v-if="localFormData.pipes.length === 0">
                    <td colspan="10" class="text-center py-3 text-grey">
                      尚未新增任何管路設施
                    </td>
                  </tr>
                  <tr class="text-muted text-caption bg-grey-lighten-4">
                    <td colspan="7" class="text-right font-weight-bold">合計</td>
                    <td class="text-center font-weight-bold">{{ totalPipesPrice }}</td>
                    <td colspan="2"></td>
                  </tr>
                </tbody>
              </v-table>
            </v-card-text>
          </v-card>
        </v-form>
      </v-card-text>
    </v-card>
  </div>
</template>

<script setup lang="ts">
import { useGrantsStore } from '@/stores/grants';

// Props and emits
const props = defineProps({
  formData: {
    type: Object,
    required: true,
    default: () => ({})
  },
  currentStep: {
    type: Number,
    required: true
  }
});

const emit = defineEmits(['update:formData', 'validated', 'go-back']);

// Access the grants store
const grantsStore = useGrantsStore();

// Form validation references
const form = ref(null);
const localValid = ref(true);

// 本地表單數據
const localFormData = reactive({
  // 補助來源
  fundingSource: '',

  // 主管
  mainPipeLength: '',
  mainPipeDiameter: '',
  mainPipeMaterial: '',
  mainPipeUnitPrice: '',
  mainPipeQuantity: '',

  // 支管
  branchPipeSpacing: '',
  sprinklerSpacing: '',
  riserHeight: '',
  variantType: '',
  branchPipeLength: '',
  branchPipeDiameter: '',
  branchPipeMaterial: '',
  branchPipeUnitPrice: '',
  branchPipeQuantity: '',

  // 末端設施
  irrigationType: '',
  installationType: '',
  waterSource: '',
  endFacilityType: '',
  endFacilityDiameter: '',
  endFacilityMaterial: '',
  endFacilityUnitPrice: '',
  endFacilityQuantity: '',

  // 管路列表
  pipes: [] as Array<{
    source: string;
    type: string;
    typeLabel: string;
    name: string;
    specification: string;
    unitPrice: number;
    quantity: number;
    totalPrice: number;
  }>,

  // Always valid for seamless navigation
  valid: true
});

// 選項
const fundingSourceOptions = [
  '農田水利署',
  '七星管理處作業基金',
  '瑠公管理處作業基金'
];

const pipeDiameterOptions = [
  '1/2"', '3/4"', '1/8"', '3/8"', '1"', '2"', '3"', '4"', '5"', '其他'
];

const pipeMaterialOptions = [
  'PE', 'PVC', 'PVCA', 'PVCB', 'PVCE', 'PVCS', 'PVCW', '不鏽鋼', '鐵', '其他'
];

const variantTypeOptions = [
  '全長不變徑',
  '1/3管長變徑'
];

const irrigationTypeOptions = [
  '穿孔管系統',
  '噴頭式系統',
  '微噴系統',
  '滴灌系統',
  '其他'
];

const installationTypeOptions = [
  '埋設固定式',
  '地表定置式',
  '附掛棚架式'
];

const waterSourceOptions = [
  '灌溉渠道',
  '野溪',
  '埤(池)塘',
  '地下水',
  '其他'
];

const endFacilityOptions = [
  '穿孔管-單管',
  '噴頭式-單口噴頭',
  '噴頭式-雙口噴頭',
  '微噴-單向微噴霧',
  '微噴-雙向微噴霧',
  '滴灌-雙向微噴霧'
];

// 計算屬性
const mainPipeTotalPrice = computed(() => {
  const length = parseFloat(localFormData.mainPipeLength) || 0;
  const unitPrice = parseFloat(localFormData.mainPipeUnitPrice) || 0;
  const quantity = parseFloat(localFormData.mainPipeQuantity) || 0;
  return (length * unitPrice * quantity).toString();
});

const branchPipeTotalPrice = computed(() => {
  const length = parseFloat(localFormData.branchPipeLength) || 0;
  const unitPrice = parseFloat(localFormData.branchPipeUnitPrice) || 0;
  const quantity = parseFloat(localFormData.branchPipeQuantity) || 0;
  return (length * unitPrice * quantity).toString();
});

const endFacilityTotalPrice = computed(() => {
  const unitPrice = parseFloat(localFormData.endFacilityUnitPrice) || 0;
  const quantity = parseFloat(localFormData.endFacilityQuantity) || 0;
  return (unitPrice * quantity).toString();
});

const totalPipesPrice = computed(() => {
  const total = localFormData.pipes.reduce((sum, pipe) => sum + (pipe.totalPrice || 0), 0);
  return total.toLocaleString();
});

// 驗證條件
const canAddMainPipe = computed(() => {
  return !!localFormData.fundingSource &&
         !!localFormData.mainPipeLength &&
         !!localFormData.mainPipeDiameter &&
         !!localFormData.mainPipeMaterial &&
         !!localFormData.mainPipeUnitPrice &&
         !!localFormData.mainPipeQuantity;
});

const canAddBranchPipe = computed(() => {
  return !!localFormData.fundingSource &&
         !!localFormData.branchPipeLength &&
         !!localFormData.branchPipeDiameter &&
         !!localFormData.branchPipeMaterial &&
         !!localFormData.branchPipeUnitPrice &&
         !!localFormData.branchPipeQuantity;
});

const canAddEndFacility = computed(() => {
  return !!localFormData.fundingSource &&
         !!localFormData.endFacilityType &&
         !!localFormData.endFacilityDiameter &&
         !!localFormData.endFacilityMaterial &&
         !!localFormData.endFacilityUnitPrice &&
         !!localFormData.endFacilityQuantity;
});

// 方法
const onIrrigationTypeChange = () => {
  updateFormData();
};

const onInstallationTypeChange = () => {
  updateFormData();
};

// 添加主管
const addMainPipe = () => {
  if (canAddMainPipe.value) {
    const length = parseFloat(localFormData.mainPipeLength);
    const unitPrice = parseFloat(localFormData.mainPipeUnitPrice);
    const quantity = parseFloat(localFormData.mainPipeQuantity);

    localFormData.pipes.push({
      source: localFormData.fundingSource,
      type: 'main',
      typeLabel: '主管',
      name: `${localFormData.mainPipeMaterial} ${localFormData.mainPipeDiameter}`,
      specification: `${localFormData.mainPipeDiameter} / 支`,
      unitPrice: unitPrice,
      quantity: quantity,
      totalPrice: length * unitPrice * quantity
    });

    // 保留補助來源，清空其他欄位
    const fundingSource = localFormData.fundingSource;
    localFormData.mainPipeLength = '';
    localFormData.mainPipeDiameter = '';
    localFormData.mainPipeMaterial = '';
    localFormData.mainPipeUnitPrice = '';
    localFormData.mainPipeQuantity = '';
    localFormData.fundingSource = fundingSource;

    updateFormData();
  }
};

// 添加支管
const addBranchPipe = () => {
  if (canAddBranchPipe.value) {
    const length = parseFloat(localFormData.branchPipeLength);
    const unitPrice = parseFloat(localFormData.branchPipeUnitPrice);
    const quantity = parseFloat(localFormData.branchPipeQuantity);

    localFormData.pipes.push({
      source: localFormData.fundingSource,
      type: 'branch',
      typeLabel: '支管',
      name: `${localFormData.branchPipeMaterial} ${localFormData.branchPipeDiameter}`,
      specification: `${localFormData.branchPipeDiameter} / 只`,
      unitPrice: unitPrice,
      quantity: quantity,
      totalPrice: length * unitPrice * quantity
    });

    // 保留部分欄位，清空其他欄位
    const fundingSource = localFormData.fundingSource;
    const branchPipeSpacing = localFormData.branchPipeSpacing;
    const sprinklerSpacing = localFormData.sprinklerSpacing;
    const riserHeight = localFormData.riserHeight;
    const variantType = localFormData.variantType;

    localFormData.branchPipeLength = '';
    localFormData.branchPipeDiameter = '';
    localFormData.branchPipeMaterial = '';
    localFormData.branchPipeUnitPrice = '';
    localFormData.branchPipeQuantity = '';

    localFormData.fundingSource = fundingSource;
    localFormData.branchPipeSpacing = branchPipeSpacing;
    localFormData.sprinklerSpacing = sprinklerSpacing;
    localFormData.riserHeight = riserHeight;
    localFormData.variantType = variantType;

    updateFormData();
  }
};

// 添加末端設施
const addEndFacility = () => {
  if (canAddEndFacility.value) {
    const unitPrice = parseFloat(localFormData.endFacilityUnitPrice);
    const quantity = parseFloat(localFormData.endFacilityQuantity);

    localFormData.pipes.push({
      source: localFormData.fundingSource,
      type: 'end',
      typeLabel: '末端設施',
      name: localFormData.endFacilityType,
      specification: `${localFormData.endFacilityDiameter} / 只`,
      unitPrice: unitPrice,
      quantity: quantity,
      totalPrice: unitPrice * quantity
    });

    // 保留部分欄位，清空其他欄位
    const fundingSource = localFormData.fundingSource;
    const irrigationType = localFormData.irrigationType;
    const installationType = localFormData.installationType;
    const waterSource = localFormData.waterSource;

    localFormData.endFacilityType = '';
    localFormData.endFacilityDiameter = '';
    localFormData.endFacilityMaterial = '';
    localFormData.endFacilityUnitPrice = '';
    localFormData.endFacilityQuantity = '';

    localFormData.fundingSource = fundingSource;
    localFormData.irrigationType = irrigationType;
    localFormData.installationType = installationType;
    localFormData.waterSource = waterSource;

    updateFormData();
  }
};

// 移除管路
const removePipe = (index: number) => {
  localFormData.pipes.splice(index, 1);
  updateFormData();
};

// 移動管路順序（上移）
const movePipeUp = (index: number) => {
  if (index > 0) {
    const temp = localFormData.pipes[index];
    localFormData.pipes[index] = localFormData.pipes[index - 1];
    localFormData.pipes[index - 1] = temp;
    updateFormData();
  }
};

// 移動管路順序（下移）
const movePipeDown = (index: number) => {
  if (index < localFormData.pipes.length - 1) {
    const temp = localFormData.pipes[index];
    localFormData.pipes[index] = localFormData.pipes[index + 1];
    localFormData.pipes[index + 1] = temp;
    updateFormData();
  }
};

// 更新父組件數據
const updateFormData = () => {
  emit('update:formData', {
    ...props.formData,
    ...localFormData,
    valid: true // Always true for seamless navigation
  });
};

// 初始化數據
onMounted(() => {
  console.log("Step 4 mounted, formData:", props.formData);

  // 從父組件接收數據
  if (props.formData) {
    // 設置基本屬性
    Object.keys(localFormData).forEach(key => {
      if (key !== 'pipes' && props.formData[key] !== undefined) {
        localFormData[key] = props.formData[key];
      }
    });

    // 確保管路列表被正確設置
    if (Array.isArray(props.formData.pipes)) {
      localFormData.pipes = [...props.formData.pipes];
    }
  }

  // 如果沒有設置補助來源，設置默認值
  if (!localFormData.fundingSource) {
    localFormData.fundingSource = '農田水利署';
  }

  // 如果管路列表為空，添加示例數據
  if (!localFormData.pipes || localFormData.pipes.length === 0) {
    localFormData.pipes = [
      {
        source: '農田水利署',
        type: 'main',
        typeLabel: '主管',
        name: 'PVC 1"',
        specification: '1" / 支',
        unitPrice: 44,
        quantity: 2,
        totalPrice: 88
      },
      {
        source: '農田水利署',
        type: 'branch',
        typeLabel: '支管',
        name: 'PVC 3/4"',
        specification: '3/4" / 只',
        unitPrice: 50,
        quantity: 1,
        totalPrice: 50
      },
      {
        source: '農田水利署',
        type: 'end',
        typeLabel: '末端設施',
        name: '單口噴頭-塑鋼',
        specification: '1/2" / 只',
        unitPrice: 35,
        quantity: 1,
        totalPrice: 35
      }
    ];
  }

  // Initial update to parent
  updateFormData();
});

// 監聽父組件數據變化
watch(() => props.formData, (newVal) => {
  if (newVal) {
    // 更新基本屬性
    Object.keys(localFormData).forEach(key => {
      if (key !== 'pipes' && newVal[key] !== undefined &&
          JSON.stringify(newVal[key]) !== JSON.stringify(localFormData[key])) {
        localFormData[key] = newVal[key];
      }
    });

    // 特別處理管路列表
    if (Array.isArray(newVal.pipes) &&
        JSON.stringify(newVal.pipes) !== JSON.stringify(localFormData.pipes)) {
      localFormData.pipes = [...newVal.pipes];
    }
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

.border {
  border: 1px solid rgba(0, 0, 0, 0.12);
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
