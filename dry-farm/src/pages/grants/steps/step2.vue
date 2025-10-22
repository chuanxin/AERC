<template>
  <div
    ref="stepContent"
    class="step-content"
  >
    <!-- Land info dialog -->
    <v-dialog
      v-model="landInfoDialog"
      max-width="700px"
    >
      <v-card rounded="lg">
        <v-card-title
          class="text-subtitle-1 font-weight-bold pa-4 d-flex justify-start"
          style="color: #2d8c8f; background-color: #e3f4f4;"
        >
          <v-icon
            color="#3ea0a3"
            class="me-2"
            size="small"
          >
            mdi-map-marker
          </v-icon>
          <span>查詢地號</span>
          <v-spacer />
          <v-btn
            class="text-none"
            :color="featureInfoVisible ? '#3ea0a3' : 'medium-emphasis'"
            :variant="featureInfoVisible ? 'flat' : 'outlined'"
            density="compact"
            rounded
            :prepend-icon="featureInfoVisible ? 'mdi-information' : 'mdi-information-variant'"
            @click="toggleFeatureInfo"
          >
            {{ featureInfoVisible ? '隱藏地號資訊' : '顯示地號資訊' }}
          </v-btn>
        </v-card-title>

        <v-card-text class="pa-4">
          <div
            class="mb-4"
            style="position: relative;"
          >
            <div
              id="step2-land-info-map"
              ref="mapElement"
              class="rounded border"
              style="height: 300px;"
            />
            <!-- 🆕 無地段圖資提示 overlay（移到地圖外部避免 DOM 衝突） -->
            <v-overlay
              v-model="noSectionDataOverlay"
              contained
              scrim="rgba(0, 0, 0, 0.5)"
              persistent
              class="align-center justify-center"
            >
              <v-card
                max-width="400"
                class="pa-4"
                rounded="lg"
                elevation="8"
              >
                <v-card-text class="text-center">
                  <v-icon
                    size="64"
                    color="warning"
                    class="mb-4"
                  >
                    mdi-map-marker-off
                  </v-icon>
                  <div class="text-h6 mb-2">
                    查無此地段圖資
                  </div>
                  <div class="text-body-2 text-grey-darken-1 mb-4">
                    目前系統中沒有此地段的地號圖資資料
                  </div>
                  <v-btn
                    color="#3ea0a3"
                    variant="flat"
                    rounded="lg"
                    @click="closeNoSectionOverlay"
                  >
                    確定
                  </v-btn>
                </v-card-text>
              </v-card>
            </v-overlay>
            <!-- Feature info popup -->
            <v-card
              v-if="featureInfoVisible"
              class="feature-info-card pa-0"
              elevation="4"
            >
              <v-card-title class="text-body-1 py-1 px-2">
                地號資訊
              </v-card-title>
              <v-divider />
              <v-card-text class="px-2 py-1">
                <div v-if="selectedFeatureInfo.Land_no">
                  <strong>地號:</strong> {{ selectedFeatureInfo.Land_no }}
                </div>
                <div v-if="selectedFeatureInfo.section">
                  <strong>地段:</strong> {{ selectedFeatureInfo.Sec_cns }}
                </div>
                <div v-if="selectedFeatureInfo.area">
                  <strong>面積:</strong> {{ selectedFeatureInfo.area }} 平方公尺
                  <div class="text-caption text-grey-darken-1">
                    來源: {{ getAreaSourceDisplay(selectedFeatureInfo) }}
                  </div>
                </div>
                <div class="mt-2">
                  <v-btn
                    density="compact"
                    color="#3ea0a3"
                    variant="outlined"
                    rounded="lg"
                    size="small"
                    @click="useSelectedFeature"
                  >
                    使用此地號
                  </v-btn>
                  <v-btn
                    density="compact"
                    variant="text"
                    size="small"
                    @click="hideFeatureInfo"
                  >
                    關閉
                  </v-btn>
                </div>
              </v-card-text>
            </v-card>
          </div>

          <!-- 🆕 查無地號提示 -->
          <v-alert
            v-if="landParcelNotFoundAlert"
            type="warning"
            variant="tonal"
            class="mb-4"
            closable
            @click:close="landParcelNotFoundAlert = false"
          >
            <div class="d-flex align-center">
              <div>
                <div class="font-weight-medium">查無此地號</div>
                <div class="text-body-2">
                  {{ landParcelNotFoundMessage }}
                </div>
              </div>
            </div>
          </v-alert>

          <v-table
            density="comfortable"
            class="border rounded mb-4"
          >
            <tbody>
              <tr>
                <!-- <td
                  class="bg-grey-lighten-4 font-weight-medium"
                  width="15%"
                >
                  補助資訊
                </td>
                <td>{{ landInfo.subsidyInfo }}</td> -->
                <td
                  class="bg-grey-lighten-4 font-weight-medium"
                  width="15%"
                >
                  縣市
                </td>
                <td>{{ displayCountyName }}</td>
                <td class="bg-grey-lighten-4 font-weight-medium">
                  水利小組
                </td>
                <td>
                  <!-- 詳細事業區層級資訊 -->
                  <div
                    v-if="landInfo.irrigationDistrictInfo && landInfo.irrigationDistrictInfo.length > 0"
                    class="d-flex flex-column gap-1"
                  >
                    <div
                      v-for="boundary in landInfo.irrigationDistrictInfo.slice(0, 2)"
                      :key="boundary.gid"
                      class="text-body-2"
                    >
                      <span class="font-weight-bold text-teal">{{ boundary.ia_name || '未知' }}</span>
                      <template v-if="boundary.mng_name">
                        <span class="mx-1 text-grey-darken-1">></span>
                        <span>{{ boundary.mng_name }}</span>
                      </template>
                      <span class="mx-1 text-grey-darken-1">></span>
                      <span>{{ boundary.stn_name || '未知工作站' }}</span>
                      <span
                        v-if="boundary.grp_name"
                        class="mx-1 text-grey-darken-1"
                      >></span>
                      <span
                        v-if="boundary.grp_name"
                        class="text-blue-grey-darken-1"
                      >{{ boundary.grp_name }}</span>
                    </div>

                    <div
                      v-if="landInfo.irrigationDistrictInfo.length > 2"
                      class="text-caption text-grey-darken-1 mt-1"
                    >
                      另有 {{ landInfo.irrigationDistrictInfo.length - 2 }} 個事業區域
                    </div>
                  </div>

                  <!-- 無事業區域資訊時的顯示 -->
                  <div
                    v-else
                    class="text-grey-darken-1"
                  >
                    查無相關事業區域資訊
                  </div>
                </td>
              </tr>
              <!-- <tr>
                <td class="bg-grey-lighten-4 font-weight-medium">
                  特殊地
                </td>
                <td>{{ landInfo.specialLand ? '是' : '否' }}</td>
              </tr> -->
            </tbody>
          </v-table>
        </v-card-text>
      </v-card>
    </v-dialog>

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
          <!-- 多筆土地資料管理區域 - 僅在非編輯模式時顯示 -->
          <v-card
            v-show="!landManagement.isEditingMode"
            flat
            class="mb-4 pa-4"
            color="#f8f9fa"
            rounded="lg"
          >
            <v-card-title
              class="text-subtitle-1 font-weight-bold pa-0 pb-4 d-flex align-center"
              style="color: #2d8c8f"
            >
              <v-icon
                color="#3ea0a3"
                class="me-2 pb-1"
                size="small"
              >
                mdi-map-legend
              </v-icon>
              <span>土地資料管理</span>
              <v-spacer />
              <!-- 只在有土地資料時顯示新增按鈕 -->
              <v-btn
                v-if="landManagement.lands.length > 0"
                color="#3ea0a3"
                variant="flat"
                rounded="lg"
                size="small"
                @click="addNewLand"
              >
                <v-icon
                  size="small"
                  class="me-1"
                >
                  mdi-plus
                </v-icon>
                新增土地
              </v-btn>
            </v-card-title>

            <!-- 總面積統計 -->
            <v-sheet
              v-if="landManagement.lands.length > 0"
              class="mb-3 pa-3 rounded"
              color="rgba(76, 175, 80, 0.1)"
            >
              <div class="d-flex align-center">
                <v-icon
                  size="small"
                  class="me-2"
                  color="success"
                >
                  mdi-calculator
                </v-icon>
                <span class="text-body-2 font-weight-medium">總施作面積：</span>
                <span class="text-h6 font-weight-bold ms-2 text-success">
                  {{ totalFacilityArea.toLocaleString() }} m²
                </span>
                <span class="text-body-2 ms-2 text-grey-darken-1">
                  ({{ totalFacilityAreaHa }} 公頃)
                </span>
              </div>
            </v-sheet>

            <!-- 土地卡片列表 -->
            <div v-if="landManagement.lands.length > 0">
              <v-row>
                <v-col
                  v-for="(land, index) in landManagement.lands"
                  :key="land.id"
                  cols="12"
                  md="6"
                  lg="4"
                >
                  <v-card
                    class="land-card cursor-pointer"
                    variant="outlined"
                    :color="landManagement.currentEditingLandId === land.id ? '#e3f4f4' : 'white'"
                    @click="editLand(land.id)"
                  >
                    <v-card-text class="pa-3">
                      <div class="d-flex justify-space-between align-start mb-2">
                        <v-chip
                          size="small"
                          color="primary"
                          variant="tonal"
                        >
                          土地 {{ index + 1 }}
                        </v-chip>
                        <v-btn
                          icon
                          size="x-small"
                          color="error"
                          variant="text"
                          @click.stop="deleteLand(land.id)"
                        >
                          <v-icon size="small">
                            mdi-close
                          </v-icon>
                        </v-btn>
                      </div>

                      <div class="land-summary">
                        <div class="text-body-2 mb-1">
                          <v-icon
                            size="small"
                            class="me-1"
                          >
                            mdi-map-marker
                          </v-icon>
                          {{ getLandLocationText(land) }}
                        </div>

                        <div class="text-body-2 mb-1">
                          <v-icon
                            size="small"
                            class="me-1"
                          >
                            mdi-land-plots
                          </v-icon>
                          地號：{{ getLandNumber(land) }}
                        </div>

                        <div class="text-body-2 mb-1">
                          <v-icon
                            size="small"
                            class="me-1"
                          >
                            mdi-ruler-square
                          </v-icon>
                          施作面積：{{ land.facilityArea || '0' }} m²
                        </div>

                        <div
                          v-if="land.crops.length > 0"
                          class="text-body-2"
                        >
                          <v-icon
                            size="small"
                            class="me-1"
                          >
                            mdi-sprout
                          </v-icon>
                          作物：{{ land.crops.map(c => c.name).join(', ') }}
                        </div>
                      </div>
                    </v-card-text>

                    <v-card-actions class="pt-0 pb-3 px-3">
                      <v-btn
                        variant="outlined"
                        color="#3ea0a3"
                        size="small"
                        block
                        @click.stop="editLand(land.id)"
                      >
                        <v-icon
                          size="small"
                          class="me-1"
                        >
                          mdi-pencil
                        </v-icon>
                        編輯
                      </v-btn>
                    </v-card-actions>
                  </v-card>
                </v-col>
              </v-row>
            </div>

            <!-- 空狀態：友善引導設計 -->
            <v-sheet
              v-else
              class="pa-8 text-center rounded"
              color="rgba(62, 160, 163, 0.05)"
            >
              <!-- 情感連結：友善的視覺引導 -->
              <div class="mb-4">
                <v-icon
                  size="64"
                  color="#3ea0a3"
                  class="mb-3"
                >
                  mdi-map-plus
                </v-icon>
              </div>

              <!-- 認知引導：清晰的狀態說明 -->
              <div class="mb-6">
                <h4
                  class="text-h6 font-weight-bold mb-3"
                  style="color: #2d8c8f;"
                >
                  尚未新增任何土地資料
                </h4>
                <p class="text-body-1 text-grey-darken-1 mb-1">
                  您可以新增多筆土地資料，系統會自動計算總施作面積
                </p>
              </div>

              <!-- 行動召喚：降低使用者啟動阻力 -->
              <v-btn
                color="#3ea0a3"
                variant="flat"
                rounded="lg"
                size="large"
                class="px-8 py-2"
                @click="addNewLand"
              >
                <v-icon
                  size="small"
                  class="me-2"
                >
                  mdi-plus
                </v-icon>
                新增第一筆土地資料
              </v-btn>
            </v-sheet>
          </v-card>

          <!-- 設施地址區域 (編輯模式時顯示) -->
          <v-card
            v-show="landManagement.isEditingMode"
            flat
            class="mb-4 pa-4"
            color="#e3f4f4"
            rounded="lg"
          >
            <!-- 狀態指示條 -->
            <v-alert
              type="info"
              variant="tonal"
              density="compact"
              class="ma-0 mb-4"
              color="warning"
              prominent
            >
              <template #prepend>
                <v-icon size="small">
                  mdi-pencil-lock
                </v-icon>
              </template>
              <div class="d-flex align-center justify-space-between">
                <span class="text-body-2">
                  {{ landManagement.currentEditingLandId ? '編輯模式' : '新增模式' }}
                </span>
                <v-chip
                  size="x-small"
                  color="warning"
                  variant="tonal"
                >
                  編輯中
                </v-chip>
              </div>
            </v-alert>
            <v-card-title
              class="text-subtitle-1 font-weight-bold pa-0 pb-4 d-flex align-center"
              style="color: #2d8c8f"
            >
              <v-icon
                color="#3ea0a3"
                class="me-2 pb-1"
                size="small"
              >
                mdi-home-map-marker
              </v-icon>
              <span>
                <span class="required-asterisk">*</span>
                {{ landManagement.currentEditingLandId ? '編輯土地資料' : '新增土地資料' }}
              </span>
              <v-spacer />
              <v-btn
                variant="text"
                color="grey"
                size="small"
                @click="cancelLandEdit"
              >
                <v-icon
                  size="small"
                  class="me-1"
                >
                  mdi-close
                </v-icon>
                取消編輯
              </v-btn>
            </v-card-title>

            <!-- 頂部操作按鈕：便利性設計 -->
            <!-- <div class="d-flex gap-3 mb-6 pb-4 border-b border-grey-lighten-2">
              <v-btn
                color="success"
                variant="flat"
                rounded="lg"
                size="large"
                class="flex-grow-1"
                @click="saveLandEdit"
              >
                <v-icon
                  size="small"
                  class="me-2"
                >
                  mdi-content-save
                </v-icon>
                {{ landManagement.currentEditingLandId ? '更新土地資料' : '儲存土地資料' }}
              </v-btn>
            </div> -->

            <!-- 地址選擇區域 -->
            <v-sheet
              class="mb-3 pa-3 rounded"
              color="white"
            >
              <div class="d-flex align-center mb-2">
                <v-icon
                  size="small"
                  class="me-2"
                >
                  mdi-land-plots
                </v-icon>
                <span class="text-body-2 font-weight-medium">設施地段</span>
              </div>
              <v-row>
                <v-col
                  cols="12"
                  md="3"
                >
                  <v-select
                    v-model="localFormData.landCounty"
                    :items="counties"
                    variant="outlined"
                    density="comfortable"
                    color="#3ea0a3"
                    bg-color="white"
                    :rules="[v => !!v || '請選擇縣市']"
                    @update:model-value="onCountyChange"
                  >
                    <template #label>
                      縣市
                    </template>
                  </v-select>
                </v-col>
                <v-col
                  cols="12"
                  md="3"
                >
                  <v-select
                    v-model="localFormData.landTown"
                    :items="towns"
                    variant="outlined"
                    density="comfortable"
                    color="#3ea0a3"
                    bg-color="white"
                    :rules="[v => !!v || '請選擇鄉鎮市區']"
                    :disabled="!localFormData.landCounty || isSpecialCity"
                    @update:model-value="onTownChange"
                  >
                    <template #label>
                      鄉鎮市區
                    </template>
                  </v-select>
                </v-col>
                <v-col
                  cols="12"
                  md="6"
                >
                  <v-autocomplete
                    :key="sectionSelectKey"
                    v-model="localFormData.landSec"
                    v-model:search="sectionSearchText"
                    :items="sections"
                    :item-title="item => item.title"
                    :item-value="item => item.code"
                    variant="outlined"
                    density="comfortable"
                    color="#3ea0a3"
                    bg-color="white"
                    hide-details
                    clearable
                    autocomplete="off"
                    :placeholder="sections.length > 0 ? '搜尋地段名稱或段號...' : '請先選擇鄉鎮市區'"
                    :disabled="!localFormData.landTown"
                    :loading="loadingSections"
                    :no-data-text="'沒有找到相符的地段'"
                    :menu-props="{ closeOnContentClick: true }"
                    :auto-select-first="false"
                    :rules="[v => !!v || '請選擇地段']"
                    aria-label="選擇地段"
                    @update:search="onSectionSearchUpdate"
                    @blur="onSectionBlur"
                    @update:model-value="onSectionChange"
                  >
                    <template #label>
                      地段
                    </template>

                    <!-- 自定義選中項的顯示方式 - 使用 Vuetify 預設樣式 -->
                    <template #selection="{ item }">
                      <template v-if="item.raw">
                        {{ item.raw.displayName || item.raw.name }}
                      </template>
                      <template v-else>
                        {{ currentSelectedSection?.displayName || currentSelectedSection?.name || localFormData.landSec }}
                      </template>
                    </template>

                    <template #item="{ props, item }">
                      <v-list-item
                        v-bind="props"
                      >
                        <template #title>
                          <div>
                            {{ item.raw.displayName || item.raw.name }}
                          </div>
                        </template>

                        <template #subtitle>
                          <div class="d-flex align-center mt-1">
                            <span class="text-caption text-grey-darken-1">
                              段號: {{ item.raw.code || '無' }}
                            </span>
                          </div>
                        </template>
                      </v-list-item>
                    </template>
                  </v-autocomplete>
                </v-col>
              </v-row>
            </v-sheet>

            <!-- 地號與查詢 -->
            <v-sheet
              class="mb-3 pa-3 rounded"
              color="white"
            >
              <div class="d-flex align-center mb-2">
                <v-icon
                  size="small"
                  class="me-2"
                >
                  mdi-land-plots-marker
                </v-icon>
                <span class="text-body-2 font-weight-medium">地號資訊</span>
              </div>

              <!-- 地號輸入區域 -->
              <v-row class="mb-0 pb-0">
                <v-col
                  cols="12"
                  md="8"
                >
                  <v-card
                    variant="outlined"
                    color="grey-lighten-1"
                    class="mb-4 bg-grey-lighten-5"
                    elevation="0"
                  >
                    <v-card-text class="pb-3">
                      <!-- <div class="d-flex align-center mb-2">
                        <v-icon
                          size="small"
                          color="#3ea0a3"
                          class="me-2"
                        >
                          mdi-format-list-numbered
                        </v-icon>
                        <span class="text-body-2 font-weight-medium text-grey-darken-2">地號輸入</span>
                      </div> -->

                      <v-row
                        align="center"
                        no-gutters
                      >
                        <v-col cols="auto">
                          <div class="d-flex align-center">
                            <!-- 母地號輸入 -->
                            <div class="me-1">
                              <div class="text-caption text-grey-darken-1 mb-1 ps-1">
                                母地號
                              </div>
                              <v-text-field
                                v-model="formattedLandNumberMain"
                                variant="outlined"
                                density="compact"
                                color="#3ea0a3"
                                bg-color="white"
                                type="tel"
                                maxlength="4"
                                style="width: 90px"
                                hide-details
                                placeholder="0000"
                                autocomplete="off"
                                :rules="[v => !!v || '請輸入主地號']"
                                @focus="landNumberMainFocused = true"
                                @blur="landNumberMainFocused = false"
                                @input="onLandNumberMainInput"
                              />
                            </div>

                            <!-- 分隔符號 -->
                            <div class="mx-2 mt-4">
                              <v-icon
                                size="20"
                                color="grey"
                              >
                                mdi-minus
                              </v-icon>
                            </div>

                            <!-- 子地號輸入 -->
                            <div class="me-3">
                              <div class="text-caption text-grey-darken-1 mb-1 ps-1">
                                子地號
                              </div>
                              <v-text-field
                                v-model="formattedLandNumberSub"
                                variant="outlined"
                                density="compact"
                                color="#3ea0a3"
                                bg-color="white"
                                type="tel"
                                maxlength="4"
                                style="width: 90px"
                                hide-details
                                placeholder="0000"
                                autocomplete="off"
                                @focus="landNumberSubFocused = true"
                                @blur="landNumberSubFocused = false"
                                @input="onLandNumberSubInput"
                              />
                            </div>

                            <!-- 查詢按鈕 -->
                            <div class="mt-4 d-flex gap-3">
                              <v-btn
                                color="#3ea0a3"
                                variant="outlined"
                                rounded="lg"
                                class="px-2"
                                @click="showLandInfoDialog"
                              >
                                <v-icon
                                  size="18"
                                  class="me-2"
                                >
                                  mdi-magnify
                                </v-icon>
                                查詢地號
                              </v-btn>
                              <v-btn
                                color="#3ea0a3"
                                variant="outlined"
                                rounded="lg"
                                class="px-2 ml-2"
                                @click="showEligibilityDialog"
                              >
                                <v-icon
                                  size="18"
                                  class="me-2"
                                >
                                  mdi-account-check
                                </v-icon>
                                申請資格預查
                              </v-btn>
                            </div>
                          </div>
                        </v-col>
                      </v-row>
                    </v-card-text>
                    <!-- 提示資訊 -->
                    <v-alert
                      variant="tonal"
                      density="compact"
                      class="mt-3 mb-0"
                      color="blue-grey"
                    >
                      <template #prepend>
                        <!-- <v-icon size="18">mdi-information-outline</v-icon> -->
                      </template>
                      <div class="text-caption">
                        <strong>查詢說明：</strong>請輸入完整地號後點擊查詢按鈕。若查無地號資料，請洽中心技術團隊。
                      </div>
                    </v-alert>
                  </v-card>
                </v-col>
                <v-spacer />
                <!-- 土地特性選項區域 -->
                <v-col
                  cols="12"
                  md="4"
                >
                  <div class="d-flex align-center ma-0">
                    <span
                      class="text-body-2 font-weight-medium me-3"
                      style="min-width: 80px;"
                    >
                      原民區域
                    </span>
                    <v-radio-group
                      v-model="localFormData.isAboriginalArea"
                      disabled
                      :false-value="false"
                      :true-value="true"
                      inline
                      hide-details
                      density="compact"
                      color="#3ea0a3"
                      @update:model-value="updateFormData"
                    >
                      <v-radio
                        label="是"
                        :value="true"
                        density="compact"
                      />
                      <v-radio
                        label="否"
                        :value="false"
                        density="compact"
                      />
                    </v-radio-group>
                  </div>

                  <div class="d-flex align-center ma-0">
                    <span
                      class="text-body-2 font-weight-medium me-3"
                      style="min-width: 80px;"
                    >
                      農田水利事業區域內
                    </span>
                    <v-radio-group
                      v-model="localFormData.isIrrigationArea"
                      disabled
                      :false-value="false"
                      :true-value="true"
                      inline
                      hide-details
                      density="compact"
                      color="#3ea0a3"
                      @update:model-value="updateFormData"
                    >
                      <v-radio
                        label="是"
                        :value="true"
                        density="compact"
                      />
                      <v-radio
                        label="否"
                        :value="false"
                        density="compact"
                      />
                    </v-radio-group>
                  </div>

                  <div class="d-flex align-center mb-2">
                    <span
                      class="text-body-2 font-weight-medium me-3"
                      style="min-width: 80px;"
                    >
                      再次申請
                    </span>
                    <v-radio-group
                      v-model="localFormData.isReapplied"
                      :false-value="false"
                      :true-value="true"
                      inline
                      hide-details
                      density="compact"
                      color="#3ea0a3"
                      @update:model-value="updateFormData"
                    >
                      <v-radio
                        label="是"
                        :value="true"
                        density="compact"
                      />
                      <v-radio
                        label="否"
                        :value="false"
                        density="compact"
                      />
                    </v-radio-group>
                  </div>

                  <!-- 土地作農業使用證明書 -->
                  <v-divider class="my-3" />

                  <div class="d-flex align-center mb-0 pb-0">
                    <span
                      class="text-body-2 font-weight-medium me-3"
                      style="min-width: 80px;"
                    >
                      土地作農業使用證明書
                    </span>
                    <v-radio-group
                      v-model="localFormData.hasAgriculturalCertificate"
                      :false-value="false"
                      :true-value="true"
                      inline
                      hide-details
                      density="compact"
                      color="#3ea0a3"
                      @update:model-value="updateFormData"
                    >
                      <v-radio
                        label="是"
                        :value="true"
                        density="compact"
                      />
                      <v-radio
                        label="否"
                        :value="false"
                        density="compact"
                      />
                    </v-radio-group>
                  </div>

                  <!-- 核發日期輸入欄位 -->
                  <div
                    v-if="localFormData.hasAgriculturalCertificate"
                    class="mb-0 pb-0"
                  >
                    <div class="d-flex align-center">
                      <span
                        class="text-body-2 font-weight-medium me-3"
                        style="min-width: 80px;"
                      >
                        核發日期
                      </span>
                      <div
                        class="date-display-text"
                        @click="showDatePicker = true"
                      >
                        <v-icon
                          size="small"
                          class="me-1"
                          color="#3ea0a3"
                        >
                          mdi-calendar
                        </v-icon>
                        <span class="text-body-2">
                          {{ certificateDateFormatted || '點擊選擇日期' }}
                        </span>
                      </div>
                    </div>
                  </div>
                </v-col>
              </v-row>

              <!-- 地號資訊說明提示 -->
              <v-alert
                type="info"
                variant="outlined"
                density="compact"
                class="my-0"
                color="deep-orange-darken-1"
              >
                <template #prepend>
                  <v-icon
                    size="small"
                    color="deep-orange-darken-1"
                  >
                    mdi-information-outline
                  </v-icon>
                </template>
                <div
                  class="text-caption font-weight-medium"
                  style="color: #424242;"
                >
                  <strong style="color: #d84315;">提醒：</strong>各選項資訊是由原地號資料判別，有土地重測或是分割情形，請再次確認
                </div>
              </v-alert>
            </v-sheet>

            <!-- 坐標資訊 -->
            <v-sheet
              class="mb-3 pa-3 rounded"
              color="white"
            >
              <div class="d-flex align-center mb-2">
                <v-icon
                  size="small"
                  class="me-2"
                >
                  mdi-map-marker
                </v-icon>
                <span class="text-body-2 font-weight-medium">坐標資訊</span>
              </div>

              <!-- 坐標說明提示 -->
              <v-alert
                type="info"
                variant="tonal"
                density="compact"
                class="mb-3"
                color="blue-grey"
              >
                <template #prepend>
                  <v-icon size="small">
                    mdi-information-outline
                  </v-icon>
                </template>
                <div class="text-caption">
                  <strong>坐標輸入說明：</strong><br>
                  <!-- • 請輸入 TWD97 坐標系統（EPSG:3826）的坐標值<br> -->
                  • 緯度範圍：約 21.8° ~ 25.4°（北緯）<br>
                  • 經度範圍：約 119.0° ~ 122.5°（東經）<br>
                  <!-- • 可使用 Google Maps 或內政部地政司網站取得坐標 -->
                </div>
              </v-alert>

              <v-row>
                <v-col
                  cols="12"
                  md="6"
                >
                  <v-text-field
                    v-model="localFormData.latitude"
                    variant="outlined"
                    density="comfortable"
                    color="#3ea0a3"
                    bg-color="white"
                    placeholder="例：23.515552"
                    hint="北緯坐標，小數點後建議4位數"
                    persistent-hint
                    :rules="[
                      v => !!v || '請輸入緯度',
                      v => !isNaN(parseFloat(v)) || '請輸入有效的數值',
                      v => (parseFloat(v) >= 21.8 && parseFloat(v) <= 25.4) || '緯度範圍應在 21.8° ~ 25.4° 之間'
                    ]"
                    @update:model-value="updateFormData"
                  >
                    <template #label>
                      緯度（°N）
                    </template>
                  </v-text-field>
                </v-col>
                <v-col
                  cols="12"
                  md="6"
                >
                  <v-text-field
                    v-model="localFormData.longitude"
                    variant="outlined"
                    density="comfortable"
                    color="#3ea0a3"
                    bg-color="white"
                    placeholder="例：120.573425"
                    hint="東經坐標，小數點後建議4位數"
                    persistent-hint
                    :rules="[
                      v => !!v || '請輸入經度',
                      v => !isNaN(parseFloat(v)) || '請輸入有效的數值',
                      v => (parseFloat(v) >= 119.0 && parseFloat(v) <= 122.5) || '經度範圍應在 119.0° ~ 122.5° 之間'
                    ]"
                    @update:model-value="updateFormData"
                  >
                    <template #label>
                      經度（°E）
                    </template>
                  </v-text-field>
                </v-col>
              </v-row>

              <!-- 坐標取得方式說明 -->
              <!-- <v-expansion-panels
                variant="accordion"
                class="mt-3"
              >
                <v-expansion-panel
                  title="如何取得坐標？"
                  collapse-icon="mdi-chevron-up"
                  expand-icon="mdi-chevron-down"
                >
                  <v-expansion-panel-text>
                    <div class="text-body-2">
                      <p class="font-weight-medium mb-2">推薦取得坐標的方式：</p>

                      <div class="mb-3">
                        <p class="font-weight-medium text-primary">方法一：使用 Google Maps</p>
                        <ol class="pl-4">
                          <li>開啟 Google Maps (maps.google.com)</li>
                          <li>搜尋或點選您的土地位置</li>
                          <li>在地圖上右鍵點擊該位置</li>
                          <li>複製彈出的坐標數值（格式：緯度, 經度）</li>
                        </ol>
                      </div>

                      <div class="mb-3">
                        <p class="font-weight-medium text-primary">方法二：內政部地政司網站</p>
                        <ol class="pl-4">
                          <li>前往內政部地政司網站</li>
                          <li>使用「地籍圖資網路便民服務系統」</li>
                          <li>查詢您的地號並取得坐標</li>
                        </ol>
                      </div>

                      <v-alert
                        type="warning"
                        variant="tonal"
                        density="compact"
                        class="mt-2"
                      >
                        <div class="text-caption">
                          <strong>注意：</strong>請確保坐標準確性，錯誤的坐標可能影響補助審核。
                        </div>
                      </v-alert>
                    </div>
                  </v-expansion-panel-text>
                </v-expansion-panel>
              </v-expansion-panels> -->
            </v-sheet>

            <!-- 面積資訊 -->
            <v-sheet
              class="mb-3 pa-3 rounded"
              color="rgba(255, 248, 225, 0.6)"
            >
              <div class="d-flex align-center mb-2">
                <v-icon
                  size="small"
                  class="me-2"
                  color="#3ea0a3"
                >
                  mdi-ruler-square
                </v-icon>
                <span class="text-body-2 font-weight-medium">面積資訊</span>
              </div>
              <v-row>
                <v-col
                  cols="12"
                  md="6"
                >
                  <div class="d-flex align-center">
                    <span class="text-body-2 font-weight-medium me-2">農地地籍面積</span>
                    <v-text-field
                      v-model="localFormData.landArea"
                      variant="outlined"
                      density="compact"
                      color="#3ea0a3"
                      bg-color="white"
                      class="me-2"
                      style="width: 60px"
                      :rules="[v => !!v || '請輸入土地面積']"
                      @update:model-value="updateFormData"
                    />
                    <div class="me-2">
                      ㎡
                    </div>
                    <v-text-field
                      v-model="landAreaHaComputed"
                      variant="outlined"
                      density="compact"
                      color="#3ea0a3"
                      bg-color="white"
                      style="width: 60px"
                      readonly
                    />
                    <div class="ms-2">
                      公頃
                    </div>
                  </div>
                </v-col>
                <v-col
                  cols="12"
                  md="6"
                >
                  <div class="d-flex align-center">
                    <span class="text-body-2 font-weight-medium me-2">施作面積</span>
                    <v-text-field
                      v-model="localFormData.facilityArea"
                      variant="outlined"
                      density="compact"
                      color="#3ea0a3"
                      bg-color="white"
                      class="me-2"
                      style="width: 60px"
                      :rules="[
                        v => !!v || '請輸入施作面積',
                        v => !v || parseFloat(v) <= parseFloat(localFormData.landArea) || '施作面積不能大於農地地籍面積'
                      ]"
                      @update:model-value="updateFormData"
                    />
                    <div class="me-2">
                      ㎡
                    </div>
                    <v-text-field
                      v-model="facilityAreaHaComputed"
                      variant="outlined"
                      density="compact"
                      color="#3ea0a3"
                      bg-color="white"
                      style="width: 60px"
                      readonly
                    />
                    <div class="ms-2">
                      公頃
                    </div>
                  </div>
                </v-col>
              </v-row>
            </v-sheet>

            <!-- 農地種植作物 -->
            <v-sheet
              class="mb-3 pa-3 rounded"
              color="white"
            >
              <div class="d-flex align-center mb-2">
                <v-icon
                  size="small"
                  class="me-2"
                  color="#3ea0a3"
                >
                  mdi-sprout
                </v-icon>
                <span class="text-body-2 font-weight-medium">農地種植作物</span>
              </div>
              <div class="d-flex align-center mb-2">
                <v-select
                  v-model="localFormData.cropCategory"
                  :items="cropCategories"
                  variant="outlined"
                  density="comfortable"
                  color="#3ea0a3"
                  bg-color="white"
                  class="me-2"
                  style="width: 200px"
                  @update:model-value="onCropCategoryChange"
                >
                  <template #label>
                    作物類別
                  </template>
                </v-select>

                <v-select
                  v-model="localFormData.cropName"
                  :items="crops"
                  variant="outlined"
                  density="comfortable"
                  color="#3ea0a3"
                  bg-color="white"
                  class="me-2"
                  style="width: 200px"
                  :disabled="!localFormData.cropCategory"
                >
                  <template #label>
                    作物名稱
                  </template>
                </v-select>
                <v-btn
                  variant="outlined"
                  color="#3ea0a3"
                  rounded="lg"
                  size="small"
                  :disabled="!localFormData.cropCategory || !localFormData.cropName"
                  @click="addCrop"
                >
                  <v-icon
                    size="small"
                    class="me-1"
                  >
                    mdi-plus
                  </v-icon>
                  加入
                </v-btn>
              </div>

              <v-table
                density="compact"
                class="rounded border"
              >
                <thead class="bg-grey-lighten-3">
                  <tr>
                    <th
                      class="text-center"
                      style="width: 50px"
                    >
                      NO.
                    </th>
                    <th>類別</th>
                    <th>作物</th>
                    <th
                      class="text-center"
                      style="width: 80px"
                    >
                      刪除
                    </th>
                  </tr>
                </thead>
                <tbody>
                  <tr
                    v-for="(crop, index) in localFormData.crops"
                    :key="index"
                  >
                    <td class="text-center">
                      {{ index + 1 }}
                    </td>
                    <td>{{ crop.category }}</td>
                    <td>{{ crop.name }}</td>
                    <td class="text-center">
                      <v-btn
                        icon
                        size="x-small"
                        color="error"
                        variant="text"
                        @click="removeCrop(index)"
                      >
                        <v-icon>mdi-close</v-icon>
                      </v-btn>
                    </td>
                  </tr>
                  <tr v-if="!localFormData.crops || localFormData.crops.length === 0">
                    <td
                      colspan="4"
                      class="text-center py-3 text-grey"
                    >
                      尚未新增任何作物，請使用上方加入按鈕新增
                    </td>
                  </tr>
                </tbody>
              </v-table>
            </v-sheet>
            <!-- 底部操作按鈕：易達性設計 -->
            <div class="d-flex gap-3 mt-6 pt-4 border-t border-grey-lighten-2">
              <v-btn
                color="success"
                variant="flat"
                rounded="lg"
                size="large"
                class="flex-grow-1"
                @click="saveLandEdit"
              >
                <v-icon
                  size="small"
                  class="me-2"
                >
                  mdi-content-save
                </v-icon>
                {{ landManagement.currentEditingLandId ? '更新土地資料' : '儲存土地資料' }}
              </v-btn>
            </div>
          </v-card>

          <!-- 所有權人資料區域 (已隱藏) -->
          <v-card
            v-if="false"
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
                mdi-account-multiple
              </v-icon>
              <span><span class="required-asterisk">*</span>所有權人資料</span>
            </v-card-title>

            <!-- 基本所有權人資料 (簡化版本，假設單一持分) -->
            <v-sheet
              class="mb-3 pa-3 rounded"
              color="white"
            >
              <div class="d-flex align-center justify-space-between mb-2">
                <div class="d-flex align-center">
                  <v-icon
                    size="small"
                    class="me-2"
                  >
                    mdi-account-details
                  </v-icon>
                  <span class="text-body-2 font-weight-medium">所有權人基本資料</span>
                  <v-chip
                    size="x-small"
                    color="success"
                    variant="tonal"
                    class="ms-2"
                  >
                    單一持分
                  </v-chip>
                </div>
                <v-btn
                  v-if="!showCoOwnerSettings"
                  variant="text"
                  color="#3ea0a3"
                  size="small"
                  @click="showCoOwnerSettings = true"
                >
                  <v-icon
                    size="small"
                    class="me-1"
                  >
                    mdi-account-plus
                  </v-icon>
                  新增共同持分人
                </v-btn>
              </div>
              <v-row>
                <v-col
                  cols="12"
                  md="6"
                >
                  <v-text-field
                    v-model="localFormData.ownerName"
                    variant="outlined"
                    density="comfortable"
                    color="#3ea0a3"
                    bg-color="white"
                    @update:model-value="updateFormData"
                  >
                    <template #label>
                      所有權人姓名
                    </template>
                  </v-text-field>
                </v-col>
                <v-col
                  cols="12"
                  md="6"
                >
                  <v-text-field
                    v-model="localFormData.ownerId"
                    variant="outlined"
                    density="comfortable"
                    color="#3ea0a3"
                    bg-color="white"
                    @update:model-value="updateFormData"
                  >
                    <template #label>
                      所有權人身分證字號
                    </template>
                  </v-text-field>
                </v-col>
              </v-row>
            </v-sheet>

            <!-- 展開的共同持分人設定區域 -->
            <v-expand-transition>
              <div v-if="showCoOwnerSettings">
                <!-- 共同持分人說明 -->
                <v-alert
                  type="info"
                  variant="tonal"
                  class="mb-3"
                  density="compact"
                >
                  您已切換至共同持分模式，請填寫各持分人的詳細資料及持分比例
                </v-alert>

                <!-- 持分人地址 -->
                <v-sheet
                  class="mb-3 pa-3 rounded"
                  color="white"
                >
                  <div class="d-flex align-center mb-2">
                    <v-icon
                      size="small"
                      class="me-2"
                    >
                      mdi-home
                    </v-icon>
                    <span class="text-body-2 font-weight-medium">持分人地址</span>
                  </div>
                  <v-row>
                    <v-col cols="12">
                      <div class="d-flex align-center flex-wrap">
                        <v-select
                          v-model="localFormData.ownerCounty"
                          :items="counties"
                          item-title="title"
                          item-value="value"
                          variant="outlined"
                          density="comfortable"
                          color="#3ea0a3"
                          bg-color="white"
                          class="me-2 mb-2"
                          style="width: 150px"
                          @update:model-value="onOwnerCountyChange"
                        >
                          <template #label>
                            縣市<span class="required-asterisk">*(必填)</span>
                          </template>
                        </v-select>
                        <v-select
                          v-model="localFormData.ownerTown"
                          :items="ownerTowns"
                          label="鄉鎮市區"
                          variant="outlined"
                          density="comfortable"
                          color="#3ea0a3"
                          bg-color="white"
                          class="me-2 mb-2"
                          style="width: 150px"
                          :disabled="!localFormData.ownerCounty"
                          @update:model-value="onOwnerTownChange"
                        />
                        <v-select
                          v-model="localFormData.ownerVillage"
                          :items="ownerVillages"
                          label="村里"
                          variant="outlined"
                          density="comfortable"
                          color="#3ea0a3"
                          bg-color="white"
                          class="mb-2"
                          style="width: 150px"
                          :disabled="!localFormData.ownerTown"
                        />
                      </div>
                    </v-col>
                  </v-row>
                </v-sheet>

                <!-- 持分資訊 -->
                <v-sheet
                  class="mb-3 pa-3 rounded"
                  color="rgba(255, 248, 225, 0.6)"
                >
                  <div class="d-flex align-center mb-2">
                    <v-icon
                      size="small"
                      class="me-2"
                      color="#3ea0a3"
                    >
                      mdi-percent
                    </v-icon>
                    <span class="text-body-2 font-weight-medium">持分資訊</span>
                  </div>
                  <v-row align="center">
                    <v-col
                      cols="12"
                      md="6"
                    >
                      <div class="d-flex align-center">
                        <span class="text-body-2 font-weight-medium me-2">持分比例</span>
                        <v-text-field
                          v-model="localFormData.ownerShare1"
                          variant="outlined"
                          density="compact"
                          color="#3ea0a3"
                          bg-color="white"
                          class="me-1"
                          style="width: 80px"
                          type="number"
                          @update:model-value="updateFormData"
                        />
                        <div class="mx-1">
                          分子
                        </div>
                        <div class="mx-1">
                          /
                        </div>
                        <v-text-field
                          v-model="localFormData.ownerShare2"
                          variant="outlined"
                          density="compact"
                          color="#3ea0a3"
                          bg-color="white"
                          class="me-1"
                          style="width: 80px"
                          type="number"
                          @update:model-value="updateFormData"
                        />
                        <div class="ms-1">
                          分母
                        </div>
                      </div>
                    </v-col>
                    <v-col
                      cols="12"
                      md="6"
                    >
                      <div class="d-flex align-center">
                        <span class="text-body-2 font-weight-medium me-2">持分面積</span>
                        <v-text-field
                          v-model="ownerAreaComputed"
                          variant="outlined"
                          density="compact"
                          color="#3ea0a3"
                          bg-color="white"
                          class="me-2"
                          style="width: 120px"
                          readonly
                        />
                        <div class="me-2">
                          ㎡
                        </div>
                        <v-btn
                          variant="outlined"
                          color="#3ea0a3"
                          rounded="lg"
                          size="small"
                          :disabled="!canAddOwner"
                          @click="addOwner"
                        >
                          <v-icon
                            size="small"
                            class="me-1"
                          >
                            mdi-plus
                          </v-icon>
                          加入
                        </v-btn>
                      </div>
                    </v-col>
                  </v-row>
                </v-sheet>

                <!-- 所有權人列表 -->
                <v-sheet class="pa-0">
                  <div class="d-flex align-center justify-space-between mb-2">
                    <span class="text-body-2 font-weight-medium">共同持分人清單</span>
                    <v-btn
                      variant="text"
                      color="grey"
                      size="small"
                      @click="collapseCoOwnerSettings"
                    >
                      <v-icon
                        size="small"
                        class="me-1"
                      >
                        mdi-chevron-up
                      </v-icon>
                      收合
                    </v-btn>
                  </div>
                  <v-table
                    density="comfortable"
                    class="rounded border"
                  >
                    <thead class="bg-grey-lighten-3">
                      <tr>
                        <th
                          class="text-center"
                          style="width: 50px"
                        >
                          NO.
                        </th>
                        <th>姓名</th>
                        <th>身分證字號</th>
                        <th>地址</th>
                        <th>持分比例</th>
                        <th>持分面積㎡</th>
                        <th
                          class="text-center"
                          style="width: 80px"
                        >
                          刪除
                        </th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr
                        v-for="(owner, index) in localFormData.owners"
                        :key="index"
                      >
                        <td class="text-center">
                          {{ index + 1 }}
                        </td>
                        <td>{{ owner.name }}</td>
                        <td>{{ owner.id }}</td>
                        <td>{{ owner.address }}</td>
                        <td>{{ owner.share }}</td>
                        <td>{{ owner.area }}</td>
                        <td class="text-center">
                          <v-btn
                            icon
                            size="x-small"
                            color="error"
                            variant="text"
                            @click="removeOwner(index)"
                          >
                            <v-icon>mdi-close</v-icon>
                          </v-btn>
                        </td>
                      </tr>
                      <tr v-if="!localFormData.owners || localFormData.owners.length === 0">
                        <td
                          colspan="7"
                          class="text-center py-3 text-grey"
                        >
                          尚未新增任何共同持分人，請使用上方加入按鈕新增
                        </td>
                      </tr>
                    </tbody>
                  </v-table>
                </v-sheet>
              </div>
            </v-expand-transition>
          </v-card>
        </v-form>
      </v-card-text>
    </v-card>

    <!-- Date picker dialog -->
    <v-dialog
      v-model="showDatePicker"
      max-width="450px"
      class="date-picker-dialog"
    >
      <v-card>
        <v-card-title
          class="text-subtitle-1 font-weight-bold pa-4"
          style="color: #2d8c8f; background-color: #e3f4f4;"
        >
          <v-icon
            color="#3ea0a3"
            class="me-2"
            size="small"
          >
            mdi-calendar
          </v-icon>
          <span>選擇核發日期</span>
        </v-card-title>

        <v-card-text class="pa-4">
          <v-row>
            <v-col cols="4">
              <v-select
                v-model="localFormData.certificateYear"
                :items="yearOptions"
                label="民國年"
                variant="outlined"
                density="comfortable"
                color="#3ea0a3"
                bg-color="white"
                item-title="title"
                item-value="value"
                @update:model-value="updateFormData"
              />
            </v-col>
            <v-col cols="4">
              <v-select
                v-model="localFormData.certificateMonth"
                :items="monthOptions"
                label="月"
                variant="outlined"
                density="comfortable"
                color="#3ea0a3"
                bg-color="white"
                item-title="title"
                item-value="value"
                :disabled="!localFormData.certificateYear"
                @update:model-value="updateFormData"
              />
            </v-col>
            <v-col cols="4">
              <v-select
                v-model="localFormData.certificateDay"
                :items="dayOptions"
                label="日"
                variant="outlined"
                density="comfortable"
                color="#3ea0a3"
                bg-color="white"
                item-title="title"
                item-value="value"
                :disabled="!localFormData.certificateYear || !localFormData.certificateMonth"
                @update:model-value="updateFormData"
              />
            </v-col>
          </v-row>

          <!-- 日期預覽 -->
          <v-alert
            v-if="certificateDateFormatted"
            type="success"
            variant="tonal"
            density="compact"
            class="mt-3"
            color="blue-grey"
          >
            <template #prepend>
              <v-icon size="small">
                mdi-calendar-check
              </v-icon>
            </template>
            <div class="text-caption">
              <strong>選擇的日期：</strong>{{ certificateDateFormatted }}
            </div>
          </v-alert>
        </v-card-text>

        <v-card-actions class="pa-4 pt-0">
          <v-spacer />
          <v-btn
            variant="text"
            @click="showDatePicker = false"
          >
            取消
          </v-btn>
          <v-btn
            color="#3ea0a3"
            variant="flat"
            :disabled="!certificateDateFormatted"
            @click="confirmDate"
          >
            確定
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup lang="ts">
// Import OpenLayers dependencies
import 'ol/ol.css';
import Map from 'ol/Map';
import View from 'ol/View';
import TileLayer from 'ol/layer/Tile';
import OSM from 'ol/source/OSM';
import { fromLonLat, transform } from 'ol/proj';
import Point from 'ol/geom/Point';
import Polygon from 'ol/geom/Polygon';
import MultiPolygon from 'ol/geom/MultiPolygon';
import { Vector as VectorLayer } from 'ol/layer';
import { Vector as VectorSource } from 'ol/source';
import { Style, Icon, Stroke, Fill } from 'ol/style';
import GeoJSON from 'ol/format/GeoJSON';
import { Select, Modify } from 'ol/interaction';
import { click } from 'ol/events/condition';
import { unByKey } from 'ol/Observable';
import type { EventsKey } from 'ol/events';
import { getArea } from 'ol/sphere';
import { createEmpty, extend } from 'ol/extent';
import { debounce } from 'lodash-es';
import type { Feature } from 'ol';
import type { Geometry } from 'ol/geom';
import { queryOfficeBoundaries, queryCountyBoundaries } from '@/services/spatialService';

