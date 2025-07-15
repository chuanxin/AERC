<template>
  <div class="fill-height d-flex flex-column">
    <v-card class="flex-grow-1 d-flex flex-column">
      <!-- <v-card-title class="d-flex align-center pe-2">
        <v-icon icon="mdi-map-marker-path" />
        &nbsp; AERC 補助案件 GIS 圖台
        <v-spacer />
        <v-btn
          density="compact"
          variant="text"
          prepend-icon="mdi-magnify"
          class="me-2"
          @click="toggleSearchPanel"
        >
          搜尋案件
        </v-btn>
        <v-btn
          density="compact"
          variant="text"
          prepend-icon="mdi-link"
          class="me-2"
          @click="copyMapLink"
        >
          複製地圖連結
        </v-btn>
      </v-card-title> -->
      <v-divider />
      <div
        id="map"
        ref="mapContainer"
        class="map-container"
        style="min-height: 0;"
      >
        <!-- 地圖容器 -->

        <!-- 左上方篩選工具欄 -->
        <div class="filter-toolbar-container">
          <v-expansion-panels
            v-model="expandedPanel"
            class="filter-expansion-panels"
            color="surface-light"
            elevation="8"
            rounded="lg"
            variant="accordion"
          >
            <v-expansion-panel
              value="filter"
              class="filter-expansion-panel"
              rounded="lg"
            >
              <!-- 面板標題 - 包含主要篩選控制 -->
              <v-expansion-panel-title class="filter-panel-title pa-3">
                <template #default="{ expanded }">
                  <div class="d-flex align-center w-100">
                    <!-- 主篩選輸入框 -->
                    <v-text-field
                      v-model="quickFilter"
                      label="快速篩選（申請人/地段/地號/案件編號）"
                      prepend-inner-icon="mdi-filter-variant"
                      class="filter-input me-3"
                      clearable
                      density="compact"
                      variant="solo"
                      hide-details
                      single-line
                      @click.stop
                      @focus="onFilterFocus"
                      @blur="onFilterBlur"
                      @input="onQuickFilterChange"
                    />

                    <!-- 年度範圍指示器 -->
                    <v-chip
                      size="small"
                      color="primary"
                      variant="outlined"
                      class="me-2 flex-shrink-0"
                    >
                      <v-icon size="small" class="me-1">mdi-calendar</v-icon>
                      民國{{ filterCriteria.yearStart }}~{{ filterCriteria.yearEnd }}年
                    </v-chip>

                    <!-- 篩選狀態指示器 -->
                    <v-chip
                      v-if="hasActiveFilters"
                      size="small"
                      color="success"
                      variant="outlined"
                      class="me-2 flex-shrink-0"
                    >
                      <v-icon size="small" class="me-1">mdi-filter-check</v-icon>
                      已篩選
                    </v-chip>
                  </div>
                </template>

                <!-- 自定義展開圖示 -->
                <template #actions="{ expanded }">
                  <v-icon
                    :icon="expanded ? 'mdi-chevron-up' : 'mdi-chevron-down'"
                    color="primary"
                  />
                </template>
              </v-expansion-panel-title>

              <!-- 面板內容 - 詳細篩選選項 -->
              <v-expansion-panel-text class="filter-panel-content pa-0 ma-0">
                <v-container fluid class="pa-0">
                  <v-row dense>
                    <!-- 詳細篩選欄位 -->
                    <v-col cols="12">
                      <div class="d-flex align-center mb-3">
                        <v-icon size="small" class="me-2">mdi-filter-outline</v-icon>
                        <span class="text-body-2 font-weight-medium">詳細篩選欄位</span>
                      </div>
                    </v-col>

                    <!-- 申請人姓名 -->
                    <v-col cols="12" md="6">
                      <v-text-field
                        v-model="filterCriteria.applicantName"
                        label="申請人姓名"
                        prepend-icon="mdi-account"
                        density="compact"
                        clearable
                        variant="outlined"
                        persistent-hint
                      />
                    </v-col>

                    <!-- 地段 -->
                    <v-col
                      cols="12"
                      md="6"
                    >
                      <v-text-field
                        v-model="filterCriteria.landSection"
                        label="地段"
                        prepend-icon="mdi-map-marker"
                        density="compact"
                        clearable
                        variant="outlined"
                        persistent-hint
                      />
                    </v-col>

                    <!-- 地號 -->
                    <v-col
                      cols="12"
                      md="6"
                    >
                      <v-text-field
                        v-model="filterCriteria.landNumber"
                        label="地號"
                        prepend-icon="mdi-map-marker-outline"
                        density="compact"
                        clearable
                        variant="outlined"
                        persistent-hint
                      />
                    </v-col>

                    <!-- 案件編號 -->
                    <v-col
                      cols="12"
                      md="6"
                    >
                      <v-text-field
                        v-model="filterCriteria.caseNumber"
                        label="案件編號"
                        prepend-icon="mdi-file-document"
                        density="compact"
                        clearable
                        variant="outlined"
                        persistent-hint
                      />
                    </v-col>

                    <!-- 申請年度範圍 -->
                    <v-col cols="12">
                      <div class="d-flex align-center mb-6">
                        <v-icon
                          size="small"
                          class="me-2"
                        >
                          mdi-calendar-range
                        </v-icon>
                        <span class="text-body-2 font-weight-medium">申請年度範圍</span>
                        <!-- <v-chip size="small" color="info" variant="outlined" class="ms-2">
                          需點擊套用篩選
                        </v-chip> -->
                      </div>
                      <v-row
                        dense
                        class="year-range-inputs pl-2"
                      >
                        <v-col cols="5">
                          <v-text-field
                            v-model.number="filterCriteria.yearStart"
                            label="起始年度"
                            placeholder="97"
                            type="number"
                            :min="97"
                            :max="getCurrentYear()"
                            density="compact"
                            variant="outlined"
                            prefix="民國"
                            suffix="年"
                            hide-details="auto"
                            :rules="[yearStartValidation]"
                          />
                        </v-col>
                        <v-col
                          cols="2"
                          class="d-flex align-center justify-center"
                        >
                          <v-icon color="grey">
                            mdi-arrow-right
                          </v-icon>
                        </v-col>
                        <v-col cols="5">
                          <v-text-field
                            v-model.number="filterCriteria.yearEnd"
                            label="結束年度"
                            placeholder="114"
                            type="number"
                            :min="97"
                            :max="getCurrentYear()"
                            density="compact"
                            variant="outlined"
                            prefix="民國"
                            suffix="年"
                            hide-details="auto"
                            :rules="[yearEndValidation]"
                          />
                        </v-col>
                      </v-row>
                    </v-col>

                    <v-divider class="my-3" />

                    <!-- 操作按鈕 -->
                    <v-row dense>
                      <v-col cols="4">
                        <v-btn
                          variant="text"
                          color="primary"
                          size="large"
                          block
                          rounded="md"
                          @click="resetFilters"
                        >
                          <v-icon class="me-2">
                            mdi-refresh
                          </v-icon>
                          重置
                        </v-btn>
                      </v-col>

                      <v-spacer />

                      <v-col cols="8">
                        <v-btn
                          color="primary"
                          variant="flat"
                          size="large"
                          block
                          rounded="md"
                          :loading="gisLoading"
                          @click="applyFilters"
                        >
                          <v-icon class="me-2">
                            mdi-magnify
                          </v-icon>
                          套用篩選
                        </v-btn>
                      </v-col>
                    </v-row>
                  </v-row>
                </v-container>
              </v-expansion-panel-text>
            </v-expansion-panel>
          </v-expansion-panels>
        </div>

        <!-- 搜尋面板 -->
        <div
          v-if="showSearchPanel"
          class="search-panel"
          :style="{
            left: searchPanelPosition.x + 'px',
            top: searchPanelPosition.y + 'px'
          }"
        >
          <v-card
            class="search-control-panel"
            elevation="8"
            rounded="lg"
          >
            <v-card-title class="d-flex align-center justify-space-between pa-3">
              <div class="d-flex align-center">
                <v-icon size="small" class="me-2">mdi-magnify</v-icon>
                <span class="text-h6">案件搜尋</span>
              </div>
              <v-btn
                icon
                variant="text"
                size="small"
                @click="toggleSearchPanel"
              >
                <v-icon>mdi-close</v-icon>
              </v-btn>
            </v-card-title>
            <v-divider />
            <v-card-text class="pa-3">
              <v-form @submit.prevent="searchCases">
                <v-row dense>
                  <v-col cols="12">
                    <v-text-field
                      v-model="searchCriteria.applicantName"
                      label="申請人姓名"
                      prepend-icon="mdi-account"
                      density="compact"
                      clearable
                      @input="debouncedSearch"
                    />
                  </v-col>
                  <v-col cols="12">
                    <v-text-field
                      v-model="searchCriteria.landSection"
                      label="地段"
                      prepend-icon="mdi-map-marker"
                      density="compact"
                      clearable
                      @input="debouncedSearch"
                    />
                  </v-col>
                  <v-col cols="12">
                    <v-text-field
                      v-model="searchCriteria.caseNumber"
                      label="案件編號"
                      prepend-icon="mdi-file-document"
                      density="compact"
                      clearable
                      @input="debouncedSearch"
                    />
                  </v-col>
                  <v-col cols="12">
                    <v-select
                      v-model="searchCriteria.sourceSystem"
                      :items="availableSourceSystems"
                      label="資料來源"
                      prepend-icon="mdi-database"
                      density="compact"
                      clearable
                      @update:model-value="refreshLayerData"
                    />
                  </v-col>
                  <v-col cols="12">
                    <v-btn
                      @click="refreshLayerData"
                      color="primary"
                      :loading="gisLoading"
                      block
                    >
                      <v-icon>mdi-magnify</v-icon>
                      搜尋
                    </v-btn>
                  </v-col>
                </v-row>
              </v-form>

              <!-- 顯示模式切換 -->
              <v-divider class="my-3" />
              <v-chip-group
                v-model="displayMode"
                mandatory
                selected-class="text-primary"
                class="mb-3"
              >
                <v-chip value="grid" size="small">
                  <v-icon left size="small">mdi-grid</v-icon>
                  格網統計圖
                </v-chip>
                <v-chip value="points" size="small">
                  <v-icon left size="small">mdi-circle</v-icon>
                  點位圖
                </v-chip>
              </v-chip-group>

              <!-- 年度區間篩選 -->
              <div class="mb-3">
                <div class="d-flex align-center mb-2">
                  <v-icon size="small" class="me-2">mdi-calendar-range</v-icon>
                  <span class="text-body-2">申請年度篩選</span>
                </div>
                <v-range-slider
                  v-model="yearRange.current"
                  :min="yearRange.min"
                  :max="yearRange.max"
                  :step="1"
                  thumb-label="always"
                  density="compact"
                  class="mb-2"
                  @update:modelValue="onYearRangeChange"
                >
                  <template #thumb-label="{ modelValue }">
                    民國{{ modelValue }}年
                  </template>
                </v-range-slider>
                <div class="d-flex justify-space-between text-caption text-grey">
                  <span>民國{{ yearRange.current[0] }}年</span>
                  <span>民國{{ yearRange.current[1] }}年</span>
                </div>
              </div>

              <!-- 統計資訊 -->
              <v-divider class="my-3" />
              <div v-if="statistics">
                <v-chip
                  color="info"
                  text-color="white"
                  size="small"
                  class="me-2 mb-2"
                >
                  <v-icon left size="small">mdi-chart-line</v-icon>
                  {{ statistics.total_points?.toLocaleString() }} 筆資料
                </v-chip>
                <v-chip
                  v-if="currentPointCount"
                  color="success"
                  text-color="white"
                  size="small"
                  class="mb-2"
                >
                  <v-icon left size="small">mdi-eye</v-icon>
                  顯示 {{ currentPointCount }} 點位
                </v-chip>
                <v-chip
                  color="orange"
                  text-color="white"
                  size="small"
                  class="mb-2"
                >
                  <v-icon left size="small">mdi-eye-settings</v-icon>
                  {{ displayMode === 'grid' ? '格網統計模式' : '點位模式' }}
                </v-chip>
              </div>
            </v-card-text>
          </v-card>
        </div>

        <!-- 圖層管理面板 -->
        <div
          v-if="showLayersPanel"
          class="layers-panel"
          :style="{
            left: panelPosition.x + 'px',
            top: panelPosition.y + 'px',
            maxWidth: layerPanelMaxWidth
          }"
        >
          <v-card
            class="layer-control-panel"
            :class="{ 'dragging': isDragging }"
            elevation="8"
            rounded="lg"
            :max-height="layerPanelMaxHeight"
            :min-height="layerPanelMinHeight"
            height="auto"
          >
            <v-card-title
              class="d-flex align-center justify-space-between pa-0 draggable-header"
              @mousedown="startDrag"
            >
              <div class="d-flex align-center">
                <v-icon
                  size="small"
                  class="me-2 drag-handle"
                >
                  mdi-drag
                </v-icon>
                <span class="text-h6">圖層管理</span>
              </div>
              <v-btn
                icon
                variant="text"
                size="small"
                @click="toggleLayers"
              >
                <v-icon>mdi-close</v-icon>
              </v-btn>
            </v-card-title>
            <v-divider />
            <v-card-text
              class="pa-0"
              :style="{ maxHeight: layerPanelContentMaxHeight, overflowY: 'auto' }"
            >
              <v-list
                density="compact"
                :max-height="layerPanelContentMaxHeight"
                style="overflow-y: auto;"
              >
                <!-- 底圖圖層區塊 -->
                <v-list-subheader class="text-primary font-weight-bold">
                  底圖圖層
                </v-list-subheader>
                <v-radio-group
                  class="px-1"
                  :model-value="getSelectedBaseLayer()"
                  @update:model-value="selectBaseLayer"
                >
                  <div
                    v-for="(layer, index) in mapLayers.filter(l => l.category === 'baselayer')"
                    :key="`baselayer-${index}`"
                  >
                    <v-list-item class="px-0 py-2">
                      <template #prepend>
                        <v-radio
                          :value="layer.name"
                          color="primary"
                          class="pr-5"
                          density="compact"
                          hide-details
                        />
                      </template>

                      <v-list-item-title class="text-body-2 font-weight-medium">
                        {{ layer.name }}
                      </v-list-item-title>
                    </v-list-item>

                    <!-- 透明度控制滑桿 - 放在圖層名稱下方 -->
                    <div
                      v-if="layer.visible"
                      class="opacity-control-section px-0 pb-2"
                    >
                      <div class="d-flex align-center">
                        <span class="opacity-label me-2">透明度:</span>
                        <v-slider
                          v-model="layer.opacity"
                          class="opacity-slider flex-grow-1"
                          :min="0"
                          :max="1"
                          :step="0.01"
                          thumb-label
                          density="compact"
                          hide-details
                          @update:model-value="updateLayerOpacity(layer)"
                        >
                          <template #thumb-label="{ modelValue }">
                            {{ Math.round(modelValue * 100) }}%
                          </template>
                        </v-slider>
                      </div>
                    </div>
                  </div>
                </v-radio-group>

                <v-divider class="my-2" />

                <!-- 疊加圖層區塊 -->
                <v-list-subheader class="text-secondary font-weight-bold">
                  疊加圖層
                </v-list-subheader>
                <div
                  v-for="(layer, index) in mapLayers.filter(l => l.category === 'overlay')"
                  :key="`overlay-${index}`"
                >
                  <v-list-item class="px-3 py-2">
                    <template #prepend>
                      <v-switch
                        v-model="layer.visible"
                        color="primary"
                        class="pr-5"
                        density="compact"
                        hide-details
                        @update:model-value="toggleLayerVisibility(layer)"
                      />
                    </template>

                    <v-list-item-title class="text-body-2 font-weight-medium">
                      {{ layer.name }}
                    </v-list-item-title>
                  </v-list-item>

                  <!-- 透明度控制滑桿 - 放在圖層名稱下方 -->
                  <div
                    v-if="layer.visible"
                    class="opacity-control-section px-0 pb-2"
                  >
                    <div class="d-flex align-center">
                      <span class="opacity-label me-2">透明度:</span>
                      <v-slider
                        v-model="layer.opacity"
                        class="opacity-slider flex-grow-1"
                        :min="0"
                        :max="1"
                        :step="0.01"
                        thumb-label
                        density="compact"
                        hide-details
                        @update:model-value="updateLayerOpacity(layer)"
                      >
                        <template #thumb-label="{ modelValue }">
                          {{ Math.round(modelValue * 100) }}%
                        </template>
                      </v-slider>
                    </div>
                  </div>

                  <!-- 分隔線 -->
                  <v-divider
                    v-if="index < mapLayers.filter(l => l.category === 'overlay').length - 1"
                  />
                </div>
              </v-list>
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
                      <v-icon size="40" class="mb-0">mdi-layers</v-icon>
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
                  :title="'我的位置'"
                  class="control-btn-vertical"
                  size="large"
                  variant="text"
                  rounded="lg"
                  @click="getCurrentLocation"
                >
                  <template #default>
                    <div class="d-flex flex-column align-center">
                      <v-icon size="40" class="mb-0">mdi-crosshairs-gps</v-icon>
                      <span class="btn-text">定位</span>
                    </div>
                  </template>
                </v-btn>
              </v-col>
            </v-row>
            <v-divider />

            <!-- 展繪按鈕 -->
            <v-row class="ma-0">
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
                      <v-icon size="40" class="mb-0">mdi-draw</v-icon>
                      <span class="btn-text">展繪</span>
                    </div>
                  </template>
                </v-btn>
              </v-col>
            </v-row>
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
                      <v-icon size="40" class="mb-0">mdi-ruler</v-icon>
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
                      <v-icon size="40" class="mb-0">mdi-plus</v-icon>
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
                      <v-icon size="40" class="mb-0">mdi-minus</v-icon>
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
                      <v-icon size="40" class="mb-0">mdi-home</v-icon>
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
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick, watch, onUnmounted, computed, toRaw } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useGisStore } from '@/stores/gis';
import { storeToRefs } from 'pinia';
import 'ol/ol.css';
import Map from 'ol/Map';
import View from 'ol/View';
import {defaults as defaultControls} from 'ol/control/defaults.js';
import ScaleLine from 'ol/control/ScaleLine.js';
import TileLayer from 'ol/layer/Tile';
import VectorLayer from 'ol/layer/Vector';
import VectorSource from 'ol/source/Vector';
import Cluster from 'ol/source/Cluster';
// import { Heatmap as HeatmapLayer } from 'ol/layer'; // 註解熱區圖
import { Polygon } from 'ol/geom';
import OSM from 'ol/source/OSM';
import StadiaMaps from 'ol/source/StadiaMaps';
import TileWMS from 'ol/source/TileWMS';
import { fromLonLat, toLonLat } from 'ol/proj';
import { Style, Fill, Stroke, Circle, Text } from 'ol/style';
import { Point } from 'ol/geom';
import { Feature } from 'ol';
import GeoJSON from 'ol/format/GeoJSON';
import type { LocationQueryValue } from 'vue-router';
import type { GeoJsonFeature, GeoJsonFeatureCollection } from '@/types/gis';
import {
  applyFrontendFilters,
  testFrontendFilters,
  getInitialOverlayLoadingParams as getInitialParams,
  type FilterCriteria
} from '@/utils/frontendFilters';

