<template>
  <v-container
    fluid
    class="material-container px-6 pb-0 pt-0"
    style="background-color: white"
  >
    <!-- 標題區域 -->
    <v-row justify="center">
      <v-col
        cols="10"
        lg="10"
        align-self="center"
        class="pt-0"
      >
        <!-- 功能按鈕區 -->
        <div class="d-flex flex-wrap align-center pr-2">
          <v-spacer />
          <div class="d-flex gap-2">
            <v-btn
              class="action-btn"
              color="#3ea0a3"
              prepend-icon="mdi-plus"
              variant="outlined"
              rounded="lg"
              size="large"
              @click="editDialog = true; Object.assign(editedItem, defaultItem)"
            >
              新增材料
            </v-btn>
          </div>
        </div>
        <div class="section-wrapper">
          <v-card
            class="mx-auto section-card pa-4"
            variant="outlined"
            rounded="lg"
          >
            <v-card-item class="custom-title">
              <v-card-title class="text-h5 font-weight-black">
                管路灌溉材料列表
              </v-card-title>
            </v-card-item>

            <v-card-text>
              <!-- 篩選卡片 -->
              <v-card
                class="table-card mb-4"
                rounded="lg"
                elevation="0"
              >
                <div
                  class="d-flex flex-wrap align-center gap-3 pa-4"
                  style="background-color: #e3f4f4;"
                >
                  <v-icon
                    icon="mdi-filter-variant"
                    color="#3ea0a3"
                    class="me-2"
                  />
                  <span class="text-subtitle-1 font-weight-medium">篩選條件</span>
                  <v-spacer />

                  <!-- 篩選區域 -->
                  <div class="d-flex flex-wrap">
                    <v-select
                      v-model="selectedModule"
                      :items="dynamicModuleOptions"
                      :loading="pfModulesStore.isLoading"
                      label="模組名稱"
                      density="comfortable"
                      variant="outlined"
                      hide-details
                      class="filter-select mr-2"
                      style="min-width: 150px"
                      clearable
                      bg-color="white"
                      rounded="lg"
                    />
                    <v-select
                      v-model="selectedMaterial"
                      :items="materialOptions"
                      :loading="pfMaterialsStore.isLoading"
                      label="材質"
                      density="comfortable"
                      variant="outlined"
                      hide-details
                      class="filter-select mr-2"
                      style="min-width: 150px"
                      clearable
                      bg-color="white"
                      rounded="lg"
                    />
                    <v-text-field
                      v-model="search"
                      density="comfortable"
                      label="模糊搜尋"
                      prepend-inner-icon="mdi-magnify"
                      variant="outlined"
                      hide-details
                      clearable
                      style="min-width: 200px"
                      bg-color="white"
                      rounded="lg"
                    />
                  </div>
                </div>
              </v-card>

              <!-- 表格區域 -->
              <v-card
                class="table-card"
                rounded="lg"
                elevation="0"
              >
                <v-data-table-virtual
                  ref="tableRef"
                  fixed-header
                  :headers="headers"
                  :items="indexedItems"
                  :loading="isLoadingMoreFromStore"
                  :height="500"
                  density="compact"
                  item-value="id"
                  class="materials-table rounded-lg"
                >
                  <!-- 自訂表格標題 -->
                  <template #[`headers`]="{ columns }">
                    <tr>
                      <th
                        v-for="header in columns"
                        :key="header.key"
                        :class="[
                          'custom-header',
                          header.sortable !== false ? 'sortable-header' : '',
                          { 'text-center': header.align === 'center', 'text-end': header.align === 'end' }
                        ]"
                        :style="{ width: header.width || 'auto', padding: '0px', margin: '0px' }"
                        @click="header.sortable !== false ? updateSorting(header.key) : null"
                        @mouseenter="setHoveredHeader(header.key)"
                        @mouseleave="clearHoveredHeader()"
                      >
                        <div class="header-content-wrapper">
                          <!-- 標題文字 -->
                          <span
                            v-if="!isHeaderHovered(header.key) || (isHeaderHovered(header.key) && sortBy !== header.key)"
                            class="header-text"
                          >{{ header.title }}</span>

                          <!-- 排序圖標容器 -->
                          <div
                            v-if="header.sortable !== false && isHeaderHovered(header.key)"
                            class="sort-icon-container"
                          >
                            <v-icon
                              size="small"
                              :icon="sortBy === header.key && sortDesc ? 'mdi-arrow-down' : 'mdi-arrow-up'"
                              :class="[
                                'sort-icon',
                                { 'active': sortBy === header.key }
                              ]"
                            />
                          </div>
                        </div>
                      </th>
                    </tr>
                  </template>

                  <!-- 模組名稱欄位 -->
                  <template #[`item.moduleName`]="{ item }">
                    <div
                      class="editable-cell"
                      @click="editCell(item, 'moduleName', $event)"
                    >
                      {{ item.raw.moduleName }}
                    </div>
                  </template>

                  <!-- 物料名稱欄位 -->
                  <template #[`item.materialName`]="{ item }">
                    <div
                      class="editable-cell"
                      @click="editCell(item, 'materialName', $event)"
                    >
                      {{ item.raw.materialName }}
                    </div>
                  </template>

                  <!-- 口徑欄位 -->
                  <template #[`item.diameter1`]="{ item }">
                    <div
                      class="editable-cell"
                      @click="editCell(item, 'diameter1', $event)"
                    >
                      {{ getDiameterDisplay(item.raw.diameter1_id) || item.raw.diameter1 }}
                    </div>
                  </template>

                  <template #[`item.diameter2`]="{ item }">
                    <div
                      class="editable-cell"
                      @click="editCell(item, 'diameter2', $event)"
                    >
                      {{ getDiameterDisplay(item.raw.diameter2_id) || item.raw.diameter2 }}
                    </div>
                  </template>

                  <template #[`item.diameter3`]="{ item }">
                    <div
                      class="editable-cell"
                      @click="editCell(item, 'diameter3', $event)"
                    >
                      {{ getDiameterDisplay(item.raw.diameter3_id) || item.raw.diameter3 }}
                    </div>
                  </template>

                  <!-- 材質欄位 -->
                  <template #[`item.material`]="{ item }">
                    <div
                      class="editable-cell"
                      @click="editCell(item, 'material', $event)"
                    >
                      {{ item.raw.material }}
                    </div>
                  </template>

                  <!-- 長度欄位 -->
                  <template #[`item.length`]="{ item }">
                    <div
                      class="editable-cell"
                      @click="editCell(item, 'length', $event)"
                    >
                      {{ item.raw.length }}
                    </div>
                  </template>

                  <!-- 品項單位欄位 -->
                  <template #[`item.unit`]="{ item }">
                    <div
                      class="editable-cell"
                      @click="editCell(item, 'unit', $event)"
                    >
                      {{ item.raw.unit }}
                    </div>
                  </template>

                  <!-- 目前單價欄位 -->
                  <template #[`item.currentPrice`]="{ item }">
                    <div class="d-flex align-center">
                      <v-chip
                        title="歷史單價"
                        append-icon="mdi-history"
                        size="normal"
                        color="amber-darken-2"
                        variant="text"
                        class="ml-2"
                        @click="showPriceHistory(item.raw)"
                      >
                        {{ item.raw.currentPrice }} 元
                      </v-chip>
                    </div>
                  </template>

                  <!-- 狀態欄位 -->
                  <template #[`item.status`]="{ item }">
                    <div
                      class="editable-cell d-flex justify-center align-center"
                      @click="editCell(item, 'status', $event)"
                    >
                      <v-chip
                        :color="getStatusColor(item.raw.status)"
                        variant="flat"
                        size="small"
                        label
                        class="font-weight-medium"
                        style="cursor: pointer;"
                      >
                        {{
                          typeof item.raw.status === 'boolean'
                            ? (item.raw.status ? '啟用' : '停用')
                            : item.raw.status
                        }}
                      </v-chip>
                    </div>
                  </template>

                  <!-- 操作按鈕 -->
                  <template #[`item.actions`]="{ item }">
                    <div class="ma-0 pa-0 d-flex gap-2 justify-end">
                      <v-btn
                        title="刪除材料"
                        icon="mdi-delete"
                        size="small"
                        color="error"
                        variant="text"
                        @click="deleteItem(item.raw.id)"
                      />
                    </div>
                  </template>

                  <!-- 表格底部分頁與合計 -->
                  <template #bottom>
                    <div class="d-flex align-center pa-3">
                      <span class="text-body-2 text-medium-emphasis">
                        共 {{ store.totalPipeFittings }} 筆資料 (已載入 {{ store.pipeFittings.length }})
                      </span>
                      <v-spacer />
                      <div
                        v-if="isLoadingMoreFromStore"
                        class="text-center"
                      >
                        <v-progress-circular
                          indeterminate
                          size="24"
                          color="#3ea0a3"
                        />
                        <span class="ml-2 text-body-2 text-medium-emphasis">載入更多...</span>
                      </div>
                    </div>
                  </template>
                </v-data-table-virtual>
              </v-card>

              <!-- 提示說明 -->
              <div class="d-flex align-center mt-4">
                <v-icon
                  icon="mdi-information-outline"
                  color="#3ea0a3"
                  class="me-2"
                  size="small"
                />
                <span class="text-caption text-medium-emphasis">
                  點擊欄位可觸發編輯對話框，點擊「歷史單價」按鈕可查看或編輯價格歷史記錄，「刪除」按鈕將永久移除該材料資料
                </span>
              </div>
            </v-card-text>
          </v-card>
        </div>
      </v-col>
    </v-row>

    <!-- 單欄位編輯對話框 -->
    <v-dialog v-model="cellEditDialog" :activator="activator" max-width="500px">
      <v-confirm-edit
        ref="confirm"
        v-model="cellEditModel"
        :title="cellEditDialogTitle"
        ok-text="儲存"
        cancel-text="取消"
        @cancel="cellEditDialog = false"
        @save="saveCellEdit"
      >
        <template v-slot:default="{ model: proxyModel, actions }">
          <v-card :title="cellEditDialogTitle" class="rounded-lg">
            <v-card-text>
              <!-- 模組名稱 -->
              <v-select
                v-if="editingField === 'moduleName'"
                v-model="proxyModel.value.moduleName"
                :items="dynamicModuleOptions"
                :loading="pfModulesStore.isLoading"
                label="模組名稱"
                density="comfortable"
                variant="outlined"
                item-title="title"
                item-value="value"
                class="mb-2"
              />

              <!-- 物料名稱 -->
              <v-text-field
                v-if="editingField === 'materialName'"
                v-model="proxyModel.value.materialName"
                label="物料名稱"
                density="comfortable"
                variant="outlined"
                class="mb-2"
              />

              <!-- 口徑欄位 -->
              <v-select
                v-if="editingField === 'diameter1'"
                v-model="proxyModel.value.diameter1"
                :items="diameter1Options"
                :loading="pfDiametersStore.isLoading"
                label="口徑1"
                density="comfortable"
                variant="outlined"
                item-title="title"
                item-value="value"
                class="mb-2"
              />

              <v-select
                v-if="editingField === 'diameter2'"
                v-model="proxyModel.value.diameter2"
                :items="diameter2Options"
                :loading="pfDiametersStore.isLoading"
                label="口徑2"
                density="comfortable"
                variant="outlined"
                item-title="title"
                item-value="value"
                class="mb-2"
              />

              <v-select
                v-if="editingField === 'diameter3'"
                v-model="proxyModel.value.diameter3"
                :items="diameter3Options"
                :loading="pfDiametersStore.isLoading"
                label="口徑3"
                density="comfortable"
                variant="outlined"
                item-title="title"
                item-value="value"
                class="mb-2"
              />

              <!-- 材質 -->
              <v-select
                v-if="editingField === 'material'"
                v-model="proxyModel.value.material"
                :items="materialOptions"
                :loading="pfMaterialsStore.isLoading"
                label="材質"
                density="comfortable"
                variant="outlined"
                item-title="title"
                item-value="value"
                class="mb-2"
              />

              <!-- 長度 -->
              <v-text-field
                v-if="editingField === 'length'"
                v-model="proxyModel.value.length"
                label="長度(m)"
                type="number"
                density="comfortable"
                variant="outlined"
                class="mb-2"
              />

              <!-- 品項單位 -->
              <v-text-field
                v-if="editingField === 'unit'"
                v-model="proxyModel.value.unit"
                label="品項單位"
                density="comfortable"
                variant="outlined"
                class="mb-2"
              />

              <!-- 狀態 -->
              <v-select
                v-if="editingField === 'status'"
                v-model="proxyModel.value.status"
                :items="[
                  { title: '啟用', value: true },
                  { title: '停用', value: false }
                ]"
                label="狀態"
                density="comfortable"
                variant="outlined"
                item-title="title"
                item-value="value"
                class="mb-2"
              />
            </v-card-text>

            <template v-slot:actions>
              <v-spacer />
              <component :is="actions" />
            </template>
          </v-card>
        </template>
      </v-confirm-edit>
    </v-dialog>

    <!-- 歷史價格對話框 -->
    <v-dialog
      v-model="priceDialog"
      max-width="500px"
    >
      <v-card class="rounded-lg">
        <v-card-title class="text-h5 bg-teal-lighten-1">
          <span>材料歷史單價</span>
          <v-spacer />
          <v-icon @click="priceDialog = false">
            mdi-close
          </v-icon>
        </v-card-title>

        <v-card-text class="pa-4">
          <div
            v-if="currentMaterial"
            class="mb-4"
          >
            <div class="d-flex align-center mb-3">
              <span class="text-subtitle-1 font-weight-bold">{{ currentMaterial.moduleName }} - {{ currentMaterial.materialName }}</span>
              <v-spacer />
              <span class="text-subtitle-2 text-medium-emphasis">編號: {{ currentMaterial.id }}</span>
            </div>

            <!-- 添加新價格 -->
            <v-row>
              <v-col cols="5">
                <v-select
                  v-model="editingPriceYear"
                  :items="yearOptions"
                  label="年度"
                  density="comfortable"
                  variant="outlined"
                  hide-details
                  class="mb-2"
                />
              </v-col>
              <v-col cols="5">
                <v-text-field
                  v-model.number="editingPrice"
                  label="單價"
                  type="number"
                  density="comfortable"
                  variant="outlined"
                  hide-details
                  suffix="元"
                  class="mb-2"
                />
              </v-col>
              <v-col cols="2">
                <v-btn
                  color="#3ea0a3"
                  variant="elevated"
                  size="small"
                  class="mt-2"
                  :disabled="!editingPriceYear || !editingPrice"
                  @click="addPriceHistory"
                >
                  新增
                </v-btn>
              </v-col>
            </v-row>

            <!-- 價格歷史表格 -->
            <v-table
              density="compact"
              class="mt-4 price-history-table"
            >
              <thead>
                <tr>
                  <th>年度</th>
                  <th class="text-right">單價 (元)</th>
                  <th class="text-center">操作</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(price, index) in currentMaterial.priceHistory" :key="price.id">
                  <td>{{ price.year }} 年</td>
                  <td class="text-right">
                    <span v-if="editingPriceIndex !== index">{{ price.price }}</span>
                    <v-text-field
                      v-else
                      v-model.number="editingPrice"
                      type="number"
                      density="compact"
                      variant="outlined"
                      hide-details
                      suffix="元"
                      class="pa-0 ma-0"
                      style="width: 100px"
                      autofocus
                      @blur="updatePrice(index)"
                      @keyup.enter="updatePrice(index)"
                    />
                  </td>
                  <td class="text-center">
                    <div class="d-flex justify-center">
                      <v-btn
                        v-if="editingPriceIndex !== index"
                        title="修改價格"
                        class="mr-1"
                        icon="mdi-pencil"
                        size="x-small"
                        color="#3ea0a3"
                        variant="text"
                        @click="startEditPrice(index)"
                      />
                      <v-btn
                        title="刪除價格"
                        icon="mdi-delete"
                        size="x-small"
                        color="error"
                        variant="text"
                        @click="deletePriceHistory(price.year)"
                      />
                    </div>
                  </td>
                </tr>
                <tr v-if="!currentMaterial.priceHistory || currentMaterial.priceHistory.length === 0">
                  <td
                    colspan="3"
                    class="text-center text-medium-emphasis"
                  >
                    尚無歷史價格資料
                  </td>
                </tr>
              </tbody>
            </v-table>
          </div>
        </v-card-text>

        <v-card-actions>
          <v-spacer />
          <v-btn
            color="#3ea0a3"
            variant="text"
            @click="priceDialog = false"
          >
            關閉
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- 編輯材料對話框 -->
    <v-dialog v-model="editDialog" max-width="500px">
      <v-card class="rounded-lg">
        <v-card-title class="text-h5 bg-teal-lighten-1">
          <span>{{ editedItem.id ? '編輯材料' : '新增材料' }}</span>
          <v-spacer />
          <v-icon @click="editDialog = false">mdi-close</v-icon>
        </v-card-title>

        <v-card-text class="pa-4">
          <v-container>
            <v-row>
              <v-col cols="12" md="6">
                <v-select
                  v-model="editedItem.moduleName"
                  :items="dynamicModuleOptions"
                  label="模組名稱"
                  required
                  density="comfortable"
                  variant="outlined"
                />
              </v-col>
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="editedItem.materialName"
                  label="物料名稱"
                  density="comfortable"
                  variant="outlined"
                />
              </v-col>
              <v-col cols="12" md="4">
                <v-select
                  v-model="editedItem.diameter1"
                  :items="diameter1Options"
                  :loading="pfDiametersStore.isLoading"
                  label="口徑1"
                  density="comfortable"
                  variant="outlined"
                  item-title="title"
                  item-value="value"
                />
              </v-col>
              <v-col cols="12" md="4">
                <v-select
                  v-model="editedItem.diameter2"
                  :items="diameter2Options"
                  :loading="pfDiametersStore.isLoading"
                  label="口徑2"
                  density="comfortable"
                  variant="outlined"
                  item-title="title"
                  item-value="value"
                />
              </v-col>
              <v-col cols="12" md="4">
                <v-select
                  v-model="editedItem.diameter3"
                  :items="diameter3Options"
                  :loading="pfDiametersStore.isLoading"
                  label="口徑3"
                  density="comfortable"
                  variant="outlined"
                  item-title="title"
                  item-value="value"
                />
              </v-col>
              <v-col cols="12" md="4">
                <v-select
                  v-model="editedItem.material"
                  :items="materialOptions"
                  :loading="pfMaterialsStore.isLoading"
                  label="材質"
                  required
                  density="comfortable"
                  variant="outlined"
                />
              </v-col>
              <v-col cols="12" md="4">
                <v-text-field
                  v-model="editedItem.length"
                  label="長度(m)"
                  type="number"
                  density="comfortable"
                  variant="outlined"
                />
              </v-col>
              <v-col cols="12" md="4">
                <v-text-field
                  v-model="editedItem.unit"
                  label="品項單位"
                  required
                  density="comfortable"
                  variant="outlined"
                />
              </v-col>
              <v-col cols="12" md="4">
                <v-text-field
                  v-model.number="editedItem.currentPrice"
                  label="目前單價"
                  type="number"
                  required
                  density="comfortable"
                  variant="outlined"
                  suffix="元"
                />
              </v-col>
              <v-col cols="12" md="4">
                <v-select
                  v-model="editedItem.status"
                  :items="['啟用', '停用']"
                  label="狀態"
                  required
                  density="comfortable"
                  variant="outlined"
                />
              </v-col>
              <v-col cols="12">
                <v-textarea
                  v-model="editedItem.note"
                  label="備註"
                  density="comfortable"
                  variant="outlined"
                  rows="2"
                />
              </v-col>
            </v-row>
          </v-container>
        </v-card-text>

        <v-card-actions>
          <v-spacer />
          <v-btn color="grey" variant="text" @click="editDialog = false">
            取消
          </v-btn>
          <v-btn color="#3ea0a3" variant="elevated" @click="saveItem">
            儲存
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script lang="ts" setup>
import { useDisplay } from 'vuetify'
import { usePipeFittingsStore } from '@/stores/pipeFittingsStore'
import { usePFModulesStore } from '@/stores/pfModulesStore'
import { useUserStore } from '@/stores/users'
import { usePFAnnualPricesStore } from '@/stores/pfAnnualPricesStore'
import { usePFMaterialsStore } from '@/stores/pfMaterialsStore'
import { usePFDiametersStore } from '@/stores/pfDiametersStore'
import type { PFMaterial } from '@/types/pfMaterials'
import type { PFDiameter } from '@/types/pfDiameters'
import type { PFAnnualPrice } from '@/types/pfAnnualPrices'

