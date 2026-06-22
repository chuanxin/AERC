<template>
  <div
    ref="stepContent"
    class="step-content"
  >
    <v-card
      class="mt-4 mb-0 pa-0"
      flat
    >
      <v-card-text class="py-0">
        <v-form
          ref="form"
          v-model="localValid"
          @submit.prevent
        >
          <!-- 版本比較與變更設計部分 -->
          <!-- 暫時註解：版本比較功能待後續開發完成後啟用 -->
          <!--
          <v-card
            v-if="shouldShowVersionComparison"
            class="mb-4"
            variant="outlined"
          >
            <v-card-title class="bg-light-blue-lighten-4 d-flex align-center justify-space-between py-2 px-4">
              <div class="d-flex align-center">
                <v-icon
                  class="me-2"
                  size="small"
                >
                  mdi-file-compare
                </v-icon>
                <span class="text-subtitle-1 font-weight-medium">版本比較與變更設計</span>
              </div>
              <v-chip
                v-if="versionSummary"
                size="small"
                color="#3ea0a3"
                variant="outlined"
              >
                v{{ versionSummary.first_version.version }} → v{{ versionSummary.latest_version.version }}
              </v-chip>
            </v-card-title>

            <v-card-text class="pa-4">
              <div
                v-if="versionComparisonLoading"
                class="text-center py-8"
              >
                <v-progress-circular
                  indeterminate
                  color="#3ea0a3"
                  size="64"
                  class="mb-3"
                />
                <div class="text-body-1">
                  載入版本比較資料中...
                </div>
              </div>

              <v-sheet
                v-else-if="facilitiesComparison && !versionComparisonLoading && !versionComparisonError"
                class="pa-3 rounded"
                color="grey-lighten-5"
              >
                <v-alert
                  v-if="facilitiesComparison.summary.total_changes > 0"
                  type="info"
                  variant="tonal"
                  class="mb-4"
                >
                  <div class="d-flex align-center">
                    <span>
                      偵測到 {{ facilitiesComparison.summary.total_changes }} 項設施變更，
                      {{ facilitiesComparison.summary.has_irrigation_changes ? '包含灌溉調控設施' : '' }}
                      {{ facilitiesComparison.summary.has_irrigation_changes && facilitiesComparison.summary.has_pipeline_changes ? '和' : '' }}
                      {{ facilitiesComparison.summary.has_pipeline_changes ? '田間管路設施' : '' }}
                    </span>
                  </div>
                </v-alert>

                <v-alert
                  v-else
                  type="success"
                  variant="tonal"
                  class="mb-4"
                >
                  <div class="d-flex align-center">
                    <span>設施配置與第一版本相同，無變更。</span>
                  </div>
                </v-alert>

                <div
                  v-if="facilitiesComparison.irrigation_control_facilities.length > 0"
                  class="mb-6"
                >
                  <h4 class="text-h6 mb-3 d-flex align-center">
                    <v-icon
                      class="me-2"
                      color="#3ea0a3"
                    >
                      mdi-water
                    </v-icon>
                    灌溉調控設施表
                  </h4>
                  <v-table class="design-change-table border-table">
                    <thead>
                      <tr>
                        <th>設施項目</th>
                        <th>規格</th>
                        <th>第一版數量</th>
                        <th>最新版數量</th>
                        <th>增減數量</th>
                        <th>單位</th>
                        <th>變更狀態</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr
                        v-for="(item, index) in facilitiesComparison.irrigation_control_facilities"
                        :key="`irrigation-${index}`"
                        :class="{
                          'bg-green-lighten-5': item.changeType === 'added',
                          'bg-red-lighten-5': item.changeType === 'removed',
                          'bg-yellow-lighten-5': item.changeType === 'modified'
                        }"
                      >
                        <td>{{ item.name }}</td>
                        <td>{{ item.specification || '-' }}</td>
                        <td class="text-center">
                          {{ item.beforeQuantity }}
                        </td>
                        <td class="text-center">
                          {{ item.afterQuantity }}
                        </td>
                        <td class="text-center">
                          <span
                            :class="{
                              'text-green-darken-2': item.quantityChange > 0,
                              'text-red-darken-2': item.quantityChange < 0
                            }"
                          >
                            {{ item.quantityChange > 0 ? '+' : '' }}{{ item.quantityChange }}
                          </span>
                        </td>
                        <td class="text-center">
                          {{ item.unit }}
                        </td>
                        <td class="text-center">
                          <v-chip
                            size="x-small"
                            :color="getChangeStatusColor(item.changeType)"
                            variant="flat"
                          >
                            {{ getChangeStatusText(item.changeType) }}
                          </v-chip>
                        </td>
                      </tr>
                    </tbody>
                  </v-table>
                </div>

                <div
                  v-if="facilitiesComparison.pipeline_facilities.length > 0"
                  class="mb-4"
                >
                  <h4 class="text-h6 mb-3 d-flex align-center">
                    <v-icon
                      class="me-2"
                      color="#3ea0a3"
                    >
                      mdi-pipe
                    </v-icon>
                    田間管路設施表
                  </h4>
                  <v-table class="design-change-table border-table">
                    <thead>
                      <tr>
                        <th>設施項目</th>
                        <th>規格</th>
                        <th>第一版數量</th>
                        <th>最新版數量</th>
                        <th>增減數量</th>
                        <th>單位</th>
                        <th>變更狀態</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr
                        v-for="(item, index) in facilitiesComparison.pipeline_facilities"
                        :key="`pipeline-${index}`"
                        :class="{
                          'bg-green-lighten-5': item.changeType === 'added',
                          'bg-red-lighten-5': item.changeType === 'removed',
                          'bg-yellow-lighten-5': item.changeType === 'modified'
                        }"
                      >
                        <td>{{ item.name }}</td>
                        <td>{{ item.specification || '-' }}</td>
                        <td class="text-center">
                          {{ item.beforeQuantity }}
                        </td>
                        <td class="text-center">
                          {{ item.afterQuantity }}
                        </td>
                        <td class="text-center">
                          <span
                            :class="{
                              'text-green-darken-2': item.quantityChange > 0,
                              'text-red-darken-2': item.quantityChange < 0
                            }"
                          >
                            {{ item.quantityChange > 0 ? '+' : '' }}{{ item.quantityChange }}
                          </span>
                        </td>
                        <td class="text-center">
                          {{ item.unit }}
                        </td>
                        <td class="text-center">
                          <v-chip
                            size="x-small"
                            :color="getChangeStatusColor(item.changeType)"
                            variant="flat"
                          >
                            {{ getChangeStatusText(item.changeType) }}
                          </v-chip>
                        </td>
                      </tr>
                    </tbody>
                  </v-table>
                </div>

                <v-card
                  v-if="facilitiesComparison.summary.total_changes > 0"
                  variant="outlined"
                  color="#3ea0a3"
                  class="mt-4"
                >
                  <v-card-text class="pa-3">
                    <div class="d-flex align-center">
                      <v-icon
                        color="#3ea0a3"
                        class="mr-2"
                      >
                        mdi-sigma
                      </v-icon>
                      <div>
                        <div class="text-subtitle-2 font-weight-medium">
                          變更總計：{{ facilitiesComparison.summary.total_changes }} 項設施
                        </div>
                        <div class="text-caption text-medium-emphasis">
                          設施配置已根據實際需求進行調整
                        </div>
                      </div>
                    </div>
                  </v-card-text>
                </v-card>
              </v-sheet>

              <v-alert
                v-else-if="versionComparisonError"
                type="error"
                variant="tonal"
                class="mb-4"
              >
                <div class="d-flex align-center">
                  <v-icon class="me-2">
                    mdi-alert-circle
                  </v-icon>
                  <span>{{ versionComparisonError }}</span>
                </div>
              </v-alert>

              <div
                v-else
                class="pa-3 text-center text-caption text-medium-emphasis"
              >
                載入狀態: {{ versionComparisonLoading }},
                有錯誤: {{ !!versionComparisonError }},
                有比較資料: {{ !!facilitiesComparison }},
                版本摘要: {{ !!versionSummary }}
              </div>
            </v-card-text>
          </v-card>
          -->

          <!-- 結案申報基本資訊區域 -->
          <v-card
            class="pa-0 mx-0"
            flat
          >
            <v-card-text class="pa-0 ">
              <v-card-title
                class="text-subtitle-1 font-weight-bold pa-0 pb-2 d-flex align-center"
                style="color: #2d8c8f"
              >
                <v-icon
                  color="#3ea0a3"
                  class="me-2 mb-0 pb-0"
                  size="small"
                >
                  mdi-clipboard-text
                </v-icon>
                本案基本資訊
              </v-card-title>

              <v-sheet
                class="mt-2 pb-4 rounded"
                color="white"
              >
                <v-table
                  density="compact"
                  fixed-header
                  class="border-thin"
                >
                  <tbody>
                    <tr>
                      <td
                        class="font-weight-medium text-center"
                        style="width: 15%; background-color: rgba(255, 224, 130, 0.15)"
                      >
                        申請年度
                      </td>
                      <td style="width: 35%">
                        {{ displayApplicationYear }}
                      </td>
                      <td
                        class="font-weight-medium text-center"
                        style="width: 15%; background-color: rgba(255, 224, 130, 0.15)"
                      >
                        案號
                      </td>
                      <td style="width: 35%">
                        {{ formatCaseNumber(displayCaseNumber) }}
                      </td>
                    </tr>
                    <tr>
                      <td
                        class="font-weight-medium text-center"
                        style="background-color: rgba(255, 224, 130, 0.15)"
                      >
                        農戶姓名
                      </td>
                      <td>
                        {{ displayApplicantName }}
                      </td>
                      <td
                        class="font-weight-medium text-center"
                        style="background-color: rgba(255, 224, 130, 0.15)"
                      >
                        農戶住址
                      </td>
                      <td>
                        {{ displayApplicantAddress }}
                      </td>
                    </tr>
                    <tr>
                      <td
                        class="font-weight-medium text-center"
                        style="background-color: rgba(255, 224, 130, 0.15)"
                      >
                        設施地段
                      </td>
                      <td>
                        <!-- 多筆土地時，地段與地號一一對應顯示 -->
                        <div v-if="displayFacilityLocationPairs.length > 1">
                          <div
                            v-for="(pair, index) in displayFacilityLocationPairs"
                            :key="index"
                            class="mb-1"
                          >
                            {{ pair.location || '-' }}
                          </div>
                        </div>
                        <div v-else>
                          {{ displayFacilityLocationPairs[0]?.location || '-' }}
                        </div>
                      </td>
                      <td
                        class="font-weight-medium text-center"
                        style="background-color: rgba(255, 224, 130, 0.15)"
                      >
                        設施地號
                      </td>
                      <td>
                        <!-- 多筆土地時，地號與地段一一對應顯示 -->
                        <div v-if="displayFacilityLocationPairs.length > 1">
                          <div
                            v-for="(pair, index) in displayFacilityLocationPairs"
                            :key="index"
                            class="mb-1"
                          >
                            {{ pair.number || '-' }}
                          </div>
                        </div>
                        <div v-else>
                          {{ displayFacilityLocationPairs[0]?.number || '-' }}
                        </div>
                      </td>
                    </tr>
                    <tr>
                      <td
                        class="font-weight-medium text-center"
                        style="background-color: rgba(255, 224, 130, 0.15)"
                      >
                        設施面積
                      </td>
                      <td>
                        {{ displayFacilityArea }}公頃
                      </td>
                      <td
                        class="font-weight-medium text-center"
                        style="background-color: rgba(255, 224, 130, 0.15)"
                      >
                        設施型式
                      </td>
                      <td>
                        {{ displayFacilityType }}
                      </td>
                    </tr>
                  </tbody>
                </v-table>
              </v-sheet>
            </v-card-text>
          </v-card>

          <!-- 竣工和測試資訊區域 -->
          <v-card
            flat
            class="mb-4 pa-4"
            color="#e3f4f4"
            rounded="lg"
          >
            <v-card-title
              class="text-subtitle-1 font-weight-bold pa-0 pb-4 d-flex align-center flex-wrap"
              style="color: #2d8c8f"
            >
              <v-icon
                color="#3ea0a3"
                class="me-2 pb-1"
                size="small"
              >
                mdi-check-decagram
              </v-icon>
              功能測試資訊
              <v-spacer />
              <!-- 僅當狀態為 withdrawn 時顯示複驗 checkbox -->
              <v-checkbox
                v-if="shouldShowReinspectionCheckbox"
                v-model="localFormData.isReinspection"
                label="複驗"
                color="#3ea0a3"
                density="compact"
                hide-details
                readonly
                @update:model-value="updateFormData"
              >
                <template #label>
                  <span class="text-grey-darken-2">
                    複驗（{{ localFormData.improvementDate ? formattedImprovementDate : '待設定改善完成日期' }}前完成改善）
                  </span>
                </template>
              </v-checkbox>
            </v-card-title>

            <v-card-text class="pa-0">
              <v-sheet
                class="pa-3 rounded"
                color="white"
              >
                <v-row>
                  <v-col
                    cols="12"
                    md="6"
                  >
                    <v-text-field
                      v-model="formattedCompletionDate"
                      variant="outlined"
                      density="comfortable"
                      readonly
                      prepend-icon="mdi-calendar"
                      :rules="[v => !!localFormData.completionDate || '請選擇申報結案日期']"
                      @click="openDateDialog('completion')"
                      @update:model-value="updateFormData"
                    >
                      <template #label>
                        申報結案日期
                      </template>
                    </v-text-field>

                    <!-- 自定義日期選擇對話框 -->
                    <v-dialog
                      v-model="datePickerDialog1"
                      width="600"
                    >
                      <v-card>
                        <v-card-title
                          class="text-h6 font-weight-bold"
                          style="color: #2d8c8f"
                        >
                          選擇申報結案日期
                        </v-card-title>
                        <v-card-text>
                          <v-row>
                            <v-col cols="4">
                              <v-select
                                v-model="completionDateComponents.year"
                                :items="yearOptions"
                                label="年"
                                variant="outlined"
                                density="comfortable"
                                color="#3ea0a3"
                              />
                            </v-col>
                            <v-col cols="4">
                              <v-select
                                v-model="completionDateComponents.month"
                                :items="monthOptions"
                                label="月"
                                variant="outlined"
                                density="comfortable"
                                color="#3ea0a3"
                              />
                            </v-col>
                            <v-col cols="4">
                              <v-select
                                v-model="completionDateComponents.day"
                                :items="dayOptions('completion')"
                                label="日"
                                variant="outlined"
                                density="comfortable"
                                color="#3ea0a3"
                              />
                            </v-col>
                          </v-row>
                        </v-card-text>
                        <v-card-actions>
                          <v-spacer />
                          <v-btn
                            variant="text"
                            @click="datePickerDialog1 = false"
                          >
                            取消
                          </v-btn>
                          <v-btn
                            color="#3ea0a3"
                            variant="text"
                            @click="confirmDateSelection('completion')"
                          >
                            確定
                          </v-btn>
                        </v-card-actions>
                      </v-card>
                    </v-dialog>
                  </v-col>
                  <v-col
                    v-if="!localFormData.isReinspection"
                    cols="12"
                    md="6"
                  >
                    <div class="d-flex align-center">
                      <v-text-field
                        v-model="localFormData.tester"
                        variant="outlined"
                        density="comfortable"
                        :rules="[v => !!v || '請填寫測試人員']"
                        prepend-icon="mdi-account"
                        class="flex-grow-1 me-2"
                        hide-details="auto"
                        @update:model-value="updateFormData"
                      >
                        <template #label>
                          測試人員
                        </template>
                      </v-text-field>

                      <v-select
                        label="快速選擇"
                        :items="availableTesters"
                        variant="outlined"
                        density="comfortable"
                        color="#3ea0a3"
                        bg-color="white"
                        hide-details="auto"
                        style="max-width: 140px;"
                        :disabled="availableTesters.length === 0"
                        @update:model-value="onTesterSelect"
                      >
                        <template #no-data>
                          <div class="px-4 py-2 text-caption text-grey">
                            尚無該單位人員資料
                          </div>
                        </template>
                      </v-select>
                    </div>
                  </v-col>
                  <v-col
                    v-if="localFormData.isReinspection"
                    cols="12"
                    md="6"
                  >
                    <div class="d-flex align-center">
                      <v-text-field
                        v-model="localFormData.reinspectionTester"
                        variant="outlined"
                        density="comfortable"
                        :rules="localFormData.isReinspection ? [v => !!v || '請填寫複驗人員'] : []"
                        prepend-icon="mdi-account"
                        class="flex-grow-1 me-2"
                        hide-details="auto"
                        @update:model-value="updateFormData"
                      >
                        <template #label>
                          複驗人員
                        </template>
                      </v-text-field>

                      <v-select
                        label="快速選擇"
                        :items="availableTesters"
                        variant="outlined"
                        density="comfortable"
                        color="#3ea0a3"
                        bg-color="white"
                        hide-details="auto"
                        style="max-width: 140px;"
                        :disabled="availableTesters.length === 0"
                        @update:model-value="onReinspectionTesterSelect"
                      >
                        <template #no-data>
                          <div class="px-4 py-2 text-caption text-grey">
                            尚無該單位人員資料
                          </div>
                        </template>
                      </v-select>
                    </div>
                  </v-col>
                </v-row>

                <!-- 非複驗狀態下顯示原測試日期和人員 -->
                <v-row>
                  <v-col
                    v-if="!localFormData.isReinspection"
                    cols="12"
                    md="6"
                  >
                    <v-text-field
                      v-model="formattedTestDate"
                      variant="outlined"
                      density="comfortable"
                      readonly
                      prepend-icon="mdi-calendar"
                      :rules="[v => !!localFormData.testDate || '請選擇功能測試日期']"
                      @click="openDateDialog('test')"
                      @update:model-value="updateFormData"
                    >
                      <template #label>
                        功能測試日期
                      </template>
                    </v-text-field>

                    <!-- 自定義日期選擇對話框 -->
                    <v-dialog
                      v-model="datePickerDialog2"
                      width="600"
                    >
                      <v-card>
                        <v-card-title
                          class="text-h6 font-weight-bold"
                          style="color: #2d8c8f"
                        >
                          選擇功能測試日期
                        </v-card-title>
                        <v-card-text>
                          <v-row>
                            <v-col cols="4">
                              <v-select
                                v-model="testDateComponents.year"
                                :items="yearOptions"
                                label="年"
                                variant="outlined"
                                density="comfortable"
                                color="#3ea0a3"
                              />
                            </v-col>
                            <v-col cols="4">
                              <v-select
                                v-model="testDateComponents.month"
                                :items="monthOptions"
                                label="月"
                                variant="outlined"
                                density="comfortable"
                                color="#3ea0a3"
                              />
                            </v-col>
                            <v-col cols="4">
                              <v-select
                                v-model="testDateComponents.day"
                                :items="dayOptions('test')"
                                label="日"
                                variant="outlined"
                                density="comfortable"
                                color="#3ea0a3"
                              />
                            </v-col>
                          </v-row>
                        </v-card-text>
                        <v-card-actions>
                          <v-spacer />
                          <v-btn
                            variant="text"
                            @click="datePickerDialog2 = false"
                          >
                            取消
                          </v-btn>
                          <v-btn
                            color="#3ea0a3"
                            variant="text"
                            @click="confirmDateSelection('test')"
                          >
                            確定
                          </v-btn>
                        </v-card-actions>
                      </v-card>
                    </v-dialog>
                  </v-col>
                  <v-col
                    v-if="localFormData.isReinspection"
                    cols="12"
                    md="6"
                  >
                    <v-text-field
                      v-model="formattedReinspectionDate"
                      variant="outlined"
                      density="comfortable"
                      readonly
                      prepend-icon="mdi-calendar"
                      :rules="localFormData.isReinspection ? [v => !!localFormData.reinspectionDate || '請選擇功能複驗日期'] : []"
                      @click="openDateDialog('reinspection')"
                      @update:model-value="updateFormData"
                    >
                      <template #label>
                        功能複驗日期
                      </template>
                    </v-text-field>

                    <!-- 複驗日期選擇對話框 -->
                    <v-dialog
                      v-model="datePickerDialog3"
                      width="600"
                    >
                      <v-card>
                        <v-card-title
                          class="text-h6 font-weight-bold"
                          style="color: #2d8c8f"
                        >
                          選擇功能複驗日期
                        </v-card-title>
                        <v-card-text>
                          <v-row>
                            <v-col cols="4">
                              <v-select
                                v-model="reinspectionDateComponents.year"
                                :items="yearOptions"
                                label="年"
                                variant="outlined"
                                density="comfortable"
                                color="#3ea0a3"
                              />
                            </v-col>
                            <v-col cols="4">
                              <v-select
                                v-model="reinspectionDateComponents.month"
                                :items="monthOptions"
                                label="月"
                                variant="outlined"
                                density="comfortable"
                                color="#3ea0a3"
                              />
                            </v-col>
                            <v-col cols="4">
                              <v-select
                                v-model="reinspectionDateComponents.day"
                                :items="dayOptions('reinspection')"
                                label="日"
                                variant="outlined"
                                density="comfortable"
                                color="#3ea0a3"
                              />
                            </v-col>
                          </v-row>
                        </v-card-text>
                        <v-card-actions>
                          <v-spacer />
                          <v-btn
                            variant="text"
                            @click="datePickerDialog3 = false"
                          >
                            取消
                          </v-btn>
                          <v-btn
                            color="#3ea0a3"
                            variant="text"
                            @click="confirmDateSelection('reinspection')"
                          >
                            確定
                          </v-btn>
                        </v-card-actions>
                      </v-card>
                    </v-dialog>
                  </v-col>
                  <v-col
                    cols="12"
                    md="6"
                  >
                    <div class="d-flex flex-row gap-3">
                      <v-sheet
                        class="py-0 pl-5 rounded flex-1"
                        color="white"
                      >
                        <label class="text-body-2 font-weight-medium mb-0 d-block">與設計圖說規劃型式</label>
                        <v-radio-group
                          v-model="localFormData.designCompliance"
                          color="#3ea0a3"
                          density="comfortable"
                          hide-details
                          inline
                          @update:model-value="updateFormData"
                        >
                          <v-radio
                            label="相符"
                            value="compliant"
                          />
                          <v-radio
                            label="不符"
                            value="non-compliant"
                          />
                        </v-radio-group>
                      </v-sheet>
                      <v-spacer />
                      <v-sheet
                        class="py-0 pr-5 rounded flex-1"
                        color="white"
                      >
                        <label class="text-body-2 font-weight-medium mb-0 d-block">經現場運轉功能</label>
                        <v-radio-group
                          v-model="localFormData.operationCompliance"
                          color="#3ea0a3"
                          density="comfortable"
                          hide-details
                          inline
                          @update:model-value="updateFormData"
                        >
                          <v-radio
                            label="相符"
                            value="compliant"
                          />
                          <v-radio
                            label="不符"
                            value="non-compliant"
                          />
                        </v-radio-group>
                      </v-sheet>
                    </div>
                  </v-col>
                </v-row>

                <!-- 測試結果 - 非複驗狀態顯示 -->
                <v-row v-if="!localFormData.isReinspection">
                  <v-col cols="12">
                    <v-select
                      v-model="localFormData.testResult"
                      :items="dynamicTestResultOptions"
                      variant="outlined"
                      density="comfortable"
                      :rules="[v => !!v || '請選擇測試結果']"
                      prepend-icon="mdi-clipboard-check"
                      @update:model-value="updateFormData"
                    >
                      <template #label>
                        測試結果
                      </template>
                    </v-select>
                  </v-col>
                </v-row>

                <!-- 複驗結果 - 複驗狀態顯示 -->
                <v-row v-if="localFormData.isReinspection">
                  <v-col cols="12">
                    <v-select
                      v-model="localFormData.reinspectionResult"
                      :items="dynamicTestResultOptions"
                      variant="outlined"
                      density="comfortable"
                      :rules="localFormData.isReinspection ? [v => !!v || '請選擇複驗結果'] : []"
                      prepend-icon="mdi-clipboard-check"
                      @update:model-value="updateFormData"
                    >
                      <template #label>
                        複驗結果
                      </template>
                    </v-select>
                  </v-col>
                </v-row>
              </v-sheet>

              <!-- 功能測試(驗收)結果區域 -->
              <v-sheet
                class="my-3 pa-3 rounded"
                color="white"
              >
                <div class="d-flex align-center mb-2">
                  <v-icon
                    size="small"
                    class="me-2"
                  >
                    mdi-check-circle
                  </v-icon>
                  <span class="text-body-2 font-weight-medium"><span class="required-asterisk">*</span>功能測試（驗收）結果</span>
                </div>
                <v-sheet
                  class="pa-3 rounded"
                  color="bg-amber-lighten-5 border border-amber"
                >
                  <!-- 合格（未減列）：原應發放 + 實際發放 並列 -->
                  <v-row v-if="(localFormData.isReinspection ? localFormData.reinspectionResult : localFormData.testResult) === 'original'">
                    <v-col
                      cols="12"
                      md="6"
                    >
                      <v-text-field
                        v-model="localFormData.originalPayment"
                        label="原應發放"
                        variant="outlined"
                        density="comfortable"
                        readonly
                        hide-details
                        bg-color="yellow-lighten-3"
                        @update:model-value="updateFormData"
                      />
                    </v-col>
                    <v-col
                      cols="12"
                      md="6"
                    >
                      <v-text-field
                        v-model="localFormData.actualPayment"
                        label="實際發放"
                        variant="outlined"
                        density="comfortable"
                        readonly
                        hide-details
                        bg-color="yellow-lighten-3"
                        @update:model-value="updateFormData"
                      />
                    </v-col>
                  </v-row>

                  <!-- 部分合格（減列）：減列 + 實際發放 並列 -->
                  <v-row v-if="(localFormData.isReinspection ? localFormData.reinspectionResult : localFormData.testResult) === 'adjusted'">
                    <v-col
                      cols="12"
                      md="6"
                    >
                      <v-text-field
                        v-model="localFormData.increasedDecreasedAmount"
                        variant="outlined"
                        density="comfortable"
                        type="text"
                        inputmode="numeric"
                        :rules="(localFormData.isReinspection ? localFormData.reinspectionResult : localFormData.testResult) === 'adjusted' ? [
                          v => !!v || '請填寫減列金額',
                          v => {
                            const num = parseFloat(v.replace(/,/g, ''));
                            return !isNaN(num) && num > 0 || '減列金額必須大於 0';
                          }
                        ] : []"
                        hide-details
                        bg-color="white"
                        prepend-inner-icon="mdi-pencil"
                        color="#3ea0a3"
                        placeholder="請輸入減列金額"
                        @update:model-value="handleDeductionAmountInput"
                      >
                        <template #label>
                          <span class="text-red-darken-2 font-weight-medium">
                            <v-icon
                              size="small"
                              class="mr-1"
                            >
                              mdi-currency-usd
                            </v-icon>
                            減列
                          </span>
                        </template>
                      </v-text-field>
                    </v-col>
                    <v-col
                      cols="12"
                      md="6"
                    >
                      <v-text-field
                        v-model="localFormData.actualPayment"
                        label="實際發放"
                        variant="outlined"
                        density="comfortable"
                        readonly
                        hide-details
                        bg-color="yellow-lighten-3"
                        @update:model-value="updateFormData"
                      />
                    </v-col>
                  </v-row>

                  <!-- 結果說明（合格/減列時獨立一列） -->
                  <v-row v-if="(localFormData.isReinspection ? localFormData.reinspectionResult : localFormData.testResult) !== 'improvement'">
                    <v-col cols="12">
                      <v-textarea
                        v-model="localFormData.testResultDescription"
                        label="結果說明（系統產生）"
                        variant="outlined"
                        density="comfortable"
                        rows="1"
                        auto-grow
                        readonly
                        bg-color="grey-lighten-4"
                        hint="此欄位由系統自動產生，不可修改"
                        persistent-hint
                      >
                        <template #label>
                          結果說明（系統產生）
                        </template>
                      </v-textarea>
                    </v-col>
                  </v-row>

                  <!-- 不合格（需改善）：結果說明 + 改善完成日期 並列 -->
                  <v-row v-if="(localFormData.isReinspection ? localFormData.reinspectionResult : localFormData.testResult) === 'improvement'">
                    <v-col
                      cols="12"
                      md="6"
                    >
                      <v-textarea
                        v-model="localFormData.testResultDescription"
                        label="結果說明（系統產生）"
                        variant="outlined"
                        density="comfortable"
                        rows="1"
                        auto-grow
                        readonly
                        bg-color="grey-lighten-4"
                        :rules="[v => !!v || '請填寫結果說明']"
                        hint="此欄位由系統自動產生，不可修改"
                        persistent-hint
                      >
                        <template #label>
                          結果說明（系統產生）
                        </template>
                      </v-textarea>
                    </v-col>
                    <v-col
                      cols="12"
                      md="6"
                    >
                      <v-text-field
                        v-model="formattedImprovementDate"
                        label="改善完成日期"
                        variant="outlined"
                        density="comfortable"
                        readonly
                        prepend-icon="mdi-calendar"
                        :rules="[
                          v => !!localFormData.improvementDate || '請選擇改善完成日期',
                          v => {
                            if (!localFormData.improvementDate) return true;
                            const selected = new Date(localFormData.improvementDate);
                            const today = new Date();
                            today.setHours(0, 0, 0, 0);
                            return selected > today || '改善完成日期範圍有誤';
                          }
                        ]"
                        hint="請選擇預計完成改善的日期"
                        persistent-hint
                        @click="openDateDialog('improvement')"
                        @update:model-value="updateFormData"
                      >
                        <template #label>
                          <span class="required-asterisk">*</span>改善完成日期
                        </template>
                      </v-text-field>

                      <!-- 改善日期選擇對話框 -->
                      <v-dialog
                        v-model="datePickerDialog4"
                        width="600"
                      >
                        <v-card>
                          <v-card-title
                            class="text-h6 font-weight-bold"
                            style="color: #2d8c8f"
                          >
                            選擇改善完成日期
                          </v-card-title>
                          <v-card-text>
                            <v-row>
                              <v-col cols="4">
                                <v-select
                                  v-model="improvementDateComponents.year"
                                  :items="yearOptions"
                                  label="年"
                                  variant="outlined"
                                  density="comfortable"
                                  color="#3ea0a3"
                                />
                              </v-col>
                              <v-col cols="4">
                                <v-select
                                  v-model="improvementDateComponents.month"
                                  :items="monthOptions"
                                  label="月"
                                  variant="outlined"
                                  density="comfortable"
                                  color="#3ea0a3"
                                />
                              </v-col>
                              <v-col cols="4">
                                <v-select
                                  v-model="improvementDateComponents.day"
                                  :items="dayOptions('improvement')"
                                  label="日"
                                  variant="outlined"
                                  density="comfortable"
                                  color="#3ea0a3"
                                />
                              </v-col>
                            </v-row>
                          </v-card-text>
                          <v-card-actions>
                            <v-spacer />
                            <v-btn
                              variant="text"
                              @click="datePickerDialog4 = false"
                            >
                              取消
                            </v-btn>
                            <v-btn
                              color="#3ea0a3"
                              variant="text"
                              @click="confirmDateSelection('improvement')"
                            >
                              確定
                            </v-btn>
                          </v-card-actions>
                        </v-card>
                      </v-dialog>
                    </v-col>
                  </v-row>

                  <v-row>
                    <v-col cols="12">
                      <v-textarea
                        v-model="localFormData.additionalNotes"
                        :label="additionalNotesLabel"
                        variant="outlined"
                        density="comfortable"
                        rows="3"
                        auto-grow
                        :placeholder="additionalNotesPlaceholder"
                        :hint="additionalNotesHint"
                        persistent-hint
                        :rules="additionalNotesRules"
                        @update:model-value="updateFormData"
                      >
                        <template #label>
                          {{ additionalNotesLabel }}
                        </template>
                      </v-textarea>
                    </v-col>
                  </v-row>
                </v-sheet>
              </v-sheet>

              <!-- 照片上傳區域 -->
              <v-sheet
                class="mt-3 pa-3 rounded"
                color="white"
              >
                <div class="d-flex align-center">
                  <v-icon
                    size="small"
                    class="me-2"
                  >
                    mdi-camera
                  </v-icon>
                  <span class="text-body-2 font-weight-medium">施工前照片</span>
                </div>
                <!-- 施工前照片區域（從 UI step3 載入，只讀） -->
                <v-sheet
                  class="pa-3 rounded mb-4"
                  color="white"
                >
                  <!-- 已載入的施工前照片展示 -->
                  <div v-if="localFormData.beforePhotoPreviews && localFormData.beforePhotoPreviews.length > 0">
                    <v-row>
                      <v-col
                        v-for="(preview, index) in localFormData.beforePhotoPreviews"
                        :key="`before-${index}`"
                        cols="6"
                        sm="4"
                        md="3"
                      >
                        <v-card
                          variant="outlined"
                          class="photo-card"
                        >
                          <v-img
                            :src="preview"
                            height="120"
                            cover
                            class="rounded-t"
                          />
                          <v-card-text class="pa-2 text-center">
                            <div class="text-caption text-grey-darken-1">
                              第 {{ index + 1 }} 張照片
                            </div>
                          </v-card-text>
                        </v-card>
                      </v-col>
                    </v-row>
                  </div>

                  <!-- 無施工前照片提示 -->
                  <div
                    v-else
                    class="text-center py-4"
                  >
                    <v-icon
                      size="48"
                      color="grey-lighten-1"
                      class="mb-2"
                    >
                      mdi-image-off-outline
                    </v-icon>
                    <div class="text-body-2 text-grey">
                      尚未在 Step 5 上傳施工前照片
                    </div>
                  </div>
                </v-sheet>

                <div class="d-flex align-center">
                  <v-icon
                    size="small"
                    class="me-2"
                  >
                    mdi-camera
                  </v-icon>
                  <span class="text-body-2 font-weight-medium"><span class="required-asterisk">*</span>竣工照片</span>
                  <span class="ml-2 text-grey text-caption">(需要1-3張照片)</span>
                </div>

                <!-- 竣工照片區域（可上傳） -->
                <v-sheet
                  class="pa-3 rounded"
                  color="white"
                >
                  <!-- 已上傳竣工照片展示區域 -->
                  <div
                    v-if="localFormData.afterPhotoPreviews && localFormData.afterPhotoPreviews.length > 0"
                    class="mb-3"
                  >
                    <v-row>
                      <v-col
                        v-for="(preview, index) in localFormData.afterPhotoPreviews"
                        :key="`after-${index}`"
                        cols="6"
                        sm="4"
                        md="3"
                      >
                        <v-card
                          variant="outlined"
                          class="photo-card"
                        >
                          <div class="position-relative">
                            <v-img
                              :src="preview"
                              height="120"
                              cover
                              class="rounded-t"
                            />
                            <v-btn
                              icon
                              size="x-small"
                              color="error"
                              variant="elevated"
                              class="position-absolute"
                              style="top: 8px; right: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.3);"
                              :disabled="props.readonly"
                              @click="removeAfterPhoto(index)"
                            >
                              <v-icon size="small">
                                mdi-close
                              </v-icon>
                            </v-btn>
                          </div>
                          <v-card-text class="pa-2 text-center">
                            <div class="text-caption text-grey-darken-1">
                              第 {{ index + 1 }} 張照片
                            </div>
                          </v-card-text>
                        </v-card>
                      </v-col>

                      <!-- 新增照片按鈕 (當未達到3張時顯示) -->
                      <v-col
                        v-if="localFormData.afterPhotoPreviews.length < 3"
                        cols="6"
                        sm="4"
                        md="3"
                      >
                        <v-card
                          variant="outlined"
                          class="photo-card add-photo-card"
                          :disabled="props.readonly"
                          @click="triggerAfterFileInput"
                        >
                          <div class="d-flex flex-column align-center justify-center h-100">
                            <v-icon
                              size="40"
                              color="grey-lighten-1"
                              class="mb-2"
                            >
                              mdi-plus-circle-outline
                            </v-icon>
                            <div class="text-caption text-grey text-center">
                              新增照片<br>
                              <span class="text-xs">({{ localFormData.afterPhotoPreviews.length }}/3)</span>
                            </div>
                          </div>
                        </v-card>
                      </v-col>
                    </v-row>
                  </div>

                  <!-- 初次上傳區域 (當沒有竣工照片時顯示) -->
                  <div v-if="localFormData.afterPhotoPreviews.length === 0">
                    <v-card
                      variant="outlined"
                      class="upload-zone"
                      @click="!props.readonly && triggerAfterFileInput()"
                    >
                      <v-card-text class="text-center pa-8">
                        <v-icon
                          size="48"
                          color="grey-lighten-1"
                          class="mb-3"
                        >
                          mdi-camera-plus-outline
                        </v-icon>
                        <div class="text-h6 text-grey-darken-1 mb-2">
                          上傳竣工照片
                        </div>
                        <div class="text-body-2 text-grey">
                          點擊選擇照片檔案<br>
                          <span class="text-caption">支援 JPG、PNG 格式，需要 1-3 張照片</span>
                        </div>
                      </v-card-text>
                    </v-card>
                  </div>

                  <!-- 隱藏的檔案輸入框 -->
                  <input
                    ref="afterFileInput"
                    type="file"
                    accept="image/*"
                    style="display: none"
                    @change="handleAfterPhotoUpload"
                  >

                  <!-- 上傳狀態提示 -->
                  <div
                    v-if="localFormData.afterPhotoPreviews.length > 0 && !props.readonly"
                    class="mt-2"
                  >
                    <v-chip
                      :color="getUploadStatusColor()"
                      variant="tonal"
                      size="small"
                    >
                      <v-icon
                        start
                        size="small"
                      >
                        {{ getUploadStatusIcon() }}
                      </v-icon>
                      {{ getUploadStatusText() }}
                    </v-chip>
                  </div>
                </v-sheet>
              </v-sheet>
            </v-card-text>
          </v-card>
        </v-form>
      </v-card-text>
    </v-card>

    <!-- 存檔確認對話框 -->
    <v-dialog
      v-model="saveConfirmDialog"
      max-width="500"
      persistent
    >
      <v-card>
        <v-card-title class="text-h6 font-weight-bold bg-orange-lighten-4 pa-4">
          <v-icon
            class="me-2"
            color="orange-darken-2"
          >
            mdi-alert-circle
          </v-icon>
          存檔確認
        </v-card-title>
        <v-card-text class="pa-6">
          <p class="mb-4 text-body-1">
            目前現場勘查後未通過驗收，將於改善後複驗。
          </p>
          <p class="mb-0 text-body-2 text-grey-darken-1">
            請確認是否要存檔此狀態？存檔後可在改善完成後進行複驗作業。
          </p>
        </v-card-text>
        <v-card-actions class="pa-4">
          <v-spacer />
          <v-btn
            color="grey"
            variant="outlined"
            @click="saveConfirmDialog = false"
          >
            取消
          </v-btn>
          <v-btn
            color="orange-darken-2"
            variant="flat"
            @click="confirmSave"
          >
            確認存檔
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup lang="ts">
import { nextTick, computed, watch, watchEffect } from 'vue';
import { useRoute } from 'vue-router';
import { useGrantsStore } from '@/stores/grants';
import { useDomicileStore } from '@/stores/domicile';
import { useUserStore } from '@/stores/users'; //added by Joya
import { inspectors } from '@/data/inspectors';//added by Joya
// 導入版本比較相關服務
import {
  compareGrantVersions,
  getGrantVersionSummary,
  compareVersionsLocally,
  type FacilitiesComparison,
} from '@/services/grantsService';
// 導入附件服務（照片上傳）
import { attachmentService } from '@/services/attachmentService';
import { formatCaseNumber } from '@/utils/frontendFilters'
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
  },
  grantId: {
    type: Number,
    required: false,
    default: 0
  },
  readonly: {
    type: Boolean,
    required: false,
    default: false
  }
});

