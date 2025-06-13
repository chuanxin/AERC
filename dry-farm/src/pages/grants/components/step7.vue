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
          <!-- 變更設計部分 -->
          <!-- <v-card
            class="mb-4"
            variant="outlined"
          >
            <v-card-title class="bg-light-blue-lighten-4 d-flex align-center py-2 px-4">
              <v-icon
                class="me-2"
                size="small"
              >
                mdi-file-compare
              </v-icon>
              <span class="text-subtitle-1 font-weight-medium">變更設計</span>
            </v-card-title>

            <v-card-text class="pa-4">
              <v-sheet
                class="pa-3 rounded"
                color="grey-lighten-5"
              >
                <v-btn
                  color="primary"
                  block
                  class="mb-4"
                  @click="toggleDesignChange"
                >
                  {{ isDesignChangeVisible ? '取消變更設計' : '進行變更設計' }}
                </v-btn>

                <div v-if="isDesignChangeVisible">
                  <v-table class="design-change-table border-table">
                    <thead>
                      <tr>
                        <th>變更項目</th>
                        <th>變更前數量</th>
                        <th>變更後數量</th>
                        <th>增減數量</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr
                        v-for="(item, index) in designChangeItems"
                        :key="index"
                      >
                        <td>{{ item.name }}</td>
                        <td>
                          <v-text-field
                            v-model="item.beforeQuantity"
                            variant="outlined"
                            density="compact"
                            type="number"
                            min="0"
                            :rules="[
                              v => v >= 0 || '數量不能為負數'
                            ]"
                            hide-details="auto"
                            @update:model-value="calculateDifference"
                          />
                        </td>
                        <td>
                          <v-text-field
                            v-model="item.afterQuantity"
                            variant="outlined"
                            density="compact"
                            type="number"
                            min="0"
                            :rules="[
                              v => v >= 0 || '數量不能為負數'
                            ]"
                            hide-details="auto"
                            @update:model-value="calculateDifference"
                          />
                        </td>
                        <td>{{ item.afterQuantity - item.beforeQuantity }}</td>
                      </tr>
                    </tbody>
                    <tfoot>
                      <tr>
                        <td
                          colspan="3"
                          class="text-right font-weight-bold"
                        >
                          合計增減
                        </td>
                        <td>{{ totalQuantityChange }}</td>
                      </tr>
                    </tfoot>
                  </v-table>
                </div>
              </v-sheet>
            </v-card-text>
          </v-card> -->

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
                        {{ localFormData.facilityLocation }}
                      </td>
                      <td class="font-weight-medium text-center">
                        設施地號
                      </td>
                      <td>
                        {{ localFormData.facilityNumber }}
                      </td>
                    </tr>
                    <tr>
                      <td class="font-weight-medium text-center">
                        設施面積
                      </td>
                      <td>
                        {{ localFormData.facilityAreaHa }}公頃
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
                      :items="testResultOptions.filter((option: any) => ['original', 'adjusted', 'improvement'].includes(option.value))"
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
                      :items="testResultOptions.filter((option: any) => ['original', 'adjusted', 'cancel'].includes(option.value))"
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
  </div>
</template>

<script setup lang="ts">
import { useGrantsStore } from '@/stores/grants';

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
const emit = defineEmits(['update:formData', 'validated', 'go-back']);

// Access the grants store
const grantsStore = useGrantsStore();

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

// 動態測試結果選項 - 根據複驗狀態顯示不同選項
const dynamicTestResultOptions = computed(() => {
  if (localFormData.isReinspection) {
    // 複驗狀態：顯示 original, adjusted, cancel
    return testResultOptions.value.filter((option: any) =>
      ['original', 'adjusted', 'cancel'].includes(option.value)
    );
  } else {
    // 非複驗狀態：顯示 original, adjusted, improvement
    return testResultOptions.value.filter((option: any) =>
      ['original', 'adjusted', 'improvement'].includes(option.value)
    );
  }
});

