<template>
  <div class="fill-height d-flex flex-column">
    <div class="d-flex flex-grow-1">
      <!-- 主要地圖區域 -->
      <v-card
        class="flex-grow-1 d-flex flex-column"
      >
        <div
          id="map"
          ref="mapContainer"
          class="map-container"
          style="min-height: 0;"
        >
          <!-- 地圖容器 -->

          <!-- 左上方篩選工具欄 -->
          <FilterToolbar
            :all-features="allLoadedFeatures"
            :statistics="statistics"
            :loading="gisLoading"
            :initial-criteria="getInitialFilterCriteria()"
            :initial-expanded="false"
            @filter-change="handleFilterChange"
            @expanded-change="handleFilterExpanded"
            @criteria-reset="handleFilterReset"
          />

          <!-- 展繪工具浮動面板 -->
          <div
            v-if="showDrawPanel"
            class="floating-panel draw-panel"
            :style="{
              left: drawPanelPosition.x + 'px',
              top: drawPanelPosition.y + 'px'
            }"
          >
            <v-card
              class="tool-panel"
              :class="{ 'dragging': isDraggingDraw }"
              elevation="8"
              rounded="lg"
              width="300"
            >
              <v-card-title
                class="d-flex align-center justify-space-between pa-0 draggable-header"
                @mousedown="startDrawDrag"
              >
                <div class="d-flex align-center">
                  <v-icon
                    size="small"
                    class="me-2 drag-handle"
                  >
                    mdi-drag
                  </v-icon>
                  <span class="text-h6">展繪工具</span>
                </div>
                <v-btn
                  icon
                  variant="text"
                  size="small"
                  @click="toggleDraw"
                >
                  <v-icon>mdi-close</v-icon>
                </v-btn>
              </v-card-title>
              <v-divider />
              <v-card-text class="pa-3">
                <v-list density="compact">
                  <v-list-item>
                    <v-btn
                      variant="outlined"
                      color="primary"
                      block
                      class="mb-2"
                    >
                      <v-icon class="me-2">
                        mdi-vector-point
                      </v-icon>
                      點標記
                    </v-btn>
                  </v-list-item>
                  <v-list-item>
                    <v-btn
                      variant="outlined"
                      color="primary"
                      block
                      class="mb-2"
                    >
                      <v-icon class="me-2">
                        mdi-vector-line
                      </v-icon>
                      線條
                    </v-btn>
                  </v-list-item>
                  <v-list-item>
                    <v-btn
                      variant="outlined"
                      color="primary"
                      block
                      class="mb-2"
                    >
                      <v-icon class="me-2">
                        mdi-vector-polygon
                      </v-icon>
                      多邊形
                    </v-btn>
                  </v-list-item>
                  <v-list-item>
                    <v-btn
                      variant="outlined"
                      color="error"
                      block
                    >
                      <v-icon class="me-2">
                        mdi-delete
                      </v-icon>
                      清除全部
                    </v-btn>
                  </v-list-item>
                </v-list>
              </v-card-text>
            </v-card>
          </div>

          <!-- 量測工具浮動面板 -->
          <div
            v-if="showMeasurePanel"
            class="floating-panel measure-panel"
            :style="{
              left: measurePanelPosition.x + 'px',
              top: measurePanelPosition.y + 'px'
            }"
          >
            <v-card
              class="tool-panel"
              :class="{ 'dragging': isDraggingMeasure }"
              elevation="8"
              rounded="lg"
              width="300"
            >
              <v-card-title
                class="d-flex align-center justify-space-between pa-0 draggable-header"
                @mousedown="startMeasureDrag"
              >
                <div class="d-flex align-center">
                  <v-icon
                    size="small"
                    class="me-2 drag-handle"
                  >
                    mdi-drag
                  </v-icon>
                  <span class="text-h6">量測工具</span>
                </div>
                <v-btn
                  icon
                  variant="text"
                  size="small"
                  @click="toggleMeasure"
                >
                  <v-icon>mdi-close</v-icon>
                </v-btn>
              </v-card-title>
              <v-divider />
              <v-card-text class="pa-3">
                <v-list density="compact">
                  <v-list-item>
                    <v-btn
                      variant="outlined"
                      :color="measureType === 'distance' ? 'primary' : 'default'"
                      block
                      class="mb-2"
                      @click="toggleMeasurementType('distance')"
                    >
                      <v-icon class="me-2">
                        mdi-ruler
                      </v-icon>
                      {{ measureType === 'distance' ? '停止測量距離' : '測量距離' }}
                    </v-btn>
                  </v-list-item>
                  <v-list-item>
                    <v-btn
                      variant="outlined"
                      :color="measureType === 'area' ? 'primary' : 'default'"
                      block
                      class="mb-2"
                      @click="toggleMeasurementType('area')"
                    >
                      <v-icon class="me-2">
                        mdi-vector-square
                      </v-icon>
                      {{ measureType === 'area' ? '停止測量面積' : '測量面積' }}
                    </v-btn>
                  </v-list-item>
                  <v-list-item>
                    <v-btn
                      variant="outlined"
                      color="error"
                      block
                      @click="clearMeasurements"
                    >
                      <v-icon class="me-2">
                        mdi-delete
                      </v-icon>
                      清除測量結果
                    </v-btn>
                  </v-list-item>
                </v-list>

                <!-- 測量結果顯示區域 -->
                <v-divider class="my-3" />
                <div class="measure-results">
                  <v-card
                    variant="tonal"
                    color="info"
                    class="pa-2"
                  >
                    <v-card-subtitle class="pa-0 text-caption">
                      測量結果
                    </v-card-subtitle>
                    <v-card-text class="pa-1">
                      <div class="text-body-2">
                        距離: {{ measureResults.distance }}<br>
                        面積: {{ measureResults.area }}
                      </div>
                    </v-card-text>
                  </v-card>
                </div>
              </v-card-text>
            </v-card>
          </div>

          <!-- 定位工具浮動面板 -->
          <div
            v-if="showLocationPanel"
            class="floating-panel location-panel"
            :style="{
              left: locationPanelPosition.x + 'px',
              top: locationPanelPosition.y + 'px'
            }"
          >
            <v-card
              class="tool-panel"
              :class="{ 'dragging': isDraggingLocation }"
              elevation="8"
              rounded="lg"
              width="350"
            >
              <v-card-title
                class="d-flex align-center justify-space-between pa-0 draggable-header"
                @mousedown="startLocationDrag"
              >
                <div class="d-flex align-center">
                  <v-icon
                    size="small"
                    class="me-2 drag-handle"
                  >
                    mdi-drag
                  </v-icon>
                  <span class="text-h6">定位工具</span>
                </div>
                <v-btn
                  icon
                  variant="text"
                  size="small"
                  @click="toggleLocation"
                >
                  <v-icon>mdi-close</v-icon>
                </v-btn>
              </v-card-title>
              <v-divider />
              <v-card-text class="pa-3">
                <!-- 定位方式選擇 -->
                <v-tabs
                  v-model="locationType"
                  density="compact"
                  color="primary"
                  class="mb-3"
                  fixed-tabs
                >
                  <v-tab value="personal">
                    個人位置
                  </v-tab>
                  <v-tab value="coordinate">
                    坐標定位
                  </v-tab>
                  <v-tab value="landNumber">
                    地籍定位
                  </v-tab>
                </v-tabs>

                <!-- 個人位置定位 -->
                <v-window v-model="locationType">
                  <v-window-item value="personal">
                    <v-row class="ma-0">
                      <v-col
                        cols="4"
                        class="pa-0 pe-1"
                      >
                        <v-btn
                          variant="outlined"
                          color="error"
                          block
                          :disabled="!hasLocationMarker"
                          @click="clearLocationMarker"
                        >
                          <v-icon>mdi-delete</v-icon>
                        </v-btn>
                      </v-col>
                      <v-col
                        cols="8"
                        class="pa-0 ps-1"
                      >
                        <v-btn
                          variant="outlined"
                          color="primary"
                          block
                          :loading="isLocationLoading"
                          @click="getCurrentLocation"
                        >
                          <v-icon class="me-2">
                            mdi-crosshairs-gps
                          </v-icon>
                          定位我的位置
                        </v-btn>
                      </v-col>
                    </v-row>
                  </v-window-item>

                  <!-- 坐標定位 -->
                  <v-window-item value="coordinate">
                    <v-btn-toggle
                      v-model="coordinateSystem"
                      mandatory
                      color="primary"
                      density="compact"
                      class="mb-3 d-flex"
                      divided
                      style="width: 100%"
                    >
                      <v-btn
                        value="wgs84"
                        size="small"
                        style="flex: 1"
                      >
                        經緯度 (WGS84)
                      </v-btn>
                      <v-btn
                        value="tw97"
                        size="small"
                        style="flex: 1"
                      >
                        TW97 (TWD97)
                      </v-btn>
                    </v-btn-toggle>

                    <div v-if="coordinateSystem === 'wgs84'">
                      <v-text-field
                        v-model="coordinateInput.longitude"
                        label="經度 (Longitude)"
                        type="number"
                        step="0.000001"
                        variant="outlined"
                        density="compact"
                        placeholder="例: 120.123456"
                        class="mb-2"
                        hide-details
                        autocomplete="off"
                      />
                      <v-text-field
                        v-model="coordinateInput.latitude"
                        label="緯度 (Latitude)"
                        type="number"
                        step="0.000001"
                        variant="outlined"
                        density="compact"
                        placeholder="例: 24.123456"
                        hide-details
                        autocomplete="off"
                      />
                    </div>

                    <div v-else>
                      <v-text-field
                        v-model="coordinateInput.tw97X"
                        label="X 坐標 (東西向)"
                        type="number"
                        step="0.01"
                        variant="outlined"
                        density="compact"
                        placeholder="例: 250000"
                        class="mb-2"
                        hide-details
                        autocomplete="off"
                      />
                      <v-text-field
                        v-model="coordinateInput.tw97Y"
                        label="Y 坐標 (南北向)"
                        type="number"
                        step="0.01"
                        variant="outlined"
                        density="compact"
                        placeholder="例: 2750000"
                        hide-details
                        autocomplete="off"
                      />
                    </div>

                    <v-divider class="my-4" />

                    <v-row class="ma-0">
                      <v-col
                        cols="4"
                        class="pa-0 pe-1"
                      >
                        <v-btn
                          variant="outlined"
                          color="error"
                          block
                          :disabled="!hasLocationMarker"
                          @click="clearLocationMarker"
                        >
                          <v-icon>mdi-delete</v-icon>
                        </v-btn>
                      </v-col>
                      <v-col
                        cols="8"
                        class="pa-0 ps-1"
                      >
                        <v-btn
                          variant="outlined"
                          color="primary"
                          block
                          :loading="isLocationLoading"
                          @click="locateByCoordinate"
                        >
                          <v-icon class="me-2">
                            mdi-map-marker
                          </v-icon>
                          定位到坐標
                        </v-btn>
                      </v-col>
                    </v-row>
                  </v-window-item>

                  <!-- 地號定位 -->
                  <v-window-item value="landNumber">
                    <v-row class="ma-0 mb-2 pt-2 pb-2">
                      <v-col
                        cols="6"
                        class="pa-0 pe-1"
                      >
                        <v-select
                          v-model="landNumberInput.county"
                          :items="countyOptions"
                          label="縣市"
                          variant="outlined"
                          density="compact"
                          hide-details
                          @update:model-value="onCountyChange"
                        />
                      </v-col>
                      <v-col
                        cols="6"
                        class="pa-0 ps-1"
                      >
                        <v-select
                          v-if="!['新竹市', '嘉義市'].includes(landNumberInput.county)"
                          v-model="landNumberInput.town"
                          :items="townOptions"
                          label="鄉鎮市區"
                          variant="outlined"
                          density="compact"
                          hide-details
                          :disabled="!landNumberInput.county"
                          @update:model-value="onTownChange"
                        />
                        <!-- 特殊城市顯示固定的地政分區資訊 -->
                        <v-text-field
                          v-else-if="landNumberInput.county"
                          :model-value="getSpecialCityDisplayText()"
                          class="flex-grow-1"
                          bg-color="grey-lighten-4"
                          label="鄉政市區"
                          variant="outlined"
                          density="compact"
                          hide-details
                          disabled
                        />
                      </v-col>
                    </v-row>

                    <!-- 地段與API狀態 -->
                    <div class="d-flex align-center mb-2">
                      <v-autocomplete
                        :key="sectionSelectKey"
                        v-model="landNumberInput.section"
                        v-model:search="sectionSearchText"
                        :items="sectionOptions"
                        :item-title="item => item.title"
                        item-value="code"
                        label="地段"
                        variant="outlined"
                        density="compact"
                        class="flex-grow-1"
                        :disabled="!landNumberInput.town && !['新竹市', '嘉義市'].includes(landNumberInput.county)"
                        :loading="loadingSections"
                        :no-data-text="'沒有找到相符的地段'"
                        :menu-props="{ closeOnContentClick: true }"
                        :auto-select-first="false"
                        :placeholder="sectionOptions.length > 0 ? '搜尋地段名稱或段號...' : '請先選擇鄉鎮市區'"
                        clearable
                        autocomplete="off"
                        hide-details
                        aria-label="選擇地段"
                        @update:search="onSectionSearchUpdate"
                        @blur="onSectionBlur"
                      >
                        <!-- 自定義選中項的顯示方式 - 只顯示地段名稱 -->
                        <template #selection="{ item }">
                          <template v-if="item.raw">
                            {{ item.raw.displayName || item.raw.name }}
                          </template>
                          <template v-else>
                            {{ item }}
                          </template>
                        </template>

                        <template #item="{ props, item }">
                          <v-list-item v-bind="props">
                            <template #title>
                              <div>
                                {{ item.raw.displayName || item.raw.name }}
                              </div>
                            </template>

                            <template #subtitle>
                              <div class="d-flex align-center mt-1">
                                <span class="text-caption text-grey-darken-1">
                                  段號: {{ item.raw.value || '無' }}
                                </span>
                              </div>
                            </template>
                          </v-list-item>
                        </template>
                      </v-autocomplete>
                    </div>

                    <div class="d-flex align-center gap-2 mb-2 pt-2">
                      <v-text-field
                        v-model="landNumberInput.motherNumber"
                        label="母地號"
                        variant="outlined"
                        density="compact"
                        autocomplete="off"
                        placeholder="例: 123"
                        maxlength="4"
                        :disabled="!landNumberInput.section"
                        hide-details
                        style="flex: 1"
                        @blur="formatMotherNumber"
                      />
                      <span class="text-h6 px-2">-</span>
                      <v-text-field
                        v-model="landNumberInput.childNumber"
                        label="子地號 (選填)"
                        variant="outlined"
                        density="compact"
                        autocomplete="off"
                        placeholder="例: 1"
                        maxlength="4"
                        :disabled="!landNumberInput.section"
                        hide-details
                        style="flex: 1"
                        @blur="formatChildNumber"
                      />
                      <!-- API連線狀態 -->
                      <div class="d-flex align-center ml-2">
                        <v-chip
                          :color="apiStatus.isOnline ? 'success' : 'error'"
                          size="small"
                          variant="outlined"
                        >
                          <v-icon
                            :icon="apiStatus.isOnline ? 'mdi-check-circle' : 'mdi-close-circle'"
                            size="small"
                            class="me-1"
                          />
                          {{ apiStatus.isOnline ? '線上' : '離線' }}
                        </v-chip>
                      </div>
                    </div>

                    <v-divider class="my-4" />

                    <v-row class="ma-0">
                      <v-col
                        cols="4"
                        class="pa-0 pe-1"
                      >
                        <v-btn
                          variant="outlined"
                          color="error"
                          block
                          :disabled="!hasLocationMarker"
                          @click="clearLocationMarker"
                        >
                          <v-icon>mdi-delete</v-icon>
                        </v-btn>
                      </v-col>
                      <v-col
                        cols="8"
                        class="pa-0 ps-1"
                      >
                        <v-btn
                          variant="outlined"
                          color="primary"
                          block
                          :disabled="!landNumberInput.section || !landNumberInput.motherNumber"
                          :loading="isLocationLoading"
                          @click="locateByLandNumber"
                        >
                          <v-icon class="me-2">
                            mdi-map-search
                          </v-icon>
                          定位到地號
                        </v-btn>
                      </v-col>
                    </v-row>
                  </v-window-item>
                </v-window>
              </v-card-text>
            </v-card>
          </div>

          <div class="map-controls">
            <v-card
              class="map-control-panel"
              elevation="3"
              rounded="lg"
            >
              <!-- 圖層按鈕 -->
              <v-row class="ma-0">
                <v-col class="pa-0 text-center">
                  <v-btn
                    :title="'圖層管理'"
                    class="control-btn-vertical"
                    size="large"
                    variant="text"
                    rounded="lg"
                    @click="toggleLayers"
                  >
                    <template #default>
                      <div class="d-flex flex-column align-center">
                        <v-icon
                          size="40"
                          class="mb-0"
                        >
                          mdi-layers
                        </v-icon>
                        <span class="btn-text">圖層</span>
                      </div>
                    </template>
                  </v-btn>
                </v-col>
              </v-row>
              <v-divider />

              <!-- 定位按鈕 -->
              <v-row class="ma-0">
                <v-col class="pa-0 text-center">
                  <v-btn
                    :title="'定位工具'"
                    class="control-btn-vertical"
                    size="large"
                    variant="text"
                    rounded="lg"
                    :color="isLocating ? 'primary' : ''"
                    @click="toggleLocation"
                  >
                    <template #default>
                      <div class="d-flex flex-column align-center">
                        <v-icon
                          size="40"
                          class="mb-0"
                        >
                          mdi-crosshairs-gps
                        </v-icon>
                        <span class="btn-text">定位</span>
                      </div>
                    </template>
                  </v-btn>
                </v-col>
              </v-row>
              <v-divider />

              <!-- 展繪按鈕 -->
              <!-- <v-row class="ma-0">
                <v-col class="pa-0 text-center">
                  <v-btn
                    :title="'繪圖工具'"
                    class="control-btn-vertical"
                    size="large"
                    variant="text"
                    rounded="lg"
                    :color="isDrawing ? 'primary' : ''"
                    @click="toggleDraw"
                  >
                    <template #default>
                      <div class="d-flex flex-column align-center">
                        <v-icon
                          size="40"
                          class="mb-0"
                        >
                          mdi-draw
                        </v-icon>
                        <span class="btn-text">展繪</span>
                      </div>
                    </template>
                  </v-btn>
                </v-col>
              </v-row> -->
              <v-divider />

              <!-- 量測按鈕 -->
              <v-row class="ma-0">
                <v-col class="pa-0 text-center">
                  <v-btn
                    :title="'測量工具'"
                    class="control-btn-vertical"
                    size="large"
                    variant="text"
                    rounded="lg"
                    :color="isMeasuring ? 'primary' : ''"
                    @click="toggleMeasure"
                  >
                    <template #default>
                      <div class="d-flex flex-column align-center">
                        <v-icon
                          size="40"
                          class="mb-0"
                        >
                          mdi-ruler
                        </v-icon>
                        <span class="btn-text">量測</span>
                      </div>
                    </template>
                  </v-btn>
                </v-col>
              </v-row>
              <v-divider />

              <!-- 放大按鈕 -->
              <v-row class="ma-0">
                <v-col class="pa-0 text-center">
                  <v-btn
                    :title="'放大'"
                    class="control-btn-vertical"
                    size="large"
                    variant="text"
                    rounded="lg"
                    @click="zoomIn"
                  >
                    <template #default>
                      <div class="d-flex flex-column align-center">
                        <v-icon
                          size="40"
                          class="mb-0"
                        >
                          mdi-plus
                        </v-icon>
                        <span class="btn-text">放大</span>
                      </div>
                    </template>
                  </v-btn>
                </v-col>
              </v-row>
              <v-divider />

              <!-- 縮小按鈕 -->
              <v-row class="ma-0">
                <v-col class="pa-0 text-center">
                  <v-btn
                    :title="'縮小'"
                    class="control-btn-vertical"
                    size="large"
                    variant="text"
                    rounded="lg"
                    @click="zoomOut"
                  >
                    <template #default>
                      <div class="d-flex flex-column align-center">
                        <v-icon
                          size="40"
                          class="mb-0"
                        >
                          mdi-minus
                        </v-icon>
                        <span class="btn-text">縮小</span>
                      </div>
                    </template>
                  </v-btn>
                </v-col>
              </v-row>
              <v-divider />

              <!-- 首頁按鈕 -->
              <v-row class="ma-0">
                <v-col class="pa-0 text-center">
                  <v-btn
                    :title="'回到原始視圖'"
                    class="control-btn-vertical"
                    size="large"
                    variant="text"
                    rounded="lg"
                    @click="resetView"
                  >
                    <template #default>
                      <div class="d-flex flex-column align-center">
                        <v-icon
                          size="40"
                          class="mb-0"
                        >
                          mdi-home
                        </v-icon>
                        <span class="btn-text">重置</span>
                      </div>
                    </template>
                  </v-btn>
                </v-col>
              </v-row>
            </v-card>
          </div>

          <!-- 版權資訊 -->
          <div class="copyright-info">
            <div class="copyright-text">
              <div>版權所有：農業部農田水利署、系統開發：財團法人農業工程研究中心</div>
            </div>
          </div>

          <!-- 圖層圖例 Navigation Drawer -->
          <v-navigation-drawer
            v-model="showLegendSnackbar"
            height="30"
            border="sm"
            rounded="xs"
            location="bottom"
            elevation="8"
            class="legend-drawer"
            disable-route-watcher
            persistent
            sticky
            temporary
            :scrim="false"
          >
            <div class="pl-3">
              <!-- 標題列 -->
              <div class="d-flex align-center justify-space-between mb-0">
                <div class="d-flex align-center">
                  <v-icon
                    color="primary"
                    size="small"
                    class="me-2"
                  >
                    mdi-information
                  </v-icon>
                  <span class="text-subtitle-2 font-weight-bold text-primary">
                    {{ selectedLegendLayer?.name }} - 圖例說明
                  </span>
                </div>
                <v-btn
                  icon
                  size="small"
                  variant="text"
                  @click="showLegendSnackbar = false"
                >
                  <v-icon size="small">
                    mdi-close
                  </v-icon>
                </v-btn>
              </div>

              <!-- 圖例項目容器 - 自動換行 + 垂直滾動 -->
              <div
                v-if="selectedLegendLayer?.legend && selectedLegendLayer.legend.length > 0"
                class="legend-items-container pr-3"
              >
                <div class="d-flex flex-wrap ga-2">
                  <v-chip
                    v-for="(item, index) in selectedLegendLayer.legend"
                    :key="index"
                    size="small"
                    variant="outlined"
                    label
                  >
                    <template #prepend>
                      <div
                        class="legend-color-box"
                        :style="{
                          width: item.text ? '36px' : '16px',
                          height: item.text ? '16px' : '16px',
                          backgroundColor: item.pattern
                            ? 'transparent'
                            : (item.borderOnly ? 'transparent' : item.color),
                          borderRadius: '2px',
                          border: (item.borderOnly || item.pattern)
                            ? `2px solid ${item.borderColor || item.color}`
                            : '1px solid rgba(0,0,0,0.2)',
                          marginRight: '6px',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          color: item.textColor || getLegendTextColor(item),
                          fontSize: '10px',
                          fontWeight: 'bold',
                          lineHeight: '1',
                          position: 'relative',
                          overflow: 'hidden',
                          ...getPatternStyle(item)
                        }"
                      >
                        {{ item.text || '' }}
                      </div>
                    </template>
                    <span class="text-caption">{{ item.label }}</span>
                  </v-chip>
                </div>
              </div>
              <div
                v-else
                class="text-center text-body-2 text-grey py-3"
              >
                此圖層無圖例資訊
              </div>
            </div>
          </v-navigation-drawer>
        </div>
      </v-card>
      <!-- 顯示成功訊息的Snackbar -->
      <v-snackbar
        v-model="showSnackbar"
        :timeout="2000"
        color="success"
      >
        {{ snackbarMessage }}
      </v-snackbar>

      <!-- 圖層管理組件 -->
      <LayerManagement
        ref="layerManagementRef"
        v-model:visible="showLayersPanel"
        :map-layers="mapLayers"
        :display-mode="displayMode"
        @close="toggleLayers"
        @layer-visibility-changed="handleLayerVisibilityChanged"
        @layer-opacity-changed="handleLayerOpacityChanged"
        @base-layer-selected="handleBaseLayerSelected"
        @display-mode-changed="handleDisplayModeChanged"
        @layer-order-changed="handleLayerOrderChanged"
        @group-order-changed="handleGroupOrderChanged"
        @add-custom-layer="showAddCustomLayerDialog = true"
        @remove-custom-layer="handleRemoveCustomLayer"
        @show-legend="handleShowLegend"
      />

      <!-- 新增自訂圖層對話框 -->
      <AddCustomLayerDialog
        v-model:visible="showAddCustomLayerDialog"
        @layers-added="handleCustomLayersAdded"
        @shapefile-loaded="handleShapefileLoaded"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick, watch, onUnmounted, computed, toRaw, markRaw } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useGisStore } from '@/stores/gis';
