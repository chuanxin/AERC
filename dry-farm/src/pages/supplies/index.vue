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
                      v-if="editingCell === `${item.id}-moduleName`"
                      class="editing-cell-container"
                    >
                      <v-select
                        v-model="tempEditValue"
                        :items="dynamicModuleOptions"
                        density="compact"
                        variant="outlined"
                        hide-details
                        autofocus
                        class="edit-select"
                        @blur="saveCell(item.id, 'moduleName')"
                        @keyup.enter="saveCell(item.id, 'moduleName')"
                        @keyup.esc="cancelEdit()"
                      />
                    </div>
                    <div
                      v-else
                      class="editable-cell"
                      @click="startCellEdit(item.id, 'moduleName', item.raw.moduleName)"
                    >
                      {{ item.raw.moduleName }}
                    </div>
                  </template>

                  <!-- 物料名稱欄位 -->
                  <template #[`item.materialName`]="{ item }">
                    <div
                      v-if="editingCell === `${item.id}-materialName`"
                      class="editing-cell-container"
                    >
                      <v-select
                        v-model="tempEditValue"
                        :items="materialOptions"
                        density="compact"
                        variant="outlined"
                        hide-details
                        autofocus
                        class="edit-select"
                        @blur="saveCell(item.id, 'materialName')"
                        @keyup.enter="saveCell(item.id, 'materialName')"
                        @keyup.esc="cancelEdit()"
                      />
                    </div>
                    <div
                      v-else
                      class="editable-cell"
                      @click="startCellEdit(item.id, 'materialName', item.raw.materialName)"
                    >
                      {{ item.raw.materialName }}
                    </div>
                  </template>

                  <!-- 口徑欄位 -->
                  <template #[`item.diameter1`]="{ item }">
                    <div
                      v-if="editingCell === `${item.id}-diameter1`"
                      class="editing-cell-container"
                    >
                      <v-text-field
                        v-model="tempEditValue"
                        density="compact"
                        variant="outlined"
                        hide-details
                        autofocus
                        class="edit-field"
                        @blur="saveCell(item.id, 'diameter1')"
                        @keyup.enter="saveCell(item.id, 'diameter1')"
                        @keyup.esc="cancelEdit()"
                      />
                    </div>
                    <div
                      v-else
                      class="editable-cell"
                      @click="startCellEdit(item.id, 'diameter1', item.raw.diameter1)"
                    >
                      {{ item.raw.diameter1 }}
                    </div>
                  </template>

                  <template #[`item.diameter2`]="{ item }">
                    <div
                      v-if="editingCell === `${item.id}-diameter2`"
                      class="editing-cell-container"
                    >
                      <v-text-field
                        v-model="tempEditValue"
                        density="compact"
                        variant="outlined"
                        hide-details
                        autofocus
                        class="edit-field"
                        @blur="saveCell(item.id, 'diameter2')"
                        @keyup.enter="saveCell(item.id, 'diameter2')"
                        @keyup.esc="cancelEdit()"
                      />
                    </div>
                    <div
                      v-else
                      class="editable-cell"
                      @click="startCellEdit(item.id, 'diameter2', item.raw.diameter2)"
                    >
                      {{ item.raw.diameter2 }}
                    </div>
                  </template>

                  <template #[`item.diameter3`]="{ item }">
                    <div
                      v-if="editingCell === `${item.id}-diameter3`"
                      class="editing-cell-container"
                    >
                      <v-text-field
                        v-model="tempEditValue"
                        density="compact"
                        variant="outlined"
                        hide-details
                        autofocus
                        class="edit-field"
                        @blur="saveCell(item.id, 'diameter3')"
                        @keyup.enter="saveCell(item.id, 'diameter3')"
                        @keyup.esc="cancelEdit()"
                      />
                    </div>
                    <div
                      v-else
                      class="editable-cell"
                      @click="startCellEdit(item.id, 'diameter3', item.raw.diameter3)"
                    >
                      {{ item.raw.diameter3 }}
                    </div>
                  </template>

                  <!-- 材質欄位 -->
                  <template #[`item.material`]="{ item }">
                    <div
                      v-if="editingCell === `${item.id}-material`"
                      class="editing-cell-container"
                    >
                      <v-text-field
                        v-model="tempEditValue"
                        density="compact"
                        variant="outlined"
                        hide-details
                        autofocus
                        class="edit-field"
                        @blur="saveCell(item.id, 'material')"
                        @keyup.enter="saveCell(item.id, 'material')"
                        @keyup.esc="cancelEdit()"
                      />
                    </div>
                    <div
                      v-else
                      class="editable-cell"
                      @click="startCellEdit(item.id, 'material', item.raw.material)"
                    >
                      {{ item.raw.material }}
                    </div>
                  </template>

                  <!-- 長度欄位 -->
                  <template #[`item.length`]="{ item }">
                    <div
                      v-if="editingCell === `${item.id}-length`"
                      class="editing-cell-container"
                    >
                      <v-text-field
                        v-model="tempEditValue"
                        type="number"
                        density="compact"
                        variant="outlined"
                        hide-details
                        autofocus
                        class="edit-field"
                        @blur="saveCell(item.id, 'length')"
                        @keyup.enter="saveCell(item.id, 'length')"
                        @keyup.esc="cancelEdit()"
                      />
                    </div>
                    <div
                      v-else
                      class="editable-cell"
                      @click="startCellEdit(item.id, 'length', item.raw.length)"
                    >
                      {{ item.raw.length }}
                    </div>
                  </template>

                  <!-- 品項單位欄位 -->
                  <template #[`item.unit`]="{ item }">
                    <div
                      v-if="editingCell === `${item.id}-unit`"
                      class="editing-cell-container"
                    >
                      <v-text-field
                        v-model="tempEditValue"
                        density="compact"
                        variant="outlined"
                        hide-details
                        autofocus
                        class="edit-field"
                        @blur="saveCell(item.id, 'unit')"
                        @keyup.enter="saveCell(item.id, 'unit')"
                        @keyup.esc="cancelEdit()"
                      />
                    </div>
                    <div
                      v-else
                      class="editable-cell"
                      @click="startCellEdit(item.id, 'unit', item.raw.unit)"
                    >
                      {{ item.raw.unit }}
                    </div>
                  </template>

                  <!-- 目前單價欄位 -->
                  <template #[`item.currentPrice`]="{ item }">
                    <div
                      v-if="editingCell === `${item.id}-currentPrice`"
                      class="editing-cell-container"
                    >
                      <v-text-field
                        v-model.number="tempEditValue"
                        type="number"
                        density="compact"
                        variant="outlined"
                        hide-details
                        autofocus
                        suffix="元"
                        class="edit-field"
                        @blur="saveCell(item.id, 'currentPrice')"
                        @keyup.enter="saveCell(item.id, 'currentPrice')"
                        @keyup.esc="cancelEdit()"
                      />
                    </div>
                    <div class="d-flex align-center">
                      <div
                        class="editable-cell text-right"
                        @click="startCellEdit(item.id, 'currentPrice', item.raw.currentPrice)"
                      >
                        {{ item.raw.currentPrice }} 元
                      </div>
                      <v-btn
                        title="歷史單價"
                        icon="mdi-history"
                        size="x-small"
                        color="amber-darken-2"
                        variant="text"
                        class="ml-2"
                        @click="showPriceHistory(item.raw)"
                      />
                    </div>
                  </template>

                  <!-- 狀態欄位 -->
                  <template #[`item.status`]="{ item }">
                    <div
                      class="editable-cell d-flex justify-center align-center"
                      @click="!editingCell ? startCellEdit(item.id, 'status', item.raw.status) : null"
                    >
                      <v-chip
                        :color="getStatusColor(editingCell === `${item.id}-status` ? tempEditValue : item.raw.status)"
                        variant="flat"
                        size="small"
                        label
                        class="font-weight-medium"
                        style="cursor: pointer;"
                        @click.stop="editingCell === `${item.id}-status` ? toggleAndSaveStatus(item.id) : startCellEdit(item.id, 'status', item.raw.status)"
                      >
                        {{
                          typeof (editingCell === `${item.id}-status` ? tempEditValue : item.raw.status) === 'boolean'
                            ? ((editingCell === `${item.id}-status` ? tempEditValue : item.raw.status) ? '啟用' : '停用')
                            : (editingCell === `${item.id}-status` ? tempEditValue : item.raw.status)
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
                      <!-- <v-pagination
                        v-model="page"
                        :length="Math.ceil(filteredItems.length / itemsPerPage)"
                        :total-visible="5"
                        density="comfortable"
                        color="#3ea0a3"
                      /> -->
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
                  點擊欄位可直接編輯內容，點擊「歷史單價」按鈕可查看或編輯價格歷史記錄，「刪除」按鈕將永久移除該材料資料
                </span>
              </div>
            </v-card-text>
          </v-card>
        </div>
      </v-col>
    </v-row>

    <!-- 歷史價格對話框 -->
    <v-dialog
      v-model="priceDialog"
      max-width="500px"
    >
      <v-card>
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
                <tr v-for="(price, index) in currentMaterial.priceHistory" :key="index">
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
    <v-dialog v-model="editDialog" max-width="700px">
      <v-card>
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
                <v-select
                  v-model="editedItem.materialName"
                  :items="materialOptions"
                  label="物料名稱"
                  required
                  density="comfortable"
                  variant="outlined"
                />
              </v-col>
              <v-col cols="12" md="4">
                <v-text-field
                  v-model="editedItem.diameter1"
                  label="口徑1"
                  density="comfortable"
                  variant="outlined"
                />
              </v-col>
              <v-col cols="12" md="4">
                <v-text-field
                  v-model="editedItem.diameter2"
                  label="口徑2"
                  density="comfortable"
                  variant="outlined"
                />
              </v-col>
              <v-col cols="12" md="4">
                <v-text-field
                  v-model="editedItem.diameter3"
                  label="口徑3"
                  density="comfortable"
                  variant="outlined"
                />
              </v-col>
              <v-col cols="12" md="4">
                <v-text-field
                  v-model="editedItem.material"
                  label="材質"
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
                  :items="['啟用', '停用', '審核中']"
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
// import type { pad } from 'lodash'

const router = useRouter()
const store = usePipeFittingsStore()
const pfModulesStore = usePFModulesStore()
const userStore = useUserStore()

const tableRef = ref<any>(null); // v-data-table-virtual 的引用
let scrollableElement: HTMLElement | null = null;
const SCROLL_THRESHOLD = 150; // 距離底部多少像素時觸發加載

const fittings = computed(() => store.pipeFittings)
const currentFitting = computed(() => store.currentPipeFitting)
// const isLoadingFromStore = computed(() => store.isLoading)
const error = computed(() => store.error)
// const total = computed(() => store.totalPipeFittings)
// const loading = isLoadingFromStore
const isLoadingInitial = computed(() => store.isLoading && !store.isLoadingMore);
const isLoadingMoreFromStore = computed(() => store.isLoadingMore);

const canLoadMoreItems = computed(() => {
  return !store.isLoadingMore && store.pipeFittings.length < store.totalPipeFittings;
});

// 排序相關
const search = ref('')
const sortBy = ref('');
const sortDesc = ref(false);
const hoveredHeaderKey = ref<string | null>(null); // New ref for hovered header
const selectedModule = ref<number | null>(null);
const selectedMaterial = ref(null);

// Mapped and prepared items for the table from the store's fittings
// !!! IMPORTANT: Adjust this mapping based on your actual PipeFitting data structure !!!
const mappedPipeFittings = computed(() => {
  return fittings.value.map(fitting => {
    // This is a placeholder mapping. You need to adapt it.
    // Ensure all fields expected by your table headers and templates are correctly mapped.
    return {
      id: fitting.pomno, // Assuming 'pomno' is the unique ID and table expects 'id'
      pomno: fitting.pomno, // Keep original pomno if needed for store operations
      moduleId: fitting.module_id,
      moduleName: fitting.module?.name || `模組 (ID: ${fitting.module_id})`, // Example: if module is nested or just an ID
      materialName: fitting.name || `物料 (POMNO: ${fitting.pomno})`, // Example: if fitting.name is the material name
      diameter1: fitting.diameter1?.value || fitting.diameter1_id?.toString() || '', // Example
      diameter2: fitting.diameter2?.value || fitting.diameter2_id?.toString() || '', // Example
      diameter3: fitting.diameter3?.value || '', // Example
      material: fitting.material?.name || `材質 (ID: ${fitting.material_id})`, // Example
      length: fitting.length ?? '', // Example, use actual field name
      unit: fitting.unit || '個', // Example
      // currentPrice: fitting.current_price ?? 0, // Example
      status: fitting.is_active, // Example
      // priceHistory: fitting.price_history || [], // Example
      note: fitting.description || '', // Example
      rawFitting: fitting,
      // Add any other fields from the original mock 'materials' that your template uses
    };
  });
});

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
  // sortItems(); // Calling sortItems here might be problematic. See note below.
};

// 排序項目
// !!! IMPORTANT: This function needs a refactor. It previously sorted 'allItems.value' in-place.
// 'allItems' is removed. Sorting computed properties directly is not advisable.
// You might need to integrate sorting into 'filteredItems' or use v-data-table-virtual's sorting.
// For now, its body is commented to prevent errors. Address table sorting as a next step.
const sortItems = () => {
  /*
  if (!sortBy.value) return;

  // This logic needs to be adapted. It cannot sort a computed property like 'mappedPipeFittings.value' in place.
  // One approach is to sort a copy of the array and have 'filteredItems' use that sorted copy.
  // Or, if v-data-table-virtual handles sorting via props, this custom function might not be needed.

  // Example of how it might be adapted if filteredItems becomes the source and we sort its copy:
  // let itemsToSort = [...filteredItems.value]; // Sort a copy
  // itemsToSort.sort((a, b) => {
  //   let valueA = a[sortBy.value];
  //   let valueB = b[sortBy.value];

  //   if (sortBy.value === 'currentPrice' || sortBy.value === 'length') {
  //     valueA = parseFloat(valueA) || 0;
  //     valueB = parseFloat(valueB) || 0;
  //   } else {
  //     valueA = String(valueA || '').toLowerCase();
  //     valueB = String(valueB || '').toLowerCase();
  //   }

  //   if (valueA < valueB) return sortDesc.value ? 1 : -1;
  //   if (valueA > valueB) return sortDesc.value ? -1 : 1;
  //   return 0;
  // });
  // // Then, 'indexedItems' would need to be based on this 'itemsToSort'
  // // This requires further refactoring of computed properties.
  console.warn("sortItems() needs refactoring to work with store-driven data.");
  */
};


// 直接編輯單元格
const editingCell = ref<string | null>(null)
const tempEditValue = ref<any>(null)

// 歷史價格對話框
const priceDialog = ref(false)
const currentMaterial = ref<any>(null)
const editingPriceYear = ref<number | null>(null)
const editingPrice = ref<number | null>(null)
const editingPriceIndex = ref<number | null>(null)

// 年度選項 - 動態生成近5年的選項（台灣年號）
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

// // 篩選選項
// const selectedModule = ref(null)
// const selectedMaterial = ref(null)

// 模組名稱選項
const dynamicModuleOptions = computed(() => {
  if (!pfModulesStore.allModules) {
    return [];
  }
  return pfModulesStore.allModules.map(module => ({
    title: module.name,
    value: module.id, // 使用 module.name 作為 value 以匹配現有的篩選邏輯
  }));
});

// 物料類型選項
const materialOptions = [
  { title: '過濾器', value: '過濾器' },
  { title: '閥門', value: '閥門' },
  { title: 'PE管', value: 'PE管' },
  { title: 'PVC管', value: 'PVC管' },
  { title: '接頭', value: '接頭' },
  { title: '滴頭', value: '滴頭' },
  { title: '噴頭', value: '噴頭' }
]

// 新表頭，移除選取與材料編號，增加項次
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
const getStatusColor = (isActive: boolean | string) => { // 參數改為 isActive (布爾值)
  if (typeof isActive === 'string') { // 處理可能的舊數據或 "審核中"
    if (isActive === '啟用') return 'light-green-lighten-5';
    if (isActive === '停用') return 'error-lighten-5';
    return 'grey-lighten-4';
  }
  return isActive ? 'light-green-lighten-5' : 'error-lighten-5';
}


// 添加項次序號到項目
const indexedItems = computed(() => {
  // Apply sorting here if `sortItems` is not directly mutating the list `filteredItems` is based on
  // For now, assuming filteredItems is the list to paginate.
  // If sorting is handled by v-data-table-virtual, this might not need to change much.
  // If custom sorting is applied before this, ensure `filteredItems` reflects the sorted list.

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
    raw: item, // 確保 raw 指向映射後的 item，以便模板中的 item.raw.xxx 能正確工作
  }));
});