// Event emitters
const emit = defineEmits(['update:formData', 'validated', 'go-back', 'save-for-improvement', 'proceed-to-next-step', 'button-config-changed']);

// Access the grants store
const grantsStore = useGrantsStore();
// Joya 新增：測試/複驗人員下拉選單邏輯 ---
const userStore = useUserStore();
const availableTesters = computed(() => {
  const currentUser = userStore.currentUser;
  
  if (!currentUser) return [];

  let currentOfficeId: number | undefined;

  if (typeof currentUser.office === 'object' && currentUser.office !== null) {
    currentOfficeId = currentUser.office.id;
  } else if (typeof currentUser.office_id === 'number') {
    currentOfficeId = currentUser.office_id;
  }

  if (!currentOfficeId) return [];

  // 使用 is_inspector (驗收及勘查人員) 來篩選
  return inspectors
    .filter(i => 
      i.office_id === currentOfficeId && 
      i.is_inspector 
    )
    .map(i => i.name);
});

// 下拉選單選擇後填入 - 測試人員
const onTesterSelect = (value: string | null) => {
  if (value) {
    localFormData.tester = value;
  }
};

// 下拉選單選擇後填入 - 複驗人員
const onReinspectionTesterSelect = (value: string | null) => {
  if (value) {
    localFormData.reinspectionTester = value;
  }
};
// ------------------------------------
const domicileStore = useDomicileStore();
const route = useRoute();