// 定義圖層介面
interface MapLayer {
  name: string;
  visible: boolean;
  opacity: number;
  category: 'baselayer' | 'overlay'; // 新增圖層類別
  layer: any | null; // OpenLayers 類型過於複雜，暫時使用 any
}

const router = useRouter();
const route = useRoute();

// 使用 GIS Store
const gisStore = useGisStore();
const {
  statistics,
  loading: gisLoading,
  displayMode,
  yearRange,
  currentPointCount,
  availableSourceSystems,
} = storeToRefs(gisStore);

// 定義地圖變數，使用具體的 Map 型別
let map: Map | null = null;
const isFluid = ref(false);
const mapContainer = ref(null);
const showSnackbar = ref(false);
const snackbarMessage = ref('');
const isDrawing = ref(false);
const isMeasuring = ref(false);
const showLayersPanel = ref(false);

// 圖層面板拖拽相關
const isDragging = ref(false);
const dragOffset = ref({ x: 0, y: 0 });

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

// 圖層面板高度控制 - 使用 computed 屬性實現響應式
const layerPanelMaxHeight = computed(() => {
  if (typeof window === 'undefined') return '400px';

  const viewportHeight = window.innerHeight;
  const safeMargin = 120;
  const maxHeight = Math.min(viewportHeight - safeMargin, 600);

  return `${maxHeight}px`;
});

