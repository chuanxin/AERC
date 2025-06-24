<template>
  <div
    ref="stepContent"
    class="step-content"
  >
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
          <!-- 設施地址區域 -->
          <v-card
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
                mdi-home-map-marker
              </v-icon>
              <span><span class="required-asterisk">*</span>設施地址</span>
            </v-card-title>

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
                  md="4"
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
                  md="4"
                >
                  <v-select
                    v-model="localFormData.landTown"
                    :items="towns"
                    variant="outlined"
                    density="comfortable"
                    color="#3ea0a3"
                    bg-color="white"
                    :rules="[v => !!v || '請選擇鄉鎮市區']"
                    :disabled="!localFormData.landCounty"
                    @update:model-value="onTownChange"
                  >
                    <template #label>
                      鄉鎮市區
                    </template>
                  </v-select>
                </v-col>
                <v-col
                  cols="12"
                  md="4"
                >
                  <v-select
                    v-model="localFormData.landSec"
                    :items="villages"
                    variant="outlined"
                    density="comfortable"
                    color="#3ea0a3"
                    bg-color="white"
                    :rules="[v => !!v || '請選擇地段']"
                    :disabled="!localFormData.landTown"
                  >
                    <template #label>
                      地段
                    </template>
                  </v-select>
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
                  md="7"
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
                                :rules="[v => !!v || '請輸入主地號']"
                                @focus="landNumberMainFocused = true"
                                @blur="landNumberMainFocused = false"
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
                                @focus="landNumberSubFocused = true"
                                @blur="landNumberSubFocused = false"
                              />
                            </div>

                            <!-- 查詢按鈕 -->
                            <div class="mt-4">
                              <v-btn
                                color="#3ea0a3"
                                variant="outlined"
                                rounded="lg"
                                class="px-4"
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
                        <strong>查詢說明：</strong>請輸入完整地號後點擊查詢按鈕。若查無地號資料，請洽中心。
                      </div>
                    </v-alert>
                  </v-card>
                </v-col>
                <v-spacer />
                <!-- 土地特性選項區域 -->
                <v-col
                  cols="12"
                  md="5"
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

                  <div class="d-flex align-center mb-2">
                    <span
                      class="text-body-2 font-weight-medium me-3"
                      style="min-width: 80px;"
                    >
                      位於灌區內
                    </span>
                    <v-radio-group
                      v-model="localFormData.isIrrigationArea"
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
                  • 經度範圍：約 119.0° ~ 122.5°（東經）<br>
                  • 緯度範圍：約 21.8° ~ 25.4°（北緯）<br>
                  <!-- • 可使用 Google Maps 或內政部地政司網站取得坐標 -->
                </div>
              </v-alert>

              <v-row>
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
                    <span class="text-body-1 font-weight-medium me-2">農地地籍面積</span>
                    <v-text-field
                      v-model="localFormData.landArea"
                      variant="outlined"
                      density="compact"
                      color="#3ea0a3"
                      bg-color="white"
                      class="me-2"
                      style="width: 120px"
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
                      style="width: 120px"
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
                    <span class="text-body-1 font-weight-medium me-2">施作面積</span>
                    <v-text-field
                      v-model="localFormData.facilityArea"
                      variant="outlined"
                      density="compact"
                      color="#3ea0a3"
                      bg-color="white"
                      class="me-2"
                      style="width: 120px"
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
                      style="width: 120px"
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
          </v-card>

          <!-- 所有權人資料區域 -->
          <v-card
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

    <!-- Land info dialog -->
    <v-dialog
      v-model="landInfoDialog"
      max-width="700px"
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
            mdi-map-marker
          </v-icon>
          <span>土地資訊</span>
        </v-card-title>

        <v-card-text class="pa-4">
          <div class="map-container mb-4">
            <div
              ref="mapElement"
              style="height: 300px; width: 100%;"
              class="rounded border"
            />
            <!-- Feature info popup -->
            <v-card
              v-if="featureInfoVisible"
              class="feature-info-card pa-2"
              elevation="4"
            >
              <v-card-title class="text-body-1 py-1 px-2">
                地段資訊
              </v-card-title>
              <v-divider />
              <v-card-text class="px-2 py-1">
                <div v-if="selectedFeatureInfo.Land_no">
                  <strong>地號:</strong> {{ selectedFeatureInfo.Land_no }}
                </div>
                <div v-if="selectedFeatureInfo.section">
                  <strong>地段:</strong> {{ selectedFeatureInfo.section }}
                </div>
                <div v-if="selectedFeatureInfo.area">
                  <strong>面積:</strong> {{ selectedFeatureInfo.area }} 平方公尺
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
          <v-table
            density="comfortable"
            class="border rounded mb-4"
          >
            <tbody>
              <tr>
                <td
                  class="bg-grey-lighten-4 font-weight-medium"
                  width="15%"
                >
                  補助資訊
                </td>
                <td>{{ landInfo.subsidyInfo }}</td>
                <td
                  class="bg-grey-lighten-4 font-weight-medium"
                  width="15%"
                >
                  縣市
                </td>
                <td>{{ landInfo.county }}</td>
              </tr>
              <tr>
                <td class="bg-grey-lighten-4 font-weight-medium">
                  水利小組
                </td>
                <td>{{ landInfo.waterResourceGroup }}</td>
                <!-- <td class="bg-grey-lighten-4 font-weight-medium">
                  特殊地
                </td>
                <td>{{ landInfo.specialLand ? '是' : '否' }}</td> -->
              </tr>
            </tbody>
          </v-table>
        </v-card-text>
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
import { Vector as VectorLayer } from 'ol/layer';
import { Vector as VectorSource } from 'ol/source';
import { Style, Icon, Stroke, Fill } from 'ol/style';
import GeoJSON from 'ol/format/GeoJSON';
import { Select, Modify } from 'ol/interaction';
import { click } from 'ol/events/condition';
import { unByKey } from 'ol/Observable';
import type { EventsKey } from 'ol/events';
import { getArea } from 'ol/sphere';
import { debounce } from 'lodash';
import type { Feature } from 'ol';
import type { Geometry } from 'ol/geom';

