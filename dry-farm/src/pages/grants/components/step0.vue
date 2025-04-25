<template>
  <div
    ref="stepContent"
    class="step-content"
  >
    <v-card
      class="mb-3 pa-0"
      flat
    >
      <v-card-text class="pb-0 pt-0">
        <v-form
          ref="form"
          v-model="localValid"
          @submit.prevent
        >
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
                mdi-account-details
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
                    mdi-home
                  </v-icon>
                  <span class="text-body-2 font-weight-medium">通訊地址</span>
                </div>
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
                      label="詳細地址"
                      variant="outlined"
                      density="comfortable"
                      :rules="[v => !!v || '請輸入詳細地址']"
                      placeholder="請輸入門牌號碼及其他地址資訊"
                      @update:model-value="updateFormData"
                    />
                  </v-col>
                </v-row>
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
                      v-model="localFormData.undertracker"
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
                    <v-select
                      v-model="localFormData.department"
                      disabled
                      label="管理處"
                      :items="departments"
                      variant="outlined"
                      density="comfortable"
                      :rules="[v => !!v || '請選擇管理處']"
                      @update:model-value="updateFormData"
                    />
                  </v-col>
                </v-row>
              </v-sheet>
            </v-card-text>
          </v-card>
        </v-form>
      </v-card-text>
    </v-card>

    <v-card
      class="step-navigation-card ma-0 pa-0"
      flat
    >
      <div class="d-flex align-center pr-4 mt-0 pt-0">
        <v-spacer />
        <div class="navigation-buttons">
          <v-btn
            color="primary"
            class="mb-2"
            size="large"
            rounded="lg"
            :disabled="!isValid"
            @click="createProject"
          >
            成案
            <v-icon end>
              mdi-check
            </v-icon>
          </v-btn>
        </div>
      </div>
    </v-card>

    <!-- 處理中對話框 -->
    <v-dialog
      v-model="isProcessing"
      persistent
      width="300"
    >
      <v-card>
        <v-card-text class="text-center pa-5">
          <v-progress-circular
            indeterminate
            color="primary"
            size="64"
            class="mb-3"
          />
          <div class="text-body-1">
            建立專案中，請稍候...
          </div>
        </v-card-text>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup lang="ts">
import { useUserStore } from '@/stores/users'
import { useOfficesStore } from '@/stores/offices'
import { useDomicileStore } from '@/stores/domicile'
import { useGrantsStore } from '@/stores/grants'


const userStore = useUserStore()
const officesStore = useOfficesStore()
const domicileStore = useDomicileStore()
const grantsStore = useGrantsStore()

const router = useRouter();
const props = defineProps<{
  formData: {
    name?: string;
    id?: string;
    phone?: string;
    county?: string;
    town?: string;
    village?: string;
    address?: string;
    undertracker?: string;
    department?: string | null;
    valid?: boolean;
    countyId?: string | null; // Add countyId to the type definition
    townId?: string | null;   // Add townId to the type definition
    villageId?: string | null; // Add villageId to the type definition
  };  // 接收父組件數據，如果有的話
}>();

const emit = defineEmits(['update:formData', 'projectCreated']);
const localValid = ref(false);
const form = ref(null);
const isProcessing = ref(false);

// Form data - now includes both text values and IDs
const localFormData = reactive({
  name: '',
  id: '',
  phone: '',
  county: '',       // Text value for display
  countyId: null,   // ID value for relationships
  town: '',         // Text value for display
  townId: null,     // ID value for relationships
  village: '',      // Text value for display
  villageId: null,  // ID value for relationships
  address: '',
  undertracker: '',
  department: computed(() => userStore.currentUser?.office?.name || null),
  departmentId: computed(() => userStore.currentUser?.office?.id || null)
})

// For the v-select components
const selectedCountyId = ref<{ title: string; value: number } | null>(null)
const selectedTownId = ref<{ title: string; value: number } | null>(null)
const selectedVillageId = ref<{ title: string; value: number } | null>(null)

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

// County dropdown items
const countyItems = computed(() => {
  return domicileStore.countyOptions.map(county => ({
    title: county.title,
    value: county.value
  }))
})

// Town dropdown items (filtered by selected county)
const townItems = computed(() => {
  if (!selectedCountyId.value) return []
  return domicileStore.getTownsForCountyId(selectedCountyId.value?.value).map(town => ({
    title: town.title,
    value: town.value
  }))
})

// Village dropdown items (filtered by selected town)
const villageItems = computed(() => {
  if (!selectedTownId.value) return []
  return domicileStore.getVillagesForTownId(selectedTownId.value?.value).map(village => ({
    title: village.title,
    value: village.value
  }))
})


const handleCountyChange = async (county: County | null): Promise<void> => {
  if (!county) return

  // Reset dependent fields
  selectedTownId.value = null
  selectedVillageId.value = null
  localFormData.town = ''
  localFormData.townId = null
  localFormData.village = ''
  localFormData.villageId = null

  // Update form data with selected county
  localFormData.county = county.title
  localFormData.countyId = county.value

  // Load towns for this county
  await domicileStore.loadTownsByCountyId(county.value)
  updateFormData()
}

// Handle town selection change
const handleTownChange = async (town) => {
  if (!town) return

  // Reset dependent fields
  selectedVillageId.value = null
  localFormData.village = ''
  localFormData.villageId = null

  // Update form data with selected town
  localFormData.town = town.title
  localFormData.townId = town.value

  // Load villages for this town
  await domicileStore.loadVillagesByTownId(town.value)
  updateFormData()
}