// 追蹤用戶是否手動修改過結果說明
const isManuallyEditedDescription = ref(false);

// 追蹤是否正在自動同步結果說明（避免誤判為手動編輯）
const isAutoSyncingDescription = ref(false);

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

// 變更設計項目
const designChangeItems = reactive([
  { name: '主管', beforeQuantity: 2, afterQuantity: 1 },
  { name: '馬達+抽水機', beforeQuantity: 1, afterQuantity: 0 },
  { name: '單口噴頭-塑鋼', beforeQuantity: 0, afterQuantity: 10 }
]);

// 計算變更總量
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

// 初始化數據
onMounted(() => {
  console.log('step2 data:', localFormData);
  console.log('facilityArea from step2:', localFormData.facilityAreaHa);
  console.log('landAreaHa from step2:', localFormData.landAreaHa);
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
  if (!localFormData.address) {
    if (grantsStore.formData[6]?.applicantAddress) {
      localFormData.address = grantsStore.formData[6].applicantAddress;
    } else {
      const step1Data = grantsStore.formData[1];
      if (step1Data) {
        const county = step1Data.county || '';
        const town = step1Data.town || '';
        const village = step1Data.village || '';
        const address = step1Data.address || '';

        if (county || town || village || address) {
          localFormData.address = `${county}${town}${village}${address}`;
        }
      }
    }
  }

  // Get facility info from previous steps
  if (!localFormData.facilityLocation) {
    if (grantsStore.formData[6]?.facilityLocation) {
      localFormData.facilityLocation = grantsStore.formData[6].facilityLocation;
    } else if (grantsStore.formData[2]) {
      const step2Data = grantsStore.formData[2];
      const county = step2Data.addressCounty || '';
      const town = step2Data.addressTown || '';
      const village = step2Data.addressVillage || '';

      if (county || town || village) {
        localFormData.facilityLocation = `${county}${town}${village}`;
      }
    }
  }

  if (!localFormData.facilityNumber) {
    if (grantsStore.formData[6]?.facilityNumber) {
      localFormData.facilityNumber = grantsStore.formData[6].facilityNumber;
    } else if (grantsStore.formData[2]?.landNumber) {
      localFormData.facilityNumber = grantsStore.formData[2].landNumber;
    }
  }

  if (!localFormData.facilityAreaHa) {
    if (grantsStore.formData[6]?.facilityAreaHa) {
      localFormData.facilityAreaHa = grantsStore.formData[6].facilityAreaHa;
    } else if (grantsStore.formData[2]?.landAreaHa) {
      localFormData.facilityAreaHa = grantsStore.formData[2].facilityAreaHa;
    }
  }

  if (!localFormData.facilityType) {
    if (grantsStore.formData[6]?.facilityType) {
      localFormData.facilityType = grantsStore.formData[6].facilityType;
    } else {
      // Try to construct from step4 data
      const step4Data = grantsStore.formData[4];
      if (step4Data) {
        const installationType = step4Data.installationType || '';
        const irrigationType = step4Data.irrigationType || '';

        if (installationType || irrigationType) {
          localFormData.facilityType = `${installationType}${irrigationType}系統`;
        }
      }
    }
  }

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
    if (grantsStore.formData[6]?.totalBudget) {
      localFormData.originalPayment = grantsStore.formData[6].totalBudget;
    } else {
      // localFormData.originalPayment = '13,378';
    }

    localFormData.actualPayment = localFormData.originalPayment;
  }

  // Set sample description if needed
  if (!localFormData.testResultDescription && localFormData.testResult === 'original') {
    // localFormData.testResultDescription = '工程完工符合規範，依核定補助款發放。';
  }

  // Set sample photo previews if none exist
  if (!localFormData.beforePhotoPreview) {
    localFormData.beforePhotoPreview = 'https://via.placeholder.com/400x300?text=施工前照片示例';
  }

  if (!localFormData.afterPhotoPreview) {
    localFormData.afterPhotoPreview = 'https://via.placeholder.com/400x300?text=竣工照片示例';
  }

  // Initial update to parent
  updateFormData();
});

