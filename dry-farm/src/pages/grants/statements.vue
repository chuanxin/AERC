<template>
  <v-container
    fluid
    class="grants-statements-container px-6 pb-0 pt-0"
    style="background-color: white"
  >
    <!-- 麵包屑導航 -->
    <!-- <v-breadcrumbs
      :items="breadcrumbItems"
      class="pa-0 mb-4"
    >
      <template #divider>
        <v-icon icon="mdi-chevron-right" />
      </template>
    </v-breadcrumbs> -->

    <!-- 主內容區 -->
    <v-row justify="center">
      <v-col
        cols="12"
        lg="10"
        align-self="center"
        class="pt-0"
      >
        <!-- 標題與操作區 -->
        <div class="d-flex flex-wrap align-center pr-2 mb-4">
          <!-- <v-btn
            icon="mdi-arrow-left"
            variant="text"
            color="#3ea0a3"
            @click="goBack"
            class="mr-3"
          />
          <div class="flex-grow-1">
            <h1 class="text-h5 font-weight-black text-primary">
              <v-icon icon="mdi-file-document-outline" class="mr-2" />
              歷史案件表單資料
            </h1>
            <p class="text-subtitle-2 text-grey-600 ma-0">
              {{ currentCase?.cover.case_number }} - {{ currentCase?.cover.applicant_name }} ({{ currentCase?.cover.facility_type }})
            </p>
          </div> -->
          <v-spacer />
          <div class="d-flex gap-2">
            <v-btn
              prepend-icon="mdi-printer"
              color="#3ea0a3"
              variant="outlined"
              rounded="lg"
              @click="printStatement"
            >
              列印
            </v-btn>
            <v-btn
              prepend-icon="mdi-download"
              color="#3ea0a3"
              variant="outlined"
              rounded="lg"
              @click="downloadPDF"
            >
              下載PDF
            </v-btn>
          </div>
        </div>

        <!-- 載入狀態 -->
        <v-progress-linear
          v-if="isLoading"
          indeterminate
          color="#3ea0a3"
          class="mb-4"
        />

        <!-- 錯誤訊息 -->
        <v-alert
          v-if="error"
          type="error"
          class="mb-4"
          closable
          @click:close="error = null"
        >
          {{ error }}
        </v-alert>

        <!-- 無資料提示 -->
        <v-alert
          v-if="!isLoading && !error && !currentCase"
          type="warning"
          class="mb-4"
        >
          找不到案件資料，請確認案件編號是否正確
        </v-alert>

        <div
          v-if="currentCase"
          class="section-wrapper"
        >
          <!-- 案件基本資訊摘要 -->
          <v-card
            class="mb-4 pa-4"
            color="#e3f4f4"
            rounded="lg"
          >
            <v-card-title
              class="text-subtitle-1 font-weight-bold pa-0 pb-4"
              style="color: #2d8c8f"
            >
              <v-icon
                color="#3ea0a3"
                class="me-2 pb-1"
                size="small"
              >
                mdi-information
              </v-icon>
              案件基本資訊
            </v-card-title>

            <v-row dense>
              <v-col
                cols="12"
                md="3"
              >
                <div class="info-item">
                  <div class="text-caption text-grey-600">
                    案件編號
                  </div>
                  <div class="text-subtitle-1 font-weight-medium">
                    {{ currentCase?.cover?.case_number || '-' }}
                  </div>
                </div>
              </v-col>
              <v-col
                cols="12"
                md="3"
              >
                <div class="info-item">
                  <div class="text-caption text-grey-600">
                    申請年度
                  </div>
                  <div class="text-subtitle-1 font-weight-medium">
                    民國 {{ currentCase?.cover?.year || '-' }} 年
                  </div>
                </div>
              </v-col>
              <v-col
                cols="12"
                md="3"
              >
                <div class="info-item">
                  <div class="text-caption text-grey-600">
                    申請人
                  </div>
                  <div class="text-subtitle-1 font-weight-medium">
                    {{ currentCase?.cover?.applicant_name || '-' }}
                  </div>
                </div>
              </v-col>
              <v-col
                cols="12"
                md="3"
              >
                <div class="info-item">
                  <div class="text-caption text-grey-600">
                    設施類型
                  </div>
                  <div class="text-subtitle-1 font-weight-medium">
                    {{ currentCase?.cover?.facility_type || '-' }}
                  </div>
                </div>
              </v-col>
            </v-row>

            <v-divider class="my-3" />

            <v-row dense>
              <v-col
                cols="12"
                md="4"
              >
                <div class="info-item">
                  <div class="text-caption text-grey-600">
                    通訊地址
                  </div>
                  <div class="text-body-2">
                    {{ currentCase?.cover?.address || '-' }}
                  </div>
                </div>
              </v-col>
              <v-col
                cols="12"
                md="4"
              >
                <div class="info-item">
                  <div class="text-caption text-grey-600">
                    設施地點
                  </div>
                  <div class="text-body-2">
                    {{ (currentCase?.cover?.facility_location?.location_summary || '') || '-' }}
                  </div>
                </div>
              </v-col>
              <v-col
                cols="12"
                md="4"
              >
                <div class="info-item">
                  <div class="text-caption text-grey-600">
                    申請面積
                  </div>
                  <div class="text-body-2">
                    {{ (currentCase?.cover?.application_area || '-') + ' ' + (currentCase?.cover?.area_unit || '') }}
                  </div>
                </div>
              </v-col>
            </v-row>
          </v-card>

          <v-card
            class="mx-auto section-card"
            elevation="2"
            rounded="lg"
          >
            <v-card-text class="pa-4">
              <!-- 工程預算書 -->
              <v-card
                flat
                class="mb-4 pa-4"
                color="#e3f4f4"
                rounded="lg"
              >
                <v-card-title
                  class="text-subtitle-1 font-weight-bold pa-0 pb-4"
                  style="color: #2d8c8f"
                >
                  <v-icon
                    color="#3ea0a3"
                    class="me-2 pb-1"
                    size="small"
                  >
                    mdi-calculator
                  </v-icon>
                  工程預算書
                </v-card-title>

                <v-row>
                  <!-- 預算項目 -->
                  <v-col
                    cols="12"
                    md="8"
                  >
                    <v-card
                      flat
                      bg-color="white"
                      rounded="lg"
                      class="pa-3"
                    >
                      <v-table
                        density="comfortable"
                        class="budget-table"
                      >
                        <thead>
                          <tr>
                            <th class="text-left">
                              項目
                            </th>
                            <th class="text-right">
                              金額 (元)
                            </th>
                            <th class="text-left">
                              備註
                            </th>
                          </tr>
                        </thead>
                        <tbody>
                          <tr
                            v-for="(item, key) in currentCase?.budget_table?.items || {}"
                            :key="key"
                          >
                            <td class="font-weight-medium">
                              {{ item.category }}
                            </td>
                            <td class="text-right">
                              {{ formatNumber(item.amount) }}
                            </td>
                            <td>{{ item.note || '-' }}</td>
                          </tr>
                        </tbody>
                      </v-table>
                    </v-card>
                  </v-col>

                  <!-- 預算摘要 -->
                  <v-col
                    cols="12"
                    md="4"
                  >
                    <v-card
                      flat
                      bg-color="white"
                      rounded="lg"
                      class="pa-3"
                    >
                      <div
                        class="text-subtitle-2 font-weight-bold mb-3"
                        style="color: #2d8c8f"
                      >
                        預算摘要
                      </div>
                      <div class="summary-item mb-2">
                        <div class="d-flex justify-space-between">
                          <span>總預算：</span>
                          <span class="font-weight-bold">{{ formatNumber(currentCase?.budget_table?.summary?.total_amount || 0) }}</span>
                        </div>
                      </div>
                      <div class="summary-item mb-2">
                        <div class="d-flex justify-space-between">
                          <span>農民自籌：</span>
                          <span>{{ formatNumber(currentCase?.budget_table?.summary?.farmer_contribution || 0) }}</span>
                        </div>
                      </div>
                      <div class="summary-item mb-2">
                        <div class="d-flex justify-space-between">
                          <span>政府補助：</span>
                          <span
                            class="font-weight-bold"
                            style="color: #3ea0a3"
                          >{{ formatNumber(currentCase?.budget_table?.summary?.government_subsidy?.total || 0) }}</span>
                        </div>
                      </div>
                      <v-divider class="my-2" />
                      <div class="text-caption text-grey-600">
                        補助標準：{{ currentCase?.budget_table?.header?.subsidy_standard || '-' }}
                      </div>
                    </v-card>
                  </v-col>
                </v-row>
              </v-card>

              <!-- 土地清冊 -->
              <v-card
                flat
                class="mb-4 pa-4"
                color="#e3f4f4"
                rounded="lg"
              >
                <v-card-title
                  class="text-subtitle-1 font-weight-bold pa-0 pb-4"
                  style="color: #2d8c8f"
                >
                  <v-icon
                    color="#3ea0a3"
                    class="me-2 pb-1"
                    size="small"
                  >
                    mdi-map
                  </v-icon>
                  土地清冊
                </v-card-title>

                <v-card
                  flat
                  bg-color="white"
                  rounded="lg"
                  class="pa-3"
                >
                  <v-table
                    density="comfortable"
                    class="land-table"
                  >
                    <thead>
                      <tr>
                        <th class="text-left">
                          地段
                        </th>
                        <th class="text-left">
                          地號
                        </th>
                        <th class="text-right">
                          土地面積(㎡)
                        </th>
                        <th class="text-right">
                          設施面積(㎡)
                        </th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr
                        v-for="(land, index) in currentCase?.lands_table?.lands || []"
                        :key="index"
                      >
                        <td>{{ land.section }}</td>
                        <td>{{ land.land_number }}</td>
                        <td class="text-right">
                          {{ formatNumber(land.land_area_sqm) }}
                        </td>
                        <td class="text-right">
                          {{ formatNumber(land.facility_area_sqm) }}
                        </td>
                      </tr>
                    </tbody>
                    <tfoot>
                      <tr
                        class="font-weight-bold"
                        style="background-color: #f5f5f5"
                      >
                        <td colspan="2">
                          總計
                        </td>
                        <td class="text-right">
                          {{ formatNumber(currentCase?.lands_table?.summary?.total_land_area || 0) }}
                        </td>
                        <td class="text-right">
                          {{ formatNumber(currentCase?.lands_table?.summary?.total_facility_area || 0) }}
                        </td>
                      </tr>
                    </tfoot>
                  </v-table>
                </v-card>
              </v-card>

              <!-- 動力與調蓄設備 -->
              <v-card
                flat
                class="mb-4 pa-4"
                color="#e3f4f4"
                rounded="lg"
              >
                <v-card-title
                  class="text-subtitle-1 font-weight-bold pa-0 pb-4"
                  style="color: #2d8c8f"
                >
                  <v-icon
                    color="#3ea0a3"
                    class="me-2 pb-1"
                    size="small"
                  >
                    mdi-engine
                  </v-icon>
                  動力與調蓄設備
                </v-card-title>

                <v-row>
                  <v-col
                    cols="12"
                    md="6"
                  >
                    <v-card
                      flat
                      bg-color="white"
                      rounded="lg"
                      class="pa-3"
                    >
                      <div
                        class="text-subtitle-2 font-weight-bold mb-3"
                        style="color: #2d8c8f"
                      >
                        動力設備
                      </div>
                      <v-table
                        density="comfortable"
                        class="equipment-table"
                      >
                        <thead>
                          <tr>
                            <th class="text-left">
                              項目
                            </th>
                            <th class="text-center">
                              數量
                            </th>
                            <th class="text-right">
                              金額
                            </th>
                          </tr>
                        </thead>
                        <tbody>
                          <tr
                            v-for="(item, index) in currentCase?.power_storage_equipments_table?.power_equipment?.items || []"
                            :key="index"
                          >
                            <td>{{ item.name }}</td>
                            <td class="text-center">
                              {{ item.quantity }}
                            </td>
                            <td class="text-right">
                              {{ formatNumber(item.amount) }}
                            </td>
                          </tr>
                        </tbody>
                        <tfoot>
                          <tr
                            class="font-weight-bold"
                            style="background-color: #f5f5f5"
                          >
                            <td>小計</td>
                            <td />
                            <td class="text-right">
                              {{ formatNumber(currentCase?.power_storage_equipments_table?.power_equipment?.subtotal || 0) }}
                            </td>
                          </tr>
                        </tfoot>
                      </v-table>
                    </v-card>
                  </v-col>

                  <v-col
                    cols="12"
                    md="6"
                  >
                    <v-card
                      flat
                      bg-color="white"
                      rounded="lg"
                      class="pa-3"
                    >
                      <div
                        class="text-subtitle-2 font-weight-bold mb-3"
                        style="color: #2d8c8f"
                      >
                        調蓄設備
                      </div>
                      <div
                        v-if="(currentCase?.power_storage_equipments_table?.storage_equipment?.items || []).length === 0"
                        class="text-center py-6"
                      >
                        <v-icon
                          size="48"
                          color="grey-lighten-2"
                        >
                          mdi-information
                        </v-icon>
                        <div class="text-body-2 text-grey-600 mt-2">
                          無調蓄設備
                        </div>
                      </div>
                      <v-table
                        v-else
                        density="comfortable"
                        class="equipment-table"
                      >
                        <thead>
                          <tr>
                            <th class="text-left">
                              項目
                            </th>
                            <th class="text-center">
                              數量
                            </th>
                            <th class="text-right">
                              金額
                            </th>
                          </tr>
                        </thead>
                        <tbody>
                          <tr
                            v-for="(item, index) in currentCase?.power_storage_equipments_table?.storage_equipment?.items || []"
                            :key="index"
                          >
                            <td>{{ item.name }}</td>
                            <td class="text-center">
                              {{ item.quantity }}
                            </td>
                            <td class="text-right">
                              {{ formatNumber(item.amount) }}
                            </td>
                          </tr>
                        </tbody>
                        <tfoot>
                          <tr
                            class="font-weight-bold"
                            style="background-color: #f5f5f5"
                          >
                            <td>小計</td>
                            <td />
                            <td class="text-right">
                              {{ formatNumber(currentCase?.power_storage_equipments_table?.storage_equipment?.subtotal || 0) }}
                            </td>
                          </tr>
                        </tfoot>
                      </v-table>
                    </v-card>
                  </v-col>
                </v-row>
              </v-card>

              <!-- 管路材料數量表 -->
              <v-card
                flat
                class="mb-4 pa-4"
                color="#e3f4f4"
                rounded="lg"
              >
                <v-card-title
                  class="text-subtitle-1 font-weight-bold pa-0 pb-4"
                  style="color: #2d8c8f"
                >
                  <v-icon
                    color="#3ea0a3"
                    class="me-2 pb-1"
                    size="small"
                  >
                    mdi-pipe
                  </v-icon>
                  管路灌溉系統材料數量表
                </v-card-title>

                <div
                  v-for="(category, categoryKey) in currentCase?.pipe_materials_table?.categories || {}"
                  :key="categoryKey"
                  class="mb-4"
                >
                  <v-card
                    flat
                    bg-color="white"
                    rounded="lg"
                    class="pa-3"
                  >
                    <div
                      class="text-subtitle-2 font-weight-bold mb-3"
                      style="color: #3ea0a3"
                    >
                      {{ category.name }}
                    </div>
                    <v-table
                      density="comfortable"
                      class="materials-table"
                    >
                      <thead>
                        <tr>
                          <th class="text-left">
                            項目
                          </th>
                          <th class="text-left">
                            規格
                          </th>
                          <th class="text-center">
                            單位
                          </th>
                          <th class="text-right">
                            數量
                          </th>
                          <th class="text-right">
                            單價
                          </th>
                          <th class="text-right">
                            總價
                          </th>
                          <th class="text-left">
                            備註
                          </th>
                        </tr>
                      </thead>
                      <tbody>
                        <tr
                          v-for="(item, index) in category.items"
                          :key="index"
                        >
                          <td>{{ item.material_name }}</td>
                          <td>{{ item.specification }}</td>
                          <td class="text-center">
                            {{ item.unit }}
                          </td>
                          <td class="text-right">
                            {{ formatNumber(item.quantity) }}
                          </td>
                          <td class="text-right">
                            {{ formatNumber(item.unit_price) }}
                          </td>
                          <td class="text-right font-weight-medium">
                            {{ formatNumber(item.total_price) }}
                          </td>
                          <td>{{ item.note || '-' }}</td>
                        </tr>
                      </tbody>
                    </v-table>
                  </v-card>
                </div>

                <v-card
                  flat
                  bg-color="white"
                  rounded="lg"
                  class="pa-3"
                >
                  <div class="text-right">
                    <div
                      class="text-subtitle-1 font-weight-bold"
                      style="color: #3ea0a3"
                    >
                      材料總價：{{ formatNumber(currentCase?.pipe_materials_table?.total_price || 0) }} 元
                    </div>
                  </div>
                </v-card>
              </v-card>

              <!-- 工程參數與系統資訊 -->
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
                      class="text-subtitle-1 font-weight-bold pa-0 pb-4"
                      style="color: #2d8c8f"
                    >
                      <v-icon
                        color="#3ea0a3"
                        class="me-2 pb-1"
                        size="small"
                      >
                        mdi-cog
                      </v-icon>
                      工程參數
                    </v-card-title>

                    <v-card
                      flat
                      bg-color="white"
                      rounded="lg"
                      class="pa-3"
                    >
                      <div class="parameter-grid">
                        <div class="parameter-item">
                          <div class="text-caption text-grey-600">
                            坵塊大小
                          </div>
                          <div class="text-body-2">
                            {{ currentCase?.metadata?.engineering_parameters?.block_shape || '-' }}
                          </div>
                        </div>
                        <div class="parameter-item">
                          <div class="text-caption text-grey-600">
                            主管配置
                          </div>
                          <div class="text-body-2">
                            {{ currentCase?.metadata?.engineering_parameters?.main_pipe_l1 || '-' }}
                          </div>
                        </div>
                        <div class="parameter-item">
                          <div class="text-caption text-grey-600">
                            支管間距
                          </div>
                          <div class="text-body-2">
                            {{ currentCase?.metadata?.engineering_parameters?.branch_spacing || '-' }}
                          </div>
                        </div>
                        <div class="parameter-item">
                          <div class="text-caption text-grey-600">
                            噴頭間距
                          </div>
                          <div class="text-body-2">
                            {{ currentCase?.metadata?.engineering_parameters?.sprinkler_spacing || '-' }}
                          </div>
                        </div>
                        <div class="parameter-item">
                          <div class="text-caption text-grey-600">
                            水源
                          </div>
                          <div class="text-body-2">
                            {{ currentCase?.metadata?.engineering_parameters?.water_source || '-' }}
                          </div>
                        </div>
                        <div class="parameter-item">
                          <div class="text-caption text-grey-600">
                            設計者
                          </div>
                          <div class="text-body-2">
                            {{ currentCase?.metadata?.engineering_parameters?.designer || '-' }}
                          </div>
                        </div>
                      </div>
                    </v-card>
                  </v-card>
                </v-col>

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
                      class="text-subtitle-1 font-weight-bold pa-0 pb-4"
                      style="color: #2d8c8f"
                    >
                      <v-icon
                        color="#3ea0a3"
                        class="me-2 pb-1"
                        size="small"
                      >
                        mdi-information
                      </v-icon>
                      系統資訊
                    </v-card-title>

                    <v-card
                      flat
                      bg-color="white"
                      rounded="lg"
                      class="pa-3"
                    >
                      <div class="parameter-grid">
                        <div class="parameter-item">
                          <div class="text-caption text-grey-600">
                            生成時間
                          </div>
                          <div class="text-body-2">
                            {{ formatDate(currentCase?.metadata?.generated_at) }}
                          </div>
                        </div>
                        <div class="parameter-item">
                          <div class="text-caption text-grey-600">
                            模板版本
                          </div>
                          <div class="text-body-2">
                            {{ currentCase?.metadata?.template_version || '-' }}
                          </div>
                        </div>
                        <div class="parameter-item">
                          <div class="text-caption text-grey-600">
                            調控設施
                          </div>
                          <div class="text-body-2">
                            {{ currentCase?.metadata?.equipment_summary?.control_facilities || '-' }}
                          </div>
                        </div>
                        <div class="parameter-item">
                          <div class="text-caption text-grey-600">
                            動力設備
                          </div>
                          <div class="text-body-2">
                            {{ currentCase?.metadata?.equipment_summary?.power_equipment || '-' }}
                          </div>
                        </div>
                        <div class="parameter-item">
                          <div class="text-caption text-grey-600">
                            調蓄設施
                          </div>
                          <div class="text-body-2">
                            {{ currentCase?.metadata?.equipment_summary?.storage_capacity || '-' }}
                          </div>
                        </div>
                        <div class="parameter-item">
                          <div class="text-caption text-grey-600">
                            資料來源
                          </div>
                          <div class="text-body-2">
                            {{ currentCase?.metadata?.source || '-' }}
                          </div>
                        </div>
                      </div>
                    </v-card>
                  </v-card>
                </v-col>
              </v-row>
            </v-card-text>
          </v-card>
        </div>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { getGrantPapers } from '@/services/grantsService'

