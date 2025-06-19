<template>
  <div
    ref="stepContent"
    class="step-content"
  >
    <v-card
      class="mt-4 pa-0"
      flat
    >
      <v-card-text class="pb-0 pt-0">
        <v-form
          ref="form"
          v-model="localValid"
          @submit.prevent
        >
          <!-- 申請人基本資料區塊 -->
          <v-row>
            <v-col
              cols="12"
              md="6"
            >
              <v-card
                flat
                class="mb-4 pa-4"
                color="#e3f4f4"
                rounded="lg"
              >
                <v-card-title
                  class="text-subtitle-1 font-weight-bold pa-0 pb-6"
                  style="color: #2d8c8f"
                >
                  <v-icon
                    color="#3ea0a3"
                    class="me-2 pb-1"
                    size="small"
                  >
                    mdi-account
                  </v-icon>
                  <span class="required-asterisk">*</span>申請人基本資料
                </v-card-title>

                <!-- 姓名與身分證區塊 -->
                <v-row dense>
                  <v-col
                    cols="12"
                    md="6"
                  >
                    <v-text-field
                      v-model="localFormData.name"
                      variant="outlined"
                      density="comfortable"
                      :rules="nameRules"
                      color="#3ea0a3"
                      bg-color="white"
                      @update:model-value="updateFormData"
                    >
                      <template #label>
                        申請人
                      </template>
                    </v-text-field>
                  </v-col>
                  <v-col
                    cols="12"
                    md="6"
                  >
                    <v-text-field
                      v-model="localFormData.id"
                      label="身分證字號"
                      variant="outlined"
                      density="comfortable"
                      :rules="idRules"
                      color="#3ea0a3"
                      bg-color="white"
                      @update:model-value="updateFormData"
                    >
                      <template #label>
                        身分證字號
                      </template>
                    </v-text-field>
                  </v-col>
                </v-row>

                <!-- 聯絡資訊區塊 -->
                <v-row dense>
                  <v-col cols="12">
                    <v-text-field
                      v-model="localFormData.phone"
                      placeholder="請輸入手機號碼"
                      variant="outlined"
                      density="comfortable"
                      :rules="phoneRules"
                      color="#3ea0a3"
                      bg-color="white"
                      @update:model-value="updateFormData"
                    >
                      <template #label>
                        連絡電話
                      </template>
                    </v-text-field>
                  </v-col>
                </v-row>
              </v-card>
            </v-col>

            <!-- 地址資訊區塊 -->
            <v-col
              cols="12"
              md="6"
            >
              <v-card
                flat
                class="mb-4 pa-4"
                color="#e3f4f4"
                rounded="lg"
              >
                <v-card-title
                  class="text-subtitle-1 font-weight-bold pa-0 pb-6"
                  style="color: #2d8c8f"
                >
                  <v-icon
                    color="#3ea0a3"
                    class="me-2 pb-1"
                    size="small"
                  >
                    mdi-map-marker
                  </v-icon>
                  <span class="required-asterisk">*</span>申請人通訊地址
                </v-card-title>

                <div class="d-flex align-center mb-2 justify-space-between">
                  <div class="d-flex align-center">
                    <v-btn
                      v-if="!isEditingAddress"
                      variant="text"
                      density="comfortable"
                      size="small"
                      color="#3ea0a3"
                      rounded="sm"
                      @click="isEditingAddress = true"
                    >
                      <v-icon>mdi-pencil</v-icon>
                      編輯地址
                    </v-btn>
                    <v-btn
                      v-else
                      variant="text"
                      density="comfortable"
                      size="small"
                      color="success"
                      rounded="circle"
                      @click="finishEditingAddress"
                    >
                      <v-icon>mdi-check</v-icon>
                      完成編輯
                    </v-btn>
                  </div>
                </div>

                <!-- Read-only address display -->
                <div
                  v-if="!isEditingAddress"
                  class="pa-2"
                >
                  <div class="d-flex flex-column">
                    <span class="text-subtitle-1 mb-2">{{ getFullAddress }}</span>
                    <span class="text-caption text-grey">點擊編輯按鈕以修改地址</span>
                  </div>
                </div>

                <!-- Editable address controls -->
                <div v-else>
                  <v-row dense>
                    <v-col
                      cols="12"
                      md="4"
                    >
                      <v-select
                        v-model="selectedCountyId"
                        :items="countyItems"
                        item-title="title"
                        item-value="value"
                        variant="outlined"
                        density="comfortable"
                        :loading="domicileStore.isLoading"
                        :rules="[v => !!v || '請選擇縣市']"
                        return-object
                        color="#3ea0a3"
                        bg-color="white"
                        @update:model-value="handleCountyChange"
                      >
                        <template #label>
                          縣市
                        </template>
                      </v-select>
                    </v-col>
                    <v-col
                      cols="12"
                      md="4"
                    >
                      <v-select
                        v-model="selectedTownId"
                        :items="townItems"
                        item-title="title"
                        item-value="value"
                        variant="outlined"
                        density="comfortable"
                        :loading="domicileStore.isLoading"
                        :rules="[v => !!v || '請選擇鄉鎮市區']"
                        :disabled="!selectedCountyId"
                        return-object
                        color="#3ea0a3"
                        bg-color="white"
                        @update:model-value="handleTownChange"
                      >
                        <template #label>
                          鄉鎮市區
                        </template>
                      </v-select>
                    </v-col>
                    <v-col
                      cols="12"
                      md="4"
                    >
                      <v-select
                        v-model="selectedVillageId"
                        :items="villageItems"
                        item-title="title"
                        item-value="value"
                        variant="outlined"
                        density="comfortable"
                        :loading="domicileStore.isLoading"
                        :rules="[v => !!v || '請選擇村里']"
                        :disabled="!selectedTownId"
                        return-object
                        color="#3ea0a3"
                        bg-color="white"
                        @update:model-value="handleVillageChange"
                      >
                        <template #label>
                          村里
                        </template>
                      </v-select>
                    </v-col>
                  </v-row>
                  <v-row dense>
                    <v-col cols="12">
                      <v-text-field
                        v-model="localFormData.address"
                        placeholder="請輸入門牌號碼及其他地址資訊"
                        variant="outlined"
                        density="comfortable"
                        :rules="[v => !!v || '請輸入詳細地址']"
                        color="#3ea0a3"
                        bg-color="white"
                        @update:model-value="updateFormData"
                      >
                        <template #label>
                          詳細地址
                        </template>
                      </v-text-field>
                    </v-col>
                  </v-row>
                </div>
              </v-card>
            </v-col>
          </v-row>

          <!-- 承辦資訊區塊 -->
          <v-card
            flat
            class="mb-4 pa-4"
            color="blue-grey-lighten-5"
            rounded="lg"
          >
            <v-card-title
              class="text-subtitle-1 font-weight-bold pa-0 pb-6"
              style="color: #2d8c8f"
            >
              <v-icon
                color="#3ea0a3"
                class="me-2 pb-1"
                size="small"
              >
                mdi-account-tie
              </v-icon>
              <span class="required-asterisk">*</span>承辦資訊
            </v-card-title>

            <v-row>
              <v-col
                cols="12"
                md="6"
              >
                <v-text-field
                  v-model="localFormData.undertracker"
                  variant="outlined"
                  density="comfortable"
                  :rules="[v => !!v || '請輸入承辦人']"
                  color="#3ea0a3"
                  bg-color="white"
                  @update:model-value="updateFormData"
                >
                  <template #label>
                    承辦人
                  </template>
                </v-text-field>
              </v-col>
              <v-col
                cols="12"
                md="6"
              >
                <v-text-field
                  v-model="localFormData.office"
                  label="管理處"
                  variant="outlined"
                  density="comfortable"
                  disabled
                  bg-color="white"
                  color="#3ea0a3"
                />
              </v-col>
            </v-row>
          </v-card>

          <!-- 系統資訊區塊 -->
          <v-card
            v-if="localFormData.caseNumber"
            flat
            class="mb-4 pa-4"
            color="blue-grey-lighten-5"
            rounded="lg"
          >
            <v-card-title
              class="text-subtitle-1 font-weight-bold pa-0 pb-6"
              style="color: #2d8c8f"
            >
              <v-icon
                class="me-2 pb-1"
                size="small"
                color="#3ea0a3"
              >
                mdi-information
              </v-icon>
              案件資訊
            </v-card-title>

            <v-row>
              <v-col
                cols="12"
                md="4"
              >
                <v-text-field
                  v-model="localFormData.caseNumber"
                  label="案件編號"
                  variant="outlined"
                  density="comfortable"
                  disabled
                  bg-color="white"
                  color="#3ea0a3"
                />
              </v-col>
              <v-col
                cols="12"
                md="4"
              >
                <v-text-field
                  v-model="localFormData.receivedDate"
                  label="收件日期"
                  disabled
                  variant="outlined"
                  density="comfortable"
                  bg-color="white"
                  color="#3ea0a3"
                />
              </v-col>
              <v-col
                cols="12"
                md="4"
              >
                <v-text-field
                  v-model="localFormData.receivedTime"
                  label="時間"
                  disabled
                  variant="outlined"
                  density="comfortable"
                  bg-color="white"
                  color="#3ea0a3"
                />
              </v-col>
            </v-row>
          </v-card>
        </v-form>
      </v-card-text>
    </v-card>
  </div>
