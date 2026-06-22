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
                    查無此地號圖資
                  </div>
                  <div class="text-body-2 text-grey-darken-1 mb-4">
                    目前系統中沒有此地號的地號圖資資料
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
                <!-- Loading 狀態 -->
                <div
                  v-if="isCadastralLoading"
                  class="d-flex flex-column align-center justify-center py-4"
                >
                  <v-progress-circular
                    indeterminate
                    color="#3ea0a3"
                    :size="40"
                    :width="3"
                  />
                  <div class="text-caption text-grey-darken-1 mt-2">
                    正在載入地籍資料...
                  </div>
                </div>

                <!-- 資料載入完成 -->
                <template v-else>
                  <div v-if="selectedFeatureInfo.Land_no">
                    <strong>地號:</strong> {{ selectedFeatureInfo.Land_no }}
                  </div>
                  <!-- <div v-if="selectedFeatureInfo.SECT">
                    <strong>地段號:</strong> {{ selectedFeatureInfo.SECT }}
                  </div> -->
                  <div v-if="selectedFeatureInfo.section">
                    <strong>地段:</strong> {{ selectedFeatureInfo.section }}
                  </div>
                  <div v-if="selectedFeatureInfo.area">
                    <strong>面積:</strong> {{ Number(selectedFeatureInfo.area).toFixed(2) }} 平方公尺
                    <!-- <span class="text-caption text-grey-darken-1">
                      ({{ (Number(selectedFeatureInfo.area) / 3.305785).toFixed(2) }} 坪)
                    </span> -->
                    <div class="text-caption text-grey-darken-1">
                      來源: {{ selectedFeatureInfo.areaSource || '地籍登記面積 (NLSC)' }}
                    </div>
                  </div>
                  <div v-if="selectedFeatureInfo.LANDUSE_NAME">
                    <strong>土地使用分區:</strong> {{ selectedFeatureInfo.LANDUSE_NAME }}
                    <span v-if="selectedFeatureInfo.LANDUSE" class="text-caption text-grey-darken-1">
                      ({{ selectedFeatureInfo.LANDUSE }})
                    </span>
                  </div>
                  <div v-if="selectedFeatureInfo.LANDDETATIS_NAME">
                    <strong>使用地類別:</strong> {{ selectedFeatureInfo.LANDDETATIS_NAME }}
                    <span v-if="selectedFeatureInfo.LANDDETATIS" class="text-caption text-grey-darken-1">
                      ({{ selectedFeatureInfo.LANDDETATIS }})
                    </span>
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
                </template>
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
                <div class="font-weight-medium">
                  {{ landParcelNotFoundTitle }}
                </div>
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
        <!-- 🆕 唯讀模式提示（硬鎖定） -->
        <v-alert
          v-if="props.readonly && grantsStore.currentGrant?.status !== 'rejected'"
          type="warning"
          variant="tonal"
          density="compact"
          class="mb-4"
          rounded="lg"
        >
          <div class="d-flex align-center">
            <span class="text-body-2">
              {{ grantsStore.currentGrant?.status === 'submitted'
                ? '已完成結案申報，此步驟已鎖定，無法編輯。'
                : '已完成申報並送審，此步驟已鎖定，無法編輯。' }}
            </span>
          </div>
        </v-alert>

        <!-- 軟鎖定警告 -->
        <v-alert
          v-if="props.softLocked && !props.readonly"
          color="warning"
          variant="tonal"
          density="compact"
          class="mb-4"
          rounded="lg"
        >
          <div class="d-flex align-center">
            <v-icon
              class="me-2"
              size="small"
            >mdi-alert</v-icon>
            <span class="text-body-2">
              已完成現場勘查，修改此步驟資料可能導致勘查結果無效，請謹慎編輯。
            </span>
          </div>
        </v-alert>

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
                v-if="landManagement.lands.length > 0 && !props.readonly"
                color="#3ea0a3"
                variant="flat"
                rounded="lg"
                size="small"
                :disabled="props.readonly"
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
                    @click="!props.readonly && editLand(land.id)"
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
                          v-if="!props.readonly"
                          icon
                          size="x-small"
                          color="error"
                          variant="text"
                          @click.stop="requestDeleteLand(land.id)"
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
                        :disabled="props.readonly"
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
                    :items="filteredCounties"
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
                    :items="filteredTowns"
                    item-title="displayTitle"
                    item-value="value"
                    :item-props="(item: any) => ({
                      disabled: item.disabled,
                      class: item.disabled ? 'text-grey' : ''
                    })"
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
                    <template #item="{ props, item }">
                      <v-list-item
                        v-bind="props"
                        :disabled="item.raw.disabled"
                      >
                        <template #title>
                          <span>{{ item.raw.title }}</span>
                          <span
                            v-if="item.raw.disabled && item.raw.requiredType"
                            class="text-caption text-grey ml-1"
                          >
                            (不屬於{{ item.raw.requiredType }}區)
                          </span>
                        </template>
                      </v-list-item>
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
                              <v-text-field
                                v-model="formattedLandNumberMain"
                                variant="outlined"
                                density="compact"
                                color="#3ea0a3"
                                bg-color="white"
                                pattern="[0-9]*"
                                maxlength="4"
                                style="width: 90px"
                                hide-details
                                placeholder="0000"
                                autocomplete="off"
                                :rules="[v => !!v || '請輸入主地號']"
                                @focus="landNumberMainFocused = true"
                                @blur="onLandNumberMainBlur"
                                @input="onLandNumberMainInput"
                              >
                                <template #label>
                                  母地號
                                </template>
                              </v-text-field>
                            </div>

                            <!-- 分隔符號 -->
                            <div class="mx-2">
                              <v-icon
                                size="20"
                                color="grey"
                              >
                                mdi-minus
                              </v-icon>
                            </div>

                            <!-- 子地號輸入 -->
                            <div class="me-3">
                              <v-text-field
                                v-model="formattedLandNumberSub"
                                variant="outlined"
                                density="compact"
                                color="#3ea0a3"
                                bg-color="white"
                                pattern="[0-9]*"
                                maxlength="4"
                                style="width: 90px"
                                hide-details
                                placeholder="0000"
                                autocomplete="off"
                                @focus="landNumberSubFocused = true"
                                @blur="onLandNumberSubBlur"
                                @input="onLandNumberSubInput"
                              >
                                <template #label>
                                  子地號
                                </template>
                              </v-text-field>
                            </div>

                            <!-- 查詢按鈕 -->
                            <div class="d-flex gap-3">
                              <v-btn
                                color="#3ea0a3"
                                variant="outlined"
                                rounded="lg"
                                class="px-2"
                                :disabled="!localFormData.landNumberMain || !localFormData.landSec"
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
                      @blur="() => { const v = parseFloat(localFormData.landArea); if (!isNaN(v)) localFormData.landArea = m2Truncate(v) }"
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
                      @blur="() => { const v = parseFloat(localFormData.facilityArea); if (!isNaN(v)) localFormData.facilityArea = m2Truncate(v) }"
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

    <!-- Delete land confirmation dialog -->
    <v-dialog
      v-model="showDeleteLandDialog"
      max-width="400px"
      persistent
    >
      <v-card rounded="lg">
        <v-card-title
          class="text-subtitle-1 font-weight-bold pa-4 d-flex align-center"
          style="color: #c62828; background-color: #ffebee;"
        >
          <v-icon
            color="error"
            class="me-2"
            size="small"
          >
            mdi-alert-circle
          </v-icon>
          <span>確認刪除土地</span>
        </v-card-title>

        <v-card-text class="pa-4">
          <p class="text-body-1">
            確定要刪除這筆土地資料嗎？
          </p>
          <p class="text-body-2 text-grey-darken-1 mt-1">
            此操作無法復原，土地資料將永久移除。
          </p>
        </v-card-text>

        <v-card-actions class="pa-4 pt-0">
          <v-spacer />
          <v-btn
            variant="text"
            @click="showDeleteLandDialog = false"
          >
            取消
          </v-btn>
          <v-btn
            color="error"
            variant="flat"
            @click="confirmDeleteLand"
          >
            確認刪除
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup lang="ts">
import Big from 'big.js';
// Import OpenLayers dependencies
import 'ol/ol.css';
import { Map, View } from 'ol';
import TileLayer from 'ol/layer/Tile';
import WMTS from 'ol/source/WMTS';
import WMTSTileGrid from 'ol/tilegrid/WMTS';
import { get as getProjection } from 'ol/proj';
import { getWidth } from 'ol/extent';
import { fromLonLat, transform } from 'ol/proj';
import { Polygon, MultiPolygon } from 'ol/geom';
import { Vector as VectorLayer } from 'ol/layer';
import { Vector as VectorSource } from 'ol/source';
import { Style, Icon, Stroke, Fill } from 'ol/style';
import GeoJSON from 'ol/format/GeoJSON';
import { Select, Modify } from 'ol/interaction';
import { click } from 'ol/events/condition';
import { unByKey } from 'ol/Observable';
import type { EventsKey } from 'ol/events';
import { getArea } from 'ol/sphere';
import { debounce } from 'lodash-es';
import type { Feature } from 'ol';
import type { Geometry } from 'ol/geom';
import { queryOfficeBoundaries, queryCountyBoundaries } from '@/services/spatialService';

// Define type for selected feature info
interface SelectedFeatureInfo {
  Land_no?: string;       // 地號（格式：####-####）
  section?: string;       // 地段名稱
  area?: string | number; // 面積（平方公尺，多個 polygon 時為總和）
  areaSource?: string;    // 面積來源（地籍登記面積、測量面積、地圖幾何計算）

  // NLSC GML 欄位（從 CadasMapQuery API 獲取）
  LANDNO?: string;        // GML 地號 8 碼（例如：00010000）
  SECT?: string;          // GML 地段代碼（例如：0532）
  CITY?: string;          // 縣市（例如：臺中市）
  TOWN?: string;          // 鄉鎮市區（例如：南區）
  OFFICE?: string;        // 地政事務所代碼（例如：BA）
  AREA?: number;          // GML 面積（平方公尺）
  Sec_cns?: string;       // 地段中文名稱（用於顯示）

