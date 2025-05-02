<template>
  <v-card flat class="step0-container pa-6">
    <div class="text-center mb-6">
      <v-avatar size="80" class="mb-4" color="#e3f4f4">
        <v-icon size="40" color="#3ea0a3">mdi-sprout</v-icon>
      </v-avatar>
      <h2 class="text-h4 font-weight-bold mb-2" style="color: #2d8c8f">歡迎使用管路灌溉補助申請系統</h2>
      <p class="text-body-1 text-medium-emphasis mb-6">
        透過本系統，您可以輕鬆申請農業部農田水利署的管路灌溉設施補助
      </p>
    </div>

    <v-row>
      <v-col cols="12" md="6">
        <v-card class="feature-card mb-4 h-100" rounded="lg" flat>
          <v-card-text class="pa-6">
            <div class="d-flex mb-4">
              <v-avatar size="56" color="#e3f4f4" class="mr-4">
                <v-icon size="32" color="#3ea0a3">mdi-water</v-icon>
              </v-avatar>
              <div>
                <h3 class="text-h6 font-weight-bold" style="color: #2d8c8f">補助內容</h3>
                <p class="text-subtitle-2 text-medium-emphasis">
                  符合條件的農地可獲得管路灌溉設施的補助
                </p>
              </div>
            </div>
            <v-list class="bg-transparent pa-0">
              <v-list-item
                v-for="(item, index) in subsidyItems"
                :key="index"
                class="px-0"
                density="comfortable"
              >
                <template #prepend>
                  <v-icon color="#3ea0a3" size="small" class="me-2">mdi-check-circle</v-icon>
                </template>
                <v-list-item-title class="text-body-2">{{ item }}</v-list-item-title>
              </v-list-item>
            </v-list>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" md="6">
        <v-card class="feature-card mb-4 h-100" rounded="lg" flat>
          <v-card-text class="pa-6">
            <div class="d-flex mb-4">
              <v-avatar size="56" color="#e3f4f4" class="mr-4">
                <v-icon size="32" color="#3ea0a3">mdi-file-document-outline</v-icon>
              </v-avatar>
              <div>
                <h3 class="text-h6 font-weight-bold" style="color: #2d8c8f">申請流程</h3>
                <p class="text-subtitle-2 text-medium-emphasis">
                  請依照以下步驟完成申請
                </p>
              </div>
            </div>
            <v-timeline density="compact" align="start" class="steps-timeline">
              <v-timeline-item
                v-for="(step, index) in applicationSteps"
                :key="index"
                dot-color="#3ea0a3"
                size="small"
                class="timeline-item"
              >
                <div class="timeline-content">
                  <p class="text-subtitle-2 font-weight-medium mb-1">
                    <span class="step-number mr-2">{{ index + 1 }}</span>
                    {{ step.title }}
                  </p>
                  <p class="text-caption text-medium-emphasis">{{ step.description }}</p>
                </div>
              </v-timeline-item>
            </v-timeline>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <v-row class="mt-4">
      <v-col cols="12">
        <v-card class="notice-card" flat>
          <v-card-text class="d-flex align-center pa-4">
            <v-icon color="#3ea0a3" class="me-3">mdi-information-outline</v-icon>
            <span class="text-body-2">
              請點擊<strong>下一步</strong>開始申請流程，或查看
              <v-btn
                color="#3ea0a3"
                variant="text"
                density="comfortable"
                class="px-1 mx-1"
                @click="downloadGuide"
              >
                <span class="text-decoration-underline">申請指南</span>
              </v-btn>
              了解更多資訊。
            </span>
          </v-card-text>
        </v-card>

        <div class="text-center mt-8">
          <v-btn
            color="#3ea0a3"
            size="large"
            variant="flat"
            width="200"
            rounded="lg"
            class="start-btn"
            @click="$emit('next-step')"
            elevation="1"
          >
            <span class="font-weight-medium">開始申請</span>
            <v-icon class="ms-2">mdi-arrow-right</v-icon>
          </v-btn>
        </div>
      </v-col>
    </v-row>
  </v-card>
</template>

<script setup lang="ts">
import { ref } from 'vue'

// 補助項目列表
const subsidyItems = [
  '水源調控設施（含水錶、過濾器等）',
  '田間管路（含管材、閥門等）',
  '灌溉管線工程施作費用',
  '其他經檢核認定有補助必要之設施'
]

// 申請流程步驟
const applicationSteps = [
  {
    title: '填寫基本資料',
    description: '提供申請人和聯絡人資訊'
  },
  {
    title: '填寫土地資訊',
    description: '登錄需要補助的農地資訊'
  },
  {
    title: '填寫灌溉調控設施',
    description: '選擇需要的灌溉設施種類'
  },
  {
    title: '填寫田間管路',
    description: '提供田間管路相關資訊'
  },
  {
    title: '安排現場勘查',
    description: '記錄現場勘查和評估結果'
  },
  {
    title: '提交補助申請',
    description: '完成申請並等待審核'
  }
]

// 下載申請指南
const downloadGuide = () => {
  // 實際應用中這裡應該有下載申請指南的邏輯
  console.log('下載申請指南')
}

// 定義事件
defineEmits(['next-step'])
</script>

<style scoped>
.step0-container {
  background-color: transparent !important;
}

.feature-card {
  background-color: rgba(255, 255, 255, 0.8) !important;
  border: 1px solid rgba(62, 160, 163, 0.15);
  transition: all 0.3s ease;
}

.feature-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08) !important;
  background-color: rgba(255, 255, 255, 0.95) !important;
  transform: translateY(-2px);
}

.notice-card {
  background-color: rgba(227, 244, 244, 0.5) !important;
  border: 1px solid rgba(62, 160, 163, 0.2);
  border-radius: 8px;
}

.steps-timeline :deep(.v-timeline-divider__dot) {
  background-color: #e3f4f4 !important;
}

.steps-timeline :deep(.v-timeline-divider__inner-dot) {
  background-color: #3ea0a3 !important;
}

.timeline-item {
  margin-bottom: 16px;
}

.timeline-content {
  background-color: rgba(255, 255, 255, 0.5);
  padding: 8px 12px;
  border-radius: 6px;
  border-left: 2px solid #3ea0a3;
}

.step-number {
  display: inline-block;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background-color: #3ea0a3;
  color: white;
  text-align: center;
  line-height: 20px;
  font-size: 12px;
  font-weight: bold;
}

.start-btn {
  transition: all 0.3s ease;
}

.start-btn:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 12px rgba(62, 160, 163, 0.2) !important;
}
</style>