// Define type for selected feature info
interface SelectedFeatureInfo {
  Land_no?: string;
  section?: string;
  area?: string | number;
  [key: string]: unknown;
}

// 定義單筆土地資料結構
interface LandData {
  id: string; // 唯一識別碼
  // 設施地段
  landCounty: string | number;
  landTown: string | number;
  landSec: string | number;
  landSecName?: string;  // 地段名稱，選擇地段時自動儲存

  // 地號資訊
  landNumber: string;
  landNumberMain: string;
  landNumberSub: string;

  // 土地特性
  isAboriginalArea: boolean;
  isIrrigationArea: boolean;
  isReapplied: boolean;
  hasAgriculturalCertificate: boolean;
  certificateYear: string;
  certificateMonth: string;
  certificateDay: string;

  // 坐標資訊
  longitude: string;
  latitude: string;

  // 面積資訊
  landArea: string;
  landAreaHa: string;
  facilityArea: string;
  facilityAreaHa: string;

  // 農地種植作物
  cropCategory: string;
  cropName: string;
  crops: Array<{category: string, name: string}>;

  // 所有權人資料
  ownerName: string;
  ownerId: string;
  ownerCounty: string | number;
  ownerTown: string | number;
  ownerVillage: string | number;
  ownerShare1: string;
  ownerShare2: string;
  ownerArea: string;
  owners: Array<{
    name: string;
    id: string;
    address: string;
    share: string;
    area: string;
  }>;
}

