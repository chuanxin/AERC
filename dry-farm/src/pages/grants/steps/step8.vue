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
        <!-- 文件上傳說明提示 -->
        <v-alert
          type="info"
          variant="tonal"
          class="mb-4"
          prominent
          border="start"
        >
          <template #prepend>
            <v-icon size="large">
              mdi-upload-multiple
            </v-icon>
          </template>
          <div class="text-h6 mb-2">
            文件上傳說明
          </div>
          <div class="text-body-1">
            <p class="mb-2">
              <strong>請注意：</strong>案件需要上傳以下所有類別的文件才能完成申請程序。
            </p>
            <ul class="ml-4">
              <li>申請資料：申請檔案</li>
              <li>土地資料：土地登記謄本、地籍圖謄本、租賃同意書、土地施設同意書</li>
              <li>其他資料：現勘紀錄表、委託規劃書、接受補助切結書、竣工報驗書、驗收報告書、領款收據、設計圖</li>
            </ul>
            <p class="mt-2 mb-0">
              <v-icon
                size="small"
                class="me-1"
              >
                mdi-information
              </v-icon>
              支援格式：PDF、JPG、PNG（設計圖另支援 DWG、DXF）
            </p>
          </div>
        </v-alert>

        <v-form
          ref="form"
          v-model="localValid"
          @submit.prevent
        >
          <!-- 申請資料區域 -->
          <v-card
            class="mb-4"
            variant="outlined"
          >
            <v-card-title class="bg-light-blue-lighten-4 d-flex align-center py-2 px-4">
              <v-icon
                class="me-2"
                size="small"
              >
                mdi-file-document
              </v-icon>
              <span class="text-subtitle-1 font-weight-medium"><span class="required-asterisk">*</span>申請資料</span>
            </v-card-title>

            <v-card-text class="pa-4">
              <v-sheet
                class="pa-3 rounded"
                color="grey-lighten-5"
              >
                <v-list class="bg-transparent">
                  <v-list-item
                    title="申請檔案"
                    subtitle="請上傳申請相關檔案 (PDF, JPG, PNG)"
                    class="mb-2"
                  >
                    <template #prepend>
                      <v-avatar :color="localFormData.uploadStatus.applicationFile ? 'success' : 'grey-lighten-1'">
                        <v-icon color="white">
                          {{ localFormData.uploadStatus.applicationFile ? 'mdi-check' : 'mdi-file-document' }}
                        </v-icon>
                      </v-avatar>
                    </template>

                    <template #append>
                      <v-file-input
                        v-model="localFormData.applicationFile"
                        variant="plain"
                        density="compact"
                        accept=".pdf,.jpg,.jpeg,.png"
                        hide-details
                        class="file-input-inline"
                        @update:model-value="handleFileChange('applicationFile')"
                      >
                        <template #prepend-inner>
                          <v-btn
                            :color="localFormData.uploadStatus.applicationFile ? 'success' : 'grey-lighten-1'"
                            :icon="localFormData.uploadStatus.applicationFile ? 'mdi-check' : 'mdi-upload'"
                            variant="text"
                            size="small"
                          />
                        </template>
                      </v-file-input>
                    </template>
                  </v-list-item>

                  <!-- 預覽區域 -->
                  <div
                    v-if="localFormData.applicationFilePreview"
                    class="mt-2 mb-4"
                  >
                    <v-img
                      :src="localFormData.applicationFilePreview"
                      max-height="200"
                      contain
                      class="bg-grey-lighten-3 rounded"
                    />
                  </div>
                </v-list>
              </v-sheet>
            </v-card-text>
          </v-card>

          <!-- 土地資料區域 -->
          <v-card
            class="mb-4"
            variant="outlined"
          >
            <v-card-title class="bg-light-blue-lighten-4 d-flex align-center py-2 px-4">
              <v-icon
                class="me-2"
                size="small"
              >
                mdi-map
              </v-icon>
              <span class="text-subtitle-1 font-weight-medium"><span class="required-asterisk">*</span>土地資料</span>
            </v-card-title>

            <v-card-text class="pa-4">
              <v-sheet
                class="pa-3 rounded"
                color="grey-lighten-5"
              >
                <v-list class="bg-transparent">
                  <v-list-item
                    title="土地登記謄本"
                    subtitle="請上傳土地登記謄本 (PDF, JPG, PNG)"
                    class="mb-2"
                  >
                    <template #prepend>
                      <v-avatar :color="localFormData.uploadStatus.landReg ? 'success' : 'grey-lighten-1'">
                        <v-icon color="white">
                          {{ localFormData.uploadStatus.landReg ? 'mdi-check' : 'mdi-file-document' }}
                        </v-icon>
                      </v-avatar>
                    </template>

                    <template #append>
                      <v-file-input
                        v-model="localFormData.landRegistration"
                        variant="plain"
                        density="compact"
                        accept=".pdf,.jpg,.jpeg,.png"
                        hide-details
                        class="file-input-inline"
                        @update:model-value="handleFileChange('landReg')"
                      >
                        <template #prepend-inner>
                          <v-btn
                            :color="localFormData.uploadStatus.landReg ? 'success' : 'grey-lighten-1'"
                            :icon="localFormData.uploadStatus.landReg ? 'mdi-check' : 'mdi-upload'"
                            variant="text"
                            size="small"
                          />
                        </template>
                      </v-file-input>
                    </template>
                  </v-list-item>

                  <div
                    v-if="localFormData.landRegistrationPreview"
                    class="mt-2 mb-4"
                  >
                    <v-img
                      :src="localFormData.landRegistrationPreview"
                      max-height="200"
                      contain
                      class="bg-grey-lighten-3 rounded"
                    />
                  </div>

                  <v-list-item
                    title="地籍圖謄本"
                    subtitle="請上傳地籍圖謄本 (PDF, JPG, PNG)"
                    class="mb-2"
                  >
                    <template #prepend>
                      <v-avatar :color="localFormData.uploadStatus.landMap ? 'success' : 'grey-lighten-1'">
                        <v-icon color="white">
                          {{ localFormData.uploadStatus.landMap ? 'mdi-check' : 'mdi-map' }}
                        </v-icon>
                      </v-avatar>
                    </template>

                    <template #append>
                      <v-file-input
                        v-model="localFormData.landMap"
                        variant="plain"
                        density="compact"
                        accept=".pdf,.jpg,.jpeg,.png"
                        hide-details
                        class="file-input-inline"
                        @update:model-value="handleFileChange('landMap')"
                      >
                        <template #prepend-inner>
                          <v-btn
                            :color="localFormData.uploadStatus.landMap ? 'success' : 'grey-lighten-1'"
                            :icon="localFormData.uploadStatus.landMap ? 'mdi-check' : 'mdi-upload'"
                            variant="text"
                            size="small"
                          />
                        </template>
                      </v-file-input>
                    </template>
                  </v-list-item>

                  <div
                    v-if="localFormData.landMapPreview"
                    class="mt-2 mb-4"
                  >
                    <v-img
                      :src="localFormData.landMapPreview"
                      max-height="200"
                      contain
                      class="bg-grey-lighten-3 rounded"
                    />
                  </div>

                  <v-list-item
                    title="租賃同意書"
                    subtitle="請上傳租賃同意書 (PDF, JPG, PNG)"
                    class="mb-2"
                  >
                    <template #prepend>
                      <v-avatar :color="localFormData.uploadStatus.lease ? 'success' : 'grey-lighten-1'">
                        <v-icon color="white">
                          {{ localFormData.uploadStatus.lease ? 'mdi-check' : 'mdi-file-document-outline' }}
                        </v-icon>
                      </v-avatar>
                    </template>

                    <template #append>
                      <v-file-input
                        v-model="localFormData.leaseAgreement"
                        variant="plain"
                        density="compact"
                        accept=".pdf,.jpg,.jpeg,.png"
                        hide-details
                        class="file-input-inline"
                        @update:model-value="handleFileChange('lease')"
                      >
                        <template #prepend-inner>
                          <v-btn
                            :color="localFormData.uploadStatus.lease ? 'success' : 'grey-lighten-1'"
                            :icon="localFormData.uploadStatus.lease ? 'mdi-check' : 'mdi-upload'"
                            variant="text"
                            size="small"
                          />
                        </template>
                      </v-file-input>
                    </template>
                  </v-list-item>

                  <div
                    v-if="localFormData.leaseAgreementPreview"
                    class="mt-2 mb-4"
                  >
                    <v-img
                      :src="localFormData.leaseAgreementPreview"
                      max-height="200"
                      contain
                      class="bg-grey-lighten-3 rounded"
                    />
                  </div>

                  <v-list-item
                    title="土地施設同意書"
                    subtitle="請上傳土地施設同意書 (PDF, JPG, PNG)"
                    class="mb-2"
                  >
                    <template #prepend>
                      <v-avatar :color="localFormData.uploadStatus.landUse ? 'success' : 'grey-lighten-1'">
                        <v-icon color="white">
                          {{ localFormData.uploadStatus.landUse ? 'mdi-check' : 'mdi-file-document-outline' }}
                        </v-icon>
                      </v-avatar>
                    </template>

                    <template #append>
                      <v-file-input
                        v-model="localFormData.landUseConsent"
                        variant="plain"
                        density="compact"
                        accept=".pdf,.jpg,.jpeg,.png"
                        hide-details
                        class="file-input-inline"
                        @update:model-value="handleFileChange('landUse')"
                      >
                        <template #prepend-inner>
                          <v-btn
                            :color="localFormData.uploadStatus.landUse ? 'success' : 'grey-lighten-1'"
                            :icon="localFormData.uploadStatus.landUse ? 'mdi-check' : 'mdi-upload'"
                            variant="text"
                            size="small"
                          />
                        </template>
                      </v-file-input>
                    </template>
                  </v-list-item>

                  <div
                    v-if="localFormData.landUseConsentPreview"
                    class="mt-2 mb-4"
                  >
                    <v-img
                      :src="localFormData.landUseConsentPreview"
                      max-height="200"
                      contain
                      class="bg-grey-lighten-3 rounded"
                    />
                  </div>
                </v-list>
              </v-sheet>
            </v-card-text>
          </v-card>

          <!-- 其他資料區域 -->
          <v-card variant="outlined">
            <v-card-title class="bg-light-blue-lighten-4 d-flex align-center py-2 px-4">
              <v-icon
                class="me-2"
                size="small"
              >
                mdi-file-multiple
              </v-icon>
              <span class="text-subtitle-1 font-weight-medium"><span class="required-asterisk">*</span>其他資料</span>
            </v-card-title>

            <v-card-text class="pa-4">
              <v-sheet
                class="pa-3 rounded"
                color="grey-lighten-5"
              >
                <v-list class="bg-transparent">
                  <v-list-item
                    title="現勘紀錄表"
                    subtitle="請上傳現勘紀錄表 (PDF, JPG, PNG)"
                    class="mb-2"
                  >
                    <template #prepend>
                      <v-avatar :color="localFormData.uploadStatus.inspection ? 'success' : 'grey-lighten-1'">
                        <v-icon color="white">
                          {{ localFormData.uploadStatus.inspection ? 'mdi-check' : 'mdi-clipboard-check' }}
                        </v-icon>
                      </v-avatar>
                    </template>

                    <template #append>
                      <v-file-input
                        v-model="localFormData.inspectionRecord"
                        variant="plain"
                        density="compact"
                        accept=".pdf,.jpg,.jpeg,.png"
                        hide-details
                        class="file-input-inline"
                        @update:model-value="handleFileChange('inspection')"
                      >
                        <template #prepend-inner>
                          <v-btn
                            :color="localFormData.uploadStatus.inspection ? 'success' : 'grey-lighten-1'"
                            :icon="localFormData.uploadStatus.inspection ? 'mdi-check' : 'mdi-upload'"
                            variant="text"
                            size="small"
                          />
                        </template>
                      </v-file-input>
                    </template>
                  </v-list-item>

                  <div
                    v-if="localFormData.inspectionRecordPreview"
                    class="mt-2 mb-4"
                  >
                    <v-img
                      :src="localFormData.inspectionRecordPreview"
                      max-height="200"
                      contain
                      class="bg-grey-lighten-3 rounded"
                    />
                  </div>

                  <v-list-item
                    title="委託規劃書"
                    subtitle="請上傳委託規劃書 (PDF, JPG, PNG)"
                    class="mb-2"
                  >
                    <template #prepend>
                      <v-avatar :color="localFormData.uploadStatus.planning ? 'success' : 'grey-lighten-1'">
                        <v-icon color="white">
                          {{ localFormData.uploadStatus.planning ? 'mdi-check' : 'mdi-file-document-outline' }}
                        </v-icon>
                      </v-avatar>
                    </template>

                    <template #append>
                      <v-file-input
                        v-model="localFormData.planningDoc"
                        variant="plain"
                        density="compact"
                        accept=".pdf,.jpg,.jpeg,.png"
                        hide-details
                        class="file-input-inline"
                        @update:model-value="handleFileChange('planning')"
                      >
                        <template #prepend-inner>
                          <v-btn
                            :color="localFormData.uploadStatus.planning ? 'success' : 'grey-lighten-1'"
                            :icon="localFormData.uploadStatus.planning ? 'mdi-check' : 'mdi-upload'"
                            variant="text"
                            size="small"
                          />
                        </template>
                      </v-file-input>
                    </template>
                  </v-list-item>

                  <div
                    v-if="localFormData.planningDocPreview"
                    class="mt-2 mb-4"
                  >
                    <v-img
                      :src="localFormData.planningDocPreview"
                      max-height="200"
                      contain
                      class="bg-grey-lighten-3 rounded"
                    />
                  </div>

                  <v-list-item
                    title="接受補助切結書"
                    subtitle="請上傳接受補助切結書 (PDF, JPG, PNG)"
                    class="mb-2"
                  >
                    <template #prepend>
                      <v-avatar :color="localFormData.uploadStatus.subsidy ? 'success' : 'grey-lighten-1'">
                        <v-icon color="white">
                          {{ localFormData.uploadStatus.subsidy ? 'mdi-check' : 'mdi-file-document-outline' }}
                        </v-icon>
                      </v-avatar>
                    </template>

                    <template #append>
                      <v-file-input
                        v-model="localFormData.subsidy"
                        variant="plain"
                        density="compact"
                        accept=".pdf,.jpg,.jpeg,.png"
                        hide-details
                        class="file-input-inline"
                        @update:model-value="handleFileChange('subsidy')"
                      >
                        <template #prepend-inner>
                          <v-btn
                            :color="localFormData.uploadStatus.subsidy ? 'success' : 'grey-lighten-1'"
                            :icon="localFormData.uploadStatus.subsidy ? 'mdi-check' : 'mdi-upload'"
                            variant="text"
                            size="small"
                          />
                        </template>
                      </v-file-input>
                    </template>
                  </v-list-item>

                  <div
                    v-if="localFormData.subsidyPreview"
                    class="mt-2 mb-4"
                  >
                    <v-img
                      :src="localFormData.subsidyPreview"
                      max-height="200"
                      contain
                      class="bg-grey-lighten-3 rounded"
                    />
                  </div>

                  <v-list-item
                    title="竣工報驗書"
                    subtitle="請上傳竣工報驗書 (PDF, JPG, PNG)"
                    class="mb-2"
                  >
                    <template #prepend>
                      <v-avatar :color="localFormData.uploadStatus.workInspection ? 'success' : 'grey-lighten-1'">
                        <v-icon color="white">
                          {{ localFormData.uploadStatus.workInspection ? 'mdi-check' : 'mdi-file-document-outline' }}
                        </v-icon>
                      </v-avatar>
                    </template>

                    <template #append>
                      <v-file-input
                        v-model="localFormData.workInspection"
                        variant="plain"
                        density="compact"
                        accept=".pdf,.jpg,.jpeg,.png"
                        hide-details
                        class="file-input-inline"
                        @update:model-value="handleFileChange('workInspection')"
                      >
                        <template #prepend-inner>
                          <v-btn
                            :color="localFormData.uploadStatus.workInspection ? 'success' : 'grey-lighten-1'"
                            :icon="localFormData.uploadStatus.workInspection ? 'mdi-check' : 'mdi-upload'"
                            variant="text"
                            size="small"
                          />
                        </template>
                      </v-file-input>
                    </template>
                  </v-list-item>

                  <div
                    v-if="localFormData.workInspectionPreview"
                    class="mt-2 mb-4"
                  >
                    <v-img
                      :src="localFormData.workInspectionPreview"
                      max-height="200"
                      contain
                      class="bg-grey-lighten-3 rounded"
                    />
                  </div>

                  <v-list-item
                    title="驗收報告書"
                    subtitle="請上傳驗收報告書 (PDF, JPG, PNG)"
                    class="mb-2"
                  >
                    <template #prepend>
                      <v-avatar :color="localFormData.uploadStatus.inspectionReport ? 'success' : 'grey-lighten-1'">
                        <v-icon color="white">
                          {{ localFormData.uploadStatus.inspectionReport ? 'mdi-check' : 'mdi-file-document-outline' }}
                        </v-icon>
                      </v-avatar>
                    </template>

                    <template #append>
                      <v-file-input
                        v-model="localFormData.inspectionReport"
                        variant="plain"
                        density="compact"
                        accept=".pdf,.jpg,.jpeg,.png"
                        hide-details
                        class="file-input-inline"
                        @update:model-value="handleFileChange('inspectionReport')"
                      >
                        <template #prepend-inner>
                          <v-btn
                            :color="localFormData.uploadStatus.inspectionReport ? 'success' : 'grey-lighten-1'"
                            :icon="localFormData.uploadStatus.inspectionReport ? 'mdi-check' : 'mdi-upload'"
                            variant="text"
                            size="small"
                          />
                        </template>
                      </v-file-input>
                    </template>
                  </v-list-item>

                  <div
                    v-if="localFormData.inspectionReportPreview"
                    class="mt-2 mb-4"
                  >
                    <v-img
                      :src="localFormData.inspectionReportPreview"
                      max-height="200"
                      contain
                      class="bg-grey-lighten-3 rounded"
                    />
                  </div>

                  <v-list-item
                    title="領款收據"
                    subtitle="請上傳領款收據 (PDF, JPG, PNG)"
                    class="mb-2"
                  >
                    <template #prepend>
                      <v-avatar :color="localFormData.uploadStatus.paymentReceipt ? 'success' : 'grey-lighten-1'">
                        <v-icon color="white">
                          {{ localFormData.uploadStatus.paymentReceipt ? 'mdi-check' : 'mdi-receipt' }}
                        </v-icon>
                      </v-avatar>
                    </template>

                    <template #append>
                      <v-file-input
                        v-model="localFormData.paymentReceipt"
                        variant="plain"
                        density="compact"
                        accept=".pdf,.jpg,.jpeg,.png"
                        hide-details
                        class="file-input-inline"
                        @update:model-value="handleFileChange('paymentReceipt')"
                      >
                        <template #prepend-inner>
                          <v-btn
                            :color="localFormData.uploadStatus.paymentReceipt ? 'success' : 'grey-lighten-1'"
                            :icon="localFormData.uploadStatus.paymentReceipt ? 'mdi-check' : 'mdi-upload'"
                            variant="text"
                            size="small"
                          />
                        </template>
                      </v-file-input>
                    </template>
                  </v-list-item>

                  <div
                    v-if="localFormData.paymentReceiptPreview"
                    class="mt-2 mb-4"
                  >
                    <v-img
                      :src="localFormData.paymentReceiptPreview"
                      max-height="200"
                      contain
                      class="bg-grey-lighten-3 rounded"
                    />
                  </div>

                  <v-list-item
                    title="設計圖"
                    subtitle="請上傳設計圖 (PDF, JPG, PNG, DWG, DXF)"
                    class="mb-2"
                  >
                    <template #prepend>
                      <v-avatar :color="localFormData.uploadStatus.designDrawing ? 'success' : 'grey-lighten-1'">
                        <v-icon color="white">
                          {{ localFormData.uploadStatus.designDrawing ? 'mdi-check' : 'mdi-drawing' }}
                        </v-icon>
                      </v-avatar>
                    </template>

                    <template #append>
                      <v-file-input
                        v-model="localFormData.designDrawing"
                        variant="plain"
                        density="compact"
                        accept=".pdf,.jpg,.jpeg,.png,.dwg,.dxf"
                        hide-details
                        class="file-input-inline"
                        @update:model-value="handleFileChange('designDrawing')"
                      >
                        <template #prepend-inner>
                          <v-btn
                            :color="localFormData.uploadStatus.designDrawing ? 'success' : 'grey-lighten-1'"
                            :icon="localFormData.uploadStatus.designDrawing ? 'mdi-check' : 'mdi-upload'"
                            variant="text"
                            size="small"
                          />
                        </template>
                      </v-file-input>
                    </template>
                  </v-list-item>

                  <div
                    v-if="localFormData.designDrawingPreview"
                    class="mt-2 mb-4"
                  >
                    <v-img
                      :src="localFormData.designDrawingPreview"
                      max-height="200"
                      contain
                      class="bg-grey-lighten-3 rounded"
                    />
                  </div>
                </v-list>
              </v-sheet>
            </v-card-text>
          </v-card>

          <!-- 上傳進度總覽
          <v-card
            variant="outlined"
            class="mt-4"
          >
            <v-card-title class="bg-grey-lighten-4 d-flex align-center py-2 px-4">
              <v-icon
                class="me-2"
                size="small"
              >
                mdi-progress-check
              </v-icon>
              <span class="text-subtitle-1 font-weight-medium">上傳進度總覽</span>
            </v-card-title>

            <v-card-text class="pa-4">
              <v-row>
                <v-col
                  cols="12"
                  md="4"
                >
                  <v-card
                    :color="uploadedFilesCount === 0 ? 'grey-lighten-3' : 'blue-lighten-5'"
                    class="pa-3 text-center"
                    variant="tonal"
                  >
                    <div class="text-h4 font-weight-bold mb-1">
                      {{ uploadedFilesCount }}
                    </div>
                    <div class="text-body-2 text-medium-emphasis">
                      已上傳檔案
                    </div>
                  </v-card>
                </v-col>
                <v-col
                  cols="12"
                  md="4"
                >
                  <v-card
                    :color="totalRequiredFiles === uploadedFilesCount ? 'green-lighten-5' : 'orange-lighten-5'"
                    class="pa-3 text-center"
                    variant="tonal"
                  >
                    <div class="text-h4 font-weight-bold mb-1">
                      {{ totalRequiredFiles }}
                    </div>
                    <div class="text-body-2 text-medium-emphasis">
                      需要檔案總數
                    </div>
                  </v-card>
                </v-col>
                <v-col
                  cols="12"
                  md="4"
                >
                  <v-card
                    :color="isAllFilesUploaded ? 'green-lighten-5' : 'red-lighten-5'"
                    class="pa-3 text-center"
                    variant="tonal"
                  >
                    <v-icon
                      :color="isAllFilesUploaded ? 'success' : 'error'"
                      size="large"
                      class="mb-1"
                    >
                      {{ isAllFilesUploaded ? 'mdi-check-circle' : 'mdi-alert-circle' }}
                    </v-icon>
                    <div class="text-body-2 text-medium-emphasis">
                      {{ isAllFilesUploaded ? '上傳完成' : '未完成' }}
                    </div>
                  </v-card>
                </v-col>
              </v-row>

              <v-progress-linear
                :model-value="uploadProgress"
                :color="isAllFilesUploaded ? 'success' : 'primary'"
                height="8"
                rounded
                class="mt-4 mb-3"
              />

              <div class="text-center">
                <div class="text-body-1 mb-2">
                  上傳進度：{{ uploadProgress.toFixed(0) }}%
                  ({{ uploadedFilesCount }}/{{ totalRequiredFiles }})
                </div>

                <v-alert
                  v-if="!isAllFilesUploaded"
                  type="warning"
                  variant="tonal"
                  density="compact"
                  class="text-start"
                >
                  <template #prepend>
                    <v-icon>mdi-alert</v-icon>
                  </template>
                  <strong>注意：</strong>您還需要上傳 {{ totalRequiredFiles - uploadedFilesCount }} 個檔案才能完成申請。
                  請確保所有必要文件都已上傳後再進行下一步。
                </v-alert>

                <v-alert
                  v-else
                  type="success"
                  variant="tonal"
                  density="compact"
                  class="text-start"
                >
                  <template #prepend>
                    <v-icon>mdi-check-circle</v-icon>
                  </template>
                  <strong>恭喜！</strong>所有必要文件已上傳完成，您現在可以進行下一步操作。
                </v-alert>
              </div>
            </v-card-text>
          </v-card> -->
        </v-form>
      </v-card-text>
    </v-card>
  </div>