// 監聽測試結果變化
watch(() => localFormData.isReinspection ? localFormData.reinspectionResult : localFormData.testResult, (newValue, oldValue) => {
  // 只有當測試結果真正變化時才重置手動編輯標記
  if (newValue !== oldValue) {
    isManuallyEditedDescription.value = false;
  }

  console.log('測試結果變化:', newValue);
  
  if (newValue === 'original') {
    // 如果是 "依核定補助款發放"，則自動設置相關金額
    // 確保每次都重新設置原補助款金額
    if (grantsStore.formData[6]?.totalBudget) {
      localFormData.originalPayment = grantsStore.formData[6].totalBudget;
    } else if (!localFormData.originalPayment) {
      // 如果沒有總預算，設置一個預設值
      localFormData.originalPayment = '0';
    }
    // 原補助款發放，實際發放等於原補助款
    localFormData.actualPayment = localFormData.originalPayment;
    localFormData.increasedDecreasedAmount = '';
    console.log('設置 original 金額:', {
      originalPayment: localFormData.originalPayment,
      actualPayment: localFormData.actualPayment
    });
  } else if (newValue === 'adjusted') {
    // 如果是 "依核定補助款增減列"，則設置金額欄位
    if (grantsStore.formData[6]?.totalBudget) {
      localFormData.originalPayment = grantsStore.formData[6].totalBudget;
    } else if (!localFormData.originalPayment) {
      localFormData.originalPayment = '0';
    }
    
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
  } else {
    // 即使手動編輯過，也要更新其他欄位
    updateFormData();
  }
});

// 監聽原金額與增減列變化，重新計算實際發放金額
watch([() => localFormData.originalPayment, () => localFormData.increasedDecreasedAmount], () => {
  const currentResult = localFormData.isReinspection ? localFormData.reinspectionResult : localFormData.testResult;
  
  console.log('金額變化 watch 觸發:', {
    currentResult,
    originalPayment: localFormData.originalPayment,
    increasedDecreasedAmount: localFormData.increasedDecreasedAmount
  });

  if (currentResult === 'adjusted' && localFormData.originalPayment && localFormData.increasedDecreasedAmount) {
    try {
      const original = parseFloat(localFormData.originalPayment.replace(/,/g, ''));
      const adjustment = parseFloat(localFormData.increasedDecreasedAmount.replace(/,/g, ''));
      if (!isNaN(original) && !isNaN(adjustment)) {
        const actual = original + adjustment;
        localFormData.actualPayment = actual.toLocaleString();
        console.log('重新計算 adjusted 實際發放金額:', localFormData.actualPayment);
      }
    } catch (e) {
      console.error('計算實際發放金額時出錯', e);
    }
  } else if (currentResult === 'original' && localFormData.originalPayment) {
    // 如果是 original 狀態，實際發放金額等於原補助款
    localFormData.actualPayment = localFormData.originalPayment;
    console.log('設置 original 實際發放金額:', localFormData.actualPayment);
  }

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
          JSON.stringify(newVal[key]) !== JSON.stringify(localFormData[key])) {
        // 如果正在自動同步結果說明，跳過 testResultDescription 的更新
        if (key === 'testResultDescription' && isAutoSyncingDescription.value) {
          return;
        }
        // 如果用戶已經手動編輯過結果說明，也跳過自動覆蓋
        if (key === 'testResultDescription' && isManuallyEditedDescription.value) {
          return;
        }
        localFormData[key] = newVal[key];
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

// 組件卸載時清理資源
onUnmounted(() => {
  cleanupPreviews();
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

/* 必填欄位紅色星號樣式 */
.required-asterisk {
  color: #ff0000 !important;
  font-weight: bold;
  margin-left: 2px;
}
</style>