import { useDomicileStore } from '@/stores/domicile';
import { checkNlscApiHealth, type LandSection } from '@/services/landSectionNlscService';
import {
  queryCadastralMap,
  queryCadastralMapByPoint,
  validateLandNumber,
  type CadastralQueryParams
} from '@/services/cadastralMapService';
import { storeToRefs } from 'pinia';
import 'ol/ol.css';
import { Map, View, Feature } from 'ol';
import { defaults as defaultControls } from 'ol/control/defaults.js';
import ScaleLine from 'ol/control/ScaleLine.js';
import TileLayer from 'ol/layer/Tile';
import VectorLayer from 'ol/layer/Vector';
import VectorSource from 'ol/source/Vector';
// import { Heatmap as HeatmapLayer } from 'ol/layer'; // 註解熱區圖
import { Polygon, LineString, Point } from 'ol/geom';
import Draw from 'ol/interaction/Draw';
import Overlay from 'ol/Overlay';
import { getArea, getLength } from 'ol/sphere';
import { unByKey } from 'ol/Observable';
import OSM from 'ol/source/OSM';
import StadiaMaps from 'ol/source/StadiaMaps';
import TileWMS from 'ol/source/TileWMS';
import WMTS, { optionsFromCapabilities } from 'ol/source/WMTS';
import WMTSTileGrid from 'ol/tilegrid/WMTS';
import { get as getProjection, transform, fromLonLat, toLonLat } from 'ol/proj';
import { getTopLeft, getWidth } from 'ol/extent';
import { Style, Fill, Stroke, Circle, Text, Icon } from 'ol/style';
// import type { FeatureLike } from 'ol/Feature';
import GeoJSON from 'ol/format/GeoJSON';
import type { LocationQueryValue } from 'vue-router';
import type { GeoJsonFeature, GeoJsonFeatureCollection } from '@/types/gis';
import {
  applyFrontendFilters,
  testFrontendFilters,
  getInitialOverlayLoadingParams as getInitialParams,
  type FilterCriteria
} from '@/utils/frontendFilters';
import { validateTWD97Coordinates } from '@/utils/proj4Config';

import FilterToolbar from './filter-toolbar.vue';
import LayerManagement from './layers-drawer.vue';
import AddCustomLayerDialog from './custom-layer-dialog.vue';

// 從配置檔案導入圖層相關類型和工具
import { MAP_LAYERS, LAYER_GROUPS, updateGroupOrder, getLayerGroups, addCustomLayer, removeCustomLayer } from './map-config'
import type { MapLayer, OGCServiceConfig } from './map-config'

const router = useRouter();
const route = useRoute();

// 使用 GIS Store
const gisStore = useGisStore();
const {
  statistics,
  loading: gisLoading,
  displayMode,
  yearRange,
} = storeToRefs(gisStore);

// 使用 Domicile Store (用於地號定位的縣市、鄉鎮資料)
const domicileStore = useDomicileStore();

// 定義地圖變數，使用具體的 Map 型別
let map: Map | null = null;

// 🔥 移除全域暴露以避免與其他組件（如 step2.vue）的 Map 實例衝突
// 原因：window.__MAP__ 會在組件間造成資源競爭和渲染問題
// 替代調試方案：使用 Vue DevTools 或組件內部的 console.log

const isFluid = ref(false);
const mapContainer = ref(null);
const showSnackbar = ref(false);
const snackbarMessage = ref('');
const isDrawing = ref(false);
const isMeasuring = ref(false);
const showLayersPanel = ref(false);
const showAddCustomLayerDialog = ref(false);
const layerManagementRef = ref<InstanceType<typeof LayerManagement> | null>(null);

// 圖層圖例顯示狀態
const showLegendSnackbar = ref(false);
const selectedLegendLayer = ref<MapLayer | null>(null);

// 計算圖例文字顏色（根據背景顏色自動判斷）
const getLegendTextColor = (item: any) => {
  // 如果只顯示邊框或有圖案，返回深灰色（因為背景可能是透明的）
  if (item.borderOnly || item.pattern) {
    return '#333'
  }

  // 解析 RGB 顏色
  const color = item.color
  let r = 0, g = 0, b = 0

  // 處理 rgb(r, g, b) 格式
  const rgbMatch = color.match(/rgb\((\d+),\s*(\d+),\s*(\d+)\)/)
  if (rgbMatch) {
    r = parseInt(rgbMatch[1])
    g = parseInt(rgbMatch[2])
    b = parseInt(rgbMatch[3])
  } else {
    // 處理 HEX 格式 (#RRGGBB)
    const hex = color.replace('#', '')
    r = parseInt(hex.substring(0, 2), 16)
    g = parseInt(hex.substring(2, 4), 16)
    b = parseInt(hex.substring(4, 6), 16)
  }

  // 計算相對亮度 (使用 WCAG 公式)
  const brightness = (r * 299 + g * 587 + b * 114) / 1000

  // 亮度大於 128 使用黑色文字，否則使用白色文字
  return brightness > 128 ? '#000' : '#fff'
}

// 生成填充圖案的 CSS background-image
const getPatternStyle = (item: any) => {
  if (!item.pattern) return {}

  const patternColor = item.patternColor || item.borderColor || item.color
  const bgColor = item.patternBackgroundColor || 'rgba(255,255,255,0.9)'

  const patterns: Record<string, string> = {
    // 斜線 /
    'diagonal': `repeating-linear-gradient(
      45deg,
      ${bgColor},
      ${bgColor} 2px,
      ${patternColor} 2px,
      ${patternColor} 3px
    )`,

    // 反斜線 \
    'diagonal-reverse': `repeating-linear-gradient(
      -45deg,
      ${bgColor},
      ${bgColor} 2px,
      ${patternColor} 2px,
      ${patternColor} 3px
    )`,

    // 交叉斜線 X
    'cross-diagonal': `repeating-linear-gradient(
      45deg,
      ${bgColor},
      ${bgColor} 2px,
      ${patternColor} 2px,
      ${patternColor} 3px
    ),
    repeating-linear-gradient(
      -45deg,
      transparent,
      transparent 2px,
      ${patternColor} 2px,
      ${patternColor} 3px
    )`,

    // 水平線 ≡
    'horizontal': `repeating-linear-gradient(
      0deg,
      ${bgColor},
      ${bgColor} 2px,
      ${patternColor} 2px,
      ${patternColor} 3px
    )`,

    // 垂直線 ‖
    'vertical': `repeating-linear-gradient(
      90deg,
      ${bgColor},
      ${bgColor} 2px,
      ${patternColor} 2px,
      ${patternColor} 3px
    )`,

    // 網格 #
    'grid': `repeating-linear-gradient(
      0deg,
      ${bgColor},
      ${bgColor} 3px,
      ${patternColor} 3px,
      ${patternColor} 4px
    ),
    repeating-linear-gradient(
      90deg,
      transparent,
      transparent 3px,
      ${patternColor} 3px,
      ${patternColor} 4px
    )`,

    // 點狀 ·
    'dots': `radial-gradient(
      circle at 4px 4px,
      ${patternColor} 1px,
      ${bgColor} 1px
    )`,

    // 密集點狀
    'dots-dense': `radial-gradient(
      circle at 3px 3px,
      ${patternColor} 1.5px,
      ${bgColor} 1.5px
    )`
  }

  const backgroundImage = patterns[item.pattern] || ''
  const backgroundSize = item.pattern === 'dots' ? '8px 8px' :
                         item.pattern === 'dots-dense' ? '6px 6px' :
                         'auto'

  return {
    backgroundImage,
    backgroundSize
  }
}

// 工具面板顯示狀態
const showDrawPanel = ref(false);
const showMeasurePanel = ref(false);
const showLocationPanel = ref(false);
const isLocating = ref(false);
const isLocationLoading = ref(false);  // 定位操作進行中的 loading 狀態

// === 量測工具相關狀態 ===
const measureType = ref<'distance' | 'area' | null>(null); // 當前量測類型
const measureSource = ref<any>(null); // 量測圖層資料源
const measureLayer = ref<any>(null); // 量測圖層
const measureDraw = ref<any>(null); // Draw interaction
const measureSketch = ref<any>(null); // 當前繪製的 feature
const measureTooltipElement = ref<HTMLElement | null>(null); // tooltip DOM 元素
const measureTooltip = ref<any>(null); // 量測結果 tooltip overlay
const helpTooltipElement = ref<HTMLElement | null>(null); // 幫助提示 DOM 元素
const helpTooltip = ref<any>(null); // 幫助提示 tooltip overlay
const measureListener = ref<any>(null); // geometry change listener
const measureResults = ref({ distance: '--', area: '--' }); // 量測結果顯示

// === 定位工具相關狀態 ===
const locationType = ref<'personal' | 'coordinate' | 'landNumber'>('personal'); // 當前定位類型
const coordinateSystem = ref<'wgs84' | 'tw97'>('wgs84'); // 坐標系統
const coordinateInput = ref({
  longitude: '',
  latitude: '',
  tw97X: '',
  tw97Y: ''
});
const landNumberInput = ref({
  county: '',
  town: '',
  section: null as string | null,
  motherNumber: '',
  childNumber: ''
});

// 定位標記圖層
const locationMarkerSource = ref<any>(null);
const locationMarkerLayer = ref<any>(null);
const cadastralResultSource = ref<any>(null);  // 地籍查詢結果圖層的資料源
const cadastralResultLayer = ref<any>(null);   // 地籍查詢結果圖層

// 檢查是否有定位標記
const hasLocationMarker = computed(() => {
  return locationMarkerSource.value && locationMarkerSource.value.getFeatures().length > 0;
});

// 縣市、鄉鎮、地段選項
const countyOptions = computed(() => {
  return domicileStore.countyOptions.map(c => c.title);
});
const townOptions = ref<string[]>([]);
const nlscSections = ref<LandSection[]>([]); // NLSC 地段資料
const loadingSections = ref(false);

// API 連線狀態
const apiStatus = ref({
  isOnline: false,
  lastChecked: null as Date | null
});

// 用於強制重新渲染地段選單的 key
const sectionSelectKey = ref(0);

// 地段搜尋狀態管理
const sectionSearchText = ref('');

// 動態獲取地段選項 - 使用 NLSC API，優化搜尋支援
const sectionOptions = computed(() => {
  return nlscSections.value
    .map(section => ({
      // title 包含地段名稱和代碼，供 v-autocomplete 預設搜尋使用
      title: `${section.name} ${section.code || ''}`,
      displayName: section.name,  // 純地段名稱，供顯示使用
      value: section.code,        // 實際存儲的值，使用 API 原始格式
      code: section.code,         // 保持 API 原始格式（如 "0446"）
      name: section.name,         // 保留名稱
      office: section.office,     // 地政事務所代碼
      county_land_code: section.county_land_code,  // 縣市地政代碼（用於 NLSC API）
      town_land_code: section.town_land_code       // 鄉鎮地政代碼
    }))
    .sort((a, b) => {
      // 優先按地段代碼排序，如果沒有代碼則按名稱排序
      if (a.code && b.code) {
        return a.code.localeCompare(b.code);
      }
      return a.name.localeCompare(b.name);
    });
})

// 圖層面板拖拽相關
const isDragging = ref(false);
const dragOffset = ref({ x: 0, y: 0 });

// 工具面板初始位置計算
const getInitialToolPanelPosition = (offsetY = 0, customPanelWidth = 300) => {
  const mapControlsWidth = 80; // map-controls 工具列寬度（約估）
  const mapControlsRight = 10; // map-controls 的 right 定位
  const layersPanelWidth = showLayersPanel.value ? 300 : 0; // 圖層面板寬度（當打開時）
  const panelPadding = 10; // 面板與相鄰元素之間的間距
  const panelWidth = customPanelWidth; // 工具面板寬度（可自訂）
  const topMargin = 10; // 上邊距，與 map-controls 對齊

  // 計算面板的 x 位置：
  // 螢幕寬度 - 圖層面板寬度 - map-controls 右邊距 - map-controls 寬度 - 間距 - 面板寬度
  const x = window.innerWidth - layersPanelWidth - mapControlsRight - mapControlsWidth - panelPadding - panelWidth;

  return {
    x: Math.max(x, 10), // 確保不會超出左邊界
    y: topMargin + offsetY
  };
};

// 工具面板拖拽相關
const drawPanelPosition = ref(getInitialToolPanelPosition());
const measurePanelPosition = ref(getInitialToolPanelPosition()); // 與展繪面板相同位置
const locationPanelPosition = ref(getInitialToolPanelPosition(0, 400)); // 定位面板位置（寬度400px）
const isDraggingDraw = ref(false);
const isDraggingMeasure = ref(false);
const isDraggingLocation = ref(false);
const drawPanelDragOffset = ref({ x: 0, y: 0 });
const measurePanelDragOffset = ref({ x: 0, y: 0 });
const locationPanelDragOffset = ref({ x: 0, y: 0 });

// 從 localStorage 讀取保存的面板位置，如果沒有則使用默認位置
const getSavedPanelPosition = () => {
  // 默認位置：右上方，工具列左邊
  // 使用 rightOffset 來計算右邊距離，確保在工具列左邊
  const rightOffset = 90;  // 工具列寬度 + 間距
  const topOffset = 10;    // 頂部間距
  return {
    x: Math.max(10, (window.innerWidth || 1200) - 300 - rightOffset),
    y: topOffset
  };
};

const panelPosition = ref(getSavedPanelPosition());

// 圖層管理相關
// 創建配置的響應式副本（避免直接修改配置源）
const mapLayers = ref<MapLayer[]>(MAP_LAYERS.map(layer => ({ ...layer })))

// GIS 補助案件相關
const showSearchPanel = ref(false);
const grantPointsLayer = ref<VectorLayer | null>(null);
// const grantHeatmapLayer = ref<HeatmapLayer | null>(null); // 註解熱區圖
const grantGridLayer = ref<VectorLayer | null>(null); // 新增格網圖層

// 搜尋條件（本地狀態，用於 UI 控制）
const searchCriteria = ref({
  applicantName: '',
  landSection: '',
  caseNumber: '',
  sourceSystem: null as string | null,
  quickFilter: '',
  quickFilterTargets: [] as string[]
});

// === 新增：疊加圖層初始載入條件參數 ===
// 統一的疊加圖層初始載入條件，目前設置為僅載入當年度資料
// 使用導入的統一函數
const getInitialOverlayLoadingParams = getInitialParams

// === 新增：篩選工具欄相關變數 ===
// 注意：這些變數已由 FilterToolbar 組件內部管理，此處保留用於相容性
const quickFilter = ref('');

// 獲取當前年度（民國年）
const getCurrentYear = () => {
  return new Date().getFullYear() - 1911;
};

// 篩選條件
const filterCriteria = ref({
  applicantName: '',
  landSection: '',
  landNumber: '',
  caseNumber: '',
  sourceSystem: null as string | null,
  yearStart: 114, // 預設值，onMounted 時會更新
  yearEnd: 114
});

// 資料來源選項
const filterSourceOptions = [
  { title: '全部', value: null },
  { title: '新系統案件', value: 'new_aerc' },
  { title: '歷史案件', value: 'legacy_farmdata' }
];

// 用於追蹤地圖是否已完全初始化
const mapInitialized = ref(false);

// 用於防止縮放事件循環
const isAutoZooming = ref(false);
const isProgrammaticZoom = ref(false);

// 用於追蹤已載入的原始資料，供前端篩選使用
const allLoadedFeatures = ref<GeoJsonFeature[]>([]);
const filteredFeatures = ref<GeoJsonFeature[]>([]);

// === FilterToolbar 事件處理 ===
// 處理篩選變更事件
const handleFilterChange = async (event: { criteria: FilterCriteria; results: GeoJsonFeature[]; resultCount: number }) => {
  // 檢查年度範圍是否變更
  const currentYearStart = yearRange.value.current[0];
  const currentYearEnd = yearRange.value.current[1];
  const newYearStart = event.criteria.yearStart;
  const newYearEnd = event.criteria.yearEnd;

  const yearRangeChanged = currentYearStart !== newYearStart || currentYearEnd !== newYearEnd;

  if (yearRangeChanged) {
    console.log(`📅 [FilterChange] 年度範圍變更: ${currentYearStart}-${currentYearEnd} → ${newYearStart}-${newYearEnd}，觸發重新載入`);

    // 更新年度範圍到 GIS Store
    const yearRangeArray: [number, number] = [newYearStart, newYearEnd];
    yearRange.value.current = yearRangeArray;
    await gisStore.updateYearRange(yearRangeArray);

    // 清空已載入的資料，強制重新載入
    allLoadedFeatures.value = [];
    filteredFeatures.value = [];

    // 觸發地圖圖層重新載入
    refreshLayerData();

    // 顯示提示訊息
    showSnackbar.value = true;
    snackbarMessage.value = `已更新年度範圍為民國${newYearStart}-${newYearEnd}年，正在重新載入資料...`;
  } else {
    // 年度範圍未變更，只進行前端篩選
    console.log(`🔍 [FilterChange] 僅前端篩選，找到 ${event.resultCount} 筆結果`);

    // 更新篩選結果
    filteredFeatures.value = event.results;

    // 更新地圖顯示
    updateLayersWithFilteredData();

    // 顯示篩選結果提示
    if (event.criteria.quickFilter) {
      const message = `快速篩選「${event.criteria.quickFilter}」找到 ${event.resultCount} 筆結果`;
      showSnackbar.value = true;
      snackbarMessage.value = message;
    }
  }
};

// 處理篩選面板展開/收合事件
const handleFilterExpanded = (expanded: boolean) => {
  // 可以在這裡處理面板狀態變更邏輯
  console.log('篩選面板展開狀態:', expanded);
};

// 處理篩選重置事件
const handleFilterReset = () => {
  // 重新載入原始資料
  if (allLoadedFeatures.value.length > 0) {
    filteredFeatures.value = allLoadedFeatures.value;
    updateLayersWithFilteredData();
  }

  showSnackbar.value = true;
  snackbarMessage.value = '篩選條件已重置';
};