</template>

<script setup lang="ts">
import { useUserStore } from '@/stores/users';
import { useDomicileStore } from '@/stores/domicile';
import type { Step1Data } from '@/types/grantForms'

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
const localValid = ref(true);
const form = ref<{ validate: () => Promise<{ valid: boolean }> } | null>(null);

const userStore = useUserStore();
const domicileStore = useDomicileStore();

// For the v-select components
const selectedCountyId = ref<{ title: string; value: number } | null>(null);
const selectedTownId = ref<{ title: string; value: number } | null>(null);
const selectedVillageId = ref<{ title: string; value: number } | null>(null);

const createInitialFormData = (): Step1Data => {
  return {
    name: '',
    id: '',
    phone: '',
    county: '',
    countyId: null,
    town: '',
    townId: null,
    village: '',
    villageId: null,
    address: '',
    undertracker: '',
    office: '',
    officeId: null,
    caseNumber: '',
    receivedDate: '',
    receivedTime: '',
    valid: true // Default to true to integrate with updated validation flow
  }
}

const localFormData = reactive<Step1Data>(createInitialFormData());

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

// Add a state to control address editing
const isEditingAddress = ref(false);

// Computed property to display the full address
const getFullAddress = computed(() => {
  let address = '';
  if (localFormData.county) address += localFormData.county;
  if (localFormData.town) address += localFormData.town;
  if (localFormData.village) address += localFormData.village;
  if (localFormData.address) address += localFormData.address;

  return address || '尚未填寫地址';
});