  // 土地使用分區（從 CSV 對照表解析）
  LANDUSE?: string;           // 土地使用分區代碼（例：AA、AF）
  LANDDETATIS?: string;       // 使用地類別代碼（例：EA、ES）
  LANDUSE_NAME?: string;      // 土地使用分區中文名稱
  LANDDETATIS_NAME?: string;  // 使用地類別中文名稱

  [key: string]: unknown;
}

// 定義單筆土地資料結構
interface LandData {
  id: string; // 唯一識別碼
  // 設施地段
  landCounty: string | number;
  landTown: string | number;
  landSec: string | number | null;
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

  // 使用地類別代碼（來自 NLSC LANDDETATIS，供後續步驟使用）
  landDetatisCode?: string;
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
import { useCropsStore } from '@/stores/crops';
import {
  queryCadastralMap,
  queryCadastralMapByPoint,
  validateLandNumber,
  type CadastralQueryParams
} from '@/services/cadastralMapService';
import type { LandSection } from '@/services/landSectionNlscService';
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
// 新增 readonly 和 softLocked prop 支援
const props = withDefaults(defineProps<{
  currentStep: number;
  readonly?: boolean;
  softLocked?: boolean;
}>(), {
  readonly: false,
  softLocked: false
})

// Reference to map element and map instance
const mapElement = ref(null);
let map: Map | null = null;

// 📦 GeoJSON Source Cache (Static File Strategy)
// Current: Load 13MB land_parcels.geojson once, cache forever, filter in frontend
// 已移除 sharedGeoJSONSource - 改用 NLSC API 按需查詢，不再需要快取整個 GeoJSON

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
const cropsStore = useCropsStore();

// 統一步驟組件架構：初始化保護與事件管理系統
interface StepInitializationGuard {
  isInitialized: boolean
  isInitializing: boolean
  isDataLoading: boolean
}

interface StepEventEmitter {
  emitDataChanged: (immediate?: boolean) => void  // 🔥 添加 immediate 參數
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
        console.log(`[step2.vue] Skipping event emission during initialization (${fn.name})`)
      }
      return result
    }) as T
  },

  // 創建受保護的 Watch 函數
  createProtectedWatch: <T extends (...args: unknown[]) => unknown>(fn: T): T => {
    return ((...args: unknown[]) => {
      if (guard.isInitializing) {
        console.log(`[step2.vue] Skipping watch execution during initialization (${fn.name})`)
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
  emit: ((evt: "step-data-changed", eventData: { step: number; data: Record<string, unknown>; valid: boolean; immediate?: boolean; }) => void) &
        ((evt: "validation-changed", eventData: { step: number; valid: boolean; }) => void) &
        ((evt: "ready-to-proceed", eventData: { step: number; data: Record<string, unknown>; }) => void) &
        ((evt: "go-back-requested", eventData: { step: number; }) => void),
  formData: Record<string, unknown>,
  validationState: Ref<boolean>,
  guard: StepInitializationGuard
): StepEventEmitter => {
  // 內部 emit 邏輯（可被 debounce 或立即調用）
  const emitDataChangedInternal = (immediate = false) => {
    if (!guard.isInitialized || guard.isInitializing) return

    // 只發送持久化資料（lands 陣列 + 計算欄位），單筆編輯欄位不發送
    const persistentData = {
      lands: formData.lands,
      totalFacilityArea: formData.totalFacilityArea,
      totalFacilityAreaHa: formData.totalFacilityAreaHa,
      valid: formData.valid
    }

    emit('step-data-changed', {
      step: stepNumber,
      data: persistentData,
      valid: validationState.value,
      immediate
    })
  }

  const debouncedEmitDataChanged = debounce(() => emitDataChangedInternal(false), 300)

  return {
    emitDataChanged: (immediate = false) => {
      if (!guard.isInitialized || guard.isInitializing) {
        console.log(`step${stepNumber}.vue: Skipping event emission during initialization`)
        return
      }
      // 🔥 如果 immediate=true，立即發送事件；否則使用 debounce
      if (immediate) {
        emitDataChangedInternal(true)
      } else {
        debouncedEmitDataChanged()
      }
    },

    emitValidationChanged: (valid: boolean) => {
      if (!guard.isInitializing && guard.isInitialized) {
        emit('validation-changed', { step: stepNumber, valid })
      } else {
        console.log(`step${stepNumber}.vue: Skipping validation event emission during initialization`)
      }
    },

    emitReadyToProceed: () => {
      console.log(`step${stepNumber}.vue: Emitting ready-to-proceed event`)
      emit('ready-to-proceed', {
        step: stepNumber,
        data: { ...formData }
      })
    },

    emitGoBackRequested: () => {
      console.log(`[step${stepNumber}.vue] Emitting go-back-requested event`)
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
  // loadLandSectionsByTownId: (townId: number) => Promise<void | null>
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
    console.log('Loading cascade data for address fields...')

    try {
      // 載入設施地址的級聯資料
      if (formData.landCounty) {
        console.log('Loading towns for landCounty:', formData.landCounty)
        await loadTownsForCounty(formData.landCounty as string | number)

        if (formData.landTown) {
          console.log('Loading sections for landTown:', formData.landTown)
          // 檢查是否為特殊城市代碼，如果是則跳過
          const isSpecialCityCode = formData.landTown === 'O01' || formData.landTown === 'I01';
          if (!isSpecialCityCode) {
            await loadLandSections(true); // 保留選擇
          }
        }
      }

      // 載入所有權人地址的級聯資料
      if (formData.ownerCounty) {
        console.log('Loading towns for ownerCounty:', formData.ownerCounty)
        await loadTownsForCounty(formData.ownerCounty as string | number)

        if (formData.ownerTown) {
          console.log('Loading villages for ownerTown:', formData.ownerTown)
          const townId = typeof formData.ownerTown === 'number' ? formData.ownerTown : parseInt(formData.ownerTown as string)
          await domicileStore.loadVillagesByTownId(townId)
        }
      }

      console.log('Cascade data loaded successfully')
    } catch (error) {
      console.error('Failed to load cascade data:', error)
    }
  },

  resetCascadeSelections: (level: 'county' | 'town' | 'village') => {
    // 🔥 修復：防止載入時錯誤清空級聯選擇
    if (guard.isInitializing) {
      console.log('resetCascadeSelections blocked during data loading')
      return
    }

    console.log(`resetCascadeSelections: ${level}`)
    switch (level) {
      case 'county':
        formData.landTown = ''
        formData.landSec = null
        console.log('  → Cleared landTown and landSec')
        break
      case 'town':
        formData.landSec = null
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
          console.log('step2.vue: Skipping validation event emission during initialization')
        }

        return valid
      }
      return true
    },

    // 統一的資料更新
    updateFormData: () => {
      // 在初始化期間不執行更新,避免重置資料庫資料
      if (!guard.isInitialized || guard.isInitializing) {
        console.log('step2.vue: Skipping updateFormData during initialization')
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
  landSec: null,

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
  }>,
  landDetatisCode: ''
})

// 事件驅動架構：創建初始表單資料函數
// 🔥 Good Taste: 保持扁平結構，單筆欄位用於 UI 綁定，發送時只送 lands 陣列 + 計算欄位
const createInitialFormData = () => ({
  // 多筆土地資料陣列（發送給後端的唯一持久化資料）
  lands: [] as LandData[],

  // 計算欄位（從 lands 陣列即時計算，發送給後端）
  totalFacilityArea: 0,
  totalFacilityAreaHa: 0,

  // 單筆土地編輯欄位（用於 v-model 綁定，不發送給後端）
  // Facility address section
  landCounty: '' as string | number,
  landTown: '' as string | number,
  landSec: null as string | number | null,
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

  // 使用地類別代碼（暫存，用於 createLandFromCurrentForm 讀取）
  landDetatisCode: '',

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
    owners: [...localFormData.owners],
    landDetatisCode: localFormData.landDetatisCode || ''
  }),

  loadLandToCurrentForm: (land: LandData, skipProtection = false): void => {
    console.log('[step2.vue] loadLandToCurrentForm - Starting land data load...', skipProtection ? '(外層保護)' : '')

    // 暫時標記為載入模式，防止級聯重置（除非外層已經開啟保護）
    const needProtection = !skipProtection && !initGuard.isInitializing
    if (needProtection) {
      initGuard.isInitializing = true
      isLandNumberUpdateProgrammatic.value = true
      console.log('loadLandToCurrentForm - 開啟載入保護')
    } else {
      console.log('loadLandToCurrentForm - 跳過保護（外層已管理）')
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

      // console.log('[step2.vue] loadLandToCurrentForm - Data loaded:')
      // console.log('  landCounty:', localFormData.landCounty, typeof localFormData.landCounty)
      // console.log('  landTown:', localFormData.landTown, typeof localFormData.landTown)
      // console.log('  landSec:', localFormData.landSec, typeof localFormData.landSec)
      // console.log('  landNumberMain:', localFormData.landNumberMain)
      // console.log('  landNumberSub:', localFormData.landNumberSub)

    } finally {
      // 使用 nextTick 確保 Vue 響應性更新完成後再開啟級聯重置（僅當由此函數開啟保護時）
      if (needProtection) {
        nextTick(() => {
          initGuard.isInitializing = false
          isLandNumberUpdateProgrammatic.value = false
          console.log('loadLandToCurrentForm - 載入保護已關閉')
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

// 存儲當前查詢到的地籍 feature（用於「使用此地號」功能）
const currentCadastralFeature = ref<Feature<Geometry> | null>(null);

// 地籍圖資料載入狀態
const isCadastralLoading = ref(false);

// 無地段圖資提示 overlay 狀態
const noSectionDataOverlay = ref(false);

// 查無地號提示 alert 狀態
const landParcelNotFoundAlert = ref(false);
const landParcelNotFoundTitle = ref('查無此地號');
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

// 顯示縣市名稱（處理代碼轉換）
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

// 🌾 Crop data - 從資料庫動態載入（透過 cropsStore）
const cropCategories = computed(() => cropsStore.categoryNames);

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

// 獲取其他土地資料（排除當前編輯的土地）
const otherLands = computed(() => {
  if (!landManagement.isEditingMode || !landManagement.currentEditingLandId) {
    return landManagement.lands;
  }
  return landManagement.lands.filter(land => land.id !== landManagement.currentEditingLandId);
});

// 編輯模式下的縣市選項過濾
const filteredCounties = computed(() => {
  // 客戶需求修改（2025-11-08）：
  // 第二筆土地的縣市不做限制，只限制鄉鎮市區的原住民屬性
  return counties.value;
});

// 編輯模式下的鄉鎮市區選項過濾
const filteredTowns = computed(() => {
  const allTowns = towns.value;

  // 新增模式或沒有其他土地資料時，返回所有選項（都可選）
  if (!landManagement.isEditingMode || otherLands.value.length === 0) {
    return allTowns.map(town => ({
      ...town,
      displayTitle: town.title,
      disabled: false
    }));
  }

  // 客戶需求修改（2025-11-08）：
  // 第二筆土地的鄉鎮市區必須與第一筆土地的 isAboriginalArea 特性相同
  // UX 改進：顯示所有選項，但禁用不符合條件的選項

  // 獲取第一筆土地的原住民區域特性
  const firstLand = otherLands.value[0];
  if (!firstLand) {
    return allTowns.map(town => ({
      ...town,
      displayTitle: town.title,
      disabled: false
    }));
  }

  const requiredIsAboriginal = firstLand.isAboriginalArea;

  // 返回所有選項，但標記不符合條件的為 disabled
  return allTowns.map(town => {
    // 使用 domicileStore.getTownById 獲取完整的 Town 資料（包含 is_indigenous）
    const townData = domicileStore.getTownById(Number(town.value));

    if (!townData) {
      return {
        ...town,
        displayTitle: town.title,
        disabled: true
      };
    }

    // 檢查該鄉鎮市區的原住民屬性是否與第一筆土地相同
    const isIndigenous = townData.is_indigenous || townData.indigenous_type === '1';
    const isDisabled = isIndigenous !== requiredIsAboriginal;

    return {
      ...town,
      displayTitle: town.title,  // 顯示在選中狀態的文字（不含提示）
      disabled: isDisabled,
      requiredType: requiredIsAboriginal ? '原民' : '非原民'  // 用於提示文字
    };
  });
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
      office: section.office,
      // 保留 NLSC API 欄位供地籍圖查詢使用
      county_land_code: section.county_land_code,
      town_land_code: section.town_land_code,
      office_name: section.office_name
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

  console.log('[step2.vue] 匹配結果:', found ? { code: found.code, name: found.name } : '未找到');
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
      // console.log('地段選擇:', { code: sectionCode, name: localFormData.landSecName });
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
// const getSpecialCityDisplayText = (): string => {
//   if (!localFormData.landCounty) return '';
//   const countyId = typeof localFormData.landCounty === 'number'
//     ? localFormData.landCounty
//     : parseInt(localFormData.landCounty);
//   const county = domicileStore.countyOptions.find(c => c.value === countyId);
//   if (!county) return '';
//   const cityInfo = specialCities[county.title];
//   return cityInfo ? cityInfo.name : '';
// };

// 保留原本的 villages 計算屬性供其他功能使用
// const villages = computed(() => {
//   if (!localFormData.landTown) return [];
//   const townId = typeof localFormData.landTown === 'number'
//     ? localFormData.landTown
//     : parseInt(localFormData.landTown);
//   return domicileStore.getLandSectionsForTownId(townId);
// });

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
  return localFormData.cropCategory ? cropsStore.getCropNamesForCategory(localFormData.cropCategory) : [];
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
const isStep2OfflineTrainingMode = import.meta.env.VITE_STEP2_OFFLINE_TRAINING === 'true';
const offlineTrainingSectionCodes = (import.meta.env.VITE_STEP2_OFFLINE_SECTIONS || 'KA0003,QE0907,BG5409,DF4350')
  .split(',')
  .map((code: string) => code.trim().toUpperCase())
  .filter(Boolean);
const offlineTrainingFeatures = ref<Feature<Geometry>[]>([]);
const offlineTrainingSections = ref<LandSection[]>([]);
let offlineTrainingLoadPromise: Promise<void> | null = null;
// 土地使用分區對照表（CSV 靜態資源，onMounted 時載入一次）
const landUseCodeMap = ref<Record<string, string>>({});
const landDetatisCodeMap = ref<Record<string, string>>({});
const landUseClassLoaded = ref(false);

const loadLandUseClassification = async () => {
  if (landUseClassLoaded.value) return;
  try {
    const response = await fetch('/land_use_classification.csv');
    if (!response.ok) throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    const text = await response.text();
    const lines = text.trim().split('\n').slice(1); // skip header
    for (const line of lines) {
      const cols = line.split(',').map(c => c.replace(/"/g, '').trim());
      const [landuse, landdetatis, name] = cols;
      if (landuse && !landUseCodeMap.value[landuse]) {
        landUseCodeMap.value[landuse] = name;
      } else if (landdetatis && !landDetatisCodeMap.value[landdetatis]) {
        landDetatisCodeMap.value[landdetatis] = name;
      }
    }
    landUseClassLoaded.value = true;
  } catch (error) {
    console.error('[step2.vue] 載入土地分類對照表失敗:', error);
  }
};

const convertLandUseCodeToName = (code: string): string =>
  landUseCodeMap.value[code] || code;

const convertLandDetatisCodeToName = (code: string): string =>
  landDetatisCodeMap.value[code] || code;

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

// 當設施地段（縣市/鄉鎮/地段）變更時，重置相關資訊
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

  console.log('已重置地號、坐標、面積、作物資訊');
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

// Blur handlers: normalize to 4-digit padded format without triggering clearLocationAndAreaInfo
const onLandNumberMainBlur = () => {
  landNumberMainFocused.value = false;
  if (localFormData.landNumberMain) {
    const padded = (localFormData.landNumberMain.replace(/^0+/, '') || '0').padStart(4, '0');
    if (padded !== localFormData.landNumberMain) {
      isLandNumberUpdateProgrammatic.value = true;
      localFormData.landNumberMain = padded;
      updateLandNumber();
      setTimeout(() => { isLandNumberUpdateProgrammatic.value = false; }, 0);
    }
  }
};

const onLandNumberSubBlur = () => {
  landNumberSubFocused.value = false;
  if (localFormData.landNumberSub) {
    const padded = (localFormData.landNumberSub.replace(/^0+/, '') || '0').padStart(4, '0');
    if (padded !== localFormData.landNumberSub) {
      isLandNumberUpdateProgrammatic.value = true;
      localFormData.landNumberSub = padded;
      updateLandNumber();
      setTimeout(() => { isLandNumberUpdateProgrammatic.value = false; }, 0);
    }
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
    // Store value as-is; padStart normalization happens on blur
    const newValue = val || '';
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
    // Store value as-is; padStart normalization happens on blur
    const newValue = val || '';
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
    return !isNaN(area) ? m2ToHa(area) : '';
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

// 平方公尺截斷至小數第 2 位（不四捨五入）
const m2Truncate = (m2: number): string =>
  new Big(m2).round(2, Big.roundDown).toString()

// 平方公尺轉公頃，截斷至第 6 位小數（不四捨五入）
const m2ToHa = (m2: number): string =>
  new Big(m2).div(10000).round(6, Big.roundDown).toString()

const facilityAreaHaComputed = computed({
  get: () => {
    if (!localFormData.facilityArea) return '';
    const area = parseFloat(localFormData.facilityArea);
    return !isNaN(area) ? m2ToHa(area) : '';
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
      const calculatedValue = new Big(landArea).times(share1).div(share2).round(1, Big.roundDown).toString();
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
    const area = land.facilityArea || '0'
    return new Big(total).plus(isNaN(parseFloat(area)) ? 0 : area).toNumber()
  }, 0)
})

const totalFacilityAreaHa = computed(() => {
  return landManagement.lands.reduce((total, land) => {
    const area = land.facilityAreaHa || '0'
    return new Big(total).plus(isNaN(parseFloat(area)) ? 0 : area).toNumber()
  }, 0)
})

// 追蹤上一次的面積值，用於檢測變化
const previousTotalFacilityArea = ref<number>(0)

// 監聽計算欄位變化，自動同步到 localFormData 以便發送給後端
watch([totalFacilityArea, totalFacilityAreaHa], async ([area, areaHa], [oldArea]) => {
  localFormData.totalFacilityArea = area
  localFormData.totalFacilityAreaHa = areaHa

  // 當設施面積發生變化時，清除 step4 和 step5 的資料
  // 因為補助額度計算依賴面積，面積變更後原有設施資料可能不再適用
  // 修正：統一架構後 UI step N = data step N
  if (previousTotalFacilityArea.value !== 0 && oldArea !== area && grantsStore.caseNumber) {
    // Phase 1: 從 API 查詢實際資料狀態（單一真實來源）
    const checkStepHasData = async (step: number): Promise<boolean> => {
      try {
        // 從 API 載入步驟資料
        const data = await grantsStore.loadStepData(grantsStore.caseNumber!, step)

        // 排除元資料欄位，檢查是否有業務資料
        const metadata_fields = ['_caseNumber', 'valid', 'case_number', 'id', 'current_step', 'status']
        const actualDataKeys = Object.keys(data || {}).filter(
          key => !metadata_fields.includes(key)
        )

        const hasData = actualDataKeys.length > 0
        console.log(`[Step2] Step ${step} API 檢查: ${hasData ? '有資料' : '無資料'} (${actualDataKeys.length} 個業務欄位)`)
        return hasData
      } catch (error) {
        console.error(`[Step2] 檢查 Step ${step} 失敗:`, error)
        return false  // API 失敗時保守判斷（不清除）
      }
    }

    const hasStep4Data = await checkStepHasData(4)
    const hasStep5Data = await checkStepHasData(5)

    if (hasStep4Data || hasStep5Data) {
      // 顯示提示說明（不提供取消選項）
      alert(
        '設施面積已變更！\n\n' +
        `原面積：${(Big(oldArea).div(10000).round(6, Big.roundDown).toString())} 公頃\n` +
        `新面積：${(Big(area).div(10000).round(6, Big.roundDown).toString())} 公頃\n\n` +
        '面積變更會影響補助額度計算，系統將自動清除以下步驟的資料：\n' +
        (hasStep4Data ? '• Step 4 - 灌溉調控設施\n' : '') +
        (hasStep5Data ? '• Step 5 - 田間管路設施\n' : '') +
        '\n請於清除後重新填寫設施資訊。'
      )

      try {
        // Phase 1: 使用新的原子性清除方法
        const clearFailures: number[] = []

        if (hasStep4Data) {
          console.log('[Step2] 清除 Step4 資料（面積變更）')
          const success = await grantsStore.clearStepData(4)
          if (!success) {
            clearFailures.push(4)
          }
        }

        if (hasStep5Data) {
          console.log('[Step2] 清除 Step5 資料（面積變更）')
          const success = await grantsStore.clearStepData(5)
          if (!success) {
            clearFailures.push(5)
          }
        }

        // 檢查是否有清除失敗
        if (clearFailures.length > 0) {
          alert(`清除步驟 ${clearFailures.join(', ')} 資料失敗，請稍後再試。`)
        } else {
          alert('已成功清除相關步驟資料，請重新填寫設施資訊。')
        }
      } catch (error) {
        console.error('清除步驟資料時發生例外:', error)
        alert('清除步驟資料時發生錯誤，請稍後再試。')
      }
    }
  }

  // 更新追蹤值
  previousTotalFacilityArea.value = area
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

const normalizeSectionCode = (code: unknown): string => String(code || '').trim().toUpperCase();

const normalizeLandNo8 = (landNo: unknown): string => {
  const digits = String(landNo || '').replace(/\D/g, '');
  return digits ? digits.padStart(8, '0').slice(-8) : '';
};

const formatLandNoForDisplay = (landNo8: string): string => {
  if (!landNo8) return '';
  const normalized = normalizeLandNo8(landNo8);
  if (!normalized) return '';
  return `${normalized.substring(0, 4)}-${normalized.substring(4, 8)}`;
};

const toLandNo8FromParts = (main: string, sub: string): string => {
  const mainPart = String(main || '').replace(/\D/g, '').padStart(4, '0').slice(-4);
  const subPart = String(sub || '0').replace(/\D/g, '').padStart(4, '0').slice(-4);
  return `${mainPart}${subPart}`;
};

const extractOfflineLandNo8 = (properties: Record<string, unknown>): string => {
  const fromGml = normalizeLandNo8(properties.LANDNO);
  if (fromGml) return fromGml;

  const rawLandNo = String(properties.Land_no || '').trim();
  if (!rawLandNo) return '';

  const [main = '', sub = '0'] = rawLandNo.split('-');
  return toLandNo8FromParts(main, sub);
};

const getOfflineSectionName = (properties: Record<string, unknown>): string => {
  return String(properties.Sec_cns || properties.section || properties.Section || properties.SECT || '').trim();
};

const normalizeOfflineFeature = (feature: Feature<Geometry>, index: number) => {
  const properties = feature.getProperties() as Record<string, unknown>;
  const normalizedSectionCode = normalizeSectionCode(properties.SECT || properties.Section || properties.section);
  const normalizedLandNo8 = extractOfflineLandNo8(properties);
  const sectionName = getOfflineSectionName(properties) || normalizedSectionCode;

  const areaFromProperties = Number(properties.Desc_area ?? properties.Map_area ?? properties.AREA ?? 0);
  const normalizedArea = Number.isFinite(areaFromProperties) ? areaFromProperties : undefined;

  feature.setProperties({
    ...properties,
    SECT: normalizedSectionCode,
    LANDNO: normalizedLandNo8,
    Land_no: formatLandNoForDisplay(normalizedLandNo8),
    AREA: normalizedArea,
    Sec_cns: sectionName,
    // 標記資料來源，方便除錯與後續追蹤
    source: 'offline-training'
  }, true);

  if (!feature.getId()) {
    feature.setId(`offline-${normalizedSectionCode}-${normalizedLandNo8 || index}`);
  }
};

const buildOfflineTrainingSections = (features: Feature<Geometry>[]): LandSection[] => {
  const sectionMap: Record<string, LandSection> = {};

  features.forEach(feature => {
    const properties = feature.getProperties() as Record<string, unknown>;
    const sectionCode = normalizeSectionCode(properties.SECT || properties.Section);

    if (!sectionCode || sectionMap[sectionCode]) {
      return;
    }

    sectionMap[sectionCode] = {
      code: sectionCode,
      name: getOfflineSectionName(properties) || sectionCode,
      office: String(properties.office || properties.OFFICE || 'OFFLINE'),
      office_name: String(properties.office_name || properties.OFFICE || '離線訓練資料'),
      county_land_code: String(properties.county_land_code || ''),
      town_land_code: String(properties.town_land_code || '')
    };
  });

  const sectionList: LandSection[] = [];
  for (const sectionCode in sectionMap) {
    sectionList.push(sectionMap[sectionCode]);
  }

  return sectionList.sort((a, b) => a.code.localeCompare(b.code));
};

const ensureOfflineTrainingDataLoaded = async () => {
  if (!isStep2OfflineTrainingMode) {
    return;
  }

  if (offlineTrainingLoadPromise) {
    await offlineTrainingLoadPromise;
    return;
  }

  offlineTrainingLoadPromise = (async () => {
    const response = await fetch('/land_parcels.geojson');
    if (!response.ok) {
      throw new Error(`載入離線地籍資料失敗: HTTP ${response.status}`);
    }

    const geoJsonData = await response.json();
    const parser = new GeoJSON();
    const allFeatures = parser.readFeatures(geoJsonData, {
      dataProjection: 'EPSG:4326',
      featureProjection: 'EPSG:3857'
    }) as Feature<Geometry>[];

    const filteredFeatures = allFeatures.filter(feature => {
      const properties = feature.getProperties() as Record<string, unknown>;
      const sectionCode = normalizeSectionCode(properties.SECT || properties.Section || properties.section);
      return offlineTrainingSectionCodes.includes(sectionCode);
    });

    filteredFeatures.forEach((feature, index) => {
      normalizeOfflineFeature(feature, index);
    });

    offlineTrainingFeatures.value = filteredFeatures;
    offlineTrainingSections.value = buildOfflineTrainingSections(filteredFeatures);

    console.log('離線訓練資料載入完成:', {
      sectionCodes: offlineTrainingSections.value.map(section => section.code),
      featureCount: offlineTrainingFeatures.value.length
    });
  })();

  try {
    await offlineTrainingLoadPromise;
  } catch (error) {
    offlineTrainingLoadPromise = null;
    throw error;
  }
};

const queryOfflineFeaturesByLandNo = (
  sectionCode: string,
  landNumberMain: string,
  landNumberSub: string
): Feature<Geometry>[] => {
  const normalizedSectionCode = normalizeSectionCode(sectionCode);
  const targetLandNo8 = toLandNo8FromParts(landNumberMain, landNumberSub || '0');

  return offlineTrainingFeatures.value.filter(feature => {
    const properties = feature.getProperties() as Record<string, unknown>;
    const featureSectionCode = normalizeSectionCode(properties.SECT || properties.Section);
    const featureLandNo8 = extractOfflineLandNo8(properties);

    return featureSectionCode === normalizedSectionCode && featureLandNo8 === targetLandNo8;
  }) as Feature<Geometry>[];
};

const queryOfflineFeatureByCoordinate = (coordinate: number[]): Feature<Geometry> | null => {
  for (const feature of offlineTrainingFeatures.value) {
    const geometry = feature.getGeometry();
    if (!geometry) continue;

    if (geometry.intersectsCoordinate(coordinate)) {
      return feature as Feature<Geometry>;
    }
  }

  return null;
};

const onCountyChange = stepManager.createCascadeHandler(async () => {
  cascadeManager.resetCascadeSelections('county');

  // 重置地段選擇和資料
  localFormData.landSec = null;
  localFormData.landSecName = '';
  nlscSections.value = [];

  // 重置地號、坐標、面積等相關資訊（從 watch 整合過來）
  resetLandRelatedInfo();

  // 強制重新渲染地段選單
  sectionSelectKey.value++;

  if (isStep2OfflineTrainingMode) {
    // 離線模式的地段使用固定資料；鄉鎮清單仍沿用既有 domicile API
    try {
      if (localFormData.landCounty) {
        const countyId = typeof localFormData.landCounty === 'number'
          ? localFormData.landCounty
          : parseInt(localFormData.landCounty);

        if (!isNaN(countyId)) {
          await domicileStore.loadTownsByCountyId(countyId);
        }
      }

      await ensureOfflineTrainingDataLoaded();
      nlscSections.value = [...offlineTrainingSections.value];
      localFormData.landTown = '';
    } catch (error) {
      console.error('離線模式載入地段失敗:', error);
      nlscSections.value = [];
    }
    return;
  }

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
          await domicileStore.loadLandSectionsByLandCodes(county.land_code, specialCode);
          // 從 store 取得載入的資料
          nlscSections.value = domicileStore.landSections.filter(s =>
            s.county_land_code === county.land_code && s.town_land_code === specialCode
          );
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
  const currentSelection = preserveSelection ? localFormData.landSec : null;

  // 重置地段選擇和資料（除非要保留選擇）
  if (!preserveSelection) {
    localFormData.landSec = null;
  }
  nlscSections.value = [];

  // 強制重新渲染地段選單
  sectionSelectKey.value++;

  // 使用 nextTick 確保重置生效
  await nextTick();

  if (isStep2OfflineTrainingMode) {
    try {
      loadingSections.value = true;
      await ensureOfflineTrainingDataLoaded();
      nlscSections.value = [...offlineTrainingSections.value];
    } catch (error) {
      console.error('離線模式載入地段失敗:', error);
      nlscSections.value = [];
    } finally {
      loadingSections.value = false;

      if (preserveSelection && currentSelection && nlscSections.value.length > 0) {
        const currentSelectionCode = normalizeSectionCode(currentSelection);
        const matchingSection = nlscSections.value.find(section =>
          normalizeSectionCode(section.code) === currentSelectionCode
        );

        localFormData.landSec = matchingSection ? matchingSection.code : currentSelection;
      }
    }

    return;
  }

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
      await domicileStore.loadLandSectionsByLandCodes(county.land_code, specialCode);
      nlscSections.value = domicileStore.landSections.filter(s =>
        s.county_land_code === county.land_code && s.town_land_code === specialCode
      );
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
      await domicileStore.loadLandSectionsByLandCodes(county.land_code, town.land_code);
      nlscSections.value = domicileStore.landSections.filter(s =>
        s.county_land_code === county.land_code && s.town_land_code === town.land_code
      );
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
        console.log('恢復地段選擇:', {
          original: currentSelection,
          matched: matchingSection.code,
          name: matchingSection.name
        });
      } else {
        // 如果找不到匹配項，保持原始選擇
        localFormData.landSec = currentSelection;
        console.log('無法找到匹配的地段，保持原始選擇:', currentSelection);
      }
    }
  }
};

const onTownChange = stepManager.createCascadeHandler(async () => {
  cascadeManager.resetCascadeSelections('town');

  // 重置地號、坐標、面積等相關資訊（從 watch 整合過來）
  resetLandRelatedInfo();

  // 載入 NLSC 地段資料
  await loadLandSections();

  // 檢查並更新原住民地區（從 watch 整合過來）
  if (localFormData.landTown) {
    const townId = typeof localFormData.landTown === 'number'
      ? localFormData.landTown
      : parseInt(localFormData.landTown);
    if (!isNaN(townId)) {
      checkAndUpdateIndigenousArea(townId);
    }
  }
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

// TODO：持分人土地功能尚未實現
const calculateTotalShare = () => {
  let totalShare = new Big(0);

  if (localFormData.owners && localFormData.owners.length > 0) {
    localFormData.owners.forEach(owner => {
      const shareParts = owner.share.split('/');
      if (shareParts.length === 2) {
        const numerator = parseFloat(shareParts[0]);
        const denominator = parseFloat(shareParts[1]);

        if (!isNaN(numerator) && !isNaN(denominator) && denominator !== 0) {
          totalShare = totalShare.plus(new Big(numerator).div(denominator));
        }
      }
    });
  }

  return totalShare.toNumber();
};

// Get area source display text
// const getAreaSourceDisplay = (featureInfo: any) => {
//   if (!featureInfo || !featureInfo.areaSource) {
//     return '未知';
//   }

//   switch (featureInfo.areaSource) {
//     case 'cadastral':
//       return '地籍登記面積 (Desc_area)';
//     case 'survey':
//       return '測量面積 (Map_area)';
//     case 'calculated':
//       return '地圖幾何計算';
//     default:
//       return '未知';
//   }
// };

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
  console.log('[step2.vue] handleProceedToNext called');

  const isValid = await validateForm();
  if (isValid) {
    console.log('step2.vue: Form is valid, emitting ready-to-proceed');
    eventEmitter.emitReadyToProceed();
  } else {
    console.log('step2.vue: Form validation failed');
  }
};

// 事件驅動架構:處理返回請求
const handleGoBack = () => {
  console.log('step2.vue: handleGoBack called');
  eventEmitter.emitGoBackRequested();
};

// 多筆土地管理功能
const addNewLand = () => {
  console.log('step2.vue: Adding new land')

  // 清空當前表單
  landUtils.clearCurrentForm()

  // 設置為新增模式
  landManagement.currentEditingLandId = null
  landManagement.isEditingMode = true // 這裡會觸發 watch，自動發送事件

  console.log('step2.vue: Ready for new land input')
}

const editLand = async (landId: string) => {
  console.log('step2.vue: Editing land:', landId)

  const land = landManagement.lands.find(l => l.id === landId)
  if (!land) {
    console.error('step2.vue: Land not found:', landId)
    return
  }

  // 開啟載入保護，防止 watch 誤觸發重置
  initGuard.isInitializing = true
  isLandNumberUpdateProgrammatic.value = true

  try {
    // P0 修復：載入該土地的級聯資料
    console.log('Loading cascade data for editing land...')
    try {
      await preloadCascadeDataForLands([land])
      console.log('Cascade data loaded for editing')
    } catch (error) {
      console.warn('Failed to load cascade data for editing:', error)
    }

    // 載入土地資料到當前表單（修復後的版本包含類型轉換）
    // 注意：傳入 true 跳過內部保護，因為我們在外層統一管理
    landUtils.loadLandToCurrentForm(land, true)

    // 如果該土地有地段資料，載入對應的 NLSC 地段選項
    if (land.landCounty && land.landTown && land.landSec) {
      console.log('Loading land section data for editing:', {
        county: land.landCounty,
        town: land.landTown,
        section: land.landSec
      });

      try {
        // 等待一下確保表單資料已載入
        await nextTick();
        await loadLandSections(true); // 保留現有的地段選擇
        console.log('Land section data loaded for editing');
      } catch (error) {
        console.warn('Failed to load land section data for editing:', error);
      }
    }

    // 設置為編輯模式
    landManagement.currentEditingLandId = landId
    landManagement.isEditingMode = true

    console.log('step2.vue: Land loaded for editing')
  } finally {
    // 所有載入完成後才關閉保護
    await nextTick()
    initGuard.isInitializing = false
    isLandNumberUpdateProgrammatic.value = false
    console.log('editLand - 載入保護已關閉')
  }
}

const saveLandEdit = () => {
  console.log('step2.vue: Saving land edit')

  // 創建土地資料
  const landData = landUtils.createLandFromCurrentForm()

  if (landManagement.currentEditingLandId) {
    // 更新現有土地
    const index = landManagement.lands.findIndex(l => l.id === landManagement.currentEditingLandId)
    if (index !== -1) {
      landData.id = landManagement.currentEditingLandId
      landManagement.lands[index] = landData
      console.log('step2.vue: Land updated successfully')
    }
  } else {
    // 新增土地
    landManagement.lands.push(landData)
    console.log('step2.vue: New land added successfully')
  }

  // 退出編輯模式（會自動觸發導航狀態更新）
  cancelLandEdit()

  // 同步到 localFormData.lands 以便儲存
  localFormData.lands = [...landManagement.lands]

  // 立即觸發資料儲存（不等待 3 秒自動儲存延遲）
  if (!initGuard.isInitializing && initGuard.isInitialized) {
    console.log('step2.vue: Triggering immediate save after land edit')
    eventEmitter.emitDataChanged(true)  // 傳遞 immediate=true
  }
}

const cancelLandEdit = () => {
  console.log('step2.vue: Cancelling land edit')

  // 清空當前表單
  landUtils.clearCurrentForm()

  // 退出編輯模式
  landManagement.currentEditingLandId = null
  landManagement.isEditingMode = false // 這裡會觸發 watch，自動發送事件

  console.log('step2.vue: Edit cancelled')
}

const showDeleteLandDialog = ref(false)
const pendingDeleteLandId = ref<string | null>(null)

const requestDeleteLand = (landId: string) => {
  pendingDeleteLandId.value = landId
  showDeleteLandDialog.value = true
}

const confirmDeleteLand = () => {
  const landId = pendingDeleteLandId.value
  if (!landId) return

  showDeleteLandDialog.value = false
  pendingDeleteLandId.value = null

  console.log('step2.vue: Deleting land:', landId)

  const index = landManagement.lands.findIndex(l => l.id === landId)
  if (index !== -1) {
    landManagement.lands.splice(index, 1)

    // 同步到 localFormData.lands (watch會自動觸發資料更新)
    localFormData.lands = [...landManagement.lands]

    // 如果正在編輯被刪除的土地，退出編輯模式
    if (landManagement.currentEditingLandId === landId) {
      cancelLandEdit()
    }
    // 立即觸發資料儲存（不等待 3 秒自動儲存延遲）
    stepManager.emitDataChanged(true)

    console.log('step2.vue: Land deleted successfully, lands count:', landManagement.lands.length)
  }
}

// 編輯狀態監聽與事件發送 + 地圖重建機制
watch(() => landManagement.isEditingMode, async (isEditing, wasEditing) => {
  // 避免初始化時觸發
  if (isEditing === wasEditing) return

  console.log(`step2.vue: Navigation state changed - isEditing: ${isEditing}`)

  // 發送導航狀態變更事件
  emit('navigation-state-changed', {
    step: 2,
    canNavigate: !isEditing,
    isEditing: isEditing,
    reason: isEditing ? '正在編輯土地資料，請先完成或取消編輯' : undefined
  })

  // 地圖初始化由 landInfoDialog watch 統一處理
  // 編輯模式切換時不主動初始化，避免與對話框 watch 衝突
}, { immediate: false })

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

// P0 修復：級聯選擇載入邏輯
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
        console.warn(`Failed to load towns for county ${countyId}:`, error)
      }
    })

    await Promise.all(townPromises)
  } catch (error) {
    console.error('[P0 Fix] Cascade data preloading failed:', error)
  }
}

// 修復初始化邏輯 - 去除過度複雜的保護機制
const initializeStep2WithCascadeData = async () => {
  console.log('[P0 Fix] Initializing Step2 with proper cascade loading...')

  try {
    // 標記開始初始化
    initGuard.isInitializing = true

    // 1. 首先載入步驟資料
    const caseNumber = grantsStore.caseNumber
    if (!caseNumber) {
      console.log('No case number available, skipping data load')
      return
    }

    console.log(`Loading step data for case: ${caseNumber}`)
    const stepData = await grantsStore.loadStepData(caseNumber, 2)

    // 2. 處理土地資料 - 向後相容
    let lands: LandData[] = []

    if (stepData?.lands?.length) {
      // 新版多筆土地資料
      lands = stepData.lands as LandData[]
      console.log(`Found ${lands.length} lands in new format`)
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
      console.log('Converted legacy single land data')
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

    // Linus式修復：完成初始化
    console.log('[P0 Fix] Step2 initialization completed successfully')

    // 先標記為已初始化
    initGuard.isInitialized = true
    initGuard.isInitializing = false

    // 關鍵修復：使用 nextTick 確保所有初始化副作用完成後再發送資料
    // 這樣可以避免初始化過程中的欄位修改被視為「變更」
    await nextTick()

    // 初始化面積追蹤值，避免首次載入時觸發清除邏輯
    previousTotalFacilityArea.value = totalFacilityArea.value
    // console.log(`[Step2] 初始化面積追蹤值: ${(totalFacilityArea.value / 10000).toFixed(4)} 公頃`)

    // 主動發送一次完整的初始化資料狀態給父組件
    // 這確保 grants store 的 previousFormData 與當前資料一致
    eventEmitter.emitDataChanged()

  } catch (error) {
    console.error('[P0 Fix] Step2 initialization failed:', error)
    initGuard.isInitializing = false
    // 確保即使初始化失敗，基本的縣市資料也要載入
    try {
      if (!domicileStore.countyOptions.length) {
        await domicileStore.loadCounties()
      }
    } catch (fallbackError) {
      console.error('Even fallback county loading failed:', fallbackError)
    }
  }
}

// 土地分類對照表載入（與主要初始化流程獨立，失敗不中斷功能）
onMounted(async () => {
  await loadLandUseClassification();
});

// 生命週期管理 - 使用修復後的邏輯
onMounted(async () => {
  window.addEventListener('beforeunload', beforeUnloadHandler)

  if (isStep2OfflineTrainingMode) {
    try {
      await ensureOfflineTrainingDataLoaded()
    } catch (error) {
      console.error('離線訓練資料預載失敗:', error)
    }
  }

  // 載入作物資料 (從資料庫)
  try {
    if (!cropsStore.isInitialized) {
      await cropsStore.initializeStore()
    }
  } catch (error) {
    console.error('[step2.vue] Failed to initialize crops store:', error)
    // 即使作物資料載入失敗，仍允許頁面繼續渲染
  }

  // P0 修復：使用新的初始化邏輯
  try {
    await initializeStep2WithCascadeData()
  } catch (error) {
    console.error('[step2.vue] Failed to initialize step2 cascade data:', error)
    // 錯誤已記錄，允許頁面繼續渲染
  }
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
            const newArea = new Big(landArea).times(numerator).div(denominator).round(1, Big.roundDown).toString();
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
      // 更新農地地籍面積公頃值（以截斷後的 m² 為基準）
      const calculatedHa = m2ToHa(area)
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
        localFormData.facilityAreaHa = m2ToHa(facilityArea);
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
const showLandInfoDialog = async () => {
  // Update land info with current form data
  if (localFormData.landNumberMain) {
    landInfo.number = localFormData.landNumberSub
      ? `${localFormData.landNumberMain}-${localFormData.landNumberSub}`
      : localFormData.landNumberMain;
  }

  if (localFormData.landCounty) {
    landInfo.county = String(localFormData.landCounty);
  }

  if (localFormData.landSec) {
    landInfo.section = String(localFormData.landSec);
  }

  landInfoDialog.value = true;
  // 地圖初始化已由 landInfoDialog watch 處理

  // 等待地圖初始化完成後，自動載入地籍圖
  await nextTick();

  // 給地圖一點時間初始化
  setTimeout(async () => {
    if (mapState.isInitialized) {
      await loadCadastralMapFromAPI();
    }
  }, 500);
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

    // 建立共用的 NLSC GoogleMapsCompatible TileGrid 配置
    // 底圖 (EMAP) 和地籍圖 (DMAPS) 都使用相同的 TileMatrixSet
    // 參考 capabilities.xml 和 wmts.xml 的 GoogleMapsCompatible 定義
    const nlscProjection = getProjection('EPSG:3857')!;
    const nlscExtent = nlscProjection.getExtent();
    const nlscSize = getWidth(nlscExtent) / 256;
    const nlscResolutions = new Array(20);
    const nlscMatrixIds = new Array(20);

    for (let z = 0; z < 20; ++z) {
      nlscResolutions[z] = nlscSize / Math.pow(2, z);
      nlscMatrixIds[z] = z.toString();
    }

    // 使用 capabilities.xml 中的精確 TopLeftCorner 值
    const nlscTileGrid = new WMTSTileGrid({
      origin: [-20037508.34278925, 20037508.34278925],
      resolutions: nlscResolutions,
      matrixIds: nlscMatrixIds,
    });

    // NLSC 底圖：臺灣通用電子地圖
    // 可選圖層：EMAP (標準版), EMAP6 (無等高線), EMAP5 (等高線+門牌), EMAP2 (透明版)
    const emapLayer = new TileLayer({
      source: new WMTS({
        url: 'https://wmts.nlsc.gov.tw/wmts/EMAP/default/GoogleMapsCompatible/{TileMatrix}/{TileRow}/{TileCol}',
        layer: 'EMAP',
        matrixSet: 'GoogleMapsCompatible',
        format: 'image/jpeg',
        projection: nlscProjection,
        tileGrid: nlscTileGrid,
        style: 'default',
        wrapX: true,
        requestEncoding: 'REST',
      }),
    });

    // NLSC 疊加層：地籍圖（透過後端 API 代理）
    const cadastralLayer = new TileLayer({
      source: new WMTS({
        url: '/api/v1/nlsc/cadastral/tiles/{TileMatrix}/{TileRow}/{TileCol}',
        layer: 'DMAPS',
        matrixSet: 'GoogleMapsCompatible',
        format: 'image/png',
        projection: nlscProjection,
        tileGrid: nlscTileGrid, // 共用相同的 TileGrid 確保完美對齊
        style: 'default',
        wrapX: true,
        requestEncoding: 'REST',
      }),
      opacity: 0.7,
    });

    // Get target element
    const targetElement = document.getElementById('step2-land-info-map');

    if (!targetElement) {
      throw new Error('Map container not found');
    }

    // Create map instance with markRaw to prevent Vue reactivity overhead
    map = markRaw(new Map({
      target: targetElement,
      layers: [emapLayer, cadastralLayer], // 加入地籍圖層
      view: new View({
        center: fromLonLat([lon, lat]),
        zoom: 16
      }),
    }));

    await nextTick();

    // Add selection interaction
    addSelectInteraction();

    // 添加地圖點擊事件監聽器，用於點座標查詢地籍圖
    map.on('click', handleMapClick);

    // Load cadastral map from NLSC API (if land info is available)
    // 地圖初始化後，不自動載入地籍圖，等待用戶點擊「查詢地號」按鈕
    // 這樣可以避免在沒有完整地號資訊時發送無效請求

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
        const truncatedM2 = m2Truncate(preciseArea);
        localFormData.landArea = truncatedM2;
        localFormData.landAreaHa = m2ToHa(parseFloat(truncatedM2));

        // If facility area is not set, set it to the same value
        if (!localFormData.facilityArea) {
          localFormData.facilityArea = truncatedM2;
          localFormData.facilityAreaHa = m2ToHa(parseFloat(truncatedM2));
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
const useSelectedFeature = async () => {
  if (selectedFeatureInfo.value) {
    // 步驟 1: 先更新設施地段（縣市、鄉鎮市區、地段）- 必須在設置地號資料之前執行
    // 這樣級聯清除就不會影響到地號資料
    if (selectedFeatureInfo.value.CITY || selectedFeatureInfo.value.TOWN || selectedFeatureInfo.value.SECT) {
      console.log('[Step 1] Updating facility location from GML data...');

      // 1. 根據 CITY 名稱找到縣市 ID
      if (selectedFeatureInfo.value.CITY) {
        const cityName = selectedFeatureInfo.value.CITY;
        const matchedCounty = counties.value.find(county =>
          county.title === cityName
        );

        if (matchedCounty) {
          localFormData.landCounty = matchedCounty.value;
          console.log(`Updated landCounty: ${cityName} (${matchedCounty.value})`);

          // 等待 Vue 更新 towns computed property
          await nextTick();
        } else {
          console.warn(`County not found: ${cityName}`);
        }
      }

      // 2. 根據 TOWN 名稱找到鄉鎮市區 ID
      if (selectedFeatureInfo.value.TOWN && localFormData.landCounty) {
        const townName = selectedFeatureInfo.value.TOWN;

        // 等待 towns 計算完成
        await nextTick();

        const matchedTown = towns.value.find(town =>
          town.title === townName
        );

        if (matchedTown) {
          localFormData.landTown = matchedTown.value;
          console.log(`Updated landTown: ${townName} (${matchedTown.value})`);

          // 觸發地段資料載入
          await onTownChange();

          // 等待地段資料載入完成
          await nextTick();
        } else {
          console.warn(`Town not found: ${townName}`);
        }
      }

      // 3. 根據 SECT 代碼找到地段
      if (selectedFeatureInfo.value.SECT && localFormData.landTown) {
        const sectionCode = selectedFeatureInfo.value.SECT;

        // 等待 sections 載入完成
        await nextTick();

        const matchedSection = sections.value.find(section =>
          section.code === sectionCode ||
          section.value === sectionCode
        );

        if (matchedSection) {
          localFormData.landSec = matchedSection.value;
          localFormData.landSecName = matchedSection.displayName || matchedSection.name;
          console.log(`Updated landSec: ${sectionCode} (${matchedSection.displayName})`);
        } else {
          console.warn(`Section not found: ${sectionCode}`);
        }
      }

      console.log('Facility location update completed');
    }

    // 步驟 2: 更新地號資料（在設施地段同步完成後執行，避免被級聯清除）
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
      const truncatedM2 = m2Truncate(parseFloat(String(selectedFeatureInfo.value.area)));
      const areaInHa = m2ToHa(parseFloat(truncatedM2));
      localFormData.landArea = truncatedM2;
      localFormData.landAreaHa = areaInHa;

      // Set the facility area to match land area by default
      localFormData.facilityArea = truncatedM2;
      localFormData.facilityAreaHa = areaInHa;
    }

    // 使用當前查詢到的 cadastral feature（從 NLSC API）
    const feature = currentCadastralFeature.value;
    if (feature) {
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

// Load Cadastral Map from NLSC API (按需查詢地籍圖)
// 使用國土測繪中心 CadasMapQuery API 查詢指定地號的地籍圖資料
// API: https://api.nlsc.gov.tw/dmaps/CadasMapQuery/[縣市]/[地段]/[地號]/[格式]/[坐標系統]
const loadCadastralMapFromAPI = async () => {
  try {
    // 開始載入，顯示 loading 動畫
    isCadastralLoading.value = true;
    featureInfoVisible.value = true;  // 顯示地號資訊面板以展示 loading

    // 驗證必要欄位
    if (!localFormData.landSec) {
      console.warn('Missing landSec, cannot query cadastral map');
      isCadastralLoading.value = false;
      return;
    }

    if (!localFormData.landNumberMain) {
      console.warn('Missing landNumberMain, cannot query cadastral map');
      isCadastralLoading.value = false;
      return;
    }

    // 驗證地號格式
    const validation = validateLandNumber(
      localFormData.landNumberMain,
      localFormData.landNumberSub
    );

    if (!validation.valid) {
      console.error('Invalid land number:', validation.message);
      isCadastralLoading.value = false;
      return;
    }

    // 取得當前選中的地段資料
    const currentSectionCode = localFormData.landSec.toString();
    const selectedSection = sections.value.find(s =>
      s.code === currentSectionCode ||
      s.value === currentSectionCode ||
      s.code === localFormData.landSec ||
      s.value === localFormData.landSec
    );

    if (!selectedSection) {
      console.error('Cannot find selected section:', currentSectionCode);
      isCadastralLoading.value = false;
      return;
    }

    if (isStep2OfflineTrainingMode) {
      await ensureOfflineTrainingDataLoaded();

      const offlineMatchedFeatures = queryOfflineFeaturesByLandNo(
        selectedSection.code,
        localFormData.landNumberMain,
        localFormData.landNumberSub || '0'
      );

      if (offlineMatchedFeatures.length === 0) {
        console.warn('離線模式查無地籍資料');
        noSectionDataOverlay.value = true;
        isCadastralLoading.value = false;
        return;
      }

      await displayCadastralFeatures(offlineMatchedFeatures);
      return;
    }

    // 建立查詢參數
    const queryParams: CadastralQueryParams = {
      countyCode: selectedSection.county_land_code,  // 縣市代碼
      sectionCode: selectedSection.code,             // 地段代碼
      landNumberMain: localFormData.landNumberMain,  // 主號
      landNumberSub: localFormData.landNumberSub || '0', // 副號（預設0）
      format: 'gml',                                  // 使用 GML 格式
      srid: '4326'                                    // 使用 WGS84 坐標系統
    };

    console.log('Querying cadastral map with params:', queryParams);

    // 呼叫 NLSC API
    const result = await queryCadastralMap(queryParams);

    if (!result.success || result.features.length === 0) {
      console.error('No cadastral data found:', result.message);
      noSectionDataOverlay.value = true;
      isCadastralLoading.value = false;
      return;
    }

    // 顯示查詢到的地籍圖（loading 會在 processFeatureAreaData 結束時設為 false）
    await displayCadastralFeatures(result.features);

  } catch (error) {
    console.error('Failed to load cadastral map from API:', error);
    isCadastralLoading.value = false;
  }
};

// 處理地圖點擊事件，使用點座標查詢地籍圖
const handleMapClick = async (event: any) => {
  try {
    // 開始載入，顯示 loading 動畫
    isCadastralLoading.value = true;
    featureInfoVisible.value = true;  // 顯示地號資訊面板以展示 loading

    // 獲取點擊位置的座標 (EPSG:3857 Web Mercator)
    const clickedCoordinate = event.coordinate;

    if (isStep2OfflineTrainingMode) {
      await ensureOfflineTrainingDataLoaded();
      const matchedFeature = queryOfflineFeatureByCoordinate(clickedCoordinate);

      if (!matchedFeature) {
        console.warn('離線模式點選位置查無地籍資料');
        isCadastralLoading.value = false;
        return;
      }

      await displayCadastralFeatures([matchedFeature]);
      return;
    }

    // 轉換為 WGS84 (EPSG:4326) 供 NLSC API 使用
    const wgs84Coordinate = transform(clickedCoordinate, 'EPSG:3857', 'EPSG:4326');
    const lon = wgs84Coordinate[0];
    const lat = wgs84Coordinate[1];

    console.log(`Map clicked at: [${lon.toFixed(6)}, ${lat.toFixed(6)}]`);

    // 調用 NLSC 點座標查詢 API
    const result = await queryCadastralMapByPoint(lon, lat, '4326', 'gml');

    if (!result.success || result.features.length === 0) {
      console.warn('No cadastral data at this point:', result.message);
      isCadastralLoading.value = false;
      // 可以選擇顯示提示訊息，但不要覆蓋現有的地籍圖
      return;
    }

    // 顯示查詢到的地籍圖（loading 會在 processFeatureAreaData 結束時設為 false）
    await displayCadastralFeatures(result.features);

  } catch (error) {
    console.error('Failed to query cadastral map by point:', error);
    isCadastralLoading.value = false;
  }
};

// 顯示地籍圖 features 在地圖上
const displayCadastralFeatures = async (features: any[]) => {
  // 檢查 features 是否有幾何資料
  if (features.length === 0) {
    console.error('No features to display');
    return;
  }

  // 驗證第一個 feature 的幾何資料
  const firstFeature = features[0];
  const geometry = firstFeature.getGeometry();
  if (!geometry) {
    console.error('Feature has no geometry:', firstFeature.getProperties());
    return;
  }

  // 建立新的 VectorSource（先創建空的）
  const cadastralSource = new VectorSource();

  // 使用 addFeatures() 方法添加所有 features（避免 Vue Proxy 問題）
  cadastralSource.addFeatures(features);

  // 移除舊的地籍圖層（如果存在）
  if (map) {
    const layers = map.getLayers().getArray();
    const oldCadastralLayer = layers.find(layer =>
      layer.get('id') === 'cadastral-parcels'
    );
    if (oldCadastralLayer) {
      map.removeLayer(oldCadastralLayer);
    }
  }

  // 建立新的地籍圖層
  const cadastralLayer = new VectorLayer({
    source: cadastralSource,
    style: new Style({
      stroke: new Stroke({ color: 'rgba(255, 0, 0, 1.0)', width: 3 }),
      fill: new Fill({ color: 'rgba(255, 0, 0, 0.2)' })
    }),
    zIndex: 10,
  });

  cadastralLayer.set('id', 'cadastral-parcels'); // 設定 ID 以便後續識別

  if (map) {
    map.addLayer(cadastralLayer);

    // 自動縮放到 features 範圍
    try {
      const extent = cadastralSource.getExtent();

      // 檢查 extent 是否有效（不是 Infinity）
      if (extent && extent.every(val => isFinite(val))) {
        map.getView().fit(extent, {
          padding: [50, 50, 50, 50],
          maxZoom: 18,
          duration: 500
        });
      } else {
        console.warn('Invalid extent, using feature geometry directly');
        // 使用第一個 feature 的幾何範圍
        const featureExtent = geometry.getExtent();
        if (featureExtent && featureExtent.every(val => isFinite(val))) {
          map.getView().fit(featureExtent, {
            padding: [50, 50, 50, 50],
            maxZoom: 18,
            duration: 500
          });
        }
      }
    } catch (error) {
      console.error('Error fitting extent:', error);
      // 如果縮放失敗，至少圖層已經加入，用戶可以手動縮放
    }
  }

  // 處理面積資料並更新表單
  await processFeatureAreaData(features);
};

/**
 * 根據 NLSC API 返回的縣市和鄉鎮名稱動態載入地段清單並查找地段名稱
 * @param cityName NLSC API 返回的縣市名稱（例如：臺中市）
 * @param townName NLSC API 返回的鄉鎮名稱（例如：南區）
 * @param sectionCode NLSC API 返回的地段代碼（例如：0532）
 * @returns 地段中文名稱，找不到則返回空字串
 */
const fetchSectionNameByCityAndTown = async (
  cityName: string,
  townName: string,
  sectionCode: string
): Promise<string> => {
  try {
    // 1. 查找縣市資料
    const county = domicileStore.countyOptions.find(c => c.title === cityName);
    if (!county || !county.land_code) {
      console.warn(`找不到縣市或缺少 land_code: ${cityName}`);
      return '';
    }

    // 2. 確保該縣市的鄉鎮資料已載入
    if (!domicileStore.townsByCountyId.get(county.value)?.length) {
      console.log(`載入縣市 ${cityName} 的鄉鎮資料...`);
      await domicileStore.loadTownsByCountyId(county.value);
    }

    // 3. 查找鄉鎮資料
    const towns = domicileStore.getTownsForCountyId(county.value);
    const town = towns.find(t => t.title === townName);
    if (!town || !town.land_code) {
      console.warn(`找不到鄉鎮或缺少 land_code: ${cityName} ${townName}`);
      return '';
    }

    // 4. 使用與下拉選單相同的方法載入地段清單
    console.log(`載入地段資料: ${cityName} ${townName} (${county.land_code}/${town.land_code})`);
    await domicileStore.loadLandSectionsByLandCodes(county.land_code, town.land_code);
    const sectionsToSearch = domicileStore.landSections.filter(s =>
      s.county_land_code === county.land_code && s.town_land_code === town.land_code
    );

    // 5. 在載入的地段清單中查找地段名稱
    const sectionCodeToFind = sectionCode.toString();
    const matchedSection = sectionsToSearch.find(s =>
      s.code === sectionCodeToFind ||
      s.code === parseInt(sectionCodeToFind, 10).toString() ||
      parseInt(s.code, 10) === parseInt(sectionCodeToFind, 10)
    );

    if (matchedSection) {
      console.log(`找到地段名稱: ${matchedSection.name} (代碼: ${sectionCode})`);
      return matchedSection.name;
    } else {
      console.warn(`找不到地段代碼 ${sectionCode} 在 ${cityName} ${townName}`);
      return '';
    }
  } catch (error) {
    console.error('動態載入地段清單失敗:', error);
    return '';
  }
};

// 處理 feature 的面積資料（從 NLSC API 返回的 GML 包含面積等屬性）
const processFeatureAreaData = async (features: any[]) => {
  if (features.length === 0) return;

  // 統一處理邏輯（使用第一筆 feature 的資料）
  // NLSC API 回傳的每筆 feature.AREA 都是總面積，不需要累加
  const feature = features[0];
  const properties = feature.getProperties();

  // NLSC GML 實際欄位 (根據實際 API 回傳)：
  // - LANDNO: 地號 8 碼（例如：00010000 = 0001-0000）
  // - SECT: 地段代碼（例如：0532）
  // - AREA: 面積(平方公尺)
  // - CITY: 縣市（例如：臺中市）
  // - TOWN: 鄉鎮市區（例如：南區）
  // - OFFICE: 地政事務所代碼（例如：BA）
  // - VALUESSESSED: 公告地價(元/平方公尺)
  // - VALUEANNOUNCE: 公告現值(元/平方公尺)
  // - LANDUSE: 使用分區
  // - LANDDETATIS: 用地編定

  const area = properties.AREA;

  // 如果沒有面積資料，使用 OpenLayers 計算幾何面積
  let calculatedArea = area;
  if (!calculatedArea) {
    const geometry = feature.getGeometry();
    if (geometry && (geometry.getType() === 'Polygon' || geometry.getType() === 'MultiPolygon')) {
      calculatedArea = geometry.getArea(); // 平方公尺
    }
  }

  // 格式化地號：從 8 碼 (例如：00010000) 轉換為 ####-#### 格式 (例如：0001-0000)
  let formattedLandNo = '';
  if (properties.LANDNO) {
    const landNo8 = properties.LANDNO.toString().padStart(8, '0');
    const mainPart = landNo8.substring(0, 4);  // 前 4 碼
    const subPart = landNo8.substring(4, 8);   // 後 4 碼
    formattedLandNo = `${mainPart}-${subPart}`;
  }

  // 獲取地段中文名稱
  let sectionName = '';
  const sectionCodeToFind = properties.SECT || localFormData.landSec?.toString();

  if (sectionCodeToFind) {
    // 優先使用 NLSC API 返回的 CITY 和 TOWN 動態載入地段清單（支援跨區查詢）
    if (properties.CITY && properties.TOWN) {
      sectionName = await fetchSectionNameByCityAndTown(
        properties.CITY,
        properties.TOWN,
        sectionCodeToFind
      );
    }

    // 如果動態載入失敗，回退到當前已載入的地段清單中查找
    if (!sectionName) {
      const selectedSection = sections.value.find(s =>
        s.code === sectionCodeToFind ||
        s.value === sectionCodeToFind
      );
      if (selectedSection) {
        sectionName = selectedSection.displayName || selectedSection.name || selectedSection.title || '';
      }
    }
  }

  // 土地使用分區：代碼 → 中文名稱轉換
  const landuseCode = properties.LANDUSE?.toString() || '';
  const landdetatisCode = properties.LANDDETATIS?.toString() || '';
  const landuseName = landuseCode ? convertLandUseCodeToName(landuseCode) : '';
  const landdetatisName = landdetatisCode ? convertLandDetatisCodeToName(landdetatisCode) : '';

  // 更新 selectedFeatureInfo 以顯示在地號資訊面板
  selectedFeatureInfo.value = {
    Land_no: formattedLandNo,           // 格式化地號（####-####）
    section: sectionName,                // 地段中文名稱
    area: calculatedArea,                // 面積（平方公尺）

    // GML 原始欄位
    LANDNO: properties.LANDNO,           // GML 地號 8 碼
    SECT: properties.SECT,               // GML 地段代碼
    CITY: properties.CITY,               // 縣市
    TOWN: properties.TOWN,               // 鄉鎮市區
    OFFICE: properties.OFFICE,           // 地政事務所代碼
    AREA: properties.AREA,               // GML 面積
    Sec_cns: sectionName,                // 地段中文名稱

    // 土地使用分區（代碼 + 中文名稱）
    LANDUSE: landuseCode || undefined,
    LANDDETATIS: landdetatisCode || undefined,
    LANDUSE_NAME: landuseName || undefined,
    LANDDETATIS_NAME: landdetatisName || undefined,
  };

  // 暫存使用地類別代碼至 localFormData（供 createLandFromCurrentForm 讀取）
  localFormData.landDetatisCode = landdetatisCode;

  // 林業用地（ES）輔助提示：立即顯示；點選其他地號時自動清除
  if (landdetatisCode === 'ES') {
    landParcelNotFoundAlert.value = true;
    landParcelNotFoundTitle.value = '林業用地限制';
    landParcelNotFoundMessage.value = '系統查詢顯示此地號使用地類別為「林業用地」(ES)。線上資料可能未反映最新地籍登記狀況，請以土地登記謄本為準，自行確認是否符合補助申請條件。';
  } else if (landParcelNotFoundTitle.value === '林業用地限制') {
    landParcelNotFoundAlert.value = false;
    landParcelNotFoundTitle.value = '查無此地號';
    landParcelNotFoundMessage.value = '';
  }

  // 存儲當前的 cadastral feature（用於「使用此地號」功能）
  currentCadastralFeature.value = feature;

  // 執行空間查詢以獲取灌區及縣市資訊（用於「使用此地號」時的 isIrrigationArea 欄位）
  const geometry = feature.getGeometry();
  if (geometry) {
    performSpatialQueries(feature);
  }

  // 顯示地號資訊面板
  featureInfoVisible.value = true;

  // 資料載入完成，關閉 loading 動畫
  isCadastralLoading.value = false;

  console.log('Updated selectedFeatureInfo:', selectedFeatureInfo.value);
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
      // 移除地圖點擊事件監聽器
      map.un('click', handleMapClick);

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
    // 重置地號警告狀態（包含林業用地阻擋訊息）
    landParcelNotFoundAlert.value = false;
    landParcelNotFoundTitle.value = '查無此地號';
    landParcelNotFoundMessage.value = '';
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

// Linus 式修復：移除重複的 watch，統一使用事件處理機制
// - 消除"兩個機制做同一件事"的特殊情況
// - 與 qualification/index.vue、maps/index.vue 保持一致
// - 所有邏輯已整合到 onCountyChange 和 onTownChange 事件處理中

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

// DEV-only: 模擬 NLSC 地號查詢結果（用於 DevTools 測試土地使用分區顯示與 ES 阻擋）
interface GMLProperties {
  CITY?: string;
  TOWN?: string;
  OFFICE?: string;
  SECT?: string;
  LANDNO?: string;
  AREA?: number;
  LANDUSE?: string;
  LANDDETATIS?: string;
  VALUESSESSED?: number;
  VALUEANNOUNCE?: number;
}

declare global {
  interface Window {
    testStep2LandInfo: (props: GMLProperties) => void;
  }
}

if (import.meta.env.DEV) {
  const simulateNLSCLandInfo = (props: GMLProperties) => {
    const landuseCode = props.LANDUSE?.toString() || '';
    const landdetatisCode = props.LANDDETATIS?.toString() || '';

    const landNo8 = (props.LANDNO || '').toString().padStart(8, '0');
    const formattedLandNo = landNo8.length >= 8
      ? `${landNo8.substring(0, 4)}-${landNo8.substring(4, 8)}`
      : landNo8;

    const sectionCodeToFind = props.SECT || '';
    const selectedSection = sections.value.find(s =>
      s.code === sectionCodeToFind || s.value === sectionCodeToFind
    );
    const sectionName = selectedSection?.displayName || selectedSection?.name || '';

    selectedFeatureInfo.value = {
      Land_no: formattedLandNo,
      section: sectionName,
      area: props.AREA,
      areaSource: '地籍登記面積 (NLSC)',
      LANDNO: props.LANDNO,
      SECT: props.SECT,
      CITY: props.CITY,
      TOWN: props.TOWN,
      OFFICE: props.OFFICE,
      AREA: props.AREA,
      Sec_cns: sectionName,
      LANDUSE: landuseCode || undefined,
      LANDDETATIS: landdetatisCode || undefined,
      LANDUSE_NAME: landuseCode ? convertLandUseCodeToName(landuseCode) : undefined,
      LANDDETATIS_NAME: landdetatisCode ? convertLandDetatisCodeToName(landdetatisCode) : undefined,
    };
    featureInfoVisible.value = true;
    if (landdetatisCode === 'ES') {
      landParcelNotFoundAlert.value = true;
      landParcelNotFoundTitle.value = '林業用地限制';
      landParcelNotFoundMessage.value = '系統查詢顯示此地號使用地類別為「林業用地」(ES)。線上資料可能未反映最新地籍登記狀況，請以土地登記謄本為準，自行確認是否符合補助申請條件。';
    } else if (landParcelNotFoundTitle.value === '林業用地限制') {
      landParcelNotFoundAlert.value = false;
      landParcelNotFoundTitle.value = '查無此地號';
      landParcelNotFoundMessage.value = '';
    }
    console.log('[step2.vue][DEV] simulateNLSCLandInfo:', selectedFeatureInfo.value);
  };

  window.testStep2LandInfo = simulateNLSCLandInfo;
}
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