// const startIndexInFiltered = (page.value - 1) * itemsPerPage.value;
//   // const endIndexInFiltered = startIndexInFiltered + itemsPerPage.value;
//   // const paginatedItems = itemsToPaginate.slice(startIndexInFiltered, endIndexInFiltered); // If manual pagination needed for v-data-table-virtual

//   // v-data-table-virtual handles its own pagination and virtualization from the full list.
//   // So, indexedItems should provide the full, filtered (and potentially sorted) list with an 'index' property.
//   // The 'index' should be based on the position in the *currently displayed page* if table does pagination,
//   // or overall index if table virtualizes the whole list.
//   // For v-data-table-virtual, usually you provide the full list.
//   // The 'index' for display might be better handled inside the template slot if it's page-relative.
//   // Let's provide an overall index for now.

//   return itemsToPaginate.map((item, globalIndex) => {
//     return {
//       ...item,
//       index: globalIndex + 1, // Overall index in the filtered (and sorted) list
//       raw: item, // Keep the mapped item as raw for template access
//     };
//   });
// });

// 過濾資料
const filteredItems = computed(() => {
  let result = mappedPipeFittings.value;

  // if (selectedModule.value) {
  //   result = result.filter(item => item.moduleName === selectedModule.value);
  // }

  if (selectedModule.value !== null) { // selectedModule.value 現在是數字或 null
    result = result.filter(item => item.moduleId === selectedModule.value); // 比較 ID
  }

  if (selectedMaterial.value) {
    result = result.filter(item => item.materialName === selectedMaterial.value);
  }

  if (search.value) {
    const searchTerm = search.value.toLowerCase();

    result = result.filter(item => {
      // 確保 item 的每個值都轉換為字符串進行比較
      return Object.values(item).some(val => // <--- 添加 return 語句
        String(val).toLowerCase().includes(searchTerm)
      );
    });
    // result = result.filter(item => {
    //   Object.values(item).some(val =>
    //     String(val).toLowerCase().includes(searchTerm)
    //   )
      // return (
      //   (item.id && String(item.id).toLowerCase().includes(searchTerm)) ||
      //   (item.moduleName && String(item.moduleName).toLowerCase().includes(searchTerm)) ||
      //   (item.materialName && String(item.materialName).toLowerCase().includes(searchTerm)) ||
      //   (item.material && String(item.material).toLowerCase().includes(searchTerm)) ||
      //   (item.diameter1 && String(item.diameter1).toLowerCase().includes(searchTerm))
      // );
    // });
  }
  // Note: Sorting should ideally be applied here if not handled by v-data-table-virtual
  return result;
})

