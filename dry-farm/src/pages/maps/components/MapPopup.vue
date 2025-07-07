<template>
  <div class="map-popup-container">
    <v-dialog
      v-model="dialogVisible"
      width="auto"
      max-width="400"
      :retain-focus="false"
    >
      <v-card class="map-popup">
        <v-card-title class="map-popup-title">
          <v-icon
            size="small"
            class="me-2"
            :color="getIconColor"
            left
          >
            {{ getIconName }}
          </v-icon>
          {{ getTitle }}
        </v-card-title>
        <v-divider />
        <v-card-text class="map-popup-content">
          <pre class="map-popup-text">{{ content }}</pre>
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn
            color="primary"
            variant="text"
            @click="dialogVisible = false"
          >
            關閉
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup lang="ts">
// 組件props
const props = defineProps<{
  visible: boolean;
  type: 'point' | 'grid' | 'cluster';
  properties?: Record<string, any>;
}>();

// 組件事件
const emit = defineEmits<{
  'update:visible': [value: boolean];
}>();

// 對話框可見性
const dialogVisible = ref(false);

// 監聽props.visible變化
watch(() => props.visible, (newVisible) => {
  dialogVisible.value = newVisible;
});

// 監聽dialogVisible變化
watch(dialogVisible, (newVisible) => {
  if (newVisible !== props.visible) {
    emit('update:visible', newVisible);
  }
});

// 計算圖標名稱
const getIconName = computed(() => {
  switch (props.type) {
    case 'point':
      return 'mdi-map-marker';
    case 'grid':
      return 'mdi-grid';
    case 'cluster':
      return 'mdi-map-marker-multiple';
    default:
      return 'mdi-information';
  }
});

// 計算圖標顏色
const getIconColor = computed(() => {
  switch (props.type) {
    case 'point':
      return props.properties?.source_system === 'new_aerc' ? 'blue' : 'red';
    case 'grid':
      return 'orange';
    case 'cluster':
      return 'purple';
    default:
      return 'grey';
  }
});

// 計算標題
const getTitle = computed(() => {
  switch (props.type) {
    case 'point':
      return props.properties?.source_system === 'new_aerc' ? '新系統案件' : '歷史案件';
    case 'grid':
      return '格網統計資訊';
    case 'cluster':
      return '聚合點位資訊';
    default:
      return '地圖資訊';
  }
});

// 計算彈出窗口內容
const content = computed(() => {
  if (!props.properties) return '無資料';

  switch (props.type) {
    case 'point':
      return `📋 案件編號: ${props.properties.source_id || '未提供'}
👤 申請人: ${props.properties.applicant_name || '未提供'}
📍 地段: ${props.properties.land_section || '未提供'}
📍 地號: ${props.properties.land_number || '未提供'}
📅 申請年度: 民國${props.properties.apply_year}年
📊 案件狀態: ${props.properties.case_status || '未提供'}`;

    case 'grid':
      const count = Number(props.properties.count) || 0;
      const maxCount = Number(props.properties.maxCount) || 1;
      const percentage = Math.round((count / maxCount) * 100);
      return `📊 此格網內案件數: ${count} 筆
📈 佔最大值比例: ${percentage}%
🏆 全區最大值: ${maxCount} 筆

💡 此格網包含了 ${count} 個補助申請案件`;

    case 'cluster':
      return `📍 聚合點位 (${props.properties.source_system === 'new_aerc' ? '新系統案件' : '歷史案件'})
📊 包含案件數: ${props.properties.point_count}
📅 年度範圍: 民國${props.properties.year_range}年
 縮放等級: ${props.properties.zoom_level}

💡 放大地圖可查看詳細的個別點位`;

    default:
      return '無資料';
  }
});
</script>

<style scoped>
.map-popup-container {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
}

.map-popup {
  border-radius: 8px;
  overflow: hidden;
}

.map-popup-title {
  background-color: rgba(0, 0, 0, 0.03);
  padding: 12px 16px;
  font-size: 1.1rem;
  font-weight: 600;
}

.map-popup-content {
  padding: 16px;
}

.map-popup-text {
  font-family: inherit;
  margin: 0;
  white-space: pre-wrap;
  font-size: 14px;
  line-height: 1.5;
}
</style>