// 土地管理狀態
interface LandManagementState {
  currentEditingLandId: string | null; // 當前編輯的土地ID
  isEditingMode: boolean; // 是否在編輯模式
  showLandEditDialog: boolean; // 是否顯示編輯對話框
  lands: LandData[]; // 所有土地資料
}

// Import store
import { useGrantsStore } from '@/stores/grants';
import { useDomicileStore } from '@/stores/domicile';
import { useRoute } from 'vue-router';
import { fetchLandSectionsByLandCodes, type LandSection } from '@/services/landSectionNlscService';
import { markRaw, nextTick, reactive } from 'vue';

// 事件驅動架構：定義事件類型
interface Step2Events {
  'step-data-changed': [eventData: { step: number; data: Record<string, unknown>; valid: boolean }];
  'validation-changed': [eventData: { step: number; valid: boolean }];
  'ready-to-proceed': [eventData: { step: number; data: Record<string, unknown> }];
  'go-back-requested': [eventData: { step: number }];
  // 新增：導航狀態控制事件
  'navigation-state-changed': [eventData: {
    step: number;
    canNavigate: boolean;
    isEditing: boolean;
    reason?: string;
  }];
}

// 事件驅動架構：定義 emits
const emit = defineEmits<Step2Events>();

// 事件驅動架構：移除 props 依賴，但保留 currentStep
defineProps<{
  currentStep: number;
}>();

const route = useRoute();

// Reference to map element and map instance
const mapElement = ref(null);
let map: Map | null = null;

// 地圖初始化狀態管理
const mapState = reactive({
  isInitialized: false,
  isInitializing: false,
});

// Form validation references
const form = ref(null);
const localValid = ref(true);

// Co-owner settings visibility control
const showCoOwnerSettings = ref(false);

// Access the grants store
const grantsStore = useGrantsStore();
const domicileStore = useDomicileStore();

// 統一步驟組件架構：初始化保護與事件管理系統
interface StepInitializationGuard {
  isInitialized: boolean
  isInitializing: boolean
  isDataLoading: boolean
}

interface StepEventEmitter {
  emitDataChanged: () => void
  emitValidationChanged: (valid: boolean) => void
  emitReadyToProceed: () => void
  emitGoBackRequested: () => void
}

interface CascadeSelectManager {
  loadCascadeData: () => Promise<void>
  resetCascadeSelections: (level: 'county' | 'town' | 'village') => void
}

// 統一的保護函數工廠
interface ProtectedFunctionFactory {
  createProtectedHandler: <T extends (...args: unknown[]) => unknown>(fn: T) => T
  createProtectedWatch: <T extends (...args: unknown[]) => unknown>(fn: T) => T
  createCascadeHandler: <T extends (...args: unknown[]) => unknown>(fn: T) => T
}

// 統一的步驟管理器
interface UnifiedStepManager extends StepEventEmitter, CascadeSelectManager, ProtectedFunctionFactory {
  guard: StepInitializationGuard
  validateForm: () => Promise<boolean>
  updateFormData: () => void
}

// 統一的初始化保護系統
const createInitializationGuard = (): StepInitializationGuard => ({
  isInitialized: false,
  isInitializing: false,
  isDataLoading: false
})

// 創建保護函數工廠
const createProtectedFunctionFactory = (
  guard: StepInitializationGuard,
  eventEmitter: StepEventEmitter
): ProtectedFunctionFactory => ({
  // 創建受保護的事件處理函數
  createProtectedHandler: <T extends (...args: unknown[]) => unknown>(fn: T): T => {
    return ((...args: unknown[]) => {
      const result = fn(...args)
      // 在初始化期間不觸發事件
      if (!guard.isInitializing && guard.isInitialized) {
        eventEmitter.emitDataChanged()
      } else {
        console.log(`⏸️ step2.vue: Skipping event emission during initialization (${fn.name})`)
      }
      return result
    }) as T
  },

  // 創建受保護的 Watch 函數
  createProtectedWatch: <T extends (...args: unknown[]) => unknown>(fn: T): T => {
    return ((...args: unknown[]) => {
      if (guard.isInitializing) {
        console.log(`⏸️ step2.vue: Skipping watch execution during initialization (${fn.name})`)
        return
      }
      return fn(...args)
    }) as T
  },

  // 創建受保護的級聯選擇處理函數
  createCascadeHandler: <T extends (...args: unknown[]) => unknown>(fn: T): T => {
    return ((...args: unknown[]) => {
      const result = fn(...args)
      if (!guard.isInitializing && guard.isInitialized) {
        eventEmitter.emitDataChanged()
      }
      return result
    }) as T
  }
})

// 統一的事件發送器
const createEventEmitter = (
  stepNumber: number,
  emit: ((evt: "step-data-changed", eventData: { step: number; data: Record<string, unknown>; valid: boolean; }) => void) &
        ((evt: "validation-changed", eventData: { step: number; valid: boolean; }) => void) &
        ((evt: "ready-to-proceed", eventData: { step: number; data: Record<string, unknown>; }) => void) &
        ((evt: "go-back-requested", eventData: { step: number; }) => void),
  formData: Record<string, unknown>,
  validationState: Ref<boolean>,
  guard: StepInitializationGuard
): StepEventEmitter => {
  const debouncedEmitDataChanged = debounce(() => {
    if (!guard.isInitialized || guard.isInitializing) return

    console.log(`🚀 step${stepNumber}.vue: Emitting step-data-changed event`)
    emit('step-data-changed', {
      step: stepNumber,
      data: { ...formData },
      valid: validationState.value
    })
  }, 300)

  return {
    emitDataChanged: () => {
      if (!guard.isInitialized || guard.isInitializing) {
        console.log(`⏸️ step${stepNumber}.vue: Skipping event emission during initialization`)
        return
      }
      debouncedEmitDataChanged()
    },

    emitValidationChanged: (valid: boolean) => {
      if (!guard.isInitializing && guard.isInitialized) {
        emit('validation-changed', { step: stepNumber, valid })
      } else {
        console.log(`⏸️ step${stepNumber}.vue: Skipping validation event emission during initialization`)
      }
    },

    emitReadyToProceed: () => {
      console.log(`✅ step${stepNumber}.vue: Emitting ready-to-proceed event`)
      emit('ready-to-proceed', {
        step: stepNumber,
        data: { ...formData }
      })
    },

    emitGoBackRequested: () => {
      console.log(`🔙 step${stepNumber}.vue: Emitting go-back-requested event`)
      emit('go-back-requested', { step: stepNumber })
    }
  }
}

// 定義 DomicileStore 類型
interface DomicileStoreType {
  countyOptions: Array<{ title: string; value: number }>
  loadCounties: () => Promise<void | null>
  loadTownsByCountyId: (countyId: number) => Promise<void | null>
  getTownsForCountyId: (countyId: number) => Array<{ title: string; value: number }>
  loadLandSectionsByTownId: (townId: number) => Promise<void | null>
  getLandSectionsForTownId: (townId: number) => Array<{ title: string; value: number }>
  loadVillagesByTownId: (townId: number) => Promise<void | null>
  getVillagesForTownId: (townId: number) => Array<{ title: string; value: number }>
  getTownById: (townId: number) => {
    is_indigenous?: boolean
    indigenous_type?: string
    title?: string
    value?: number
  } | undefined
}

// 創建統一的級聯選擇管理器
const createCascadeSelectManager = (
  formData: Record<string, unknown>,
  domicileStore: DomicileStoreType,
  guard: StepInitializationGuard
): CascadeSelectManager => ({
  loadCascadeData: async () => {
    console.log('🔗 Loading cascade data for address fields...')

    try {
      // 載入設施地址的級聯資料
      if (formData.landCounty) {
        console.log('📍 Loading towns for landCounty:', formData.landCounty)
        await loadTownsForCounty(formData.landCounty as string | number)

        if (formData.landTown) {
          console.log('📍 Loading sections for landTown:', formData.landTown)
          // 檢查是否為特殊城市代碼，如果是則跳過
          const isSpecialCityCode = formData.landTown === 'O01' || formData.landTown === 'I01';
          if (!isSpecialCityCode) {
            await loadLandSections(true); // 保留選擇
          }
        }
      }

      // 載入所有權人地址的級聯資料
      if (formData.ownerCounty) {
        console.log('📍 Loading towns for ownerCounty:', formData.ownerCounty)
        await loadTownsForCounty(formData.ownerCounty as string | number)

        if (formData.ownerTown) {
          console.log('📍 Loading villages for ownerTown:', formData.ownerTown)
          const townId = typeof formData.ownerTown === 'number' ? formData.ownerTown : parseInt(formData.ownerTown as string)
          await domicileStore.loadVillagesByTownId(townId)
        }
      }

      console.log('✅ Cascade data loaded successfully')
    } catch (error) {
      console.error('❌ Failed to load cascade data:', error)
    }
  },

  resetCascadeSelections: (level: 'county' | 'town' | 'village') => {
    // 🔥 修復：防止載入時錯誤清空級聯選擇
    if (guard.isInitializing) {
      console.log('⏸️ resetCascadeSelections blocked during data loading')
      return
    }

    console.log(`🔄 resetCascadeSelections: ${level}`)
    switch (level) {
      case 'county':
        formData.landTown = ''
        formData.landSec = ''
        console.log('  → Cleared landTown and landSec')
        break
      case 'town':
        formData.landSec = ''
        console.log('  → Cleared landSec')
        break
    }
  }
})