// 獲取初始篩選條件
const getInitialFilterCriteria = (): FilterCriteria => {
  const initialParams = getInitialParams();
  const currentYear = new Date().getFullYear() - 1911;

  return {
    applicantName: '',
    landSection: '',
    landNumber: '',
    caseNumber: '',
    sourceSystem: null,
    yearStart: initialParams.apply_year_min || currentYear,
    yearEnd: initialParams.apply_year_max || currentYear
  };
};

const toggleLayers = async () => {
  showLayersPanel.value = !showLayersPanel.value;
  await nextTick();

  // 當圖層面板打開時，檢查是否與工具面板重疊
  if (showLayersPanel.value) {
    const layersPanelWidth = 300; // 圖層面板寬度
    const layersPanelRight = window.innerWidth; // 圖層面板從右側邊界開始
    const layersPanelLeft = layersPanelRight - layersPanelWidth;
    const buffer = 10; // 緩衝距離

    // 檢查展繪面板是否與圖層面板重疊（含緩衝區）
    if (showDrawPanel.value) {
      const drawPanelWidth = 300;
      const drawPanelRight = drawPanelPosition.value.x + drawPanelWidth;

      // 如果展繪面板右側邊界 + 緩衝 >= 圖層面板左側邊界，則有重疊
      if (drawPanelRight + buffer >= layersPanelLeft) {
        drawPanelPosition.value = getInitialToolPanelPosition();
      }
    }

    // 檢查量測面板是否與圖層面板重疊（含緩衝區）
    if (showMeasurePanel.value) {
      const measurePanelWidth = 300;
      const measurePanelRight = measurePanelPosition.value.x + measurePanelWidth;

      // 如果量測面板右側邊界 + 緩衝 >= 圖層面板左側邊界，則有重疊
      if (measurePanelRight + buffer >= layersPanelLeft) {
        measurePanelPosition.value = getInitialToolPanelPosition();
      }
    }

    // 檢查定位面板是否與圖層面板重疊（含緩衝區）
    if (showLocationPanel.value) {
      const locationPanelWidth = 400;
      const locationPanelRight = locationPanelPosition.value.x + locationPanelWidth;

      // 如果定位面板右側邊界 + 緩衝 >= 圖層面板左側邊界，則有重疊
      if (locationPanelRight + buffer >= layersPanelLeft) {
        locationPanelPosition.value = getInitialToolPanelPosition(0, 400);
      }
    }
  }
};

const onDrag = (event: MouseEvent) => {
  if (!isDragging.value) return;

  // 計算新位置
  const newX = event.clientX - dragOffset.value.x;
  const newY = event.clientY - dragOffset.value.y;

  // 獲取視窗邊界
  const maxX = window.innerWidth - 300; // 面板寬度約300px
  const maxY = window.innerHeight - 400; // 面板高度約400px

  // 限制在視窗範圍內
  panelPosition.value = {
    x: Math.max(0, Math.min(newX, maxX)),
    y: Math.max(0, Math.min(newY, maxY))
  };
};

const stopDrag = () => {
  isDragging.value = false;

  // 移除全局監聽器
  document.removeEventListener('mousemove', onDrag);
  document.removeEventListener('mouseup', stopDrag);
};

// 展繪面板拖曳功能
const startDrawDrag = (event: MouseEvent) => {
  isDraggingDraw.value = true;

  // 計算滑鼠相對於面板當前位置的偏移量
  drawPanelDragOffset.value = {
    x: event.clientX - drawPanelPosition.value.x,
    y: event.clientY - drawPanelPosition.value.y
  };

  // 添加全局監聽器
  document.addEventListener('mousemove', onDrawDrag);
  document.addEventListener('mouseup', stopDrawDrag);

  // 防止文字選擇
  event.preventDefault();
};

const onDrawDrag = (event: MouseEvent) => {
  if (!isDraggingDraw.value) return;

  // 計算新位置
  const newX = event.clientX - drawPanelDragOffset.value.x;
  const newY = event.clientY - drawPanelDragOffset.value.y;

  // 確保面板不會超出邊界
  const maxX = window.innerWidth - 300; // 面板寬度
  const maxY = window.innerHeight - 200; // 面板最小高度

  drawPanelPosition.value = {
    x: Math.max(0, Math.min(newX, maxX)),
    y: Math.max(0, Math.min(newY, maxY))
  };
};

const stopDrawDrag = () => {
  isDraggingDraw.value = false;

  // 移除全局監聽器
  document.removeEventListener('mousemove', onDrawDrag);
  document.removeEventListener('mouseup', stopDrawDrag);
};

// 量測面板拖曳功能
const startMeasureDrag = (event: MouseEvent) => {
  isDraggingMeasure.value = true;

  // 計算滑鼠相對於面板當前位置的偏移量
  measurePanelDragOffset.value = {
    x: event.clientX - measurePanelPosition.value.x,
    y: event.clientY - measurePanelPosition.value.y
  };

  // 添加全局監聽器
  document.addEventListener('mousemove', onMeasureDrag);
  document.addEventListener('mouseup', stopMeasureDrag);

  // 防止文字選擇
  event.preventDefault();
};

const onMeasureDrag = (event: MouseEvent) => {
  if (!isDraggingMeasure.value) return;

  // 計算新位置
  const newX = event.clientX - measurePanelDragOffset.value.x;
  const newY = event.clientY - measurePanelDragOffset.value.y;

  // 確保面板不會超出邊界
  const maxX = window.innerWidth - 300; // 面板寬度
  const maxY = window.innerHeight - 200; // 面板最小高度

  measurePanelPosition.value = {
    x: Math.max(0, Math.min(newX, maxX)),
    y: Math.max(0, Math.min(newY, maxY))
  };
};

const stopMeasureDrag = () => {
  isDraggingMeasure.value = false;

  // 移除全局監聽器
  document.removeEventListener('mousemove', onMeasureDrag);
  document.removeEventListener('mouseup', stopMeasureDrag);
};

// 定位面板拖曳功能
const startLocationDrag = (event: MouseEvent) => {
  isDraggingLocation.value = true;

  // 計算滑鼠相對於面板當前位置的偏移量
  locationPanelDragOffset.value = {
    x: event.clientX - locationPanelPosition.value.x,
    y: event.clientY - locationPanelPosition.value.y
  };

  // 添加全局監聽器
  document.addEventListener('mousemove', onLocationDrag);
  document.addEventListener('mouseup', stopLocationDrag);

  event.preventDefault();
};

const onLocationDrag = (event: MouseEvent) => {
  if (!isDraggingLocation.value) return;

  // 計算新位置
  const newX = event.clientX - locationPanelDragOffset.value.x;
  const newY = event.clientY - locationPanelDragOffset.value.y;

  // 限制在視窗範圍內
  const locationPanelWidth = 400;
  const locationPanelMinHeight = 350;
  const maxX = window.innerWidth - locationPanelWidth;
  const maxY = window.innerHeight - locationPanelMinHeight;

  locationPanelPosition.value = {
    x: Math.max(0, Math.min(newX, maxX)),
    y: Math.max(0, Math.min(newY, maxY))
  };
};

const stopLocationDrag = () => {
  isDraggingLocation.value = false;

  // 移除全局監聽器
  document.removeEventListener('mousemove', onLocationDrag);
  document.removeEventListener('mouseup', stopLocationDrag);
};


// 選擇底圖圖層 (單選模式)
const selectBaseLayer = (layerName: string | null) => {
  if (!layerName) {
    console.warn('收到空的圖層名稱');
    return;
  }

  console.log('切換底圖圖層:', layerName);

  // 找到選中的圖層
  const selectedLayer = mapLayers.value.find(layer =>
    layer.category === 'baselayer' && layer.name === layerName
  );

  if (!selectedLayer) {
    console.error('找不到指定的底圖圖層:', layerName);
    return;
  }

  // 關閉所有底圖圖層
  mapLayers.value.forEach(layer => {
    if (layer.category === 'baselayer') {
      layer.visible = false;
      if (layer.layer) {
        layer.layer.setVisible(false);
      }
    }
  });

  // 啟用選中的底圖圖層
  selectedLayer.visible = true;
  if (selectedLayer.layer) {
    selectedLayer.layer.setVisible(true);
    console.log('底圖圖層', selectedLayer.name, '已啟用');
  }
};

// LayerManagement 組件事件處理函數
const handleLayerVisibilityChanged = (layer: MapLayer) => {
  // 直接調用現有的圖層可見性處理邏輯
  if (layer.layer) {
    layer.layer.setVisible(layer.visible);
  }
  console.log('圖層可見性已更新:', layer.name, '可見:', layer.visible);

  // 更新所有圖層的 zIndex（因為可見圖層集合已改變）
  updateOverlayLayersZIndex();
};

const handleLayerOpacityChanged = (layer: MapLayer) => {
  // 直接調用現有的透明度處理邏輯
  if (layer.layer) {
    layer.layer.setOpacity(layer.opacity);
  }
  console.log('圖層透明度已更新:', layer.name, '透明度:', layer.opacity);
};

const handleBaseLayerSelected = (layerName: string) => {
  // 直接調用現有的底圖選擇邏輯
  selectBaseLayer(layerName);
};

const handleDisplayModeChanged = (mode: string) => {
  // 更新顯示模式，使用 gisStore 的方法
  gisStore.updateDisplayMode(mode as 'points' | 'grid');
  console.log('顯示模式已更改:', mode);
};

// 更新所有可見套疊圖層的 zIndex
const updateOverlayLayersZIndex = () => {
  if (!map) return

  // 獲取所有已開啟的套疊圖層
  const visibleOverlayLayers = mapLayers.value
    .filter(l => l.category === 'overlay' && l.layer && l.visible)

  // 按 LAYER_GROUPS 的 group order，然後按 MapLayer 的 order 排序
  // group order 大的在下層，group order 小的在上層
  // 同 group 內 order 大的在上層
  const sortedLayers = visibleOverlayLayers.sort((a, b) => {
    const groupA = LAYER_GROUPS[a.group as keyof typeof LAYER_GROUPS]
    const groupB = LAYER_GROUPS[b.group as keyof typeof LAYER_GROUPS]

    // 先按 group order 排序（降序：order 大的在下層）
    if (groupA.order !== groupB.order) {
      return groupB.order - groupA.order
    }
    // 同 group 內按 layer order 排序（升序：order 小的在下層）
    return a.order - b.order
  })

  // 分配 zIndex：從 1 開始，最下層圖層 zIndex = 1，最上層 = visibleCount
  sortedLayers.forEach((l, index) => {
    const zIndex = index + 1
    l.layer.setZIndex(zIndex)
  })

  console.log('[Debug] 套疊圖層 zIndex 已更新:', sortedLayers.map((l, idx) => `${l.name}(zIndex:${idx + 1})`).join(' -> '))
}

// 處理圖層順序變更
const handleLayerOrderChanged = (layerId: string, direction: 'up' | 'down') => {
  const layer = mapLayers.value.find(l => l.id === layerId)
  if (!layer || !layer.layer) return

  // 找到同分組的所有套疊圖層，按 order 降序排列（order 大的在上層）
  const layersInGroup = mapLayers.value
    .filter(l => l.category === 'overlay' && l.group === layer.group)
    .sort((a, b) => b.order - a.order) // 降序

  const currentIndex = layersInGroup.findIndex(l => l.id === layerId)
  if (currentIndex === -1) return

  // up = 向上移動 = order 增加 = 在降序數組中向前移動
  // down = 向下移動 = order 減少 = 在降序數組中向後移動
  const targetIndex = direction === 'up' ? currentIndex - 1 : currentIndex + 1
  if (targetIndex < 0 || targetIndex >= layersInGroup.length) return

  // 找到相鄰圖層並交換 order 值
  const targetLayer = layersInGroup[targetIndex]
  const tempOrder = layer.order
  layer.order = targetLayer.order
  targetLayer.order = tempOrder

  console.log(`圖層 ${layer.name} 已${direction === 'up' ? '上移' : '下移'}（order: ${tempOrder} → ${layer.order}）`)

  // 更新所有圖層的 zIndex
  updateOverlayLayersZIndex()
};

// 處理分組順序變更
const handleGroupOrderChanged = (groupId: string, direction: 'up' | 'down') => {
  const groups = getLayerGroups().sort((a, b) => a.order - b.order) // 升序排列
  const currentIndex = groups.findIndex(g => g.id === groupId)
  if (currentIndex === -1) return

  // up = 向上移動 = order 減少 = 在升序數組中向前移動
  // down = 向下移動 = order 增加 = 在升序數組中向後移動
  const targetIndex = direction === 'up' ? currentIndex - 1 : currentIndex + 1
  if (targetIndex < 0 || targetIndex >= groups.length) return

  // 交換兩個分組的 order 值
  const currentGroup = groups[currentIndex]
  const targetGroup = groups[targetIndex]
  const tempOrder = currentGroup.order

  updateGroupOrder(currentGroup.id, targetGroup.order)
  updateGroupOrder(targetGroup.id, tempOrder)

  console.log(`分組 ${currentGroup.title} 已${direction === 'up' ? '上移' : '下移'}（order: ${tempOrder} → ${targetGroup.order}）`)

  // 更新所有圖層的 zIndex
  updateOverlayLayersZIndex()
};

// 處理刪除自訂圖層
const handleRemoveCustomLayer = (layerId: string) => {
  const layerIndex = mapLayers.value.findIndex(l => l.id === layerId)
  if (layerIndex === -1) {
    console.warn(`圖層 ${layerId} 不存在`)
    return
  }

  const layerConfig = mapLayers.value[layerIndex]
  if (!layerConfig.isCustom) {
    console.warn(`圖層 ${layerId} 不是自訂圖層`)
    return
  }

  const layerName = layerConfig.name

  // 從地圖移除 OpenLayers 圖層
  if (map) {
    // 從地圖的圖層集合中查找並移除
    // 使用我們設置的自訂屬性來識別圖層
    const allLayers = map.getLayers().getArray()
    const targetLayer = allLayers.find(layer => {
      return layer.get('customLayerId') === layerId
    })

    if (targetLayer) {
      map.removeLayer(targetLayer)
      console.log(`已從地圖移除圖層: ${layerName} (ID: ${layerId})`)
    } else {
      console.warn(`在地圖上找不到圖層 ${layerName} (ID: ${layerId})`)
    }
  }

  // 從響應式陣列移除圖層
  mapLayers.value.splice(layerIndex, 1)

  // 從配置中移除圖層
  removeCustomLayer(layerId)

  // 重新計算同分組內剩餘圖層的 order 值,確保連續性
  const customLayers = mapLayers.value.filter(l => l.group === 'custom')
  customLayers
    .sort((a, b) => b.order - a.order) // 按 order 降序排列
    .forEach((layer, index) => {
      layer.order = customLayers.length - index // 重新分配順序
    })

  // 重新計算所有套疊圖層的 zIndex
  updateOverlayLayersZIndex()

  // 顯示提示訊息
  snackbarMessage.value = `已刪除自訂圖層: ${layerName}`
  showSnackbar.value = true

  console.log(`已刪除自訂圖層: ${layerName} (ID: ${layerId})`)
  console.log(`剩餘自訂圖層數量: ${customLayers.length}`)
}

// 處理顯示圖層圖例
const handleShowLegend = (layer: MapLayer) => {
  selectedLegendLayer.value = layer
  showLegendSnackbar.value = true
  console.log(`顯示圖層圖例: ${layer.name}`, layer.legend)
}

// 生成隨機顏色（明亮且易於區分的顏色）
const generateRandomColor = () => {
  // 使用 HSL 色彩空間生成明亮且飽和的顏色
  const hue = Math.floor(Math.random() * 360) // 0-360
  const saturation = 65 + Math.floor(Math.random() * 20) // 65-85% 飽和度
  const lightness = 45 + Math.floor(Math.random() * 15) // 45-60% 亮度

  // HSL 轉 RGB
  const h = hue / 360
  const s = saturation / 100
  const l = lightness / 100

  const hue2rgb = (p: number, q: number, t: number) => {
    if (t < 0) t += 1
    if (t > 1) t -= 1
    if (t < 1/6) return p + (q - p) * 6 * t
    if (t < 1/2) return q
    if (t < 2/3) return p + (q - p) * (2/3 - t) * 6
    return p
  }

  let r, g, b
  if (s === 0) {
    r = g = b = l // achromatic
  } else {
    const q = l < 0.5 ? l * (1 + s) : l + s - l * s
    const p = 2 * l - q
    r = hue2rgb(p, q, h + 1/3)
    g = hue2rgb(p, q, h)
    b = hue2rgb(p, q, h - 1/3)
  }

  const toHex = (x: number) => {
    const hex = Math.round(x * 255).toString(16)
    return hex.length === 1 ? '0' + hex : hex
  }

  return `#${toHex(r)}${toHex(g)}${toHex(b)}`
}

// 處理 Shapefile 圖層載入
const handleShapefileLoaded = (
  layersData: Array<{ name: string; geoJson: GeoJsonFeatureCollection }>,
  callback: (success: boolean, error?: string) => void
) => {
  if (!map) {
    callback(false, '地圖未初始化')
    return
  }

  try {
    const addedLayers: MapLayer[] = []
    let combinedExtent: number[] | null = null

    // 遍歷每個圖層
    for (const data of layersData) {
      // 檢查是否有 features
      if (!data.geoJson.features || data.geoJson.features.length === 0) {
        console.warn(`[Shapefile] 圖層 ${data.name} 沒有有效的幾何圖形資料，跳過`)
        continue
      }

      console.log(`[Shapefile] 載入圖層: ${data.name}`, {
        featureCount: data.geoJson.features.length
      })

      // 建立 VectorSource 從 GeoJSON
      const vectorSource = new VectorSource({
        features: new GeoJSON().readFeatures(data.geoJson, {
          dataProjection: 'EPSG:4326',
          featureProjection: 'EPSG:3857'
        })
      })

      const featureCount = vectorSource.getFeatures().length

      // 驗證是否成功讀取 features
      if (featureCount === 0) {
        console.warn(`[Shapefile] 無法解析圖層 ${data.name} 的幾何資料，可能缺少坐標系統定義，跳過`)
        continue
      }

      // 檢查範圍是否有效
      const extent = vectorSource.getExtent()

      if (!extent || !extent.every(val => isFinite(val))) {
        console.warn(`[Shapefile] 圖層 ${data.name} 坐標範圍無效，跳過`)
        continue
      }

      // 檢查範圍是否在合理的地球範圍內（EPSG:3857）
      const [minX, minY, maxX, maxY] = extent
      const earthBounds = {
        minX: -20037508.34,
        maxX: 20037508.34,
        minY: -20037508.34,
        maxY: 20037508.34
      }

      if (minX < earthBounds.minX || maxX > earthBounds.maxX ||
          minY < earthBounds.minY || maxY > earthBounds.maxY) {
        console.warn(`[Shapefile] 圖層 ${data.name} 坐標範圍超出地球範圍，跳過`)
        continue
      }

      // 建立圖層配置
      const layerId = `custom-shapefile-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`

      // 生成隨機顏色
      const randomColor = generateRandomColor()
      const strokeColor = randomColor
      const fillColor = `${randomColor}4D` // 添加 30% 透明度 (4D = 77/255 ≈ 30%)

      // 建立 VectorLayer
      const vectorLayer = new VectorLayer({
        source: vectorSource,
        style: new Style({
          stroke: new Stroke({
            color: strokeColor,
            width: 2
          }),
          fill: new Fill({
            color: fillColor
          })
        }),
        visible: true,
        opacity: 0.8
      })

      // 在 OpenLayers 圖層上設置自訂屬性以便後續識別
      vectorLayer.set('customLayerId', layerId)
      vectorLayer.set('customLayerName', data.name)
      vectorLayer.set('customLayerColor', randomColor) // 保存顏色以便後續使用
      const newLayer: MapLayer = {
        id: layerId,
        name: data.name,
        category: 'overlay',
        group: 'custom',
        visible: true,
        opacity: 0.8,
        description: `Shapefile 圖層 (${featureCount} 個特徵)`,
        order: 0,
        layer: vectorLayer,
        isCustom: true
      }

      // 加入到配置
      addCustomLayer(newLayer)
      mapLayers.value.push(newLayer)

      // 加入到地圖
      map.addLayer(vectorLayer)

      addedLayers.push(newLayer)

      // 更新組合範圍
      if (!combinedExtent) {
        combinedExtent = [...extent]
      } else {
        combinedExtent = [
          Math.min(combinedExtent[0], extent[0]),
          Math.min(combinedExtent[1], extent[1]),
          Math.max(combinedExtent[2], extent[2]),
          Math.max(combinedExtent[3], extent[3])
        ]
      }

      console.log(`[Shapefile] 已新增圖層: ${data.name} (${featureCount} features)`)
    }

    // 檢查是否至少成功加載一個圖層
    if (addedLayers.length === 0) {
      throw new Error('沒有成功載入任何圖層，請確認 Shapefile 格式是否正確')
    }

    // 更新 zIndex
    updateOverlayLayersZIndex()

    // 縮放至所有圖層的組合範圍
    if (combinedExtent) {
      map.getView().fit(combinedExtent, {
        padding: [50, 50, 50, 50],
        duration: 1000
      })
    }

    snackbarMessage.value = `成功載入 ${addedLayers.length} 個 Shapefile 圖層`
    showSnackbar.value = true

    console.log(`[Shapefile] 批次載入完成: ${addedLayers.length} 個圖層`)

    // 展開自訂圖層分組
    if (layerManagementRef.value) {
      layerManagementRef.value.expandCustomGroup()
    }

    // 通知對話框成功
    callback(true)

  } catch (error) {
    const errorMsg = (error as Error).message
    console.error('[Shapefile] 圖層建立失敗:', error)
    snackbarMessage.value = `Shapefile 圖層建立失敗: ${errorMsg}`
    showSnackbar.value = true

    // 通知對話框失敗
    callback(false, errorMsg)
  }
}