// Method to finish editing and validate address
const finishEditingAddress = () => {
  // Check if the address is valid before closing edit mode
  const hasRequiredFields = !!selectedCountyId.value &&
                           !!selectedTownId.value &&
                           !!selectedVillageId.value &&
                           !!localFormData.address;

  if (hasRequiredFields) {
    isEditingAddress.value = false;
    updateFormData();
  } else {
    // Show error or keep edit mode open
    alert('請填寫完整地址資訊');
  }
};

// County dropdown items
const countyItems = computed(() => {
  return domicileStore.countyOptions.map(county => ({
    title: county.title,
    value: county.value
  }));
});

// Town dropdown items (filtered by selected county)
const townItems = computed(() => {
  if (!selectedCountyId.value) return [];
  return domicileStore.getTownsForCountyId(selectedCountyId.value?.value).map(town => ({
    title: town.title,
    value: town.value
  }));
});

// Village dropdown items (filtered by selected town)
const villageItems = computed(() => {
  if (!selectedTownId.value) return [];
  return domicileStore.getVillagesForTownId(selectedTownId.value?.value).map(village => ({
    title: village.title,
    value: village.value
  }));
});

// Handle county selection change
const handleCountyChange = async (county: { title: string; value: number }) => {
  if (!county) return;

  // Reset dependent fields
  selectedTownId.value = null;
  selectedVillageId.value = null;
  localFormData.town = '';
  localFormData.townId = null;
  localFormData.village = '';
  localFormData.villageId = null;

  // Update form data with selected county
  localFormData.county = county.title;
  localFormData.countyId = county.value;

  // Load towns for this county
  await domicileStore.loadTownsByCountyId(county.value);
  updateFormData();
};

