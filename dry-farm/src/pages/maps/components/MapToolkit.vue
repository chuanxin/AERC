<template>
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
            @click="$emit('toggle-layers')"
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
            @click="$emit('get-location')"
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
            @click="$emit('toggle-draw')"
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
            @click="$emit('toggle-measure')"
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
            @click="$emit('zoom-in')"
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
            @click="$emit('zoom-out')"
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
            @click="$emit('reset-view')"
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
</template>

<script setup lang="ts">
// 組件props
const props = defineProps<{
  isDrawing: boolean;
  isMeasuring: boolean;
}>();

// 組件事件
defineEmits<{
  'toggle-layers': [];
  'get-location': [];
  'toggle-draw': [];
  'toggle-measure': [];
  'zoom-in': [];
  'zoom-out': [];
  'reset-view': [];
}>();
</script>

<style scoped>
/* 自定義地圖控制按鈕樣式 */
.map-controls {
  position: absolute;
  top: 10px;
  right: 10px;
  z-index: 1000;
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
</style>
