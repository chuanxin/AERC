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
                    label="縣市"
                    variant="outlined"
                    density="comfortable"
                    :rules="[v => !!v || '請選擇縣市']"
                    @update:model-value="onCountyChange"
                  />
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
                  />
                </v-col>
                <v-col cols="12" md="4">
                  <v-select
                    v-model="localFormData.addressVillage"
                    :items="villages"
                    label="地段"
                    variant="outlined"
                    density="comfortable"
                    :disabled="!localFormData.addressTown"
                  />
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
                <v-col cols="12" md="4" class="d-flex align-center">
                  <v-text-field
                    v-model="localFormData.landNumberMain"
                    label="地號"
                    variant="outlined"
                    density="comfortable"
                    class="me-1"
                    type="number"
                    style="width: 70px"
                    :rules="[
                      v => !!v || '請輸入主地號',
                      // v => (parseInt(v) >= 900 && parseInt(v) < 1000) || '此地段主地號需在 900 以上 1000 以下'
                    ]"
                  />
                  <v-icon class="me-1">mdi-minus</v-icon>
                  <v-text-field
                    v-model="localFormData.landNumberSub"
                    variant="outlined"
                    density="comfortable"
                    type="number"
                    style="width: 60px"
                  />
                </v-col>
                <v-col cols="12" md="8" class="d-flex align-center">
                  <v-btn
                    color="secondary"
                    variant="tonal"
                    class="me-2"
                    @click="showLandInfoDialog"
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
                  />
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
                    />
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
                    />
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
            rounded="pill"
            @click="goToPreviousStep"
          >
            <v-icon start>mdi-arrow-left</v-icon>
            上一步
          </v-btn>

          <!-- <div class="text-caption d-none d-sm-block text-grey"> 步驟 {{ currentStep }}/8 </div> -->

          <v-btn
            color="green-darken-1"
            :disabled="!isValid"
            size="large"
            rounded="pill"
            @click="goToNextStep"
          >
            {{ currentStep === 8 ? '完成' : '下一步' }}
            <v-icon end v-if="currentStep < 8">mdi-arrow-right</v-icon>
            <v-icon end v-else>mdi-check</v-icon>
          </v-btn>
        </div>
      </div>
    </v-card>

    <v-dialog v-model="landInfoDialog" max-width="700px">
      <v-card>
        <v-card-title class="bg-light-blue-lighten-4 d-flex align-center py-2 px-4">
          <v-icon class="me-2" size="small">mdi-map-marker</v-icon>
          <span class="text-subtitle-1 font-weight-medium">土地資訊</span>
        </v-card-title>

        <v-card-text class="pa-4">
          <div class="map-container mb-4">
            <div ref="mapElement" style="height: 300px; width: 100%;" class="rounded border"></div>
            <!-- Feature info popup -->
            <v-card v-if="featureInfoVisible" class="feature-info-card pa-2" elevation="4">
              <v-card-title class="text-body-1 py-1 px-2">地段資訊</v-card-title>
              <v-divider></v-divider>
              <v-card-text class="px-2 py-1">
                <div v-if="selectedFeatureInfo.Land_no">
                  <strong>地號:</strong> {{ selectedFeatureInfo.Land_no }}
                </div>
                <div v-if="selectedFeatureInfo.section">
                  <strong>地段:</strong> {{ selectedFeatureInfo.section }}
                </div>
                <div v-if="selectedFeatureInfo.area">
                  <strong>面積:</strong> {{ selectedFeatureInfo.area }} 平方公尺
                </div>
                <div class="mt-2">
                  <v-btn density="compact" color="info" size="small" @click="useSelectedFeature">
                    使用此地號
                  </v-btn>
                  <v-btn density="compact" variant="text" size="small" @click="hideFeatureInfo">
                    關閉
                  </v-btn>
                </div>
              </v-card-text>
            </v-card>
          </div>
          <v-table density="comfortable" class="border rounded mb-4">
            <tbody>
              <tr>
                <td class="bg-grey-lighten-4 font-weight-medium" width="15%">補助資訊</td>
                <td>{{ landInfo.subsidyInfo }}</td>
                <td class="bg-grey-lighten-4 font-weight-medium" width="15%">縣市</td>
                <td>{{ landInfo.county }}</td>
              </tr>
              <tr>
                <td class="bg-grey-lighten-4 font-weight-medium">地段</td>
                <td>{{ landInfo.section }}</td>
                <td class="bg-grey-lighten-4 font-weight-medium">地號</td>
                <td>{{ localFormData.landNumberMain }}<v-icon>mdi-minus</v-icon>{{ localFormData.landNumberSub }}</td>
              </tr>
              <tr>
                <td class="bg-grey-lighten-4 font-weight-medium">管理處</td>
                <td>{{ landInfo.managementOffice }}</td>
                <td class="bg-grey-lighten-4 font-weight-medium">工作站</td>
                <td>{{ landInfo.workstation }}</td>
              </tr>
              <tr>
                <td class="bg-grey-lighten-4 font-weight-medium">水利小組</td>
                <td>{{ landInfo.waterResourceGroup }}</td>
                <td class="bg-grey-lighten-4 font-weight-medium">特殊地</td>
                <td>{{ landInfo.specialLand ? '是' : '否' }}</td>
              </tr>
            </tbody>
          </v-table>

          <!-- <div class="d-flex justify-end">
            <v-btn color="primary" variant="tonal" @click="useLandInfo">
              使用此筆資料
            </v-btn>
            <v-btn color="grey" class="ms-2" variant="outlined" @click="landInfoDialog = false">
              關閉
            </v-btn>
          </div> -->
        </v-card-text>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup lang="ts">