// 創建統一的步驟管理器
const createUnifiedStepManager = (
  stepNumber: number,
  emit: ((evt: "step-data-changed", eventData: { step: number; data: Record<string, unknown>; valid: boolean; }) => void) &
        ((evt: "validation-changed", eventData: { step: number; valid: boolean; }) => void) &
        ((evt: "ready-to-proceed", eventData: { step: number; data: Record<string, unknown>; }) => void) &
        ((evt: "go-back-requested", eventData: { step: number; }) => void),
  formData: Record<string, unknown>,
  validationState: Ref<boolean>,
  form: Ref<{ validate: () => Promise<{ valid: boolean }> } | null>,
  domicileStore: DomicileStoreType
): UnifiedStepManager => {
  const guard = createInitializationGuard()
  const eventEmitter = createEventEmitter(stepNumber, emit, formData, validationState, guard)
  const cascadeManager = createCascadeSelectManager(formData, domicileStore, guard)
  const protectedFactory = createProtectedFunctionFactory(guard, eventEmitter)

  return {
    // 基本狀態
    guard,

    // 事件發送器方法
    ...eventEmitter,

    // 級聯選擇管理器方法
    ...cascadeManager,

    // 保護函數工廠方法
    ...protectedFactory,

    // 統一的表單驗證
    validateForm: async (): Promise<boolean> => {
      if (form.value) {
        const { valid } = await (form.value as { validate: () => Promise<{ valid: boolean }> }).validate()
        validationState.value = valid

        // 在初始化期間不發送驗證事件,避免觸發不當的儲存
        if (!guard.isInitializing && guard.isInitialized) {
          eventEmitter.emitValidationChanged(valid)
        } else {
          console.log('⏸️ step2.vue: Skipping validation event emission during initialization')
        }

        return valid
      }
      return true
    },

    // 統一的資料更新
    updateFormData: () => {
      // 在初始化期間不執行更新,避免重置資料庫資料
      if (!guard.isInitialized || guard.isInitializing) {
        console.log('⏸️ step2.vue: Skipping updateFormData during initialization')
        return
      }

      // 發送資料變更事件 (驗證會在validateForm方法中處理)
      eventEmitter.emitDataChanged()
    }
  }
}

// 創建單筆土地初始資料
const createInitialLandData = (id?: string): LandData => ({
  id: id || `land_${Date.now()}_${Math.random().toString(36).substring(2, 9)}`,
  // 設施地段
  landCounty: '',
  landTown: '',
  landSec: '',

  // 地號資訊
  landNumber: '',
  landNumberMain: '',
  landNumberSub: '',

  // 土地特性
  isAboriginalArea: false,
  isIrrigationArea: false,
  isReapplied: false,
  hasAgriculturalCertificate: false,
  certificateYear: '',
  certificateMonth: '',
  certificateDay: '',

  // 坐標資訊
  longitude: '',
  latitude: '',

  // 面積資訊
  landArea: '',
  landAreaHa: '',
  facilityArea: '',
  facilityAreaHa: '',

  // 農地種植作物
  cropCategory: '',
  cropName: '',
  crops: [] as Array<{category: string, name: string}>,

  // 所有權人資料
  ownerName: '',
  ownerId: '',
  ownerCounty: '',
  ownerTown: '',
  ownerVillage: '',
  ownerShare1: '',
  ownerShare2: '',
  ownerArea: '',
  owners: [] as Array<{
    name: string;
    id: string;
    address: string;
    share: string;
    area: string;
  }>
})

// 事件驅動架構：創建初始表單資料函數 (向後相容 + 多筆土地支援)
const createInitialFormData = () => ({
  // 多筆土地資料陣列
  lands: [] as LandData[],

  // 向後相容：保留原有的單筆土地資料結構
  // Facility address section
  landCounty: '',
  landTown: '',
  landSec: '',
  landSecName: '',  // 地段名稱
  landNumber: '',
  landNumberMain: '',
  landNumberSub: '',
  isAboriginalArea: false,
  isIrrigationArea: false,
  isReapplied: false,
  hasAgriculturalCertificate: false,
  certificateYear: '',
  certificateMonth: '',
  certificateDay: '',

  // Land data
  longitude: '',
  latitude: '',
  landArea: '',
  landAreaHa: '',
  facilityArea: '',
  facilityAreaHa: '',

  // Crop data
  cropCategory: '',
  cropName: '',
  crops: [] as Array<{category: string, name: string}>,

  // Owner data
  ownerName: '',
  ownerId: '',
  ownerCounty: '',
  ownerTown: '',
  ownerVillage: '',
  ownerShare1: '',
  ownerShare2: '',
  ownerArea: '',
  owners: [] as Array<{
    name: string,
    id: string,
    address: string,
    share: string,
    area: string
  }>,

  // Always valid for seamless navigation
  valid: true
})

// 事件驅動架構：本地表單資料管理
const localFormData = reactive(createInitialFormData())

// 土地管理狀態
const landManagement = reactive<LandManagementState>({
  currentEditingLandId: null,
  isEditingMode: false,
  showLandEditDialog: false,
  lands: []
})

// 土地管理工具函數
const landUtils = {
  // 生成唯一ID
  generateLandId: (): string => `land_${Date.now()}_${Math.random().toString(36).substring(2, 9)}`,

  // 從當前表單資料創建土地資料
  createLandFromCurrentForm: (): LandData => ({
    id: landUtils.generateLandId(),
    landCounty: localFormData.landCounty,
    landTown: localFormData.landTown,
    landSec: localFormData.landSec,
    landSecName: localFormData.landSecName,
    landNumber: localFormData.landNumber,
    landNumberMain: localFormData.landNumberMain,
    landNumberSub: localFormData.landNumberSub,
    isAboriginalArea: localFormData.isAboriginalArea,
    isIrrigationArea: localFormData.isIrrigationArea,
    isReapplied: localFormData.isReapplied,
    hasAgriculturalCertificate: localFormData.hasAgriculturalCertificate,
    certificateYear: localFormData.certificateYear,
    certificateMonth: localFormData.certificateMonth,
    certificateDay: localFormData.certificateDay,
    longitude: localFormData.longitude,
    latitude: localFormData.latitude,
    landArea: localFormData.landArea,
    landAreaHa: localFormData.landAreaHa,
    facilityArea: localFormData.facilityArea,
    facilityAreaHa: localFormData.facilityAreaHa,
    cropCategory: localFormData.cropCategory,
    cropName: localFormData.cropName,
    crops: [...localFormData.crops],
    ownerName: localFormData.ownerName,
    ownerId: localFormData.ownerId,
    ownerCounty: localFormData.ownerCounty,
    ownerTown: localFormData.ownerTown,
    ownerVillage: localFormData.ownerVillage,
    ownerShare1: localFormData.ownerShare1,
    ownerShare2: localFormData.ownerShare2,
    ownerArea: localFormData.ownerArea,
    owners: [...localFormData.owners]
  }),

  // 🔥 修復：防止載入時觸發級聯重置的土地資料載入
  loadLandToCurrentForm: (land: LandData, skipProtection = false): void => {
    console.log('🔧 loadLandToCurrentForm - Starting land data load...', skipProtection ? '(外層保護)' : '')

    // 暫時標記為載入模式，防止級聯重置（除非外層已經開啟保護）
    const needProtection = !skipProtection && !initGuard.isInitializing
    if (needProtection) {
      initGuard.isInitializing = true
      isLandNumberUpdateProgrammatic.value = true
      console.log('🔒 loadLandToCurrentForm - 開啟載入保護')
    } else {
      console.log('⏭️ loadLandToCurrentForm - 跳過保護（外層已管理）')
    }

    try {
      // 確保資料類型正確轉換
      Object.assign(localFormData, {
        landCounty: typeof land.landCounty === 'string' ? parseInt(land.landCounty) || land.landCounty : land.landCounty,
        landTown: typeof land.landTown === 'string' ? parseInt(land.landTown) || land.landTown : land.landTown,
        landSec: typeof land.landSec === 'string' ? parseInt(land.landSec) || land.landSec : land.landSec,
        landSecName: land.landSecName || '',
        landNumber: land.landNumber,
        landNumberMain: land.landNumberMain,
        landNumberSub: land.landNumberSub,
        isAboriginalArea: land.isAboriginalArea,
        isIrrigationArea: land.isIrrigationArea,
        isReapplied: land.isReapplied,
        hasAgriculturalCertificate: land.hasAgriculturalCertificate,
        certificateYear: land.certificateYear,
        certificateMonth: land.certificateMonth,
        certificateDay: land.certificateDay,
        longitude: land.longitude,
        latitude: land.latitude,
        landArea: land.landArea,
        landAreaHa: land.landAreaHa,
        facilityArea: land.facilityArea,
        facilityAreaHa: land.facilityAreaHa,
        cropCategory: land.cropCategory,
        cropName: land.cropName,
        crops: [...land.crops],
        ownerName: land.ownerName,
        ownerId: land.ownerId,
        ownerCounty: typeof land.ownerCounty === 'string' ? parseInt(land.ownerCounty) || land.ownerCounty : land.ownerCounty,
        ownerTown: typeof land.ownerTown === 'string' ? parseInt(land.ownerTown) || land.ownerTown : land.ownerTown,
        ownerVillage: typeof land.ownerVillage === 'string' ? parseInt(land.ownerVillage) || land.ownerVillage : land.ownerVillage,
        ownerShare1: land.ownerShare1,
        ownerShare2: land.ownerShare2,
        ownerArea: land.ownerArea,
        owners: [...land.owners]
      })

      // Update previous values for tracking
      previousLandNumberMain.value = land.landNumberMain || '';
      previousLandNumberSub.value = land.landNumberSub || '';

      console.log('🔧 loadLandToCurrentForm - Data loaded:')
      console.log('  landCounty:', localFormData.landCounty, typeof localFormData.landCounty)
      console.log('  landTown:', localFormData.landTown, typeof localFormData.landTown)
      console.log('  landSec:', localFormData.landSec, typeof localFormData.landSec)
      console.log('  landNumberMain:', localFormData.landNumberMain)
      console.log('  landNumberSub:', localFormData.landNumberSub)

    } finally {
      // 使用 nextTick 確保 Vue 響應性更新完成後再開啟級聯重置（僅當由此函數開啟保護時）
      if (needProtection) {
        nextTick(() => {
          initGuard.isInitializing = false
          isLandNumberUpdateProgrammatic.value = false
          console.log('✅ loadLandToCurrentForm - 載入保護已關閉')
        })
      }
    }
  },


  clearCurrentForm: (): void => {
    const initialData = createInitialLandData()

    // 創建一個不包含 id 的初始資料副本
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    const { id: _id, ...dataWithoutId } = initialData

    // 使用 Object.assign 合併，保留現有的 id
    Object.assign(localFormData, dataWithoutId)
  },

  // 獲取土地摘要資訊
  getLandSummary: (land: LandData): string => {
    const location = [land.landCounty, land.landTown, land.landSec].filter(Boolean).join('')
    const landNumber = land.landNumber || '未設定'
    const area = land.facilityArea ? `${land.facilityArea}m²` : '未設定'
    return `${location} ${landNumber} (${area})`
  }
}

// 實例化統一的步驟管理器
const stepManager = createUnifiedStepManager(2, emit, localFormData, localValid, form, domicileStore)

// 為了向後相容，保留原有的引用
const initGuard = stepManager.guard
const eventEmitter = stepManager
const cascadeManager = stepManager

// Dialog state
const landInfoDialog = ref(false);
const landInfo = reactive({
  subsidyInfo: '',
  county: '',
  section: '',
  number: '',
  managementOffice: '',
  workstation: '',
  irrigationDistrictInfo: [] as any[], // 儲存完整的事業區階層資訊陣列
  specialLand: false
});

// Feature info state
const featureInfoVisible = ref(false);
const selectedFeatureInfo = ref<SelectedFeatureInfo>({});

// 🆕 無地段圖資提示 overlay 狀態
const noSectionDataOverlay = ref(false);

// 🆕 查無地號提示 alert 狀態
const landParcelNotFoundAlert = ref(false);
const landParcelNotFoundMessage = ref('');

// Variables to track interactions with proper types
let select: Select | null = null;
let modify: Modify | null = null;
let selectedFeatureKey: EventsKey | null = null;
let modifyFeatureKey: EventsKey | null = null;

// Address data
const counties = computed(() => {
  return domicileStore.countyOptions.map(county => ({
    title: county.title,
    value: county.value
  }));
});

// 🆕 顯示縣市名稱（處理代碼轉換）
const displayCountyName = computed(() => {
  const countyValue = landInfo.county;

  // 如果為空或未定義，返回 '-'
  if (!countyValue) return '-';

  // 如果是數字或數字字串，嘗試從 counties 中查找對應名稱
  const numericValue = typeof countyValue === 'number'
    ? countyValue
    : (typeof countyValue === 'string' && !isNaN(Number(countyValue)) ? Number(countyValue) : null);

  if (numericValue !== null) {
    const found = counties.value.find(c => c.value === numericValue);
    return found ? found.title : '-';
  }

  // 如果已經是文字名稱，直接返回
  return countyValue;
});

// Load towns and villages for a county when it's selected
const loadTownsForCounty = async (countyValue: number | string) => {
  if (typeof countyValue === 'number') {
    await domicileStore.loadTownsByCountyId(countyValue);
  } else if (typeof countyValue === 'string' && !isNaN(parseInt(countyValue))) {
    await domicileStore.loadTownsByCountyId(parseInt(countyValue));
  }
};

// 已移除 loadVillagesForTown 函數，改用 loadLandSections 處理 NLSC API

// Crop data
const cropCategoriesData = {
  '糧食作物': ['稻米', '小麥', '玉米', '大豆'],
  '特用作物': ['茶葉', '咖啡', '香蕉'],
  '果樹作物': ['橘', '香蕉', '芒果', '鳳梨'],
  '蔬菜作物': ['番茄', '青椒', '茄子', '胡蘿蔔'],
  '景觀花卉作物': ['玫瑰', '百合', '康乃馨'],
  '其他作物': ['其他']
};

const cropCategories = Object.keys(cropCategoriesData);

// Computed properties for reactive filtering
const towns = computed(() => {
  if (!localFormData.landCounty) return [];

  const countyId = typeof localFormData.landCounty === 'number'
    ? localFormData.landCounty
    : parseInt(localFormData.landCounty);
  const county = domicileStore.countyOptions.find(c => c.value === countyId);

  // 如果是特殊城市，返回對應的單一選項
  if (county && isSpecialCity.value) {
    const cityInfo = specialCities[county.title];
    return cityInfo ? [{
      title: cityInfo.name,
      value: cityInfo.code,
      code: cityInfo.code
    }] : [];
  }

  // 一般縣市返回正常的鄉鎮清單
  return domicileStore.getTownsForCountyId(countyId);
});

// 動態獲取地段選項 - 使用 NLSC API 原始格式，優化搜尋支援
const sections = computed(() => {
  const result = nlscSections.value
    .map(section => ({
      // title 包含地段名稱和代碼，供 v-autocomplete 預設搜尋使用
      title: `${section.name} ${section.code || ''}`,
      displayName: section.name,  // 純地段名稱，供顯示使用
      value: section.code,        // 實際存儲的值，使用 API 原始格式
      code: section.code,         // 保持 API 原始格式（如 "0446"）
      name: section.name,         // 保留名稱
      office: section.office
    }))
    .sort((a, b) => {
      // 優先按地段代碼排序，如果沒有代碼則按名稱排序
      if (a.code && b.code) {
        return a.code.localeCompare(b.code);
      }
      return a.name.localeCompare(b.name);
    });

  // Debug: 檢查資料結構
  if (result.length > 0) {
    console.log('🔍 sections 資料結構範例:', result[0]);
    console.log('🔍 預設搜尋將搜尋 title 欄位:', result[0].title);
  }

  return result;
});

// 當前選中的地段資訊 - 智能匹配
const currentSelectedSection = computed(() => {
  const currentCode = localFormData.landSec;
  if (!currentCode || sections.value.length === 0) return null;

  const currentCodeStr = currentCode.toString();

  console.log('🔍 尋找地段匹配:', {
    currentCode,
    currentCodeStr,
    currentCodeType: typeof currentCode,
    sectionsCount: sections.value.length,
    firstFewSections: sections.value.slice(0, 3).map(s => ({ code: s.code, name: s.name }))
  });

  // 嘗試多種匹配方式以處理歷史資料
  const found = sections.value.find(s => {
    // 直接匹配
    if (s.code === currentCode || s.code === currentCodeStr) {
      return true;
    }

    // 數值匹配（處理 446 vs "0446" 的情況）
    try {
      return parseInt(s.code) === parseInt(currentCodeStr);
    } catch {
      return false;
    }
  });

  console.log('🎯 匹配結果:', found ? { code: found.code, name: found.name } : '未找到');
  return found || null;
});

// 地段搜尋事件處理函數
const onSectionSearchUpdate = (searchValue: string) => {
  sectionSearchText.value = searchValue;
};

// 地段選單失焦事件處理函數
const onSectionBlur = () => {
  // 當失焦時清空搜尋文字，避免影響下次搜尋
  sectionSearchText.value = '';
};

// 地段選擇變更事件處理函數 - 同時儲存代碼和名稱
const onSectionChange = (sectionCode: string | number) => {
  if (sectionCode) {
    // 從 sections 資料中找到對應的地段資訊
    const selectedSection = sections.value.find(s => s.code === sectionCode || s.value === sectionCode);
    if (selectedSection) {
      // 同時儲存地段名稱
      localFormData.landSecName = selectedSection.displayName || selectedSection.name;
      // console.log('🏷️ 地段選擇:', { code: sectionCode, name: localFormData.landSecName });
    }
  } else {
    // 清空時也清空名稱
    localFormData.landSecName = '';
  }
};

// 特殊城市配置 - 與 qualification/index.vue 保持一致
const specialCities: Record<string, { code: string; name: string }> = {
  '新竹市': { code: 'O01', name: '新竹市' },
  '嘉義市': { code: 'I01', name: '嘉義市' }
};

// 檢查是否為特殊城市
const isSpecialCity = computed(() => {
  if (!localFormData.landCounty) return false;
  const countyId = typeof localFormData.landCounty === 'number'
    ? localFormData.landCounty
    : parseInt(localFormData.landCounty);
  const county = domicileStore.countyOptions.find(c => c.value === countyId);
  return county ? specialCities.hasOwnProperty(county.title) : false;
});

// 取得特殊城市的顯示文字
const getSpecialCityDisplayText = (): string => {
  if (!localFormData.landCounty) return '';
  const countyId = typeof localFormData.landCounty === 'number'
    ? localFormData.landCounty
    : parseInt(localFormData.landCounty);
  const county = domicileStore.countyOptions.find(c => c.value === countyId);
  if (!county) return '';
  const cityInfo = specialCities[county.title];
  return cityInfo ? cityInfo.name : '';
};