const layerPanelMinHeight = computed(() => {
  if (typeof window === 'undefined') return '200px';

  const viewportHeight = window.innerHeight;

  // 根據視窗高度調整最小高度
  if (viewportHeight < 600) {
    return '150px';
  } else if (viewportHeight < 800) {
    return '200px';
  } else {
    return '250px';
  }
});

// 圖層面板內容區域最大高度
const layerPanelContentMaxHeight = computed(() => {
  if (typeof window === 'undefined') return '300px';

  const viewportHeight = window.innerHeight;
  const safeMargin = 180; // 包含標題欄和按鈕的高度
  const maxHeight = Math.min(viewportHeight - safeMargin, 500);

  return `${maxHeight}px`;
});

// 圖層面板最大寬度
const layerPanelMaxWidth = computed(() => {
  if (typeof window === 'undefined') return '350px';

  const viewportWidth = window.innerWidth;

  // 根據視窗寬度調整面板寬度
  if (viewportWidth < 768) {
    return `${Math.min(viewportWidth - 40, 300)}px`;
  } else if (viewportWidth < 1024) {
    return '320px';
  } else {
    return '350px';
  }
});

// 圖層管理相關
const mapLayers = ref<MapLayer[]>([
  {
    name: '臺灣通用電子地圖',
    visible: true,
    opacity: 1,
    category: 'baselayer',
    layer: null
  },
  {
    name: '開放街圖 (OpenStreetMap)',
    visible: false,
    opacity: 1,
    category: 'baselayer',
    layer: null
  },
  {
    name: '水彩風格底圖',
    visible: false,
    opacity: 1,
    category: 'baselayer',
    layer: null
  },
  {
    name: '補助案件格網統計圖',
    visible: true,
    opacity: 0.8,
    category: 'overlay',
    layer: null
  },
  {
    name: '補助案件點位',
    visible: false,
    opacity: 1,
    category: 'overlay',
    layer: null
  },
]);