// Import OpenLayers dependencies - add these at the top of your script
import 'ol/ol.css'; // Make sure to install the 'ol' package
import Map from 'ol/Map';
import View from 'ol/View';
import TileLayer from 'ol/layer/Tile';
import OSM from 'ol/source/OSM';
import { fromLonLat, transform } from 'ol/proj';
import Feature from 'ol/Feature';
import Point from 'ol/geom/Point';
import { Vector as VectorLayer } from 'ol/layer';
import { Vector as VectorSource } from 'ol/source';
import { Style, Icon, Stroke, Fill } from 'ol/style';
import GeoJSON from 'ol/format/GeoJSON';
import { Select, Modify } from 'ol/interaction';
import { click } from 'ol/events/condition';
import { unByKey } from 'ol/Observable';
import { getArea } from 'ol/sphere';

// Reference to map element and map instance
const mapElement = ref(null);
let map: any = null;

const localValid = ref(false);
const form = ref(null);

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

// Emit events
const emit = defineEmits(['update:formData', 'validated', 'go-back']);

// Define isValid for the navigation button - changed to a computed property v2
const isValid = computed(() => {
  // For demo purposes, always allow navigation
  return true;
});

// Step indicator colors
const getStepColor = (step: number) => {
  if (step < props.currentStep) return 'success'; // completed
  if (step === props.currentStep) return 'primary'; // current
  return 'grey'; // not started
};

// // Navigate to next step v1
// const goToNextStep = async () => {
//   const { valid } = await validate();
//   if (!valid) return;

//   console.log('Emitting validated event for step 2');
//   emit('validated', { valid: true, step: 2 });
// };

// Navigate to next step - simplified for localStorage demo
const goToNextStep = async () => {
  // For demo, no validation needed, simply emit the event
  // Update form data before navigation
  updateFormData();

  console.log('Emitting validated event for step 2');
  emit('validated', { valid: true, step: 2 });
};

// // Go back to previous step v1
// const goToPreviousStep = () => {
//   console.log('Going back from step 2');
//   emit('go-back');
// };

// Go back to previous step - simplified for localStorage demo
const goToPreviousStep = () => {
  // Update form data before going back
  updateFormData();

  console.log('Going back from step 2');
  emit('go-back');
};

// // 本地表單數據 v1
// const localFormData = reactive({
//   // 設施地址區塊
//   addressCounty: '',
//   addressTown: '',
//   addressVillage: '',
//   landNumber: '',
//   isAboriginalArea: false,
//   isIrrigationArea: false,
//   isReapplied: false,
//   longitude: '',
//   latitude: '',
//   landArea: '',
//   landAreaHa: '',
//   facilityArea: '',
//   facilityAreaHa: '',
//   cropCategory: '',
//   cropName: '',
//   crops: [] as Array<{category: string, name: string}>,
//   landData: [],
//   valid: false,