// 保留原本的 villages 計算屬性供其他功能使用
const villages = computed(() => {
  if (!localFormData.landTown) return [];
  const townId = typeof localFormData.landTown === 'number'
    ? localFormData.landTown
    : parseInt(localFormData.landTown);
  return domicileStore.getLandSectionsForTownId(townId);
});

const ownerTowns = computed(() => {
  if (!localFormData.ownerCounty) return [];
  const countyId = typeof localFormData.ownerCounty === 'number'
    ? localFormData.ownerCounty
    : parseInt(localFormData.ownerCounty);
  return domicileStore.getTownsForCountyId(countyId);
});

const ownerVillages = computed(() => {
  if (!localFormData.ownerTown) return [];
  const townId = typeof localFormData.ownerTown === 'number'
    ? localFormData.ownerTown
    : parseInt(localFormData.ownerTown);
  return domicileStore.getVillagesForTownId(townId);
});

const crops = computed(() => {
  return localFormData.cropCategory ? (cropCategoriesData[localFormData.cropCategory as keyof typeof cropCategoriesData] || []) : [];
});

const currentShare = computed(() => {
  if (!localFormData.ownerShare1 || !localFormData.ownerShare2) return 0;

  const share1 = parseFloat(localFormData.ownerShare1);
  const share2 = parseFloat(localFormData.ownerShare2);

  return (!isNaN(share1) && !isNaN(share2) && share2 !== 0) ? (share1 / share2) : 0;
});

const shareExceedsLimit = computed(() => {
  const totalShareWithNew = calculateTotalShare() + currentShare.value;
  return totalShareWithNew > 1;
});

const canAddOwner = computed(() => {
  return !!localFormData.ownerName &&
         !!localFormData.ownerId &&
         !!localFormData.ownerShare1 &&
         !!localFormData.ownerShare2 &&
         !!localFormData.ownerArea &&
         !shareExceedsLimit.value;
});

const landNumberMainFocused = ref(false);
const landNumberSubFocused = ref(false);

// NLSC 地段資料
const nlscSections = ref<LandSection[]>([]);
const loadingSections = ref(false);
// 地段搜尋文字
const sectionSearchText = ref('');

// 用於強制重新渲染地段選單的 key
const sectionSelectKey = ref(0);
const showDatePicker = ref(false);

// 證明書日期格式化計算屬性
const certificateDateFormatted = computed(() => {
  if (!localFormData.certificateYear || !localFormData.certificateMonth || !localFormData.certificateDay) {
    return '';
  }
  return `民國${localFormData.certificateYear}年${localFormData.certificateMonth}月${localFormData.certificateDay}日`;
});

// 年份選項（民國年）
const yearOptions = computed(() => {
  const currentYear = new Date().getFullYear() - 1911; // 轉換為民國年
  const years = [];
  // 從民國90年到目前年份
  for (let i = 90; i <= currentYear; i++) {
    years.push({
      title: `民國 ${i} 年`,
      value: i.toString()
    });
  }
  return years.reverse(); // 最新年份在前
});

// 月份選項
const monthOptions = computed(() => {
  return Array.from({ length: 12 }, (_, i) => ({
    title: `${i + 1} 月`,
    value: (i + 1).toString()
  }));
});

// 日期選項（根據選擇的年月動態計算）
const dayOptions = computed(() => {
  if (!localFormData.certificateYear || !localFormData.certificateMonth) {
    return [];
  }

  const year = parseInt(localFormData.certificateYear) + 1911; // 轉換為西元年
  const month = parseInt(localFormData.certificateMonth);
  const daysInMonth = new Date(year, month, 0).getDate();

  return Array.from({ length: daysInMonth }, (_, i) => ({
    title: `${i + 1} 日`,
    value: (i + 1).toString()
  }));
});

// Event handlers
// Formatted land number with 4 digits (main)
// Flag to track if land number changes are programmatic (not user input)
const isLandNumberUpdateProgrammatic = ref(false);

// Watch direct changes to landNumberMain and landNumberSub
watch(() => localFormData.landNumberMain, (newValue, oldValue) => {
  if (oldValue !== newValue && oldValue !== undefined && !isLandNumberUpdateProgrammatic.value) {
    clearLocationAndAreaInfo();
  }

  // Update tracked previous value
  if (!isLandNumberUpdateProgrammatic.value) {
    previousLandNumberMain.value = newValue;
  }
});

watch(() => localFormData.landNumberSub, (newValue, oldValue) => {
  if (oldValue !== newValue && oldValue !== undefined && !isLandNumberUpdateProgrammatic.value) {
    clearLocationAndAreaInfo();
  }

  // Update tracked previous value
  if (!isLandNumberUpdateProgrammatic.value) {
    previousLandNumberSub.value = newValue;
  }
});

// Function to clear coordinate and area information when land number is manually changed
const clearLocationAndAreaInfo = () => {
  localFormData.longitude = '';
  localFormData.latitude = '';
  localFormData.landArea = '';
  localFormData.landAreaHa = '';
  localFormData.facilityArea = '';
  localFormData.facilityAreaHa = '';
  localFormData.isIrrigationArea = false;
};

// 🆕 當設施地段（縣市/鄉鎮/地段）變更時，重置相關資訊
const resetLandRelatedInfo = () => {
  // 重置地號資訊
  localFormData.landNumberMain = '';
  localFormData.landNumberSub = '';

  // 重置坐標資訊
  localFormData.longitude = '';
  localFormData.latitude = '';

  // 重置面積資訊
  localFormData.landArea = '';
  localFormData.landAreaHa = '';
  localFormData.facilityArea = '';
  localFormData.facilityAreaHa = '';
  localFormData.isIrrigationArea = false;

  // 重置農地種植作物
  localFormData.cropCategory = '';
  localFormData.cropName = '';

  console.log('🔄 已重置地號、坐標、面積、作物資訊');
};

// Previous values to track manual changes
const previousLandNumberMain = ref(localFormData.landNumberMain);
const previousLandNumberSub = ref(localFormData.landNumberSub);

// Input handlers for manual land number changes (backup mechanism)
const onLandNumberMainInput = () => {
  if (!isLandNumberUpdateProgrammatic.value) {
    // Use setTimeout to ensure the v-model has been updated
    setTimeout(() => {
      if (previousLandNumberMain.value !== localFormData.landNumberMain) {
        clearLocationAndAreaInfo();
        previousLandNumberMain.value = localFormData.landNumberMain;
      }
    }, 0);
  }
};

const onLandNumberSubInput = () => {
  if (!isLandNumberUpdateProgrammatic.value) {
    // Use setTimeout to ensure the v-model has been updated
    setTimeout(() => {
      if (previousLandNumberSub.value !== localFormData.landNumberSub) {
        clearLocationAndAreaInfo();
        previousLandNumberSub.value = localFormData.landNumberSub;
      }
    }, 0);
  }
};

const formattedLandNumberMain = computed({
  get: () => {
    // When focused, show the raw value
    if (landNumberMainFocused.value) {
      return localFormData.landNumberMain
    }
    // Format with leading zeros when displaying
    if (!localFormData.landNumberMain) return ''
    return localFormData.landNumberMain.toString().padStart(4, '0')
  },
  set: (val) => {
    const previousValue = localFormData.landNumberMain;
    // Store numeric value (remove leading zeros)
    const newValue = val ? val.replace(/^0+/, '') || '0' : '';
    localFormData.landNumberMain = newValue;

    // Clear coordinate and area info if the value actually changed and it's a manual user input
    if (previousValue !== newValue && !isLandNumberUpdateProgrammatic.value) {
      clearLocationAndAreaInfo();
    }

    updateLandNumber()
  }
});

// Formatted land number with 4 digits (sub)
const formattedLandNumberSub = computed({
  get: () => {
    if (landNumberSubFocused.value) {
      return localFormData.landNumberSub;
    }
    if (!localFormData.landNumberSub) return '';
    return localFormData.landNumberSub.toString().padStart(4, '0');
  },
  set: (val) => {
    const previousValue = localFormData.landNumberSub;
    // Store numeric value (remove leading zeros)
    const newValue = val ? val.replace(/^0+/, '') || '0' : '';
    localFormData.landNumberSub = newValue;

    // Clear coordinate and area info if the value actually changed and it's a manual user input
    if (previousValue !== newValue && !isLandNumberUpdateProgrammatic.value) {
      clearLocationAndAreaInfo();
    }

    updateLandNumber();
  }
});

const landAreaHaComputed = computed({
  get: () => {
    if (!localFormData.landArea) return '';
    const area = parseFloat(localFormData.landArea);
    return !isNaN(area) ? (area / 10000).toString() : '';
  },
  set: (val) => {
    if (val) {
      const haArea = parseFloat(val);
      if (!isNaN(haArea)) {
        // 更新公頃值
        localFormData.landAreaHa = val;
      }
    } else {
      localFormData.landAreaHa = '';
    }
  }
});

const facilityAreaHaComputed = computed({
  get: () => {
    if (!localFormData.facilityArea) return '';
    const area = parseFloat(localFormData.facilityArea);
    return !isNaN(area) ? (area / 10000).toString() : '';
  },
  set: (val) => {
    if (val) {
      const haArea = parseFloat(val);
      if (!isNaN(haArea)) {
        // 更新公頃值
        localFormData.facilityAreaHa = val;
      }
    } else {
      localFormData.facilityAreaHa = '';
    }
  }
});

const ownerAreaComputed = computed({
  get: () => {
    if (!localFormData.landArea || !localFormData.ownerShare1 || !localFormData.ownerShare2) {
      return '';
    }

    const landArea = parseFloat(localFormData.landArea);
    const share1 = parseFloat(localFormData.ownerShare1);
    const share2 = parseFloat(localFormData.ownerShare2);

    if (!isNaN(landArea) && !isNaN(share1) && !isNaN(share2) && share2 !== 0) {
      const calculatedValue = ((landArea * share1) / share2).toFixed(1);
      // 在 getter 中同步更新 localFormData.ownerArea
      localFormData.ownerArea = calculatedValue;
      return calculatedValue;
    }

    localFormData.ownerArea = '';
    return '';
  },
  set: (val) => {
    localFormData.ownerArea = val;
  }
});

// 多筆土地計算屬性
const totalFacilityArea = computed(() => {
  return landManagement.lands.reduce((total, land) => {
    const area = parseFloat(land.facilityArea || '0')
    return total + (isNaN(area) ? 0 : area)
  }, 0)
})

const totalFacilityAreaHa = computed(() => {
  return totalFacilityArea.value / 10000
})

// 土地資料展示工具函數
const getLandLocationText = (land: LandData): string => {
  const parts = []

  // 縣市
  let countyName = ''
  if (land.landCounty) {
    if (typeof land.landCounty === 'number') {
      const county = counties.value.find(c => c.value === land.landCounty)
      if (county) {
        countyName = county.title
        parts.push(county.title)
      }
    } else {
      countyName = land.landCounty
      parts.push(land.landCounty)
    }
  }

  // 特殊城市配置 - 與其他地方保持一致
  const specialCities = ['新竹市', '嘉義市']

  // 鄉鎮 - 特殊城市跳過鄉鎮市區顯示
  if (land.landTown && !specialCities.includes(countyName)) {
    if (typeof land.landTown === 'number') {
      const town = domicileStore.getTownsForCountyId(land.landCounty as number)
        .find(t => t.value === land.landTown)
      if (town) parts.push(town.title)
    } else {
      // 對於字串值，只有不是特殊城市代碼才顯示
      if (land.landTown !== 'O01' && land.landTown !== 'I01') {
        parts.push(land.landTown)
      }
    }
  }

  // 地段 - 優先使用儲存的地段名稱，提高效能和可靠性
  if (land.landSec) {
    // 第一優先：使用已儲存的地段名稱
    if (land.landSecName) {
      parts.push(land.landSecName)
    } else {
      // 第二優先：從 NLSC sections 資料中查找地段名稱
      const section = sections.value.find(s => s.code === land.landSec || s.value === land.landSec)
      if (section) {
        parts.push(section.displayName || section.name)
      } else {
        // 第三優先：回退到 domicileStore 查找（向後相容）
        if (typeof land.landSec === 'number') {
          const legacySection = domicileStore.getLandSectionsForTownId(land.landTown as number)
            .find(s => s.value === land.landSec)
          if (legacySection) parts.push(legacySection.title)
        } else {
          // 如果是字串代碼，嘗試從 NLSC 資料中找到對應名稱
          const nlscSection = sections.value.find(s => s.code === land.landSec)
          if (nlscSection) {
            parts.push(nlscSection.displayName || nlscSection.name)
          } else {
            // 最後回退：直接顯示代碼（不理想但確保有內容顯示）
            parts.push(land.landSec)
          }
        }
      }
    }
  }

  return parts.length > 0 ? parts.join('') : '未設定位置'
}

// 動態計算並顯示地號的函數
const getLandNumber = (land: LandData): string => {
  // 優先使用 landNumber，如果沒有則從 landNumberMain 和 landNumberSub 計算
  if (land.landNumber) {
    return land.landNumber
  }

  if (land.landNumberMain) {
    return land.landNumberSub
      ? `${land.landNumberMain}-${land.landNumberSub}`
      : land.landNumberMain
  }

  return '未設定'
}


// 使用統一的保護函數工廠重構事件處理函數
const updateLandNumber = stepManager.createProtectedHandler(() => {
  if (localFormData.landNumberMain) {
    localFormData.landNumber = localFormData.landNumberSub
      ? `${localFormData.landNumberMain}-${localFormData.landNumberSub}`
      : localFormData.landNumberMain;
  } else {
    localFormData.landNumber = '';
  }
});

const onCountyChange = stepManager.createCascadeHandler(async () => {
  cascadeManager.resetCascadeSelections('county');

  // 重置地段選擇和資料
  localFormData.landSec = '';
  localFormData.landSecName = '';
  nlscSections.value = [];

  // 強制重新渲染地段選單
  sectionSelectKey.value++;

  if (localFormData.landCounty) {
    const countyId = typeof localFormData.landCounty === 'number'
      ? localFormData.landCounty
      : parseInt(localFormData.landCounty);
    const county = domicileStore.countyOptions.find(c => c.value === countyId);

    if (county) {
      await domicileStore.loadTownsByCountyId(county.value);

      // 如果是特殊城市，自動設定對應的鄉鎮代碼並載入地段資料
      if (specialCities[county.title] && county.land_code) {
        console.log(`檢測到特殊城市 ${county.title}，自動設定鄉鎮代碼並載入地段資料`);
        const specialCode = specialCities[county.title].code;
        // 設定對應的鄉鎮代碼
        localFormData.landTown = specialCode;
        loadingSections.value = true;
        try {
          nlscSections.value = await fetchLandSectionsByLandCodes(county.land_code, specialCode);
          console.log(`已自動載入 ${county.title} 的地段資料 (${specialCode}):`, nlscSections.value.length);
        } catch (error) {
          console.error('Failed to load land sections for special city:', error);
          nlscSections.value = [];
        } finally {
          loadingSections.value = false;
        }
      } else {
        // 一般縣市清空town選擇
        localFormData.landTown = '';
      }
    }
  }
});

// 載入 NLSC 地段資料的函數
const loadLandSections = async (preserveSelection = false) => {
  // 保存當前的地段選擇（如果需要保留）
  const currentSelection = preserveSelection ? localFormData.landSec : '';

  // 重置地段選擇和資料（除非要保留選擇）
  if (!preserveSelection) {
    localFormData.landSec = '';
  }
  nlscSections.value = [];

  // 強制重新渲染地段選單
  sectionSelectKey.value++;

  // 使用 nextTick 確保重置生效
  await nextTick();

  if (!localFormData.landCounty || !localFormData.landTown) {
    console.log('缺少縣市或鄉鎮資料，跳過地段載入');
    return;
  }

  // 取得縣市資料 - 在 step2 中 landCounty 是 ID
  const countyId = typeof localFormData.landCounty === 'number'
    ? localFormData.landCounty
    : parseInt(localFormData.landCounty);
  const county = domicileStore.countyOptions.find(c => c.value === countyId);

  if (!county || !county.land_code) {
    console.log('找不到縣市資料或缺少地政代碼');
    return;
  }

  // 特殊城市處理 - 使用縣市名稱判斷，與全域配置保持一致
  const specialCityCodes: Record<string, string> = {
    '新竹市': 'O01',
    '嘉義市': 'I01'
  };

  try {
    loadingSections.value = true;

    if (specialCityCodes[county.title]) {
      // 特殊城市，直接使用縣市的 land_code 和特殊代碼
      const specialCode = specialCityCodes[county.title];
      console.log(`開始載入特殊城市地段資料: ${county.title} (${county.land_code}/${specialCode})`);
      nlscSections.value = await fetchLandSectionsByLandCodes(county.land_code, specialCode);
      console.log(`載入 ${county.title} 的地段資料 (${specialCode}):`, nlscSections.value.length);
    } else {
      // 一般鄉鎮，取得鄉鎮資料 - 在 step2 中 landTown 是 ID
      const townId = typeof localFormData.landTown === 'number'
        ? localFormData.landTown
        : parseInt(localFormData.landTown);
      const town = domicileStore.getTownsForCountyId(countyId).find(t => t.value === townId);

      if (!town || !town.land_code) {
        console.log('找不到鄉鎮資料或缺少地政代碼');
        return;
      }

      // 一般鄉鎮，使用縣市和鄉鎮的 land_code
      console.log(`開始載入地段資料: ${county.title} ${town.title} (${county.land_code}/${town.land_code})`);
      nlscSections.value = await fetchLandSectionsByLandCodes(county.land_code, town.land_code);
      console.log(`載入 ${county.title} ${town.title} 的地段資料 (${town.land_code}):`, nlscSections.value.length);
    }
  } catch (error) {
    console.error('Failed to load land sections:', error);
    nlscSections.value = [];
  } finally {
    loadingSections.value = false;

    // 如果要保留選擇且有資料載入成功，恢復原本的選擇
    if (preserveSelection && currentSelection && nlscSections.value.length > 0) {
      // 嘗試在新載入的 sections 中找到匹配的項目
      const matchingSection = nlscSections.value.find(section => {
        // 數值匹配（舊格式 446 vs 新格式 "0446"）
        return parseInt(section.code) === parseInt(currentSelection.toString());
      });

      if (matchingSection) {
        // 使用找到的項目的原始代碼格式
        localFormData.landSec = matchingSection.code;
        console.log('🔄 恢復地段選擇:', {
          original: currentSelection,
          matched: matchingSection.code,
          name: matchingSection.name
        });
      } else {
        // 如果找不到匹配項，保持原始選擇
        localFormData.landSec = currentSelection;
        console.log('⚠️ 無法找到匹配的地段，保持原始選擇:', currentSelection);
      }
    }
  }
};

const onTownChange = stepManager.createCascadeHandler(async () => {
  cascadeManager.resetCascadeSelections('town');

  // 載入 NLSC 地段資料
  await loadLandSections();
});

const onOwnerCountyChange = stepManager.createProtectedHandler(() => {
  localFormData.ownerTown = '';
  localFormData.ownerVillage = '';
});

const onOwnerTownChange = stepManager.createProtectedHandler(() => {
  localFormData.ownerVillage = '';
});

const onCropCategoryChange = stepManager.createProtectedHandler(() => {
  localFormData.cropName = '';
});