// Handle village selection change
const handleVillageChange = (village) => {
  if (!village) return

  // Update form data with selected village
  localFormData.village = village.title
  localFormData.villageId = village.value
  updateFormData()
}

// 管理處列表
const departments = computed(() => officesStore.items)

// With this filtered version:
// const departments = computed(() =>
//   officesStore.items.filter(item => item.raw?.classification === 1 || item.classification === 1)
// )


const isValid = computed(() => {
  return localValid.value;
});


// 表單驗證
const validate = async () => {
  const { valid } = await form.value.validate();
  if (valid) {
    updateFormData();
  }
  return valid;
};

// 建立專案
const createProject = async () => {
  const valid = await validate()
  if (!valid) return

  isProcessing.value = true

  try {
    const projectData = {
      applicant_name: localFormData.name,
      applicant_id: localFormData.id,
      applicant_phone: localFormData.phone,
      county: localFormData.county,
      county_id: Number(localFormData.countyId),
      town: localFormData.town,
      townId: Number(localFormData.townId),
      village: localFormData.village,
      village_id: localFormData.villageId ? Number(localFormData.villageId) : undefined,
      address: localFormData.address,
      undertracker: localFormData.undertracker,
      office: localFormData.department || '',
      office_id: Number(localFormData.departmentId)
    }

    console.log('Sending to API:', JSON.stringify(projectData));

    // Call the store action to create the project
    const result = await grantsStore.createProject(projectData)

    // Emit event for parent components
    emit('projectCreated', {
      projectId: result.case_number,
      data: { ...localFormData }
    })

    // Navigate to the edit page
    router.push({
      path: '/grants/edit',
      query: { id: result.case_number }
    });
  } catch (error) {
    console.error('創建專案失敗', error);
    // You could add a toast/notification here
  } finally {
    isProcessing.value = false;
  }

    // 這裡應該調用後端 API 建立專案
    // 例如: const response = await axios.post('/api/projects/create', localFormData);

    // 模擬 API 呼叫延遲
    // await new Promise(resolve => setTimeout(resolve, 1500));

    // 假設後端返回了一個專案 ID
    // const projectId = '113010001'; // 這個值應該從後端 API 響應中獲取

    // 觸發專案創建成功事件
    // emit('projectCreated', {
      // projectId,
      // data: { ...localFormData }
    // });

    // 導航到專案編輯頁面
    // router.push({
      // name: 'grant-edit',
      // params: { id: projectId }
    // });
  // } catch (error) {
    // console.error('創建專案失敗', error);
    // 處理錯誤情況，例如顯示錯誤提示
  // } finally {
    // isProcessing.value = false;
  // }
};

// 初始化數據
// onMounted(async () => {
//   await domicileStore.initializeStore()

//   localFormData.undertracker = userStore.userFullName
//   // 從父組件接收數據（如果有的話）
//   // if (props.formData) {
//   //   Object.keys(localFormData).forEach(key => {
//   //     if (props.formData[key] !== undefined) {
//   //       localFormData[key] = props.formData[key];
//   //     }
//   //   });
//   // }

//   // Handle any existing parent data
//   // if (props.formData) {
//   //   Object.keys(localFormData).forEach(key => {
//   //     if (props.formData[key] !== undefined) {
//   //       localFormData[key] = props.formData[key];
//   //     }
//   //   });
//   // }

//   // Ensure office data is loaded
//   // if (!officesStore.isOfficesLoaded) {
//   //   officesStore.fetchOffices()
//   // }
// });

// Initialize form data
onMounted(async () => {
  // Initialize the domicile store
  await domicileStore.initializeStore()

  // Set default values from user
  localFormData.undertracker = userStore.userFullName

  // Restore previous selections if available
  if (props.formData) {
    if (props.formData.countyId) {
      const county = domicileStore.getCountyById(Number(props.formData.countyId))
      if (county) {
        selectedCountyId.value = { title: county.name, value: county.id }
        await domicileStore.loadTownsByCountyId(county.id)
      }
    }

    if (props.formData.townId) {
      const town = domicileStore.getTownById(Number(props.formData.townId))
      if (town) {
        selectedTownId.value = { title: town.name, value: town.id }
        await domicileStore.loadVillagesByTownId(town.id)
      }
    }

    if (props.formData.villageId) {
      const villages = domicileStore.getVillagesForTownId(Number(props.formData.townId))
      const village = villages.find(v => v.value === Number(props.formData.villageId))
      if (village) {
        selectedVillageId.value = { title: village.title, value: village.value }
      }
    }
  }
})

// 監聽父組件數據變化
// watch(() => props.formData, (newVal) => {
//   if (newVal) {
//     Object.keys(localFormData).forEach(key => {
//       if (newVal[key] !== undefined && newVal[key] !== localFormData[key]) {
//         localFormData[key] = newVal[key];
//       }
//     });
//   }
// }, { deep: true });

// 監聽本地數據變化，更新父組件
watch(localFormData, () => {
  console.log('localFormData changed:', localFormData)
  updateFormData();
}, { deep: true });

// 監聽本地表單驗證狀態
watch(localValid, (newVal) => {
  if (props.formData?.valid !== newVal) {
    updateFormData();
  }
});
watchEffect(() => {
  // This will automatically run whenever user data changes
  // and update the field immediately
  if (userStore.userFullName) {
    // localFormData.undertracker = userStore.userFullName;
  }

  // Update department when office data is available
  // if (userStore.currentUser?.office?.id) {
  //   const officeId = userStore.currentUser.office.id;
  //   localFormData.department = officeId;
  // }
})

// Update parent form data
const updateFormData = () => {
  emit('update:formData', {
    ...props.formData,
    ...localFormData,
    valid: localValid.value
  })
}
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