// 判斷是否應該顯示複驗 checkbox（當狀態為 withdrawn 時顯示）
const shouldShowReinspectionCheckbox = computed(() => {
  return grantsStore.currentGrant?.status === 'withdrawn';
});

// 版本比較相關狀態
const versionComparisonLoading = ref(false);
const versionComparisonError = ref<string | null>(null);
const facilitiesComparison = ref<FacilitiesComparison | null>(null);
const versionSummary = ref<{
  total_versions: number;
  first_version: { id: number; version: number; created_at: string };
  latest_version: { id: number; version: number; created_at: string };
  has_versions: boolean;
} | null>(null);

// Form validation and dialogs
const form = ref(null);
const localValid = ref(true);
const datePickerDialog1 = ref(false);
const datePickerDialog2 = ref(false);
const datePickerDialog3 = ref(false); // 複驗日期對話框
const datePickerDialog4 = ref(false); // 改善完成日期對話框

// 移除括號內容的輔助函數（用於系統產生的結果說明）
const removeParenthesesContent = (text: string): string => {
  // 移除所有括號及其內容，包括全形和半形括號
  return text.replace(/[（(][^）)]*[）)]/g, '').trim();
};

// 測試結果選項 - 動態計算，包含對應的發放金額
const testResultOptions = computed(() => {
  // original 選項顯示原補助款金額
  const originalPaymentText = localFormData.originalPayment ? ` ${localFormData.originalPayment} 元` : '';

  // adjusted 選項顯示實際發放金額
  const actualPaymentText = localFormData.actualPayment ? ` ${localFormData.actualPayment} 元` : '';

  return [
    { title: `合格，依核定補助款發放${originalPaymentText}`, value: 'original' },
    { title: `合格，依核定補助款減列金額，發放${actualPaymentText}（請說明原因）`, value: 'adjusted' },
    { title: `不合格，限期改善複查（請註明完成改善日期）`, value: 'improvement' },
    { title: '不合格，取消補助資格', value: 'cancel' }
  ];
});