// GIS 補助案件相關
const showSearchPanel = ref(false);
const grantPointsLayer = ref<VectorLayer | null>(null);
// const grantHeatmapLayer = ref<HeatmapLayer | null>(null); // 註解熱區圖
const grantGridLayer = ref<VectorLayer | null>(null); // 新增格網圖層

// 搜尋面板位置
const searchPanelPosition = ref({ x: 10, y: 10 });

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
// 篩選工具欄狀態
const expandedPanel = ref<string[]>([]);
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

// 年度輸入驗證規則
const yearStartValidation = (value: number) => {
  if (!value) return '請輸入起始年度';
  if (value < 97) return '年度不可小於民國97年';
  if (value > getCurrentYear()) return `年度不可大於民國${getCurrentYear()}年`;
  if (filterCriteria.value.yearEnd && value > filterCriteria.value.yearEnd) {
    return '起始年度不可大於結束年度';
  }
  return true;
};

const yearEndValidation = (value: number) => {
  if (!value) return '請輸入結束年度';
  if (value < 97) return '年度不可小於民國97年';
  if (value > getCurrentYear()) return `年度不可大於民國${getCurrentYear()}年`;
  if (filterCriteria.value.yearStart && value < filterCriteria.value.yearStart) {
    return '結束年度不可小於起始年度';
  }
  return true;
};