// --- 無限滾動相關函數 ---
const handleTableScroll = () => {
  if (!scrollableElement || !canLoadMoreItems.value || isLoadingMoreFromStore.value) return;

  const { scrollTop, clientHeight, scrollHeight } = scrollableElement;
  // 判斷是否滾動到接近底部
  if (scrollHeight - scrollTop - clientHeight < SCROLL_THRESHOLD) {
    loadMorePipeFittings();
  }
};

const loadMorePipeFittings = async () => {
  console.log(`[VUE LOADMORE] Attempting to load more. CanLoad: ${canLoadMoreItems.value}, IsLoadingMore: ${isLoadingMoreFromStore.value}`);
  if (!canLoadMoreItems.value) { // 再次檢查，防止重複調用
    // console.log('Cannot load more or already loading.');
    return;
  }

  const currentLoadedCount = store.pipeFittings.length;
  const userOfficeId = 99; // <<<< IMPORTANT: 替換為實際的 office_id
  const itemsToFetchPerPage = 50; // 每次加載的數量
  console.log(`[VUE LOADMORE] Calling store action with: skip=${currentLoadedCount}, limit=${itemsToFetchPerPage}, append=true`);
  // console.log(`Requesting more items. Skip: ${currentLoadedCount}, Limit: ${itemsToFetchPerPage}`);
  await store.fetchPipeFittingsByOfficeId(userOfficeId, {
    skip: currentLoadedCount,
    limit: itemsToFetchPerPage,
    append: true, // 標記為追加數據
  });
};