// Add and remove crops
const addCrop = stepManager.createProtectedHandler(() => {
  if (localFormData.cropCategory && localFormData.cropName) {
    const crop = {
      category: localFormData.cropCategory,
      name: localFormData.cropName
    };

    // Check if already exists
    const exists = localFormData.crops.some(c =>
      c.category === crop.category && c.name === crop.name
    );

    if (!exists) {
      // Ensure crops array exists
      if (!localFormData.crops) {
        localFormData.crops = [];
      }

      localFormData.crops.push(crop);
      // Clear selection
      localFormData.cropName = '';
    }
  }
});

const removeCrop = stepManager.createProtectedHandler((...args: unknown[]) => {
  const index = args[0] as number;
  localFormData.crops.splice(index, 1);
});

// Date picker methods
const confirmDate = stepManager.createProtectedHandler(() => {
  showDatePicker.value = false;
});

const calculateTotalShare = () => {
  let totalShare = 0;

  if (localFormData.owners && localFormData.owners.length > 0) {
    localFormData.owners.forEach(owner => {
      const shareParts = owner.share.split('/');
      if (shareParts.length === 2) {
        const numerator = parseFloat(shareParts[0]);
        const denominator = parseFloat(shareParts[1]);

        if (!isNaN(numerator) && !isNaN(denominator) && denominator !== 0) {
          totalShare += numerator / denominator;
        }
      }
    });
  }

  return totalShare;
};

// Get area source display text
const getAreaSourceDisplay = (featureInfo: any) => {
  if (!featureInfo || !featureInfo.areaSource) {
    return '未知';
  }

  switch (featureInfo.areaSource) {
    case 'cadastral':
      return '地籍登記面積 (Desc_area)';
    case 'survey':
      return '測量面積 (Map_area)';
    case 'calculated':
      return '地圖幾何計算';
    default:
      return '未知';
  }
};

// Add and remove owners - 使用保護函數工廠
const addOwner = stepManager.createProtectedHandler(() => {
  if (localFormData.ownerName && localFormData.ownerId &&
      localFormData.ownerShare1 && localFormData.ownerShare2) {

    const ownerArea = ownerAreaComputed.value;

    const ownerAddress = [
      localFormData.ownerCounty,
      localFormData.ownerTown,
      localFormData.ownerVillage
    ].filter(Boolean).join('');

    const owner = {
      name: localFormData.ownerName,
      id: localFormData.ownerId,
      address: ownerAddress || 'XX',
      share: `${localFormData.ownerShare1}/${localFormData.ownerShare2}`,
      area: ownerArea
    };

    // Ensure owners array exists
    if (!localFormData.owners) {
      localFormData.owners = [];
    }

    localFormData.owners.push(owner);

    // Clear input fields but keep address
    localFormData.ownerName = '';
    localFormData.ownerId = '';
    localFormData.ownerShare1 = '';
    localFormData.ownerShare2 = '';
    localFormData.ownerArea = '';
  }
});

const removeOwner = stepManager.createProtectedHandler((...args: unknown[]) => {
  const index = args[0] as number;
  localFormData.owners.splice(index, 1);
});

// Collapse co-owner settings
const collapseCoOwnerSettings = () => {
  showCoOwnerSettings.value = false;
  // Clear input fields when collapsing
  localFormData.ownerName = '';
  localFormData.ownerId = '';
  localFormData.ownerCounty = '';
  localFormData.ownerTown = '';
  localFormData.ownerVillage = '';
  localFormData.ownerShare1 = '';
  localFormData.ownerShare2 = '';
  localFormData.ownerArea = '';
};

// 事件驅動架構：統一的資料變更處理 (使用統一管理器)
const updateFormData = stepManager.updateFormData;

// 事件驅動架構:表單驗證 (使用統一管理器)
const validateForm = stepManager.validateForm;

// 事件驅動架構:處理下一步請求
const handleProceedToNext = async () => {
  console.log('🎯 step2.vue: handleProceedToNext called');

  const isValid = await validateForm();
  if (isValid) {
    console.log('✅ step2.vue: Form is valid, emitting ready-to-proceed');
    eventEmitter.emitReadyToProceed();
  } else {
    console.log('❌ step2.vue: Form validation failed');
  }
};

// 事件驅動架構:處理返回請求
const handleGoBack = () => {
  console.log('🔙 step2.vue: handleGoBack called');
  eventEmitter.emitGoBackRequested();
};

// 多筆土地管理功能
const addNewLand = () => {
  console.log('🏞️ step2.vue: Adding new land')

  // 清空當前表單
  landUtils.clearCurrentForm()

  // 設置為新增模式
  landManagement.currentEditingLandId = null
  landManagement.isEditingMode = true // 這裡會觸發 watch，自動發送事件

  console.log('✅ step2.vue: Ready for new land input')
}

const editLand = async (landId: string) => {
  console.log('✏️ step2.vue: Editing land:', landId)

  const land = landManagement.lands.find(l => l.id === landId)
  if (!land) {
    console.error('❌ step2.vue: Land not found:', landId)
    return
  }

  // 🆕 開啟載入保護，防止 watch 誤觸發重置
  initGuard.isInitializing = true
  isLandNumberUpdateProgrammatic.value = true

  try {
    // 🔥 P0 修復：載入該土地的級聯資料
    console.log('🔗 Loading cascade data for editing land...')
    try {
      await preloadCascadeDataForLands([land])
      console.log('✅ Cascade data loaded for editing')
    } catch (error) {
      console.warn('⚠️ Failed to load cascade data for editing:', error)
    }

    // 載入土地資料到當前表單（修復後的版本包含類型轉換）
    // 注意：傳入 true 跳過內部保護，因為我們在外層統一管理
    landUtils.loadLandToCurrentForm(land, true)

    // 如果該土地有地段資料，載入對應的 NLSC 地段選項
    if (land.landCounty && land.landTown && land.landSec) {
      console.log('🎯 載入編輯土地的地段資料:', {
        county: land.landCounty,
        town: land.landTown,
        section: land.landSec
      });

      try {
        // 等待一下確保表單資料已載入
        await nextTick();
        await loadLandSections(true); // 保留現有的地段選擇
        console.log('✅ 編輯模式地段資料載入完成');
      } catch (error) {
        console.warn('⚠️ 編輯模式地段資料載入失敗:', error);
      }
    }

    // 設置為編輯模式
    landManagement.currentEditingLandId = landId
    landManagement.isEditingMode = true

    console.log('✅ step2.vue: Land loaded for editing')
  } finally {
    // 🆕 所有載入完成後才關閉保護
    await nextTick()
    initGuard.isInitializing = false
    isLandNumberUpdateProgrammatic.value = false
    console.log('✅ editLand - 載入保護已關閉')
  }
}

const saveLandEdit = () => {
  console.log('💾 step2.vue: Saving land edit')

  // 創建土地資料
  const landData = landUtils.createLandFromCurrentForm()

  if (landManagement.currentEditingLandId) {
    // 更新現有土地
    const index = landManagement.lands.findIndex(l => l.id === landManagement.currentEditingLandId)
    if (index !== -1) {
      landData.id = landManagement.currentEditingLandId
      landManagement.lands[index] = landData
      console.log('✅ step2.vue: Land updated successfully')
    }
  } else {
    // 新增土地
    landManagement.lands.push(landData)
    console.log('✅ step2.vue: New land added successfully')
  }

  // 退出編輯模式（會自動觸發導航狀態更新）
  cancelLandEdit()

  // 同步到 localFormData.lands 以便儲存
  localFormData.lands = [...landManagement.lands]

  // 觸發資料更新
  if (!initGuard.isInitializing && initGuard.isInitialized) {
    eventEmitter.emitDataChanged()
  }
}

const cancelLandEdit = () => {
  console.log('❌ step2.vue: Cancelling land edit')

  // 清空當前表單
  landUtils.clearCurrentForm()

  // 退出編輯模式
  landManagement.currentEditingLandId = null
  landManagement.isEditingMode = false // 這裡會觸發 watch，自動發送事件

  console.log('✅ step2.vue: Edit cancelled')
}

const deleteLand = (landId: string) => {
  console.log('🗑️ step2.vue: Deleting land:', landId)

  const index = landManagement.lands.findIndex(l => l.id === landId)
  if (index !== -1) {
    landManagement.lands.splice(index, 1)

    // 同步到 localFormData.lands (watch會自動觸發資料更新)
    localFormData.lands = [...landManagement.lands]

    // 如果正在編輯被刪除的土地，退出編輯模式
    if (landManagement.currentEditingLandId === landId) {
      cancelLandEdit()
    }

    // watch(localFormData) 會自動觸發 updateFormData()
    // 不需要手動呼叫 eventEmitter.emitDataChanged()

    console.log('✅ step2.vue: Land deleted successfully, lands count:', landManagement.lands.length)
  }
}

// 編輯狀態監聽與事件發送 + 地圖重建機制
watch(() => landManagement.isEditingMode, async (isEditing, wasEditing) => {
  // 避免初始化時觸發
  if (isEditing === wasEditing) return

  console.log(`🎛️ step2.vue: Navigation state changed - isEditing: ${isEditing}`)

  // 發送導航狀態變更事件
  emit('navigation-state-changed', {
    step: 2,
    canNavigate: !isEditing,
    isEditing: isEditing,
    reason: isEditing ? '正在編輯土地資料，請先完成或取消編輯' : undefined
  })

  // ✅ 地圖初始化由 landInfoDialog watch 統一處理
  // 編輯模式切換時不主動初始化，避免與對話框 watch 衝突
}, { immediate: false })

// 向後相容性處理：從舊版單筆土地資料轉換為多筆土地格式
// const convertLegacyDataToMultipleLands = () => {
//   // 檢查是否有舊版資料但沒有新版 lands 陣列
//   if (localFormData.landCounty && (!localFormData.lands || localFormData.lands.length === 0)) {
//     console.log('🔄 step2.vue: Converting legacy single land data to multiple lands format')

//     // 創建土地資料
//     const legacyLandData = landUtils.createLandFromCurrentForm()
//     legacyLandData.id = 'legacy_land_1'

//     // 加入到土地陣列
//     landManagement.lands = [legacyLandData]
//     localFormData.lands = [...landManagement.lands]

//     console.log('✅ step2.vue: Legacy data converted successfully')
//   }
// }

// 瀏覽器原生防護
const beforeUnloadHandler = (event: BeforeUnloadEvent) => {
  if (landManagement.isEditingMode) {
    event.preventDefault()
    event.returnValue = '您有未完成的土地資料編輯，確定要離開嗎？'
    return event.returnValue
  }
}

// 事件驅動架構:暴露方法給父組件 + 新增編輯狀態暴露
defineExpose({
  handleProceedToNext,
  handleGoBack,
  // 新增：編輯狀態暴露
  isEditingMode: computed(() => landManagement.isEditingMode),
  canNavigate: computed(() => !landManagement.isEditingMode),
  navigationState: computed(() => ({
    canNavigate: !landManagement.isEditingMode,
    blockingReason: landManagement.isEditingMode ? '正在編輯土地資料' : null,
    hasUnsavedChanges: landManagement.isEditingMode
  }))
});

// 🔥 P0 修復：級聯選擇載入邏輯
// Linus 原則：Simple, Predictable, Fast

// 簡化的級聯資料預載 - 消除複雜的保護機制
const preloadCascadeDataForLands = async (lands: LandData[]) => {
  console.log('🔧 [P0 Fix] Preloading cascade data for lands...')

  try {
    // 1. 確保縣市資料已載入
    if (!domicileStore.countyOptions.length) {
      console.log('📍 Loading counties...')
      await domicileStore.loadCounties()
    }

    // 2. 收集所有需要的縣市和鄉鎮ID
    const countyIds = new Set<number>()
    const townIds = new Set<number>()

    lands.forEach(land => {
      if (land.landCounty && typeof land.landCounty === 'number') {
        countyIds.add(land.landCounty)
      }
      if (land.landTown && typeof land.landTown === 'number') {
        townIds.add(land.landTown)
      }
    })

    // 3. 平行載入所有需要的鄉鎮資料
    const townPromises = Array.from(countyIds).map(async (countyId) => {
      console.log(`📍 Loading towns for county ${countyId}...`)
      try {
        await domicileStore.loadTownsByCountyId(countyId)
      } catch (error) {
        console.warn(`⚠️ Failed to load towns for county ${countyId}:`, error)
      }
    })

    await Promise.all(townPromises)

    // 4. 平行載入所有需要的地段資料
    // const sectionPromises = Array.from(townIds).map(async (townId) => {
    //   console.log(`📍 Loading sections for town ${townId}...`)
    //   try {
    //     await domicileStore.loadLandSectionsByTownId(townId)
    //   } catch (error) {
    //     console.warn(`⚠️ Failed to load sections for town ${townId}:`, error)
    //   }
    // })

    // await Promise.all(sectionPromises)

    // console.log('✅ [P0 Fix] Cascade data preloading completed')
  } catch (error) {
    console.error('❌ [P0 Fix] Cascade data preloading failed:', error)
  }
}

// 修復初始化邏輯 - 去除過度複雜的保護機制
const initializeStep2WithCascadeData = async () => {
  console.log('🎯 [P0 Fix] Initializing Step2 with proper cascade loading...')

  try {
    // 標記開始初始化
    initGuard.isInitializing = true

    // 1. 首先載入步驟資料
    const caseNumber = grantsStore.caseNumber
    if (!caseNumber) {
      console.log('⚠️ No case number available, skipping data load')
      return
    }

    console.log(`📦 Loading step data for case: ${caseNumber}`)
    const stepData = await grantsStore.loadStepData(caseNumber, 2)

    // 2. 處理土地資料 - 向後相容
    let lands: LandData[] = []

    if (stepData?.lands?.length) {
      // 新版多筆土地資料
      lands = stepData.lands as LandData[]
      console.log(`📍 Found ${lands.length} lands in new format`)
    } else if (stepData?.landCounty) {
      // 向後相容：轉換舊版單筆資料
      const legacyLand = {
        id: 'legacy_land_1',
        landCounty: stepData.landCounty,
        landTown: stepData.landTown,
        landSec: stepData.landSec,
        landNumber: stepData.landNumber || '',
        landNumberMain: stepData.landNumberMain || '',
        landNumberSub: stepData.landNumberSub || '',
        isAboriginalArea: stepData.isAboriginalArea || false,
        isIrrigationArea: stepData.isIrrigationArea || false,
        isReapplied: stepData.isReapplied || false,
        hasAgriculturalCertificate: stepData.hasAgriculturalCertificate || false,
        certificateYear: stepData.certificateYear || '',
        certificateMonth: stepData.certificateMonth || '',
        certificateDay: stepData.certificateDay || '',
        longitude: stepData.longitude || '',
        latitude: stepData.latitude || '',
        landArea: stepData.landArea || '',
        landAreaHa: stepData.landAreaHa || '',
        facilityArea: stepData.facilityArea || '',
        facilityAreaHa: stepData.facilityAreaHa || '',
        cropCategory: stepData.cropCategory || '',
        cropName: stepData.cropName || '',
        crops: stepData.crops || [],
        ownerName: stepData.ownerName || '',
        ownerId: stepData.ownerId || '',
        ownerCounty: stepData.ownerCounty || '',
        ownerTown: stepData.ownerTown || '',
        ownerVillage: stepData.ownerVillage || '',
        ownerShare1: stepData.ownerShare1 || '',
        ownerShare2: stepData.ownerShare2 || '',
        ownerArea: stepData.ownerArea || '',
        owners: stepData.owners || []
      } as LandData

      lands = [legacyLand]
      console.log('🔄 Converted legacy single land data')
    }

    // 3. 關鍵修復：預載所有級聯資料
    if (lands.length > 0) {
      await preloadCascadeDataForLands(lands)
    } else {
      // 即使沒有土地資料，也要載入基本的縣市資料
      if (!domicileStore.countyOptions.length) {
        await domicileStore.loadCounties()
      }
    }

    // 4. 更新元件狀態
    landManagement.lands = lands
    localFormData.lands = lands

    // 5. 如果有單筆土地資料，同時更新向後相容的欄位
    if (lands.length === 1) {
      const land = lands[0]

      // Set programmatic flag to prevent clearing coordinate/area info during initialization
      isLandNumberUpdateProgrammatic.value = true;

      Object.assign(localFormData, {
        landCounty: land.landCounty,
        landTown: land.landTown,
        landSec: land.landSec,
        landNumber: land.landNumber,
        landNumberMain: land.landNumberMain,
        landNumberSub: land.landNumberSub,
        // ... 其他欄位保持原有邏輯
      })

      // Update previous values for tracking
      previousLandNumberMain.value = land.landNumberMain || '';
      previousLandNumberSub.value = land.landNumberSub || '';

      // Reset the flag after initialization
      setTimeout(() => {
        isLandNumberUpdateProgrammatic.value = false;
      }, 100); // Use a bit longer delay for initialization
    }

    // 🔥 Linus式修復：完成初始化
    console.log('✅ [P0 Fix] Step2 initialization completed successfully')

    // 先標記為已初始化
    initGuard.isInitialized = true
    initGuard.isInitializing = false

    // 🔥 關鍵修復：使用 nextTick 確保所有初始化副作用完成後再發送資料
    // 這樣可以避免初始化過程中的欄位修改被視為「變更」
    await nextTick()

    // 主動發送一次完整的初始化資料狀態給父組件
    // 這確保 grants store 的 previousFormData 與當前資料一致
    eventEmitter.emitDataChanged()

  } catch (error) {
    console.error('❌ [P0 Fix] Step2 initialization failed:', error)
    initGuard.isInitializing = false
    // 確保即使初始化失敗，基本的縣市資料也要載入
    try {
      if (!domicileStore.countyOptions.length) {
        await domicileStore.loadCounties()
      }
    } catch (fallbackError) {
      console.error('❌ Even fallback county loading failed:', fallbackError)
    }
  }
}

// 生命週期管理 - 使用修復後的邏輯
onMounted(async () => {
  window.addEventListener('beforeunload', beforeUnloadHandler)

  // 🔥 P0 修復：使用新的初始化邏輯
  await initializeStep2WithCascadeData()
})

onUnmounted(() => {
  window.removeEventListener('beforeunload', beforeUnloadHandler)
})

// Area calculations
watch(() => localFormData.landArea, stepManager.createProtectedWatch((...args: unknown[]) => {
  const newVal = args[0] as string;
  if (newVal && localFormData.owners && localFormData.owners.length > 0) {
    const landArea = parseFloat(newVal);

    if (!isNaN(landArea)) {
      // 更新每個所有權人的持分面積
      localFormData.owners.forEach((owner, index) => {
        const shareParts = owner.share.split('/');
        if (shareParts.length === 2) {
          const numerator = parseFloat(shareParts[0]);
          const denominator = parseFloat(shareParts[1]);

          if (!isNaN(numerator) && !isNaN(denominator) && denominator !== 0) {
            // 重新計算持分面積
            const newArea = ((landArea * numerator) / denominator).toFixed(1);
            localFormData.owners[index] = {
              ...owner,
              area: newArea
            };
          }
        }
      });
    }
  }

  if (newVal) {
    const area = parseFloat(newVal);
    if (!isNaN(area)) {
      // 更新農地地籍面積公頃值
      const calculatedHa = (area / 10000).toString()
      localFormData.landAreaHa = calculatedHa

      // 檢查設施面積是否超出農地地籍面積
      const facilityArea = parseFloat(localFormData.facilityArea || '0');
      if (!isNaN(facilityArea) && facilityArea > area) {
        // 如果設施面積超出農地地籍面積，將設施面積調整為等於農地地籍面積
        localFormData.facilityArea = newVal;
        localFormData.facilityAreaHa = calculatedHa;
      }
    }
  } else {
    localFormData.landAreaHa = '';
  }

  eventEmitter.emitDataChanged();
}));