// Define type for selected feature info
interface SelectedFeatureInfo {
  Land_no?: string;
  section?: string;
  area?: string | number;
  [key: string]: unknown;
}

// Import store
import { useGrantsStore } from '@/stores/grants';
import { useDomicileStore } from '@/stores/domicile';
import { useRoute } from 'vue-router';

// 事件驅動架構：定義事件類型
interface Step2Events {
  'step-data-changed': [eventData: { step: number; data: Record<string, unknown>; valid: boolean }];
  'validation-changed': [eventData: { step: number; valid: boolean }];
  'ready-to-proceed': [eventData: { step: number; data: Record<string, unknown> }];
  'go-back-requested': [eventData: { step: number }];
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

// 統一的初始化保護系統
const createInitializationGuard = (): StepInitializationGuard => ({
  isInitialized: false,
  isInitializing: false,
  isDataLoading: false
})

// 統一的事件發送器
const createEventEmitter = (
  stepNumber: number,
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  emit: any,
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

// 創建統一的級聯選擇管理器
const createCascadeSelectManager = (
  formData: Record<string, unknown>,
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  domicileStore: any,
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
          console.log('📍 Loading villages for landTown:', formData.landTown)
          const townId = typeof formData.landTown === 'number' ? formData.landTown : parseInt(formData.landTown as string)
          await loadVillagesForTown(townId)
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
    if (guard.isInitializing) return

    switch (level) {
      case 'county':
        formData.landTown = ''
        formData.landSec = ''
        break
      case 'town':
        formData.landSec = ''
        break
    }
  }
})

// 實例化統一系統
const initGuard = reactive(createInitializationGuard())