// 開始編輯單元格
const startCellEdit = (itemId: string, field: string, currentValue: any) => {
  editingCell.value = `${itemId}-${field}`
  // 對於 status 字段，tempEditValue 應該是布爾值
  if (field === 'status') {
    const fitting = mappedPipeFittings.value.find(f => String(f.id) === itemId);
    tempEditValue.value = fitting ? fitting.rawFitting.is_active : false;
  } else {
    tempEditValue.value = currentValue
  }
}

// 取消編輯
const cancelEdit = () => {
  editingCell.value = null
  tempEditValue.value = null
}

// 儲存單元格編輯
// const saveCell = (itemId: string, field: string) => {
//   const index = allItems.value.findIndex(item => item.id === itemId)
//   if (index !== -1) {
//     // 更新欄位值
//     const item = allItems.value[index]
//     item[field] = tempEditValue.value

//     // 如果更新的是目前單價，也需要更新歷史價格
//     if (field === 'currentPrice' && tempEditValue.value !== null && tempEditValue.value > 0) {
//       // 檢查是否有本年度的價格
//       const currentYearIndex = item.priceHistory.findIndex(p => p.year === currentYear)

//       if (currentYearIndex >= 0) {
//         // 更新本年度價格
//         item.priceHistory[currentYearIndex].price = tempEditValue.value
//       } else {
//         // 添加本年度價格
//         item.priceHistory.push({
//           year: currentYear,
//           price: tempEditValue.value
//         })