// 動態測試結果選項 - 根據複驗狀態和合規性顯示不同選項
const dynamicTestResultOptions = computed(() => {
  console.log('計算動態測試結果選項:', {
    designCompliance: localFormData.designCompliance,
    operationCompliance: localFormData.operationCompliance,
    isReinspection: localFormData.isReinspection
  });

  // 檢查是否有任一合規性為不符（non-compliant）
  const hasNonCompliant = localFormData.designCompliance === 'non-compliant' ||
                         localFormData.operationCompliance === 'non-compliant';

  if (hasNonCompliant) {
    // 有不符合項目時，根據複驗狀態顯示不同選項
    if (localFormData.isReinspection) {
      // 複驗狀態且有不符合項目：只顯示取消補助資格
      console.log('複驗狀態且有不符合項目，只顯示 cancel 選項');
      return testResultOptions.value.filter((option: any) =>
        option.value === 'cancel'
      );
    } else {
      // 非複驗狀態且有不符合項目：只顯示限期改善
      console.log('非複驗狀態且有不符合項目，只顯示 improvement 選項');
      return testResultOptions.value.filter((option: any) =>
        option.value === 'improvement'
      );
    }
  } else if (localFormData.isReinspection) {
    // 複驗狀態且無不符合項目：顯示 original, adjusted, cancel
    console.log('複驗狀態且無不符合項目，顯示 original, adjusted, cancel 選項');
    return testResultOptions.value.filter((option: any) =>
      ['original', 'adjusted', 'cancel'].includes(option.value)
    );
  } else {
    // 非複驗狀態且無不符合項目：顯示 original, adjusted, improvement
    console.log('非複驗狀態且無不符合項目，顯示 original, adjusted, improvement 選項');
    return testResultOptions.value.filter((option: any) =>
      ['original', 'adjusted', 'improvement'].includes(option.value)
    );
  }
});

// 追蹤用戶是否手動修改過結果說明
const isManuallyEditedDescription = ref(false);

// 追蹤是否正在自動同步結果說明（避免誤判為手動編輯）
const isAutoSyncingDescription = ref(false);

// 追蹤是否正在自動計算金額，避免循環觸發
const isAutoCalculatingAmount = ref(false);

// 計算按鈕配置 - 完整的按鈕配置信息
const buttonConfig = computed(() => {
  const shouldSave = !localFormData.isReinspection && localFormData.testResult === 'improvement';

  return {
    text: shouldSave ? '存檔' : '結案',
    color: shouldSave ? 'orange-darken-2' : '#3ea0a3',
    icon: shouldSave ? 'mdi-content-save' : 'mdi-arrow-right',
    action: shouldSave ? 'save' : 'proceed'
  };
});

// 提示訊息對話框狀態
const saveConfirmDialog = ref(false);

// 本地表單數據
const localFormData = reactive({
  // 基本資訊
  applicationYear: '',     // 申請年度
  caseNumber: '',          // 案號
  name: '',       // 農戶姓名
  applicantAddress: '',    // 農戶住址
  facilityLocation: '',    // 設施地段
  facilityNumber: '',      // 設施地號
  facilityAreaHa: '',        // 設施面積
  facilityType: '',        // 設施型式

  // 竣工資訊
  completionDate: '',      // 申報結案日期
  designCompliance: '',    // 與設計圖說規劃型式相符 ('compliant' | 'non-compliant')
  operationCompliance: '', // 經現場運轉功能相符 ('compliant' | 'non-compliant')
  testDate: '',            // 功能測試日期
  tester: '',              // 測試人員
  testResult: '',          // 測試結果

  // 複驗相關欄位
  isReinspection: false,   // 是否為複驗
  reinspectionDate: '',    // 功能複驗日期
  reinspectionTester: '',  // 複驗人員
  reinspectionResult: '',  // 複驗結果

  // 功能測試(驗收)結果
  originalPayment: '',          // 原應發放
  increasedDecreasedAmount: '', // 增減列
  actualPayment: '',            // 實際發放
  testResultDescription: '',    // 結果說明（系統產生）
  additionalNotes: '',          // 補充說明（使用者輸入）
  improvementDate: '',          // 改善完成日期（ISO格式）

  // 照片 - 改為陣列格式支援多張照片
  beforeConstructionPhotos: [] as File[],      // 施工前照片（從 UI step3 載入，只讀）
  afterConstructionPhotos: [] as File[],       // 竣工照片（可上傳）
  beforePhotoPreviews: [] as string[],         // 施工前照片預覽
  afterPhotoPreviews: [] as string[],          // 竣工照片預覽

  // 設置默認值，確保與edit.vue中的顯示邏輯保持一致
  valid: true
});

// 照片相關的 ref
const uploadedBeforePhotos = ref<any[]>([]);  // 已上傳的施工前照片（從 step3）
const uploadedAfterPhotos = ref<any[]>([]);   // 已上傳的竣工照片
const afterFileInput = ref<HTMLInputElement | null>(null);

// 載入版本比較資料
const loadVersionComparison = async () => {
  console.log('loadVersionComparison 被調用，檢查案件狀態:', {
    currentGrant: grantsStore.currentGrant,
    caseNumber: grantsStore.currentGrant?.case_number
  });

  if (!grantsStore.currentGrant?.case_number) {
    console.warn('無法載入版本比較：案件編號不存在')
    return
  }

  try {
    versionComparisonLoading.value = true
    versionComparisonError.value = null

    console.log('嘗試載入版本摘要...')

    try {
      // 嘗試獲取版本摘要
      const summary = await getGrantVersionSummary(grantsStore.currentGrant.case_number)
      versionSummary.value = summary
      console.log('版本摘要載入成功:', summary)

      // 如果有多個版本，才進行比較
      if (summary.has_versions && summary.total_versions > 1) {
        console.log('載入版本比較...')

        try {
          // 嘗試使用 API 進行版本比較
          const comparisonResult = await compareGrantVersions(grantsStore.currentGrant.case_number)
          facilitiesComparison.value = comparisonResult.facilities_comparison
          console.log('API 版本比較完成:', facilitiesComparison.value)
        } catch (apiError) {
          console.warn('API 版本比較失敗，使用本地比較:', apiError)

          // API 失敗時，使用本地比較
          const firstVersionData = grantsStore.formData // 假設當前是最新版本
          const latestVersionData = grantsStore.formData // 這裡應該獲取第一版本的數據

          facilitiesComparison.value = compareVersionsLocally(firstVersionData, latestVersionData)
          console.log('本地版本比較完成:', facilitiesComparison.value)
        }
      } else {
        console.log('只有一個版本或無版本，跳過比較')
        facilitiesComparison.value = null
      }
    } catch (apiError) {
      // API 不存在或其他錯誤，靜默處理
      console.log('版本比較 API 尚未實現，跳過版本比較功能')

      // 設置預設值，表示沒有多版本
      versionSummary.value = {
        total_versions: 1,
        first_version: { id: 1, version: 1, created_at: new Date().toISOString() },
        latest_version: { id: 1, version: 1, created_at: new Date().toISOString() },
        has_versions: false
      }
      facilitiesComparison.value = null
      versionComparisonError.value = null // 不顯示錯誤
    }

  } catch (error) {
    console.warn('版本比較功能暫時不可用:', error)
    // 設置安全的預設值
    versionSummary.value = {
      total_versions: 1,
      first_version: { id: 1, version: 1, created_at: new Date().toISOString() },
      latest_version: { id: 1, version: 1, created_at: new Date().toISOString() },
      has_versions: false
    }
    facilitiesComparison.value = null
    versionComparisonError.value = null
  } finally {
    versionComparisonLoading.value = false
  }
}

// 變更設計項目（保留原有功能作為備用）
const designChangeItems = reactive([
  { name: '主管', beforeQuantity: 2, afterQuantity: 1 },
  { name: '馬達+抽水機', beforeQuantity: 1, afterQuantity: 0 },
  { name: '單口噴頭-塑鋼', beforeQuantity: 0, afterQuantity: 10 }
]);

// 日期選擇組件
const completionDateComponents = reactive({
  year: new Date().getFullYear(),
  month: new Date().getMonth() + 1,
  day: new Date().getDate()
});

const testDateComponents = reactive({
  year: new Date().getFullYear(),
  month: new Date().getMonth() + 1,
  day: new Date().getDate()
});

const reinspectionDateComponents = reactive({
  year: new Date().getFullYear(),
  month: new Date().getMonth() + 1,
  day: new Date().getDate()
});

const improvementDateComponents = reactive({
  year: new Date().getFullYear(),
  month: new Date().getMonth() + 1,
  day: new Date().getDate()
});

// 產生年份選項 (民國年)
const yearOptions = computed(() => {
  const currentYear = new Date().getFullYear();
  const years = [];
  // 產生從當前年份到五年前和五年後的年份選項
  for (let year = currentYear - 5; year <= currentYear + 5; year++) {
    years.push({
      title: `民國 ${year - 1911} 年`,
      value: year
    });
  }
  return years;
});

// 產生月份選項
const monthOptions = computed(() => {
  return Array.from({ length: 12 }, (_, i) => ({
    title: `${i + 1} 月`,
    value: i + 1
  }));
});

// 產生日期選項 (考慮每月天數)
const dayOptions = (type) => {
  const components = type === 'completion'
    ? completionDateComponents
    : type === 'reinspection'
    ? reinspectionDateComponents
    : type === 'improvement'
    ? improvementDateComponents
    : testDateComponents;

  const year = components.year;
  const month = components.month;

  // 計算當月天數
  const daysInMonth = new Date(year, month, 0).getDate();

  return Array.from({ length: daysInMonth }, (_, i) => ({
    title: `${i + 1} 日`,
    value: i + 1
  }));
};

// 日期格式化（民國年）
const formattedCompletionDate = computed(() => {
  if (!localFormData.completionDate) return '';

  try {
    const date = new Date(localFormData.completionDate);
    if (isNaN(date.getTime())) return '';

    // 計算民國年
    const twYear = date.getFullYear() - 1911;
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');

    return `民國 ${twYear} 年 ${month} 月 ${day} 日`;
  } catch (error) {
    console.error('日期格式化錯誤:', error);
    return '';
  }
});

const formattedTestDate = computed(() => {
  if (!localFormData.testDate) return '';

  try {
    const date = new Date(localFormData.testDate);
    if (isNaN(date.getTime())) return '';

    // 計算民國年
    const twYear = date.getFullYear() - 1911;
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');

    return `民國 ${twYear} 年 ${month} 月 ${day} 日`;
  } catch (error) {
    console.error('日期格式化錯誤:', error);
    return '';
  }
});

const formattedReinspectionDate = computed(() => {
  if (!localFormData.reinspectionDate) return '';

  try {
    const date = new Date(localFormData.reinspectionDate);
    if (isNaN(date.getTime())) return '';

    // 計算民國年
    const twYear = date.getFullYear() - 1911;
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');

    return `民國 ${twYear} 年 ${month} 月 ${day} 日`;
  } catch (error) {
    console.error('日期格式化錯誤:', error);
    return '';
  }
});

const formattedImprovementDate = computed(() => {
  if (!localFormData.improvementDate) return '';

  try {
    const date = new Date(localFormData.improvementDate);
    if (isNaN(date.getTime())) return '';

    // 計算民國年
    const twYear = date.getFullYear() - 1911;
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');

    return `民國 ${twYear} 年 ${month} 月 ${day} 日`;
  } catch (error) {
    console.error('日期格式化錯誤:', error);
    return '';
  }
});

// 補充說明欄位的標籤（根據測試結果動態變化）
const additionalNotesLabel = computed(() => {
  const currentResult = localFormData.isReinspection ? localFormData.reinspectionResult : localFormData.testResult;
  if (currentResult === 'adjusted' || currentResult === 'improvement') {
    return '補充說明（必填）';
  }
  return '補充說明（選填）';
});

// 補充說明欄位的提示文字
const additionalNotesPlaceholder = computed(() => {
  const currentResult = localFormData.isReinspection ? localFormData.reinspectionResult : localFormData.testResult;
  if (currentResult === 'adjusted') {
    return '請說明減列原因...';
  } else if (currentResult === 'improvement') {
    return '請說明需要改善的項目...';
  }
  return '如有需要，請在此輸入補充說明...';
});

// 補充說明欄位的 hint 文字
const additionalNotesHint = computed(() => {
  const currentResult = localFormData.isReinspection ? localFormData.reinspectionResult : localFormData.testResult;
  if (currentResult === 'adjusted') {
    return '減列情況下，請說明減列的原因';
  } else if (currentResult === 'improvement') {
    return '不合格情況下，請說明需要改善的項目，並在上方選擇預計完成改善的日期';
  }
  return '此欄位供您輸入額外的補充說明';
});

// 補充說明欄位的驗證規則
const additionalNotesRules = computed(() => {
  const currentResult = localFormData.isReinspection ? localFormData.reinspectionResult : localFormData.testResult;

  return [
    (v: string) => {
      if (currentResult === 'adjusted' || currentResult === 'improvement') {
        return !!v || '此情況下補充說明為必填';
      }
      return true;
    }
  ];
});

// 計算顯示用的申請年度（統一單一來源）
const displayApplicationYear = computed(() => {
  const step6Data = getStepDataSafely(6);
  if (step6Data?.applicationYear) {
    return step6Data.applicationYear;
  }

  // Fallback to localFormData
  if (localFormData.applicationYear) {
    return localFormData.applicationYear;
  }

  // Default to current Taiwan calendar year
  const currentYear = new Date().getFullYear() - 1911;
  return `${currentYear}`;
});

// 計算顯示用的案號（統一單一來源）
const displayCaseNumber = computed(() => {
  // Priority: grantsStore.caseNumber > localFormData.caseNumber
  return grantsStore.caseNumber;
});

// 計算顯示用的申請人姓名（從 grants 表讀取，不在 all_steps_data 中）
const displayApplicantName = computed(() => {
  // Step1 資料儲存在 grants 表的 applicant_name 欄位
  return grantsStore.currentGrant?.applicant_name || localFormData.name || '';
});