const store = usePipeFittingsStore()
const pfModulesStore = usePFModulesStore()
const userStore = useUserStore()
const annualPricesStore = usePFAnnualPricesStore()
const pfMaterialsStore = usePFMaterialsStore()
const pfDiametersStore = usePFDiametersStore()

const tableRef = ref<any>(null)
let scrollableElement: HTMLElement | null = null
const SCROLL_THRESHOLD = 150

const fittings = computed(() => store.pipeFittings)
const currentFitting = computed(() => store.currentPipeFitting)
const error = computed(() => store.error)
const isLoadingInitial = computed(() => store.isLoading && !store.isLoadingMore)
const isLoadingMoreFromStore = computed(() => store.isLoadingMore)

const canLoadMoreItems = computed(() => {
  return !store.isLoadingMore && store.pipeFittings.length < store.totalPipeFittings
})

// 排序相關
const search = ref('')
const sortBy = ref('')
const sortDesc = ref(false)
const hoveredHeaderKey = ref<string | null>(null)
const selectedModule = ref<number | null>(null)
const selectedMaterial = ref(null)

// 單欄位編輯對話框相關
const cellEditDialog = ref(false)
const activator = ref(null)
const confirm = ref(null)
const cellEditModel = ref({
  moduleName: '',
  materialName: '',
  diameter1: '',
  diameter2: '',
  diameter3: '',
  material: '',
  length: '',
  unit: '',
  status: true,
})
const selectedItemId = ref('')
const editingField = ref<string | null>(null)