//   // 所有權人資料區塊
//   ownerName: '',
//   ownerId: '',
//   ownerCounty: '',
//   ownerTown: '',
//   ownerVillage: '',
//   ownerShare1: '',
//   ownerShare2: '',
//   ownerArea: '',
//   owners: [] as Array<{
//     name: string,
//     id: string,
//     address: string,
//     share: string,
//     area: string
//   }>
// });

// Local form data - keep existing structure v2
const localFormData = reactive({
  // Facility address section
  addressCounty: '',
  addressTown: '',
  addressVillage: '',
  landNumber: '',
  landNumberMain: '',
  landNumberSub: '',
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
  landData: [],
  valid: true, // Changed to default true for demo

  // Owner data section
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
    '竹崎鄉': ['龍山村', '灣橋村', '瓦厝埔段', '內埔子段'],
    // 其他鄉鎮村里
  }
});

const landInfoDialog = ref(false);
const landInfo = reactive({
  subsidyInfo: '符合補助資格',
  county: '嘉義縣',
  section: '瓦厝埔段',
  number: '996-1',
  managementOffice: '瑠公管理處',
  workstation: '嘉義工作站',
  waterResourceGroup: '第三水利小組',
  specialLand: false
});

// Function to show the land info dialog
const showLandInfoDialog = () => {
  // Update land info with current form data
  if (localFormData.landNumberMain) {
    // Format the land number with or without the sub number
    landInfo.number = localFormData.landNumberSub
      ? `${localFormData.landNumberMain}-${localFormData.landNumberSub}`
      : localFormData.landNumberMain;
  }
  // If there's a county selected, use it for the dialog
  if (localFormData.addressCounty) {
    landInfo.county = localFormData.addressCounty;
  }
  // If there's a village selected, use it for the dialog
  if (localFormData.addressVillage) {
    landInfo.section = localFormData.addressVillage;
  }

  landInfoDialog.value = true;
  // Allow time for the dialog to open and map to initialize
  nextTick(() => {
    // This will be called after the map is initialized through the watcher
    // The map initialization will trigger the feature search
  });
};

const findAndSelectFeatureByLandNumber = () => {
  if (!map) return;

  // Get the main and sub numbers
  const mainNumber = localFormData.landNumberMain;
  const subNumber = localFormData.landNumberSub;

  if (!mainNumber) return false;

  // Format the search pattern based on available data
  const fullLandNumber = subNumber ? `${mainNumber}-${subNumber}` : mainNumber;
  console.log(`Searching for land number: ${fullLandNumber}`);

  // Look through all vector layers
  const layers = map.getLayers().getArray().filter(layer =>
    layer instanceof VectorLayer && layer.getSource() instanceof VectorSource
  );

  let exactMatch = null;
  let mainNumberMatch = null;

  // For each layer, try to find the feature
  for (const layer of layers) {
    const source = layer.getSource();
    const features = source.getFeatures();

    // First pass: look for exact matches
    features.forEach(feature => {
      const featureNumber = feature.get('Land_no');
      if (!featureNumber) return;

      // Check for exact match first
      if (featureNumber === fullLandNumber) {
        exactMatch = feature;
      }
      // If we're looking for a full number but no exact match yet, check for main number match
      else if (subNumber && !exactMatch && featureNumber === mainNumber) {
        mainNumberMatch = feature;
      }
    });

    // If we found an exact match, use it
    if (exactMatch) {
      console.log(`Found exact match feature with land number: ${exactMatch.get('Land_no')}`);
      selectFeature(exactMatch);
      return true;
    }
  }

  // If no exact match was found but we have a main number match, use that
  if (mainNumberMatch) {
    console.log(`Found main number match: ${mainNumberMatch.get('Land_no')}`);
    selectFeature(mainNumberMatch);
    return true;
  }

  console.log(`No feature found with land number: ${fullLandNumber}`);
  return false;
};

// Helper function to select a feature
const selectFeature = (feature) => {
  if (select) {
    select.getFeatures().clear(); // Clear any existing selection
    select.getFeatures().push(feature); // Add this feature to selection

    // Trigger the feature selection handler manually
    handleFeatureSelect({
      selected: [feature],
      deselected: []
    });

    // Center the map on this feature
    const geometry = feature.getGeometry();
    if (geometry) {
      map.getView().fit(geometry, {
        padding: [50, 50, 50, 50],
        duration: 500
      });
    }
  }
};