// 計算顯示用的申請人地址（從 grants 表讀取，不在 all_steps_data 中）
const displayApplicantAddress = computed(() => {
  // Step1 地址資料儲存在 grants 表的 county, town, village, address 欄位
  const grant = grantsStore.currentGrant;
  if (!grant) return localFormData.applicantAddress || '';

  // 組合完整地址：縣市 + 鄉鎮 + 村里 + 詳細地址
  const addressParts = [
    grant.county,
    grant.town,
    grant.village,
    grant.address
  ].filter(Boolean);

  return addressParts.length > 0 ? addressParts.join('') : (localFormData.applicantAddress || '');
});

// 計算顯示用的設施型式（統一單一來源）
const displayFacilityType = computed(() => {
  const step4Data = getStepDataSafely(5);  // step4.vue → formData[5]

  // Priority: step4.irrigationType > localFormData
  if (step4Data?.irrigationType) {
    return step4Data.irrigationType;
  }

  return localFormData.facilityType || '';
});

// 計算設施地段和地號的配對資料（用於一一對應顯示）
const displayFacilityLocationPairs = computed(() => {
  const step2Data = getStepDataSafely(2);
  if (!step2Data) {
    return [{
      location: localFormData.facilityLocation || '',
      number: localFormData.facilityNumber || ''
    }];
  }

  // 處理多筆土地格式
  if (step2Data.lands && Array.isArray(step2Data.lands) && step2Data.lands.length > 0) {
    return step2Data.lands.map((land: any) => ({
      location: getLandLocationText(land),
      number: land.landNumber || ''
    })).filter(pair => pair.location || pair.number);
  }

  // 向後相容：處理舊格式
  if (step2Data.landCounty || step2Data.landTown || step2Data.landSec) {
    const land = {
      landCounty: step2Data.landCounty,
      landTown: step2Data.landTown,
      landSec: step2Data.landSec
    };
    return [{
      location: getLandLocationText(land),
      number: step2Data.landNumber || ''
    }];
  }

  return [{
    location: localFormData.facilityLocation || '',
    number: localFormData.facilityNumber || ''
  }];
});

// 計算顯示用的設施面積（與step2同步）
const displayFacilityArea = computed(() => {
  const step2Data = getStepDataSafely(2);
  if (!step2Data) return localFormData.facilityAreaHa || '';

  // 處理多筆土地格式
  if (step2Data.lands && Array.isArray(step2Data.lands) && step2Data.lands.length > 0) {
    const totalFacilityAreaM2 = step2Data.lands.reduce((total: number, land: any) => {
      const area = parseFloat(land.facilityArea || '0');
      return total + (isNaN(area) ? 0 : area);
    }, 0);
    const totalFacilityAreaHa = totalFacilityAreaM2 / 10000;
    return totalFacilityAreaHa > 0 ? totalFacilityAreaHa.toFixed(4) : localFormData.facilityAreaHa || '';
  }

  // 向後相容：處理舊格式
  if (step2Data.landArea) {
    const landAreaM2 = parseFloat(step2Data.landArea || '0');
    const landAreaHa = landAreaM2 / 10000;
    return landAreaHa > 0 ? landAreaHa.toFixed(4) : localFormData.facilityAreaHa || '';
  }

  return localFormData.facilityAreaHa || '';
});

// 土地位置文字轉換函數（將ID轉換為中文地名）
// 土地資料展示工具函數（與 step2 保持一致）
const getLandLocationText = (land: any): string => {
  const parts = [];

  // 縣市
  let countyName = '';
  if (land.landCounty) {
    if (typeof land.landCounty === 'number') {
      const county = domicileStore.countyOptions.find(c => c.value === land.landCounty);
      if (county) {
        countyName = county.title;
        parts.push(county.title);
      }
    } else {
      countyName = land.landCounty;
      parts.push(land.landCounty);
    }
  }

  // 特殊城市配置 - 與 step2 保持一致
  const specialCities = ['新竹市', '嘉義市'];

  // 鄉鎮 - 特殊城市跳過鄉鎮市區顯示
  if (land.landTown && !specialCities.includes(countyName)) {
    if (typeof land.landTown === 'number') {
      const town = domicileStore.getTownsForCountyId(land.landCounty as number)
        .find(t => t.value === land.landTown);
      if (town) parts.push(town.title);
    } else {
      // 對於字串值，只有不是特殊城市代碼才顯示
      if (land.landTown !== 'O01' && land.landTown !== 'I01') {
        parts.push(land.landTown);
      }
    }
  }

  // 地段 - 優先使用儲存的地段名稱，提高效能和可靠性
  if (land.landSec) {
    // 第一優先：使用已儲存的地段名稱
    if (land.landSecName) {
      parts.push(land.landSecName);
    } else {
      // 第二優先：從 domicileStore 查找地段名稱
      if (typeof land.landSec === 'number') {
        const section = domicileStore.getLandSectionsForTownId(land.landTown as number)
          .find(s => s.value === land.landSec);
        if (section) parts.push(section.title);
      } else {
        // 如果是字串代碼，直接顯示（通常是地段名稱）
        parts.push(land.landSec);
      }
    }
  }

  return parts.length > 0 ? parts.join('') : '未設定位置';
};

// 初始化設施資訊的函數
const initializeFacilityInfo = async () => {
  console.log('Initializing facility info...');

  // 統一使用 getStepDataSafely 獲取 step2 資料
  const step2Data = getStepDataSafely(2);
  if (!step2Data) {
    console.log('No step2 data available');
    return;
  }

  // 需要載入的縣市和鄉鎮資料
  const countyIds = new Set<number>();
  const townIds = new Set<number>();

  // 收集需要載入的資料
  if (step2Data.lands && Array.isArray(step2Data.lands)) {
    step2Data.lands.forEach((land: any) => {
      if (land.landCounty && typeof land.landCounty === 'number') {
        countyIds.add(land.landCounty);
      }
      if (land.landTown && typeof land.landTown === 'number') {
        townIds.add(land.landTown);
      }
    });
  } else if (step2Data.landCounty && step2Data.landTown) {
    if (typeof step2Data.landCounty === 'number') countyIds.add(step2Data.landCounty);
    if (typeof step2Data.landTown === 'number') townIds.add(step2Data.landTown);
  }

  // 載入鄉鎮資料
  for (const countyId of countyIds) {
    try {
      await domicileStore.loadTownsByCountyId(countyId);
      console.log(`Loaded towns for county ${countyId}`);
    } catch (error) {
      console.warn(`Failed to load towns for county ${countyId}:`, error);
    }
  }

  // 載入地段資料
  for (const townId of townIds) {
    try {
      await domicileStore.loadLandSectionsByTownId(townId);
      console.log(`Loaded sections for town ${townId}`);
    } catch (error) {
      console.warn(`Failed to load sections for town ${townId}:`, error);
    }
  }

  // 初始化設施資訊
  console.log('Initializing facility info with domicile data...');

  // Get facility location (使用中文地名)
  if (step2Data.lands && Array.isArray(step2Data.lands) && step2Data.lands.length > 0) {
    const locations = step2Data.lands.map((land: any) => {
      return getLandLocationText(land);
    }).filter(Boolean);

    const uniqueLocations = [...new Set(locations)];
    if (uniqueLocations.length > 0) {
      localFormData.facilityLocation = uniqueLocations.join('、');
    }
  }
  // 向後相容：處理舊格式
  else if (step2Data.landCounty || step2Data.landTown || step2Data.landSec) {
    const land = {
      landCounty: step2Data.landCounty,
      landTown: step2Data.landTown,
      landSec: step2Data.landSec
    };
    const locationText = getLandLocationText(land);
    if (locationText) {
      localFormData.facilityLocation = locationText;
    }
  }

  // Get facility numbers
  if (step2Data.lands && Array.isArray(step2Data.lands) && step2Data.lands.length > 0) {
    const landNumbers = step2Data.lands
      .map((land: any) => land.landNumber)
      .filter(Boolean)
      .join('、');
    if (landNumbers) {
      localFormData.facilityNumber = landNumbers;
    }
  }
  // 向後相容：從舊格式取得地號
  else if (step2Data.landNumber) {
    localFormData.facilityNumber = step2Data.landNumber;
  }

  // Get facility area
  if (step2Data.lands && Array.isArray(step2Data.lands)) {
    const totalFacilityAreaM2 = step2Data.lands.reduce((total: number, land: any) => {
      const area = parseFloat(land.facilityArea || '0');
      return total + (isNaN(area) ? 0 : area);
    }, 0);
    const totalFacilityAreaHa = totalFacilityAreaM2 / 10000;
    if (totalFacilityAreaHa > 0) {
      localFormData.facilityAreaHa = totalFacilityAreaHa.toFixed(4);
    }
  } else if (step2Data.landArea) {
    // 舊格式：從單筆土地面積計算
    const landAreaM2 = parseFloat(step2Data.landArea || '0');
    const landAreaHa = landAreaM2 / 10000;
    if (landAreaHa > 0) {
      localFormData.facilityAreaHa = landAreaHa.toFixed(4);
    }
  }

  // Get facility type - 統一使用 getStepDataSafely
  const step4Data = getStepDataSafely(5);  // step4.vue → formData[5]
  if (step4Data?.irrigationType) {
    localFormData.facilityType = step4Data.irrigationType;
  }

  console.log('Facility info initialized:', {
    facilityLocation: localFormData.facilityLocation,
    facilityNumber: localFormData.facilityNumber,
    facilityAreaHa: localFormData.facilityAreaHa,
    facilityType: localFormData.facilityType
  });
};

// 開啟日期選擇對話框
const openDateDialog = (type) => {
  // 選擇要操作的組件和對話框
  const components = type === 'completion'
    ? completionDateComponents
    : type === 'reinspection'
    ? reinspectionDateComponents
    : type === 'improvement'
    ? improvementDateComponents
    : testDateComponents;

  const dateValue = type === 'completion'
    ? localFormData.completionDate
    : type === 'reinspection'
    ? localFormData.reinspectionDate
    : type === 'improvement'
    ? localFormData.improvementDate
    : localFormData.testDate;

  // 如果已有日期，解析它
  if (dateValue) {
    try {
      const date = new Date(dateValue);
      if (!isNaN(date.getTime())) {
        components.year = date.getFullYear();
        components.month = date.getMonth() + 1;
        components.day = date.getDate();
      }
    } catch (error) {
      console.error('日期解析錯誤:', error);
      // 預設為今天或明天
      const today = new Date();
      // 改善日期預設為明天
      if (type === 'improvement') {
        const tomorrow = new Date(today);
        tomorrow.setDate(tomorrow.getDate() + 1);
        components.year = tomorrow.getFullYear();
        components.month = tomorrow.getMonth() + 1;
        components.day = tomorrow.getDate();
      } else {
        components.year = today.getFullYear();
        components.month = today.getMonth() + 1;
        components.day = today.getDate();
      }
    }
  } else if (type === 'improvement') {
    // 改善日期若無值，預設為明天
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    components.year = tomorrow.getFullYear();
    components.month = tomorrow.getMonth() + 1;
    components.day = tomorrow.getDate();
  }

  // 打開對話框
  if (type === 'completion') {
    datePickerDialog1.value = true;
  } else if (type === 'reinspection') {
    datePickerDialog3.value = true;
  } else if (type === 'improvement') {
    datePickerDialog4.value = true;
  } else {
    datePickerDialog2.value = true;
  }
};

// 確認日期選擇
const confirmDateSelection = (type) => {
  // 選擇要操作的組件和對話框
  const components = type === 'completion'
    ? completionDateComponents
    : type === 'reinspection'
    ? reinspectionDateComponents
    : type === 'improvement'
    ? improvementDateComponents
    : testDateComponents;

  // 用選擇的年、月、日構建日期字串
  const year = components.year;
  const month = String(components.month).padStart(2, '0');
  const day = String(components.day).padStart(2, '0');
  const dateString = `${year}-${month}-${day}`;

  // 更新 localFormData 中的日期
  if (type === 'completion') {
    localFormData.completionDate = dateString;
    datePickerDialog1.value = false;
  } else if (type === 'reinspection') {
    localFormData.reinspectionDate = dateString;
    datePickerDialog3.value = false;
  } else if (type === 'improvement') {
    localFormData.improvementDate = dateString;
    datePickerDialog4.value = false;
  } else {
    localFormData.testDate = dateString;
    datePickerDialog2.value = false;
  }

  // 更新父組件數據
  updateFormData();
};

// 清理預覽 URL
const cleanupPreviews = (type: 'before' | 'after') => {
  const previews = type === 'before' ? localFormData.beforePhotoPreviews : localFormData.afterPhotoPreviews;
  previews.forEach(preview => {
    if (preview && typeof preview === 'string' && preview.startsWith('blob:')) {
      URL.revokeObjectURL(preview);
    }
  });
};

// 載入施工前照片（從 UI step3，只讀）
const loadBeforePhotos = async () => {
  if (!props.grantId || props.grantId === 0) {
    console.warn('[step7] loadBeforePhotos: grantId 無效，跳過載入', props.grantId);
    return;
  }

  try {
    const stepNumber = 3;  // UI Step 3 = data step 3（統一架構）
    console.log(`[step7] 開始載入施工前照片 - grantId: ${props.grantId}, step: ${stepNumber}`);

    const response = await attachmentService.list(props.grantId, stepNumber, 'inspection_before');
    console.log(`[step7] 施工前照片 API 回應:`, response);

    uploadedBeforePhotos.value = response.attachments || [];

    // 清除本地預覽並使用 API 照片
    cleanupPreviews('before');
    localFormData.beforePhotoPreviews = [];
    localFormData.beforeConstructionPhotos = [];

    // 為每張已上傳的照片創建預覽 URL
    for (const photo of uploadedBeforePhotos.value) {
      try {
        const blob = await attachmentService.download(photo.id);
        const previewUrl = URL.createObjectURL(blob);
        localFormData.beforePhotoPreviews.push(previewUrl);
        console.log(`[step7] 施工前照片 ${photo.id} 載入成功`);
      } catch (downloadError) {
        console.error(`[step7] 下載施工前照片 ${photo.id} 失敗:`, downloadError);
      }
    }

    console.log(`[step7] 施工前照片載入完成，共 ${uploadedBeforePhotos.value.length} 張`);
  } catch (error) {
    console.error('[step7] 載入施工前照片失敗:', error);
  }
};