// 處理自訂圖層新增
const handleCustomLayersAdded = (configs: OGCServiceConfig[]) => {
  if (!map) return

  configs.forEach((config) => {
    // 生成唯一 ID
    const layerId = `custom-${config.type.toLowerCase()}-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`

    // 建立 OpenLayers 圖層實例
    let olLayer: TileLayer<TileWMS | WMTS> | null = null

    if (config.type === 'WMS') {
      olLayer = new TileLayer({
        source: new TileWMS({
          url: config.url,
          params: {
            LAYERS: config.layerName,
            VERSION: config.version || '1.3.0',
            ...config.params
          },
          serverType: 'geoserver'
        }),
        visible: true,
        opacity: 0.8
      })
    } else if (config.type === 'WMTS') {
      // WMTS 需要 rawCapabilities 來建立 TileMatrixSet
      if (!config.rawCapabilities) {
        console.error(`WMTS 圖層 ${config.layerName} 缺少 rawCapabilities`)
        snackbarMessage.value = `WMTS 圖層 ${config.layerName} 配置不完整`
        showSnackbar.value = true
        return
      }

      try {
        // 使用 OpenLayers 內建函數生成 WMTS 配置
        const wmtsOptions = optionsFromCapabilities(config.rawCapabilities, {
          layer: config.layerName
        })

        if (!wmtsOptions) {
          throw new Error(`無法為圖層 ${config.layerName} 生成 WMTS 配置`)
        }

        olLayer = new TileLayer({
          source: new WMTS(wmtsOptions),
          visible: true,
          opacity: 0.8
        })

        console.log(`成功建立 WMTS 圖層: ${config.layerName}`)
      } catch (error) {
        console.error(`WMTS 圖層建立失敗:`, error)
        snackbarMessage.value = `WMTS 圖層 ${config.layerName} 建立失敗: ${(error as Error).message}`
        showSnackbar.value = true
        return
      }
    } else if (config.type === 'WFS') {
      // WFS 通常用 VectorLayer，這裡暫不實作
      console.warn('WFS 圖層需要使用 VectorLayer，目前暫不支援')
      return
    }

    if (!olLayer) return

    // 在 OpenLayers 圖層上設置自訂屬性以便後續識別
    olLayer.set('customLayerId', layerId)
    olLayer.set('customLayerName', config.title || config.layerName)

    // 建立 MapLayer 配置
    const newLayer: MapLayer = {
      id: layerId,
      name: config.title || config.layerName,
      category: 'overlay',
      group: 'custom',
      visible: true,
      opacity: 0.8,
      description: config.abstract,
      order: 0, // addCustomLayer 會自動計算
      layer: olLayer,
      isCustom: true,
      ogcConfig: config
    }

    // 加入到全局配置
    addCustomLayer(newLayer)

    // 直接加入到 mapLayers 響應式陣列(不破壞既有引用)
    mapLayers.value.push(newLayer)

    // 加入到地圖
    if (map) {
      map.addLayer(olLayer)
    }

    console.log(`已新增自訂圖層: ${newLayer.name} (${config.type})`)
  })

  // 所有圖層加入完成後,統一重新計算 zIndex
  updateOverlayLayersZIndex()

  // 展開自訂圖層分組
  if (layerManagementRef.value) {
    layerManagementRef.value.expandCustomGroup()
  }

  // 顯示成功訊息
  snackbarMessage.value = `成功加入 ${configs.length} 個自訂圖層`
  showSnackbar.value = true
}

// 添加定位標記到地圖
const addLocationMarker = (coordinates: number[], label: string) => {
  if (!locationMarkerSource.value) return;

  // 清除舊的標記
  locationMarkerSource.value.clear();

  // 創建新的標記點
  const marker = new Feature({
    geometry: new Point(coordinates),
    name: label
  });

  locationMarkerSource.value.addFeature(marker);
};

// 清除定位標記及地籍圖層
const clearLocationMarker = () => {
  let cleared = false;

  // 清除定位標記
  if (locationMarkerSource.value) {
    locationMarkerSource.value.clear();
    cleared = true;
  }

  // 清除地籍查詢結果圖層
  if (cadastralResultSource.value) {
    cadastralResultSource.value.clear();
    cleared = true;
  }

  if (cleared) {
    snackbarMessage.value = '已清除定位標記及地籍圖層';
    showSnackbar.value = true;
  }
};

// 定位功能
const getCurrentLocation = () => {
  if (!navigator.geolocation) {
    snackbarMessage.value = '您的瀏覽器不支援定位功能';
    showSnackbar.value = true;
    return;
  }

  isLocationLoading.value = true;

  navigator.geolocation.getCurrentPosition(
    (position) => {
      if (!map) {
        isLocationLoading.value = false;
        return;
      }

      const { longitude, latitude } = position.coords;
      const center = fromLonLat([longitude, latitude]);

      // 添加標記
      addLocationMarker(center, '我的位置');

      map.getView().animate({
        center: center,
        zoom: 16,
        duration: 500
      });

      snackbarMessage.value = '已定位到您的位置';
      showSnackbar.value = true;
      isLocationLoading.value = false;
    },
    (error) => {
      console.error('定位失敗:', error);
      snackbarMessage.value = '定位失敗，請檢查位置權限設定';
      showSnackbar.value = true;
      isLocationLoading.value = false;
    },
    {
      enableHighAccuracy: true,
      timeout: 10000,
      maximumAge: 300000
    }
  );
};

// 坐標定位功能（整合地籍查詢）
const locateByCoordinate = async () => {
  if (!map) return;

  isLocationLoading.value = true;
  let center: number[] = [];
  let lon: number = 0;
  let lat: number = 0;
  let srid: '4326' | '3826' = '4326';

  if (coordinateSystem.value === 'wgs84') {
    // WGS84 經緯度坐標
    lon = parseFloat(coordinateInput.value.longitude);
    lat = parseFloat(coordinateInput.value.latitude);

    if (isNaN(lon) || isNaN(lat)) {
      snackbarMessage.value = '請輸入有效的經緯度坐標';
      showSnackbar.value = true;
      isLocationLoading.value = false;
      return;
    }

    // 檢查範圍（台灣大約範圍）
    if (lon < 119 || lon > 122 || lat < 21 || lat > 26) {
      snackbarMessage.value = '坐標超出台灣範圍，請檢查輸入';
      showSnackbar.value = true;
      isLocationLoading.value = false;
      return;
    }

    center = fromLonLat([lon, lat]);
    srid = '4326';
  } else {
    // TW97 (TWD97) 坐標
    const tw97X = parseFloat(coordinateInput.value.tw97X);
    const tw97Y = parseFloat(coordinateInput.value.tw97Y);

    if (isNaN(tw97X) || isNaN(tw97Y)) {
      snackbarMessage.value = '請輸入有效的 TW97 坐標';
      showSnackbar.value = true;
      isLocationLoading.value = false;
      return;
    }

    // 驗證 TWD97 坐標範圍
    if (!validateTWD97Coordinates(tw97X, tw97Y)) {
      snackbarMessage.value = 'TWD97 坐標超出有效範圍（X: 140000-360000, Y: 2400000-2800000）';
      showSnackbar.value = true;
      isLocationLoading.value = false;
      return;
    }

    // 使用 proj4 進行精確轉換：EPSG:3826 (TWD97) → EPSG:3857 (Web Mercator)
    // proj4 已在應用初始化時註冊，transform 函數可直接使用
    try {
      center = transform([tw97X, tw97Y], 'EPSG:3826', 'EPSG:3857');
      // 用於 NLSC API 查詢
      lon = tw97X;
      lat = tw97Y;
      srid = '3826';
    } catch (error) {
      console.error('TWD97 coordinate transformation failed:', error);
      snackbarMessage.value = 'TWD97 坐標轉換失敗，請檢查坐標是否正確';
      showSnackbar.value = true;
      isLocationLoading.value = false;
      return;
    }
  }

  // 🗺️ 使用 NLSC API 查詢地籍圖
  try {
    console.log(`🔍 查詢坐標地籍圖: [${lon}, ${lat}], SRID: ${srid}`);
    const result = await queryCadastralMapByPoint(lon, lat, srid, 'gml');

    if (result.success && result.features.length > 0) {
      // 清空舊的地籍查詢結果
      if (cadastralResultSource.value) {
        cadastralResultSource.value.clear();
      }

      // 為地籍 features 設置標識，避免與案件 features 混淆
      result.features.forEach(feature => {
        feature.set('cadastral', true);
      });

      // 將所有 features 加入到地籍結果圖層（與地籍定位相同）
      if (cadastralResultSource.value) {
        cadastralResultSource.value.addFeatures(result.features);
        console.log(`✅ 已加入 ${result.features.length} 筆地籍 feature 到圖層`);
      }
    } else {
      console.warn('⚠️ 此坐標位置查無地籍資料');
    }
  } catch (error) {
    console.error('❌ 地籍查詢失敗:', error);
    // 不中斷定位流程，僅記錄錯誤
  }

  // 添加標記
  const label = coordinateSystem.value === 'wgs84'
    ? `坐標定位 (${coordinateInput.value.longitude}, ${coordinateInput.value.latitude})`
    : `坐標定位 (TW97: ${coordinateInput.value.tw97X}, ${coordinateInput.value.tw97Y})`;
  addLocationMarker(center, label);

  map.getView().animate({
    center: center,
    zoom: 16,
    duration: 500
  });

  snackbarMessage.value = '已定位到指定坐標';
  showSnackbar.value = true;
  isLocationLoading.value = false;
};

// 地號定位相關函數

// 地段搜尋事件處理函數
const onSectionSearchUpdate = (searchValue: string) => {
  sectionSearchText.value = searchValue;
};

// 地段選單失焦事件處理函數
const onSectionBlur = () => {
  // 當失焦時清空搜尋文字，避免影響下次搜尋
  sectionSearchText.value = '';
};

// 格式化母地號：失去焦點時自動補正為四位數
const formatMotherNumber = () => {
  if (landNumberInput.value.motherNumber && landNumberInput.value.motherNumber.trim()) {
    // 只保留數字
    const cleanValue = landNumberInput.value.motherNumber.replace(/\D/g, '');
    if (cleanValue) {
      // 補正為四位數
      landNumberInput.value.motherNumber = cleanValue.padStart(4, '0');
    } else {
      // 如果清理後沒有數字，清空欄位
      landNumberInput.value.motherNumber = '';
    }
  }
};

// 格式化子地號：失去焦點時自動補正為四位數
const formatChildNumber = () => {
  if (landNumberInput.value.childNumber && landNumberInput.value.childNumber.trim()) {
    // 只保留數字
    const cleanValue = landNumberInput.value.childNumber.replace(/\D/g, '');
    if (cleanValue) {
      // 補正為四位數
      landNumberInput.value.childNumber = cleanValue.padStart(4, '0');
    } else {
      // 如果清理後沒有數字，清空欄位
      landNumberInput.value.childNumber = '';
    }
  }
};

// 縣市變更處理
const onCountyChange = async (newCounty: string) => {
  // 重置鄉鎮和地段
  landNumberInput.value.town = '';
  landNumberInput.value.section = null;
  nlscSections.value = [];

  // 強制重新渲染地段選單
  sectionSelectKey.value++;

  // 使用 nextTick 確保重置生效
  await nextTick();

  if (!newCounty) {
    townOptions.value = [];
    return;
  }

  // 找到對應的縣市
  const county = domicileStore.countyOptions.find(c => c.title === newCounty);
  if (!county) {
    console.error('County not found:', newCounty);
    return;
  }

  // 載入該縣市的鄉鎮資料
  try {
    await domicileStore.loadTownsByCountyId(county.value);

    // 取得鄉鎮列表
    const towns = domicileStore.getTownsForCountyId(county.value);
    townOptions.value = towns.map(t => t.title);

    // 特殊城市處理（新竹市、嘉義市不需要選擇鄉鎮，直接載入地段）
    if (specialCities[newCounty] && county.land_code) {
      // 為特殊城市設定一個虛擬的town值
      landNumberInput.value.town = 'SPECIAL_CITY_AUTO';

      const specialCode = specialCities[newCounty].code;
      loadingSections.value = true;
      try {
        await domicileStore.loadLandSectionsByLandCodes(county.land_code, specialCode);
        nlscSections.value = domicileStore.landSections.filter(s =>
          s.county_land_code === county.land_code && s.town_land_code === specialCode
        );
        console.log(`已自動載入 ${newCounty} 的地段資料 (${specialCode}):`, nlscSections.value.length);
      } catch (error) {
        console.error('Failed to load land sections for special city:', error);
        nlscSections.value = [];
        snackbarMessage.value = '載入地段資料失敗';
        showSnackbar.value = true;
      } finally {
        loadingSections.value = false;
      }
    }
  } catch (error) {
    console.error('Failed to load towns:', error);
    snackbarMessage.value = '載入鄉鎮資料失敗';
    showSnackbar.value = true;
  }
};

// 特殊城市配置
const specialCities: Record<string, { code: string; name: string }> = {
  '新竹市': { code: 'O01', name: '新竹市' },
  '嘉義市': { code: 'I01', name: '嘉義市' }
};

// 取得特殊城市的顯示文字
const getSpecialCityDisplayText = (): string => {
  if (!landNumberInput.value.county) return '';
  const cityInfo = specialCities[landNumberInput.value.county];
  return cityInfo ? `${cityInfo.name}` : '';
};


// 取得適用於 NLSC API 的地政代碼
const getLandCodeForNlsc = (countyName: string, townLandCode: string | null | undefined): string | null => {
  // 如果是特殊城市，統一使用固定的地政代碼
  if (specialCities[countyName]) {
    return specialCities[countyName].code;
  }
  // 其他縣市使用原始的 land_code
  return townLandCode || null;
};

// 鄉鎮變更處理
const onTownChange = async (newTown: string) => {
  // 重置地段
  landNumberInput.value.section = null;
  nlscSections.value = [];

  // 強制重新渲染地段選單
  sectionSelectKey.value++;

  // 使用 nextTick 確保重置生效
  await nextTick();

  if (!newTown) {
    return;
  }

  // 載入該鄉鎮的地段資料 - 使用 NLSC API
  const county = domicileStore.countyOptions.find(c => c.title === landNumberInput.value.county);
  if (county && county.land_code) {
    const town = domicileStore.getTownsForCountyId(county.value).find(t => t.title === newTown);
    if (town) {
      // 獲取適用於 NLSC API 的地政代碼
      const nlscLandCode = getLandCodeForNlsc(landNumberInput.value.county, town.land_code);

      if (nlscLandCode) {
        loadingSections.value = true;
        try {
          await domicileStore.loadLandSectionsByLandCodes(county.land_code, nlscLandCode);
          nlscSections.value = domicileStore.landSections.filter(s =>
            s.county_land_code === county.land_code && s.town_land_code === nlscLandCode
          );
          console.log(`載入 ${landNumberInput.value.county} ${newTown} 的地段資料 (${nlscLandCode}):`, nlscSections.value.length);
        } catch (error) {
          console.error('Failed to load land sections:', error);
          nlscSections.value = [];
          snackbarMessage.value = '載入地段資料失敗';
          showSnackbar.value = true;
        } finally {
          loadingSections.value = false;
        }
      } else {
        console.warn('No valid land_code found for', landNumberInput.value.county, newTown);
      }
    }
  }
};

// 🗺️ 地號定位功能 - 使用 NLSC CadasMapQuery API
// API: https://api.nlsc.gov.tw/dmaps/CadasMapQuery/[縣市]/[地段]/[地號]/[格式]/[坐標系統]
const locateByLandNumber = async () => {
  if (!map) return;

  const { section, motherNumber, childNumber } = landNumberInput.value;

  // 驗證必要欄位
  if (!section) {
    snackbarMessage.value = '請選擇地段';
    showSnackbar.value = true;
    return;
  }

  if (!motherNumber) {
    snackbarMessage.value = '請輸入母地號';
    showSnackbar.value = true;
    return;
  }

  // 驗證地號格式
  const validation = validateLandNumber(motherNumber, childNumber || '');
  if (!validation.valid) {
    snackbarMessage.value = `地號格式錯誤: ${validation.message}`;
    showSnackbar.value = true;
    return;
  }

  isLocationLoading.value = true;

  try {
    // 取得當前選中的地段資料
    const currentSectionCode = section.toString();
    const selectedSection = sectionOptions.value.find(s =>
      s.code === currentSectionCode ||
      s.value === currentSectionCode
    );

    if (!selectedSection) {
      snackbarMessage.value = '無法找到選中的地段資料';
      showSnackbar.value = true;
      isLocationLoading.value = false;
      return;
    }

    // 建立查詢參數
    const queryParams: CadastralQueryParams = {
      countyCode: selectedSection.county_land_code || '',  // 縣市地政代碼
      sectionCode: selectedSection.code || '',             // 地段代碼
      landNumberMain: motherNumber,                        // 主號
      landNumberSub: childNumber || '0',                   // 副號（預設0）
      format: 'gml',                                       // 使用 GML 格式
      srid: '4326'                                         // 使用 WGS84 坐標系統
    };

    console.log('🔍 查詢地籍圖參數:', queryParams);

    // 呼叫 NLSC API
    const result = await queryCadastralMap(queryParams);

    if (!result.success || result.features.length === 0) {
      snackbarMessage.value = '查無此地號的地籍資料';
      showSnackbar.value = true;
      isLocationLoading.value = false;
      return;
    }

    // 清空舊的地籍查詢結果
    if (cadastralResultSource.value) {
      cadastralResultSource.value.clear();
    }

    // 為地籍 features 設置標識，避免與案件 features 混淆
    result.features.forEach(feature => {
      feature.set('cadastral', true);
    });

    // 將所有 features 加入到地籍結果圖層
    if (cadastralResultSource.value) {
      cadastralResultSource.value.addFeatures(result.features);
      console.log(`✅ 已加入 ${result.features.length} 筆地籍 feature 到圖層`);
    }

    // 計算幾何重心作為標記位置
    // ⚠️ 注意：geometry 已經是 EPSG:3857 坐標系統（由 cadastralMapService 轉換）
    let center: number[];

    if (result.features.length === 1) {
      // 單一 feature：使用其幾何重心
      const geometry = result.features[0].getGeometry();
      if (geometry && typeof (geometry as any).getInteriorPoint === 'function') {
        const interiorPoint = (geometry as any).getInteriorPoint();
        center = interiorPoint.getCoordinates();
      } else {
        // Fallback: 使用 extent 中心
        const extent = cadastralResultSource.value.getExtent();
        center = [(extent[0] + extent[2]) / 2, (extent[1] + extent[3]) / 2];
      }
    } else {
      // 多筆 features：找出面積最大的 feature，使用其重心
      const largestFeature = result.features.reduce((largest, current) => {
        const largestGeometry = largest.getGeometry();
        const currentGeometry = current.getGeometry();

        if (!largestGeometry) return current;
        if (!currentGeometry) return largest;

        const largestArea = typeof (largestGeometry as any).getArea === 'function'
          ? (largestGeometry as any).getArea()
          : 0;
        const currentArea = typeof (currentGeometry as any).getArea === 'function'
          ? (currentGeometry as any).getArea()
          : 0;

        return currentArea > largestArea ? current : largest;
      });

      const geometry = largestFeature.getGeometry();
      if (geometry && typeof (geometry as any).getInteriorPoint === 'function') {
        const interiorPoint = (geometry as any).getInteriorPoint();
        center = interiorPoint.getCoordinates();
      } else {
        // Fallback: 使用 extent 中心
        const extent = cadastralResultSource.value.getExtent();
        center = [(extent[0] + extent[2]) / 2, (extent[1] + extent[3]) / 2];
      }
    }

    // 構建完整地號
    const fullLandNumber = childNumber
      ? `${motherNumber}-${childNumber}`
      : motherNumber;

    // 取得地段名稱
    const sectionName = selectedSection.displayName || selectedSection.name || selectedSection.code;

    // 添加標記
    const label = `地號: ${sectionName} ${fullLandNumber}`;
    addLocationMarker(center, label);

    // 定位到該地號並縮放
    map.getView().animate({
      center: center,
      zoom: 18,
      duration: 500
    });

    snackbarMessage.value = `已定位到 ${sectionName} ${fullLandNumber}（${result.features.length} 筆圖徵）`;
    showSnackbar.value = true;
    isLocationLoading.value = false;

    console.log('✅ 地號定位成功:', {
      section: sectionName,
      landNumber: fullLandNumber,
      featureCount: result.features.length,
      centerType: result.features.length === 1 ? 'single_centroid' : 'largest_centroid',
      center_3857: center
    });

  } catch (error) {
    console.error('❌ 地號定位失敗:', error);
    snackbarMessage.value = '地號定位失敗，請檢查網路連線或稍後再試';
    showSnackbar.value = true;
    isLocationLoading.value = false;
  }
};

// 展繪功能
const toggleDraw = () => {
  isDrawing.value = !isDrawing.value;
  showDrawPanel.value = isDrawing.value;

  if (isMeasuring.value) {
    isMeasuring.value = false;
    showMeasurePanel.value = false;
  }

  // 重置面板位置到 map-controls 左側
  if (isDrawing.value) {
    drawPanelPosition.value = getInitialToolPanelPosition();
  }

  console.log('展繪工具:', isDrawing.value ? '啟用' : '停用');
  snackbarMessage.value = isDrawing.value ? '展繪工具已啟用' : '展繪工具已停用';
  showSnackbar.value = true;
};