// 事件驅動架構：創建初始表單資料函數
const createInitialFormData = () => ({
  // Facility address section
  landCounty: '',
  landTown: '',
  landSec: '',
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

const eventEmitter = createEventEmitter(2, emit, localFormData, localValid, initGuard)
const cascadeManager = createCascadeSelectManager(localFormData, domicileStore, initGuard)

// Dialog state
const landInfoDialog = ref(false);
const landInfo = reactive({
  subsidyInfo: '符合補助資格',
  county: '嘉義縣',
  section: '瓦厝埔段',
  number: '996-1',
  managementOffice: '瑠公管理處',
  workstation: '嘉義工作站',
  waterResourceGroup: '第三水利小組',
  specialLand: false
});

// Feature info state
const featureInfoVisible = ref(false);
const selectedFeatureInfo = ref<SelectedFeatureInfo>({});

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

// Load towns and villages for a county when it's selected
const loadTownsForCounty = async (countyValue: number | string) => {
  if (typeof countyValue === 'number') {
    await domicileStore.loadTownsByCountyId(countyValue);
  } else if (typeof countyValue === 'string' && !isNaN(parseInt(countyValue))) {
    await domicileStore.loadTownsByCountyId(parseInt(countyValue));
  }
};

const loadVillagesForTown = async (townValue: number) => {
  await domicileStore.loadLandSectionsByTownId(townValue);
};

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
  return domicileStore.getTownsForCountyId(countyId);
});

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
    // Store numeric value (remove leading zeros)
    localFormData.landNumberMain = val ? val.replace(/^0+/, '') || '0' : ''
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
    // Store numeric value (remove leading zeros)
    localFormData.landNumberSub = val ? val.replace(/^0+/, '') || '0' : '';
    updateLandNumber();
  }
});

const landAreaHaComputed = computed({
  get: () => {
    if (!localFormData.landArea) return '';
    const area = parseFloat(localFormData.landArea);
    return !isNaN(area) ? (area / 10000).toFixed(4) : '';
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
    return !isNaN(area) ? (area / 10000).toFixed(4) : '';
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

// Helper function to format land numbers for display elsewhere
// const formatLandNumber = (value) => {
//   if (!value) return '0000';
//   return value.toString().padStart(4, '0');
// };

const updateLandNumber = () => {
  if (localFormData.landNumberMain) {
    localFormData.landNumber = localFormData.landNumberSub
      ? `${localFormData.landNumberMain}-${localFormData.landNumberSub}`
      : localFormData.landNumberMain;
  } else {
    localFormData.landNumber = '';
  }
  // 在初始化期間不觸發事件
  if (!initGuard.isInitializing) {
    eventEmitter.emitDataChanged();
  }
};

const onCountyChange = () => {
  cascadeManager.resetCascadeSelections('county');
  // 在初始化期間不觸發事件
  if (!initGuard.isInitializing) {
    eventEmitter.emitDataChanged();
  }
};

const onTownChange = () => {
  cascadeManager.resetCascadeSelections('town');
  // 在初始化期間不觸發事件
  if (!initGuard.isInitializing) {
    eventEmitter.emitDataChanged();
  }
};

const onOwnerCountyChange = () => {
  localFormData.ownerTown = '';
  localFormData.ownerVillage = '';
  // 在初始化期間不觸發事件
  if (!initGuard.isInitializing) {
    eventEmitter.emitDataChanged();
  }
};

const onOwnerTownChange = () => {
  localFormData.ownerVillage = '';
  // 在初始化期間不觸發事件
  if (!initGuard.isInitializing) {
    eventEmitter.emitDataChanged();
  }
};

const onCropCategoryChange = () => {
  localFormData.cropName = '';
  // 在初始化期間不觸發事件
  if (!initGuard.isInitializing) {
    eventEmitter.emitDataChanged();
  }
};

// Add and remove crops
const addCrop = () => {
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

    // 🔥 修復問題2：在初始化期間不觸發事件
    if (!initGuard.isInitializing) {
      eventEmitter.emitDataChanged();
    }
  }
};

const removeCrop = (index: number) => {
  localFormData.crops.splice(index, 1);
  // 🔥 修復問題2：在初始化期間不觸發事件
  if (!initGuard.isInitializing) {
    eventEmitter.emitDataChanged();
  }
};

// Date picker methods
const confirmDate = () => {
  showDatePicker.value = false;
  // 🔥 修復問題2：在初始化期間不觸發事件
  if (!initGuard.isInitializing) {
    eventEmitter.emitDataChanged();
  }
};

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

// Add and remove owners
const addOwner = () => {
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

    // 在初始化期間不觸發事件
    if (!initGuard.isInitializing) {
      eventEmitter.emitDataChanged();
    }
  }
};

const removeOwner = (index: number) => {
  localFormData.owners.splice(index, 1);
  // 在初始化期間不觸發事件
  if (!initGuard.isInitializing) {
    eventEmitter.emitDataChanged();
  }
};

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

// 事件驅動架構：統一的資料變更處理 (現在由 eventEmitter 處理)
const updateFormData = () => {
  // 在初始化期間不執行更新，避免重置資料庫資料
  if (!initGuard.isInitialized || initGuard.isInitializing) {
    console.log('⏸️ step2.vue: Skipping updateFormData during initialization');
    return;
  }

  // 驗證表單
  validateForm();

  // 發送資料變更事件
  eventEmitter.emitDataChanged();
};

// 事件驅動架構:表單驗證
const validateForm = async (): Promise<boolean> => {
  if (form.value) {
    const { valid } = await (form.value as { validate: () => Promise<{ valid: boolean }> }).validate();
    localValid.value = valid;

    // 在初始化期間不發送驗證事件，避免觸發不當的儲存
    if (!initGuard.isInitializing && initGuard.isInitialized) {
      eventEmitter.emitValidationChanged(valid);
    } else {
      console.log('⏸️ step2.vue: Skipping validation event emission during initialization');
    }

    return valid;
  }
  return true;
};

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

// 事件驅動架構:暴露方法給父組件
defineExpose({
  handleProceedToNext,
  handleGoBack
});

// Area calculations
watch(() => localFormData.landArea, (newVal) => {
  // 在初始化期間不執行面積計算，避免觸發事件
  if (initGuard.isInitializing) {
    console.log('⏸️ step2.vue: Skipping landArea calculation during initialization');
    return;
  }

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
      const calculatedHa = (area / 10000).toFixed(4)
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
});

watch(() => localFormData.facilityArea, (newVal) => {
  // 在初始化期間不執行面積計算，避免觸發事件
  if (initGuard.isInitializing) {
    console.log('⏸️ step2.vue: Skipping facilityArea calculation during initialization');
    return;
  }

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
        localFormData.facilityAreaHa = (facilityArea / 10000).toFixed(4);
      }
    }
  } else {
    localFormData.facilityAreaHa = '';
  }

  // 更新父組件資料
  eventEmitter.emitDataChanged();
});

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

  // Allow time for the dialog to open and map to initialize
  nextTick(() => {
    // This will be called after the DOM updates
    if (mapElement.value) {
      initMap();
    }
  });
};