//         // 按年度排序
//         item.priceHistory.sort((a, b) => b.year - a.year)
//       }
//     }
//   }
const saveCell = async (itemId: string, field: string) => { // 改為 async
  const itemIndex = mappedPipeFittings.value.findIndex(item => item.id === itemId);
  if (itemIndex === -1) {
    cancelEdit();
    return;
  }

  const originalFitting = fittings.value.find(f => f.pomno === itemId);
  if (!originalFitting) {
    cancelEdit();
    return;
  }

  let valueToSave = tempEditValue.value;

  // 準備更新數據
  const updateData: any = {};

  if (field === 'status') {
    updateData.is_active = valueToSave; // valueToSave 應該是布爾值
  } else if (field === 'moduleName') {
    // 如果 moduleName 存的是 ID
    // updateData.module_id = valueToSave; // 假設 tempEditValue 是 module_id
    // 如果 moduleName 存的是 name，需要轉換為 ID
    const selectedModule = pfModulesStore.allModules.find(m => m.id === valueToSave); // 假設 tempEditValue 是 id
    if (selectedModule) {
      updateData.module_id = selectedModule.id;
    } else {
      console.warn('Module not found for saving:', tempEditValue.value);
      cancelEdit();
      return;
    }
  } else if (field === 'materialName') {
    updateData.name = valueToSave; // 假設 materialName 對應 fitting.name
  } else if (field === 'diameter1') {
    // 假設 diameter1 存的是 ID
    // updateData.diameter1_id = valueToSave; // 需要轉換為 ID
    // 這裡需要 PFDiametersStore 來查找 ID
  }
  // ... 為其他可編輯字段添加類似的映射 ...
  else {
    // 假設其他字段名直接對應 PipeFittingUpdate schema 中的字段名
    // 注意：這需要確保 mappedPipeFittings 中的 key 與 PipeFittingUpdate 的 key 一致
    // 或者在這裡進行映射
    // 例如，如果 mappedPipeFittings 的 key 是 'length' 而 PipeFittingUpdate 的 key 也是 'length'
    updateData[field] = valueToSave;
  }


  if (Object.keys(updateData).length > 0) {
    try {
      console.log(`Saving item ${itemId}, field ${field}, value:`, valueToSave, 'Update data:', updateData);
      await store.updatePipeFitting(itemId, updateData); // 調用 store action 更新後端
      // 更新成功後，store 應該會重新獲取數據或更新本地數據，
      // mappedPipeFittings 會自動響應
    } catch (error) {
      console.error('Failed to save cell:', error);
      // 可以添加錯誤提示
    }
  }

  cancelEdit();
}