// === 量測工具功能函數 ===

// 格式化距離輸出
const formatLength = (line: LineString): string => {
  const length = getLength(line);
  if (length > 100) {
    return `${Math.round((length / 1000) * 100) / 100} 公里`;
  }
  return `${Math.round(length * 100) / 100} 公尺`;
};

// 格式化面積輸出
const formatArea = (polygon: Polygon): string => {
  const area = getArea(polygon);
  if (area > 10000) {
    return `${Math.round((area / 10000) * 100) / 100} 公頃`;
  }
  return `${Math.round(area * 100) / 100} 平方公尺`;
};

// 創建幫助提示 tooltip
const createHelpTooltip = () => {
  if (!map) return;

  if (helpTooltipElement.value) {
    helpTooltipElement.value.parentNode?.removeChild(helpTooltipElement.value);
  }
  helpTooltipElement.value = document.createElement('div');
  helpTooltipElement.value.className = 'ol-tooltip hidden';
  helpTooltip.value = new Overlay({
    element: helpTooltipElement.value,
    offset: [15, 0],
    positioning: 'center-left',
  });
  map.addOverlay(helpTooltip.value);
};

// 創建量測 tooltip
const createMeasureTooltip = () => {
  if (!map) return;

  if (measureTooltipElement.value) {
    measureTooltipElement.value.parentNode?.removeChild(measureTooltipElement.value);
  }
  measureTooltipElement.value = document.createElement('div');
  measureTooltipElement.value.className = 'ol-tooltip ol-tooltip-measure';
  measureTooltip.value = new Overlay({
    element: measureTooltipElement.value,
    offset: [0, -15],
    positioning: 'bottom-center',
    stopEvent: false,
    insertFirst: false,
  });
  map.addOverlay(measureTooltip.value);
};

// 鼠標移動處理
const pointerMoveHandler = (evt: any) => {
  if (evt.dragging) {
    return;
  }

  let helpMsg = '點擊開始測量';

  if (measureSketch.value) {
    const geom = measureSketch.value.getGeometry();
    if (geom instanceof Polygon) {
      helpMsg = '點擊繼續繪製多邊形，或回到起點結束測量';
    } else if (geom instanceof LineString) {
      helpMsg = '點擊繼續繪製線段，或點擊兩下結束測量';
    }
  }

  if (helpTooltipElement.value) {
    helpTooltipElement.value.innerHTML = helpMsg;
    helpTooltip.value?.setPosition(evt.coordinate);
    helpTooltipElement.value.classList.remove('hidden');
  }
};

// 切換測量類型（開啟或關閉）
const toggleMeasurementType = (type: 'distance' | 'area') => {
  // 如果點擊的是當前正在進行的測量，則停止測量
  if (measureType.value === type) {
    stopMeasurement();
  } else {
    // 否則切換到新的測量類型
    startMeasurement(type);
  }
};

// 停止當前測量
const stopMeasurement = () => {
  if (measureDraw.value && map) {
    // 重新啟用被禁用的 interactions
    const disabledList = (measureDraw.value as any)?._disabledInteractions || [];
    disabledList.forEach((item: { interaction: any; name: string }) => {
      item.interaction.setActive(true);
    });

    map.removeInteraction(measureDraw.value);
    map.un('pointermove', pointerMoveHandler);
    measureDraw.value = null;
  }

  // 停止測量時只移除動態 tooltip（保留靜態的測量結果標籤）
  if (map) {
    const overlays = map.getOverlays().getArray().slice();
    overlays.forEach((overlay) => {
      const element = overlay.getElement();
      // 只移除動態 tooltip（ol-tooltip-measure 但不是 ol-tooltip-static）和 help tooltip
      if (element && element.className.includes('ol-tooltip') &&
          !element.className.includes('ol-tooltip-static')) {
        map.removeOverlay(overlay);
      }
    });
  }

  // 重置動態 tooltip 引用（但保留已完成的測量結果在地圖上）
  measureTooltipElement.value = null;
  measureTooltip.value = null;
  helpTooltipElement.value = null;
  helpTooltip.value = null;
  measureSketch.value = null;
  if (measureListener.value) {
    unByKey(measureListener.value);
    measureListener.value = null;
  }

  measureType.value = null;

  snackbarMessage.value = '已停止測量';
  showSnackbar.value = true;
};

// 開始量測（距離或面積）
const startMeasurement = (type: 'distance' | 'area') => {
  if (!map || !measureSource.value) {
    console.error('地圖或量測圖層尚未初始化');
    return;
  }

  // 移除舊的 Draw interaction
  if (measureDraw.value) {
    map.removeInteraction(measureDraw.value);
    map.un('pointermove', pointerMoveHandler);
  }

  measureType.value = type;
  const drawType = type === 'distance' ? 'LineString' : 'Polygon';

  // 創建 tooltips
  createMeasureTooltip();
  createHelpTooltip();

  // 添加 pointermove 監聽
  map.on('pointermove', pointerMoveHandler);

  // mouseout 時隱藏 help tooltip
  map.getViewport().addEventListener('mouseout', () => {
    if (helpTooltipElement.value) {
      helpTooltipElement.value.classList.add('hidden');
    }
  });

  // 創建 Draw interaction
  measureDraw.value = new Draw({
    source: measureSource.value,
    type: drawType,
  });

  // drawstart 事件
  measureDraw.value.on('drawstart', (evt: any) => {
    measureSketch.value = evt.feature;

    let tooltipCoord = evt.coordinate;

    measureListener.value = measureSketch.value.getGeometry().on('change', (event: any) => {
      const geom = event.target;
      let output: string;

      if (geom instanceof Polygon) {
        output = formatArea(geom);
        tooltipCoord = geom.getInteriorPoint().getCoordinates();
        measureResults.value.area = output;
      } else if (geom instanceof LineString) {
        output = formatLength(geom);
        tooltipCoord = geom.getLastCoordinate();
        measureResults.value.distance = output;
      }

      if (measureTooltipElement.value) {
        measureTooltipElement.value.innerHTML = output!;
        measureTooltip.value?.setPosition(tooltipCoord);
      }
    });
  });

  // drawend 事件
  measureDraw.value.on('drawend', () => {
    if (measureTooltipElement.value) {
      measureTooltipElement.value.className = 'ol-tooltip ol-tooltip-static';
    }
    measureTooltip.value?.setOffset([0, -7]);
    measureSketch.value = null;
    measureTooltipElement.value = null;
    createMeasureTooltip();
    unByKey(measureListener.value);
  });

  map.addInteraction(measureDraw.value);

  // 禁用其他 interactions 以避免衝突（保持 Draw 激活）
  // 修復: 使用 instanceof 而不是 constructor.name（避免 minification 問題）
  const disabledInteractions: Array<{ interaction: any; name: string }> = [];
  map.getInteractions().forEach((interaction) => {
    const name = interaction.constructor.name;
    // 只禁用非 Draw interactions
    if (!(interaction instanceof Draw)) {
      interaction.setActive(false);
      disabledInteractions.push({ interaction, name });
    }
  });

  // 保存禁用列表以便後續恢復
  (measureDraw.value as any)._disabledInteractions = disabledInteractions;

  // 提示用戶
  const typeText = type === 'distance' ? '距離' : '面積';
  snackbarMessage.value = `${typeText}量測已啟動，點擊地圖開始繪製`;
  showSnackbar.value = true;
};

// 清除所有量測結果（只清除繪製的圖形和結果數字，保留 tooltip）
const clearMeasurements = () => {
  // 清除繪製的圖形
  if (measureSource.value) {
    measureSource.value.clear();
  }

  // 只移除靜態的測量結果 tooltip（ol-tooltip-static），保留動態的測量 tooltip
  if (map) {
    const overlays = map.getOverlays().getArray().slice();
    overlays.forEach((overlay) => {
      const element = overlay.getElement();
      // 只移除靜態 tooltip（已完成測量的標籤）
      if (element?.className.includes('ol-tooltip-static')) {
        map.removeOverlay(overlay);
      }
    });
  }

  // 清除當前正在繪製的 sketch（如果有）
  if (measureSketch.value) {
    measureSketch.value = null;
  }
  if (measureListener.value) {
    unByKey(measureListener.value);
    measureListener.value = null;
  }

  // 重置量測結果數字
  measureResults.value = { distance: '--', area: '--' };

  snackbarMessage.value = '已清除所有量測結果';
  showSnackbar.value = true;
};

// 切換量測工具開關
const toggleMeasure = () => {
  isMeasuring.value = !isMeasuring.value;
  showMeasurePanel.value = isMeasuring.value;

  if (isDrawing.value) {
    isDrawing.value = false;
    showDrawPanel.value = false;
  }

  // 重置面板位置到 map-controls 左側
  if (isMeasuring.value) {
    measurePanelPosition.value = getInitialToolPanelPosition();
  } else {
    // 停用時清除量測
    if (measureDraw.value && map) {
      // 重新啟用被禁用的 interactions
      const disabledList = (measureDraw.value as any)?._disabledInteractions || [];
      disabledList.forEach((item: { interaction: any; name: string }) => {
        item.interaction.setActive(true);
      });

      map.removeInteraction(measureDraw.value);
      map.un('pointermove', pointerMoveHandler);
      measureDraw.value = null;
    }
    measureType.value = null;
    clearMeasurements();
  }

  snackbarMessage.value = isMeasuring.value ? '量測工具已啟用，請點擊「測量距離」或「測量面積」開始' : '量測工具已停用';
  showSnackbar.value = true;
};

// 切換定位工具開關
const toggleLocation = () => {
  isLocating.value = !isLocating.value;
  showLocationPanel.value = isLocating.value;

  // 如果開啟定位工具，關閉其他工具面板
  if (isLocating.value) {
    if (isDrawing.value) {
      isDrawing.value = false;
      showDrawPanel.value = false;
    }
    if (isMeasuring.value) {
      isMeasuring.value = false;
      showMeasurePanel.value = false;
      if (measureDraw.value && map) {
        const disabledList = (measureDraw.value as any)?._disabledInteractions || [];
        disabledList.forEach((item: { interaction: any; name: string }) => {
          item.interaction.setActive(true);
        });
        map.removeInteraction(measureDraw.value);
        map.un('pointermove', pointerMoveHandler);
        measureDraw.value = null;
      }
      measureType.value = null;
    }

    // 重置面板位置到 map-controls 左側
    locationPanelPosition.value = getInitialToolPanelPosition(0, 400);
  }

  snackbarMessage.value = isLocating.value ? '定位工具已啟用' : '定位工具已停用';
  showSnackbar.value = true;
};

// === GIS 補助案件相關功能 ===

// 年度範圍變更處理（觸發 OpenLayers 重新載入）
const onYearRangeChange = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(async () => {
    try {
      await gisStore.updateYearRange(yearRange.value.current)
      refreshLayerData() // 改為觸發 OpenLayers 重新載入
    } catch (error) {
      console.error('年度範圍變更失敗:', error)
      showError('年度範圍變更失敗')
    }
  }, 300)
}

// 顯示模式變更處理（觸發圖層可見性切換）
watch(displayMode, async (newMode) => {
  try {
    await gisStore.updateDisplayMode(newMode);
    updateLayerVisibility();
    refreshLayerData(); // 改為觸發 OpenLayers 重新載入
  } catch (error) {
    console.error('顯示模式變更失敗:', error);
    showError('顯示模式變更失敗');
  }
});

// 更新圖層可見性（使用 ID 查找）
const updateLayerVisibility = () => {
  const gridLayer = mapLayers.value.find(l => l.id === 'grant-grid')
  const pointsLayer = mapLayers.value.find(l => l.id === 'grant-points')

  if (grantPointsLayer.value && grantGridLayer.value && gridLayer && pointsLayer) {
    if (displayMode.value === 'grid') {
      grantGridLayer.value.setVisible(gridLayer.visible);
      grantPointsLayer.value.setVisible(false);
      pointsLayer.visible = false;

      // 確保格網圖層有資料
      const gridSource = grantGridLayer.value.getSource();
      if (gridSource && gridSource.getFeatures().length === 0) {
        console.log('[格網圖層] 切換到格網模式，觸發資料載入');
        // 觸發載入
        gridSource.refresh();
      }
    } else {
      grantGridLayer.value.setVisible(false);
      grantPointsLayer.value.setVisible(pointsLayer.visible);
      gridLayer.visible = false;
    }
  }
};

// 顯示錯誤訊息
const showError = (message: string) => {
  snackbarMessage.value = message;
  showSnackbar.value = true;
};

// === FilterToolbar 組件事件處理 ===
// 注意：篩選邏輯現在由 FilterToolbar 組件處理

// 前端篩選處理函數
const applyFrontendFilter = () => {
  console.log('執行前端篩選, quickFilter:', quickFilter.value);
  console.log('目前已載入的特徵數量:', allLoadedFeatures.value.length);

  if (allLoadedFeatures.value.length === 0) {
    console.log('沒有已載入的資料，執行初始載入');
    // 如果沒有資料，執行初始載入
    refreshLayerData();
    return;
  }

  // 準備篩選條件
  const detailedFilters: Partial<FilterCriteria> = {
    applicantName: filterCriteria.value.applicantName,
    landSection: filterCriteria.value.landSection,
    landNumber: filterCriteria.value.landNumber,
    caseNumber: filterCriteria.value.caseNumber,
    sourceSystem: filterCriteria.value.sourceSystem,
    yearStart: filterCriteria.value.yearStart,
    yearEnd: filterCriteria.value.yearEnd
  };

  // 執行前端篩選
  filteredFeatures.value = applyFrontendFilters(
    allLoadedFeatures.value,
    quickFilter.value,
    detailedFilters
  );

  console.log(`篩選結果: ${filteredFeatures.value.length}/${allLoadedFeatures.value.length} 個特徵`);

  // 更新圖層顯示
  updateLayersWithFilteredData();

  // 顯示篩選結果提示
  if (quickFilter.value) {
    const message = `快速篩選「${quickFilter.value}」找到 ${filteredFeatures.value.length} 筆結果`;
    snackbarMessage.value = message;
    showSnackbar.value = true;
  }
};

// 套用篩選（混合模式：詳細篩選仍使用後端API，快速篩選使用前端）
const applyFilters = async () => {
  try {
    console.log('套用篩選條件:', filterCriteria.value);
    console.log('快速篩選條件:', quickFilter.value);

    // 檢查是否有詳細篩選條件
    const hasDetailedFilters = !!(
      filterCriteria.value.applicantName ||
      filterCriteria.value.landSection ||
      filterCriteria.value.landNumber ||
      filterCriteria.value.caseNumber ||
      filterCriteria.value.sourceSystem ||
      filterCriteria.value.yearStart !== getCurrentYear() ||
      filterCriteria.value.yearEnd !== getCurrentYear()
    );

    if (hasDetailedFilters) {
      // 有詳細篩選條件時，使用後端API重新載入
      console.log('檢測到詳細篩選條件，使用後端API重新載入');

      // 準備搜尋條件
      const combinedCriteria = { ...filterCriteria.value };

      // 同步到原有的搜尋條件（用於後端API）
      searchCriteria.value.applicantName = combinedCriteria.applicantName;
      searchCriteria.value.landSection = combinedCriteria.landSection;
      searchCriteria.value.caseNumber = combinedCriteria.caseNumber;
      searchCriteria.value.sourceSystem = combinedCriteria.sourceSystem;

      // 更新年度範圍到 GIS Store
      const yearRangeArray: [number, number] = [filterCriteria.value.yearStart, filterCriteria.value.yearEnd];
      yearRange.value.current = yearRangeArray;
      await gisStore.updateYearRange(yearRangeArray);

      // 清空已載入的資料，強制重新載入
      allLoadedFeatures.value = [];
      filteredFeatures.value = [];

      // 觸發圖層資料重新載入
      refreshLayerData();

      snackbarMessage.value = '篩選條件已套用，重新載入資料';
      showSnackbar.value = true;
    } else {
      // 僅有快速篩選時，使用前端篩選
      console.log('僅有快速篩選，使用前端篩選');
      applyFrontendFilter();
    }
  } catch (error) {
    console.error('套用篩選失敗:', error);
    showError('套用篩選失敗');
  }
};

// 重置篩選條件
const resetFilters = () => {
  // 獲取統一的初始載入條件參數
  const initialParams = getInitialOverlayLoadingParams()

  // 重置所有篩選條件到初始載入條件
  quickFilter.value = '';
  filterCriteria.value = {
    applicantName: '',
    landSection: '',
    landNumber: '',
    caseNumber: '',
    sourceSystem: initialParams.source_system || null,
    yearStart: initialParams.apply_year_min!,
    yearEnd: initialParams.apply_year_max!
  };

  // 同步年度範圍到 GIS Store
  const yearRangeArray: [number, number] = [initialParams.apply_year_min!, initialParams.apply_year_max!]
  yearRange.value.current = yearRangeArray

  // 同步到原有的搜尋條件
  searchCriteria.value = {
    applicantName: '',
    landSection: '',
    caseNumber: '',
    sourceSystem: initialParams.source_system || null,
    quickFilter: '',
    quickFilterTargets: []
  };

  // 套用重置後的篩選
  applyFilters();

  // 清空已載入的資料，強制重新載入
  allLoadedFeatures.value = [];
  filteredFeatures.value = [];

  snackbarMessage.value = `篩選條件已重置到初始條件（民國${initialParams.apply_year_min}年）`;
  showSnackbar.value = true;
};

// 使用篩選後的資料更新圖層顯示
const updateLayersWithFilteredData = () => {
  console.log('使用篩選後的資料更新圖層顯示');

  if (!grantPointsLayer.value) {
    console.warn('圖層尚未初始化');
    return;
  }

  // 將篩選後的特徵轉換為 GeoJSON 格式
  const filteredGeoJson: GeoJsonFeatureCollection = {
    type: 'FeatureCollection',
    features: filteredFeatures.value,
    meta: {
      count: filteredFeatures.value.length,
      clustering: {
        enabled: false,
        strategy: 'individual_points'
      },
      filters: {
        no_clustering: true
      },
      performance: {
        limit_applied: filteredFeatures.value.length,
        optimization: 'limit_only'
      }
    }
  };

  console.log(`更新圖層顯示，篩選後特徵數量: ${filteredFeatures.value.length}`);

  // 根據顯示模式更新對應的圖層
  if (displayMode.value === 'grid') {
    // 更新格網統計圖層
    updateGridLayer(filteredFeatures.value);
  } else {
    // 更新點位圖層
    const pointSource = grantPointsLayer.value.getSource() as VectorSource;
    if (pointSource) {
      pointSource.clear();

      try {
        const geoJSONFormat = new GeoJSON();
        const features = geoJSONFormat.readFeatures(filteredGeoJson, {
          featureProjection: 'EPSG:3857'
        });

        pointSource.addFeatures(features);
        console.log(`點位圖層已更新，載入 ${features.length} 個點位`);
      } catch (error) {
        console.error('GeoJSON 解析失敗:', error);
        // 降級處理
        const features = filteredFeatures.value.map((featureData: GeoJsonFeature) => {
          if (featureData.geometry?.type === 'Point') {
            const coords = featureData.geometry.coordinates as [number, number];
            const point = new Point(fromLonLat(coords));
            return new Feature({
              geometry: point,
              ...featureData.properties
            });
          }
          return null;
        }).filter((f): f is Feature<Point> => f !== null);

        pointSource.addFeatures(features);
        console.log(`點位圖層已更新（手動方式），載入 ${features.length} 個點位`);
      }
    }
  }

  // 強制重新渲染地圖
  if (map) {
    map.render();
  }
};


// 搜尋時更新圖層可見性（使用 ID 查找）
// eslint-disable-next-line @typescript-eslint/no-unused-vars
const updateLayerVisibilityForSearch = () => {
  console.log('更新搜尋時的圖層可見性');

  const gridLayer = mapLayers.value.find(l => l.id === 'grant-grid')
  const pointsLayer = mapLayers.value.find(l => l.id === 'grant-points')

  // 隱藏格網圖層，顯示點位圖層
  if (grantPointsLayer.value && gridLayer && pointsLayer) {
    if (grantGridLayer.value) {
      grantGridLayer.value.setVisible(false);
    }
    grantPointsLayer.value.setVisible(true);

    // 更新圖層管理面板的狀態
    gridLayer.visible = false; // 格網圖層
    pointsLayer.visible = true;  // 點位圖層

    console.log('圖層可見性已更新：格網圖層隱藏，點位圖層顯示');
  }
};

// 載入 GeoJSON 到補助案件圖層（簡化版）
// eslint-disable-next-line @typescript-eslint/no-unused-vars
const loadGeoJsonToGrantLayer = (geoJsonData: GeoJsonFeatureCollection) => {
  if (!grantPointsLayer.value) return

  const vectorSource = grantPointsLayer.value.getSource()
  if (!vectorSource) return

  // 清除現有資料並設為可見
  vectorSource.clear()
  grantPointsLayer.value.setVisible(true)

  try {
    const geoJSONFormat = new GeoJSON()
    const features = geoJSONFormat.readFeatures(geoJsonData, {
      featureProjection: 'EPSG:3857'
    })

    if (features.length > 0) {
      vectorSource.addFeatures(features)
      map?.render()
    }
  } catch (error) {
    console.error('解析 GeoJSON 失敗:', error)
    // 降級處理：手動創建特徵
    try {
      const features = geoJsonData.features?.map((featureData: GeoJsonFeature) => {
        if (featureData.geometry?.type === 'Point') {
          const coords = featureData.geometry.coordinates as [number, number]
          const point = new Point(fromLonLat(coords))
          return new Feature({
            geometry: point,
            ...featureData.properties
          })
        }
        return null;
      }).filter(Boolean) || [];

      if (features.length > 0) {
        vectorSource.addFeatures(features)
        map?.render()
      }
    } catch (manualError) {
      console.error('手動創建特徵失敗:', manualError)
    }
  }
}