// const useLandInfo = () => {
//   // Update form with data from the dialog
//   localFormData.landNumber = landInfo.number;

//   // Parse main and sub number
//   const parts = landInfo.number.split('-');
//   localFormData.landNumberMain = parts[0];
//   localFormData.landNumberSub = parts.length > 1 ? parts[1] : '';

//   // Set county if not set
//   if (!localFormData.landCounty) {
//     localFormData.landCounty = landInfo.county;
//   }

//   // Set land section if applicable
//   if (landInfo.section) {
//     // Find the section by name in the available sections
//     const matchingSection = villages.value.find(section => section.title === landInfo.section);
//     if (matchingSection) {
//       localFormData.landSec = matchingSection.value.toString();
//     }
//   }

//   // Update aboriginal area status
//   localFormData.isAboriginalArea = landInfo.specialLand;

//   // Clean up map resources
//   if (map) {
//     map.setTarget(null);
//     map = null;
//   }

//   // Close the dialog
//   landInfoDialog.value = false;

//   // Update parent form data
//   updateFormData();
// };

// OpenLayers map initialization
const initMap = () => {
  if (!mapElement.value || map) return;

  // Convert coordinate strings to numbers
  const lon = parseFloat(localFormData.longitude || '120.5734');
  const lat = parseFloat(localFormData.latitude || '23.5155');

  // Create map instance
  map = new Map({
    target: mapElement.value,
    layers: [
      new TileLayer({
        source: new OSM()
      })
    ],
    view: new View({
      center: fromLonLat([lon, lat]),
      zoom: 16
    })
  });

  // Add selection interaction
  addSelectInteraction();

  // Load GeoJSON layer
  loadGeoJSONFile();
};