</template>

<script setup lang="ts">
// Props definition
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

// Form validation references
const form = ref(null);
const localValid = ref(true);

// Define upload status interface
interface UploadStatus {
  idFront: boolean;
  idBack: boolean;
  applicationFile: boolean;
  landReg: boolean;
  landMap: boolean;
  lease: boolean;
  landUse: boolean;
  inspection: boolean;
  planning: boolean;
  subsidy: boolean;
  workInspection: boolean;
  inspectionReport: boolean;
  paymentReceipt: boolean;
  designDrawing: boolean;
}

// Define form data interface
interface FormData {
  idCardFront: File | null;
  idCardBack: File | null;
  idCardFrontPreview: string | null;
  idCardBackPreview: string | null;
  applicationFile: File | null;
  applicationFilePreview: string | null;
  landRegistration: File | null;
  landRegistrationPreview: string | null;
  landMap: File | null;
  landMapPreview: string | null;
  leaseAgreement: File | null;
  leaseAgreementPreview: string | null;
  landUseConsent: File | null;
  landUseConsentPreview: string | null;
  inspectionRecord: File | null;
  inspectionRecordPreview: string | null;
  planningDoc: File | null;
  planningDocPreview: string | null;
  subsidy: File | null;
  subsidyPreview: string | null;
  workInspection: File | null;
  workInspectionPreview: string | null;
  inspectionReport: File | null;
  inspectionReportPreview: string | null;
  paymentReceipt: File | null;
  paymentReceiptPreview: string | null;
  designDrawing: File | null;
  designDrawingPreview: string | null;
  uploadStatus: UploadStatus;
  valid: boolean;
}