// Handle town selection change
const handleTownChange = async (town: { title: string; value: number }) => {
  if (!town) return;

  // Reset dependent fields
  selectedVillageId.value = null;
  localFormData.village = '';
  localFormData.villageId = null;

  // Update form data with selected town
  localFormData.town = town.title;
  localFormData.townId = town.value;

  // Load villages for this town
  await domicileStore.loadVillagesByTownId(town.value);
  updateFormData();
};

// Handle village selection change
const handleVillageChange = (village: { title: string; value: number }) => {
  if (!village) return;

  // Update form data with selected village
  localFormData.village = village.title;
  localFormData.villageId = village.value;
  updateFormData();
};

// 更新父組件數據 - 簡化實現避免無限迴圈
const updateFormData = () => {
  if (isUpdatingFromProps.value) {
    console.log('🚫 step1.vue: Skipping updateFormData (updating from props)');
    return;
  }

  console.log('📤 step1.vue: Emitting updated form data to parent');
  emit('update:formData', {
    ...props.formData,
    ...localFormData,
    valid: localValid.value
  });
};

// Validate and emit validated event
// const validate = async () => {
//   if (!form.value) return { valid: false };

//   const { valid } = await form.value.validate();

//   if (valid) {
//     updateFormData();
//   }

//   return { valid };
// };

// Initialize address dropdowns based on string values from the store
const initializeAddressDropdowns = async () => {
  try {
    // First ensure counties are loaded
    if (domicileStore.counties.length === 0) {
      await domicileStore.loadCounties();
    }      // Ensure countyOptions exists before using find()
      if (!domicileStore.countyOptions || !Array.isArray(domicileStore.countyOptions)) {
        console.warn('County options not available yet, using direct county string');
        // Fallback: Create a temporary county option
        if (localFormData.county) {
          selectedCountyId.value = {
            title: localFormData.county,
            value: localFormData.countyId || 0
          };
          return; // Exit early since we can't proceed with cascading data
        }
        return;
      }

      // Find county by name
      const county = domicileStore.countyOptions.find(c => c.title === localFormData.county);
      if (county) {
        selectedCountyId.value = county;
        localFormData.countyId = county.value;

        // Load towns for this county
        await domicileStore.loadTownsByCountyId(county.value);

        // Get towns for this county from the map
        const countyTowns = domicileStore.townsByCountyId.get(county.value) || [];
        if (countyTowns.length === 0) {
          console.warn('Towns not available yet for county:', county.title);
          return;
        }

        // Find town by name
        const town = countyTowns.find(t => t.name === localFormData.town);
        if (town) {
          selectedTownId.value = {
            title: town.name,
            value: town.id
          };
          localFormData.townId = town.id;

          // Load villages for this town
          await domicileStore.loadVillagesByTownId(town.id);

          // Get villages for this town from the map
          const townVillages = domicileStore.villagesByTownId.get(town.id) || [];
          if (townVillages.length === 0) {
            console.warn('Villages not available yet for town:', town.name);
            return;
          }

          // Find village by name
          const village = townVillages.find(v => v.name === localFormData.village);
          if (village) {
            selectedVillageId.value = {
              title: village.name,
              value: village.id
            };
            localFormData.villageId = village.id;
          }
        }
      }
    } catch (error) {
      console.error('Error initializing address dropdowns:', error);
    }
};