// const addMarker = (lon, lat) => {
//   if (!map) return;

//   // Create marker feature
//   const markerFeature = new Feature({
//     geometry: new Point(fromLonLat([lon, lat])),
//     name: '所選位置',
//     type: 'marker'
//   });

//   markerFeature.setStyle(
//     new Style({
//       image: new Icon({
//         scale: 0.7,
//         src: '/assets/images/marker.png'
//       })
//     })
//   );

//   const markerSource = new VectorSource({
//     features: [markerFeature]
//   });

//   const markerLayer = new VectorLayer({
//     source: markerSource,
//     zIndex: 10  // Set a higher zIndex to keep marker on top
//   });

//   map.addLayer(markerLayer);
// };

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

  // Add the modify interaction to the map
  map.addInteraction(modify);

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

    // Calculate the new area
    const geometry = feature.getGeometry();
    if (geometry) {
      // Get area in square meters
      const areaValue = getArea(geometry);
      // Round to 1 decimal place
      const roundedArea = Math.round(areaValue * 10) / 10;

      // Update the feature's area property
      feature.set('area', roundedArea);

      // Update the selectedFeatureInfo to reflect the new area
      if (selectedFeatureInfo.value) {
        selectedFeatureInfo.value = {
          ...selectedFeatureInfo.value,
          area: roundedArea
        };
      }

      // Update the land area in the form if this is the currently used feature
      if (landInfo.number === feature.get('Land_no')) {
        localFormData.landArea = roundedArea.toString();
        localFormData.landAreaHa = (roundedArea / 10000).toFixed(4);

        // If facility area is not set, set it to the same value
        if (!localFormData.facilityArea) {
          localFormData.facilityArea = roundedArea.toString();
          localFormData.facilityAreaHa = (roundedArea / 10000).toFixed(4);
        }

        // 🔥 修復問題2：在初始化期間不觸發事件
        if (!initGuard.isInitializing) {
          eventEmitter.emitDataChanged();
        }
      }

      console.log(`Feature modified. New area: ${roundedArea} m²`);
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

      // Calculate area of the feature if it has a geometry
      const geometry = feature.getGeometry();
      let areaValue = 0;

      if (geometry) {
        // Get area in square meters
        areaValue = getArea(geometry);
        // Round to 1 decimal place
        areaValue = Math.round(areaValue * 10) / 10;

        // Set area property on the feature
        feature.set('area', areaValue);

        // If the feature already has an area property, use that instead
        if (properties.area && !isNaN(parseFloat(properties.area))) {
          areaValue = parseFloat(properties.area);
        }
      }

      // Create a copy of properties with updated area
      const updatedProperties = {
        ...properties,
        area: areaValue
      };

      // You can show a popup with feature info including the area
      selectedFeatureInfo.value = updatedProperties;
      featureInfoVisible.value = true;
    }
  } else {
    // Handle deselection
    hideFeatureInfo();
  }
};

// Show feature info popup
// const showFeatureInfo = (feature) => {
//   const properties = feature.getProperties();
//   selectedFeatureInfo.value = properties;
//   featureInfoVisible.value = true;
// };

// Hide feature info popup
const hideFeatureInfo = () => {
  featureInfoVisible.value = false;
};

// Function to use selected feature data
const useSelectedFeature = () => {
  if (selectedFeatureInfo.value) {
    // Update land number fields from Land_no
    if (selectedFeatureInfo.value.Land_no) {
      const landNo = selectedFeatureInfo.value.Land_no;

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
    }

    // If the feature has an area, update the area fields
    if (selectedFeatureInfo.value.area) {
      localFormData.landArea = String(selectedFeatureInfo.value.area);
      // Convert to hectares
      const areaInHa = (parseFloat(String(selectedFeatureInfo.value.area)) / 10000).toFixed(4);
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
        // Get the extent (bounding box) of the geometry
        const extent = geometry.getExtent();
        // Calculate the center of the extent
        const center = [(extent[0] + extent[2]) / 2, (extent[1] + extent[3]) / 2];

        // Transform from the map projection (EPSG:3857) to WGS84 (EPSG:4326)
        const transformedCenter = transform(center, 'EPSG:3857', 'EPSG:4326');

        // Update the form with the center coordinates (rounded to 6 decimal places)
        localFormData.longitude = transformedCenter[0].toFixed(6);
        localFormData.latitude = transformedCenter[1].toFixed(6);

        console.log(`Updated coordinates to center of polygon: ${localFormData.longitude}, ${localFormData.latitude}`);
      }
    }

    // Hide the feature info popup
    hideFeatureInfo();
    // Close the dialog
    landInfoDialog.value = false;
    // 🔥 修復問題2：在初始化期間不觸發事件
    if (!initGuard.isInitializing) {
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

    // Add properties to features if they don't have them
    features.forEach((feature, index) => {
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
    })
  });

  if (map) {
    map.addLayer(geoJSONLayer);
  }
};