watch(() => localFormData.facilityArea as string, stepManager.createProtectedWatch((...args: unknown[]) => {
  const newVal = args[0] as string;
  if (newVal) {
    const facilityArea = parseFloat(newVal);
    const landArea = parseFloat(localFormData.landArea || '0');

    if (!isNaN(facilityArea)) {
      // 如果設施面積超過農地地籍面積
      if (!isNaN(landArea) && facilityArea > landArea) {
        // 調整為等於農地地籍面積
        localFormData.facilityArea = localFormData.landArea;
        localFormData.facilityAreaHa = localFormData.landAreaHa;
      } else {
        // 正常更新公頃值
        localFormData.facilityAreaHa = (facilityArea / 10000).toString();
      }
    }
  } else {
    localFormData.facilityAreaHa = '';
  }

  // 更新父組件資料
  eventEmitter.emitDataChanged();
}));

// Calculate owner area
// watch([() => localFormData.landArea, () => localFormData.ownerShare1, () => localFormData.ownerShare2], () => {
//   if (localFormData.landArea && localFormData.ownerShare1 && localFormData.ownerShare2) {
//     const landArea = parseFloat(localFormData.landArea);
//     const share1 = parseFloat(localFormData.ownerShare1);
//     const share2 = parseFloat(localFormData.ownerShare2);

//     if (!isNaN(landArea) && !isNaN(share1) && !isNaN(share2) && share2 !== 0) {
//       localFormData.ownerArea = ((landArea * share1) / share2).toFixed(1);
//     }
//   } else {
//     localFormData.ownerArea = '';
//   }
// });

// Land dialog handlers
const showLandInfoDialog = () => {
  // Update land info with current form data
  if (localFormData.landNumberMain) {
    landInfo.number = localFormData.landNumberSub
      ? `${localFormData.landNumberMain}-${localFormData.landNumberSub}`
      : localFormData.landNumberMain;
  }

  if (localFormData.landCounty) {
    landInfo.county = localFormData.landCounty;
  }

  if (localFormData.landSec) {
    landInfo.section = localFormData.landSec;
  }

  landInfoDialog.value = true;
  // ✅ 地圖初始化已由 landInfoDialog watch 處理，無需在此手動初始化
};

// OpenLayers map initialization - 增強版本
const initMap = async () => {
  // 防止重複初始化
  // Prevent duplicate initialization
  if (mapState.isInitializing) {
    return;
  }

  // Check if map element exists
  if (!mapElement.value) {
    return;
  }

  try {
    mapState.isInitializing = true;

    // 清理舊實例
    if (map) {
      cleanupMap();
      await nextTick();
    }

    // 清空容器
    if (mapElement.value) {
      const container = mapElement.value as HTMLElement;
      while (container.firstChild) {
        container.removeChild(container.firstChild);
      }
    }

    // Convert coordinate strings to numbers
    const lon = parseFloat(localFormData.longitude || '120.5734');
    const lat = parseFloat(localFormData.latitude || '23.5155');

    // Create OSM layer
    const osmLayer = new TileLayer({
      source: new OSM(),
    });

    // Get target element
    const targetElement = document.getElementById('step2-land-info-map');

    if (!targetElement) {
      throw new Error('Map container not found');
    }

    // Create map instance with markRaw to prevent Vue reactivity overhead
    map = markRaw(new Map({
      target: targetElement,
      layers: [osmLayer],
      view: new View({
        center: fromLonLat([lon, lat]),
        zoom: 16
      }),
    }));

    await nextTick();

    // Add selection interaction
    addSelectInteraction();

    // Load GeoJSON layer
    loadGeoJSONFile();

    mapState.isInitialized = true;

  } catch (error) {
    console.error('Error initializing map:', error);
  } finally {
    mapState.isInitializing = false;
  }
};

const addSelectInteraction = () => {
  if (!map) return;

  // Define style for selected features
  const selectedStyle = new Style({
    stroke: new Stroke({
      color: 'rgba(255, 105, 0, 1)',
      width: 3
    }),
    fill: new Fill({
      color: 'rgba(255, 165, 0, 0.4)'
    })
  });

  // Create select interaction
  select = new Select({
    condition: click,
    style: selectedStyle,
    filter: (feature) => {
      // Don't select the marker
      return feature.get('type') !== 'marker';
    }
  });

  // Add the interaction to the map
  map.addInteraction(select);

  // Create modify interaction that works with the selected features
  modify = new Modify({
    features: select.getFeatures(),
    // Add a custom style to show edit handles
    style: new Style({
      image: new Icon({
        anchor: [0.5, 0.5],
        src: '/assets/images/handle.png'
      }),
      stroke: new Stroke({
        width: 3,
        color: 'rgba(255, 105, 0, 1)'
      }),
      fill: new Fill({
        color: 'rgba(255, 165, 0, 0.4)'
      })
    })
  });

  // #已停用編輯功能# Add the modify interaction to the map
  // map.addInteraction(modify);

  // Listen for selection changes
  selectedFeatureKey = select.on('select', handleFeatureSelect);

  // Listen for geometry modifications
  modifyFeatureKey = modify.on('modifyend', handleFeatureModify);
};

// Handle feature modifications
const handleFeatureModify = (event: { features: { getArray: () => Feature<Geometry>[] } }) => {
  // Get the modified features
  const features = event.features.getArray();

  if (features.length > 0) {
    const feature = features[0];

    // When feature is modified, always use OpenLayers calculated area
    const geometry = feature.getGeometry();
    if (geometry) {
      // Get area in square meters using OpenLayers calculation
      const areaValue = getArea(geometry);
      // Use precise area value without rounding
      const preciseArea = areaValue;

      // Update the feature's area property and mark it as calculated
      feature.set('area', preciseArea);
      feature.set('areaSource', 'calculated'); // Override any previous source

      console.log(`Feature modified. Using calculated area: ${preciseArea} m² (source: calculated)`);

      // Update the selectedFeatureInfo to reflect the new area and source
      if (selectedFeatureInfo.value) {
        selectedFeatureInfo.value = {
          ...selectedFeatureInfo.value,
          area: preciseArea,
          areaSource: 'calculated'
        };
      }

      // Update the land area in the form if this is the currently used feature
      if (landInfo.number === feature.get('Land_no')) {
        localFormData.landArea = preciseArea.toString();
        localFormData.landAreaHa = (preciseArea / 10000).toString();

        // If facility area is not set, set it to the same value
        if (!localFormData.facilityArea) {
          localFormData.facilityArea = preciseArea.toString();
          localFormData.facilityAreaHa = (preciseArea / 10000).toString();
        }

        // 使用統一的事件保護
        if (!initGuard.isInitializing && initGuard.isInitialized) {
          eventEmitter.emitDataChanged();
        }
      }
    }
  }
};

// Function to handle feature selection
const handleFeatureSelect = (e: { selected: Feature<Geometry>[]; deselected: Feature<Geometry>[] }) => {
  const selectedFeatures = e.selected;

  if (selectedFeatures.length > 0) {
    const feature = selectedFeatures[0];
    // Get properties from the feature
    const properties = feature.getProperties();
    console.log('Selected feature properties:', properties);

    // Populate the land info dialog with feature data
    if (properties) {
      // Update land info with feature properties
      landInfo.section = properties.section || landInfo.section;
      landInfo.number = properties.Land_no || landInfo.number;
      landInfo.specialLand = properties.specialLand || landInfo.specialLand;

      // If the feature has coordinates, update the form
      if (properties.lon && properties.lat) {
        localFormData.longitude = properties.lon;
        localFormData.latitude = properties.lat;
      }

      // Calculate area of the feature - prioritize Desc_area from GeoJSON
      const geometry = feature.getGeometry();
      let areaValue = 0;
      let areaSource = 'none';

      // Priority 1: Use Desc_area from GeoJSON properties (cadastral area)
      if (properties.Desc_area && !isNaN(parseFloat(properties.Desc_area))) {
        areaValue = parseFloat(properties.Desc_area);
        areaSource = 'cadastral';
        console.log(`Using cadastral area (Desc_area): ${areaValue} m²`);
      }
      // Priority 2: Use Map_area from GeoJSON properties (survey area)
      else if (properties.Map_area && !isNaN(parseFloat(properties.Map_area))) {
        areaValue = parseFloat(properties.Map_area);
        areaSource = 'survey';
        console.log(`Using survey area (Map_area): ${areaValue} m²`);
      }
      // Priority 3: Calculate from geometry using OpenLayers
      else if (geometry) {
        // Get area in square meters
        areaValue = getArea(geometry);
        // Use precise area value without rounding
        areaSource = 'calculated';
        console.log(`Using calculated area from geometry: ${areaValue} m²`);
      }

      // Set area property and source on the feature for future reference
      if (areaValue > 0) {
        feature.set('area', areaValue);
        feature.set('areaSource', areaSource);
      }

      // Create a copy of properties with updated area and source
      const updatedProperties = {
        ...properties,
        area: areaValue,
        areaSource: areaSource
      };

      // Perform spatial queries to get office boundaries and county information
      if (geometry) {
        performSpatialQueries(feature);
      }

      // You can show a popup with feature info including the area
      selectedFeatureInfo.value = updatedProperties;
      featureInfoVisible.value = true;
    }
  } else {
    // Handle deselection
    hideFeatureInfo();
  }
};


// Hide feature info popup
const hideFeatureInfo = () => {
  featureInfoVisible.value = false;
};

// Toggle feature info popup visibility
const toggleFeatureInfo = () => {
  featureInfoVisible.value = !featureInfoVisible.value;
};

// 🆕 關閉無地段圖資 overlay，同時關閉查詢地號對話窗
const closeNoSectionOverlay = () => {
  noSectionDataOverlay.value = false;
  landInfoDialog.value = false;
};

// Perform spatial queries with the selected feature geometry
const performSpatialQueries = async (feature: Feature<Geometry>) => {
  try {
    // Convert OpenLayers geometry to GeoJSON format
    const geoJSONFormat = new GeoJSON();
    const geoJSONFeature = geoJSONFormat.writeFeatureObject(feature, {
      featureProjection: 'EPSG:3857',
      dataProjection: 'EPSG:4326'
    });

    const geometryData = geoJSONFeature.geometry;

    // Perform both spatial queries in parallel
    const [officeResult, countyResult] = await Promise.all([
      queryOfficeBoundaries(geometryData).catch(error => {
        console.error('Office boundaries query failed:', error);
        return null;
      }),
      queryCountyBoundaries(geometryData).catch(error => {
        console.error('County boundaries query failed:', error);
        return null;
      })
    ]);

    // Update landInfo with spatial query results
    if (officeResult && officeResult.office_boundaries && officeResult.office_boundaries.length > 0) {
      landInfo.irrigationDistrictInfo = officeResult.office_boundaries;
      console.log('Irrigation district info found:', officeResult.office_boundaries.length, 'boundaries');
    } else {
      landInfo.irrigationDistrictInfo = [];
    }

    if (countyResult && countyResult.county_boundaries && countyResult.county_boundaries.length > 0) {
      const county = countyResult.county_boundaries[0];
      landInfo.county = county.countyname || '未知縣市';
      console.log('County found:', county.countyname);
    } else {
      landInfo.county = '查無相關縣市';
    }

  } catch (error) {
    console.error('Spatial queries failed:', error);
    landInfo.irrigationDistrictInfo = [];
    landInfo.county = '空間查詢失敗';
  }
};

// Function to use selected feature data
const useSelectedFeature = () => {
  if (selectedFeatureInfo.value) {
    // Update land number fields from Land_no
    if (selectedFeatureInfo.value.Land_no) {
      const landNo = selectedFeatureInfo.value.Land_no;

      // Set flag to indicate this is a programmatic update
      isLandNumberUpdateProgrammatic.value = true;

      // Check if the Land_no contains a dash (main-sub format)
      if (landNo.includes('-')) {
        const [main, sub] = landNo.split('-');
        localFormData.landNumberMain = main;
        localFormData.landNumberSub = sub;
      } else {
        // If no dash, use the entire value as main number and set sub to empty
        localFormData.landNumberMain = landNo;
        localFormData.landNumberSub = '';
      }

      // Update landNumber to ensure card display sync
      localFormData.landNumber = localFormData.landNumberSub
        ? `${localFormData.landNumberMain}-${localFormData.landNumberSub}`
        : localFormData.landNumberMain;

      // Update previous values for tracking
      previousLandNumberMain.value = localFormData.landNumberMain;
      previousLandNumberSub.value = localFormData.landNumberSub;

      // Reset the flag after the update
      setTimeout(() => {
        isLandNumberUpdateProgrammatic.value = false;
      }, 0);
    }

    // If the feature has an area, update the area fields
    if (selectedFeatureInfo.value.area) {
      localFormData.landArea = String(selectedFeatureInfo.value.area);
      // Convert to hectares
      const areaInHa = (parseFloat(String(selectedFeatureInfo.value.area)) / 10000).toString();
      localFormData.landAreaHa = areaInHa;

      // Set the facility area to match land area by default
      localFormData.facilityArea = String(selectedFeatureInfo.value.area);
      localFormData.facilityAreaHa = areaInHa;
    }

    // Find the selected feature in the map
    const selectedFeatures = select?.getFeatures().getArray() || [];
    if (selectedFeatures.length > 0) {
      const feature = selectedFeatures[0];
      const geometry = feature.getGeometry();

      if (geometry) {
        // Calculate center point that is guaranteed to be within the geometry bounds
        const extent = geometry.getExtent();
        let center = [(extent[0] + extent[2]) / 2, (extent[1] + extent[3]) / 2]; // Default to extent center

        try {
          // For Polygon/MultiPolygon, try to find a better interior point
          if (geometry instanceof Polygon || geometry instanceof MultiPolygon) {
            // Check if the extent center is within the geometry
            if (geometry.intersectsCoordinate(center)) {
              // Extent center is already inside, use it
              console.log('Using extent center as it is within the geometry');
            } else {
              // If extent center is outside, try to find a point inside
              // Use a simple grid search within the extent
              const stepX = (extent[2] - extent[0]) / 10;
              const stepY = (extent[3] - extent[1]) / 10;
              let foundInteriorPoint = false;

              for (let i = 1; i <= 9 && !foundInteriorPoint; i++) {
                for (let j = 1; j <= 9 && !foundInteriorPoint; j++) {
                  const testPoint = [
                    extent[0] + i * stepX,
                    extent[1] + j * stepY
                  ];
                  if (geometry.intersectsCoordinate(testPoint)) {
                    center = testPoint;
                    foundInteriorPoint = true;
                    console.log('Found interior point using grid search');
                  }
                }
              }

              if (!foundInteriorPoint) {
                console.log('No interior point found, using extent center as fallback');
              }
            }
          }
        } catch (error) {
          // If any method fails, center is already set to extent center
          console.warn('Interior point calculation failed, using extent center:', error);
        }

        // Transform from the map projection (EPSG:3857) to WGS84 (EPSG:4326)
        const transformedCenter = transform(center, 'EPSG:3857', 'EPSG:4326');

        // Update the form with the calculated coordinates (rounded to 6 decimal places)
        localFormData.longitude = transformedCenter[0].toFixed(6);
        localFormData.latitude = transformedCenter[1].toFixed(6);

        console.log(`Updated coordinates to interior point of polygon: ${localFormData.longitude}, ${localFormData.latitude}`);
      }
    }

    // Check if the land is within irrigation district and update isIrrigationArea
    if (landInfo.irrigationDistrictInfo && landInfo.irrigationDistrictInfo.length > 0) {
      localFormData.isIrrigationArea = true;
      console.log('Land is within irrigation district, set isIrrigationArea to true');
    } else {
      localFormData.isIrrigationArea = false;
      console.log('Land is not within irrigation district, set isIrrigationArea to false');
    }

    // Hide the feature info popup
    hideFeatureInfo();
    // Close the dialog
    landInfoDialog.value = false;
    // 使用統一的事件保護
    if (!initGuard.isInitializing && initGuard.isInitialized) {
      eventEmitter.emitDataChanged();
    }
  }
};

// Function to load GeoJSON file
const loadGeoJSONFile = () => {
  // Path to the GeoJSON file in assets
  const geoJSONFilePath = `../src/assets/GML/land_parcels.geojson`;

  console.log('Attempting to load GeoJSON from:', geoJSONFilePath);

  // Create a vector source with GeoJSON format
  const geoJSONSource = new VectorSource({
    url: geoJSONFilePath,
    format: new GeoJSON()
  });

  // Add success event listener
  geoJSONSource.on('featuresloadend', function() {
    const features = geoJSONSource.getFeatures();
    console.log(`GeoJSON loaded successfully with ${features.length} features`);

    // 🆕 即時查詢當前選中地段的 office 和 code，組合成 Section 過濾條件
    let filterSection: string | null = null;
    if (localFormData.landSec) {
      const currentSectionCode = localFormData.landSec.toString();
      const selectedSection = sections.value.find(s =>
        s.code === currentSectionCode ||
        s.value === currentSectionCode ||
        s.code === localFormData.landSec ||
        s.value === localFormData.landSec
      );

      if (selectedSection && selectedSection.office && selectedSection.code) {
        filterSection = `${selectedSection.office}${selectedSection.code}`;
        console.log(`🔍 Filtering GeoJSON by Section: ${filterSection} (office: ${selectedSection.office}, code: ${selectedSection.code})`);
      }
    }

    // 🆕 過濾 features：只保留符合當前地段的地號
    let filteredFeatures = features;
    if (filterSection) {
      filteredFeatures = features.filter(feature => {
        const featureSection = feature.get('Section');
        return featureSection === filterSection;
      });
      console.log(`✅ Filtered to ${filteredFeatures.length} features in Section ${filterSection} (from ${features.length} total)`);

      // 🆕 如果過濾後沒有任何 features，顯示「查無此地段圖資」overlay
      if (filteredFeatures.length === 0) {
        console.warn(`⚠️ No features found in Section ${filterSection}`);
        noSectionDataOverlay.value = true;
      }
    }

    // 🆕 清空原始 source 並重新加入過濾後的 features
    geoJSONSource.clear();
    geoJSONSource.addFeatures(filteredFeatures);

    // Add properties to features if they don't have them
    filteredFeatures.forEach((feature, index) => {
      if (!feature.get('id')) {
        feature.set('id', `parcel-${index + 1}`);
      }
      if (!feature.get('section')) {
        // Convert landSec ID to section name for map display
        let sectionName = '瓦厝埔段'; // default
        if (localFormData.landSec) {
          const sectionId = parseInt(localFormData.landSec);
          const section = villages.value.find(s => s.value === sectionId);
          if (section) {
            sectionName = section.title;
          }
        }
        feature.set('section', sectionName);
      }
      if (!feature.get('Land_no')) {

        // Create a random land number for demo
        const mainNum = Math.floor(900 + Math.random() * 100);
        const subNum = Math.floor(1 + Math.random() * 9);
        feature.set('Land_no', `${mainNum}-${subNum}`);
      }
    });

    // Try to find and select the feature with matching land number
    setTimeout(() => {
      findAndSelectFeatureByLandNumber();
    }, 100); // Small delay to ensure map is fully initialized
  });

  // Handle loading errors (commented out due to TypeScript issues with OpenLayers event types)
  // geoJSONSource.on('loaderror', function(event) {
  //   console.error('Error loading GeoJSON file:', event);
  // });

  // Create and add the vector layer
  const geoJSONLayer = new VectorLayer({
    source: geoJSONSource,
    style: new Style({
      stroke: new Stroke({
        color: 'rgba(0, 128, 255, 1.0)',
        width: 2
      }),
      fill: new Fill({
        color: 'rgba(0, 128, 255, 0.2)'
      })
    }),
    zIndex: 10, // 🔥 確保在 OSM 圖層之上
  });

  if (map) {
    map.addLayer(geoJSONLayer);
  }
};