// 載入 GeoJSON 到格網統計圖層（簡化版）
// eslint-disable-next-line @typescript-eslint/no-unused-vars
const loadGeoJsonToGridLayer = (geoJsonData: GeoJsonFeatureCollection) => {
  if (!grantGridLayer.value) return

  updateGridLayer(geoJsonData.features || []);
  console.log(`載入了格網統計圖資料，包含 ${geoJsonData.features?.length || 0} 個點位`)
}

// 更新格網統計圖層
const updateGridLayer = (features: GeoJsonFeature[]) => {
  console.log(`[updateGridLayer] 開始處理 ${features.length} 個特徵`);

  if (!grantGridLayer.value || !map) {
    console.log('[updateGridLayer] 缺少格網圖層或地圖實例');
    return;
  }

  const gridSource = grantGridLayer.value.getSource();
  if (!gridSource) {
    console.log('[updateGridLayer] 格網圖層沒有資料源');
    return;
  }

  // 清除現有格網
  gridSource.clear();

  if (features.length === 0) {
    console.log('[updateGridLayer] 沒有資料，清空格網');
    return;
  }

  // 取得當前地圖的範圍
  const extent = map.getView().calculateExtent(map.getSize());
  console.log('[updateGridLayer] 當前地圖範圍:', extent);

  // 計算格網大小（可以根據縮放等級調整）
  const zoom = map.getView().getZoom() || 7;
  let gridSize: number;

  if (zoom < 8) {
    gridSize = 20000; // 大格網
  } else if (zoom < 12) {
    gridSize = 10000; // 中等格網
  } else {
    gridSize = 5000;  // 小格網
  }

  console.log(`[updateGridLayer] 使用格網大小: ${gridSize}, 縮放等級: ${zoom}`);

  // 建立格網統計 - 使用普通對象避免響應式代理問題
  const gridStats: Record<string, { count: number; bounds: number[] }> = {};

  // 統計每個格網內的點位數量 - 使用 toRaw 避免響應式代理問題
  let validPointCount = 0;
  const rawFeatures = toRaw(features);
  for (let i = 0; i < rawFeatures.length; i++) {
    const feature = rawFeatures[i];
    if (feature.geometry?.type === 'Point') {
      validPointCount++;
      const coords = feature.geometry.coordinates as [number, number];
      const projectedCoords = fromLonLat(coords);

      // 計算格網索引
      const gridX = Math.floor(projectedCoords[0] / gridSize) * gridSize;
      const gridY = Math.floor(projectedCoords[1] / gridSize) * gridSize;
      const gridKey = `${gridX},${gridY}`;

      if (!gridStats[gridKey]) {
        gridStats[gridKey] = {
          count: 0,
          bounds: [gridX, gridY, gridX + gridSize, gridY + gridSize]
        };
      }

      gridStats[gridKey].count++;
    }
  }

  console.log(`[updateGridLayer] 處理了 ${validPointCount} 個有效點位，建立了 ${Object.keys(gridStats).length} 個格網`);

  // 建立格網特徵
  const gridFeatures: Feature[] = [];
  const allCounts = Object.values(gridStats).map(s => s.count);
  const maxCount = Math.max(...allCounts);
  console.log(`[updateGridLayer] 格網最大案件數: ${maxCount}`);

  Object.entries(gridStats).forEach(([gridKey, stat]) => {
    if (stat.count > 0) {
      // 建立格網矩形
      const [minX, minY, maxX, maxY] = stat.bounds;
      const polygon = new Polygon([[
        [minX, minY],
        [maxX, minY],
        [maxX, maxY],
        [minX, maxY],
        [minX, minY]
      ]]);

      // 計算顏色強度（0-1）
      const intensity = stat.count / maxCount;
      const opacity = Math.max(0.2, intensity * 0.8);

      // 根據數量設定顏色
      let fillColor: string;
      if (stat.count >= maxCount * 0.8) {
        fillColor = `rgba(255, 0, 0, ${opacity})`; // 紅色
      } else if (stat.count >= maxCount * 0.6) {
        fillColor = `rgba(255, 165, 0, ${opacity})`; // 橙色
      } else if (stat.count >= maxCount * 0.4) {
        fillColor = `rgba(255, 255, 0, ${opacity})`; // 黃色
      } else if (stat.count >= maxCount * 0.2) {
        fillColor = `rgba(173, 255, 47, ${opacity})`; // 黃綠色
      } else {
        fillColor = `rgba(0, 255, 0, ${opacity})`; // 綠色
      }

      const gridFeature = new Feature({
        geometry: polygon,
        count: stat.count,
        gridKey: gridKey,
        maxCount: maxCount
      });

      // 設定格網樣式
      gridFeature.setStyle(new Style({
        fill: new Fill({
          color: fillColor
        }),
        stroke: new Stroke({
          color: 'rgba(255, 255, 255, 0.8)',
          width: 1
        }),
        text: new Text({
          text: stat.count.toString(),
          fill: new Fill({
            color: '#000000'
          }),
          stroke: new Stroke({
            color: '#ffffff',
            width: 2
          }),
          font: 'bold 14px Arial',
          textAlign: 'center',
          textBaseline: 'middle'
        })
      }));

      gridFeatures.push(gridFeature);
    }
  });

  // 將格網特徵加入圖層
  gridSource.addFeatures(gridFeatures);
  console.log(`[updateGridLayer] 建立了 ${gridFeatures.length} 個格網，總計 ${features.length} 個點位`);
  console.log(`[updateGridLayer] 格網圖層現在有 ${gridSource.getFeatures().length} 個特徵`);

  // 強制重新渲染
  map.render();
  console.log(`[updateGridLayer] 已觸發地圖重新渲染`);
};

// 顯示格網統計資訊彈出視窗
const showGridPopup = (coordinate: number[], properties: Record<string, unknown>) => {
  const count = Number(properties.count) || 0;
  const maxCount = Number(properties.maxCount) || 1;
  const percentage = Math.round((count / maxCount) * 100);

  const info = `📊 格網統計資訊
📍 此格網內案件數: ${count} 筆
📈 佔最大值比例: ${percentage}%
🏆 全區最大值: ${maxCount} 筆

💡 此格網包含了 ${count} 個補助申請案件`

  alert(info)
}

const formatCaseStatus = (status: unknown): string => {
  if (status === 'completed' || status === 'submitted') return '已結案'
  return '未結案'
}

// 顯示案件詳細資訊彈出視窗（簡化版）
const showGrantPopup = (coordinate: number[], properties: Record<string, unknown>) => {
  let info: string

  if (properties.cluster) {
    // 聚合點位資訊
    const systemType = properties.source_system === 'new_aerc' ? '新系統案件' : '歷史案件'
    info = `📍 聚合點位 (${systemType})
📊 包含案件數: ${properties.point_count}
📅 年度範圍: 民國${properties.year_range}年
🔍 縮放等級: ${properties.zoom_level}

💡 放大地圖可查看詳細的個別點位`
  } else {
    // 個別點位資訊
    const systemType = properties.source_system === 'new_aerc' ? '新系統案件' : '歷史案件'
    info = `📍 ${systemType}
📋 案件編號: ${properties.case_number || '未提供'}
👤 申請人: ${properties.applicant_name || '未提供'}
📍 地段: ${properties.land_section || '未提供'}
📍 地號: ${properties.land_number || '未提供'}
📅 申請年度: 民國${properties.apply_year}年
📊 案件狀態: ${formatCaseStatus(properties.case_status)}`
  }

  alert(info)
}

// 簡化的防抖搜尋（觸發 OpenLayers 重新載入）
let searchTimeout: ReturnType<typeof setTimeout>
const debouncedSearch = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    refreshLayerData() // 改為觸發 OpenLayers 重新載入
  }, 500)
}

// 搜尋案件函數（觸發 OpenLayers 重新載入）
const searchCases = () => {
  refreshLayerData()
}

const zoomIn = () => {
  if (!map) return;

  const view = map.getView();
  const currentZoom = view.getZoom();
  if (currentZoom !== undefined) {
    console.log('手動放大，從 zoom:', currentZoom, '到', currentZoom + 1);

    // 標記為程式化縮放
    isProgrammaticZoom.value = true;

    view.animate({
      zoom: currentZoom + 1,
      duration: 250
    });

    // 重置標記
    setTimeout(() => {
      isProgrammaticZoom.value = false;
      console.log('手動放大完成，重置標記');
    }, 300);
  }
};

const zoomOut = () => {
  if (!map) return;

  const view = map.getView();
  const currentZoom = view.getZoom();
  if (currentZoom !== undefined) {
    console.log('手動縮小，從 zoom:', currentZoom, '到', currentZoom - 1);

    // 標記為程式化縮放
    isProgrammaticZoom.value = true;

    view.animate({
      zoom: currentZoom - 1,
      duration: 250
    });

    // 重置標記
    setTimeout(() => {
      isProgrammaticZoom.value = false;
      console.log('手動縮小完成，重置標記');
    }, 300);
  }
};

const resetView = () => {
  if (!map) return;

  console.log('重置視圖到台灣中心點');

  // 標記為程式化縮放
  isProgrammaticZoom.value = true;

  map.getView().animate({
    center: fromLonLat([121.0, 23.5]), // 台灣中心點
    zoom: 7,
    duration: 500
  });

  // 重置標記
  setTimeout(() => {
    isProgrammaticZoom.value = false;
    console.log('重置視圖完成，重置標記');
  }, 600);
};

// 複製當前地圖連結
const copyMapLink = () => {
  if (!map) return;

  const view = map.getView();
  const center = view.getCenter();
  const zoom = view.getZoom();

  if (!center || zoom === undefined) return;

  // 將坐標從 EPSG:3857 轉換為經緯度 (EPSG:4326)
  const lonLat = toLonLat(center);

  // 構建新URL
  const url = new URL(window.location.href);
  url.searchParams.set('lon', lonLat[0].toFixed(6));
  url.searchParams.set('lat', lonLat[1].toFixed(6));
  url.searchParams.set('z', zoom.toFixed(2));

  // 複製到剪貼板
  navigator.clipboard.writeText(url.toString())
    .then(() => {
      snackbarMessage.value = '地圖連結已複製到剪貼板';
      showSnackbar.value = true;
    })
    .catch(err => {
      console.error('無法複製連結', err);
    });
};

// 監聽窗口大小變化
const handleResize = () => {
  if (map) {
    map.updateSize();
  }

  // 檢查面板位置是否需要調整（避免面板超出視窗）
  if (showLayersPanel.value) {
    const maxX = window.innerWidth - 300; // 面板寬度約300px
    const maxY = window.innerHeight - 400; // 面板高度約400px

    if (panelPosition.value.x > maxX || panelPosition.value.y > maxY) {
      panelPosition.value = {
        x: Math.max(0, Math.min(panelPosition.value.x, maxX)),
        y: Math.max(0, Math.min(panelPosition.value.y, maxY))
      };
    }
  }

  // 檢查工具面板位置是否需要調整
  const toolPanelWidth = 300;
  const toolPanelHeight = 250;
  const rightMargin = 20;

  // 調整展繪面板位置
  if (showDrawPanel.value) {
    const maxX = window.innerWidth - toolPanelWidth - rightMargin;
    const maxY = window.innerHeight - toolPanelHeight;

    if (drawPanelPosition.value.x > maxX || drawPanelPosition.value.y > maxY) {
      drawPanelPosition.value = {
        x: Math.max(rightMargin, Math.min(drawPanelPosition.value.x, maxX)),
        y: Math.max(10, Math.min(drawPanelPosition.value.y, maxY))
      };
    }
  }

  // 調整量測面板位置
  if (showMeasurePanel.value) {
    const maxX = window.innerWidth - toolPanelWidth - rightMargin;
    const maxY = window.innerHeight - toolPanelHeight;

    if (measurePanelPosition.value.x > maxX || measurePanelPosition.value.y > maxY) {
      measurePanelPosition.value = {
        x: Math.max(rightMargin, Math.min(measurePanelPosition.value.x, maxX)),
        y: Math.max(10, Math.min(measurePanelPosition.value.y, maxY))
      };
    }
  }

  // 調整定位面板位置
  if (showLocationPanel.value) {
    const locationPanelWidth = 400;
    const locationPanelHeight = 350;
    const maxX = window.innerWidth - locationPanelWidth - rightMargin;
    const maxY = window.innerHeight - locationPanelHeight;

    if (locationPanelPosition.value.x > maxX || locationPanelPosition.value.y > maxY) {
      locationPanelPosition.value = {
        x: Math.max(rightMargin, Math.min(locationPanelPosition.value.x, maxX)),
        y: Math.max(10, Math.min(locationPanelPosition.value.y, maxY))
      };
    }
  }
};

// 統一的視窗變化處理器（OpenLayers 自動載入模式）
const handleViewChange = () => {
  if (!mapInitialized.value || isProgrammaticZoom.value || isAutoZooming.value) {
    return
  }

  // 更新 URL
  updateUrlFromMap()

  // OpenLayers 會自動根據新的視窗範圍重新載入資料
  console.log('[HandleViewChange] 地圖視窗變化，OpenLayers 將自動重新載入資料')
}

// 更新 URL 從地圖狀態
const updateUrlFromMap = () => {
  if (!map || !mapInitialized.value) return

  const view = map.getView()
  const center = view.getCenter()
  const zoom = view.getZoom()

  if (!center || zoom === undefined) return

  // 將坐標從 EPSG:3857 轉換為經緯度 (EPSG:4326)
  const lonLat = toLonLat(center)

  // 使用 replaceState 而不是 history.pushState，以避免創建大量歷史記錄
  const query = {
    ...route.query,
    lon: lonLat[0].toFixed(6),
    lat: lonLat[1].toFixed(6),
    z: zoom.toFixed(2)
  }

  router.replace({ query })
}

// 輔助函數：安全地將 LocationQueryValue 轉換為字符串
const queryValueToString = (value: LocationQueryValue | LocationQueryValue[]): string | null => {
  if (typeof value === 'string') return value
  if (Array.isArray(value) && value.length > 0 && typeof value[0] === 'string') return value[0]
  return null
}

// 從URL讀取地圖參數
const readMapParamsFromUrl = () => {
  const lonStr = queryValueToString(route.query.lon);
  const latStr = queryValueToString(route.query.lat);
  const zStr = queryValueToString(route.query.z);

  if (lonStr && latStr && zStr) {
    return {
      center: fromLonLat([parseFloat(lonStr), parseFloat(latStr)]),
      zoom: parseFloat(zStr)
    };
  }

  return {
    center: fromLonLat([121.0, 23.5]), // 台灣中心點
    zoom: 7
  };
};

onMounted(async () => {
  // 從 localStorage 讀取 fluid 偏好設置
  const preferFluid = localStorage.getItem('preferFluid');
  if (preferFluid !== null) {
    isFluid.value = preferFluid === 'true';
  }

  // 獲取統一的疊加圖層初始載入條件參數
  const initialParams = getInitialOverlayLoadingParams()

  // 初始化篩選工具欄（使用統一的初始載入條件設置年度區間初值）
  filterCriteria.value.yearStart = initialParams.apply_year_min!
  filterCriteria.value.yearEnd = initialParams.apply_year_max!

  // 同步年度範圍到 GIS Store
  const yearRangeArray: [number, number] = [initialParams.apply_year_min!, initialParams.apply_year_max!]
  yearRange.value.current = yearRangeArray

  console.log(`[Init] 設置疊加圖層初始載入條件: 年度範圍 ${initialParams.apply_year_min}-${initialParams.apply_year_max}`)

  // 載入縣市資料（用於地號定位）
  try {
    await domicileStore.loadCounties();
    console.log('Counties loaded for location panel');
  } catch (error) {
    console.error('Failed to load counties:', error);
  }

  // 檢查 NLSC API 健康狀態
  try {
    const healthStatus = await checkNlscApiHealth();
    apiStatus.value.isOnline = healthStatus.nlsc_api_status === 'online';
    apiStatus.value.lastChecked = new Date();
    console.log('NLSC API health status:', healthStatus);
  } catch (error) {
    console.error('Failed to check NLSC API health:', error);
    apiStatus.value.isOnline = false;
    apiStatus.value.lastChecked = new Date();
  }

  // 確保面板位置在視窗尺寸確定後正確設置
  nextTick(() => {
    const rightOffset = 90;
    const topOffset = 10;
    panelPosition.value = {
      x: Math.max(10, window.innerWidth - 300 - rightOffset),
      y: topOffset
    };
  });

  // 延遲一點點初始化地圖，確保 DOM 準備好了
  setTimeout(async () => {
    await initMap();

    // 添加 resize 事件監聽器
    window.addEventListener('resize', handleResize);

    // 設置一個 MutationObserver 來監視容器大小變化
    const observer = new ResizeObserver(() => {
      if (map) {
        map.updateSize();
      }
    });

    if (mapContainer.value) {
      observer.observe(mapContainer.value);
    }

    console.log('[Init] 地圖初始化完成，疊加圖層將按設定條件載入');
  }, 100);
});

onUnmounted(() => {
  if (map) {
    // 移除地圖移動監聽
    map.un('moveend', updateUrlFromMap);
    map.setTarget(undefined);
    map = null;
  }

  // 移除事件監聽器
  window.removeEventListener('resize', handleResize);

  // 清理拖拽事件監聽器
  document.removeEventListener('mousemove', onDrag);
  document.removeEventListener('mouseup', stopDrag);
});