// 載入竣工照片（step7，可編輯）
const loadAfterPhotos = async () => {
  if (!props.grantId || props.grantId === 0) {
    console.warn('[step7] loadAfterPhotos: grantId 無效，跳過載入', props.grantId);
    return;
  }

  try {
    const stepNumber = 7;
    console.log(`[step7] 開始載入竣工照片 - grantId: ${props.grantId}, step: ${stepNumber}`);

    const response = await attachmentService.list(props.grantId, stepNumber, 'inspection_after');
    console.log(`[step7] 竣工照片 API 回應:`, response);

    uploadedAfterPhotos.value = response.attachments || [];

    // 清除本地預覽並使用 API 照片
    cleanupPreviews('after');
    localFormData.afterPhotoPreviews = [];
    localFormData.afterConstructionPhotos = [];

    // 為每張已上傳的照片創建預覽 URL
    for (const photo of uploadedAfterPhotos.value) {
      try {
        const blob = await attachmentService.download(photo.id);
        const previewUrl = URL.createObjectURL(blob);
        localFormData.afterPhotoPreviews.push(previewUrl);
        console.log(`[step7] 竣工照片 ${photo.id} 載入成功`);
      } catch (downloadError) {
        console.error(`[step7] 下載竣工照片 ${photo.id} 失敗:`, downloadError);
      }
    }

    console.log(`[step7] 竣工照片載入完成，共 ${uploadedAfterPhotos.value.length} 張`);
  } catch (error) {
    console.error('[step7] 載入竣工照片失敗:', error);
  }
};

// 觸發竣工照片上傳
const triggerAfterFileInput = () => {
  if (localFormData.afterPhotoPreviews.length < 3) {
    afterFileInput.value?.click();
  }
};

// 處理竣工照片上傳（單張上傳）
const handleAfterPhotoUpload = async (event: Event) => {
  const target = event.target as HTMLInputElement;
  const file = target.files?.[0];

  if (!file) {
    return;
  }

  if (!props.grantId || props.grantId === 0) {
    alert('無法上傳照片：缺少 grant ID');
    return;
  }

  try {
    console.log(`[step7] 開始上傳竣工照片: ${file.name}`);

    // 上傳照片到後端
    const stepNumber = 7;
    const uploadedPhoto = await attachmentService.upload(
      props.grantId,
      stepNumber,
      file,
      'inspection_after'
    );

    console.log(`[step7] 竣工照片上傳成功:`, uploadedPhoto);

    // 重新載入照片列表
    await loadAfterPhotos();

    // 清空 input
    target.value = '';

    updateFormData();
  } catch (error) {
    console.error('[step7] 上傳竣工照片失敗:', error);
    alert('上傳照片失敗，請稍後再試');
    target.value = '';
  }
};

// 刪除竣工照片
const removeAfterPhoto = async (index: number) => {
  try {
    // 如果是已上傳的照片，從後端刪除
    if (uploadedAfterPhotos.value[index]) {
      const photoToDelete = uploadedAfterPhotos.value[index];
      console.log(`[step7] 刪除竣工照片 ID: ${photoToDelete.id}`);

      await attachmentService.delete(photoToDelete.id);
      console.log(`[step7] 成功刪除竣工照片 ID: ${photoToDelete.id}`);
    }

    // 清除預覽
    if (localFormData.afterPhotoPreviews[index] &&
        typeof localFormData.afterPhotoPreviews[index] === 'string' &&
        localFormData.afterPhotoPreviews[index].startsWith('blob:')) {
      URL.revokeObjectURL(localFormData.afterPhotoPreviews[index]);
    }

    // 重新載入照片列表
    await loadAfterPhotos();

    updateFormData();
  } catch (error) {
    console.error('[step7] 刪除竣工照片失敗:', error);
    alert('刪除照片失敗，請稍後再試');
  }
};

// 獲取上傳狀態顏色
const getUploadStatusColor = () => {
  const count = localFormData.afterPhotoPreviews.length;
  if (count === 0) return 'grey';
  if (count < 3) return 'orange';
  return 'green';
};

// 獲取上傳狀態圖標
const getUploadStatusIcon = () => {
  const count = localFormData.afterPhotoPreviews.length;
  if (count === 0) return 'mdi-alert-circle';
  if (count < 3) return 'mdi-clock-alert';
  return 'mdi-check-circle';
};

// 獲取上傳狀態文字
const getUploadStatusText = () => {
  const count = localFormData.afterPhotoPreviews.length;
  if (count === 0) return '尚未上傳竣工照片';
  if (count < 3) return `已上傳 ${count} 張，建議上傳 1-3 張`;
  return `已上傳 ${count} 張照片`;
};

// 智慧資料來源選擇器：透過案件號比對確保 formData 歸屬正確（參考 Step6）
const getStepDataSafely = (step: number) => {
  const currentCaseNumber = route.query.id as string;
  console.log(`Step7: getStepDataSafely(${step}) - 案件編號:`, currentCaseNumber);

  // 確保只處理當前案件的資料
  if (!currentCaseNumber) {
    console.log('Step7: 沒有案件編號');
    return null;
  }

  const formData = grantsStore.formData[step];
  const allStepsData = (grantsStore.currentGrant?.active_version as any)?.all_steps_data?.steps?.[step.toString()];

  console.log(`Step7: step ${step} - formData:`, formData);
  console.log(`Step7: step ${step} - allStepsData:`, allStepsData);

  // 檢查 formData 是否屬於當前案件（透過 _caseNumber 欄位比對）
  const formDataCaseNumber = formData?._caseNumber;
  const isFormDataValid = formDataCaseNumber === currentCaseNumber;

  console.log(`Step7: step ${step} - formDataCaseNumber: ${formDataCaseNumber}, isValid: ${isFormDataValid}`);

  if (isFormDataValid && formData && Object.keys(formData).length > 1) { // >1 因為至少有 _caseNumber
    console.log(`Step7: Using formData for step ${step} (case: ${formDataCaseNumber})`);
    return formData; // 使用 formData（即時同步）
  }

  // 否則使用 all_steps_data（持久化資料）
  if (allStepsData && Object.keys(allStepsData).length > 0) {
    console.log(`📚 Step7: Using all_steps_data for step ${step} (formData case: ${formDataCaseNumber}, current: ${currentCaseNumber})`);
    return allStepsData;
  }

  console.log(`Step7: step ${step} 沒有可用資料`);
  return null;
};

// 計算田間管路設施補助總額（從 step4.subsidyAmount 獲取）
const calculatePipeLineSubsidy = () => {
  const step4Data = getStepDataSafely(5);  // step4.vue → formData[5]
  console.log('Step7: calculatePipeLineSubsidy - step4Data:', step4Data);

  if (!step4Data || Object.keys(step4Data).length === 0) {
    console.log('Step7: step4Data 為空或不存在');
    return 0;
  }

  // 直接使用 step4 的 subsidyAmount（補助金額，而非總成本）
  const subsidyAmount = step4Data.subsidyAmount || 0;
  const parsedAmount = typeof subsidyAmount === 'number'
    ? subsidyAmount
    : parseFloat(subsidyAmount as string || '0');

  console.log('Step7: step4 補助金額:', {
    subsidyAmount: step4Data.subsidyAmount,
    parsed: parsedAmount
  });

  return parsedAmount;
};

// 計算灌溉調控設施補助總額（從 step3.facilities[].subsidyAmount 獲取）
const calculateFacilitySubsidy = () => {
  const step3Data = getStepDataSafely(4);  // step3.vue → formData[4]
  console.log('Step7: calculateFacilitySubsidy - step3Data:', step3Data);

  if (!step3Data || Object.keys(step3Data).length === 0 || !step3Data?.facilities || !Array.isArray(step3Data.facilities)) {
    console.log('Step7: step3Data.facilities 為空或不存在');
    return 0;
  }

  console.log('Step7: facilities 資料:', step3Data.facilities);

  // 使用 subsidyAmount（補助金額）而非 totalPrice（總成本）
  const total = step3Data.facilities.reduce((sum: number, facility: Record<string, unknown>) => {
    const subsidyAmount = facility.subsidyAmount || 0;
    const parsed = typeof subsidyAmount === 'number'
                  ? subsidyAmount
                  : parseFloat(subsidyAmount as string || '0');

    console.log('💰 Step7: facility 補助金額:', {
      name: facility.name,
      subsidyAmount: facility.subsidyAmount,
      parsed
    });
    return sum + parsed;
  }, 0);

  console.log('Step7: calculateFacilitySubsidy 結果:', total);
  return total;
};

// 從資料庫讀取設計費（不重新計算，避免重複計算）
const getDesignFee = () => {
  const step4Data = getStepDataSafely(5);  // step4.vue → formData[5]
  if (!step4Data) {
    return 0;
  }

  // 直接從 step4.designFee 讀取（step4 已經計算並儲存）
  const designFee = step4Data.designFee || 0;
  const parsed = typeof designFee === 'number'
    ? designFee
    : parseFloat(designFee as string || '0');

  console.log('Step7: 讀取設計費 (從 step4):', {
    designFee: step4Data.designFee,
    parsed
  });

  return parsed;
};

// 計算補助總額（所有金額來自資料庫，不重新計算）
const calculateTotalBudget = () => {
  const pipelineSubsidy = calculatePipeLineSubsidy();  // step4 補助
  const facilitySubsidy = calculateFacilitySubsidy();  // step3 補助
  const total = pipelineSubsidy + facilitySubsidy;
  return total;
};

// 響應式計算補助金額 - 當 Step3/Step4 資料變化時自動重新計算
const computedTotalBudget = computed(() => {
  console.log('Step7: computedTotalBudget 正在計算...');

  // 明確監聽這些數據源，讓 Vue 知道需要響應它們的變化
  const step3FormData = grantsStore.formData[3];
  const step4FormData = grantsStore.formData[4];
  const step3AllStepsData = (grantsStore.currentGrant?.active_version as any)?.all_steps_data?.steps?.['3'];
  const step4AllStepsData = (grantsStore.currentGrant?.active_version as any)?.all_steps_data?.steps?.['4'];

  console.log('Step7: 數據源監聽狀態:', {
    step3FormData: step3FormData ? Object.keys(step3FormData).length : 0,
    step4FormData: step4FormData ? Object.keys(step4FormData).length : 0,
    step3AllStepsData: step3AllStepsData ? Object.keys(step3AllStepsData).length : 0,
    step4AllStepsData: step4AllStepsData ? Object.keys(step4AllStepsData).length : 0
  });

  const pipelineValue = calculatePipeLineSubsidy();
  const facilityValue = calculateFacilitySubsidy();
  const designValue = getDesignFee();  // 從 step4 讀取，不重新計算
  const total = pipelineValue + facilityValue + designValue;

  console.log('Step7: computedTotalBudget 計算結果:', {
    pipelineValue,
    facilityValue,
    designValue,
    total,
    formatted: total > 0 ? total.toLocaleString() : '0'
  });

  return {
    pipelineValue,
    facilityValue,
    designValue,
    total,
    formatted: total > 0 ? total.toLocaleString() : '0'
  };
});

// 監聽計算結果變化並自動更新 localFormData
watch(computedTotalBudget, (newBudget, oldBudget) => {
  // 只有當金額真的有變化且大於 0 時才更新
  if (newBudget.total !== oldBudget?.total && newBudget.total > 0) {
    console.log('Step7: 響應式補助金額更新', {
      舊金額: oldBudget?.formatted || '0',
      新金額: newBudget.formatted,
      計算詳情: {
        pipelineValue: newBudget.pipelineValue,
        facilityValue: newBudget.facilityValue,
        designValue: newBudget.designValue
      }
    });

    // 更新 originalPayment
    localFormData.originalPayment = newBudget.formatted;

    // 如果是原補助款發放模式，同時更新實際發放金額
    if (localFormData.testResult === 'original') {
      localFormData.actualPayment = newBudget.formatted;
    }
    // 如果是調整模式，重新計算實際發放金額
    else if (localFormData.testResult === 'adjusted' && localFormData.increasedDecreasedAmount) {
      try {
        const original = newBudget.total;
        const deduction = parseFloat(localFormData.increasedDecreasedAmount.replace(/,/g, ''));
        if (!isNaN(deduction) && deduction > 0) {
          // 減列：原金額 - 減列金額（直接相減）
          const actual = original - deduction;
          localFormData.actualPayment = actual.toLocaleString();
        }
      } catch (e) {
        console.error('重新計算調整後金額失敗:', e);
      }
    }

    // 更新父組件
    updateFormData();
  }
}, { immediate: false });


// 處理減列金額輸入（只允許正數，自動格式化為千分位）
const handleDeductionAmountInput = (value: string) => {
  if (!value) {
    localFormData.increasedDecreasedAmount = '';
    updateFormData();
    return;
  }

  // 移除所有非數字字符（保留小數點）
  let cleanValue = value.replace(/[^\d.]/g, '');

  // 確保只有一個小數點
  const parts = cleanValue.split('.');
  if (parts.length > 2) {
    cleanValue = parts[0] + '.' + parts.slice(1).join('');
  }

  // 解析數字
  const numValue = parseFloat(cleanValue);

  // 如果是有效的正數，格式化為千分位
  if (!isNaN(numValue) && numValue > 0) {
    // 保留小數部分
    const [integer, decimal] = cleanValue.split('.');
    const formattedInteger = parseInt(integer).toLocaleString();
    localFormData.increasedDecreasedAmount = decimal !== undefined
      ? `${formattedInteger}.${decimal}`
      : formattedInteger;
  } else if (cleanValue === '' || cleanValue === '0') {
    localFormData.increasedDecreasedAmount = '';
  } else {
    // 保持輸入中的狀態，允許用戶繼續輸入
    localFormData.increasedDecreasedAmount = cleanValue;
  }

  updateFormData();
};

// 金額欄位：去除千分位（存入後端）
const stripCommas = (val: string) => val ? val.replace(/,/g, '') : val;
// 金額欄位：加上千分位（從後端取回顯示）
const formatWithCommas = (val: string) => {
  if (!val) return val;
  const clean = val.replace(/,/g, '');
  const num = parseFloat(clean);
  return isNaN(num) ? val : num.toLocaleString();
};
const PAYMENT_KEYS = ['originalPayment', 'actualPayment', 'increasedDecreasedAmount'] as const;

// 更新父組件數據
const updateFormData = () => {
  emit('update:formData', {
    ...props.formData,
    ...localFormData,
    originalPayment: stripCommas(localFormData.originalPayment),
    actualPayment: stripCommas(localFormData.actualPayment),
    increasedDecreasedAmount: stripCommas(localFormData.increasedDecreasedAmount),
    designChangeItems: [...designChangeItems],
    valid: true // Always set to true for seamless navigation
  });
};