// 本地表單數據
const localFormData = reactive<FormData>({
  // 申請資料
  idCardFront: null,
  idCardBack: null,
  idCardFrontPreview: null,
  idCardBackPreview: null,
  applicationFile: null,
  applicationFilePreview: null,

  // 土地資料
  landRegistration: null,
  landRegistrationPreview: null,
  landMap: null,
  landMapPreview: null,
  leaseAgreement: null,
  leaseAgreementPreview: null,
  landUseConsent: null,
  landUseConsentPreview: null,

  // 其他資料
  inspectionRecord: null,
  inspectionRecordPreview: null,
  planningDoc: null,
  planningDocPreview: null,
  subsidy: null,
  subsidyPreview: null,
  workInspection: null,
  workInspectionPreview: null,
  inspectionReport: null,
  inspectionReportPreview: null,
  paymentReceipt: null,
  paymentReceiptPreview: null,
  designDrawing: null,
  designDrawingPreview: null,

  // 檔案上傳狀態
  uploadStatus: {
    idFront: false,
    idBack: false,
    applicationFile: false,
    landReg: false,
    landMap: false,
    lease: false,
    landUse: false,
    inspection: false,
    planning: false,
    subsidy: false,
    workInspection: false,
    inspectionReport: false,
    paymentReceipt: false,
    designDrawing: false
  },

  // Always set to true for seamless navigation
  valid: true
});