// 資料來源選項
const filterSourceOptions = [
  { title: '全部', value: null },
  { title: '新系統案件', value: 'new_aerc' },
  { title: '歷史案件', value: 'legacy_farmdata' }
];

// 防抖計時器
let filterTimeout: ReturnType<typeof setTimeout>;

// 檢查是否有啟用的篩選條件
const hasActiveFilters = computed(() => {
  return !!(
    quickFilter.value ||
    filterCriteria.value.applicantName ||
    filterCriteria.value.landSection ||
    filterCriteria.value.landNumber ||
    filterCriteria.value.caseNumber ||
    filterCriteria.value.sourceSystem ||
    filterCriteria.value.yearStart !== getCurrentYear() ||
    filterCriteria.value.yearEnd !== getCurrentYear()
  );
});

// 用於追蹤地圖是否已完全初始化
const mapInitialized = ref(false);

// 用於防止縮放事件循環
const isAutoZooming = ref(false);
const isProgrammaticZoom = ref(false);

// 用於追蹤已載入的原始資料，供前端篩選使用
const allLoadedFeatures = ref<GeoJsonFeature[]>([]);
const filteredFeatures = ref<GeoJsonFeature[]>([]);

// 切換 fluid 狀態的方法
const toggleFluid = () => {
  isFluid.value = !isFluid.value;
  // 保存用戶偏好到 localStorage
  localStorage.setItem('preferFluid', String(isFluid.value));

  // 在布局變化後更新地圖大小
  nextTick(() => {
    setTimeout(() => {
      if (map) {
        map.updateSize();
      }
    }, 100);
  });
};

const toggleLayers = () => {
  showLayersPanel.value = !showLayersPanel.value;
};

const toggleSearchPanel = async () => {
  showSearchPanel.value = !showSearchPanel.value;
  if (showSearchPanel.value && !statistics.value) {
    try {
      await gisStore.loadStatistics();
    } catch (error) {
      console.error('載入統計資料失敗:', error);
      showError('載入統計資料失敗');
    }
  }
};

