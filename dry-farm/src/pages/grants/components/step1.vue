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
          <!-- 系統資訊區塊 -->
          <v-card
            v-if="!localFormData.caseNumber"
            class="mb-4"
            variant="outlined"
          >
            <v-card-title class="bg-light-blue-lighten-4 d-flex align-center py-2 px-4">
              <v-icon
                class="me-2"
                size="small"
              >
                mdi-information
              </v-icon>
              <span class="text-subtitle-1 font-weight-medium">申請基本資訊</span>
            </v-card-title>

            <v-card-text class="pa-4">
              <v-sheet
                class="pa-3 rounded"
                color="grey-lighten-5"
              >
                <v-row>
                  <v-col
                    cols="12"
                    md="4"
                  >
                    <v-text-field
                      v-model="localFormData.caseNumber"
                      label="案件編號"
                      readonly
                      variant="outlined"
                      density="comfortable"
                      bg-color="grey-lighten-4"
                    />
                  </v-col>
                  <v-col
                    cols="12"
                    md="4"
                  >
                    <v-text-field
                      v-model="localFormData.receivedDate"
                      label="收件日期"
                      readonly
                      variant="outlined"
                      density="comfortable"
                      bg-color="grey-lighten-4"
                    />
                  </v-col>
                  <v-col
                    cols="12"
                    md="4"
                  >
                    <v-text-field
                      v-model="localFormData.receivedTime"
                      label="時間"
                      readonly
                      variant="outlined"
                      density="comfortable"
                      bg-color="grey-lighten-4"
                    />
                  </v-col>
                </v-row>
              </v-sheet>
            </v-card-text>
          </v-card>

          <!-- 申請人基本資料區塊 -->
          <v-card
            class="mb-4"
            variant="outlined"
          >
            <v-card-title class="bg-light-blue-lighten-4 d-flex align-center py-2 px-4">
              <v-icon
                class="me-2"
                size="small"
              >
                mdi-account-detail
              </v-icon>
              <span class="text-subtitle-1 font-weight-medium">申請人基本資料</span>
            </v-card-title>

            <v-card-text class="pa-4">
              <!-- 姓名與身分證區塊 -->
              <v-sheet
                class="mb-3 pa-3 rounded"
                color="blue-grey-lighten-5"
              >
                <div class="d-flex align-center mb-2">
                  <v-icon
                    size="small"
                    class="me-2"
                  >
                    mdi-card-account-details
                  </v-icon>
                  <span class="text-body-2 font-weight-medium">身分資訊</span>
                </div>
                <v-row>
                  <v-col
                    cols="12"
                    md="6"
                  >
                    <v-text-field
                      v-model="localFormData.name"
                      label="申請人"
                      variant="outlined"
                      density="comfortable"
                      :rules="nameRules"
                      @update:model-value="updateFormData"
                    />
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
                      @update:model-value="updateFormData"
                    />
                  </v-col>
                </v-row>
              </v-sheet>

              <!-- 聯絡資訊區塊 -->
              <v-sheet
                class="mb-3 pa-3 rounded"
                color="blue-grey-lighten-5"
              >
                <div class="d-flex align-center mb-2">
                  <v-icon
                    size="small"
                    class="me-2"
                  >
                    mdi-phone
                  </v-icon>
                  <span class="text-body-2 font-weight-medium">聯絡資訊</span>
                </div>
                <v-row>
                  <v-col cols="12">
                    <v-text-field
                      v-model="localFormData.phone"
                      placeholder="請輸入手機號碼"
                      label="連絡電話"
                      variant="outlined"
                      density="comfortable"
                      :rules="phoneRules"
                      @update:model-value="updateFormData"
                    />
                  </v-col>
                </v-row>
              </v-sheet>

              <!-- 地址資訊區塊 -->
              <v-sheet
                class="mb-3 pa-3 rounded"
                color="blue-grey-lighten-5"
              >
                <div class="d-flex align-center mb-2 justify-space-between">
                  <div class="d-flex align-center">
                    <v-icon
                      size="small"
                      class="me-2"
                    >
                      mdi-home
                    </v-icon>
                    <span class="text-body-2 font-weight-medium">通訊地址</span>
                  </div>
                  <v-btn
                    v-if="!isEditingAddress"
                    variant="text"
                    density="comfortable"
                    icon="mdi-pencil"
                    size="small"
                    color="primary"
                    rounded="circle"
                    @click="isEditingAddress = true"
                  />
                  <v-btn
                    v-else
                    variant="text"
                    density="comfortable"
                    icon="mdi-check"
                    size="small"
                    color="success"
                    @click="finishEditingAddress"
                  />
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
                  <v-row>
                    <v-col
                      cols="12"
                      md="4"
                    >
                      <v-select
                        v-model="selectedCountyId"
                        label="縣市"
                        :items="countyItems"
                        item-title="title"
                        item-value="value"
                        variant="outlined"
                        density="comfortable"
                        :loading="domicileStore.isLoading"
                        :rules="[v => !!v || '請選擇縣市']"
                        return-object
                        @update:model-value="handleCountyChange"
                      />
                    </v-col>
                    <v-col
                      cols="12"
                      md="4"
                    >
                      <v-select
                        v-model="selectedTownId"
                        label="鄉鎮市區"
                        :items="townItems"
                        item-title="title"
                        item-value="value"
                        variant="outlined"
                        density="comfortable"
                        :loading="domicileStore.isLoading"
                        :rules="[v => !!v || '請選擇鄉鎮市區']"
                        :disabled="!selectedCountyId"
                        return-object
                        @update:model-value="handleTownChange"
                      />
                    </v-col>
                    <v-col
                      cols="12"
                      md="4"
                    >
                      <v-select
                        v-model="selectedVillageId"
                        label="村里"
                        :items="villageItems"
                        item-title="title"
                        item-value="value"
                        variant="outlined"
                        density="comfortable"
                        :loading="domicileStore.isLoading"
                        :rules="[v => !!v || '請選擇村里']"
                        :disabled="!selectedTownId"
                        return-object
                        @update:model-value="handleVillageChange"
                      />
                    </v-col>
                  </v-row>
                  <v-row>
                    <v-col cols="12">
                      <v-text-field
                        v-model="localFormData.address"
                        placeholder="請輸入門牌號碼及其他地址資訊"
                        label="詳細地址"
                        variant="outlined"
                        density="comfortable"
                        :rules="[v => !!v || '請輸入詳細地址']"
                        @update:model-value="updateFormData"
                      />
                    </v-col>
                  </v-row>
                </div>
              </v-sheet>
            </v-card-text>
          </v-card>

          <!-- 承辦資訊區塊 -->
          <v-card variant="outlined">
            <v-card-title class="bg-light-blue-lighten-4 d-flex align-center py-2 px-4">
              <v-icon
                class="me-2"
                size="small"
              >
                mdi-account-tie
              </v-icon>
              <span class="text-subtitle-1 font-weight-medium">承辦資訊</span>
            </v-card-title>

            <v-card-text class="pa-4">
              <v-sheet
                class="pa-3 rounded"
                color="grey-lighten-5"
              >
                <v-row>
                  <v-col
                    cols="12"
                    md="6"
                  >
                    <v-text-field
                      v-model="localFormData.manager"
                      label="承辦人"
                      variant="outlined"
                      density="comfortable"
                      :rules="[v => !!v || '請輸入承辦人']"
                      @update:model-value="updateFormData"
                    />
                  </v-col>
                  <v-col
                    cols="12"
                    md="6"
                  >
                    <v-text-field
                      v-model="localFormData.department"
                      label="管理處"
                      variant="outlined"
                      density="comfortable"
                      readonly
                      bg-color="grey-lighten-4"
                    />
                  </v-col>
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
import { useUserStore } from '@/stores/users';
import { useDomicileStore } from '@/stores/domicile';

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
const form = ref(null);