// 計算屬性：已上傳檔案數量
const uploadedFilesCount = computed(() => {
  return Object.values(localFormData.uploadStatus).filter(status => status).length;
});

// 計算屬性：總檔案數量
const totalRequiredFiles = computed(() => {
  return Object.keys(localFormData.uploadStatus).length;
});

// 計算屬性：是否所有檔案都已上傳
const isAllFilesUploaded = computed(() => {
  return uploadedFilesCount.value === totalRequiredFiles.value;
});

// 計算屬性：上傳進度百分比
const uploadProgress = computed(() => {
  if (totalRequiredFiles.value === 0) return 0;
  return (uploadedFilesCount.value / totalRequiredFiles.value) * 100;
});

// 判斷檔案是否為圖片類型
const isImageFile = (file: File | string | null): boolean => {
  if (!file) return false;

  // Handle string URLs (like placeholders or previously saved images)
  if (typeof file === 'string') return true;

  const imageTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/jpg'];
  return file instanceof File && imageTypes.includes(file.type);
};

// 處理檔案變更並產生預覽（如果是圖片）
const handleFileChange = (type: keyof UploadStatus) => {
  // 更新檔案上傳狀態
  localFormData.uploadStatus[type] = true;

  // 根據不同類型的檔案處理預覽
  switch(type) {
    case 'idFront':
      createPreview(localFormData.idCardFront, 'idCardFrontPreview');
      break;
    case 'idBack':
      createPreview(localFormData.idCardBack, 'idCardBackPreview');
      break;
    case 'applicationFile':
      createPreview(localFormData.applicationFile, 'applicationFilePreview');
      break;
    case 'landReg':
      createPreview(localFormData.landRegistration, 'landRegistrationPreview');
      break;
    case 'landMap':
      createPreview(localFormData.landMap, 'landMapPreview');
      break;
    case 'lease':
      createPreview(localFormData.leaseAgreement, 'leaseAgreementPreview');
      break;
    case 'landUse':
      createPreview(localFormData.landUseConsent, 'landUseConsentPreview');
      break;
    case 'inspection':
      createPreview(localFormData.inspectionRecord, 'inspectionRecordPreview');
      break;
    case 'planning':
      createPreview(localFormData.planningDoc, 'planningDocPreview');
      break;
    case 'subsidy':
      createPreview(localFormData.subsidy, 'subsidyPreview');
      break;
    case 'workInspection':
      createPreview(localFormData.workInspection, 'workInspectionPreview');
      break;
    case 'inspectionReport':
      createPreview(localFormData.inspectionReport, 'inspectionReportPreview');
      break;
    case 'paymentReceipt':
      createPreview(localFormData.paymentReceipt, 'paymentReceiptPreview');
      break;
    case 'designDrawing':
      createPreview(localFormData.designDrawing, 'designDrawingPreview');
      break;
  }

  // 觸發驗證更新
  localValid.value = isAllFilesUploaded.value;
  updateFormData();
};