// 歷史價格對話框
const priceDialog = ref(false)
const currentMaterial = ref<{
  id: string
  moduleName: string
  materialName: string
  rawFitting: any
  priceHistory: PFAnnualPrice[]
} | null>(null)
const editingPriceYear = ref<number | null>(null)
const editingPrice = ref<number | null>(null)
const editingPriceIndex = ref<number | null>(null)

// 年度選項
const currentYear = new Date().getFullYear() - 1911
const yearOptions = Array.from({ length: 5 }, (_, i) => {
  const year = currentYear - i
  return { title: `${year}年`, value: year }
})

// 編輯對話框
const editDialog = ref(false)
const editedItem = reactive({
  id: '',
  moduleName: '',
  materialName: '',
  diameter1: '',
  diameter2: '',
  diameter3: '',
  material: '',
  length: '',
  unit: '',
  currentPrice: 0,
  status: '啟用',
  priceHistory: [] as { year: number, price: number }[],
  note: ''
})
const defaultItem = {
  id: '',
  moduleName: '',
  materialName: '',
  diameter1: '',
  diameter2: '',
  diameter3: '',
  material: '',
  length: '',
  unit: '',
  currentPrice: 0,
  status: '啟用',
  priceHistory: [] as { year: number, price: number }[],
  note: ''
}