// 定義歷史案件資料的類型
interface HistoricalCaseData {
  report?: {
    cover?: any
    budget_table?: any
    lands_table?: any
    power_storage_equipments_table?: any
    pipe_materials_table?: any
    metadata?: any
  }
}

// Router setup
const route = useRoute()

// 從路由查詢參數取得案件編號和案件ID
const caseNumber = computed(() => route.query.case as string)
const grantsId = computed(() => {
  const id = route.query.grants_id as string
  return id ? parseInt(id) : undefined
})

// 載入狀態
const isLoading = ref(false)
const error = ref<string | null>(null)

// 歷史案件資料（從資料庫載入）
const historicalCase = ref<HistoricalCaseData | null>(null)

// 載入案件文件資料
const loadGrantPapersData = async () => {
  if (!caseNumber.value) return

  isLoading.value = true
  error.value = null

  try {
    console.log('🔄 載入案件文件資料:', caseNumber.value, grantsId.value ? `(ID: ${grantsId.value})` : '')

    // 從 grant_papers 表格載入預算報表資料
    const papersData = await getGrantPapers(caseNumber.value, 'budget_statement', grantsId.value)

    if (papersData && papersData.document_data) {
      historicalCase.value = papersData.document_data
      console.log('✅ 成功載入案件文件資料')
      console.log('📦 資料結構:', papersData.document_data)
    } else {
      throw new Error('文件資料格式不正確')
    }

  } catch (err) {
    console.error('❌ 載入案件文件資料失敗:', err)
    error.value = err instanceof Error ? err.message : '載入失敗'

    // 如果載入失敗，設定為空的預設結構
    historicalCase.value = {
      report: {
        cover: {},
        budget_table: { items: {}, summary: {} },
        lands_table: { lands: [], summary: {} },
        power_storage_equipments_table: {
          power_equipment: { items: [] },
          storage_equipment: { items: [] }
        },
        pipe_materials_table: { categories: {} },
        metadata: {}
      }
    }
  } finally {
    isLoading.value = false
  }
}