// Function to use the land information
const useLandInfo = () => {
  // Update form with data from the dialog
  localFormData.landNumber = landInfo.number;

  // Set county if not set
  if (!localFormData.addressCounty) {
    localFormData.addressCounty = landInfo.county;
    // This should trigger onCountyChange which will populate towns
  }

  // Set village if applicable
  if (landInfo.section && villages.value.includes(landInfo.section)) {
    localFormData.addressVillage = landInfo.section;
  }

  // Update aboriginal area status
  localFormData.isAboriginalArea = landInfo.specialLand;

  if (map) {
    map.setTarget(null);
    map = null;
  }
  // Close the dialog
  landInfoDialog.value = false;

  // Update parent form data
  updateFormData();
};

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

// // 更新父組件數據 v1
// const updateFormData = () => {
//   emit('update:formData', {
//     ...props.formData,
//     ...localFormData,
//     valid: localValid.value
//   });
// };

// Update parent component data v2
const updateFormData = () => {
  emit('update:formData', {
    ...props.formData,
    ...localFormData,
    valid: true // Always set to true for demo
  });
};


// // 表單驗證 v1
// const validate = async () => {
//   if (!form.value) return { valid: false };

//   const { valid } = await form.value.validate();
//   if (valid) {
//     updateFormData();
//   }
//   // emit('validated', { valid, step: 2 });
//   return { valid };
// };

// Form validation - simplified for localStorage demo v2
const validate = async () => {
  updateFormData();
  return { valid: true }; // Always return valid for demo
};

// // 初始化數據 v1
// onMounted(() => {
//   // 設置預設數據
//   if (props.formData) {
//     Object.keys(localFormData).forEach(key => {
//       if (props.formData[key] !== undefined) {
//         localFormData[key] = props.formData[key];
//       }
//     });
//   }

//   // 設置模擬數據
//   if (!localFormData.landNumber) {
//     localFormData.landNumber = '996-1';
//   }
//   if (!localFormData.longitude) {
//     localFormData.longitude = '120.5734';
//   }
//   if (!localFormData.latitude) {
//     localFormData.latitude = '23.5155';
//   }
//   if (!localFormData.landArea) {
//     localFormData.landArea = '8455';
//     localFormData.landAreaHa = '0.8455';
//   }
//   if (!localFormData.facilityArea) {
//     localFormData.facilityArea = '8455';
//     localFormData.facilityAreaHa = '0.8455';
//   }

//   // 設置一個範例作物
//   if (localFormData.crops.length === 0) {
//     localFormData.crops.push({
//       category: '果樹作物',
//       name: '橘'
//     });
//   }

//   // 設置一個範例所有權人
//   if (localFormData.owners.length === 0) {
//     localFormData.owners.push({
//       name: '王三三',
//       id: 'A123456789',
//       address: 'XX',
//       share: '1/2',
//       area: '4227.5'
//     });
//   }
// });

// Initialize data v2
onMounted(() => {
  // Set default data from props
  if (props.formData) {
    Object.keys(localFormData).forEach(key => {
      if (props.formData[key] !== undefined) {
        localFormData[key] = props.formData[key];
      }
    });
  }

  // Set sample data if empty
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

  // Set a sample crop if empty
  if (!localFormData.crops || localFormData.crops.length === 0) {
    localFormData.crops = [{
      category: '果樹作物',
      name: '橘'
    }];
  }

  // Set a sample owner if empty
  if (!localFormData.owners || localFormData.owners.length === 0) {
    localFormData.owners = [{
      name: '王三三',
      id: 'A123456789',
      address: 'XX',
      share: '1/2',
      area: '4227.5'
    }];
  }

  // Initial update to parent
  updateFormData();
});