const findAndSelectFeatureByLandNumber = () => {
  if (!map) return;

  // Get the main and sub numbers
  const mainNumber = localFormData.landNumberMain;
  const subNumber = localFormData.landNumberSub;
  // const mainNumber = localFormData.landNumberMain ? localFormData.landNumberMain.replace(/^0+/, '') || '0' : ''
  // const subNumber = localFormData.landNumberSub ? localFormData.landNumberSub.replace(/^0+/, '') || '0' : ''

  if (!mainNumber) return false;

  // Format the search pattern based on available data
  const fullLandNumber = subNumber ? `${mainNumber}-${subNumber}` : mainNumber;
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
      console.log(`Found exact match feature with land number: ${(exactMatch as Feature<Geometry>).get('Land_no')}`);
      selectFeature(exactMatch);
      return true;
    }
  }

  // If no exact match was found but we have a main number match, use that
  if (mainNumberMatch) {
    console.log(`Found main number match: ${(mainNumberMatch as Feature<Geometry>).get('Land_no')}`);
    selectFeature(mainNumberMatch);
    return true;
  }

  console.log(`No feature found with land number: ${fullLandNumber}`);
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

// Clean up interactions when map is destroyed
const cleanupMap = () => {
  if (select && selectedFeatureKey) {
    unByKey(selectedFeatureKey);
  }

  if (modify && modifyFeatureKey) {
    unByKey(modifyFeatureKey);
  }

  if (map) {
    map.setTarget(undefined);
    map = null;
  }
};

// 事件驅動架構:自主載入資料
const loadStepData = async () => {
  if (initGuard.isDataLoading || initGuard.isInitializing) return;

  const caseNumber = route.query.id as string;
  if (!caseNumber) {
    console.warn('❌ step2.vue: No case number in route');
    return;
  }

  try {
    initGuard.isDataLoading = true;
    initGuard.isInitializing = true;

    console.log('📥 step2.vue: Loading step data for case:', caseNumber);

    // 調用 grantsStore.loadStepData 從 API 載入資料
    console.log('🎯 step2.vue: Calling grantsStore.loadStepData(2) to load from API...');
    await grantsStore.loadStepData(caseNumber, 2);
    console.log('✅ step2.vue: grantsStore.loadStepData completed');

    // 從 grantsStore 取得已載入的 step 2 資料
    if (grantsStore.formData[2]) {
      const savedData = grantsStore.formData[2];
      console.log('📦 step2.vue: Found loaded data from grantsStore:', Object.keys(savedData));

      // 暫時禁用 watch，避免觸發不當的更新
      initGuard.isInitializing = true;

      // 更新本地表單資料，排除 valid 欄位
      Object.keys(savedData).forEach(key => {
        if (key !== 'valid' && savedData[key] !== undefined && key in localFormData) {
          (localFormData as Record<string, unknown>)[key] = savedData[key];
        }
      });

      // 載入級聯選擇資料
      await cascadeManager.loadCascadeData();

    } else {
      console.log('📝 step2.vue: No data found in grantsStore.formData[2], using default values');
    }

    // 確保陣列存在
    if (!Array.isArray(localFormData.crops)) {
      localFormData.crops = [];
    }

    if (!Array.isArray(localFormData.owners)) {
      localFormData.owners = [];
    }

    console.log('✅ step2.vue: Data loaded successfully');
    console.log('📊 step2.vue: Final localFormData keys:', Object.keys(localFormData));

  } catch (error) {
    console.error('❌ step2.vue: Failed to load step data:', error);

    // 即使 API 載入失敗，也要確保陣列欄位存在
    if (!Array.isArray(localFormData.crops)) {
      localFormData.crops = [];
    }

    if (!Array.isArray(localFormData.owners)) {
      localFormData.owners = [];
    }
  } finally {
    initGuard.isDataLoading = false;

    // 延遲設定初始化完成，確保所有副作用完成後才允許事件發送
    nextTick(() => {
      // 增加額外延遲，確保所有計算屬性和 watch 都已穩定
      setTimeout(() => {
        initGuard.isInitialized = true;
        initGuard.isInitializing = false;

        // 初始驗證（現在有保護機制）
        validateForm();

        console.log('🎉 step2.vue: Initialization completed, events now enabled');
      }, 100); // 100ms 延遲確保所有副作用完成
    });
  }
};