// 當前案件
const currentCase = computed(() => {
  return historicalCase.value?.report || null
})

// 格式化數字
const formatNumber = (num: number | undefined) => {
  if (num === undefined || num === null || isNaN(num)) return '0'
  return new Intl.NumberFormat('zh-TW').format(num)
}

// 格式化日期
const formatDate = (dateStr: string | undefined) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleString('zh-TW')
}

// 列印功能
const printStatement = () => {
  window.print()
}

// 下載PDF功能
const downloadPDF = () => {
  // TODO: 實現PDF下載功能
  console.log('下載PDF功能待實現')
}

onMounted(async () => {
  // 頁面載入時根據路由參數載入對應的歷史案件資料
  console.log('載入歷史案件:', caseNumber.value)
  await loadGrantPapersData()
})
</script>

<style scoped>
.grants-statements-container {
  min-height: 100vh;
}

.section-wrapper {
  margin-bottom: 2rem;
}

.section-card {
  box-shadow: 0 2px 8px rgba(62, 160, 163, 0.1);
}

.info-item {
  margin-bottom: 12px;
}

.summary-item {
  padding: 4px 0;
}

.parameter-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 12px;
}

.parameter-item {
  padding: 8px 0;
}

/* 表格樣式 */
.budget-table th,
.land-table th,
.equipment-table th,
.materials-table th {
  background-color: #f8f9fa;
  font-weight: 600;
  color: #2d8c8f;
}

.budget-table tbody tr:hover,
.land-table tbody tr:hover,
.equipment-table tbody tr:hover,
.materials-table tbody tr:hover {
  background-color: #f8f9fa;
}

/* 響應式設計 */
@media (max-width: 768px) {
  .parameter-grid {
    grid-template-columns: 1fr;
  }
}

@media print {
  .v-btn,
  .v-breadcrumbs {
    display: none !important;
  }
}
</style>