// 確認存檔
const confirmSave = () => {
  console.log('確認存檔，現場勘查未通過驗收，將於改善後複驗');
  // 關閉對話框
  saveConfirmDialog.value = false;
  // 更新表單數據
  updateFormData();
  // 發送存檔事件給父組件
  emit('save-for-improvement');
};

// 初始化數據
onMounted(async () => {
  console.log('step2 data:', localFormData);
  console.log('facilityArea from step2:', localFormData.facilityAreaHa);
  console.log('landAreaHa from step2:', localFormData.landAreaHa);

  // 初始化 domicile store 以獲取縣市資料
  try {
    await domicileStore.loadCounties();
    console.log('Counties loaded successfully');
  } catch (error) {
    console.error('Failed to load counties:', error);
  }

  // 從父組件接收數據
  if (props.formData) {
    // 設置基本屬性
    Object.keys(localFormData).forEach(key => {
      // 排除應從 API 載入的照片欄位
      if (key === 'beforePhotoPreviews' ||
          key === 'beforeConstructionPhotos' ||
          key === 'afterPhotoPreviews' ||
          key === 'afterConstructionPhotos') {
        return;
      }

      if (props.formData[key] !== undefined) {
        const val = props.formData[key];
        localFormData[key] = PAYMENT_KEYS.includes(key as any) ? formatWithCommas(val) : val;
      }
    });

    // 變更設計項目
    if (Array.isArray(props.formData.designChangeItems)) {
      props.formData.designChangeItems.forEach((item, index) => {
        if (index < designChangeItems.length) {
          designChangeItems[index].beforeQuantity = item.beforeQuantity;
          designChangeItems[index].afterQuantity = item.afterQuantity;
        } else {
          designChangeItems.push({ ...item });
        }
      });
    }
  }

  // Initialize data from other steps if necessary - 統一使用 getStepDataSafely
  if (!localFormData.applicationYear) {
    // Try to get from step6 or use default
    const step6Data = getStepDataSafely(6);
    if (step6Data?.applicationYear) {
      localFormData.applicationYear = step6Data.applicationYear;
    } else {
      const currentYear = new Date().getFullYear() - 1911; // Taiwan calendar year
      localFormData.applicationYear = `${currentYear}`;
    }
  }

  // Get case number
  if (!localFormData.caseNumber) {
    if (grantsStore.caseNumber) {
      localFormData.caseNumber = grantsStore.caseNumber;
    }
  }

  // Get applicant info - 統一使用 getStepDataSafely
  if (!localFormData.name) {
    const step1Data = getStepDataSafely(1);
    const step6Data = getStepDataSafely(6);

    if (step1Data?.name) {
      localFormData.name = step1Data.name;
    } else if (step6Data?.name) {
      localFormData.name = step6Data.name;
    }
  }

  // Get applicant address - 統一使用 getStepDataSafely
  if (!localFormData.applicantAddress) {
    const step6Data = getStepDataSafely(6);
    const step1Data = getStepDataSafely(1);

    if (step6Data?.applicantAddress) {
      localFormData.applicantAddress = step6Data.applicantAddress;
    } else if (step1Data) {
      const county = step1Data.county || '';
      const town = step1Data.town || '';
      const village = step1Data.village || '';
      const address = step1Data.address || '';

      if (county || town || village || address) {
        localFormData.applicantAddress = `${county}${town}${village}${address}`;
      }
    }
  }

  // 獲取設施資訊 - 確保在 domicileStore 載入後執行
  await initializeFacilityInfo();

  // Set default completion information
  if (!localFormData.completionDate) {
    const today = new Date();
    const year = today.getFullYear();
    const month = String(today.getMonth() + 1).padStart(2, '0');
    const day = String(today.getDate()).padStart(2, '0');
    localFormData.completionDate = `${year}-${month}-${day}`;
  }

  if (!localFormData.testDate) {
    const today = new Date();
    const year = today.getFullYear();
    const month = String(today.getMonth() + 1).padStart(2, '0');
    const day = String(today.getDate()).padStart(2, '0');
    localFormData.testDate = `${year}-${month}-${day}`;
  }

  // Set default values for new forms
  if (!localFormData.designCompliance) {
    // localFormData.designCompliance = true;
  }

  if (!localFormData.operationCompliance) {
    // localFormData.operationCompliance = true;
  }

  if (!localFormData.tester) {
    // localFormData.tester = '王工程師';
  }

  if (!localFormData.testResult) {
    // localFormData.testResult = 'original';
  }

  // Set default payment info
  if (!localFormData.originalPayment && localFormData.testResult === 'original') {
    console.log('=== Step7 onMounted originalPayment 初始化調試 ===');

    // 使用新的計算邏輯來獲取補助金額
    const calculatedBudget = calculateTotalBudget();

    if (calculatedBudget > 0) {
      localFormData.originalPayment = calculatedBudget.toLocaleString();
      console.log('onMounted 使用計算邏輯設置 originalPayment:', localFormData.originalPayment);
    } else {
      console.log('onMounted 計算結果為 0，嘗試其他方法...');
      // 備用：嘗試從 grantsStore.formData[6] 取得
      if (grantsStore.formData[6]?.totalBudget) {
        const totalBudget = grantsStore.formData[6].totalBudget;
        localFormData.originalPayment = typeof totalBudget === 'string' ? totalBudget : totalBudget.toString();
        console.log('onMounted 從 formData 設置 originalPayment:', localFormData.originalPayment);
      }
    }

    localFormData.actualPayment = localFormData.originalPayment;
  }

  // Set sample description if needed
  if (!localFormData.testResultDescription && localFormData.testResult === 'original') {
    // localFormData.testResultDescription = '工程完工符合規範，依核定補助款發放。';
  }

  // 載入照片（僅在 grantId 有效時）
  if (props.grantId && props.grantId > 0) {
    try {
      console.log('[step7] 開始載入照片...', { grantId: props.grantId });
      await loadBeforePhotos();  // 從 UI step3 載入施工前照片
      await loadAfterPhotos();   // 載入竣工照片
      console.log('[step7] 照片載入完成');
    } catch (error) {
      console.error('[step7] 載入照片失敗:', error);
    }
  } else {
    console.log('[step7] grantId 無效，跳過照片載入（將在 grantId 更新後載入）', { grantId: props.grantId });
  }

  // Initial update to parent
  updateFormData();

  // 載入版本比較資料
  try {
    // 添加小延遲確保 grantsStore 已經準備好
    await nextTick();
    await loadVersionComparison();
  } catch (error) {
    console.warn('載入版本比較資料失敗:', error);
  }
});

// 監聽測試結果變化
watch(() => localFormData.isReinspection ? localFormData.reinspectionResult : localFormData.testResult, (newValue, oldValue) => {
  // 只有當測試結果真正變化時才重置手動編輯標記
  if (newValue !== oldValue) {
    isManuallyEditedDescription.value = false;
  }

  console.log('測試結果變化:', newValue);

  console.log('測試結果變化 - 詳細除錯:', {
    newValue,
    currentOriginalPayment: localFormData.originalPayment,
    currentActualPayment: localFormData.actualPayment,
    totalBudget: grantsStore.formData[6]?.totalBudget
  });

  // 設置自動計算標記，避免與金額變化watch衝突
  isAutoCalculatingAmount.value = true;

  if (newValue === 'original') {
    // 如果是 "依核定補助款發放"，則自動設置相關金額
    console.log('=== Step7 originalPayment 設置調試 ===');

    // 使用新的計算邏輯來獲取補助金額
    const calculatedBudget = calculateTotalBudget();

    if (calculatedBudget > 0) {
      localFormData.originalPayment = calculatedBudget.toLocaleString();
      console.log('從計算邏輯設置 originalPayment:', localFormData.originalPayment);
    } else {
      console.log('計算結果為 0，嘗試其他方法...');
      // 備用：嘗試從 grantsStore.formData[6] 取得
      if (grantsStore.formData[6]?.totalBudget) {
        const totalBudget = grantsStore.formData[6].totalBudget;
        localFormData.originalPayment = typeof totalBudget === 'string' ? totalBudget : totalBudget.toString();
        console.log('從 formData 設置 originalPayment:', localFormData.originalPayment);
      }
    }

    // 清空減列金額
    localFormData.increasedDecreasedAmount = '';

    // 原補助款發放，實際發放等於原補助款
    localFormData.actualPayment = localFormData.originalPayment;

    console.log('設置 original 金額完成:', {
      originalPayment: localFormData.originalPayment,
      actualPayment: localFormData.actualPayment,
      increasedDecreasedAmount: localFormData.increasedDecreasedAmount
    });
  } else if (newValue === 'adjusted') {
    // 如果是 "依核定補助款增減列"，則設置金額欄位
    console.log('=== Step7 adjusted originalPayment 設置調試 ===');

    // 使用新的計算邏輯來獲取補助金額
    const calculatedBudget = calculateTotalBudget();

    if (calculatedBudget > 0) {
      localFormData.originalPayment = calculatedBudget.toLocaleString();
      console.log('adjusted: 從計算邏輯設置 originalPayment:', localFormData.originalPayment);
    } else if (grantsStore.formData[6]?.totalBudget) {
      const totalBudget = grantsStore.formData[6].totalBudget;
      localFormData.originalPayment = typeof totalBudget === 'string' ? totalBudget : totalBudget.toString();
      console.log('adjusted: 從 formData 設置 originalPayment:', localFormData.originalPayment);
    } else {
      console.log('totalBudget 不存在，嘗試計算...');
      // 嘗試從其他步驟獲取預算資料
      if (grantsStore.formData[6]?.pipeLineSubsidy || grantsStore.formData[6]?.facilitySubsidy) {
        const pipelineSubsidy = parseInt(((grantsStore.formData[6].pipeLineSubsidy as string) || '0').replace(/,/g, ''));
        const facilitySubsidy = parseInt(((grantsStore.formData[6].facilitySubsidy as string) || '0').replace(/,/g, ''));
        const designFee = parseInt(((grantsStore.formData[6].designFee as string) || '0').replace(/,/g, ''));
        const calculatedTotal = pipelineSubsidy + facilitySubsidy + designFee;

        if (calculatedTotal > 0) {
          localFormData.originalPayment = calculatedTotal.toLocaleString();
          console.log('從子項目計算 adjusted originalPayment:', localFormData.originalPayment);
        } else if (!localFormData.originalPayment) {
          localFormData.originalPayment = '0';
          console.log('設置預設值 0');
        }
      } else if (!localFormData.originalPayment) {
        localFormData.originalPayment = '0';
        console.log('設置預設值 0');
      }
    }

    // 設置預設減列金額（正數，不帶負號）
    if (!localFormData.increasedDecreasedAmount) {
      localFormData.increasedDecreasedAmount = ''; //初始為空，讓用戶輸入
    }

    // 實際發放金額會通過減列計算（原金額 - 減列金額）
    try {
      const original = parseFloat(localFormData.originalPayment.replace(/,/g, ''));
      const deduction = parseFloat(localFormData.increasedDecreasedAmount.replace(/,/g, ''));
      if (!isNaN(original) && !isNaN(deduction) && deduction > 0) {
        // 減列：原金額 - 減列金額（直接相減）
        const actual = original - deduction;
        localFormData.actualPayment = actual.toLocaleString();
      }
    } catch (e) {
      console.error('計算實際發放金額時出錯', e);
    }

    console.log('設置 adjusted 金額:', {
      originalPayment: localFormData.originalPayment,
      increasedDecreasedAmount: localFormData.increasedDecreasedAmount,
      actualPayment: localFormData.actualPayment
    });
  } else if (newValue === 'improvement') {
    // 限期改善，清空金額欄位
    localFormData.originalPayment = '';
    localFormData.increasedDecreasedAmount = '';
    localFormData.actualPayment = '';
    console.log('設置 improvement，清空金額');
  } else {
    // 其他情況，清空金額欄位
    localFormData.originalPayment = '';
    localFormData.increasedDecreasedAmount = '';
    localFormData.actualPayment = '';
    console.log('其他情況，清空金額');
  }

  // 立即更新父組件資料，確保金額變化能立即反映
  updateFormData();

  // 重置自動計算標記
  nextTick(() => {
    isAutoCalculatingAmount.value = false;
    console.log('測試結果變化: 重置自動計算標記');
  });

  // 只有在用戶沒有手動編輯過結果說明時，才自動更新結果說明
  if (!isManuallyEditedDescription.value) {
    nextTick(() => {
      isAutoSyncingDescription.value = true;

      // 找到對應的測試結果選項
      const selectedOption = testResultOptions.value.find(option => option.value === newValue);
      if (selectedOption) {
        // 移除括號內容後再設置到結果說明
        const cleanTitle = removeParenthesesContent(selectedOption.title);
        console.log('自動帶入測試結果說明:', cleanTitle);
        localFormData.testResultDescription = cleanTitle;

        // 延遲更新父組件資料，確保本地資料先更新完成
        nextTick(() => {
          updateFormData();
          nextTick(() => {
            isAutoSyncingDescription.value = false;
          });
        });
      } else {
        isAutoSyncingDescription.value = false;
      }
    });
  }
});

// 監聽合規性狀態變化，自動調整測試結果選項
watch([() => localFormData.designCompliance, () => localFormData.operationCompliance], ([newDesign, newOperation]) => {
  console.log('合規性狀態變化:', {
    designCompliance: newDesign,
    operationCompliance: newOperation,
    isReinspection: localFormData.isReinspection
  });

  const hasNonCompliant = newDesign === 'non-compliant' || newOperation === 'non-compliant';
  const currentResult = localFormData.isReinspection ? localFormData.reinspectionResult : localFormData.testResult;

  if (hasNonCompliant) {
    // 有不符合項目時，根據複驗狀態設置不同的測試結果
    if (localFormData.isReinspection) {
      // 複驗狀態：設置為取消補助資格
      if (currentResult !== 'cancel') {
        console.log('複驗狀態且有不符合項目，自動設置測試結果為 cancel');
        localFormData.reinspectionResult = 'cancel';

        // 清空金額欄位（取消補助資格不需要金額）
        localFormData.originalPayment = '';
        localFormData.increasedDecreasedAmount = '';
        localFormData.actualPayment = '';

        updateFormData();
      }
    } else {
      // 非複驗狀態：設置為限期改善
      if (currentResult !== 'improvement') {
        console.log('非複驗狀態且有不符合項目，自動設置測試結果為 improvement');
        localFormData.testResult = 'improvement';

        // 清空金額欄位（限期改善不需要金額）
        localFormData.originalPayment = '';
        localFormData.increasedDecreasedAmount = '';
        localFormData.actualPayment = '';

        updateFormData();
      }
    }
  } else if (!hasNonCompliant && (currentResult === 'cancel' || currentResult === 'improvement')) {
    // 如果沒有不符合項目但當前選擇是 cancel 或 improvement，可以考慮重置為空讓用戶重新選擇
    console.log('不符合項目已修正，可重新選擇測試結果');
  }

  // 確保所有變更都同步到父組件
  console.log('=== 測試結果變化完成，同步資料到父組件 ===');
  console.log('當前 originalPayment:', localFormData.originalPayment);
  updateFormData();
});