const findAndSelectFeatureByLandNumber = () => {
  if (!map) return;

  // 🆕 清除之前的查無地號 alert
  landParcelNotFoundAlert.value = false;
  landParcelNotFoundMessage.value = '';

  // Get the main and sub numbers
  const mainNumber = localFormData.landNumberMain;
  const subNumber = localFormData.landNumberSub;
  // const mainNumber = localFormData.landNumberMain ? localFormData.landNumberMain.replace(/^0+/, '') || '0' : ''
  // const subNumber = localFormData.landNumberSub ? localFormData.landNumberSub.replace(/^0+/, '') || '0' : ''

  if (!mainNumber) return false;

  // Format the search pattern based on available data
  const fullLandNumber = subNumber ? `${mainNumber}-${subNumber}` : mainNumber;

  // 🆕 即時查詢當前選中地段的 office 和 code，組合成 Section 查詢字串
  let querySection: string | null = null;
  if (localFormData.landSec) {
    const currentSectionCode = localFormData.landSec.toString();
    const selectedSection = sections.value.find(s =>
      s.code === currentSectionCode ||
      s.value === currentSectionCode ||
      s.code === localFormData.landSec ||
      s.value === localFormData.landSec
    );

    if (selectedSection && selectedSection.office && selectedSection.code) {
      querySection = `${selectedSection.office}${selectedSection.code}`;
      console.log(`Searching with Section filter: ${querySection} (office: ${selectedSection.office}, code: ${selectedSection.code})`);
    }
  }

  console.log(`Searching for land number: ${fullLandNumber}`);

  // Look through all vector layers
  const layers = map.getLayers().getArray().filter((layer): layer is VectorLayer<VectorSource> =>
    layer instanceof VectorLayer && layer.getSource() instanceof VectorSource
  );

  let exactMatch: Feature<Geometry> | null = null;
  let mainNumberMatch: Feature<Geometry> | null = null;

  // For each layer, try to find the feature
  for (const layer of layers) {
    const source = layer.getSource();
    if (!source) continue;
    const features = source.getFeatures();

    // First pass: look for exact matches
    features.forEach((feature: Feature<Geometry>) => {
      const featureNumber = feature.get('Land_no');
      if (!featureNumber) return;

      // 🆕 取得 feature 的 Section 屬性
      const featureSection = feature.get('Section');

      // 🆕 如果有 Section 查詢條件，先檢查 Section 是否匹配
      if (querySection && featureSection) {
        if (featureSection !== querySection) {
          // Section 不匹配，跳過此 feature
          return;
        }
      }

      // Check for exact match first
      if (featureNumber === fullLandNumber) {
        exactMatch = feature;
      }
      // If we're looking for a full number but no exact match yet, check for main number match
      else if (subNumber && exactMatch === null && featureNumber === mainNumber) {
        mainNumberMatch = feature;
      }
    });

    // If we found an exact match, use it
    if (exactMatch) {
      const matchedSection = (exactMatch as Feature<Geometry>).get('Section');
      console.log(`✅ Found exact match - Land_no: ${(exactMatch as Feature<Geometry>).get('Land_no')}${matchedSection ? `, Section: ${matchedSection}` : ''}`);
      selectFeature(exactMatch);
      return true;
    }
  }

  // If no exact match was found but we have a main number match, use that
  if (mainNumberMatch) {
    const matchedSection = (mainNumberMatch as Feature<Geometry>).get('Section');
    console.log(`✅ Found main number match - Land_no: ${(mainNumberMatch as Feature<Geometry>).get('Land_no')}${matchedSection ? `, Section: ${matchedSection}` : ''}`);
    selectFeature(mainNumberMatch);
    return true;
  }

  // 🆕 找不到匹配的地號時，嘗試縮放到整個 Section 的範圍
  console.log(`❌ No feature found with land number: ${fullLandNumber}${querySection ? ` in Section: ${querySection}` : ''}`);

  // 🆕 設置查無地號 alert（僅在未顯示「查無地段圖資」overlay 時）
  if (!noSectionDataOverlay.value) {
    const selectedSection = sections.value.find(s =>
      s.code === localFormData.landSec?.toString() ||
      s.value === localFormData.landSec?.toString()
    );
    const sectionName = selectedSection?.name || selectedSection?.displayName || '所選地段';

    landParcelNotFoundAlert.value = true;
    landParcelNotFoundMessage.value = querySection
      ? `在「${sectionName}」中找不到地號「${fullLandNumber}」，已自動縮放至地段範圍供您查看。`
      : `找不到地號「${fullLandNumber}」，請確認地號是否正確。`;
  }

  if (querySection && map) {
    // 收集所有符合 Section 的 features，計算其 bbox
    const sectionExtent = createEmpty();
    let sectionFeatureCount = 0;

    for (const layer of layers) {
      const source = layer.getSource();
      if (!source) continue;
      const features = source.getFeatures();

      features.forEach((feature: Feature<Geometry>) => {
        const featureSection = feature.get('Section');
        if (featureSection === querySection) {
          const geometry = feature.getGeometry();
          if (geometry) {
            extend(sectionExtent, geometry.getExtent());
            sectionFeatureCount++;
          }
        }
      });
    }

    // 如果找到該 Section 的 features，縮放到其範圍
    if (sectionFeatureCount > 0) {
      console.log(`🔍 Zooming to Section ${querySection} with ${sectionFeatureCount} features`);
      map.getView().fit(sectionExtent, {
        duration: 500,
        padding: [50, 50, 50, 50], // 添加邊距以便更好地顯示
        maxZoom: 16 // 限制最大縮放級別，避免過度放大
      });
      return true; // 雖然沒找到精確地號，但成功顯示了地段範圍
    }
  }

  return false;
};

// Helper function to select a feature
const selectFeature = (feature: Feature<Geometry>) => {
  if (select) {
    select.getFeatures().clear(); // Clear any existing selection
    select.getFeatures().push(feature); // Add this feature to selection

    // Trigger the feature selection handler manually
    handleFeatureSelect({
      selected: [feature],
      deselected: []
    });

    // Center the map on this feature
    const geometry = feature.getGeometry();
    if (geometry && map) {
      // Get the extent of the geometry for fitting
      const extent = geometry.getExtent();
      map.getView().fit(extent, {
        duration: 500
      });
    }
  }
};

// Clean up interactions when map is destroyed - 增強版本
const cleanupMap = () => {
  try {
    // Clean up selection interaction
    if (select && selectedFeatureKey) {
      unByKey(selectedFeatureKey);
      selectedFeatureKey = null;
    }

    // Clean up modify interaction
    if (modify && modifyFeatureKey) {
      unByKey(modifyFeatureKey);
      modifyFeatureKey = null;
    }

    // Clean up map instance
    if (map) {
      // Release canvas rendering contexts
      const viewport = map.getViewport();
      if (viewport) {
        const canvases = viewport.querySelectorAll('canvas');
        canvases.forEach(canvas => {
          // Release WebGL context
          const gl = canvas.getContext('webgl') || canvas.getContext('webgl2');
          const loseContextExt = gl?.getExtension('WEBGL_lose_context');
          if (loseContextExt) {
            loseContextExt.loseContext();
          }

          // Clear 2D Canvas
          const ctx = canvas.getContext('2d');
          if (ctx) {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
          }

          // Remove canvas element
          canvas.remove();
        });
      }

      // Clean up all layers and their sources
      map.getLayers().forEach(layer => {
        if ('getSource' in layer && typeof layer.getSource === 'function') {
          const source = layer.getSource();
          if (source && typeof source.dispose === 'function') {
            source.dispose();
          }
        }
      });
      map.getLayers().clear();

      // Remove all interactions
      map.getInteractions().clear();

      // Clean up all controls
      map.getControls().clear();

      // Unbind target to prevent conflicts
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      map.setTarget(null as any);

      // Wait for DOM update
      setTimeout(() => {
        if (map) {
          map.setTarget(undefined);
        }
      }, 0);

      // Dispose map resources
      map.dispose();

      map = null;
    }
    // Reset selection state
    select = null;
    modify = null;
    featureInfoVisible.value = false;
    selectedFeatureInfo.value = {};

    mapState.isInitialized = false;

  } catch (error) {
    console.error('Error during map cleanup:', error);
  }
};

// 事件驅動架構:監聽本地表單資料變更 - 使用統一的保護機制
watch(localFormData, stepManager.createProtectedWatch(() => {
  updateFormData();
}), { deep: true });

// Watch for dialog open/close to initialize/cleanup map - 增強版本
watch(landInfoDialog, async (isOpen, wasOpen) => {
  // Avoid duplicate triggers
  if (isOpen === wasOpen) return;

  if (isOpen) {
    // Clean up previous map instance
    if (map) {
      cleanupMap();
    }

    await nextTick();

    // Simple delay to wait for DOM rendering
    setTimeout(() => {
      initMap();
    }, 100)

  } else {
    // Clean up map when dialog closes
    cleanupMap();
  }
});

// Update map when coordinates change
watch([() => localFormData.longitude, () => localFormData.latitude], () => {
  if (map && localFormData.longitude && localFormData.latitude) {
    const lon = parseFloat(localFormData.longitude);
    const lat = parseFloat(localFormData.latitude);

    if (!isNaN(lon) && !isNaN(lat)) {
      // Update view center
      map.getView().setCenter(fromLonLat([lon, lat]));

      // Update marker position
      const vectorLayer = map.getLayers().getArray().find(layer =>
        layer instanceof VectorLayer
      );

      if (vectorLayer) {
        const feature = vectorLayer.getSource().getFeatures()[0];
        if (feature) {
          feature.setGeometry(new Point(fromLonLat([lon, lat])));
        }
      }
    }
  }
});

// Auto-detect indigenous area based on town selection - 使用保護函數工廠
const checkAndUpdateIndigenousArea = stepManager.createProtectedHandler((...args: unknown[]) => {
  const townId = args[0] as number;
  const town = domicileStore.getTownById(townId);
  if (town) {
    // Set isAboriginalArea to true if the town is indigenous (indigenous_type = 1)
    const isIndigenous = town.is_indigenous || town.indigenous_type === '1';
    if (localFormData.isAboriginalArea !== isIndigenous) {
      localFormData.isAboriginalArea = isIndigenous;
    }
  }
});

// Watchers for automatic town/village loading and indigenous area detection - 使用保護 Watch 工廠
watch(() => localFormData.landCounty as string | number, stepManager.createProtectedWatch(async (...args: unknown[]) => {
  const newCounty = args[0] as string | number;
  const oldCounty = args[1] as string | number;

  if (newCounty) {
    localFormData.landTown = '';
    localFormData.landSec = '';

    // 🆕 只有在真正變更且非載入狀態時才重置（避免編輯模式載入時誤觸發）
    if (!initGuard.isInitializing && oldCounty && oldCounty !== newCounty) {
      resetLandRelatedInfo();
    }

    await loadTownsForCounty(newCounty);
  }
}));

watch(() => localFormData.landTown, stepManager.createProtectedWatch(async (...args: unknown[]) => {
  const newTown = args[0] as string | number;
  const oldTown = args[1] as string | number;

  if (newTown) {
    const townId = typeof newTown === 'number' ? newTown : parseInt(newTown);

    // 🆕 只有在真正變更且非載入狀態時才重置（避免編輯模式載入時誤觸發）
    if (!initGuard.isInitializing && oldTown && oldTown !== newTown) {
      resetLandRelatedInfo();
    }

    // 檢查是否為特殊城市的代碼，如果是則跳過處理
    const isSpecialCityCode = newTown === 'O01' || newTown === 'I01';
    if (!isSpecialCityCode) {
      // 一般鄉鎮才載入地段資料
      await loadLandSections();
      checkAndUpdateIndigenousArea(townId);
    }
  }
}));

// 🆕 監聽地段變更，重置相關資訊
watch(() => localFormData.landSec, stepManager.createProtectedWatch((...args: unknown[]) => {
  const newSec = args[0] as string | number;
  const oldSec = args[1] as string | number;

  // 只有在真正變更且非載入狀態時才重置（避免編輯模式載入時誤觸發）
  if (!initGuard.isInitializing && newSec && oldSec && oldSec !== newSec) {
    resetLandRelatedInfo();
  }
}));

watch(() => localFormData.ownerCounty, stepManager.createProtectedWatch(async (...args: unknown[]) => {
  const newCounty = args[0] as string | number;
  if (newCounty) {
    localFormData.ownerTown = '';
    localFormData.ownerVillage = '';
    await loadTownsForCounty(newCounty);
  }
}));

watch(() => localFormData.ownerTown, stepManager.createProtectedWatch(async (...args: unknown[]) => {
  const newTown = args[0] as number | string;
  if (newTown) {
    localFormData.ownerVillage = '';
    const townId = typeof newTown === 'number' ? newTown : parseInt(newTown);
    await domicileStore.loadVillagesByTownId(townId);
  }
}));

// 申請資格預查功能 - 在新分頁開啟 qualification 頁面並傳遞地段地號資訊
const openQualificationQuery = () => {
  // 從當前表單資料獲取地段和地號資訊
  const county = localFormData.landCounty
  const town = localFormData.landTown
  const section = localFormData.landSec
  const parentLandNumber = localFormData.landNumberMain
  const childLandNumber = localFormData.landNumberSub

  // 建構 URL 參數
  const params = new URLSearchParams()

  // 獲取縣市名稱，用於判斷是否為特殊城市
  const countyName = typeof county === 'number'
    ? domicileStore.countyOptions.find(c => c.value === county)?.title || ''
    : county

  if (county) {
    if (countyName) params.set('county', countyName.toString())
  }

  if (town) {
    // 特殊城市不需要傳送 town 參數
    if (!specialCities[countyName as string]) {
      // 如果是數字 ID，需要轉換為鄉鎮名稱
      const townName = typeof town === 'number'
        ? domicileStore.getTownById(town)?.name || ''
        : town
      if (townName) params.set('town', townName.toString())
    }
  }

  if (section) {
    let sectionName = ''

    if (specialCities[countyName as string]) {
      // 特殊縣市：section 是代碼值，直接使用
      sectionName = section.toString()
    } else {
      // 一般縣市：section 是數字 ID，從 domicile store 查找
      sectionName = typeof section === 'number'
        ? domicileStore.getLandSectionsForTownId(typeof town === 'number' ? town : parseInt(town?.toString() || '0')).find(s => s.value === section)?.title || ''
        : section.toString()
    }

    if (sectionName) params.set('section', sectionName)
  }

  if (parentLandNumber) {
    params.set('parentLandNumber', parentLandNumber.toString())
  }

  if (childLandNumber) {
    params.set('childLandNumber', childLandNumber.toString())
  }

  // 構建完整的 URL
  const baseUrl = `${window.location.origin}/qualification`
  const fullUrl = params.toString() ? `${baseUrl}?${params.toString()}` : baseUrl

  // 在新分頁開啟 qualification 頁面
  window.open(fullUrl, '_blank')
}

// 修正按鈕點擊事件名稱
const showEligibilityDialog = openQualificationQuery

// Clean up resources when component is unmounted
onUnmounted(() => {
  cleanupMap();
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

/* 按鈕懸停效果 */
.v-btn[variant="outlined"] {
  transition: all 0.2s ease;
}

.v-btn[variant="outlined"]:hover {
  background-color: #3ea0a3 !important;
  color: white !important;
}

.v-card-title {
  line-height: 1.5;
}

.v-table {
  background-color: white;
}

.v-table th {
  font-weight: 600;
  color: rgba(0, 0, 0, 0.7);
}

.feature-info-card {
  position: absolute;
  top: 2px;
  right: 2px;
  width: 200px;
  max-width: 40%;
  background: white;
  font-size: 0.875rem;
}

.border {
  border: 1px solid rgba(0, 0, 0, 0.12);
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

/* 多筆土地管理樣式 */
.land-card {
  transition: all 0.3s ease;
  cursor: pointer;
}

.land-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15) !important;
}

.land-card.selected {
  border-color: #3ea0a3 !important;
  background-color: rgba(62, 160, 163, 0.04);
}

.land-summary {
  min-height: 80px;
}

.land-summary .text-body-2 {
  color: rgba(0, 0, 0, 0.7);
  font-size: 0.875rem;
  line-height: 1.5;
}

.cursor-pointer {
  cursor: pointer;
}

/* 總面積統計樣式 */
.text-success {
  color: #4caf50 !important;
}

/* 土地卡片編號樣式 */
.land-card .v-chip {
  font-weight: 600;
}

/* 土地卡片圖標樣式 */
.land-summary .v-icon {
  color: rgba(62, 160, 163, 0.8);
  margin-right: 4px;
}

/* 編輯按鈕樣式 */
.land-card .v-card-actions .v-btn {
  font-weight: 500;
  transition: all 0.2s ease;
}

.land-card .v-card-actions .v-btn:hover {
  background-color: #3ea0a3 !important;
  color: white !important;
  transform: scale(1.02);
}

/* 刪除按鈕樣式 */
.land-card .v-btn--icon {
  transition: all 0.2s ease;
}

.land-card .v-btn--icon:hover {
  background-color: rgba(244, 67, 54, 0.1) !important;
  transform: scale(1.1);
}

/* 空狀態樣式 */
.empty-state {
  min-height: 200px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

/* 響應式設計 */
@media (max-width: 768px) {
  .land-card {
    margin-bottom: 1rem;
  }

  .land-summary {
    min-height: 60px;
  }

  .land-summary .text-body-2 {
    font-size: 0.8125rem;
  }
}

/* 編輯模式樣式 */
.editing-mode {
  border: 2px solid #3ea0a3;
  background-color: rgba(62, 160, 163, 0.02);
}

/* 日期選擇器對話框樣式 */
.date-picker-dialog {
  border-radius: 12px;
}

.date-picker-dialog .v-card-title {
  border-top-left-radius: 12px;
  border-top-right-radius: 12px;
}

/* 下拉選單樣式 */
/* :deep(.v-select .v-field__input) {
  font-weight: 500;
}
:deep(.v-autocomplete .v-field__input) {
  font-weight: 500;
}*/

/* 確定按鈕增強樣式 */
:deep(.v-btn--variant-flat) {
  box-shadow: 0 2px 4px rgba(62, 160, 163, 0.2);
  transition: all 0.3s ease;
}

:deep(.v-btn--variant-flat:hover) {
  box-shadow: 0 4px 8px rgba(62, 160, 163, 0.3);
  transform: translateY(-1px);
}

/* 日期輸入框點擊效果 */
.clickable-input:hover {
  cursor: pointer;
  background-color: rgba(62, 160, 163, 0.04);
  transition: background-color 0.2s ease;
}

/* 日期顯示文字樣式 */
.date-display-text {
  display: inline-flex;
  align-items: center;
  padding: 4px 8px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
  color: rgba(0, 0, 0, 0.87);
  min-height: 24px;
}

.date-display-text:hover {
  background-color: rgba(62, 160, 163, 0.08);
  color: #3ea0a3;
}

.date-display-text span {
  font-size: 0.875rem;
  line-height: 1.4;
}

/* 響應式設計改進 */
@media (max-width: 480px) {
  .date-picker-dialog {
    margin: 16px;
    max-width: calc(100vw - 32px);
  }

  .date-picker-dialog .v-card-text {
    padding: 16px 12px;
  }

  .date-picker-dialog .v-select {
    font-size: 14px;
  }
}
</style>