// 監聽父組件數據變化
watch(() => props.formData, (newData) => {
  if (newData) {
    Object.keys(localFormData).forEach(key => {
      if (newData[key] !== undefined) {
        localFormData[key] = newData[key];
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

// Initialize the map when dialog opens
watch(landInfoDialog, (isOpen) => {
  if (isOpen) {
    // Allow time for DOM to update
    nextTick(() => {
      initMap();
    });
  }
});

// Initialize OpenLayers map
const initMap = () => {
  if (!mapElement.value || map) return;

  // Convert coordinate strings to numbers
  const lon = parseFloat(localFormData.longitude || '120.5734');
  const lat = parseFloat(localFormData.latitude || '23.5155');

  // Create map instance
  map = new Map({
    target: mapElement.value,
    layers: [
      new TileLayer({
        source: new OSM()
      })
    ],
    view: new View({
      center: fromLonLat([lon, lat]),
      zoom: 16
    })
  });

  // // Add marker after GeoJSON is loaded to ensure it's on top
  // addMarker(lon, lat);

  // Add selection interaction
  addSelectInteraction();
  // Load GeoJSON layer
  loadGeoJSONFile();

};

const addMarker = (lon, lat) => {
  if (!map) return;

  // Create marker feature
  const markerFeature = new Feature({
    geometry: new Point(fromLonLat([lon, lat])),
    name: '所選位置',
    type: 'marker'
  });

  markerFeature.setStyle(
    new Style({
      image: new Icon({
        anchor: [0.5, 1],
        src: 'https://openlayers.org/en/latest/examples/data/icon.png',
        scale: 0.7
      })
    })
  );

  const markerSource = new VectorSource({
    features: [markerFeature]
  });

  const markerLayer = new VectorLayer({
    source: markerSource,
    zIndex: 10  // Set a higher zIndex to keep marker on top
  });

  map.addLayer(markerLayer);
};

// Add these variables to track interactions
let select = null;
let modify = null;
let selectedFeatureKey = null;
let modifyFeatureKey = null;

const addSelectInteraction = () => {
  if (!map) return;

  // Define style for selected features
  const selectedStyle = new Style({
    stroke: new Stroke({
      color: 'rgba(255, 105, 0, 1)',
      width: 3
    }),
    fill: new Fill({
      color: 'rgba(255, 165, 0, 0.4)'
    })
  });

  // Create select interaction
  select = new Select({
    condition: click,
    style: selectedStyle,
    filter: (feature) => {
      // Don't select the marker
      return feature.get('type') !== 'marker';
    }
  });

  // Add the interaction to the map
  map.addInteraction(select);

  // Create modify interaction that works with the selected features
  modify = new Modify({
    features: select.getFeatures(),
    // Add a custom style to show edit handles
    style: new Style({
      image: new Icon({
        src: 'https://openlayers.org/en/latest/examples/data/square.png',
        scale: 0.7,
        anchor: [0.5, 0.5]
      }),
      stroke: new Stroke({
        color: 'rgba(255, 105, 0, 1)',
        width: 3
      }),
      fill: new Fill({
        color: 'rgba(255, 165, 0, 0.4)'
      })
    })
  });

  // Add the modify interaction to the map
  map.addInteraction(modify);

  // Listen for selection changes
  selectedFeatureKey = select.on('select', handleFeatureSelect);

  // Listen for geometry modifications
  modifyFeatureKey = modify.on('modifyend', handleFeatureModify);
};

// Add this function to handle feature modifications
const handleFeatureModify = (event) => {
  // Get the modified features
  const features = event.features.getArray();

  if (features.length > 0) {
    const feature = features[0];

    // Calculate the new area
    const geometry = feature.getGeometry();
    if (geometry) {
      // Get area in square meters
      const areaValue = getArea(geometry);
      // Round to 1 decimal place
      const roundedArea = Math.round(areaValue * 10) / 10;

      // Update the feature's area property
      feature.set('area', roundedArea);

      // Update the selectedFeatureInfo to reflect the new area
      if (selectedFeatureInfo.value) {
        selectedFeatureInfo.value = {
          ...selectedFeatureInfo.value,
          area: roundedArea
        };
      }

      // Update the land area in the form if this is the currently used feature
      if (landInfo.number === feature.get('Land_no')) {
        localFormData.landArea = roundedArea.toString();
        // Convert to hectares
        const areaInHa = (roundedArea / 10000).toFixed(4);
        localFormData.landAreaHa = areaInHa;
      }

      console.log(`Feature modified. New area: ${roundedArea} m²`);
    }
  }
};

// Function to handle feature selection
const handleFeatureSelect = (e) => {
  const selectedFeatures = e.selected;

  if (selectedFeatures.length > 0) {
    const feature = selectedFeatures[0];
    // Get properties from the feature
    const properties = feature.getProperties();
    console.log('Selected feature properties:', properties);

    // Populate the land info dialog with feature data
    if (properties) {
      // Update land info with feature properties
      landInfo.section = properties.section || landInfo.section;
      landInfo.number = properties.Land_no || landInfo.number;
      landInfo.specialLand = properties.specialLand || landInfo.specialLand;

      // If the feature has coordinates, update the form
      if (properties.lon && properties.lat) {
        localFormData.longitude = properties.lon;
        localFormData.latitude = properties.lat;
      }

      // Calculate area of the feature if it has a geometry
      const geometry = feature.getGeometry();
      let areaValue = 0;

      if (geometry) {
        // Get area in square meters
        areaValue = getArea(geometry);
        // Round to 1 decimal place
        areaValue = Math.round(areaValue * 10) / 10;

        // Set area property on the feature
        feature.set('area', areaValue);

        // If the feature already has an area property, use that instead
        if (properties.area && !isNaN(parseFloat(properties.area))) {
          areaValue = parseFloat(properties.area);
        }
      }

      // Create a copy of properties with updated area
      const updatedProperties = {
        ...properties,
        area: areaValue
      };

      // Populate the land info dialog with feature data
      if (updatedProperties) {
        // Update land info with feature properties
        landInfo.section = updatedProperties.section || landInfo.section;
        landInfo.number = updatedProperties.number || landInfo.number;
        landInfo.specialLand = updatedProperties.specialLand || landInfo.specialLand;

        // If the feature has coordinates, update the form
        if (updatedProperties.lon && updatedProperties.lat) {
          localFormData.longitude = updatedProperties.lon;
          localFormData.latitude = updatedProperties.lat;
        }

        // You can show a popup with feature info including the area
        selectedFeatureInfo.value = updatedProperties;
        featureInfoVisible.value = true;
      }

      // You can show a popup with feature info
      showFeatureInfo(feature);
    }
  } else {
    // Handle deselection
    hideFeatureInfo();
  }
};

// References for feature info popup
const featureInfoVisible = ref(false);
const selectedFeatureInfo = ref({});

// Show feature info popup
const showFeatureInfo = (feature) => {
  const properties = feature.getProperties();
  selectedFeatureInfo.value = properties;
  featureInfoVisible.value = true;
};

// Hide feature info popup
const hideFeatureInfo = () => {
  featureInfoVisible.value = false;
  landInfoDialog.value = false;
};

// Clean up interactions when map is destroyed
const cleanupMap = () => {
  if (select && selectedFeatureKey) {
    unByKey(selectedFeatureKey);
  }

  if (modify && modifyFeatureKey) {
    unByKey(modifyFeatureKey);
  }

  if (map) {
    map.setTarget(null);
    map = null;
  }
};

// Update map cleanup in watch
watch(landInfoDialog, (isOpen) => {
  if (!isOpen) {
    cleanupMap();
  }
});

// Add this to the useSelectedFeature function to update the area fields
const useSelectedFeature = () => {
  if (selectedFeatureInfo.value) {
    // Update land number fields from Land_no
    if (selectedFeatureInfo.value.Land_no) {
      const landNo = selectedFeatureInfo.value.Land_no;

      // Check if the Land_no contains a dash (main-sub format)
      if (landNo.includes('-')) {
        const [main, sub] = landNo.split('-');
        localFormData.landNumberMain = main;
        localFormData.landNumberSub = sub;
      } else {
        // If no dash, use the entire value as main number and set sub to '0'
        localFormData.landNumberMain = landNo;
        localFormData.landNumberSub = '';
      }
    }

    // If the feature has an area, update the area fields
    if (selectedFeatureInfo.value.area) {
      localFormData.landArea = selectedFeatureInfo.value.area;
      // Convert to hectares
      const areaInHa = (parseFloat(selectedFeatureInfo.value.area) / 10000).toFixed(4);
      localFormData.landAreaHa = areaInHa;

      // Set the facility area to match land area by default
      localFormData.facilityArea = selectedFeatureInfo.value.area;
      localFormData.facilityAreaHa = areaInHa;
    }

    // Find the selected feature in the map
    const selectedFeatures = select.getFeatures().getArray();
    if (selectedFeatures.length > 0) {
      const feature = selectedFeatures[0];
      const geometry = feature.getGeometry();

      if (geometry) {
        // Get the extent (bounding box) of the geometry
        const extent = geometry.getExtent();
        // Calculate the center of the extent
        const center = [(extent[0] + extent[2]) / 2, (extent[1] + extent[3]) / 2];

        // Transform from the map projection (EPSG:3857) to WGS84 (EPSG:4326)
        const transformedCenter = transform(center, 'EPSG:3857', 'EPSG:4326');

        // Update the form with the center coordinates (rounded to 6 decimal places)
        localFormData.longitude = transformedCenter[0].toFixed(6);
        localFormData.latitude = transformedCenter[1].toFixed(6);

        console.log(`Updated coordinates to center of polygon: ${localFormData.longitude}, ${localFormData.latitude}`);
      }
    }


    // Hide the feature info popup
    hideFeatureInfo();
    // Close the dialog
    landInfoDialog.value = false;
    // Make sure to update parent form data
    updateFormData();
  }
};

// Function to load GeoJSON file (replace the GML function)
const loadGeoJSONFile = () => {
  // Path to the GeoJSON file in assets
  const geoJSONFilePath = `../src/assets/GML/land_parcels.geojson`;

  console.log('Attempting to load GeoJSON from:', geoJSONFilePath);

  // Create a vector source with GeoJSON format
  const geoJSONSource = new VectorSource({
    url: geoJSONFilePath,
    format: new GeoJSON()
  });

  // Add success event listener
  // geoJSONSource.on('featuresloadend', function(event) {
  //   const features = geoJSONSource.getFeatures();
  //   console.log(`GeoJSON loaded successfully with ${features.length} features`);
  // });

  // Add success event listener
  geoJSONSource.on('featuresloadend', function(event) {
    const features = geoJSONSource.getFeatures();
    console.log(`GeoJSON loaded successfully with ${features.length} features`);

    // Add properties to features if they don't have them
    features.forEach((feature, index) => {
      if (!feature.get('id')) {
        feature.set('id', `parcel-${index + 1}`);
      }
      if (!feature.get('section')) {
        feature.set('section', localFormData.addressVillage || '瓦厝埔段');
      }
      // if (!feature.get('number')) {
      //   // Create a random land number for demo
      //   const mainNum = Math.floor(900 + Math.random() * 100);
      //   const subNum = Math.floor(1 + Math.random() * 9);
      //   feature.set('number', `${mainNum}-${subNum}`);
      // }
    });
    // Try to find and select the feature with matching land number
    setTimeout(() => {
      findAndSelectFeatureByLandNumber();
    }, 100); // Small delay to ensure map is fully initialized
  });

  // Handle loading errors
  geoJSONSource.on('loaderror', function(event) {
    console.error('Error loading GeoJSON file:', event);
  });

  // Create and add the vector layer
  const geoJSONLayer = new VectorLayer({
    source: geoJSONSource,
    style: new Style({
      stroke: new Stroke({
        color: 'rgba(0, 128, 255, 1.0)',
        width: 2
      }),
      fill: new Fill({
        color: 'rgba(0, 128, 255, 0.2)'
      })
    })
  });

  if (map) {
    map.addLayer(geoJSONLayer);
  }
}

// Clean up map when dialog closes
watch(landInfoDialog, (isOpen) => {
  if (!isOpen && map) {
    // Clean up the map when dialog closes
    map.setTarget(null);
    map = null;
  }
});

// Update map when coordinates change
watch([() => localFormData.longitude, () => localFormData.latitude], () => {
  if (map && localFormData.longitude && localFormData.latitude) {
    const lon = parseFloat(localFormData.longitude);
    const lat = parseFloat(localFormData.latitude);

    if (!isNaN(lon) && !isNaN(lat)) {
      // Update view center
      map.getView().setCenter(fromLonLat([lon, lat]));

      // Update marker position
      const vectorLayer = map.getLayers().getArray().find(layer =>
        layer instanceof VectorLayer
      );

      if (vectorLayer) {
        const feature = vectorLayer.getSource().getFeatures()[0];
        if (feature) {
          feature.setGeometry(new Point(fromLonLat([lon, lat])));
        }
      }
    }
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

.map-container {
  position: relative;
}

.feature-info-card {
  position: absolute;
  top: 10px;
  right: 10px;
  width: 200px;
  max-width: 40%;
  background: white;
  z-index: 100;
  font-size: 0.875rem;
}
</style>