async function initMap() {
  try {
    // 確认元素存在
    if (!mapContainer.value) {
      console.error('找不到地圖容器元素');
      return;
    }

    // 從 URL 獲取初始地圖參數
    const mapParams = readMapParamsFromUrl();

    // 創建圖層並關聯到 mapLayers（使用 ID 查找）
    const nlscMapLayer = mapLayers.value.find(l => l.id === 'nlsc-map')!
    const nlscLayer = new TileLayer({
      source: new TileWMS({
        url: 'https://wms.nlsc.gov.tw/wms',
        params: {
          'LAYERS': 'EMAP5',
          'VERSION': '1.1.1',
          'FORMAT': 'image/png',
          'TRANSPARENT': true,
          'SRS': 'EPSG:3857'
        },
        serverType: 'geoserver',
      }),
      visible: nlscMapLayer.visible,
      opacity: nlscMapLayer.opacity
    });

    const osmMapLayer = mapLayers.value.find(l => l.id === 'osm-map')!
    const osmLayer = new TileLayer({
      source: new OSM(),
      visible: osmMapLayer.visible,
      opacity: osmMapLayer.opacity
    });

    const stamenMapLayer = mapLayers.value.find(l => l.id === 'stamen-watercolor')!
    const stamenLayer = new TileLayer({
      source: new StadiaMaps({
        layer: 'stamen_watercolor',
        retina: false,
        apiKey: 'fb83ebeb-aba3-4c37-ba97-3107a384e553',
      }),
      visible: stamenMapLayer.visible,
      opacity: stamenMapLayer.opacity
    });

    // 建立補助案件格網統計圖層 - 替代熱區圖
    const gridVectorSource = new VectorSource({
      loader: async (extent, resolution, projection) => {
        try {
          console.log('[GridLayer] OpenLayers 自動觸發資料載入')
          await loadRawDataForLayer('grid', extent, resolution, projection, gridVectorSource)
        } catch (error) {
          console.error('[GridLayer] 載入失敗:', error)
          showError('格網圖層載入失敗')
        }
      },
      strategy: (extent) => {
        // 使用當前視窗範圍作為載入策略，但擴展一些範圍以減少邊界載入
        const buffer = 0.1 // 10% 緩衝區
        const width = extent[2] - extent[0]
        const height = extent[3] - extent[1]
        return [[
          extent[0] - width * buffer,
          extent[1] - height * buffer,
          extent[2] + width * buffer,
          extent[3] + height * buffer
        ]]
      }
    });

    const grantGridMapLayer = mapLayers.value.find(l => l.id === 'grant-grid')!
    const gridLayer = new VectorLayer({
      source: gridVectorSource,
      visible: grantGridMapLayer.visible,
      opacity: grantGridMapLayer.opacity
    });

    // 註解掉原本的熱區圖層
    // const heatmapVectorSource = new VectorSource({
    //   format: new GeoJSON(),
    //   loader: async (extent, resolution, projection) => {
    //     try {
    //       console.log('[HeatmapLayer] OpenLayers 自動觸發資料載入')
    //       await loadRawDataForLayer('heatmap', extent, resolution, projection, heatmapVectorSource)
    //     } catch (error) {
    //       console.error('[HeatmapLayer] 載入失敗:', error)
    //       showError('熱區圖層載入失敗')
    //     }
    //   },
    //   strategy: (extent) => {
    //     const buffer = 0.1
    //     const width = extent[2] - extent[0]
    //     const height = extent[3] - extent[1]
    //     return [[
    //       extent[0] - width * buffer,
    //       extent[1] - height * buffer,
    //       extent[2] + width * buffer,
    //       extent[3] + height * buffer
    //     ]]
    //   }
    // });

    // const heatmapLayer = new HeatmapLayer({
    //   source: heatmapVectorSource,
    //   blur: 15,
    //   radius: 8,
    //   gradient: [
    //     '#00f', '#0ff', '#0f0', '#ff0', '#f00'
    //   ],
    //   visible: mapLayers.value[3].visible,
    //   opacity: mapLayers.value[3].opacity
    // });

    // 建立補助案件點位圖層 - 使用原始資料 + OpenLayers 聚合
    const baseVectorSource = new VectorSource({
      format: new GeoJSON(),
      loader: async (extent, resolution, projection) => {
        try {
          console.log('[GrantLayer] OpenLayers 自動觸發資料載入')
          await loadRawDataForLayer('points', extent, resolution, projection, baseVectorSource)
        } catch (error) {
          console.error('[GrantLayer] 載入失敗:', error)
          showError('點位圖層載入失敗')
        }
      },
      strategy: (extent) => {
        // 使用當前視窗範圍作為載入策略，但擴展一些範圍以減少邊界載入
        const buffer = 0.1 // 10% 緩衝區
        const width = extent[2] - extent[0]
        const height = extent[3] - extent[1]
        return [[
          extent[0] - width * buffer,
          extent[1] - height * buffer,
          extent[2] + width * buffer,
          extent[3] + height * buffer
        ]]
      }
    });

    const grantPointsMapLayer = mapLayers.value.find(l => l.id === 'grant-points')!
    const grantLayer = new VectorLayer({
      source: baseVectorSource,
      style: (feature) => {
        return createPointStyle(feature)
      },
      visible: grantPointsMapLayer.visible,
      opacity: grantPointsMapLayer.opacity
    });

    // 儲存圖層引用
    grantGridLayer.value = gridLayer;
    grantPointsLayer.value = grantLayer;

    // 建立國土功能分區圖 WMTS 圖層
    // 使用自定義的 TileMatrixSet 'functional_zoning_2'（從 GetCapabilities 取得）
    const projection = getProjection('EPSG:3857')!

    // 從 GetCapabilities 取得的 TileMatrix identifiers（用於 URL 請求）
    const matrixIds = [
      '2311166.8394888',
      '1155583.4197444',
      '577791.7098722',
      '288895.8549361',
      '144447.9274681',
      '72223.963734',
      '36111.981867',
      '18055.9909335',
      '9027.99546680001',
      '4513.99773339999',
      '2256.9988667'
    ]

    // 對應的 ScaleDenominator 值（用於計算 resolution）
    const scaleDenominators = [
      2183915.09386218,
      1091957.54693109,
      545978.773465546,
      272989.386732773,
      136494.693366434,
      68247.3466831696,
      34123.6733415848,
      17061.8366707924,
      8530.91833544346,
      4265.45916772172,
      2132.72958386086
    ]

    // 計算解析度：resolution = scaleDenominator × 0.28mm/pixel ÷ 1000
    const resolutions = scaleDenominators.map(sd => sd * 0.00028)

    // 從 GetCapabilities 取得的 TopLeftCorner
    const origin: [number, number] = [13132780.1813854, 3058175.99664622]

    const functionalZoneMapLayer = mapLayers.value.find(l => l.id === 'functional-zone-land-designated-use')!
    const functionalZoneLayer = new TileLayer({
      source: new WMTS({
        url: 'https://www.iacloud.ia.gov.tw/ServerGate/SGSGate.ashx/WMTS/functional_zoning_2',
        layer: 'functional_zoning_2',
        matrixSet: 'functional_zoning_2',
        format: 'image/png',
        projection: projection,
        tileGrid: new WMTSTileGrid({
          origin: origin,
          resolutions: resolutions,
          matrixIds: matrixIds
        }),
        style: 'default',
        wrapX: false
      }),
      visible: functionalZoneMapLayer.visible,
      opacity: functionalZoneMapLayer.opacity
    })

    // 建立標準 GoogleMapsCompatible TileGrid（NLSC 圖層共用）
    const nlscProjection = getProjection('EPSG:3857')!
    const nlscProjectionExtent = nlscProjection.getExtent()
    const nlscSize = getWidth(nlscProjectionExtent) / 256
    const nlscResolutions = new Array(20)
    const nlscMatrixIds = new Array(20)
    for (let z = 0; z < 20; ++z) {
      nlscResolutions[z] = nlscSize / Math.pow(2, z)
      nlscMatrixIds[z] = z.toString()
    }
    const nlscTileGrid = new WMTSTileGrid({
      origin: getTopLeft(nlscProjectionExtent),
      resolutions: nlscResolutions,
      matrixIds: nlscMatrixIds
    })

    // 建立非都市土地使用分區圖 WMTS 圖層（使用標準 GoogleMapsCompatible）
    const nonUrbanLandUseMapLayer = mapLayers.value.find(l => l.id === 'non-urban-land-use')!
    const nonUrbanLandUseLayer = new TileLayer({
      source: new WMTS({
        url: 'https://wmts.nlsc.gov.tw/wmts',
        layer: 'nURBAN1',
        matrixSet: 'GoogleMapsCompatible',
        format: 'image/png',
        projection: nlscProjection,
        tileGrid: nlscTileGrid,
        style: 'default',
        wrapX: false
      }),
      visible: nonUrbanLandUseMapLayer.visible,
      opacity: nonUrbanLandUseMapLayer.opacity
    })

    // 建立公有土地地籍圖 WMTS 圖層（使用標準 GoogleMapsCompatible）
    const publicLandMapLayer = mapLayers.value.find(l => l.id === 'public-land')!
    const publicLandLayer = new TileLayer({
      source: new WMTS({
        url: 'https://wmts.nlsc.gov.tw/wmts',
        layer: 'LAND_OPENDATA',
        matrixSet: 'GoogleMapsCompatible',
        format: 'image/png',
        projection: nlscProjection,
        tileGrid: nlscTileGrid,
        style: 'default',
        wrapX: false
      }),
      visible: publicLandMapLayer.visible,
      opacity: publicLandMapLayer.opacity
    })
  // Joya 加入 其他輔助圖層
  // 1. 都市計畫土地使用分區圖 (LUIMAP)
    const urbanLandUseMapLayer = mapLayers.value.find(l => l.id === 'urban-land-use')!
    const urbanLandUseLayer = new TileLayer({
      source: new WMTS({
        url: 'https://wmts.nlsc.gov.tw/wmts',
        layer: 'LUIMAP', // 都市計畫使用分區
        matrixSet: 'GoogleMapsCompatible',
        format: 'image/png',
        projection: nlscProjection,
        tileGrid: nlscTileGrid,
        style: 'default',
        wrapX: false
      }),
      visible: urbanLandUseMapLayer.visible,
      opacity: urbanLandUseMapLayer.opacity,
      zIndex: 10 // 預設層級，後續會被自動排序覆蓋
    })

    // 2. 村里界 (VILLAGE)
    const villageMapLayer = mapLayers.value.find(l => l.id === 'village-boundary')!
    const villageLayer = new TileLayer({
      source: new WMTS({
        url: 'https://wmts.nlsc.gov.tw/wmts',
        layer: 'Village', // 村里界
        matrixSet: 'GoogleMapsCompatible',
        format: 'image/png',
        projection: nlscProjection,
        tileGrid: nlscTileGrid,
        style: 'default',
        wrapX: false
      }),
      visible: villageMapLayer.visible,
      opacity: villageMapLayer.opacity
    })

    // 3. 鄉鎮市區界 (TOWN)
    const townshipMapLayer = mapLayers.value.find(l => l.id === 'township-boundary')!
    const townshipLayer = new TileLayer({
      source: new WMTS({
        url: 'https://wmts.nlsc.gov.tw/wmts',
        layer: 'TOWN', // 鄉鎮市區界
        matrixSet: 'GoogleMapsCompatible',
        format: 'image/png',
        projection: nlscProjection,
        tileGrid: nlscTileGrid,
        style: 'default',
        wrapX: false
      }),
      visible: townshipMapLayer.visible,
      opacity: townshipMapLayer.opacity
    })

    // 4. 正射影像圖 (通用版) (PHOTO2)
    const orthophotoMapLayer = mapLayers.value.find(l => l.id === 'orthophoto-general')!
    const orthophotoLayer = new TileLayer({
      source: new WMTS({
        url: 'https://wmts.nlsc.gov.tw/wmts',
        layer: 'PHOTO2', // 正射影像
        matrixSet: 'GoogleMapsCompatible',
        format: 'image/jpeg', // 影像通常是 jpg
        projection: nlscProjection,
        tileGrid: nlscTileGrid,
        style: 'default',
        wrapX: false
      }),
      visible: orthophotoMapLayer.visible,
      opacity: orthophotoMapLayer.opacity
    })

    // 5. 正射影像圖 (混和) 
    const orthophotoMixMapLayer = mapLayers.value.find(l => l.id === 'orthophoto-hybrid')!
    const orthophotoMixLayer = new TileLayer({
      source: new WMTS({
        url: 'https://wmts.nlsc.gov.tw/wmts',
        layer: 'PHOTO_MIX', // 正射影像
        matrixSet: 'GoogleMapsCompatible',
        format: 'image/jpeg', // 影像通常是 jpg
        projection: nlscProjection,
        tileGrid: nlscTileGrid,
        style: 'default',
        wrapX: false
      }),
      visible: orthophotoMixMapLayer.visible,
      opacity: orthophotoMixMapLayer.opacity
    })
    

    // 6. 地段外圍圖/段籍圖 (LANDSECT)
    const landSectionMapLayer = mapLayers.value.find(l => l.id === 'land-section')!
    const landSectionLayer = new TileLayer({
      source: new WMTS({
        url: 'https://wmts.nlsc.gov.tw/wmts',
        layer: 'LANDSECT', // NLSC 圖層名稱: 地段外圍圖
        matrixSet: 'GoogleMapsCompatible',
        format: 'image/png',
        projection: nlscProjection,
        tileGrid: nlscTileGrid,
        style: 'default',
        wrapX: false
      }),
      visible: landSectionMapLayer.visible,
      opacity: landSectionMapLayer.opacity,
      zIndex: 12 // 通常段籍圖需要疊在比較上層
    })
    //joya add end
    
    // === 創建量測圖層 ===
    measureSource.value = new VectorSource();
    measureLayer.value = new VectorLayer({
      source: measureSource.value,
      style: new Style({
        fill: new Fill({
          color: 'rgba(255, 255, 255, 0.2)',
        }),
        stroke: new Stroke({
          color: '#ffcc33',
          width: 2,
        }),
        image: new Circle({
          radius: 7,
          fill: new Fill({
            color: '#ffcc33',
          }),
        }),
      }),
      visible: true,
      zIndex: 1000, // 確保量測圖層在最上層
    });

    // === 創建定位標記圖層 ===
    locationMarkerSource.value = new VectorSource();

    // 創建 mdi-map-marker SVG data URL
    const markerSvg = `
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="48" height="48">
        <path fill="#EF5350" d="M12,11.5A2.5,2.5 0 0,1 9.5,9A2.5,2.5 0 0,1 12,6.5A2.5,2.5 0 0,1 14.5,9A2.5,2.5 0 0,1 12,11.5M12,2A7,7 0 0,0 5,9C5,14.25 12,22 12,22C12,22 19,14.25 19,9A7,7 0 0,0 12,2Z"/>
        <path fill="#FFFFFF" stroke="#FFFFFF" stroke-width="0.5" d="M12,11.5A2.5,2.5 0 0,1 9.5,9A2.5,2.5 0 0,1 12,6.5A2.5,2.5 0 0,1 14.5,9A2.5,2.5 0 0,1 12,11.5Z" opacity="0.9"/>
      </svg>
    `.trim();
    const markerDataUrl = 'data:image/svg+xml;charset=utf-8,' + encodeURIComponent(markerSvg);

    locationMarkerLayer.value = new VectorLayer({
      source: locationMarkerSource.value,
      style: new Style({
        image: new Icon({
          src: markerDataUrl,
          anchor: [0.5, 1], // 錨點設在底部中央，符合地圖標記習慣
          scale: 1,
        }),
      }),
      visible: true,
      zIndex: 1001, // 確保定位標記在量測圖層之上
    });

    // === 創建地籍查詢結果圖層 ===
    cadastralResultSource.value = new VectorSource();

    cadastralResultLayer.value = new VectorLayer({
      source: cadastralResultSource.value,
      style: new Style({
        stroke: new Stroke({
          color: '#FF5722',  // 深橘色邊界
          width: 3
        }),
        fill: new Fill({
          color: 'rgba(255, 87, 34, 0.2)'  // 半透明橘色填充
        })
      }),
      visible: true,
      zIndex: 999, // 在量測圖層下方，但在其他圖層上方
    });

    const layers = [nlscLayer, osmLayer, stamenLayer, urbanLandUseLayer, villageLayer, townshipLayer, orthophotoLayer, orthophotoMixLayer, landSectionLayer, gridLayer, grantLayer, functionalZoneLayer, nonUrbanLandUseLayer, publicLandLayer, measureLayer.value, cadastralResultLayer.value, locationMarkerLayer.value];

    // 關聯圖層到 mapLayers 數據結構（使用 ID 查找）
    nlscMapLayer.layer = nlscLayer;
    osmMapLayer.layer = osmLayer;
    stamenMapLayer.layer = stamenLayer;
    grantGridMapLayer.layer = gridLayer;
    grantPointsMapLayer.layer = grantLayer;
    functionalZoneMapLayer.layer = functionalZoneLayer;
    nonUrbanLandUseMapLayer.layer = nonUrbanLandUseLayer;
    publicLandMapLayer.layer = publicLandLayer;
    //Joya add
    urbanLandUseMapLayer.layer = urbanLandUseLayer;
    villageMapLayer.layer = villageLayer;
    townshipMapLayer.layer = townshipLayer;
    orthophotoMapLayer.layer = orthophotoLayer;
    orthophotoMixMapLayer.layer = orthophotoMixLayer;
    landSectionMapLayer.layer = landSectionLayer;
    //joya add end

    // 設置初始可見性和透明度
    mapLayers.value.forEach((layerInfo) => {
      if (layerInfo.layer) {
        layerInfo.layer.setVisible(layerInfo.visible);
        layerInfo.layer.setOpacity(layerInfo.opacity);
        console.log(`圖層 ${layerInfo.name} 初始化: 可見=${layerInfo.visible}, 透明度=${layerInfo.opacity}`);
      }
    });

    // 創建 ScaleLine 控制
    const scaleLineControl = new ScaleLine({
      units: 'metric',
      bar: true,
      steps: 4,
      text: true,
      minWidth: 100
    });

    // 創建地圖 - 使用 markRaw 防止 Vue reactivity 包裝
    map = markRaw(new Map({
      target: mapContainer.value,
      layers: layers,
      view: new View({
        center: mapParams.center,
        zoom: mapParams.zoom,
        minZoom: 5,
        maxZoom: 19
      }),
      controls: defaultControls({
        zoom: false,
        attribution: true,
        rotate: false
      }).extend([scaleLineControl])
    }));

    // 添加點擊事件處理補助案件點位和格網
    // 注意：使用較低的優先級，讓 Draw interaction 優先處理
    const handleMapClick = (event: any) => {
      // 暫時註釋掉，測試是否影響 Draw
      // if (measureDraw.value || isDrawing.value) {
      //   return;
      // }

      // 只在沒有 Draw 時處理 feature 查詢
      if (measureDraw.value || isDrawing.value) {
        return;
      }

      const features = map!.getFeaturesAtPixel(event.pixel);
      if (features.length > 0) {
        if (displayMode.value === 'points') {
          // 點位模式：處理聚合點位
          const feature = features.find((f: any) => {
            const layer = f.get('layer');
            const isCadastral = f.get('cadastral'); // 排除地籍圖層
            return !isCadastral && (layer === grantLayer || !layer); // 補助案件特徵
          });

          if (feature) {
            const properties = feature.getProperties();
            showGrantPopup(event.coordinate, properties);
          }
        } else if (displayMode.value === 'grid') {
          // 格網模式：處理格網統計
          const gridFeature = features.find((f: any) => f.get('gridKey'));
          if (gridFeature) {
            const properties = gridFeature.getProperties();
            showGridPopup(event.coordinate, properties);
          }
        }
      }
    };

    map.on('singleclick', handleMapClick);

    // 確保地圖正確渲染
    setTimeout(async () => {
      if (map) {
        map.updateSize();

        // 添加地圖移動和縮放事件監聽（統一處理）
        map.on('moveend', handleViewChange)

        // 添加縮放變化監聽（使用防抖）
        let zoomTimeout: ReturnType<typeof setTimeout>
        map.getView().on('change:resolution', () => {
          clearTimeout(zoomTimeout)
          zoomTimeout = setTimeout(() => {
            handleViewChange()
          }, 500)
        })

        // 標記地圖已初始化完成
        mapInitialized.value = true;

        // 記錄初始縮放等級
        const initialZoom = map?.getView().getZoom();
        console.log('地圖初始化完成，初始縮放等級:', initialZoom);

        // 初始化 GIS Store
        try {
          await gisStore.initialize();

          // 使用統一的初始載入條件設置 GIS Store
          const initialParams = getInitialOverlayLoadingParams()
          const initialYearRange: [number, number] = [initialParams.apply_year_min!, initialParams.apply_year_max!]
          yearRange.value.current = initialYearRange
          await gisStore.updateYearRange(initialYearRange)

          console.log(`[InitMap] 使用統一初始載入條件設定年度範圍: 民國${initialParams.apply_year_min}-${initialParams.apply_year_max}年`)
        } catch (error) {
          console.error('GIS Store 初始化失敗:', error);
          showError('GIS 系統初始化失敗');
        }

        // 設置初始圖層可見性
        updateLayerVisibility();

        // 確保初始化後觸發圖層資料載入
        setTimeout(() => {
          if (displayMode.value === 'grid' && grantGridLayer.value) {
            const gridSource = grantGridLayer.value.getSource();
            if (gridSource) {
              console.log('[InitMap] 初始化完成，觸發格網圖層資料載入');
              gridSource.refresh();
            }
          } else if (displayMode.value === 'points' && grantPointsLayer.value) {
            const pointSource = grantPointsLayer.value.getSource() as VectorSource;
            if (pointSource) {
              console.log('[InitMap] 初始化完成，觸發點位圖層資料載入');
              pointSource.refresh();
            }
          }
        }, 100);

        // OpenLayers 會自動觸發資料載入，使用當前篩選條件
        console.log('地圖初始化完成，OpenLayers 將使用初始篩選條件載入圖層資料');
      }
    }, 200);

    console.log('地圖初始化成功');
  } catch (error) {
    console.error('地圖初始化失敗:', error);
  }
}

// 在開發環境中暴露測試函數
if (import.meta.env.DEV) {
  (window as any).testFrontendFilters = testFrontendFilters
  (window as any).getInitialOverlayLoadingParams = getInitialParams
  // 新增格網測試函數
  (window as any).testGridLayer = () => {
    console.log('[TestGrid] 開始測試格網圖層...');
    if (grantGridLayer.value) {
      const gridSource = grantGridLayer.value.getSource();
      console.log('[TestGrid] 格網圖層存在:', !!grantGridLayer.value);
      console.log('[TestGrid] 格網資料源存在:', !!gridSource);
      console.log('[TestGrid] 格網特徵數量:', gridSource?.getFeatures().length || 0);
      console.log('[TestGrid] 格網圖層可見性:', grantGridLayer.value.getVisible());
      console.log('[TestGrid] 顯示模式:', displayMode.value);

      // 手動觸發格網更新
      if (allLoadedFeatures.value.length > 0) {
        console.log('[TestGrid] 使用已載入資料更新格網:', allLoadedFeatures.value.length, '個特徵');
        updateGridLayer(allLoadedFeatures.value);
      } else {
        console.log('[TestGrid] 觸發格網圖層重新載入');
        gridSource?.refresh();
      }
    } else {
      console.log('[TestGrid] 格網圖層不存在！');
    }
  };

  // 新增測試格網函數，使用假資料
  (window as any).createTestGrid = () => {
    console.log('[CreateTestGrid] 建立測試格網...');
    if (!grantGridLayer.value || !map) {
      console.log('[CreateTestGrid] 格網圖層或地圖不存在！');
      return;
    }

    // 建立一些測試點位資料（台灣中部）
    const testFeatures: GeoJsonFeature[] = [
      {
        type: 'Feature',
        geometry: { type: 'Point', coordinates: [120.9, 23.5] },
        properties: { cluster: false, id: 1, source_system: 'new_aerc', source_id: 'test1', applicant_name: '測試1', land_section: '測試段', land_number: '001', apply_year: 114, case_status: '核准', land_type: '農地' }
      },
      {
        type: 'Feature',
        geometry: { type: 'Point', coordinates: [120.91, 23.51] },
        properties: { cluster: false, id: 2, source_system: 'new_aerc', source_id: 'test2', applicant_name: '測試2', land_section: '測試段', land_number: '002', apply_year: 114, case_status: '核准', land_type: '農地' }
      },
      {
        type: 'Feature',
        geometry: { type: 'Point', coordinates: [120.92, 23.52] },
        properties: { cluster: false, id: 3, source_system: 'new_aerc', source_id: 'test3', applicant_name: '測試3', land_section: '測試段', land_number: '003', apply_year: 114, case_status: '核准', land_type: '農地' }
      }
    ];

    console.log('[CreateTestGrid] 使用測試資料建立格網:', testFeatures.length, '個點位');
    updateGridLayer(testFeatures);
  };
  console.log('[Dev] 已暴露測試函數: testFrontendFilters, getInitialOverlayLoadingParams, testGridLayer, createTestGrid')
}

// 監視 fluid 狀態變化，以便在切換時更新地圖
watch(isFluid, () => {
  nextTick(() => {
    setTimeout(() => {
      if (map) {
        map.updateSize();
      }
    }, 100);
  });
});

