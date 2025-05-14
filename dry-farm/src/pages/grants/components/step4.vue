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
          <!-- 田間管路配置區域 -->
          <v-card class="mb-4" variant="outlined">
            <v-card-title class="bg-light-blue-lighten-4 d-flex align-center py-2 px-4">
              <v-icon class="me-2" size="small">mdi-layers-triple-outline</v-icon>
              <span class="text-subtitle-1 font-weight-medium">田間管路配置</span>
            </v-card-title>

            <v-card-text class="pa-4">
              <v-sheet class="pa-3 rounded" color="grey-lighten-5">
                <div class="d-flex flex-wrap align-center mb-4">
                  <!-- 栅塊形狀 -->
                  <div class="d-flex align-center flex-wrap me-4 mb-2">
                    <div class="text-body-2 me-2">坵塊形狀:</div>
                    <v-text-field
                      v-model="localFormData.fieldLength"
                      label="長(m)"
                      variant="outlined"
                      density="comfortable"
                      style="width: 100px"
                      class="me-1"
                      @update:model-value="calculateWidth"
                    />
                    <span class="mx-1">x</span>
                    <v-text-field
                      v-model="localFormData.fieldWidth"
                      label="寬(m)"
                      variant="outlined"
                      density="comfortable"
                      style="width: 100px"
                      class="me-1"
                      readonly
                    />
                  </div>

                  <!-- 施設面積 -->
                  <div class="d-flex align-center me-4 mb-2">
                    <div class="text-body-2 me-2">施設面積:</div>
                    <v-text-field
                      v-model="localFormData.fieldArea"
                      suffix="m²"
                      variant="outlined"
                      density="comfortable"
                      style="width: 120px"
                      readonly
                    />
                  </div>

                  <!-- 自動帶入材料按鈕 -->
                  <v-btn
                    color="success"
                    class="ms-auto mb-2"
                    :loading="isLoadingMaterials"
                    :disabled="!canAutoFillMaterials"
                    @click="autoFillMaterials"
                  >
                    <v-icon start size="small">mdi-autorenew</v-icon>
                    自動帶入材料
                  </v-btn>
                </div>
              </v-sheet>
            </v-card-text>
          </v-card>

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
                mdi-hand-coin
              </v-icon>
              <span class="text-subtitle-1 font-weight-medium">補助來源</span>
            </v-card-title>

            <v-card-text class="pa-4">
              <v-sheet
                class="pa-3 rounded"
                color="grey-lighten-5"
              >
                <v-select
                  v-model="localFormData.fundingSource"
                  :items="fundingSourceOptions"
                  label="補助單位"
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
                    @update:model-value="calculateMainPipeQuantity"
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
                    @update:model-value="fetchPipePrice"
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
                    @update:model-value="fetchPipePrice"
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
                          @update:model-value="calculateBranchPipeQuantity"
                        />
                        <span>M</span>
                      </div>
                    </div>

                    <div class="me-3 mb-2">
                      <div class="text-body-2">噴頭間距(SS)</div>
                      <div class="d-flex align-center">
                        <v-text-field
                          v-model="localFormData.sprinklerSpacing"
                          variant="outlined"
                          density="comfortable"
                          style="width: 80px"
                          class="me-1"
                          @update:model-value="calculateSprinklerQuantity"
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
                    @update:model-value="fetchBranchPipePrice"
                  />

                  <v-select
                    v-model="localFormData.branchPipeMaterial"
                    :items="pipeMaterialOptions"
                    label="材質"
                    variant="outlined"
                    density="comfortable"
                    class="me-2 mb-2"
                    style="width: 120px"
                    @update:model-value="fetchBranchPipePrice"
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

                <div class="d-flex align-center flex-wrap" v-if="showEndFacilityType">
                  <template v-if="localFormData.irrigationType === '穿孔管系統'">
                    <v-select
                      v-model="localFormData.perforatedPipeType"
                      :items="perforatedPipeTypeOptions"
                      label="穿孔管類型"
                      variant="outlined"
                      density="comfortable"
                      class="me-2 mb-2"
                      style="width: 120px"
                      @update:model-value="updateFormData"
                    />
                  </template>

                  <template v-else-if="localFormData.irrigationType === '噴頭式系統'">
                    <v-select
                      v-model="localFormData.sprinklerType"
                      :items="sprinklerTypeOptions"
                      label="噴頭類型"
                      variant="outlined"
                      density="comfortable"
                      class="me-2 mb-2"
                      style="width: 160px"
                      @update:model-value="updateFormData"
                    />
                  </template>

                  <template v-else-if="localFormData.irrigationType === '滴灌系統'">
                    <v-select
                      v-model="localFormData.dripperType"
                      :items="dripperTypeOptions"
                      label="滴頭類型"
                      variant="outlined"
                      density="comfortable"
                      class="me-2 mb-2"
                      style="width: 160px"
                      @update:model-value="updateFormData"
                    />
                  </template>
                </div>

                <div class="d-flex align-center flex-wrap">
                  <v-select
                    v-model="localFormData.endFacilityType"
                    :items="filteredEndFacilityOptions"
                    label="末端設施"
                    variant="outlined"
                    density="comfortable"
                    class="me-2 mb-2"
                    style="width: 180px"
                    @update:model-value="fetchEndFacilityPrice"
                  />

                  <v-select
                    v-model="localFormData.endFacilityDiameter"
                    :items="pipeDiameterOptions"
                    label="管徑(吋)"
                    variant="outlined"
                    density="comfortable"
                    class="me-2 mb-2"
                    style="width: 120px"
                    @update:model-value="fetchEndFacilityPrice"
                  />

                  <v-select
                    v-model="localFormData.endFacilityMaterial"
                    :items="endFacilityMaterialOptions"
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
                    <th class="text-center" style="width: 80px">群組</th>
                    <th>名稱</th>
                    <th>類別</th>
                    <th>規格</th>
                    <th>單位</th>
                    <th>說明</th>
                    <th class="text-center">單價</th>
                    <th class="text-center">數量</th>
                    <th class="text-center">總價</th>
                    <th class="text-center" style="width: 50px">排序</th>
                    <th class="text-center" style="width: 80px">刪除</th>
                  </tr>
                </thead>
                <tbody>
                  <!-- 群組標題 -->
                  <template v-for="(group, groupIndex) in groupedPipes" :key="`group-${groupIndex}`">
                    <tr class="bg-grey-lighten-5">
                      <td colspan="12" class="py-2 px-4 font-weight-bold">
                        {{ groupIndex + 1 }}. {{ group.name }}
                      </td>
                    </tr>

                    <!-- 群組材料 -->
                    <tr v-for="(pipe, pipeIndex) in group.items" :key="`pipe-${groupIndex}-${pipeIndex}`">
                      <td class="text-center">{{ groupIndex + 1 }}-{{ pipeIndex + 1 }}</td>
                      <td class="text-center">{{ pipe.groupId }}</td>
                      <td>{{ pipe.name }}</td>
                      <td>{{ pipe.moduleType }}</td>
                      <td>{{ pipe.specification }}</td>
                      <td>{{ pipe.unit }}</td>
                      <td>{{ pipe.description }}</td>
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
                            :disabled="pipeIndex === 0"
                            @click="movePipeUp(groupIndex, pipeIndex)"
                          >
                            <v-icon size="small">mdi-chevron-up</v-icon>
                          </v-btn>
                          <v-btn
                            icon
                            size="x-small"
                            color="primary"
                            variant="text"
                            :disabled="pipeIndex === group.items.length - 1"
                            @click="movePipeDown(groupIndex, pipeIndex)"
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
                          @click="removePipe(groupIndex, pipeIndex)"
                        >
                          <v-icon>mdi-close</v-icon>
                        </v-btn>
                      </td>
                    </tr>
                  </template>

                  <tr v-if="localFormData.pipes.length === 0">
                    <td colspan="12" class="text-center py-3 text-grey">
                      尚未新增任何管路設施
                    </td>
                  </tr>
                  <tr class="text-muted text-caption bg-grey-lighten-4">
                    <td colspan="9" class="text-right font-weight-bold">合計</td>
                    <td class="text-center font-weight-bold">{{ totalPipesPrice }}</td>
                    <td colspan="2"></td>
                  </tr>
                </tbody>
              </v-table>
            </v-card-text>
          </v-card>

          <!-- 補助計算結果 -->
          <v-card variant="outlined" class="mt-4">
            <v-card-title class="bg-light-blue-lighten-4 d-flex align-center py-2 px-4">
              <v-icon class="me-2" size="small">mdi-calculator</v-icon>
              <span class="text-subtitle-1 font-weight-medium">補助計算結果</span>
            </v-card-title>

            <v-card-text class="pa-4">
              <v-table class="rounded border" style="max-width: 600px">
                <thead class="bg-grey-lighten-3">
                  <tr>
                    <th>項目</th>
                    <th class="text-center">金額(NT$)</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td>總經費</td>
                    <td class="text-center">{{ subsidyTotalAmount }}</td>
                  </tr>
                  <tr>
                    <td>政府補助</td>
                    <td class="text-center text-success font-weight-bold">{{ subsidyAmount }}</td>
                  </tr>
                  <tr>
                    <td>農民自付</td>
                    <td class="text-center text-warning font-weight-bold">{{ farmerSelfAmount }}</td>
                  </tr>
                </tbody>
              </v-table>

              <v-btn
                color="primary"
                class="mt-4"
                :loading="isCalculatingSubsidy"
                @click="calculateSubsidy"
              >
                計算輔助金額
              </v-btn>
            </v-card-text>
          </v-card>
        </v-form>
      </v-card-text>
    </v-card>
  </div>