// Helper function to create previews
const createPreview = (file: File | null, previewKey: keyof FormData) => {
  if (isImageFile(file)) {
    // Clean up existing preview if it's a blob URL
    const currentPreview = localFormData[previewKey];
    if (currentPreview &&
        typeof currentPreview === 'string' &&
        currentPreview.startsWith('blob:')) {
      URL.revokeObjectURL(currentPreview);
    }

    // Create new preview if file is a File object
    if (file instanceof File) {
      (localFormData[previewKey] as string | null) = URL.createObjectURL(file);
    }
  }
};

// 更新父組件數據
const updateFormData = () => {
  emit('update:formData', {
    ...props.formData,
    ...localFormData,
    valid: isAllFilesUploaded.value // 根據檔案上傳完成狀態設定有效性
  });
};

// 清理所有預覽資源的函數
const cleanupAllPreviews = () => {
  const previewKeys: (keyof FormData)[] = [
    'idCardFrontPreview', 'idCardBackPreview', 'applicationFilePreview',
    'landRegistrationPreview', 'landMapPreview', 'leaseAgreementPreview',
    'landUseConsentPreview', 'inspectionRecordPreview', 'planningDocPreview',
    'subsidyPreview', 'workInspectionPreview', 'inspectionReportPreview',
    'paymentReceiptPreview', 'designDrawingPreview'
  ];

  previewKeys.forEach(key => {
    const preview = localFormData[key];
    if (preview &&
        typeof preview === 'string' &&
        preview.startsWith('blob:')) {
      URL.revokeObjectURL(preview);
      (localFormData[key] as string | null) = null;
    }
  });
};