// Mapped and prepared items for the table from the store's fittings
const mappedPipeFittings = computed(() => {
  return fittings.value.map(fitting => {
    return {
      id: fitting.pomno,
      pomno: fitting.pomno,
      moduleId: fitting.module_id,
      moduleName: fitting.module?.name || `模組 (ID: ${fitting.module_id})`,
      materialName: fitting.name || `物料 (POMNO: ${fitting.pomno})`,
      diameter1: fitting.diameter1?.value || fitting.diameter1_id?.toString() || '',
      diameter2: fitting.diameter2?.value || fitting.diameter2_id?.toString() || '',
      diameter3: fitting.diameter3?.value || '',
      material: fitting.material?.name || `材質 (ID: ${fitting.material_id})`,
      length: fitting.length ?? '',
      unit: fitting.unit || '個',
      currentPrice: fitting.current_price || 0,
      status: fitting.is_active,
      priceHistory: fitting.price_history || [],
      note: fitting.description || '',
      rawFitting: fitting,
    }
  })
})

// 模組名稱選項
const dynamicModuleOptions = computed(() => {
  if (!pfModulesStore.allModules) {
    return [];
  }
  return pfModulesStore.allModules.map(module => ({
    title: module.name,
    value: module.id,
  }));
});

// 動態獲取的材質選項
const dynamicMaterialOptions = computed(() => {
  if (!pfMaterialsStore.materials) {
    return [];
  }
  return pfMaterialsStore.materials.map(material => ({
    title: material.name,
    value: material.name,
  }));
});

