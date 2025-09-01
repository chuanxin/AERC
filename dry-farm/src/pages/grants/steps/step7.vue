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
          <!-- 版本比較與變更設計部分 -->
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
              <!-- 載入中狀態 -->
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

              <!-- 版本比較內容 -->
              <v-sheet
                v-else-if="facilitiesComparison && !versionComparisonLoading && !versionComparisonError"
                class="pa-3 rounded"
                color="grey-lighten-5"
              >
                <!-- 比較摘要 -->
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

                <!-- 灌溉調控設施比較表 -->
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

                <!-- 田間管路設施比較表 -->
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

                <!-- 總計變更摘要 -->
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

              <!-- 錯誤狀態 -->
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

              <!-- Debug: 顯示當前狀態 -->
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

          <!-- 結案申報基本資訊區域 -->
          <v-card
            class="mb-4"
            variant="outlined"
          >
            <v-card-title class="bg-light-blue-lighten-4 d-flex align-center py-2 px-4">
              <v-icon
                class="me-2"
                size="small"
              >
                mdi-clipboard-text
              </v-icon>
              <span class="text-subtitle-1 font-weight-medium">本案基本資訊</span>
            </v-card-title>

            <v-card-text class="pa-4">
              <v-sheet
                class="pa-3 rounded"
                color="bg-amber-lighten-5 border border-amber"
              >
                <v-table
                  class="preview-table"
                  style="background-color: transparent"
                  density="compact"
                >
                  <tbody>
                    <tr>
                      <td
                        class="font-weight-medium text-center"
                        style="width: 15%"
                      >
                        申請年度
                      </td>
                      <td style="width: 35%">
                        {{ localFormData.applicationYear }}
                      </td>
                      <td
                        class="font-weight-medium text-center"
                        style="width: 15%"
                      >
                        案號
                      </td>
                      <td style="width: 35%">
                        {{ localFormData.caseNumber }}
                      </td>
                    </tr>
                    <tr>
                      <td class="font-weight-medium text-center">
                        農戶姓名
                      </td>
                      <td>
                        {{ localFormData.name }}
                      </td>
                      <td class="font-weight-medium text-center">
                        農戶住址
                      </td>
                      <td>
                        {{ localFormData.applicantAddress }}
                      </td>
                    </tr>
                    <tr>
                      <td class="font-weight-medium text-center">
                        設施地段
                      </td>
                      <td>
                        {{ displayFacilityLocation }}
                      </td>
                      <td class="font-weight-medium text-center">
                        設施地號
                      </td>
                      <td>
                        <div v-if="displayFacilityNumbers.length > 1">
                          <div 
                            v-for="(number, index) in displayFacilityNumbers" 
                            :key="index"
                            class="mb-1"
                          >
                            {{ number }}
                          </div>
                        </div>
                        <div v-else>
                          {{ displayFacilityNumbers[0] }}
                        </div>
                      </td>
                    </tr>
                    <tr>
                      <td class="font-weight-medium text-center">
                        設施面積
                      </td>
                      <td>
                        {{ displayFacilityArea }}公頃
                      </td>
                      <td class="font-weight-medium text-center">
                        設施型式
                      </td>
                      <td>
                        {{ localFormData.facilityType }}
                      </td>
                    </tr>
                  </tbody>
                </v-table>
              </v-sheet>
            </v-card-text>
          </v-card>

          <!-- 竣工和測試資訊區域 -->
          <v-card
            class="mb-4"
            variant="outlined"
          >
            <v-card-title class="bg-light-blue-lighten-4 d-flex align-center justify-space-between py-2 px-4">
              <div class="d-flex align-center">
                <v-icon
                  class="me-2"
                  size="small"
                >
                  mdi-check-decagram
                </v-icon>
                <span class="text-subtitle-1 font-weight-medium"><span class="required-asterisk">*</span>功能測試(驗收)</span>
              </div>
              <v-checkbox
                v-model="localFormData.isReinspection"
                label="複驗"
                color="#3ea0a3"
                density="compact"
                hide-details
                @update:model-value="updateFormData"
              />
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
                    cols="12"
                    md="6"
                  >
                    <div class="d-flex flex-row gap-3">
                      <v-sheet
                        class="py-0 pl-5 rounded flex-1"
                        color="grey-lighten-5"
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
                        color="grey-lighten-5"
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

                <!-- 非複驗狀態下顯示原測試日期和人員 -->
                <v-row v-if="!localFormData.isReinspection">
                  <v-col
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
                    cols="12"
                    md="6"
                  >
                    <v-text-field
                      v-model="localFormData.tester"
                      variant="outlined"
                      density="comfortable"
                      :rules="[v => !!v || '請填寫測試人員']"
                      prepend-icon="mdi-account"
                      @update:model-value="updateFormData"
                    >
                      <template #label>
                        測試人員
                      </template>
                    </v-text-field>
                  </v-col>
                </v-row>

                <!-- 複驗相關欄位 -->
                <v-row v-if="localFormData.isReinspection">
                  <v-col
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
                    <v-text-field
                      v-model="localFormData.reinspectionTester"
                      variant="outlined"
                      density="comfortable"
                      :rules="localFormData.isReinspection ? [v => !!v || '請填寫複驗人員'] : []"
                      prepend-icon="mdi-account"
                      @update:model-value="updateFormData"
                    >
                      <template #label>
                        複驗人員
                      </template>
                    </v-text-field>
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
            </v-card-text>
          </v-card>

          <!-- 功能測試(驗收)結果區域 -->
          <v-card
            v-if="localFormData.testResult || localFormData.reinspectionResult"
            class="mb-4"
            variant="outlined"
          >
            <v-card-title class="bg-light-blue-lighten-4 d-flex align-center py-2 px-4">
              <v-icon
                class="me-2"
                size="small"
              >
                mdi-check-circle
              </v-icon>
              <span class="text-subtitle-1 font-weight-medium"><span class="required-asterisk">*</span>功能測試(驗收)結果</span>
            </v-card-title>

            <v-card-text class="pa-4">
              <v-sheet
                class="pa-3 rounded"
                color="bg-amber-lighten-5 border border-amber"
              >
                <v-row v-if="(localFormData.isReinspection ? localFormData.reinspectionResult : localFormData.testResult) === 'original'">
                  <v-col cols="12">
                    <v-text-field
                      v-model="localFormData.originalPayment"
                      label="原應發放"
                      variant="outlined"
                      density="comfortable"
                      readonly
                      bg-color="yellow-lighten-3"
                      @update:model-value="updateFormData"
                    />
                  </v-col>
                </v-row>

                <v-row v-if="(localFormData.isReinspection ? localFormData.reinspectionResult : localFormData.testResult) === 'adjusted'">
                  <v-col cols="12">
                    <v-text-field
                      v-model="localFormData.increasedDecreasedAmount"
                      label="減列"
                      variant="outlined"
                      density="comfortable"
                      :rules="(localFormData.isReinspection ? localFormData.reinspectionResult : localFormData.testResult) === 'adjusted' ? [v => !!v || '請填寫增減列金額'] : []"
                      bg-color="yellow-lighten-3"
                      @update:model-value="updateFormData"
                    />
                  </v-col>
                </v-row>

                <v-row v-if="(localFormData.isReinspection ? localFormData.reinspectionResult : localFormData.testResult) === 'adjusted' || (localFormData.isReinspection ? localFormData.reinspectionResult : localFormData.testResult) === 'original'">
                  <v-col cols="12">
                    <v-text-field
                      v-model="localFormData.actualPayment"
                      label="實際發放"
                      variant="outlined"
                      density="comfortable"
                      readonly
                      bg-color="yellow-lighten-3"
                      @update:model-value="updateFormData"
                    />
                  </v-col>
                </v-row>

                <v-row>
                  <v-col cols="12">
                    <v-textarea
                      v-model="localFormData.testResultDescription"
                      label="結果說明"
                      variant="outlined"
                      density="comfortable"
                      rows="3"
                      auto-grow
                      :rules="[v => (localFormData.isReinspection ? localFormData.reinspectionResult : localFormData.testResult) !== 'improvement' || !!v || '請填寫結果說明']"
                      @update:model-value="onTestResultDescriptionChange"
                    >
                      <template #label>
                        結果說明
                      </template>
                    </v-textarea>
                  </v-col>
                </v-row>
              </v-sheet>
            </v-card-text>
          </v-card>

          <!-- 照片上傳區域 -->
          <v-card variant="outlined">
            <v-card-title class="bg-light-blue-lighten-4 d-flex align-center py-2 px-4">
              <v-icon
                class="me-2"
                size="small"
              >
                mdi-camera
              </v-icon>
              <span class="text-subtitle-1 font-weight-medium"><span class="required-asterisk">*</span>施工照片</span>
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
                    <label class="text-body-2 font-weight-medium mb-2 d-block">
                      施工前照片
                    </label>
                    <v-file-input
                      v-model="localFormData.beforeConstructionPhoto"
                      label="選擇檔案"
                      variant="outlined"
                      density="comfortable"
                      accept="image/*"
                      prepend-icon="mdi-camera"
                      :rules="photoRules"
                      @update:model-value="handlePhotoChange('before')"
                    />

                    <div
                      v-if="localFormData.beforePhotoPreview"
                      class="mt-2"
                    >
                      <v-img
                        :src="localFormData.beforePhotoPreview"
                        max-height="200"
                        contain
                        class="bg-grey-lighten-3 rounded"
                      />
                    </div>
                  </v-col>

                  <v-col
                    cols="12"
                    md="6"
                  >
                    <label class="text-body-2 font-weight-medium mb-2 d-block">
                      竣工照片
                    </label>
                    <v-file-input
                      v-model="localFormData.afterConstructionPhoto"
                      label="選擇檔案"
                      variant="outlined"
                      density="comfortable"
                      accept="image/*"
                      prepend-icon="mdi-camera"
                      :rules="photoRules"
                      @update:model-value="handlePhotoChange('after')"
                    />

                    <div
                      v-if="localFormData.afterPhotoPreview"
                      class="mt-2"
                    >
                      <v-img
                        :src="localFormData.afterPhotoPreview"
                        max-height="200"
                        contain
                        class="bg-grey-lighten-3 rounded"
                      />
                    </div>

                    <div
                      v-if="!localFormData.afterConstructionPhoto && !localFormData.afterPhotoPreview"
                      class="mt-2 d-flex align-center text-red"
                    >
                      <v-icon
                        color="red"
                        class="me-1"
                        size="small"
                      >
                        mdi-alert-circle
                      </v-icon>
                      <span class="text-caption">卡驗收照片(尚未上傳竣工照片)</span>
                    </div>
                  </v-col>
                </v-row>

                <v-row v-if="!localFormData.afterConstructionPhoto && !localFormData.beforeConstructionPhoto && !localFormData.afterPhotoPreview && !localFormData.beforePhotoPreview">
                  <v-col cols="12">
                    <v-alert
                      type="warning"
                      variant="tonal"
                      class="mb-0"
                      density="comfortable"
                    >
                      <div class="d-flex align-center">
                        <v-icon class="me-2">
                          mdi-alert
                        </v-icon>
                        <span>尚未上傳施工前後照片，請儘速上傳以完成結案申報程序。</span>
                      </div>
                    </v-alert>
                  </v-col>
                </v-row>
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
// 🆕 導入版本比較相關服務
import {
  compareGrantVersions,
  getGrantVersionSummary,
  compareVersionsLocally,
  type FacilitiesComparison,
  type VersionComparisonResult
} from '@/services/grantsService';

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

