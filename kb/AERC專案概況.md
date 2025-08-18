# AERC專案概況

## 專案概況

- **位置**: `/Users/cxin/dev/AERC/`
- **技術棧**:
    - 前端：Vue.js 3 + TypeScript + Vuetify 3 + Pinia
    - 後端：FastAPI + Tortoise ORM + PostgreSQL 17 + PostGIS 3.5
    - 容器化：Docker Compose

## 核心功能模組

### 1. 補助申請流程（9個步驟）

- Step 0-2: 申請人資料、案件基本資料、土地資料（已完成事件驅動重構）
- Step 3-4: 灌溉調控設施、田間管路配置（材料自動帶入功能）
- Step 5-7: 現場勘查、文件列印、功能測試（含變更設計功能）
- Step 8-9: 佐證文件上傳

### 2. GIS圖台功能

- 整合89,408筆歷史案件資料
- 支援熱區圖、格網統計圖、點位圖多種顯示模式
- 實作篩選工具欄（年度範圍、申請人、地段、案件編號）
- PostGIS空間查詢和聚合優化

### 3. 版本管理系統

- grant_versions資料表管理案件版本
- 「變更設計」功能觸發新版本建立
- 完整的歷史追蹤和版本比對功能

### 4. 最近完成的重要功能

- **批次跨年度處理**：支援多筆案件批次移轉至次年度
- **歷史案件PDF生成**：整合reportlab生成工程預算書
- **混合儲存策略**：localStorage（暫存）+ API（持久化）

## 技術亮點

1. **事件驅動架構**：step1、step2已完成重構，建立標準設計模式
2. **智能材料比對**：step4自動帶入材料功能，支援pipeFittingsStore比對
3. **PostGIS整合**：成功升級PostgreSQL 17 + PostGIS 3.5.3
4. **效能優化**：防抖機制、快取策略、聚合查詢

## 資料規模

- grants表：54,593筆案件記錄
- grant_versions：54,537筆版本記錄
- grant_papers：54,504筆報告資料
- 資料庫總大小：736MB

## 最新開發需求

您最近正在處理：

1. step2.vue多筆土地資料功能
2. 歷史案件報表生成（使用grant_versions的all_steps_data）
3. Windows Server部署準備（從Docker遷移）