// 動態獲取的口徑選項
const diameter1Options = computed(() => {
  if (!pfDiametersStore.diameters) {
    return [];
  }
  return pfDiametersStore.diameters.map(diameter => ({
    title: `${diameter.name} (${diameter.value})`,
    value: diameter.id,
  }));
});

const diameter2Options = computed(() => diameter1Options.value);
const diameter3Options = computed(() => diameter1Options.value);

// 物料類型選項
const materialOptions = computed(() => {
  if (pfMaterialsStore.hasMaterials) {
    return dynamicMaterialOptions.value;
  }

  return [
    { title: '過濾器', value: '過濾器' },
    { title: '閥門', value: '閥門' },
    { title: 'PE管', value: 'PE管' },
    { title: 'PVC管', value: 'PVC管' },
    { title: '接頭', value: '接頭' },
    { title: '滴頭', value: '滴頭' },
    { title: '噴頭', value: '噴頭' }
  ];
});

const getDiameterDisplay = (diameterId: number | null) => {
  if (!diameterId) return '';
  const diameter = pfDiametersStore.getDiameterById(diameterId);
  return diameter ? `${diameter.name} (${diameter.value})` : '';
};

// 新表頭
const headers = ref<{ title: string; key: string; align?: 'center' | 'end' | 'start'; width?: string }[]>([
  { title: '項次', key: 'index', align: 'center', width: '60px' },
  { title: '模組名稱', key: 'moduleName', align: 'center' },
  { title: '物料名稱', key: 'materialName', align: 'center' },
  { title: '口徑1', key: 'diameter1', align: 'center' },
  { title: '口徑2', key: 'diameter2', align: 'center' },
  { title: '口徑3', key: 'diameter3', align: 'center' },
  { title: '材質', key: 'material', align: 'center' },
  { title: '長度(m)', key: 'length', align: 'center' },
  { title: '品項單位', key: 'unit', align: 'center' },
  { title: '目前單價', key: 'currentPrice', align: 'center' },
  { title: '狀態', key: 'status', align: 'center' },
  { title: '操作', key: 'actions', align: 'center' },
])

const { name } = useDisplay()
const isSmallScreen = computed(() => name.value === 'xs' || name.value === 'sm')

// 根據材料狀態返回對應的顏色
const getStatusColor = (isActive: boolean | string) => {
  if (typeof isActive === 'string') {
    if (isActive === '啟用') return 'light-green-lighten-5';
    if (isActive === '停用') return 'error-lighten-5';
    return 'grey-lighten-4';
  }
  return isActive ? 'light-green-lighten-5' : 'error-lighten-5';
}

// 檢查特定標頭是否懸停
const isHeaderHovered = (key: string) => {
  return hoveredHeaderKey.value === key;
};

// 設定懸停的標頭
const setHoveredHeader = (key: string) => {
  const headerConfig = headers.value.find(h => h.key === key);
  if (headerConfig && headerConfig.sortable !== false) {
    hoveredHeaderKey.value = key;
  }
};

// 清除懸停的標頭
const clearHoveredHeader = () => {
  hoveredHeaderKey.value = null;
};

// 更新排序方法
const updateSorting = (key: string) => {
  if (sortBy.value === key) {
    sortDesc.value = !sortDesc.value;
  } else {
    sortBy.value = key;
    sortDesc.value = false;
  }
};

// 過濾資料
const filteredItems = computed(() => {
  let result = mappedPipeFittings.value;

  if (selectedModule.value !== null) {
    result = result.filter(item => item.moduleId === selectedModule.value);
  }

  if (selectedMaterial.value) {
    result = result.filter(item => item.material === selectedMaterial.value);
  }

  if (search.value) {
    const searchTerm = search.value.toLowerCase();
    result = result.filter(item => {
      return Object.values(item).some(val =>
        String(val).toLowerCase().includes(searchTerm)
      );
    });
  }
  return result;
})