//   // 退出編輯模式
//   editingCell.value = null
//   tempEditValue.value = null
// }


const toggleAndSaveStatus = (itemId: string) => {
  // 找到對應的 fitting 來獲取當前 is_active 狀態
  const fitting = mappedPipeFittings.value.find(f => String(f.id) === itemId);
  if (fitting) {
    // 切換狀態
    tempEditValue.value = !fitting.rawFitting.is_active;
    // 立即保存
    saveCell(itemId, 'status');
  }
  // 不需要保持編輯模式，因為點擊即保存
  editingCell.value = null;
};

const editItem = (itemId: string) => {
  const item = allItems.value.find(item => item.id === itemId)
  if (item) {
    // 複製項目數據到編輯表單
    Object.assign(editedItem, item)
    // 開啟編輯對話框
    editDialog.value = true
  }
}

const deleteItem = (itemId: string) => {
  if (confirm(`確定要刪除編號 ${itemId} 的材料嗎？`)) {
    try {
      // 從UI中移除
      allItems.value = allItems.value.filter(item => item.id !== itemId)
      console.log('刪除材料:', itemId)
    } catch (error) {
      console.error('刪除材料失敗:', error)
    }
  }
}

// 顯示歷史價格對話框
const showPriceHistory = (item: any) => {
  currentMaterial.value = item
  priceDialog.value = true
  editingPriceIndex.value = null
  editingPriceYear.value = null
  editingPrice.value = null
}