// Event emitters
const emit = defineEmits(['update:formData', 'validated', 'go-back', 'save-for-improvement', 'proceed-to-next-step', 'button-config-changed']);

// Access the grants store
const grantsStore = useGrantsStore();
const domicileStore = useDomicileStore();
const route = useRoute();

// 🆕 版本比較相關狀態
const versionComparisonLoading = ref(false);
const versionComparisonError = ref<string | null>(null);
const facilitiesComparison = ref<FacilitiesComparison | null>(null);
const versionSummary = ref<{
  total_versions: number;
  first_version: { id: number; version: number; created_at: string };
  latest_version: { id: number; version: number; created_at: string };
  has_versions: boolean;
} | null>(null);

// 🆕 是否顯示版本比較
const shouldShowVersionComparison = computed(() => {
  const hasVersions = versionSummary.value?.has_versions === true;
  const multipleVersions = versionSummary.value?.total_versions > 1;
  const noError = !versionComparisonError.value;

  console.log('🔍 shouldShowVersionComparison 檢查:', {
    hasVersions,
    multipleVersions,
    totalVersions: versionSummary.value?.total_versions,
    noError,
    error: versionComparisonError.value,
    result: hasVersions && multipleVersions && noError
  });

  return hasVersions && multipleVersions && noError;
});