// Initialize data
onMounted(async () => {
  try {
    // Initialize the domicile store
    await domicileStore.initializeStore();

    // Only try to set dropdown selections if we have the necessary data
    if (localFormData.countyId && domicileStore.counties.length > 0) {
      // Set county dropdown
      const countyObj = domicileStore.counties.find(c => c.id === localFormData.countyId);
      if (countyObj) {
        selectedCountyId.value = {
          title: countyObj.name,
          value: countyObj.id
        };

        // Continue with town and village setup
        await domicileStore.loadTownsByCountyId(countyObj.id);

        if (localFormData.townId) {
          const townObj = domicileStore.towns.find(t => t.id === localFormData.townId);
          if (townObj) {
            selectedTownId.value = {
              title: townObj.name,
              value: townObj.id
            };

            await domicileStore.loadVillagesByTownId(townObj.id);

            if (localFormData.villageId) {
              const villageObj = domicileStore.villages.find(v => v.id === localFormData.villageId);
              if (villageObj) {
                selectedVillageId.value = {
                  title: villageObj.name,
                  value: villageObj.id
                };
              }
            }
          }
        }
      }
    }
    // If we have county string but no countyId or selections
    else if (localFormData.county && !selectedCountyId.value) {
      await initializeAddressDropdowns();
    }

    // Set default office if not set
    if (!localFormData.office) {
      localFormData.office = userStore.currentUser?.office?.name ?? '';
    }

    // Initial update to parent
    updateFormData();
  } catch (error) {
    console.error('Error in onMounted:', error);
  }
});

// 使用 ref 來防止無限迴圈 - 必須在 watchers 之前宣告
const isUpdatingFromProps = ref(false);

// Watch for props changes
watch(() => props.formData, async (newData) => {
  if (!newData) return;

  try {
    // 暫停 localFormData 的監聽以避免無限迴圈
    isUpdatingFromProps.value = true;
    let hasChanges = false;    // 使用最簡潔且類型安全的寫法
    Object.entries(localFormData).forEach(([key, currentValue]) => {
      const newValue = newData[key as keyof Step1Data];
      if (newValue !== undefined && newValue !== currentValue) {
        // 直接使用 Object.assign 避免類型問題
        Object.assign(localFormData, { [key]: newValue });
        hasChanges = true;
      }
    });

    // If we have county data but no dropdown selection, try to initialize
    if (newData.county && !selectedCountyId.value && domicileStore.counties.length > 0) {
      await initializeAddressDropdowns();
    }

    // 只在有實際變化時才記錄
    if (hasChanges) {
      console.log('📥 step1.vue: Props updated, synced to localFormData');
    }

    // 恢復監聽
    await nextTick();
    isUpdatingFromProps.value = false;
  } catch (error) {
    console.error('Error in formData watcher:', error);
    isUpdatingFromProps.value = false;
  }
}, { deep: true });

// Watch for changes in local form data
watch(localFormData, () => {
  // 如果正在從 props 更新，就不要觸發 updateFormData
  if (isUpdatingFromProps.value) {
    console.log('🚫 step1.vue: Skipping updateFormData (updating from props)');
    return;
  }

  console.log('📤 step1.vue: localFormData changed, calling updateFormData');
  updateFormData();
}, { deep: true });

// Watch for validation status changes
watch(localValid, (newVal) => {
  if (isUpdatingFromProps.value) return;

  if (props.formData?.valid !== newVal) {
    console.log('📋 step1.vue: Validation status changed:', newVal);
    updateFormData();
  }
});
</script>

<style scoped>
.step-content {
  padding: 0;
  background-color: transparent !important;
}

/* 卡片懸停效果 */
.v-card.pa-4 {
  transition: all 0.3s ease;
}

.v-card.pa-4:hover {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05) !important;
}

/* 唯讀輸入框樣式 */
:deep(.v-field--disabled .v-field__input) {
  color: rgba(0, 0, 0, 1) !important;
}

/* 必填欄位紅色星號樣式 */
.required-asterisk {
  color: #ff0000 !important;
  font-weight: bold;
  margin-left: 2px;
}
</style>