const userStore = useUserStore();
const domicileStore = useDomicileStore();

// For the v-select components
const selectedCountyId = ref<{ title: string; value: number } | null>(null);
const selectedTownId = ref<{ title: string; value: number } | null>(null);
const selectedVillageId = ref<{ title: string; value: number } | null>(null);

// Define local form data with reactive to track changes
const localFormData = reactive({
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
  manager: '',
  department: '',
  departmentId: null,
  caseNumber: '',
  receivedDate: '',
  receivedTime: '',
  valid: true // Default to true to integrate with updated validation flow
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
const handleCountyChange = async (county) => {
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
const handleTownChange = async (town) => {
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
const handleVillageChange = (village) => {
  if (!village) return;

  // Update form data with selected village
  localFormData.village = village.title;
  localFormData.villageId = village.value;
  updateFormData();
};

// 更新父組件數據 - Updated to work with new grants store approach
const updateFormData = () => {
  // Create data object to send to parent
  // const updatedData = {
  //   ...props.formData,
  //   ...localFormData,
  //   valid: localValid.value
  // }
  // console.log('Updated form data:', updatedData)
  // Emit to parent to update grants store
  // emit('update:formData', updatedData)
  emit('update:formData', {
    ...props.formData,
    ...localFormData,
    valid: localValid.value
  })
  // Also update localStorage directly to ensure synchronization
  try {
    // Get current grants data from localStorage or initialize empty object
    const storedData = localStorage.getItem('grantsData');
    const grantsData = storedData ? JSON.parse(storedData) : {};

    // Update step1 data
    grantsData.step1 = {
      name: localFormData.name,
      id: localFormData.id,
      phone: localFormData.phone,
      county: localFormData.county,
      countyId: localFormData.countyId,
      town: localFormData.town,
      townId: localFormData.townId,
      village: localFormData.village,
      villageId: localFormData.villageId,
      address: localFormData.address,
      manager: localFormData.manager,
      department: localFormData.department,
      departmentId: localFormData.departmentId,
      caseNumber: localFormData.caseNumber,
      receivedDate: localFormData.receivedDate,
      receivedTime: localFormData.receivedTime
    }

    // Store back to localStorage
    localStorage.setItem('grantsData', JSON.stringify(grantsData));
  } catch (error) {
    console.error('Error saving to localStorage:', error);
  }
};

// Validate and emit validated event
const validate = async () => {
  if (!form.value) return { valid: false };

  const { valid } = await form.value.validate();

  if (valid) {
    updateFormData();
  }

  return { valid };
};

// Initialize address dropdowns based on string values from the store
const initializeAddressDropdowns = async () => {
  try {
    // First ensure counties are loaded
    if (domicileStore.counties.length === 0) {
      await domicileStore.loadCounties();
    }

    // Ensure countyOptions exists before using find()
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

      // Ensure townOptions exists
      if (!domicileStore.townOptions || !Array.isArray(domicileStore.townOptions)) {
        console.warn('Town options not available yet');
        return;
      }

      // Find town by name
      const town = domicileStore.townOptions.find(t => t.title === localFormData.town);
      if (town) {
        selectedTownId.value = town;
        localFormData.townId = town.value;

        // Load villages for this town
        await domicileStore.loadVillagesByTownId(town.value);

        // Ensure villageOptions exists
        if (!domicileStore.villageOptions || !Array.isArray(domicileStore.villageOptions)) {
          console.warn('Village options not available yet');
          return;
        }

        // Find village by name
        const village = domicileStore.villageOptions.find(v => v.title === localFormData.village);
        if (village) {
          selectedVillageId.value = village;
          localFormData.villageId = village.value;
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

    // Set form data from props safely
    if (props.formData) {
      Object.keys(localFormData).forEach(key => {
        if (props.formData[key] !== undefined) {
          // Force reactivity with direct assignment
          localFormData[key] = props.formData[key];
        }
      });

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
    }

    // Set default department if not set
    if (!localFormData.department) {
      localFormData.department = userStore.currentUser?.department || '瑠公管理處';
    }

    // Initial update to parent
    updateFormData();
  } catch (error) {
    console.error('Error in onMounted:', error);
  }
});

// Watch for props changes
watch(() => props.formData, async (newData) => {
  if (!newData) return;

  try {
    // Update local form data
    Object.keys(localFormData).forEach(key => {
      if (newData[key] !== undefined && newData[key] !== localFormData[key]) {
        localFormData[key] = newData[key];
      }
    });

    // If we have county data but no dropdown selection, try to initialize
    if (newData.county && !selectedCountyId.value && domicileStore.counties.length > 0) {
      await initializeAddressDropdowns();
    }
  } catch (error) {
    console.error('Error in formData watcher:', error);
  }
}, { deep: true });

// Watch for changes in local form data
watch(localFormData, () => {
  updateFormData();
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

.bg-light-blue-lighten-5 {
  background-color: #e3f2fd !important;
}
</style>