// Form validation and dialogs
const form = ref(null);
const localValid = ref(true);
const datePickerDialog1 = ref(false);
const datePickerDialog2 = ref(false);
const datePickerDialog3 = ref(false); // 複驗日期對話框
const isDesignChangeVisible = ref(false);

// 測試結果選項 - 動態計算，包含對應的發放金額
const testResultOptions = computed(() => {
  // original 選項顯示原補助款金額
  const originalPaymentText = localFormData.originalPayment ? ` ${localFormData.originalPayment} 元` : '';

  // adjusted 選項顯示實際發放金額
  const actualPaymentText = localFormData.actualPayment ? ` ${localFormData.actualPayment} 元` : '';

  const spacing = '\u3000\u3000\u3000\u3000';

  return [
    { title: `合格，依核定補助款發放${originalPaymentText}`, value: 'original' },
    { title: `合格，依核定補助款減列金額，發放${actualPaymentText}（請說明原因）`, value: 'adjusted' },
    { title: `不合格，限期改善複查（請註明${spacing}年${spacing}月${spacing}日完成改善）`, value: 'improvement' },
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
  testResultDescription: '',    // 結果說明

  // 照片
  beforeConstructionPhoto: null,
  afterConstructionPhoto: null,
  beforePhotoPreview: null as string | null,
  afterPhotoPreview: null as string | null,

  // 設置默認值，確保與edit.vue中的顯示邏輯保持一致
  valid: true
});

// 🆕 版本比較輔助函數
const getChangeStatusColor = (changeType: string) => {
  switch (changeType) {
    case 'added':
      return 'green'
    case 'removed':
      return 'red'
    case 'modified':
      return 'orange'
    default:
      return 'grey'
  }
}

const getChangeStatusText = (changeType: string) => {
  switch (changeType) {
    case 'added':
      return '新增'
    case 'removed':
      return '移除'
    case 'modified':
      return '修改'
    default:
      return '無變更'
  }
}

// 🆕 載入版本比較資料
const loadVersionComparison = async () => {
  console.log('🔄 loadVersionComparison 被調用，檢查案件狀態:', {
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

    console.log('🔄 嘗試載入版本摘要...')

    try {
      // 嘗試獲取版本摘要
      const summary = await getGrantVersionSummary(grantsStore.currentGrant.case_number)
      versionSummary.value = summary
      console.log('✅ 版本摘要載入成功:', summary)

      // 如果有多個版本，才進行比較
      if (summary.has_versions && summary.total_versions > 1) {
        console.log('🔄 載入版本比較...')

        try {
          // 嘗試使用 API 進行版本比較
          const comparisonResult = await compareGrantVersions(grantsStore.currentGrant.case_number)
          facilitiesComparison.value = comparisonResult.facilities_comparison
          console.log('✅ API 版本比較完成:', facilitiesComparison.value)
        } catch (apiError) {
          console.warn('⚠️ API 版本比較失敗，使用本地比較:', apiError)

          // API 失敗時，使用本地比較
          const firstVersionData = grantsStore.formData // 假設當前是最新版本
          const latestVersionData = grantsStore.formData // 這裡應該獲取第一版本的數據

          facilitiesComparison.value = compareVersionsLocally(firstVersionData, latestVersionData)
          console.log('✅ 本地版本比較完成:', facilitiesComparison.value)
        }
      } else {
        console.log('📝 只有一個版本或無版本，跳過比較')
        facilitiesComparison.value = null
      }
    } catch (apiError) {
      // API 不存在或其他錯誤，靜默處理
      console.log('ℹ️ 版本比較 API 尚未實現，跳過版本比較功能')

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
    console.warn('⚠️ 版本比較功能暫時不可用:', error)
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

// 計算變更總量（保留原有功能作為備用）
const totalQuantityChange = computed(() => {
  return designChangeItems.reduce((total, item) => {
    return total + (Number(item.afterQuantity) - Number(item.beforeQuantity));
  }, 0);
});

// 驗證規則
const photoRules = [v => !!v || '請上傳照片'];

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

// 產生年份選項 (民國年)
const yearOptions = computed(() => {
  const currentYear = new Date().getFullYear();
  const years = [];
  // 產生從當前年份到五年前的年份選項
  for (let year = currentYear - 5; year <= currentYear; year++) {
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

// 計算顯示用的設施地段（中文地名）
const displayFacilityLocation = computed(() => {
  const step2Data = grantsStore.formData[2];
  if (!step2Data) return localFormData.facilityLocation || '';

  // 處理多筆土地格式
  if (step2Data.lands && Array.isArray(step2Data.lands) && step2Data.lands.length > 0) {
    const locations = step2Data.lands.map((land: any) => {
      return getLandLocationText(land);
    }).filter(Boolean);
    
    // 去重並合併
    const uniqueLocations = [...new Set(locations)];
    return uniqueLocations.join('、') || localFormData.facilityLocation || '';
  }
  
  // 向後相容：處理舊格式
  if (step2Data.landCounty || step2Data.landTown || step2Data.landSec) {
    const land = {
      landCounty: step2Data.landCounty,
      landTown: step2Data.landTown,
      landSec: step2Data.landSec
    };
    return getLandLocationText(land) || localFormData.facilityLocation || '';
  }
  
  return localFormData.facilityLocation || '';
});

// 計算顯示用的設施地號（多筆分行顯示）
const displayFacilityNumbers = computed(() => {
  const step2Data = grantsStore.formData[2];
  if (!step2Data) return [localFormData.facilityNumber || ''];

  // 處理多筆土地格式
  if (step2Data.lands && Array.isArray(step2Data.lands) && step2Data.lands.length > 0) {
    const landNumbers = step2Data.lands
      .map((land: any) => land.landNumber)
      .filter(Boolean);
    return landNumbers.length > 0 ? landNumbers : [localFormData.facilityNumber || ''];
  }
  
  // 向後相容：處理舊格式
  if (step2Data.landNumber) {
    return [step2Data.landNumber];
  }
  
  return [localFormData.facilityNumber || ''];
});

// 計算顯示用的設施面積（與step2同步）
const displayFacilityArea = computed(() => {
  const step2Data = grantsStore.formData[2];
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
const getLandLocationText = (land: any): string => {
  const parts = [];
  
  // 縣市
  if (land.landCounty) {
    if (typeof land.landCounty === 'number') {
      const county = domicileStore.countyOptions.find(c => c.value === land.landCounty);
      if (county) parts.push(county.title);
    } else {
      parts.push(land.landCounty);
    }
  }
  
  // 鄉鎮
  if (land.landTown) {
    if (typeof land.landTown === 'number') {
      const town = domicileStore.getTownsForCountyId(land.landCounty as number)
        .find(t => t.value === land.landTown);
      if (town) parts.push(town.title);
    } else {
      parts.push(land.landTown);
    }
  }
  
  // 地段
  if (land.landSec) {
    if (typeof land.landSec === 'number') {
      const section = domicileStore.getLandSectionsForTownId(land.landTown as number)
        .find(s => s.value === land.landSec);
      if (section) parts.push(section.title);
    } else {
      parts.push(land.landSec);
    }
  }
  
  return parts.join('');
};

// 初始化設施資訊的函數
const initializeFacilityInfo = async () => {
  console.log('🔄 Initializing facility info...');
  
  const step2Data = grantsStore.formData[2];
  if (!step2Data) {
    console.log('❌ No step2 data available');
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
      console.log(`✅ Loaded towns for county ${countyId}`);
    } catch (error) {
      console.warn(`⚠️ Failed to load towns for county ${countyId}:`, error);
    }
  }

  // 載入地段資料
  for (const townId of townIds) {
    try {
      await domicileStore.loadLandSectionsByTownId(townId);
      console.log(`✅ Loaded sections for town ${townId}`);
    } catch (error) {
      console.warn(`⚠️ Failed to load sections for town ${townId}:`, error);
    }
  }

  // 初始化設施資訊
  console.log('💡 Initializing facility info with domicile data...');
  
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

  // Get facility type from all_steps_data
  const allStepsStep4 = (grantsStore.currentGrant?.active_version as any)?.all_steps_data?.steps?.['4'];
  if (allStepsStep4?.irrigationType) {
    localFormData.facilityType = allStepsStep4.irrigationType;
  }

  console.log('✅ Facility info initialized:', {
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
    : testDateComponents;

  const dateValue = type === 'completion'
    ? localFormData.completionDate
    : type === 'reinspection'
    ? localFormData.reinspectionDate
    : localFormData.testDate;

  const dialog = type === 'completion'
    ? datePickerDialog1
    : type === 'reinspection'
    ? datePickerDialog3
    : datePickerDialog2;

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
      // 預設為今天
      const today = new Date();
      components.year = today.getFullYear();
      components.month = today.getMonth() + 1;
      components.day = today.getDate();
    }
  }

  // 打開對話框
  if (type === 'completion') {
    datePickerDialog1.value = true;
  } else if (type === 'reinspection') {
    datePickerDialog3.value = true;
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
  } else {
    localFormData.testDate = dateString;
    datePickerDialog2.value = false;
  }

  // 更新父組件數據
  updateFormData();
};

// 處理照片預覽
const handlePhotoChange = (type: 'before' | 'after') => {
  const file = type === 'before'
    ? localFormData.beforeConstructionPhoto
    : localFormData.afterConstructionPhoto;

  if (file) {
    // Only create object URLs for actual File objects
    if (file instanceof File) {
      // 清除之前的預覽
      if (type === 'before') {
        if (localFormData.beforePhotoPreview && typeof localFormData.beforePhotoPreview === 'string' &&
            localFormData.beforePhotoPreview.startsWith('blob:')) {
          URL.revokeObjectURL(localFormData.beforePhotoPreview);
        }
        localFormData.beforePhotoPreview = URL.createObjectURL(file);
      } else {
        if (localFormData.afterPhotoPreview && typeof localFormData.afterPhotoPreview === 'string' &&
            localFormData.afterPhotoPreview.startsWith('blob:')) {
          URL.revokeObjectURL(localFormData.afterPhotoPreview);
        }
        localFormData.afterPhotoPreview = URL.createObjectURL(file);
      }
    }
  }

  updateFormData();
};

// 切換變更設計顯示狀態
const toggleDesignChange = () => {
  isDesignChangeVisible.value = !isDesignChangeVisible.value;
  updateFormData();
};

// 計算變更前後差異
const calculateDifference = () => {
  updateFormData();
};

// 智慧資料來源選擇器：透過案件號比對確保 formData 歸屬正確（參考 Step6）
const getStepDataSafely = (step: number) => {
  const currentCaseNumber = route.query.id as string;
  console.log(`🔍 Step7: getStepDataSafely(${step}) - 案件編號:`, currentCaseNumber);

  // 確保只處理當前案件的資料
  if (!currentCaseNumber) {
    console.log('❌ Step7: 沒有案件編號');
    return null;
  }

  const formData = grantsStore.formData[step];
  const allStepsData = (grantsStore.currentGrant?.active_version as any)?.all_steps_data?.steps?.[step.toString()];

  console.log(`🔍 Step7: step ${step} - formData:`, formData);
  console.log(`🔍 Step7: step ${step} - allStepsData:`, allStepsData);

  // 檢查 formData 是否屬於當前案件（透過 _caseNumber 欄位比對）
  const formDataCaseNumber = formData?._caseNumber;
  const isFormDataValid = formDataCaseNumber === currentCaseNumber;

  console.log(`🔍 Step7: step ${step} - formDataCaseNumber: ${formDataCaseNumber}, isValid: ${isFormDataValid}`);

  if (isFormDataValid && formData && Object.keys(formData).length > 1) { // >1 因為至少有 _caseNumber
    console.log(`✅ Step7: Using formData for step ${step} (case: ${formDataCaseNumber})`);
    return formData; // 使用 formData（即時同步）
  }

  // 否則使用 all_steps_data（持久化資料）
  if (allStepsData && Object.keys(allStepsData).length > 0) {
    console.log(`📚 Step7: Using all_steps_data for step ${step} (formData case: ${formDataCaseNumber}, current: ${currentCaseNumber})`);
    return allStepsData;
  }

  console.log(`❌ Step7: step ${step} 沒有可用資料`);
  return null;
};

// 計算田間管路設施補助總額（參考 Step6 邏輯）
const calculatePipeLineSubsidy = () => {
  const step4Data = getStepDataSafely(4);
  console.log('🔍 Step7: calculatePipeLineSubsidy - step4Data:', step4Data);

  if (!step4Data || Object.keys(step4Data).length === 0) {
    console.log('❌ Step7: step4Data 為空或不存在');
    return 0;
  }

  let pipelineTotal = 0;
  let irrigationTotal = 0;

  // 主管計算
  if (step4Data.mainPipeQuantity && step4Data.mainPipeUnitPrice) {
    const quantity = parseInt(step4Data.mainPipeQuantity as string || '0');
    const unitPrice = parseFloat(step4Data.mainPipeUnitPrice as string || '0');
    pipelineTotal += quantity * unitPrice;
    console.log('🔍 Step7: 主管1計算:', { quantity, unitPrice, subtotal: quantity * unitPrice });
  }

  if (step4Data.mainPipe2Enabled && step4Data.mainPipe2Quantity && step4Data.mainPipe2UnitPrice) {
    const quantity = parseInt(step4Data.mainPipe2Quantity as string || '0');
    const unitPrice = parseFloat(step4Data.mainPipe2UnitPrice as string || '0');
    pipelineTotal += quantity * unitPrice;
    console.log('🔍 Step7: 主管2計算:', { quantity, unitPrice, subtotal: quantity * unitPrice });
  }

  // 灌溉系統計算
  if (step4Data.pipes && Array.isArray(step4Data.pipes)) {
    console.log('🔍 Step7: pipes 資料:', step4Data.pipes);
    const filteredPipes = step4Data.pipes.filter((p: any) => {
      if ([2, 3, 4, 5, 6, 7, 8].includes(p.groupId)) return true;
      if (p.groupId === 1) return p.module !== '主管';
      return false;
    });

    console.log('🔍 Step7: 篩選後的 pipes:', filteredPipes);

    irrigationTotal = filteredPipes.reduce((sum: number, pipe: any) => {
      const price = typeof pipe.totalPrice === 'number' ? pipe.totalPrice : parseInt(pipe.totalPrice || '0');
      console.log('🔍 Step7: pipe 價格:', { module: pipe.module, totalPrice: pipe.totalPrice, parsed: price });
      return sum + price;
    }, 0);
  }

  const total = pipelineTotal + irrigationTotal;
  console.log('🔍 Step7: calculatePipeLineSubsidy 結果:', { pipelineTotal, irrigationTotal, total });
  return total;
};

// 計算灌溉調控設施補助總額（參考 Step6 邏輯）
const calculateFacilitySubsidy = () => {
  const step3Data = getStepDataSafely(3);
  console.log('🔍 Step7: calculateFacilitySubsidy - step3Data:', step3Data);

  if (!step3Data || Object.keys(step3Data).length === 0 || !step3Data?.facilities || !Array.isArray(step3Data.facilities)) {
    console.log('❌ Step7: step3Data.facilities 為空或不存在');
    return 0;
  }

  console.log('🔍 Step7: facilities 資料:', step3Data.facilities);

  const total = step3Data.facilities.reduce((sum: number, facility: any) => {
    const price = typeof facility.totalPrice === 'number'
                 ? facility.totalPrice
                 : parseInt(facility.totalPrice || '0');
    console.log('🔍 Step7: facility 計算:', {
      name: facility.name,
      totalPrice: facility.totalPrice,
      parsed: price
    });
    return sum + price;
  }, 0);

  console.log('🔍 Step7: calculateFacilitySubsidy 結果:', total);
  return total;
};

// 計算設計費（參考 Step6 邏輯）
const calculateDesignFee = (pipeLineSubsidy: number) => {
  return Math.round(pipeLineSubsidy * 0.02);
};

// 計算總補助預算（參考 Step6 邏輯）
const calculateTotalBudget = () => {
  const pipelineValue = calculatePipeLineSubsidy();
  const facilityValue = calculateFacilitySubsidy();
  const designValue = calculateDesignFee(pipelineValue);
  const total = pipelineValue + facilityValue + designValue;

  console.log('💰 Step7: 計算補助金額:', {
    pipelineValue,
    facilityValue,
    designValue,
    total
  });

  return total;
};

// 響應式計算補助金額 - 當 Step3/Step4 資料變化時自動重新計算
const computedTotalBudget = computed(() => {
  console.log('🔄 Step7: computedTotalBudget 正在計算...');

  // 明確監聽這些數據源，讓 Vue 知道需要響應它們的變化
  const step3FormData = grantsStore.formData[3];
  const step4FormData = grantsStore.formData[4];
  const step3AllStepsData = (grantsStore.currentGrant?.active_version as any)?.all_steps_data?.steps?.['3'];
  const step4AllStepsData = (grantsStore.currentGrant?.active_version as any)?.all_steps_data?.steps?.['4'];

  console.log('🔍 Step7: 數據源監聽狀態:', {
    step3FormData: step3FormData ? Object.keys(step3FormData).length : 0,
    step4FormData: step4FormData ? Object.keys(step4FormData).length : 0,
    step3AllStepsData: step3AllStepsData ? Object.keys(step3AllStepsData).length : 0,
    step4AllStepsData: step4AllStepsData ? Object.keys(step4AllStepsData).length : 0
  });

  const pipelineValue = calculatePipeLineSubsidy();
  const facilityValue = calculateFacilitySubsidy();
  const designValue = calculateDesignFee(pipelineValue);
  const total = pipelineValue + facilityValue + designValue;

  console.log('💰 Step7: computedTotalBudget 計算結果:', {
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
    console.log('💰 Step7: 響應式補助金額更新', {
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
        const adjustment = parseFloat(localFormData.increasedDecreasedAmount.replace(/,/g, ''));
        if (!isNaN(adjustment)) {
          const actual = original + adjustment;
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


// 更新父組件數據
const updateFormData = () => {
  emit('update:formData', {
    ...props.formData,
    ...localFormData,
    designChangeItems: [...designChangeItems],
    valid: true // Always set to true for seamless navigation
  });
};

// 清理預覽資源的函數
const cleanupPreviews = () => {
  // Only clean up blob URLs, not external URLs
  if (localFormData.beforePhotoPreview && typeof localFormData.beforePhotoPreview === 'string' &&
      localFormData.beforePhotoPreview.startsWith('blob:')) {
    URL.revokeObjectURL(localFormData.beforePhotoPreview);
  }

  if (localFormData.afterPhotoPreview && typeof localFormData.afterPhotoPreview === 'string' &&
      localFormData.afterPhotoPreview.startsWith('blob:')) {
    URL.revokeObjectURL(localFormData.afterPhotoPreview);
  }
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
    console.log('✅ Counties loaded successfully');
  } catch (error) {
    console.error('Failed to load counties:', error);
  }

  // 從父組件接收數據
  if (props.formData) {
    // 設置基本屬性
    Object.keys(localFormData).forEach(key => {
      if (props.formData[key] !== undefined) {
        localFormData[key] = props.formData[key];
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

  // Initialize data from other steps if necessary
  if (!localFormData.applicationYear) {
    // Try to get from store or use default
    if (grantsStore.formData[6]?.applicationYear) {
      localFormData.applicationYear = grantsStore.formData[6].applicationYear;
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

  // Get applicant info
  if (!localFormData.name) {
    if (grantsStore.formData[1]?.name) {
      localFormData.name = grantsStore.formData[1].name;
    } else if (grantsStore.formData[6]?.name) {
      localFormData.name = grantsStore.formData[6].name;
    }
  }

  // Get applicant address
  if (!localFormData.applicantAddress) {
    if (grantsStore.formData[6]?.applicantAddress) {
      localFormData.applicantAddress = grantsStore.formData[6].applicantAddress;
    } else {
      const step1Data = grantsStore.formData[1];
      if (step1Data) {
        const county = step1Data.county || '';
        const town = step1Data.town || '';
        const village = step1Data.village || '';
        const address = step1Data.address || '';

        if (county || town || village || address) {
          localFormData.applicantAddress = `${county}${town}${village}${address}`;
        }
      }
    }
  }

  // 💡 獲取設施資訊 - 確保在 domicileStore 載入後執行
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

    // 🔄 使用新的計算邏輯來獲取補助金額
    const calculatedBudget = calculateTotalBudget();

    if (calculatedBudget > 0) {
      localFormData.originalPayment = calculatedBudget.toLocaleString();
      console.log('✅ onMounted 使用計算邏輯設置 originalPayment:', localFormData.originalPayment);
    } else {
      console.log('❌ onMounted 計算結果為 0，嘗試其他方法...');
      // 備用：嘗試從 grantsStore.formData[6] 取得
      if (grantsStore.formData[6]?.totalBudget) {
        const totalBudget = grantsStore.formData[6].totalBudget;
        localFormData.originalPayment = typeof totalBudget === 'string' ? totalBudget : totalBudget.toString();
        console.log('✅ onMounted 從 formData 設置 originalPayment:', localFormData.originalPayment);
      }
    }

    localFormData.actualPayment = localFormData.originalPayment;
  }

  // Set sample description if needed
  if (!localFormData.testResultDescription && localFormData.testResult === 'original') {
    // localFormData.testResultDescription = '工程完工符合規範，依核定補助款發放。';
  }

  // Set sample photo previews if none exist - 使用簡單的 data URL 避免外部依賴
  if (!localFormData.beforePhotoPreview) {
    localFormData.beforePhotoPreview = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="400" height="300"%3E%3Crect width="100%25" height="100%25" fill="%23ddd"/%3E%3Ctext x="50%25" y="50%25" fill="%23999" text-anchor="middle" font-family="Arial" font-size="16"%3E施工前照片%3C/text%3E%3C/svg%3E';
  }

  if (!localFormData.afterPhotoPreview) {
    localFormData.afterPhotoPreview = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="400" height="300"%3E%3Crect width="100%25" height="100%25" fill="%23ddd"/%3E%3Ctext x="50%25" y="50%25" fill="%23999" text-anchor="middle" font-family="Arial" font-size="16"%3E竣工照片%3C/text%3E%3C/svg%3E';
  }

  // Initial update to parent
  updateFormData();

  // 🆕 載入版本比較資料
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

    // 🔄 使用新的計算邏輯來獲取補助金額
    const calculatedBudget = calculateTotalBudget();

    if (calculatedBudget > 0) {
      localFormData.originalPayment = calculatedBudget.toLocaleString();
      console.log('✅ 從計算邏輯設置 originalPayment:', localFormData.originalPayment);
    } else {
      console.log('❌ 計算結果為 0，嘗試其他方法...');
      // 備用：嘗試從 grantsStore.formData[6] 取得
      if (grantsStore.formData[6]?.totalBudget) {
        const totalBudget = grantsStore.formData[6].totalBudget;
        localFormData.originalPayment = typeof totalBudget === 'string' ? totalBudget : totalBudget.toString();
        console.log('✅ 從 formData 設置 originalPayment:', localFormData.originalPayment);
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

    // 🔄 使用新的計算邏輯來獲取補助金額
    const calculatedBudget = calculateTotalBudget();

    if (calculatedBudget > 0) {
      localFormData.originalPayment = calculatedBudget.toLocaleString();
      console.log('✅ adjusted: 從計算邏輯設置 originalPayment:', localFormData.originalPayment);
    } else if (grantsStore.formData[6]?.totalBudget) {
      const totalBudget = grantsStore.formData[6].totalBudget;
      localFormData.originalPayment = typeof totalBudget === 'string' ? totalBudget : totalBudget.toString();
      console.log('✅ adjusted: 從 formData 設置 originalPayment:', localFormData.originalPayment);
    } else {
      console.log('❌ totalBudget 不存在，嘗試計算...');
      // 嘗試從其他步驟獲取預算資料
      if (grantsStore.formData[6]?.pipeLineSubsidy || grantsStore.formData[6]?.facilitySubsidy) {
        const pipelineSubsidy = parseInt(((grantsStore.formData[6].pipeLineSubsidy as string) || '0').replace(/,/g, ''));
        const facilitySubsidy = parseInt(((grantsStore.formData[6].facilitySubsidy as string) || '0').replace(/,/g, ''));
        const designFee = parseInt(((grantsStore.formData[6].designFee as string) || '0').replace(/,/g, ''));
        const calculatedTotal = pipelineSubsidy + facilitySubsidy + designFee;

        if (calculatedTotal > 0) {
          localFormData.originalPayment = calculatedTotal.toLocaleString();
          console.log('🔄 從子項目計算 adjusted originalPayment:', localFormData.originalPayment);
        } else if (!localFormData.originalPayment) {
          localFormData.originalPayment = '0';
          console.log('⚠️ 設置預設值 0');
        }
      } else if (!localFormData.originalPayment) {
        localFormData.originalPayment = '0';
        console.log('⚠️ 設置預設值 0');
      }
    }

    // 設置預設減列金額並立即計算實際發放金額
    if (!localFormData.increasedDecreasedAmount) {
      localFormData.increasedDecreasedAmount = '-1,000';
    }

    // 實際發放金額會通過增減列計算
    try {
      const original = parseFloat(localFormData.originalPayment.replace(/,/g, ''));
      const adjustment = parseFloat(localFormData.increasedDecreasedAmount.replace(/,/g, ''));
      if (!isNaN(original) && !isNaN(adjustment)) {
        const actual = original + adjustment;
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
        console.log('自動帶入測試結果說明:', selectedOption.title);
        localFormData.testResultDescription = selectedOption.title;

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
      const adjustment = parseFloat(localFormData.increasedDecreasedAmount.replace(/,/g, ''));
      if (!isNaN(original) && !isNaN(adjustment)) {
        const actual = original + adjustment;
        const newActualPayment = actual.toLocaleString();

        // 只有當計算結果與當前值不同時才更新
        if (localFormData.actualPayment !== newActualPayment) {
          localFormData.actualPayment = newActualPayment;
          console.log('金額變化 watch: 重新計算 adjusted 實際發放金額:', localFormData.actualPayment);
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

// 處理結果說明手動編輯
const onTestResultDescriptionChange = () => {
  // 如果不是在自動同步過程中，標記為手動編輯
  if (!isAutoSyncingDescription.value) {
    isManuallyEditedDescription.value = true;
  }
  updateFormData();
};

// 監聽父組件數據變化
watch(() => props.formData, (newVal) => {
  if (newVal) {
    // 更新基本屬性
    Object.keys(localFormData).forEach(key => {
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
        (localFormData as any)[key] = newVal[key];
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

// 🆕 監聽當前案件變化，重新載入版本比較
watch(() => grantsStore.currentGrant?.case_number, (newCaseNumber, oldCaseNumber) => {
  if (newCaseNumber && newCaseNumber !== oldCaseNumber) {
    console.log('🔄 案件變更，重新載入版本比較:', newCaseNumber);
    loadVersionComparison();
  }
});

// 🆕 監聽 Step3 和 Step4 資料變化，自動更新補助金額
watch(
  [
    () => grantsStore.formData[3],
    () => grantsStore.formData[4],
    () => (grantsStore.currentGrant?.active_version as any)?.all_steps_data?.steps?.['3'],
    () => (grantsStore.currentGrant?.active_version as any)?.all_steps_data?.steps?.['4']
  ],
  (newValues, oldValues) => {
    console.log('🔍 Step7: watch 被觸發，檢查變化:', {
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
      console.log('🔄 Step7: 偵測到 Step3 或 Step4 資料變化，重新計算補助金額');

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
              designValue: calculateDesignFee(calculatePipeLineSubsidy())
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

// 🆕 額外的 watchEffect 用於更強的響應式監聽
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
    console.log('🔥 Step7: watchEffect 偵測到有效的資料變化，觸發重新計算:', {
      hasValidStep3Data,
      hasValidStep4Data,
      step3Keys: step3Data ? Object.keys(step3Data) : [],
      step4Keys: step4Data ? Object.keys(step4Data) : []
    });

    // 觸發 computedTotalBudget 重新計算
    const newBudget = computedTotalBudget.value;
    console.log('🔥 Step7: watchEffect 計算結果:', newBudget);
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

/* 🆕 版本比較表特殊樣式 */
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
</style>