</template>

<script setup lang="ts">
import { useGrantsStore } from '@/stores/grants';
import { ref, reactive, computed, onMounted, watch } from 'vue';
import axios from 'axios';

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
const stepContent = ref(null);

// 載入與計算狀態
const isLoadingMaterials = ref(false);
const isCalculatingSubsidy = ref(false);

// 本地表單數據
const localFormData = reactive({
  // 栅塊形狀和面積
  fieldLength: '100',
  fieldWidth: '100',
  fieldArea: '10000',

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
  perforatedPipeType: '',  // 穿孔管類型
  sprinklerType: '', // 噴頭類型
  dripperType: '', // 滴灌類型
  endFacilityType: '',
  endFacilityDiameter: '',
  endFacilityMaterial: '',
  endFacilityUnitPrice: '',
  endFacilityQuantity: '',

  // 管路列表 (分群組)
  pipes: [] as Array<{
    groupId: number;
    moduleType: string;
    name: string;
    specification: string;
    unit: string;
    description: string;
    unitPrice: number;
    quantity: number;
    totalPrice: number;
  }>,

  // 補助計算結果
  subsidyTotal: 0,
  subsidyAmount: 0,
  farmerSelfAmount: 0,

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
  '1/2"', '3/4"', '1"', '1-1/4"', '1-1/2"', '2"', '3"', '4"', '5"', '6"', '其他'
];
//
const pipeMaterialOptions = [
  'PVC', 'PE', 'PVCA', 'PVCB', 'PVCE', 'PVCS', 'PVCW', '不鏽鋼', '鐵', '其他'
];

const variantTypeOptions = [
  { value: 1, title: '全長不變徑' },
  { value: 2, title: '1/3管長變徑' }
];

const irrigationTypeOptions = [
  '穿孔管系統',
  '噴頭式系統',
  '微噴系統',
  '滴灌系統',
  '其他'
];

const perforatedPipeTypeOptions = [
  { value: 1, title: '單向' },
  { value: 2, title: '雙向' }
];

const sprinklerTypeOptions = [
  { value: 2, title: '一般' },
  { value: 6, title: '高壓大型噴頭系統' }
];

const dripperTypeOptions = [
  { value: 7, title: '滴嘴滴灌系統' },
  { value: 8, title: '滴水管滴灌系統' }
];

const installationTypeOptions = [
  { value: 1, title: '埋設固定式' },
  { value: 2, title: '地表定置式' },
  { value: 3, title: '附掛棚架式' }
];

const waterSourceOptions = [
  { value: 1, title: '灌溉渠道' },
  { value: 2, title: '野溪' },
  { value: 3, title: '埤(池)塘' },
  { value: 4, title: '地下水' },
  { value: 5, title: '其他' }
];

// 根據灌溉類型篩選末端設施選項
const endFacilityOptions = [
  { value: '穿孔管-單管', irrigationType: '穿孔管系統' },
  { value: '穿孔管-雙管', irrigationType: '穿孔管系統' },
  { value: '噴頭式-單口噴頭', irrigationType: '噴頭式系統' },
  { value: '噴頭式-雙口噴頭', irrigationType: '噴頭式系統' },
  { value: '微噴-單向微噴霧', irrigationType: '微噴系統' },
  { value: '微噴-雙向微噴霧', irrigationType: '微噴系統' },
  { value: '滴灌-滴嘴', irrigationType: '滴灌系統' },
  { value: '滴灌-滴水管', irrigationType: '滴灌系統' }
];

const endFacilityMaterialOptions = [
  '塑膠', '塑鋼', '不鏽鋼', '金屬', '其他'
];

// 根據灌溉類型篩選末端設施選項
const filteredEndFacilityOptions = computed(() => {
  if (!localFormData.irrigationType) return [];
  return endFacilityOptions
    .filter(option => option.irrigationType === localFormData.irrigationType)
    .map(option => option.value);
});

// 是否顯示末端設施類型選擇
const showEndFacilityType = computed(() => {
  return ['穿孔管系統', '噴頭式系統', '滴灌系統'].includes(localFormData.irrigationType);
});

// 計算屬性
const mainPipeTotalPrice = computed(() => {
  const length = parseFloat(localFormData.mainPipeLength) || 0;
  const unitPrice = parseFloat(localFormData.mainPipeUnitPrice) || 0;
  const quantity = parseFloat(localFormData.mainPipeQuantity) || 0;
  return Math.round(length * unitPrice * quantity).toString();
});

const branchPipeTotalPrice = computed(() => {
  const length = parseFloat(localFormData.branchPipeLength) || 0;
  const unitPrice = parseFloat(localFormData.branchPipeUnitPrice) || 0;
  const quantity = parseFloat(localFormData.branchPipeQuantity) || 0;
  return Math.round(length * unitPrice * quantity).toString();
});

const endFacilityTotalPrice = computed(() => {
  const unitPrice = parseFloat(localFormData.endFacilityUnitPrice) || 0;
  const quantity = parseFloat(localFormData.endFacilityQuantity) || 0;
  return Math.round(unitPrice * quantity).toString();
});

// 將管路按群組分類
const groupedPipes = computed(() => {
  const groups = {};

  // 找出所有群組ID
  const groupIds = [...new Set(localFormData.pipes.map(pipe => pipe.groupId))];

  // 定義群組名稱
  const groupNames = {
    1: '主管配件',
    2: '支管配件',
    3: '末端設施',
    4: '閥件',
    5: '集水槽',
    6: '控制系統',
    7: '雜項',
  };

  // 為每個群組建立條目
  groupIds.forEach(groupId => {
    const items = localFormData.pipes.filter(pipe => pipe.groupId === groupId);
    if (items.length > 0) {
      groups[groupId] = {
        id: groupId,
        name: groupNames[groupId] || `群組 ${groupId}`,
        items: items
      };
    }
  });

  // 返回排序後的群組陣列
  return Object.values(groups).sort((a, b) => a.id - b.id);
});

const totalPipesPrice = computed(() => {
  const total = localFormData.pipes.reduce((sum, pipe) => sum + (pipe.totalPrice || 0), 0);
  return total.toLocaleString();
});

// 補助結果
const subsidyTotalAmount = computed(() => {
  return localFormData.subsidyTotal.toLocaleString();
});

const subsidyAmount = computed(() => {
  return localFormData.subsidyAmount.toLocaleString();
});

const farmerSelfAmount = computed(() => {
  return localFormData.farmerSelfAmount.toLocaleString();
});

// 驗證條件
const canAutoFillMaterials = computed(() => {
  return (
    !!localFormData.fieldLength &&
    !!localFormData.fieldWidth &&
    !!localFormData.fundingSource &&
    !!localFormData.irrigationType &&
    !!localFormData.installationType &&
    !!localFormData.mainPipeLength &&
    !!localFormData.mainPipeMaterial &&
    !!localFormData.branchPipeSpacing &&
    !!localFormData.sprinklerSpacing
  );
});

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
// 計算寬度（基於長度和面積）
const calculateWidth = () => {
  const length = parseFloat(localFormData.fieldLength) || 0;
  const area = parseFloat(localFormData.fieldArea) || 0;

  if (length > 0 && area > 0) {
    localFormData.fieldWidth = Math.round(area / length).toString();
  }

  updateFormData();
};

// 計算主管數量（根據長度）
const calculateMainPipeQuantity = () => {
  const length = parseFloat(localFormData.mainPipeLength) || 0;
  if (length > 0) {
    // 每支管長通常為4公尺，數量為向上取整的長度除以4
    localFormData.mainPipeQuantity = Math.ceil(length / 4).toString();
  }
  updateFormData();
};

// 計算支管數量
const calculateBranchPipeQuantity = () => {
  const fieldLength = parseFloat(localFormData.fieldLength) || 0;
  const branchPipeSpacing = parseFloat(localFormData.branchPipeSpacing) || 0;

  if (fieldLength > 0 && branchPipeSpacing > 0) {
    // 支管數量為場地長度除以支管間距，向上取整
    const quantity = Math.ceil(fieldLength / branchPipeSpacing);
    localFormData.branchPipeQuantity = quantity.toString();
  }

  updateFormData();
};

// 計算噴頭數量
const calculateSprinklerQuantity = () => {
  const fieldLength = parseFloat(localFormData.fieldLength) || 0;
  const fieldWidth = parseFloat(localFormData.fieldWidth) || 0;
  const branchPipeSpacing = parseFloat(localFormData.branchPipeSpacing) || 0;
  const sprinklerSpacing = parseFloat(localFormData.sprinklerSpacing) || 0;

  if (fieldLength > 0 && fieldWidth > 0 && branchPipeSpacing > 0 && sprinklerSpacing > 0) {
    // 支管數量 = 場地長度 / 支管間距
    const branchPipes = Math.ceil(fieldLength / branchPipeSpacing);

    // 每個支管上的噴頭數量 = 場地寬度 / 噴頭間距
    const sprinklersPerBranch = Math.ceil(fieldWidth / sprinklerSpacing);

    // 總噴頭數量 = 支管數量 * 每個支管上的噴頭數量
    const totalSprinklers = branchPipes * sprinklersPerBranch;

    if (localFormData.irrigationType === '噴頭式系統' ||
        localFormData.irrigationType === '微噴系統' ||
        localFormData.irrigationType === '滴灌系統') {
      localFormData.endFacilityQuantity = totalSprinklers.toString();
    }
  }

  updateFormData();
};

// 灌溉類型變更
const onIrrigationTypeChange = () => {
  // 重置末端設施相關欄位
  localFormData.endFacilityType = '';
  localFormData.perforatedPipeType = '';
  localFormData.sprinklerType = '';
  localFormData.dripperType = '';

  // 根據灌溉類型設置默認值
  if (localFormData.irrigationType === '穿孔管系統') {
    localFormData.perforatedPipeType = perforatedPipeTypeOptions[0].value;
  } else if (localFormData.irrigationType === '噴頭式系統') {
    localFormData.sprinklerType = sprinklerTypeOptions[0].value;
  } else if (localFormData.irrigationType === '滴灌系統') {
    localFormData.dripperType = dripperTypeOptions[0].value;
  }

  updateFormData();
};

// 設施類型變更
const onInstallationTypeChange = () => {
  updateFormData();
};

// 獲取管路價格
const fetchPipePrice = async () => {
  if (!localFormData.mainPipeMaterial || !localFormData.mainPipeDiameter) return;

  try {
    // 模擬API調用獲取價格
    // 實際應用中應替換為真實的API調用
    console.log('Fetching pipe price for:', localFormData.mainPipeMaterial, localFormData.mainPipeDiameter);

    // 模擬延遲
    await new Promise(resolve => setTimeout(resolve, 300));

    // 模擬價格
    const price = Math.floor(Math.random() * 100) + 50;
    localFormData.mainPipeUnitPrice = price.toString();

    updateFormData();
  } catch (error) {
    console.error('Error fetching pipe price:', error);
  }
};

// 獲取支管價格
const fetchBranchPipePrice = async () => {
  if (!localFormData.branchPipeMaterial || !localFormData.branchPipeDiameter) return;

  try {
    // 模擬API調用獲取價格
    console.log('Fetching branch pipe price for:', localFormData.branchPipeMaterial, localFormData.branchPipeDiameter);

    // 模擬延遲
    await new Promise(resolve => setTimeout(resolve, 300));

    // 模擬價格
    const price = Math.floor(Math.random() * 80) + 40;
    localFormData.branchPipeUnitPrice = price.toString();

    updateFormData();
  } catch (error) {
    console.error('Error fetching branch pipe price:', error);
  }
};

// 獲取末端設施價格
const fetchEndFacilityPrice = async () => {
  if (!localFormData.endFacilityType || !localFormData.endFacilityDiameter) return;

  try {
    // 模擬API調用獲取價格
    console.log('Fetching end facility price for:', localFormData.endFacilityType, localFormData.endFacilityDiameter);

    // 模擬延遲
    await new Promise(resolve => setTimeout(resolve, 300));

    // 模擬價格
    const price = Math.floor(Math.random() * 60) + 30;
    localFormData.endFacilityUnitPrice = price.toString();

    updateFormData();
  } catch (error) {
    console.error('Error fetching end facility price:', error);
  }
};

// 添加主管
const addMainPipe = () => {
  if (canAddMainPipe.value) {
    const length = parseFloat(localFormData.mainPipeLength);
    const unitPrice = parseFloat(localFormData.mainPipeUnitPrice);
    const quantity = parseFloat(localFormData.mainPipeQuantity);

    localFormData.pipes.push({
      groupId: 1, // 主管配件組
      moduleType: '主管',
      name: `${localFormData.mainPipeMaterial} ${localFormData.mainPipeDiameter}`,
      specification: `${localFormData.mainPipeDiameter}`,
      unit: '支',
      description: `主管管線(${localFormData.mainPipeMaterial})`,
      unitPrice: unitPrice,
      quantity: quantity,
      totalPrice: Math.round(unitPrice * quantity)
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
      groupId: 2, // 支管配件組
      moduleType: '支管',
      name: `${localFormData.branchPipeMaterial} ${localFormData.branchPipeDiameter}`,
      specification: `${localFormData.branchPipeDiameter}`,
      unit: '支',
      description: `支管管線(${localFormData.branchPipeMaterial})`,
      unitPrice: unitPrice,
      quantity: quantity,
      totalPrice: Math.round(unitPrice * quantity)
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
      groupId: 3, // 末端設施組
      moduleType: '末端設施',
      name: localFormData.endFacilityType,
      specification: `${localFormData.endFacilityDiameter}`,
      unit: '個',
      description: `${localFormData.endFacilityType}(${localFormData.endFacilityMaterial})`,
      unitPrice: unitPrice,
      quantity: quantity,
      totalPrice: Math.round(unitPrice * quantity)
    });

    // 保留部分欄位，清空其他欄位
    const fundingSource = localFormData.fundingSource;
    const irrigationType = localFormData.irrigationType;
    const installationType = localFormData.installationType;
    const waterSource = localFormData.waterSource;
    const perforatedPipeType = localFormData.perforatedPipeType;
    const sprinklerType = localFormData.sprinklerType;
    const dripperType = localFormData.dripperType;

    localFormData.endFacilityType = '';
    localFormData.endFacilityDiameter = '';
    localFormData.endFacilityMaterial = '';
    localFormData.endFacilityUnitPrice = '';
    localFormData.endFacilityQuantity = '';

    localFormData.fundingSource = fundingSource;
    localFormData.irrigationType = irrigationType;
    localFormData.installationType = installationType;
    localFormData.waterSource = waterSource;
    localFormData.perforatedPipeType = perforatedPipeType;
    localFormData.sprinklerType = sprinklerType;
    localFormData.dripperType = dripperType;

    updateFormData();
  }
};

// 移除管路
const removePipe = (groupIndex, pipeIndex) => {
  const group = groupedPipes.value[groupIndex];
  const pipe = group.items[pipeIndex];

  // 找到在原數組中的索引
  const originalIndex = localFormData.pipes.findIndex(p =>
    p.groupId === pipe.groupId &&
    p.name === pipe.name &&
    p.specification === pipe.specification &&
    p.unitPrice === pipe.unitPrice &&
    p.quantity === pipe.quantity);

  if (originalIndex >= 0) {
    localFormData.pipes.splice(originalIndex, 1);
    updateFormData();
  }
};

// 上移管路順序
const movePipeUp = (groupIndex, pipeIndex) => {
  if (pipeIndex <= 0) return;

  const group = groupedPipes.value[groupIndex];
  const pipe1 = group.items[pipeIndex];
  const pipe2 = group.items[pipeIndex - 1];

  // 找到在原數組中的索引
  const index1 = localFormData.pipes.findIndex(p =>
    p.groupId === pipe1.groupId &&
    p.name === pipe1.name &&
    p.specification === pipe1.specification &&
    p.unitPrice === pipe1.unitPrice &&
    p.quantity === pipe1.quantity);

  const index2 = localFormData.pipes.findIndex(p =>
    p.groupId === pipe2.groupId &&
    p.name === pipe2.name &&
    p.specification === pipe2.specification &&
    p.unitPrice === pipe2.unitPrice &&
    p.quantity === pipe2.quantity);

  if (index1 >= 0 && index2 >= 0) {
    // 交換元素
    const temp = localFormData.pipes[index1];
    localFormData.pipes[index1] = localFormData.pipes[index2];
    localFormData.pipes[index2] = temp;
    updateFormData();
  }
};

// 下移管路順序
const movePipeDown = (groupIndex, pipeIndex) => {
  const group = groupedPipes.value[groupIndex];
  if (pipeIndex >= group.items.length - 1) return;

  const pipe1 = group.items[pipeIndex];
  const pipe2 = group.items[pipeIndex + 1];

  // 找到在原數組中的索引
  const index1 = localFormData.pipes.findIndex(p =>
    p.groupId === pipe1.groupId &&
    p.name === pipe1.name &&
    p.specification === pipe1.specification &&
    p.unitPrice === pipe1.unitPrice &&
    p.quantity === pipe1.quantity);

  const index2 = localFormData.pipes.findIndex(p =>
    p.groupId === pipe2.groupId &&
    p.name === pipe2.name &&
    p.specification === pipe2.specification &&
    p.unitPrice === pipe2.unitPrice &&
    p.quantity === pipe2.quantity);

  if (index1 >= 0 && index2 >= 0) {
    // 交換元素
    const temp = localFormData.pipes[index1];
    localFormData.pipes[index1] = localFormData.pipes[index2];
    localFormData.pipes[index2] = temp;
    updateFormData();
  }
};

// 自動帶入材料
const autoFillMaterials = async () => {
  if (!canAutoFillMaterials.value) {
    console.error('Not all required fields filled for auto-filling materials');
    return;
  }

  isLoadingMaterials.value = true;

  try {
    // 構建請求數據
    const requestData = {
      // 栅塊數據
      Length: parseInt(localFormData.fieldLength),
      width: parseInt(localFormData.fieldWidth),

      // 主管數據
      L1Len: parseFloat(localFormData.mainPipeLength),
      L1Material: parseInt(getMatTypeId(localFormData.mainPipeMaterial)),
      L1Spec: parseInt(getSpecId(localFormData.mainPipeDiameter)),
      L1Price: parseFloat(localFormData.mainPipeUnitPrice) || 0,
      L1MatAmt: parseInt(localFormData.mainPipeQuantity) || 0,

      // 支管數據
      L2Len: 0,
      L2Material: 1,
      L2Spec: 1,
      L2Price: 0,
      L2MatAmt: 0,

      // 灌溉系統數據
      ddl_EndType: getEndTypeId(localFormData.irrigationType),
      ddl_Sprinkler: localFormData.sprinklerType || 2,
      ddl_Drop: localFormData.dripperType || 7,
      ddl_Perforated: localFormData.perforatedPipeType || 1,

      // 設施類型
      ddl_FacType: localFormData.installationType || 1,

      // 灌溉水源
      ddl_WtaerSrc: localFormData.waterSource || 1,

      // 支管與噴頭間距
      SL: parseFloat(localFormData.branchPipeSpacing) || 0,
      SS: parseFloat(localFormData.sprinklerSpacing) || 0,

      // 支管材質與規格
      BranchMaterial: parseInt(getMatTypeId(localFormData.branchPipeMaterial)) || 1,
      BranchSpec: parseInt(getSpecId(localFormData.branchPipeDiameter)) || 1,

      // 變徑規格
      ChangeBranchSpec: localFormData.variantType || 1,

      // 豎管高度
      StdpipeHei: parseFloat(localFormData.riserHeight) || 1,

      // 其他需要的參數
      StdpipeSpec: 1,
      StdpipeMat: 1,
      NozzleMaterial: 1,
      NozzleSpec: 1
    };

    console.log('Auto-filling materials with data:', requestData);

    // 模擬API調用（實際使用中替換為真實的API調用）
    // const response = await axios.post('../FarmerSys/GetStdSysByConditionAddGroup', requestData);

    // 模擬延遲
    await new Promise(resolve => setTimeout(resolve, 1500));

    // 模擬API響應數據
    const mockResponse = {
      data: getMockMaterialData()
    };

    // 處理響應數據
    const materialGroups = mockResponse.data;

    // 清空當前管路列表
    localFormData.pipes = [];

    // 添加新的材料列表
    materialGroups.forEach(group => {
      group.List.forEach(material => {
        localFormData.pipes.push({
          groupId: group.GroupNo,
          moduleType: material.module,
          name: material.matname,
          specification: `${material.spec1} ${material.spec2} ${material.spec3}`.trim(),
          unit: material.itemunit,
          description: material.description,
          unitPrice: material.matprice,
          quantity: material.matamount,
          totalPrice: Math.round(material.matprice * material.matamount)
        });
      });
    });

    // 計算輔助金額
    calculateSubsidy();
  } catch (error) {
    console.error('Error auto-filling materials:', error);
  } finally {
    isLoadingMaterials.value = false;
  }
};

// 計算補助金額
const calculateSubsidy = async () => {
  isCalculatingSubsidy.value = true;

  try {
    // 構建請求數據
    const requestData = {
      // 補助來源
      Unit: getFundingSourceId(localFormData.fundingSource),

      // 栅塊形狀
      Block: `${localFormData.fieldLength}x${localFormData.fieldWidth}`,

      // 灌溉系統數據
      EndTypeDataAry: [{
        Endtype: getEndTypeId(localFormData.irrigationType),
        Fac: parseInt(localFormData.installationType) || 1,
        SS: parseFloat(localFormData.sprinklerSpacing) || 0,
        SL: parseFloat(localFormData.branchPipeSpacing) || 0,
        BranchPipeMaterial: localFormData.branchPipeMaterial,
        BranchPipeSpec: parseInt(getSpecId(localFormData.branchPipeDiameter)) || 1,
        StdpipeHei: parseFloat(localFormData.riserHeight) || 0,
        NozzleSpec: 1,
        NozzleType: '',
        StdpipeMat: '',
        StdpipeSpec: 1,
        PerforatedPipe: parseInt(localFormData.perforatedPipeType) || 1
      }],

      // 灌溉水源
      IrrWCode: parseInt(localFormData.waterSource) || 1,

      // 主管數據
      MainJsonDataAry: [{
        Length: parseFloat(localFormData.mainPipeLength) || 0,
        Mat: localFormData.mainPipeMaterial,
        Spec: parseInt(getSpecId(localFormData.mainPipeDiameter)) || 1,
        LPrice: parseFloat(localFormData.mainPipeUnitPrice) || 0,
        Amount: parseInt(localFormData.mainPipeQuantity) || 0
      }],

      // 材料清單數據
      PriceJsonDataAry: localFormData.pipes.map(pipe => ({
        POMNo: getPOMNo(pipe.moduleType, pipe.name),
        Group: pipe.groupId,
        Order: 1,
        Amt: pipe.quantity,
        Price: pipe.unitPrice,
        TotalPrice: pipe.totalPrice
      })),

      // 總價格
      TotalPrice: getTotalPrice()
    };

    console.log('Calculating subsidy with data:', requestData);

    // 模擬API調用（實際使用中替換為真實的API調用）
    // const response = await axios.post('../FarmerSys/GetTotalPrice', requestData);

    // 模擬延遲
    await new Promise(resolve => setTimeout(resolve, 1000));

    // 模擬API響應數據（format: "總價;補助金額;自付金額"）
    const mockResponse = {
      data: `${getTotalPrice()};${Math.round(getTotalPrice() * 0.6)};${Math.round(getTotalPrice() * 0.4)}`
    };

    // 處理響應數據
    const priceData = mockResponse.data.split(';');
    localFormData.subsidyTotal = parseInt(priceData[0]) || 0;
    localFormData.subsidyAmount = parseInt(priceData[1]) || 0;
    localFormData.farmerSelfAmount = parseInt(priceData[2]) || 0;

    updateFormData();
  } catch (error) {
    console.error('Error calculating subsidy:', error);
  } finally {
    isCalculatingSubsidy.value = false;
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

// 實用函數
// 取得材質類型ID
const getMatTypeId = (materialName) => {
  const materialMap = {
    'PVC': 1,
    'PE': 2,
    'PVCA': 3,
    'PVCB': 4,
    'PVCE': 5,
    'PVCS': 6,
    'PVCW': 7,
    '不鏽鋼': 8,
    '鐵': 9,
    '其他': 10
  };
  return materialMap[materialName] || 1;
};

// 取得規格ID
const getSpecId = (diameter) => {
  const specMap = {
    '1/2"': 1,
    '3/4"': 2,
    '1"': 3,
    '1-1/4"': 4,
    '1-1/2"': 5,
    '2"': 6,
    '3"': 7,
    '4"': 8,
    '5"': 9,
    '6"': 10,
    '其他': 11
  };
  return specMap[diameter] || 1;
};

// 取得末端設施類型ID
const getEndTypeId = (irrigationType) => {
  const typeMap = {
    '穿孔管系統': 1,
    '噴頭式系統': 2,
    '微噴系統': 3,
    '滴灌系統': 4,
    '其他': 5
  };
  return typeMap[irrigationType] || 1;
};

// 取得補助來源ID
const getFundingSourceId = (fundingSource) => {
  const sourceMap = {
    '農田水利署': 0,
    '七星管理處作業基金': 16,
    '瑠公管理處作業基金': 17
  };
  return sourceMap[fundingSource] || 0;
};

// 模擬取得物料編號
const getPOMNo = (moduleType, name) => {
  // 實際應用中，這裡應該使用真實的物料編號邏輯
  // 這裡僅返回一個隨機模擬編號
  return Math.floor(Math.random() * 10000) + 10000;
};

// 獲取總價格
const getTotalPrice = () => {
  return localFormData.pipes.reduce((sum, pipe) => sum + pipe.totalPrice, 0);
};

// 獲取模擬材料數據
const getMockMaterialData = () => {
  // 模擬按群組返回材料數據
  return [
    {
      GroupNo: 1,
      GroupName: '主管配件',
      List: [
        {
          module: '主管',
          matname: `${localFormData.mainPipeMaterial} ${localFormData.mainPipeDiameter} 管`,
          spec1: localFormData.mainPipeDiameter,
          spec2: '',
          spec3: '',
          itemunit: '支',
          matprice: parseFloat(localFormData.mainPipeUnitPrice) || 60,
          matamount: parseInt(localFormData.mainPipeQuantity) || 10,
          description: '主管管線'
        },
        {
          module: '主管',
          matname: '配件-閥門',
          spec1: localFormData.mainPipeDiameter,
          spec2: '',
          spec3: '',
          itemunit: '個',
          matprice: 180,
          matamount: 2,
          description: '控制閥門'
        }
      ]
    },
    {
      GroupNo: 2,
      GroupName: '支管配件',
      List: [
        {
          module: '支管',
          matname: 'PVC 3/4" 管',
          spec1: '3/4"',
          spec2: '',
          spec3: '',
          itemunit: '支',
          matprice: 40,
          matamount: Math.ceil(parseFloat(localFormData.fieldLength) / (parseFloat(localFormData.branchPipeSpacing) || 5)),
          description: '支管管線'
        },
        {
          module: '支管',
          matname: '配件-T型接頭',
          spec1: '3/4"',
          spec2: '',
          spec3: '',
          itemunit: '個',
          matprice: 25,
          matamount: Math.ceil(parseFloat(localFormData.fieldLength) / (parseFloat(localFormData.branchPipeSpacing) || 5)),
          description: 'T型連接器'
        }
      ]
    },
    {
      GroupNo: 3,
      GroupName: '末端設施',
      List: [
        {
          module: '末端設施',
          matname: localFormData.irrigationType === '滴灌系統' ? '滴嘴' :
                   localFormData.irrigationType === '噴頭式系統' ? '噴頭' :
                   localFormData.irrigationType === '穿孔管系統' ? '穿孔管' : '噴頭',
          spec1: '1/2"',
          spec2: '',
          spec3: '',
          itemunit: '個',
          matprice: 35,
          matamount: localFormData.sprinklerSpacing && localFormData.branchPipeSpacing ?
                     Math.ceil(parseFloat(localFormData.fieldLength) / parseFloat(localFormData.branchPipeSpacing)) *
                     Math.ceil(parseFloat(localFormData.fieldWidth) / parseFloat(localFormData.sprinklerSpacing)) : 20,
          description: '用於灌溉的末端裝置'
        }
      ]
    },
    {
      GroupNo: 4,
      GroupName: '閥件',
      List: [
        {
          module: '閥件',
          matname: '球閥',
          spec1: '1"',
          spec2: '',
          spec3: '',
          itemunit: '個',
          matprice: 120,
          matamount: 2,
          description: '用於控制水流的球閥'
        }
      ]
    },
    {
      GroupNo: 7,
      GroupName: '雜項',
      List: [
        {
          module: '雜項',
          matname: '快速接頭',
          spec1: '1"',
          spec2: '',
          spec3: '',
          itemunit: '個',
          matprice: 45,
          matamount: 4,
          description: '用於快速連接水管的接頭'
        },
        {
          module: '雜項',
          matname: '預備費',
          spec1: '',
          spec2: '',
          spec3: '',
          itemunit: '式',
          matprice: Math.round(getTotalPrice() * 0.02),
          matamount: 1,
          description: '預備費用約2%'
        }
      ]
    }
  ];
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

  // 如果沒有設置面積，根據長寬計算
  if (!localFormData.fieldArea && localFormData.fieldLength && localFormData.fieldWidth) {
    localFormData.fieldArea = (parseFloat(localFormData.fieldLength) * parseFloat(localFormData.fieldWidth)).toString();
  }

  // 如果管路列表為空，添加示例數據
  if (!localFormData.pipes || localFormData.pipes.length === 0) {
    localFormData.pipes = [
      {
        groupId: 1,
        moduleType: '主管',
        name: 'PVC 1"',
        specification: '1"',
        unit: '支',
        description: '主管管線(PVC)',
        unitPrice: 44,
        quantity: 2,
        totalPrice: 88
      },
      {
        groupId: 2,
        moduleType: '支管',
        name: 'PVC 3/4"',
        specification: '3/4"',
        unit: '支',
        description: '支管管線(PVC)',
        unitPrice: 38,
        quantity: 8,
        totalPrice: 304
      },
      {
        groupId: 3,
        moduleType: '末端設施',
        name: '單口噴頭',
        specification: '1/2"',
        unit: '個',
        description: '噴頭-塑膠',
        unitPrice: 25,
        quantity: 16,
        totalPrice: 400
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