// 事件驅動架構:組件掛載時自主載入資料
onMounted(async () => {
  console.log('🔧 step2.vue: Component mounted, starting initialization');

  // 初始化 domicile store
  await domicileStore.loadCounties();

  // 自主載入步驟資料
  await loadStepData();
});

// 事件驅動架構:監聽本地表單資料變更
watch(localFormData, () => {
  // 🔥 修復問題2：在初始化期間不觸發更新，避免重置資料庫資料
  if (!initGuard.isInitializing && initGuard.isInitialized) {
    updateFormData();
  }
}, { deep: true });

// Watch for dialog open/close to initialize/cleanup map
watch(landInfoDialog, (isOpen) => {
  if (isOpen) {
    // Initialize map when dialog opens
    nextTick(() => {
      initMap();
    });
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

// Auto-detect indigenous area based on town selection
const checkAndUpdateIndigenousArea = (townId: number) => {
  const town = domicileStore.getTownById(townId);
  if (town) {
    // Set isAboriginalArea to true if the town is indigenous (indigenous_type = 1)
    const isIndigenous = town.is_indigenous || town.indigenous_type === '1';
    if (localFormData.isAboriginalArea !== isIndigenous) {
      localFormData.isAboriginalArea = isIndigenous;
      // 在初始化期間不觸發事件
      if (!initGuard.isInitializing) {
        eventEmitter.emitDataChanged();
      }
    }
  }
};

// Watchers for automatic town/village loading and indigenous area detection
watch(() => localFormData.landCounty, async (newCounty) => {
  if (newCounty && !initGuard.isInitializing) {
    localFormData.landTown = '';
    localFormData.landSec = '';
    await loadTownsForCounty(newCounty);
  }
});

watch(() => localFormData.landTown, async (newTown) => {
  if (newTown && !initGuard.isInitializing) {
    localFormData.landSec = '';
    const townId = typeof newTown === 'number' ? newTown : parseInt(newTown);
    await loadVillagesForTown(townId);
    checkAndUpdateIndigenousArea(townId);
  }
});

watch(() => localFormData.ownerCounty, async (newCounty) => {
  if (newCounty && !initGuard.isInitializing) {
    localFormData.ownerTown = '';
    localFormData.ownerVillage = '';
    await loadTownsForCounty(newCounty);
  }
});

watch(() => localFormData.ownerTown, async (newTown) => {
  if (newTown && !initGuard.isInitializing) {
    localFormData.ownerVillage = '';
    const townId = typeof newTown === 'number' ? newTown : parseInt(newTown);
    await domicileStore.loadVillagesByTownId(townId);
  }
});

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

.map-container {
  position: relative;
}

.feature-info-card {
  position: absolute;
  top: 10px;
  right: 10px;
  width: 200px;
  max-width: 40%;
  background: white;
  z-index: 100;
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

/* 日期選擇器對話框樣式 */
.date-picker-dialog {
  border-radius: 12px;
}

.date-picker-dialog .v-card-title {
  border-top-left-radius: 12px;
  border-top-right-radius: 12px;
}

/* 日期預覽 alert 樣式 */
/* Removed empty rule for .v-alert--variant-tonal */

/* 日期選擇器下拉選單樣式 */
:deep(.v-select .v-field__input) {
  font-weight: 500;
}

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