// 添加項次序號到項目
const indexedItems = computed(() => {
  let itemsToProcess = [...filteredItems.value];
  if (sortBy.value) {
    itemsToProcess.sort((a, b) => {
      let valueA = a[sortBy.value];
      let valueB = b[sortBy.value];
      const numericKeys = ['currentPrice', 'length', 'id', 'pomno'];
      if (numericKeys.includes(sortBy.value)) {
        valueA = parseFloat(String(valueA).replace(/[^0-9.-]+/g,"")) || 0;
        valueB = parseFloat(String(valueB).replace(/[^0-9.-]+/g,"")) || 0;
      } else {
        valueA = String(valueA || '').toLowerCase();
        valueB = String(valueB || '').toLowerCase();
      }
      if (valueA < valueB) return sortDesc.value ? 1 : -1;
      if (valueA > valueB) return sortDesc.value ? -1 : 1;
      return 0;
    });
  }
  return itemsToProcess.map((item, globalIndex) => ({
    ...item,
    index: globalIndex + 1,
    raw: item,
  }));
});

// 單欄位編輯對話框相關函數
const cellEditDialogTitle = computed(() => {
  if (!selectedItemId.value) return '編輯資料'
  const item = mappedPipeFittings.value.find(i => i.id === selectedItemId.value)
  const itemName = item ? `${item.moduleName} - ${item.materialName}` : ''

  const fieldLabels = {
    moduleName: '模組名稱',
    materialName: '物料名稱',
    diameter1: '口徑1',
    diameter2: '口徑2',
    diameter3: '口徑3',
    material: '材質',
    length: '長度',
    unit: '品項單位',
    status: '狀態'
  }

  const fieldLabel = fieldLabels[editingField.value] || editingField.value
  return `編輯 "${itemName}" 的${fieldLabel}`
})

// 註冊當前點擊的儲存格作為 dialog 的觸發器
function registerActivator(event) {
  activator.value = event.currentTarget
}

// 選取並載入要編輯的數據 (由儲存格點擊觸發)
function editCell(item, field, event) {
  registerActivator(event)
  selectedItemId.value = item.id
  editingField.value = field

  // 載入項目數據到 cellEditModel
  const itemData = item.raw

  // 根據不同欄位設定對應的值
  if (field === 'moduleName') {
    cellEditModel.value.moduleName = itemData.moduleId || itemData.moduleName
  } else if (field === 'materialName') {
    cellEditModel.value.materialName = itemData.materialName
  } else if (field === 'diameter1') {
    cellEditModel.value.diameter1 = itemData.rawFitting.diameter1_id || itemData.diameter1
  } else if (field === 'diameter2') {
    cellEditModel.value.diameter2 = itemData.rawFitting.diameter2_id || itemData.diameter2
  } else if (field === 'diameter3') {
    cellEditModel.value.diameter3 = itemData.rawFitting.diameter3_id || itemData.diameter3
  } else if (field === 'material') {
    cellEditModel.value.material = itemData.material
  } else if (field === 'length') {
    cellEditModel.value.length = itemData.length
  } else if (field === 'unit') {
    cellEditModel.value.unit = itemData.unit
  } else if (field === 'status') {
    cellEditModel.value.status = itemData.rawFitting.is_active
  }

  cellEditDialog.value = true
}

// 儲存單欄位編輯
async function saveCellEdit() {
  cellEditDialog.value = false

  if (!selectedItemId.value || !editingField.value) return

  const originalFitting = fittings.value.find(f => f.pomno === selectedItemId.value);
  if (!originalFitting) return;

  const valueToSave = cellEditModel.value[editingField.value];
  const updateData: any = {};

  try {
    if (editingField.value === 'status') {
      updateData.is_active = valueToSave;
    } else if (editingField.value === 'moduleName') {
      const selectedModule = pfModulesStore.allModules.find(m => m.id === valueToSave);
      if (selectedModule) {
        updateData.module_id = selectedModule.id;
      }
    } else if (editingField.value === 'materialName') {
      updateData.name = valueToSave;
    } else if (editingField.value === 'material') {
      const selectedMaterial = pfMaterialsStore.materials.find(m => m.name === valueToSave);
      if (selectedMaterial) {
        updateData.material_id = selectedMaterial.id;
      }
    } else if (['diameter1', 'diameter2', 'diameter3'].includes(editingField.value)) {
      const idField = `${editingField.value}_id`;
      updateData[idField] = valueToSave;
    } else {
      updateData[editingField.value] = valueToSave;
    }

    if (Object.keys(updateData).length > 0) {
      await store.updatePipeFitting(selectedItemId.value, updateData);
    }
  } catch (error) {
    console.error('Failed to save cell:', error);
  }

  editingField.value = null;
}

// 無限滾動相關函數
const handleTableScroll = () => {
  if (!scrollableElement || !canLoadMoreItems.value || isLoadingMoreFromStore.value) return;

  const { scrollTop, clientHeight, scrollHeight } = scrollableElement;
  if (scrollHeight - scrollTop - clientHeight < SCROLL_THRESHOLD) {
    loadMorePipeFittings();
  }
};

const loadMorePipeFittings = async () => {
  console.log(`[VUE LOADMORE] Attempting to load more. CanLoad: ${canLoadMoreItems.value}, IsLoadingMore: ${isLoadingMoreFromStore.value}`);
  if (!canLoadMoreItems.value) {
    return;
  }

  const currentLoadedCount = store.pipeFittings.length;
  const userOfficeId = 99;
  const itemsToFetchPerPage = 50;
  console.log(`[VUE LOADMORE] Calling store action with: skip=${currentLoadedCount}, limit=${itemsToFetchPerPage}, append=true`);

  await store.fetchPipeFittingsByOfficeId(userOfficeId, {
    skip: currentLoadedCount,
    limit: itemsToFetchPerPage,
    append: true,
  });
};

const deleteItem = (itemId: string) => {
  if (confirm(`確定要刪除編號 ${itemId} 的材料嗎？`)) {
    try {
      console.log('刪除材料:', itemId)
    } catch (error) {
      console.error('刪除材料失敗:', error)
    }
  }
}