// 初始化數據
onMounted(() => {
  console.log("Step 8 mounted, formData:", props.formData);

  // 從父組件接收數據
  if (props.formData) {
    // 設置基本屬性
    (Object.keys(localFormData) as (keyof FormData)[]).forEach(key => {
      if (props.formData[key] !== undefined) {
        if (key === 'uploadStatus') {
          // Handle nested uploadStatus object
          if (props.formData.uploadStatus) {
            (Object.keys(props.formData.uploadStatus) as (keyof UploadStatus)[]).forEach(statusKey => {
              if (props.formData.uploadStatus[statusKey] !== undefined) {
                localFormData.uploadStatus[statusKey] = props.formData.uploadStatus[statusKey];
              }
            });
          }
        } else {
          // Handle normal properties with proper typing
          const typedLocalFormData = localFormData as Record<string, unknown>;
          typedLocalFormData[key] = props.formData[key];
        }
      }
    });
  }

  // Set example data for demonstration purposes
  // if (!localFormData.idCardFrontPreview) {
  //   localFormData.idCardFrontPreview = 'https://via.placeholder.com/400x250?text=身分證正面示例';
  //   localFormData.uploadStatus.idFront = true;
  // }

  // if (!localFormData.idCardBackPreview) {
  //   localFormData.idCardBackPreview = 'https://via.placeholder.com/400x250?text=身分證反面示例';
  //   localFormData.uploadStatus.idBack = true;
  // }

  // if (!localFormData.landRegistrationPreview) {
  //   localFormData.landRegistrationPreview = 'https://via.placeholder.com/400x250?text=土地登記謄本示例';
  //   localFormData.uploadStatus.landReg = true;
  // }

  // if (!localFormData.landMapPreview) {
  //   localFormData.landMapPreview = 'https://via.placeholder.com/400x250?text=地籍圖謄本示例';
  //   localFormData.uploadStatus.landMap = true;
  // }

  // Initial update to parent
  updateFormData();
});