// 開始編輯某個價格
const startEditPrice = (index: number) => {
  editingPriceIndex.value = index
  editingPrice.value = currentMaterial.value.priceHistory[index].price
}

// 更新價格
const updatePrice = (index: number) => {
  if (editingPrice.value !== null && editingPrice.value > 0) {
    // 更新價格
    currentMaterial.value.priceHistory[index].price = editingPrice.value

    // 如果是最新年份的價格，更新當前價格
    const year = currentMaterial.value.priceHistory[index].year
    const latestYear = Math.max(...currentMaterial.value.priceHistory.map((p: any) => p.year))
    if (year === latestYear) {
      currentMaterial.value.currentPrice = editingPrice.value
    }
  }

  // 結束編輯狀態
  editingPriceIndex.value = null
  editingPrice.value = null
}

// 新增歷史價格
const addPriceHistory = () => {
  if (currentMaterial.value && editingPriceYear.value && editingPrice.value) {
    // 檢查是否已存在該年度價格
    const existingPriceIndex = currentMaterial.value.priceHistory.findIndex(
      (p: any) => p.year === editingPriceYear.value
    )

    if (existingPriceIndex >= 0) {
      // 更新現有價格
      currentMaterial.value.priceHistory[existingPriceIndex].price = editingPrice.value
    } else {
      // 添加新價格記錄
      currentMaterial.value.priceHistory.push({
        year: editingPriceYear.value,
        price: editingPrice.value
      })

      // 根據年度排序（降序）
      currentMaterial.value.priceHistory.sort((a: any, b: any) => b.year - a.year)
    }

    // 更新當前價格（最新年度的價格）
    if (!currentMaterial.value.priceHistory.length ||
        editingPriceYear.value >= Math.max(...currentMaterial.value.priceHistory.map((p: any) => p.year))) {
      currentMaterial.value.currentPrice = editingPrice.value
    }

    // 重置編輯欄位
    editingPriceYear.value = null
    editingPrice.value = null
  }
}

// 刪除歷史價格
const deletePriceHistory = (year: number) => {
  if (currentMaterial.value) {
    currentMaterial.value.priceHistory = currentMaterial.value.priceHistory.filter(
      (p: any) => p.year !== year
    )

    // 如果刪除的是目前顯示的價格，更新為最新年度的價格
    if (currentMaterial.value.priceHistory.length > 0) {
      const latestYear = Math.max(...currentMaterial.value.priceHistory.map((p: any) => p.year))
      const latestPrice = currentMaterial.value.priceHistory.find((p: any) => p.year === latestYear)?.price
      if (latestPrice) {
        currentMaterial.value.currentPrice = latestPrice
      }
    }
  }
}

// 保存編輯的材料
const saveItem = () => {
  if (editedItem.id) {
    // 編輯現有項目
    const index = allItems.value.findIndex(item => item.id === editedItem.id)
    if (index !== -1) {
      // 更新項目
      Object.assign(allItems.value[index], editedItem)
    }
  } else {
    // 創建新項目
    const newItem = { ...editedItem }
    // 生成新ID
    newItem.id = `M${(allItems.value.length + 1).toString().padStart(3, '0')}`
    // 添加當前年度價格到歷史記錄
    if (newItem.currentPrice > 0) {
      newItem.priceHistory = [{
        year: currentYear,
        price: newItem.currentPrice
      }]
    }
    // 添加到列表
    allItems.value.push(newItem)
  }

  // 關閉對話框
  editDialog.value = false
  // 重置編輯項目
  Object.assign(editedItem, defaultItem)
}