// 顯示歷史價格對話框
const showPriceHistory = (item: any) => {
  currentMaterial.value = item;
  priceDialog.value = true;
  editingPriceIndex.value = null;
  editingPriceYear.value = null;
  editingPrice.value = null;
}

// 開始編輯某個價格
const startEditPrice = (index: number) => {
  editingPriceIndex.value = index
  editingPrice.value = currentMaterial.value.priceHistory[index].price
}

// 更新價格
const updatePrice = async (index: number) => {
  if (currentMaterial.value && editingPrice.value !== null && editingPrice.value > 0) {
    try {
      const priceRecord = currentMaterial.value.priceHistory[index];
      const updatedPrice = await annualPricesStore.updateAnnualPrice(
        priceRecord.id,
        {
          price: editingPrice.value,
          modified_by_id: userStore.currentUser?.id
        }
      );

      currentMaterial.value.priceHistory[index] = updatedPrice;

      const maxYear = Math.max(...currentMaterial.value.priceHistory.map(p => p.year));
      if (priceRecord.year === maxYear) {
        const materialIndex = indexedItems.value.findIndex(item => item.raw.id === currentMaterial.value?.id);
        if (materialIndex !== -1) {
          indexedItems.value[materialIndex].raw.currentPrice = editingPrice.value;
        }
      }
    } catch (error) {
      console.error('更新價格失敗:', error);
    }
  }

  editingPriceIndex.value = null;
  editingPrice.value = null;
}

// 新增歷史價格
const addPriceHistory = async () => {
  if (currentMaterial.value && editingPriceYear.value && editingPrice.value) {
    try {
      const userOfficeId = userStore.currentUser?.office?.id;
      const newPrice = await annualPricesStore.createAnnualPrice({
        pipe_fitting_id: Number(currentMaterial.value.id),
        office_id: userOfficeId,
        year: editingPriceYear.value,
        price: editingPrice.value,
        is_active: true,
        created_by_id: userStore.currentUser?.id
      });

      if (currentMaterial.value) {
        if (!currentMaterial.value.priceHistory) {
          currentMaterial.value.priceHistory = [];
        }

        currentMaterial.value.priceHistory.push(newPrice);
        currentMaterial.value.priceHistory.sort((a, b) => b.year - a.year);
      }

      const index = indexedItems.value.findIndex(item => item.raw.id === currentMaterial.value.id);
      if (index !== -1 &&
          (!indexedItems.value[index].raw.currentPrice ||
           editingPriceYear.value >= Math.max(...currentMaterial.value.priceHistory.map(p => p.year)))) {
        indexedItems.value[index].raw.currentPrice = editingPrice.value;
      }

      editingPriceYear.value = null;
      editingPrice.value = null;
    } catch (error) {
      console.error('新增價格歷史失敗:', error);
    }
  }
}

// 刪除歷史價格
const deletePriceHistory = async (year: number) => {
  if (currentMaterial.value) {
    try {
      const priceIndex = currentMaterial.value.priceHistory.findIndex(p => p.year === year);
      if (priceIndex === -1) return;

      const priceId = currentMaterial.value.priceHistory[priceIndex].id;

      await annualPricesStore.deleteAnnualPrice(
        priceId,
        Number(currentMaterial.value.id)
      );

      currentMaterial.value.priceHistory.splice(priceIndex, 1);

      if (currentMaterial.value.priceHistory.length > 0) {
        const latestYear = Math.max(...currentMaterial.value.priceHistory.map(p => p.year));
        const latestPrice = currentMaterial.value.priceHistory.find(p => p.year === latestYear)?.price;

        if (latestPrice) {
          const materialIndex = indexedItems.value.findIndex(item => item.raw.id === currentMaterial.value?.id);
          if (materialIndex !== -1) {
            indexedItems.value[materialIndex].raw.currentPrice = latestPrice;
          }
        }
      }
    } catch (error) {
      console.error('刪除價格歷史失敗:', error);
    }
  }
}

// 保存編輯的材料
const saveItem = async () => {
  try {
    const saveData: any = { ...editedItem };

    if (typeof saveData.moduleName === 'string') {
      const module = pfModulesStore.allModules.find(m => m.name === saveData.moduleName);
      if (module) {
        saveData.module_id = module.id;
      }
    } else {
      saveData.module_id = saveData.moduleName;
    }
    delete saveData.moduleName;

    saveData.name = saveData.materialName;
    delete saveData.materialName;

    if (typeof saveData.material === 'string') {
      const material = pfMaterialsStore.materials.find(m => m.name === saveData.material);
      if (material) {
        saveData.material_id = material.id;
      }
    } else if (typeof saveData.material === 'number') {
      saveData.material_id = saveData.material;
    }
    delete saveData.material;

    ['diameter1', 'diameter2', 'diameter3'].forEach(field => {
      if (saveData[field]) {
        saveData[`${field}_id`] = saveData[field];
        delete saveData[field];
      }
    });

    if (saveData.status) {
      saveData.is_active = saveData.status === '啟用';
      delete saveData.status;
    }

    if (saveData.currentPrice) {
      const priceData = {
        year: new Date().getFullYear() - 1911,
        price: saveData.currentPrice
      };
    }
    delete saveData.currentPrice;

    delete saveData.priceHistory;
    delete saveData.index;
    delete saveData.raw;
    delete saveData.id;

    console.log('準備儲存的資料:', saveData);

    if (editedItem.id) {
      await store.updatePipeFitting(editedItem.id, saveData);
    } else {
      await store.createPipeFitting(saveData);
    }

    const userOfficeId = userStore.currentUser?.office?.id || 99;
    await store.fetchPipeFittingsByOfficeId(userOfficeId, {
      skip: 0,
      limit: 50,
      append: false
    });

    editDialog.value = false;
    Object.assign(editedItem, defaultItem);

  } catch (error) {
    console.error('保存材料時發生錯誤:', error);
  }
}