// 監聽路由變化，如果URL參數變了，更新地圖
watch(() => route.query, (newQuery) => {
  if (!map || !mapInitialized.value) return;

  const lonStr = queryValueToString(newQuery.lon);
  const latStr = queryValueToString(newQuery.lat);
  const zStr = queryValueToString(newQuery.z);

  if (lonStr && latStr && zStr) {
    const view = map.getView();
    const center = fromLonLat([parseFloat(lonStr), parseFloat(latStr)]);

    view.animate({
      center: center,
      zoom: parseFloat(zStr),
      duration: 500
    });
  }
}, { deep: true });

// === OpenLayers 自動載入相關函數 ===

// 將 OpenLayers extent 轉換為 bbox 字符串
const extentToBbox = (extent: number[]) => {
  // extent 格式: [minX, minY, maxX, maxY] (投影坐標)
  // 轉換為經緯度
  const bottomLeft = toLonLat([extent[0], extent[1]])
  const topRight = toLonLat([extent[2], extent[3]])

  // 返回 bbox 字符串格式
  return `${bottomLeft[0]},${bottomLeft[1]},${topRight[0]},${topRight[1]}`
}

// 從 resolution 計算縮放等級
const resolutionToZoomLevel = (resolution: number) => {
  // OpenLayers resolution   // 轉換為縮放等級的近似公式
  return Math.round(Math.log2(156543.03392804097 / resolution))
}

// OpenLayers 圖層資料載入器（聚合用）- 只載入原始點位資料
const loadRawDataForLayer = async (
  layerType: 'grid' | 'points',
  extent: number[],
  resolution: number,
  projection: import('ol/proj/Projection').default,
  vectorSource: VectorSource
) => {
  try {
    // 防止重複載入
    if (gisLoading.value) {
      console.log(`[${layerType}Layer] 正在載入中，跳過此次請求`)
      return
    }

    const bbox = extentToBbox(extent)
    const zoomLevel = resolutionToZoomLevel(resolution)

    console.log(`[${layerType}Layer] OpenLayers 觸發原始資料載入:`, {
      bbox,
      zoomLevel,
      resolution,
      projection: projection.getCode()
    })

    // 根據圖層類型和當前狀態決定是否載入資料
    if (layerType === 'grid' && displayMode.value !== 'grid') {
      console.log('[GridLayer] 當前非格網統計模式，跳過載入')
      return
    }

    if (layerType === 'points' && displayMode.value !== 'points') {
      console.log('[PointsLayer] 當前非點位模式，跳過載入')
      return
    }

    // 檢查是否有搜尋條件（包含快速篩選和個別篩選）
    const hasQuickFilter = quickFilter.value;
    const hasIndividualCriteria = searchCriteria.value.applicantName ||
                                   searchCriteria.value.landSection ||
                                   searchCriteria.value.caseNumber;
    const hasSearchCriteria = hasQuickFilter || hasIndividualCriteria;

    let geoJsonData: GeoJsonFeatureCollection | null = null

    if (hasSearchCriteria) {
      // 執行搜尋 - 要求原始資料，移除數量限制以評估效能
      console.log(`[${layerType}Layer] 執行搜尋載入（原始資料，無數量限制）`)

      // 準備搜尋參數
      const searchParams: Record<string, unknown> = {};

      if (hasQuickFilter) {
        // 快速篩選（統一對所有欄位進行OR邏輯）
        console.log(`快速篩選: "${quickFilter.value}" 對所有欄位進行OR搜尋（申請人姓名、地段、地號、案件編號）`);
        searchParams.quick_filter = quickFilter.value;
        searchParams.quick_filter_targets = ['applicantName', 'landSection', 'landNumber', 'caseNumber'];
      }

      if (hasIndividualCriteria) {
        // 個別篩選（AND邏輯）
        searchParams.applicant_name = searchCriteria.value.applicantName || undefined;
        searchParams.land_section = searchCriteria.value.landSection || undefined;
        searchParams.case_number = searchCriteria.value.caseNumber || undefined;
      }

      await gisStore.searchCases(bbox, searchParams)
      geoJsonData = gisStore.lastLoadedData
    } else {
      // 一般載入 - 使用當前年度範圍和篩選條件
      const currentYearMin = yearRange.value.current[0];
      const currentYearMax = yearRange.value.current[1];

      // 強制使用高縮放等級確保後端回傳原始點位而非聚合資料
      const forceHighZoom = Math.max(zoomLevel, 15)
      await gisStore.loadGrantLocations(bbox, forceHighZoom, {
        apply_year_min: currentYearMin,
        apply_year_max: currentYearMax,
        no_clustering: true,
        source_system: searchCriteria.value.sourceSystem as 'new_aerc' | 'legacy_farmdata' | undefined
      })
      geoJsonData = gisStore.lastLoadedData
    }

    if (!geoJsonData || !geoJsonData.features) {
      console.log(`[${layerType}Layer] 無原始資料返回`)
      return
    }

    // ===== 新增：保存原始資料供前端篩選使用 =====
    // 如果是第一次載入或重新載入，保存原始資料
    if (!hasSearchCriteria) {
      // 一般載入時，保存所有資料
      allLoadedFeatures.value = [...geoJsonData.features];
      filteredFeatures.value = [...geoJsonData.features];
      console.log(`已保存原始資料：${allLoadedFeatures.value.length} 個特徵，供前端篩選使用`);
    } else {
      // 搜尋載入時，不更新原始資料（保持現有的原始資料）
      console.log('搜尋載入，保持現有原始資料不變');
    }

    // 清除現有特徵
    vectorSource.clear()

    // 載入新特徵 - 都作為個別點位處理
    if (layerType === 'grid') {
      // 格網圖層：直接使用原始特徵資料進行格網統計
      updateGridLayer(geoJsonData.features);
      console.log(`[GridLayer] 載入了 ${geoJsonData.features.length} 個原始點位進行格網統計`)

    } else {
      // 點位圖層：使用 GeoJSON format
      try {
        const geoJSONFormat = new GeoJSON()
        const features = geoJSONFormat.readFeatures(geoJsonData, {
          featureProjection: 'EPSG:3857'
        })

        vectorSource.addFeatures(features)
        console.log(`[PointsLayer] 載入了 ${features.length} 個原始點位`)

      } catch (error) {
        console.error(`[PointsLayer] GeoJSON 解析失敗:`, error)
        // 降級處理
        const features = geoJsonData.features.map((featureData: GeoJsonFeature) => {
          if (featureData.geometry?.type === 'Point') {
            const coords = featureData.geometry.coordinates as [number, number]
            const point = new Point(fromLonLat(coords))
            return new Feature({
              geometry: point,
              ...featureData.properties
            })
          }
          return null;
        }).filter((f): f is Feature<Point> => f !== null)

        vectorSource.addFeatures(features)
        console.log(`[PointsLayer] 手動載入了 ${features.length} 個原始點位`)
      }
    }

  } catch (error) {
    console.error(`[${layerType}Layer] 原始資料載入失敗:`, error)
    throw error
  }
}

// 建立聚合點位樣式
const createPointStyle = (feature: Feature | import('ol/render/Feature').default) => {
  const sourceSystem = feature.get('source_system')
  const isNewSystem = sourceSystem === 'new_aerc'
  const fillColor = isNewSystem ? '#3498db' : '#e74c3c'
  const strokeColor = isNewSystem ? '#2980b9' : '#c0392b'

  return new Style({
    image: new Circle({
      radius: 8,
      fill: new Fill({ color: fillColor }),
      stroke: new Stroke({ color: strokeColor, width: 2 })
    })
  })
}

// 刷新圖層資料（供手動觸發使用）
const refreshLayerData = () => {
  if (grantGridLayer.value && displayMode.value === 'grid') {
    console.log('[RefreshLayers] 刷新格網統計圖層')
    // 格網圖層需要重新載入或統計
    const gridSource = grantGridLayer.value.getSource();
    if (gridSource) {
      // 觸發重新載入
      gridSource.refresh();
    }
  }

  if (grantPointsLayer.value && displayMode.value === 'points') {
    console.log('[RefreshLayers] 刷新點位圖層')
    const pointSource = grantPointsLayer.value.getSource() as VectorSource
    pointSource?.refresh()
  }
}
</script>

<style>
/* 圖例 Snackbar 全寬度樣式 */
.legend-snackbar-content {
  width: 100% !important;
  max-width: none !important;
  margin: 0 !important;
}

.ol-zoom {
  display: none !important;
}

.ol-control button {
  background-color: rgba(40, 40, 40, 0.8) !important;
}

.ol-control button:hover {
  background-color: rgba(40, 40, 40, 1) !important;
}

.fill-height {
  height: 100vh;
}

#map {
  position: relative;
  overflow: hidden;
  height: 100%;
  width: 100%;
}

#map:focus {
  outline: none;
}

.container-full-height {
  display: flex;
  flex-direction: column;
  height: calc(100vh - 151px); /* 扣除 NavBar 高度，通常是 64px */
  padding: 0 !important;
  margin: 0 !important;
  max-width: 100% !important;
  overflow: hidden;
}

.map-card {
  display: flex;
  flex-direction: column;
  flex-grow: 1;
  height: 100%;
  border-radius: 0 !important;
  overflow: hidden;
}

.map-container {
  flex-grow: 1;
  width: 100%;
  height: 0; /* 讓 flex-grow 控制高度 */
  min-height: 0; /* 移除 min-height: 100vh */
  overflow: hidden;
}

/* 自定義地圖控制按鈕樣式 */
.map-controls {
  position: absolute;
  top: 10px;
  right: 10px;
  z-index: 1000;
}

/* 圖層管理面板樣式 */
.layers-panel {
  position: absolute;
  z-index: 1001;
  max-width: 350px; /* 稍微增加最大寬度 */
  min-width: 250px;
  width: auto; /* 讓寬度根據內容調整 */
  transition: none; /* 取消過渡動畫，以便拖拽更流暢 */
}

/* 浮動工具面板樣式 */
.floating-panel {
  position: absolute;
  z-index: 1002;
  transition: none; /* 取消過渡動畫，以便拖拽更流暢 */
}

.tool-panel {
  background-color: rgba(255, 255, 255, 0.95) !important;
  backdrop-filter: blur(8px);
  border: 1px solid rgba(0, 0, 0, 0.1);
}

.tool-panel.dragging {
  opacity: 0.9;
  cursor: grabbing;
}

.tool-panel .draggable-header {
  cursor: grab;
  user-select: none;
  padding: 12px 16px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
  background: rgba(0, 0, 0, 0.02);
}

.tool-panel .draggable-header:hover {
  background: rgba(0, 0, 0, 0.05);
}

.tool-panel .draggable-header:active {
  cursor: grabbing;
}

.tool-panel .drag-handle {
  color: rgba(0, 0, 0, 0.4);
  cursor: grab;
}


.measure-results {
  margin-top: 8px;
}

.layer-control-panel {
  background-color: rgba(255, 255, 255, 0.95) !important;
  max-height: calc(100vh - 120px); /* 使用視窗高度減去安全邊距 */
  min-height: 200px; /* 設定最小高度 */
  height: auto; /* 自動調整高度 */
  overflow-y: auto;
  user-select: none; /* 防止拖拽時選中文字 */
  width: auto; /* 讓寬度根據內容調整 */
  display: flex;
  flex-direction: column;
}

.layer-control-panel .v-card-text {
  flex: 1;
  overflow-y: auto;
  max-height: none;
}

.layer-control-panel .v-list {
  padding: 0;
}

.layer-control-panel .v-list-subheader {
  background-color: rgba(248, 248, 248, 0.9);
  padding: 12px 16px;
  margin: 0;
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
  font-weight: 600;
  letter-spacing: 0.5px;
}

.layer-control-panel .v-list-item {
  min-height: 48px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
  transition: background-color 0.2s ease;
}

.layer-control-panel .v-list-item:hover {
  background-color: rgba(0, 0, 0, 0.02);
}

.layer-control-panel .v-list-item:last-child {
  border-bottom: none;
}

.draggable-header {
  cursor: move;
  user-select: none;
}

.draggable-header:hover {
  background-color: rgba(0, 0, 0, 0.05);
}

.layer-control-panel.dragging {
  opacity: 0.8;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3) !important;
  cursor: move;
}

.drag-handle {
  opacity: 0.6;
  color: #666;
}

/* 透明度控制區域優化 */
.opacity-control-section {
  background-color: rgba(248, 248, 248, 0.8);
  margin: 0 8px;
  border-radius: 4px;
  padding: 8px 12px;
  transition: background-color 0.2s ease;
}

.opacity-control-section:hover {
  background-color: rgba(240, 240, 240, 0.9);
}

/* 自定義滾動條樣式 */
.layer-control-panel::-webkit-scrollbar {
  width: 6px;
}

.layer-control-panel::-webkit-scrollbar-track {
  background: rgba(0, 0, 0, 0.1);
  border-radius: 3px;
}

.layer-control-panel::-webkit-scrollbar-thumb {
  background: rgba(0, 0, 0, 0.3);
  border-radius: 3px;
}

.layer-control-panel::-webkit-scrollbar-thumb:hover {
  background: rgba(0, 0, 0, 0.5);
}

/* 地圖控制面板樣式 */
.map-control-panel {
  background-color: rgba(255, 255, 255, 0.9) !important;
  min-width: 70px; /* 增加寬度以容納文字 */
}

.control-btn-vertical {
  width: 100% !important;
  height: auto !important;
  min-height: 60px !important;
  padding: 8px 4px !important;
}

.control-btn-vertical .v-btn__content {
  flex-direction: column !important;
  height: auto !important;
}

.btn-text {
  font-size: 14px;
  color: inherit;
  line-height: 1;
  font-weight: 500;
  white-space: nowrap;
}

/* 當按鈕處於 active 狀態時，文字也會繼承顏色 */
.v-btn--active .btn-text {
  color: inherit;
}

.btn-label {
  font-size: 14px;
  color: rgba(0, 0, 0, 0.6);
  line-height: 1;
  font-weight: 500;
  margin-top: 2px;
}

.control-btn {
  width: 40px;
  height: 40px;
}

/* 篩選工具欄樣式 */
.filter-toolbar-container {
  position: absolute;
  top: 10px;
  left: 10px;
  z-index: 1002;
  width: 480px; /* 固定寬度，不會因展開而改變 */
  max-width: calc(100vw - 120px); /* 確保不會與右側控制面板重疊 */
}

/* v-expansion-panels 主體樣式 */
.filter-expansion-panels {
  /* background-color: rgba(255, 255, 255, 0.95) !important; */
  /* backdrop-filter: blur(10px); */
  border: 1px solid rgba(0, 0, 0, 0.1) !important;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15) !important;
  border-radius: 12px !important; /* lg 圓角 */
  overflow: hidden; /* 確保內容不會超出圓角 */
  width: 100% !important; /* 繼承容器固定寬度 */
  max-width: 100% !important; /* 防止內容撐大 */
}

/* v-expansion-panel 個別面板樣式 */
.filter-expansion-panel {
  /* background-color: transparent !important; */
  width: 100% !important; /* 確保與父容器同寬 */
  max-width: 100% !important; /* 防止內容撐大 */
}

/* 確保面板標題與主容器同寬 */
.filter-expansion-panel .v-expansion-panel-title {
  width: 100% !important;
  /* border-radius: 0 !important; /* 移除內部圓角，讓外層統一控制 */
}

/* 確保面板內容與主容器同寬 */
.filter-expansion-panel .v-expansion-panel-text {
  width: 100% !important;
  /* border-radius: 0 !important; /* 移除內部圓角，讓外層統一控制 */
}

/* 面板標題樣式 */
.filter-panel-title {
  /* padding: 16px 20px !important; */
  min-height: auto !important;
  width: 100% !important;
  max-width: 100% !important;
  overflow: hidden; /* 防止內容溢出 */
}

/* 面板標題內容區域 */
.filter-panel-title .d-flex {
  width: 100% !important;
  max-width: 100% !important;
  overflow: hidden; /* 防止內容溢出 */
}

/* 主篩選輸入框樣式 */
.filter-input {
  min-width: 200px;
  max-width: 260px; /* 減少最大寬度以適應固定容器 */
  /* flex-grow: 1; */
  /*flex-shrink: 1; /* 允許收縮 */
}

/* 面板內容樣式 - 已註解 */

/* 內容區域的容器樣式 */
.filter-panel-content .v-container {
  max-width: 100% !important;
  width: 100% !important;
  /* padding: 0 !important; */
}

/* 年度範圍輸入框樣式 */
.year-range-inputs {
  margin: 0 !important;
}

.year-range-inputs .v-col {
  padding: 0 4px !important;
}

.year-range-inputs .v-text-field {
  font-size: 0.875rem;
}

.year-range-inputs .v-field__prefix,
.year-range-inputs .v-field__suffix {
  font-size: 0.8rem;
  color: rgba(0, 0, 0, 0.6);
  font-weight: 500;
}

/* 年度輸入框焦點樣式 */
.year-range-inputs .v-text-field .v-field--focused {
  box-shadow: 0 0 0 2px rgba(25, 118, 210, 0.2);
}

/* 確保數字輸入框樣式一致 */
.year-range-inputs input[type="number"] {
  text-align: center;
  font-weight: 500;
}

/* 移除 Chrome 的數字輸入框箭頭 */
.year-range-inputs input[type="number"]::-webkit-outer-spin-button,
.year-range-inputs input[type="number"]::-webkit-inner-spin-button {
  -webkit-appearance: none;
  margin: 0;
}

/* 行動版時進一步優化 */
@media (max-width: 768px) {
  /* 行動版年度輸入框優化 */
  .year-range-inputs .v-text-field {
    font-size: 0.8rem;
  }

  .year-range-inputs .v-field__prefix,
  .year-range-inputs .v-field__suffix {
    font-size: 0.75rem;
  }
}

@media (max-width: 480px) {
  .filter-toolbar-container {
    width: calc(100vw - 16px) !important;
    max-width: 100%;
  }

  .filter-input {
    min-width: 120px;
    max-width: 150px;
  }

  /* 小屏幕時隱藏部分 chips 或使用更小的樣式 */
  .filter-panel-title .v-chip {
    font-size: 0.7rem;
    height: 20px;
    padding: 0 8px;
  }
}

/* 確保篩選面板層次正確 */
.filter-toolbar-container {
  z-index: 1002;
}

.search-panel {
  z-index: 1001;
}

.layers-panel {
  z-index: 1001;
}

/* 展開動畫優化 */
.filter-expansion-panels .v-expansion-panel-title__icon {
  transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

/* 自定義滾動條 */
.filter-panel-content::-webkit-scrollbar {
  width: 6px;
}

/* 版權資訊樣式 */
.copyright-info {
  position: absolute;
  bottom: 10px;
  right: 10px;
  z-index: 1000;
  pointer-events: none; /* 允許滑鼠事件穿透到地圖 */
}

.copyright-text {
  background-color: rgba(255, 255, 255, 0);
  backdrop-filter: blur(4px);
  padding: 8px 12px;
  border-radius: 6px;
  /* box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1); */
  font-size: 12px;
  color: rgba(0, 0, 0, 0.7);
  line-height: 1.4;
  text-align: right;
  /* border: 1px solid rgba(0, 0, 0, 0.1); */
}

.copyright-text > div {
  margin: 0;
  white-space: nowrap;
}

/* 響應式調整 */
@media (max-width: 768px) {
  .copyright-info {
    bottom: 8px;
    right: 8px;
  }

  .copyright-text {
    padding: 6px 10px;
    font-size: 11px;
  }
}

@media (max-width: 480px) {
  .copyright-info {
    bottom: 6px;
    right: 6px;
  }

  .copyright-text {
    padding: 5px 8px;
    font-size: 10px;
  }
}

/* === 量測工具 Tooltip 樣式 === */
.ol-tooltip {
  position: relative;
  background: rgba(0, 0, 0, 0.75);
  border-radius: 4px;
  color: white;
  padding: 6px 10px;
  opacity: 0.9;
  white-space: nowrap;
  font-size: 13px;
  font-weight: 500;
  cursor: default;
  pointer-events: none;
}

.ol-tooltip-measure {
  opacity: 1;
  font-weight: bold;
  background: rgba(33, 150, 243, 0.9);
}

.ol-tooltip-static {
  background-color: rgba(255, 152, 0, 0.9);
  color: white;
  border: 2px solid rgba(255, 255, 255, 0.8);
  font-size: 12px;
  padding: 4px 8px;
}

.ol-tooltip-measure:before,
.ol-tooltip-static:before {
  border-top: 6px solid rgba(33, 150, 243, 0.9);
  border-right: 6px solid transparent;
  border-left: 6px solid transparent;
  content: "";
  position: absolute;
  bottom: -6px;
  margin-left: -7px;
  left: 50%;
}

.ol-tooltip-static:before {
  border-top-color: rgba(255, 152, 0, 0.9);
}

.hidden {
  display: none;
}

/* === 圖例 Drawer 樣式 === */
.legend-drawer {
  position: absolute !important;
  max-height: 120px;
  z-index: 1000;
}

.legend-items-container::-webkit-scrollbar {
  width: 6px;
}

.legend-items-container::-webkit-scrollbar-track {
  background: rgba(0, 0, 0, 0.05);
  border-radius: 3px;
}

.legend-items-container::-webkit-scrollbar-thumb {
  background: rgba(0, 0, 0, 0.2);
  border-radius: 3px;
}

.legend-items-container::-webkit-scrollbar-thumb:hover {
  background: rgba(0, 0, 0, 0.3);
}

/* 響應式調整 */
@media (max-width: 768px) {
  .legend-drawer {
    max-height: 150px;
  }

  .legend-items-container {
    max-height: 100px;
  }
}
</style>