// 監聽按鈕配置變化，通知父組件
watch(buttonConfig, (newConfig) => {
  console.log('按鈕配置變化:', newConfig);
  // 通知父組件按鈕配置變化
  emit('button-config-changed', newConfig);
}, { immediate: true });

// 監聽原金額與增減列變化，以及實際發放金額變化
watch([() => localFormData.originalPayment, () => localFormData.increasedDecreasedAmount, () => localFormData.actualPayment], () => {
  // 如果正在自動計算金額，跳過這次監聽
  if (isAutoCalculatingAmount.value) {
    console.log('金額變化 watch: 跳過，正在自動計算中');
    return;
  }

  const currentResult = localFormData.isReinspection ? localFormData.reinspectionResult : localFormData.testResult;

  console.log('金額變化 watch 觸發:', {
    currentResult,
    originalPayment: localFormData.originalPayment,
    increasedDecreasedAmount: localFormData.increasedDecreasedAmount,
    actualPayment: localFormData.actualPayment,
    isAutoCalculatingAmount: isAutoCalculatingAmount.value
  });

  // 如果沒有測試結果，不進行任何計算
  if (!currentResult) {
    console.log('沒有測試結果，跳過金額計算');
    return;
  }

  // 設置自動計算標記，避免循環觸發
  isAutoCalculatingAmount.value = true;

  if (currentResult === 'adjusted' && localFormData.originalPayment && localFormData.increasedDecreasedAmount) {
    try {
      const original = parseFloat(localFormData.originalPayment.replace(/,/g, ''));
      const deduction = parseFloat(localFormData.increasedDecreasedAmount.replace(/,/g, ''));

      if (!isNaN(original) && !isNaN(deduction) && deduction >= 0) {
        // 減列：原金額 - 減列金額（直接相減）
        const actual = original - deduction;
        const newActualPayment = actual.toLocaleString();

        // 只有當計算結果與當前值不同時才更新
        if (localFormData.actualPayment !== newActualPayment) {
          localFormData.actualPayment = newActualPayment;
          console.log('金額變化 watch: 計算實際發放金額 (原金額 - 減列):', {
            原金額: original,
            減列金額: deduction,
            實際發放: actual,
            格式化: newActualPayment
          });
        }
      }
    } catch (e) {
      console.error('計算實際發放金額時出錯', e);
    }
  } else if (currentResult === 'original' && localFormData.originalPayment) {
    // 如果是 original 狀態，實際發放金額等於原補助款
    if (localFormData.actualPayment !== localFormData.originalPayment) {
      localFormData.actualPayment = localFormData.originalPayment;
      console.log('金額變化 watch: 同步 original 實際發放金額:', localFormData.actualPayment);
    }
  }

  // 重置自動計算標記
  nextTick(() => {
    isAutoCalculatingAmount.value = false;
    console.log('金額變化 watch: 重置自動計算標記');
  });

  updateFormData();
});

// 監聽金額變化，自動更新結果說明中的金額顯示
watch([() => localFormData.originalPayment, () => localFormData.actualPayment], () => {
  // 只有在用戶沒有手動編輯過結果說明時，才自動更新金額
  if (isManuallyEditedDescription.value) {
    console.log('結果說明已手動編輯，跳過金額同步');
    return;
  }

  const currentResult = localFormData.isReinspection ? localFormData.reinspectionResult : localFormData.testResult;

  // 如果有測試結果，更新結果說明中的金額
  if (currentResult) {
    nextTick(() => {
      isAutoSyncingDescription.value = true;

      // 找到對應的測試結果選項（會自動包含最新的金額）
      const selectedOption = testResultOptions.value.find(option => option.value === currentResult);
      if (selectedOption) {
        // 移除括號內容後再設置到結果說明
        const cleanTitle = removeParenthesesContent(selectedOption.title);
        console.log('金額變化: 自動更新結果說明中的金額:', cleanTitle);
        localFormData.testResultDescription = cleanTitle;

        // 延遲更新父組件資料
        nextTick(() => {
          updateFormData();
          nextTick(() => {
            isAutoSyncingDescription.value = false;
          });
        });
      } else {
        isAutoSyncingDescription.value = false;
      }
    });
  }
});

// 監聽案件狀態變化，當狀態為 withdrawn 時自動勾選複驗
watch(() => grantsStore.currentGrant?.status, (newStatus) => {
  if (newStatus === 'withdrawn') {
    console.log('案件狀態為 withdrawn，自動勾選複驗');
    localFormData.isReinspection = true;
    updateFormData();
  }
}, { immediate: true });

// 監聽父組件數據變化
watch(() => props.formData, (newVal) => {
  if (newVal) {
    // 更新基本屬性
    Object.keys(localFormData).forEach(key => {
      // 🔒 排除應從 API 載入的照片欄位，避免被覆蓋
      if (key === 'beforePhotoPreviews' ||
          key === 'beforeConstructionPhotos' ||
          key === 'afterPhotoPreviews' ||
          key === 'afterConstructionPhotos') {
        return;
      }

      if (newVal[key] !== undefined &&
          JSON.stringify(newVal[key]) !== JSON.stringify((localFormData as any)[key])) {
        // 如果正在自動同步結果說明，跳過 testResultDescription 的更新
        if (key === 'testResultDescription' && isAutoSyncingDescription.value) {
          return;
        }
        // 如果用戶已經手動編輯過結果說明，也跳過自動覆蓋
        if (key === 'testResultDescription' && isManuallyEditedDescription.value) {
          return;
        }
        const val = newVal[key];
        (localFormData as any)[key] = PAYMENT_KEYS.includes(key as any) ? formatWithCommas(val) : val;
      }
    });

    // 更新變更設計項目
    if (Array.isArray(newVal.designChangeItems) &&
        JSON.stringify(newVal.designChangeItems) !== JSON.stringify(designChangeItems)) {
      // Clear existing items
      while (designChangeItems.length > 0) {
        designChangeItems.pop();
      }

      // Add new items
      newVal.designChangeItems.forEach(item => {
        designChangeItems.push({ ...item });
      });
    }
  }
}, { deep: true });

// 監聽表單驗證狀態變化
watch(localValid, (newVal) => {
  if (props.formData?.valid !== newVal) {
    updateFormData();
  }
});

// 監聽當前案件變化，重新載入版本比較
watch(() => grantsStore.currentGrant?.case_number, (newCaseNumber, oldCaseNumber) => {
  if (newCaseNumber && newCaseNumber !== oldCaseNumber) {
    console.log('案件變更，重新載入版本比較:', newCaseNumber);
    loadVersionComparison();
  }
});

// 監聽 Step3 和 Step4 資料變化，自動更新補助金額
watch(
  [
    () => grantsStore.formData[3],
    () => grantsStore.formData[4],
    () => (grantsStore.currentGrant?.active_version as any)?.all_steps_data?.steps?.['3'],
    () => (grantsStore.currentGrant?.active_version as any)?.all_steps_data?.steps?.['4']
  ],
  (newValues, oldValues) => {
    console.log('Step7: watch 被觸發，檢查變化:', {
      step3FormDataKeys: newValues[0] ? Object.keys(newValues[0]) : [],
      step4FormDataKeys: newValues[1] ? Object.keys(newValues[1]) : [],
      step3AllStepsDataKeys: newValues[2] ? Object.keys(newValues[2]) : [],
      step4AllStepsDataKeys: newValues[3] ? Object.keys(newValues[3]) : [],
      step3CaseNumber: newValues[0]?._caseNumber,
      step4CaseNumber: newValues[1]?._caseNumber,
      currentCaseNumber: route.query.id
    });

    // 檢查是否有實際的資料變化
    const hasChanges = newValues.some((newVal, index) => {
      const oldVal = oldValues?.[index];
      const hasChange = JSON.stringify(newVal) !== JSON.stringify(oldVal);
      if (hasChange) {
        console.log(`🔍 Step7: 資料源 ${index} 有變化:`, {
          dataType: index === 0 ? 'step3FormData' :
                   index === 1 ? 'step4FormData' :
                   index === 2 ? 'step3AllStepsData' : 'step4AllStepsData',
          newKeys: newVal ? Object.keys(newVal) : [],
          oldKeys: oldVal ? Object.keys(oldVal) : []
        });
      }
      return hasChange;
    });

    if (hasChanges) {
      console.log('Step7: 偵測到 Step3 或 Step4 資料變化，重新計算補助金額');

      // 重新計算補助金額
      const calculatedBudget = calculateTotalBudget();

      if (calculatedBudget > 0) {
        const newAmount = calculatedBudget.toLocaleString();

        // 只有當金額真的有變化時才更新
        if (localFormData.originalPayment !== newAmount) {
          console.log('💰 Step7: 補助金額更新', {
            原金額: localFormData.originalPayment,
            新金額: newAmount,
            計算詳情: {
              pipelineValue: calculatePipeLineSubsidy(),
              facilityValue: calculateFacilitySubsidy(),
              designValue: getDesignFee()  // 從 step4 讀取，不重新計算
            }
          });

          // 更新補助金額
          localFormData.originalPayment = newAmount;

          // 如果是原補助款發放模式，同時更新實際發放金額
          if (localFormData.testResult === 'original') {
            localFormData.actualPayment = newAmount;
          }

          // 更新父組件
          updateFormData();
        }
      }
    }
  },
  {
    deep: true, // 深度監聽物件屬性變化
    flush: 'post' // 在 DOM 更新後觸發
  }
);

// 額外的 watchEffect 用於更強的響應式監聽
watchEffect(() => {
  // 只有在正確的頁面和步驟時才運行
  const currentCaseNumber = route.query.id as string;
  if (!currentCaseNumber || route.query.step !== '7') return;

  // 訪問資料源以建立響應式依賴
  const step3Data = grantsStore.formData[3];
  const step4Data = grantsStore.formData[4];
  const step3AllSteps = (grantsStore.currentGrant?.active_version as any)?.all_steps_data?.steps?.['3'];
  const step4AllSteps = (grantsStore.currentGrant?.active_version as any)?.all_steps_data?.steps?.['4'];

  // 檢查是否有有效的資料變化
  const hasValidStep3Data = (step3Data?._caseNumber === currentCaseNumber && Object.keys(step3Data).length > 1) ||
                           (step3AllSteps && Object.keys(step3AllSteps).length > 0);

  const hasValidStep4Data = (step4Data?._caseNumber === currentCaseNumber && Object.keys(step4Data).length > 1) ||
                           (step4AllSteps && Object.keys(step4AllSteps).length > 0);

  if (hasValidStep3Data || hasValidStep4Data) {
    console.log('Step7: watchEffect 偵測到有效的資料變化，觸發重新計算:', {
      hasValidStep3Data,
      hasValidStep4Data,
      step3Keys: step3Data ? Object.keys(step3Data) : [],
      step4Keys: step4Data ? Object.keys(step4Data) : []
    });

    // 觸發 computedTotalBudget 重新計算
    const newBudget = computedTotalBudget.value;
    console.log('Step7: watchEffect 計算結果:', newBudget);
  }
});

// 組件卸載時清理資源
onUnmounted(() => {
  cleanupPreviews();
});

// 處理存檔請求
const handleSaveRequest = () => {
  console.log('處理存檔請求');
  saveConfirmDialog.value = true;
};

// 處理結案請求
const handleProceedRequest = () => {
  console.log('處理結案請求');
  updateFormData();
  emit('proceed-to-next-step');
};

// 統一的動作請求處理器
const handleActionRequest = (action: string) => {
  console.log('接收到動作請求:', action);

  if (action === 'save') {
    handleSaveRequest();
  } else if (action === 'proceed') {
    handleProceedRequest();
  }
};

// 只暴露動作請求處理器
defineExpose({
  handleActionRequest
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

.preview-table {
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

.text-red {
  color: red;
}

.design-change-table {
  width: 100%;
  border-collapse: collapse;
}

.design-change-table th,
.design-change-table td {
  border: 1px solid rgba(0, 0, 0, 0.12);
  padding: 8px;
}

.design-change-table th {
  background-color: rgba(0, 0, 0, 0.05);
  font-weight: 600;
}

/* 版本比較表特殊樣式 */
.design-change-table tbody tr.bg-green-lighten-5 {
  background-color: rgba(76, 175, 80, 0.1) !important;
}

.design-change-table tbody tr.bg-red-lighten-5 {
  background-color: rgba(244, 67, 54, 0.1) !important;
}

.design-change-table tbody tr.bg-yellow-lighten-5 {
  background-color: rgba(255, 193, 7, 0.1) !important;
}

.design-change-table tbody tr:hover {
  background-color: rgba(62, 160, 163, 0.1) !important;
}

/* 數量變更文字顏色 */
.text-green-darken-2 {
  color: #2e7d32 !important;
  font-weight: 500;
}

.text-red-darken-2 {
  color: #c62828 !important;
  font-weight: 500;
}

/* 版本比較區塊樣式 */
.version-comparison-summary {
  border-left: 4px solid #3ea0a3;
  padding-left: 12px;
}

/* 必填欄位紅色星號樣式 */
.required-asterisk {
  color: #ff0000 !important;
  font-weight: bold;
  margin-left: 2px;
}

/* 照片卡片樣式 */
.photo-card {
  height: 160px;
  cursor: default;
  transition: all 0.2s ease-in-out;
}

.photo-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}

.add-photo-card {
  cursor: pointer;
  border: 2px dashed #e0e0e0;
  background-color: #fafafa;
}

.add-photo-card:hover {
  border-color: #3ea0a3;
  background-color: #f5f5f5;
}

.upload-zone {
  cursor: pointer;
  border: 2px dashed #e0e0e0;
  background-color: #fafafa;
  transition: all 0.2s ease-in-out;
}

.upload-zone:hover {
  border-color: #3ea0a3;
  background-color: #f5f5f5;
}
</style>