// 組件掛載時載入資料
onMounted(async () => {
  console.log('Component Mounted: Initializing PipeFittings...');

  const userOfficeId = userStore.currentUser?.office?.id;
  const initialLimit = 50;

  await store.fetchPipeFittingsByOfficeId(userOfficeId, {
    skip: 0,
    limit: initialLimit,
    append: false,
  });

  await pfModulesStore.ensureAllModulesLoaded()
  await pfMaterialsStore.ensureAllMaterialsLoaded()
  await pfDiametersStore.ensureAllDiametersLoaded()

  console.log('Store: Fittings after initial fetch:', fittings.value.length);
  console.log('Store: Total after initial fetch:', store.totalPipeFittings);

  await nextTick();
  if (tableRef.value && tableRef.value.$el) {
    const wrapper = tableRef.value.$el.querySelector('.v-table__wrapper');
    if (wrapper) {
      scrollableElement = wrapper as HTMLElement;
      scrollableElement.addEventListener('scroll', handleTableScroll);
    } else {
      console.warn('Could not find .v-table__wrapper for v-data-table-virtual. Infinite scroll might not work.');
    }
  }

  if (mappedPipeFittings.value.length > 0) {
    const firstItem = mappedPipeFittings.value[0];
    if (firstItem && typeof firstItem.pomno !== 'undefined') {
      await store.fetchPipeFittingById(firstItem.pomno);
    }
  }
})

onBeforeUnmount(() => {
  if (scrollableElement) {
    scrollableElement.removeEventListener('scroll', handleTableScroll);
  }
  annualPricesStore.clearAllPrices();
})
</script>

<style scoped>
/* 添加背景圖片樣式 */
.material-container {
  background-image: url('@/assets/bg_index.svg');
  background-size: cover;
  background-position: center bottom;
  background-repeat: no-repeat;
  background-attachment: fixed;
}

/* 區塊共通容器 */
.section-wrapper {
  padding: 8px 4px 0px 4px;
}

/* 卡片與標題樣式 */
.section-card {
  position: relative;
  margin: 24px 0;
  overflow: visible !important;
  border-top-left-radius: 0 !important;
  transition: all 0.3s ease;

  /* 毛玻璃效果 */
  background-color: rgba(255, 255, 255, 0.6) !important;
  backdrop-filter: blur(10px) !important;
  -webkit-backdrop-filter: blur(10px) !important;
  border: 1px solid rgba(255, 255, 255, 0.25) !important;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.05) !important;
}

.section-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08) !important;
  background-color: rgba(255, 255, 255, 0.85) !important;
}

.section-card:hover .custom-title {
  background-color: #2d8c8f !important;
  box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.08);
}

.custom-title {
  position: absolute;
  top: -50px;
  left: -1px;
  width: auto !important;
  min-width: 130px;
  height: 50px;
  background-color: #3ea0a3 !important;
  border-radius: 8px 8px 0 0;
  z-index: 1;
  transition: all 0.3s ease;
}

.v-card-title {
  color: white !important;
  display: flex;
  justify-content: flex-start;
  align-items: center;
  width: 100%;
  height: 100%;
}

/* 表格區域樣式 */
.table-card {
  border-radius: 12px;
  overflow: hidden;
}

/* 表格樣式 */
.materials-table :deep(thead th) {
  background-color: #62b7bb30 !important;
  color: #333 !important;
  font-weight: 900 !important;
  position: relative;
  text-align: start;
}

.materials-table :deep(thead th.text-center .header-content-wrapper) {
  justify-content: center;
}
.materials-table :deep(thead th.text-end .header-content-wrapper) {
  justify-content: flex-end;
}

.header-content-wrapper {
  display: flex;
  align-items: center;
  width: 100%;
  height: 100%;
  min-height: 24px;
}

.header-text {
  transition: opacity 0.2s ease-in-out;
  flex-grow: 1;
}

.sort-icon-container {
  display: flex;
  align-items: center;
  justify-content: center;
  transition: opacity 0.2s ease-in-out;
  opacity: 0;
  position: absolute;
  left: 50%;
  top: 50%;
  transform: translate(-50%, -50%);
}

.custom-header.sortable-header:hover .sort-icon-container {
  opacity: 1;
}

.custom-header.sortable-header:hover .header-text {
  opacity: 0;
}

.custom-header.sortable-header:hover .sort-icon-container.active,
.custom-header.sortable-header .sort-icon-container.active {
  opacity: 1;
}
.custom-header.sortable-header:hover .header-text:has(+ .sort-icon-container.active) {
   opacity: 0;
}

.sort-icon {
  color: #333;
}

.sort-icon.active {
  color: #3ea0a3 !important;
}

.materials-table :deep(.v-data-table__tr:hover) {
  background-color: rgba(98, 183, 187, 0.1) !important;
}

.materials-table :deep(.v-data-table__tr:nth-child(even)) {
  background-color: rgba(98, 183, 187, 0.05);
}

/* 可編輯單元格樣式 */
.editable-cell {
  padding: 6px 8px;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s ease;
  min-height: 32px;
  display: flex;
  align-items: center;
  text-align: start;
}

.editable-cell:hover {
  background-color: rgba(62, 160, 163, 0.1);
}

/* 按鈕樣式 */
.action-btn {
  background-color: white !important;
  font-weight: 500;
  transition: all 0.2s ease;
}

.action-btn:hover {
  background-color: #3ea0a3 !important;
  color: white !important;
}

/* 篩選區域樣式 */
.filter-select {
  max-width: 200px;
}

@media (max-width: 600px) {
  .filter-select {
    min-width: 100%;
  }
}

/* 歷史價格表格樣式 */
.price-history-table :deep(tbody tr:hover) {
  background-color: rgba(98, 183, 187, 0.1) !important;
}

.price-history-table :deep(thead th) {
  background-color: #62b7bb15 !important;
  color: #333 !important;
  font-weight: 700 !important;
}

.price-history-table :deep(tbody tr:nth-child(even)) {
  background-color: rgba(98, 183, 187, 0.03);
}
</style>