// 圖層面板拖拽功能
const startDrag = (event: MouseEvent) => {
  isDragging.value = true;

  // 計算滑鼠相對於面板當前位置的偏移量
  dragOffset.value = {
    x: event.clientX - panelPosition.value.x,
    y: event.clientY - panelPosition.value.y
  };

  // 添加全局監聽器
  document.addEventListener('mousemove', onDrag);
  document.addEventListener('mouseup', stopDrag);

  // 防止文字選擇
  event.preventDefault();
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

// 圖層可見性切換 (僅處理疊加圖層)
const toggleLayerVisibility = (layer: MapLayer) => {
  console.log('切換疊加圖層:', layer.name, '可見性:', layer.visible);

  // 只處理疊加圖層，底圖圖層有專門的函數處理
  if (layer.category === 'overlay') {
    // 處理補助案件圖層的特殊邏輯
    if (layer.name === '補助案件格網統計圖') {
      // 切換到格網統計模式
      if (layer.visible) {
        displayMode.value = 'grid';
        mapLayers.value[4].visible = false; // 關閉點位圖層
      }
    } else if (layer.name === '補助案件點位') {
      // 切換到點位模式
      if (layer.visible) {
        displayMode.value = 'points';
        mapLayers.value[3].visible = false; // 關閉格網圖層
      }
    }

    // 更新圖層可見性
    updateLayerVisibility();

    console.log('疊加圖層', layer.name, '已設置為:', layer.visible ? '可見' : '隱藏');
  } else {
    console.warn('toggleLayerVisibility 僅用於疊加圖層，底圖圖層請使用 selectBaseLayer');
  }
};

// 更新圖層透明度
const updateLayerOpacity = (layer: MapLayer) => {
  if (layer.layer) {
    layer.layer.setOpacity(layer.opacity);
  }
};

// 獲取當前選中的底圖圖層名稱
const getSelectedBaseLayer = (): string => {
  const selectedLayer = mapLayers.value.find(layer =>
    layer.category === 'baselayer' && layer.visible
  );
  return selectedLayer ? selectedLayer.name : '';
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

// 舊的 toggleBaseLayer 函數 (保留以備不時之需)
const toggleBaseLayer = (selectedLayer: MapLayer) => {
  selectBaseLayer(selectedLayer.name);
};

// 定位功能
const getCurrentLocation = () => {
  if (!navigator.geolocation) {
    snackbarMessage.value = '您的瀏覽器不支援定位功能';
    showSnackbar.value = true;
    return;
  }

  navigator.geolocation.getCurrentPosition(
    (position) => {
      if (!map) return;

      const { longitude, latitude } = position.coords;
      const center = fromLonLat([longitude, latitude]);

      map.getView().animate({
        center: center,
        zoom: 16,
        duration: 1000
      });

      snackbarMessage.value = '已定位到您的位置';
      showSnackbar.value = true;
    },
    (error) => {
      console.error('定位失敗:', error);
      snackbarMessage.value = '定位失敗，請檢查位置權限設定';
      showSnackbar.value = true;
    },
    {
      enableHighAccuracy: true,
      timeout: 10000,
      maximumAge: 300000
    }
  );
};

// 展繪功能
const toggleDraw = () => {
  isDrawing.value = !isDrawing.value;
  if (isMeasuring.value) {
    isMeasuring.value = false;
  }

  console.log('展繪工具:', isDrawing.value ? '啟用' : '停用');
  snackbarMessage.value = isDrawing.value ? '展繪工具已啟用' : '展繪工具已停用';
  showSnackbar.value = true;

  // TODO: 實作繪圖功能
};

// 量測功能
const toggleMeasure = () => {
  isMeasuring.value = !isMeasuring.value;
  if (isDrawing.value) {
    isDrawing.value = false;
  }

  console.log('量測工具:', isMeasuring.value ? '啟用' : '停用');
  snackbarMessage.value = isMeasuring.value ? '量測工具已啟用' : '量測工具已停用';
  showSnackbar.value = true;

  // TODO: 實作測量功能
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

// 更新圖層可見性
const updateLayerVisibility = () => {
  if (grantPointsLayer.value && grantGridLayer.value) {
    if (displayMode.value === 'grid') {
      grantGridLayer.value.setVisible(mapLayers.value[3].visible);
      grantPointsLayer.value.setVisible(false);
      mapLayers.value[3].name = '補助案件格網統計圖';
      mapLayers.value[4].visible = false;

      // 確保格網圖層有資料
      const gridSource = grantGridLayer.value.getSource();
      if (gridSource && gridSource.getFeatures().length === 0) {
        console.log('[格網圖層] 切換到格網模式，觸發資料載入');
        // 觸發載入
        gridSource.refresh();
      }
    } else {
      grantGridLayer.value.setVisible(false);
      grantPointsLayer.value.setVisible(mapLayers.value[4].visible);
      mapLayers.value[4].name = '補助案件點位';
      mapLayers.value[3].visible = false;
    }
  }
};

// 顯示錯誤訊息
const showError = (message: string) => {
  snackbarMessage.value = message;
  showSnackbar.value = true;
};

// === 新增：篩選工具欄方法 ===

// 篩選工具欄 Focus 事件
const onFilterFocus = () => {
  // 當快速篩選獲得焦點時，自動展開面板
  if (!expandedPanel.value.includes('filter')) {
    expandedPanel.value = ['filter'];
  }
};

// 篩選工具欄 Blur 事件
const onFilterBlur = () => {
  // 不自動收合，讓用戶手動控制
};

// 快速篩選變更處理(前端篩選)
const onQuickFilterChange = () => {
  console.log('快速篩選變更:', quickFilter.value);

  // 使用防抖機制
  clearTimeout(filterTimeout);
  filterTimeout = setTimeout(() => {
    applyFrontendFilter();
  }, 300); // 更短的延遲時間，提升使用者體驗
};

// 年度輸入變更處理
const onYearInputChange = () => {
  // 確保年度值是有效的數字
  if (filterCriteria.value.yearStart && filterCriteria.value.yearEnd) {
    // 如果起始年度大於結束年度，自動調整結束年度
    if (filterCriteria.value.yearStart > filterCriteria.value.yearEnd) {
      filterCriteria.value.yearEnd = filterCriteria.value.yearStart;
    }
  }

  // 確保年度值在有效範圍內
  const currentYear = getCurrentYear();
  if (filterCriteria.value.yearStart) {
    filterCriteria.value.yearStart = Math.max(97, Math.min(currentYear, filterCriteria.value.yearStart));
  }
  if (filterCriteria.value.yearEnd) {
    filterCriteria.value.yearEnd = Math.max(97, Math.min(currentYear, filterCriteria.value.yearEnd));
  }

  debouncedFilterUpdate();
};

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

// 防抖篩選更新
const debouncedFilterUpdate = () => {
  clearTimeout(filterTimeout);
  filterTimeout = setTimeout(() => {
    applyFrontendFilter();
  }, 300);
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
      let combinedCriteria = { ...filterCriteria.value };

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

  if (!grantPointsLayer.value || !grantHeatmapLayer.value) {
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
    const clusterSource = grantPointsLayer.value.getSource() as Cluster;
    const baseSource = clusterSource?.getSource();
    if (baseSource) {
      baseSource.clear();

      try {
        const geoJSONFormat = new GeoJSON();
        const features = geoJSONFormat.readFeatures(filteredGeoJson, {
          featureProjection: 'EPSG:3857'
        });

        baseSource.addFeatures(features);
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

        baseSource.addFeatures(features);
        console.log(`點位圖層已更新（手動方式），載入 ${features.length} 個點位`);
      }
    }
  }

  // 強制重新渲染地圖
  if (map) {
    map.render();
  }
};


// 搜尋時更新圖層可見性
// eslint-disable-next-line @typescript-eslint/no-unused-vars
const updateLayerVisibilityForSearch = () => {
  console.log('更新搜尋時的圖層可見性');

  // 隱藏熱區圖層，顯示點位圖層
  if (grantHeatmapLayer.value && grantPointsLayer.value) {
    grantHeatmapLayer.value.setVisible(false);
    grantPointsLayer.value.setVisible(true);

    // 更新圖層管理面板的狀態
    mapLayers.value[3].visible = false; // 熱區圖層
    mapLayers.value[4].visible = true;  // 點位圖層

    console.log('圖層可見性已更新：熱區圖層隱藏，點位圖層顯示');
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

// 顯示案件詳細資訊彈出視窗（簡化版）
const showGrantPopup = (coordinate: number[], properties: Record<string, unknown>) => {
  let info: string

  if (properties.cluster) {
    // 聚合點位資訊
    const systemType = properties.source_system === 'new_aerc' ? '新系統案件' : '歷史案件'
    info = `📍 聚合點位 (${systemType})
📊 包含案件數: ${properties.point_count}
📅 年度範圍: 民國${properties.year_range}年
 縮放等級: ${properties.zoom_level}

💡 放大地圖可查看詳細的個別點位`
  } else {
    // 個別點位資訊
    const systemType = properties.source_system === 'new_aerc' ? '新系統案件' : '歷史案件'
    info = `📍 ${systemType}
📋 案件編號: ${properties.source_id || '未提供'}
👤 申請人: ${properties.applicant_name || '未提供'}
📍 地段: ${properties.land_section || '未提供'}
📍 地號: ${properties.land_number || '未提供'}
📅 申請年度: 民國${properties.apply_year}年
📊 案件狀態: ${properties.case_status || '未提供'}`
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

onMounted(() => {
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

  // 確保面板位置在視窗尺寸確定後正確設置
  nextTick(() => {
    const rightOffset = 90;
    const topOffset = 10;
    panelPosition.value = {
      x: Math.max(10, window.innerWidth - 300 - rightOffset),
      y: topOffset
    };
  });

  // 確保 CSS 已正確載入
  const link = document.createElement('link');
  link.rel = 'stylesheet';
  link.href = 'https://cdn.jsdelivr.net/npm/ol@v10.5.0/ol.css';
  document.head.appendChild(link);

  // 延遲一點點初始化地圖，確保 DOM 和 CSS 都準備好了
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

    // 創建圖層並關聯到 mapLayers
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
      visible: mapLayers.value[0].visible,
      opacity: mapLayers.value[0].opacity
    });

    const osmLayer = new TileLayer({
      source: new OSM(),
      visible: mapLayers.value[1].visible,
      opacity: mapLayers.value[1].opacity
    });

    const stamenLayer = new TileLayer({
      source: new StadiaMaps({
        layer: 'stamen_watercolor',
        retina: false,
        apiKey: 'fb83ebeb-aba3-4c37-ba97-3107a384e553',
      }),
      visible: mapLayers.value[2].visible,
      opacity: mapLayers.value[2].opacity
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

    const gridLayer = new VectorLayer({
      source: gridVectorSource,
      visible: mapLayers.value[3].visible,
      opacity: mapLayers.value[3].opacity
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

    // 建立 OpenLayers 聚合源
    const clusterSource = new Cluster({
      source: baseVectorSource,
      distance: 50, // 聚合距離（像素）
      minDistance: 20, // 最小聚合距離
    });

    const grantLayer = new VectorLayer({
      source: clusterSource,
      style: (feature) => {
        return createClusterStyle(feature)
      },
      visible: mapLayers.value[4].visible,
      opacity: mapLayers.value[4].opacity
    });

    // 儲存圖層引用
    grantGridLayer.value = gridLayer;
    grantPointsLayer.value = grantLayer;

    const layers = [nlscLayer, osmLayer, stamenLayer, gridLayer, grantLayer];

    // 關聯圖層到 mapLayers 數據結構
    mapLayers.value[0].layer = nlscLayer;
    mapLayers.value[1].layer = osmLayer;
    mapLayers.value[2].layer = stamenLayer;
    mapLayers.value[3].layer = gridLayer;
    mapLayers.value[4].layer = grantLayer;

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

    // 創建地圖
    map = new Map({
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
    });

    // 添加點擊事件處理補助案件點位和格網
    map.on('singleclick', (event) => {
      const features = map!.getFeaturesAtPixel(event.pixel);
      if (features.length > 0) {
        if (displayMode.value === 'points') {
          // 點位模式：處理聚合點位
          const feature = features.find(f => {
            const layer = f.get('layer');
            return layer === grantLayer || !layer; // 補助案件特徵
          });

          if (feature) {
            const properties = feature.getProperties();
            showGrantPopup(event.coordinate, properties);
          }
        } else if (displayMode.value === 'grid') {
          // 格網模式：處理格網統計
          const gridFeature = features.find(f => f.get('gridKey'));
          if (gridFeature) {
            const properties = gridFeature.getProperties();
            showGridPopup(event.coordinate, properties);
          }
        }
      }
    });

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
            const clusterSource = grantPointsLayer.value.getSource() as Cluster;
            const baseSource = clusterSource?.getSource();
            if (baseSource) {
              console.log('[InitMap] 初始化完成，觸發點位圖層資料載入');
              baseSource.refresh();
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
      // 一般載入 - 使用統一的初始載入條件參數
      console.log(`[${layerType}Layer] 執行一般載入（使用統一初始載入條件）`)

      // 獲取統一的初始載入條件
      const initialParams = getInitialOverlayLoadingParams()

      // 強制使用高縮放等級確保後端回傳原始點位而非聚合資料
      const forceHighZoom = Math.max(zoomLevel, 15)
      await gisStore.loadGrantLocations(bbox, forceHighZoom, {
        ...initialParams,
        source_system: searchCriteria.value.sourceSystem as 'new_aerc' | 'legacy_farmdata' | undefined || initialParams.source_system
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
const createClusterStyle = (feature: Feature | import('ol/render/Feature').default) => {
  // 取得聚合內的特徵數量
  const features = feature.get('features') as Feature[]
  const size = features ? features.length : 1

  if (size === 1) {
    // 單一點位樣式
    const singleFeature = features[0]
    const sourceSystem = singleFeature.get('source_system')

    // 根據資料來源設定不同顏色
    const isNewSystem = sourceSystem === 'new_aerc'
    const fillColor = isNewSystem ? '#3498db' : '#e74c3c'
    const strokeColor = isNewSystem ? '#2980b9' : '#c0392b'

    return new Style({
      image: new Circle({
        radius: 8,
        fill: new Fill({
          color: fillColor
        }),
        stroke: new Stroke({
          color: strokeColor,
          width: 2
        })
      })
    });
  } else {
    // 聚合點位樣式
    // 根據聚合數量調整大小和顏色
    let radius = 15;
    let fillColor = '#ff9500';
    let strokeColor = '#e67e00';

    if (size >= 100) {
      radius = 25;
      fillColor = '#e74c3c';
      strokeColor = '#c0392b';
    } else if (size >= 50) {
      radius = 22;
      fillColor = '#f39c12';
      strokeColor = '#d68910';
    } else if (size >= 20) {
      radius = 19;
      fillColor = '#ff9500';
      strokeColor = '#e67e00';
    } else if (size >= 10) {
      radius = 17;
      fillColor = '#ffb74d';
      strokeColor = '#ff9800';
    }

    return new Style({
      image: new Circle({
        radius: radius,
        fill: new Fill({
          color: fillColor
        }),
        stroke: new Stroke({
          color: strokeColor,
          width: 3
        })
      }),
      text: new Text({
        text: size.toString(),
        fill: new Fill({
          color: '#ffffff'
        }),
        stroke: new Stroke({
          color: strokeColor,
          width: 2
        }),
        font: 'bold 14px Arial',
        textAlign: 'center',
        textBaseline: 'middle'
      })
    })
  }
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
    const clusterSource = grantPointsLayer.value.getSource() as Cluster
    clusterSource?.getSource()?.refresh() // Cluster source 需要兩層
  }
}

// === 以下是原有的 GIS 補助案件相關功能（保持向後兼容） ===
</script>

<style>
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

/* 針對不同螢幕尺寸調整 NavBar 高度 */
/* @media (max-width: 960px) {
  .container-full-height {
    height: calc(100vh - 103px);
  }
} */

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
</style>