// 監聽父組件數據變化
watch(() => props.formData, (newVal) => {
  if (newVal) {
    // Simple re-copy of new values, skipping complex file objects
    (Object.keys(localFormData) as (keyof FormData)[]).forEach(key => {
      if (key !== 'uploadStatus' && newVal[key] !== undefined &&
          !(newVal[key] instanceof File) && // Skip File objects which can't be deeply compared
          JSON.stringify(newVal[key]) !== JSON.stringify(localFormData[key])) {
        const typedLocalFormData = localFormData as Record<string, unknown>;
        typedLocalFormData[key] = newVal[key];
      }
    });

    // Handle uploadStatus specifically
    if (newVal.uploadStatus) {
      (Object.keys(newVal.uploadStatus) as (keyof UploadStatus)[]).forEach(statusKey => {
        if (newVal.uploadStatus[statusKey] !== undefined &&
            newVal.uploadStatus[statusKey] !== localFormData.uploadStatus[statusKey]) {
          localFormData.uploadStatus[statusKey] = newVal.uploadStatus[statusKey];
        }
      });
    }
  }
}, { deep: true });

// Watch local form validation status
watch(localValid, (newVal) => {
  if (props.formData?.valid !== newVal) {
    updateFormData();
  }
});

// 監聽上傳狀態變化，自動更新表單有效性
watch(isAllFilesUploaded, (newVal) => {
  localValid.value = newVal;
  localFormData.valid = newVal;
}, { immediate: true });

// Clean up on component unmount
onUnmounted(() => {
  cleanupAllPreviews();
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

.text-red {
  color: red;
}

/* 必填欄位紅色星號樣式 */
.required-asterisk {
  color: #ff0000 !important;
  font-weight: bold;
  margin-left: 2px;
}
</style>