// 組件掛載時載入資料
onMounted(async () => {
  // loadAllItems()
  console.log('Component Mounted: Initializing PipeFittings...');

  // Replace 99 with the actual user's office_id
  // This should ideally come from auth store or user profile
  const userOfficeId = userStore.currentUser?.office?.id; // <<<< Access office through currentUser
  const initialLimit = 50;

  // 初始數據加載
  await store.fetchPipeFittingsByOfficeId(userOfficeId, {
    skip: 0,
    limit: initialLimit,
    append: false, // 初始加載，非追加
  });

  await pfModulesStore.ensureAllModulesLoaded()

  console.log('Store: Fittings after initial fetch:', fittings.value.length);
  console.log('Store: Total after initial fetch:', store.totalPipeFittings);

  // 設置滾動監聽器
  await nextTick(); // 等待 DOM 更新完成
  if (tableRef.value && tableRef.value.$el) {
    // v-data-table-virtual 的滾動容器通常是 .v-table__wrapper
    const wrapper = tableRef.value.$el.querySelector('.v-table__wrapper');
    if (wrapper) {
      scrollableElement = wrapper as HTMLElement;
      scrollableElement.addEventListener('scroll', handleTableScroll);
      // console.log('Scroll listener attached to .v-table__wrapper');
    } else {
      console.warn('Could not find .v-table__wrapper for v-data-table-virtual. Infinite scroll might not work.');
    }
  }

  // 測試 fetchPipeFittingById (保持不變，但注意 pomno 的來源)
  if (mappedPipeFittings.value.length > 0) {
    const firstItem = mappedPipeFittings.value[0];
    if (firstItem && typeof firstItem.pomno !== 'undefined') {
      await store.fetchPipeFittingById(firstItem.pomno);
      // console.log('Store: Current fitting after fetch by ID:', currentFitting.value);
    }
  }
})

onBeforeUnmount(() => {
  if (scrollableElement) {
    scrollableElement.removeEventListener('scroll', handleTableScroll);
    // console.log('Scroll listener removed.');
  }
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
  background-color: rgba(255, 255, 255, 0.6) !important; /* 半透明白色背景 */
  backdrop-filter: blur(10px) !important; /* 背景模糊效果 */
  -webkit-backdrop-filter: blur(10px) !important; /* Safari 支持 */
  border: 1px solid rgba(255, 255, 255, 0.25) !important; /* 細微邊框增強玻璃感 */
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.05) !important; /* 柔和陰影增強玻璃感 */
}

.section-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08) !important;
  background-color: rgba(255, 255, 255, 0.85) !important; /* 懸停時略微增加不透明度 */
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
  position: relative; /* For positioning the icon */
  text-align: left; /* Default alignment */
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
  min-height: 24px; /* Adjust as needed based on your font size and padding */
}

.header-text {
  transition: opacity 0.2s ease-in-out;
  flex-grow: 1; /* Allow text to take available space */
}

.sort-icon-container {
  display: flex; /* Use flex to center icon if needed */
  align-items: center;
  justify-content: center; /* Center icon if it's the only element */
  transition: opacity 0.2s ease-in-out;
  opacity: 0; /* Initially hidden */
  position: absolute; /* Position it within the th */
  left: 50%;
  top: 50%;
  transform: translate(-50%, -50%); /* Center it perfectly */
}

.custom-header.sortable-header:hover .sort-icon-container {
  opacity: 1; /* Show on hover */
}

.custom-header.sortable-header:hover .header-text {
  opacity: 0; /* Hide text on hover */
}

/* Ensure active sort icon is also visible if text is hidden */
.custom-header.sortable-header:hover .sort-icon-container.active,
.custom-header.sortable-header .sort-icon-container.active {
  opacity: 1;
}
.custom-header.sortable-header:hover .header-text:has(+ .sort-icon-container.active) {
   opacity: 0;
}


.sort-icon {
  color: #333; /* Default color */
}

.sort-icon.active {
  color: #3ea0a3 !important; /* Active sort color */
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
