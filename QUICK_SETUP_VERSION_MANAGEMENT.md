# 🚀 版本管理功能 - 快速設置指南

## 📋 前置需求檢查

確保以下組件已正確設置：

✅ **資料庫遷移**
```bash
# 確認 GrantVersions 表已創建
# 檢查 migrations/models/37_20250605042342_add_grant_versions_model_with_grant_relation.py
```

✅ **後端依賴**
- FastAPI 應用程式正在運行
- Tortoise ORM 已正確配置
- 所有路由已註冊

✅ **前端依賴**
- Vue 3 + TypeScript
- Pinia Store
- 相關 API 服務層

## ⚡ 快速啟動步驟

### 1. 後端啟動
```bash
cd /Users/cxin/dev/AERC/api
python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. 前端啟動
```bash
cd /Users/cxin/dev/AERC/dry-farm
npm run dev
# 或
yarn dev
```

### 3. 驗證設置
打開瀏覽器訪問 `http://localhost:3000` 並：
- 登入系統
- 創建或編輯一個申請案
- 查看是否有「版本管理」區域

## 🧪 快速功能測試

### 方法 1：自動化測試
```bash
cd /Users/cxin/dev/AERC
python test_version_management.py
```

### 方法 2：手動測試（5分鐘）
1. **創建申請案**
   - 進入申請案列表
   - 點擊「新增申請案」
   - 填寫申請人資料並儲存

2. **測試版本功能**
   - 進入申請案編輯頁面
   - 展開「版本管理」面板
   - 點擊「建立新版本」
   - 輸入版本說明並確認

3. **驗證版本列表**
   - 展開版本詳細管理
   - 查看版本歷史是否正確顯示
   - 嘗試版本比較功能

## 🔧 常見設置問題

### 問題 1：版本管理組件不顯示
**可能原因：**
- VersionManager.vue 組件未正確導入
- Grants Store 未包含版本管理功能

**解決方案：**
```typescript
// 檢查 edit.vue 是否包含：
import VersionManager from './components/VersionManager.vue'

// 檢查模板中是否有：
<VersionManager />
```

### 問題 2：API 調用失敗
**可能原因：**
- 後端路由未正確註冊
- CORS 設置問題

**解決方案：**
```python
# 確認 main.py 中包含：
from src.routes import grant_versions
app.include_router(grant_versions.router)
```

### 問題 3：版本建立失敗
**可能原因：**
- 用戶權限問題
- 資料格式錯誤

**解決方案：**
```typescript
// 檢查控制台錯誤訊息
// 確認用戶已正確登入
// 驗證 localStorage 中有步驟資料
```

## 📊 功能驗證清單

### 後端 API 驗證
```bash
# 測試建立版本
curl -X POST "http://localhost:8000/grant-versions/from-current/114990010" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"all_steps_data": {"1": {"name": "測試"}}, "comment": "測試版本"}'

# 測試版本列表
curl -X GET "http://localhost:8000/grant-versions/grant/1" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 前端功能驗證
- [ ] 版本管理區域正常顯示
- [ ] 建立版本功能正常運作
- [ ] 版本列表正確載入
- [ ] 版本比較功能正常
- [ ] 模式切換功能正常

## 🎯 核心檔案檢查

確保以下檔案已正確創建/修改：

### 後端檔案
- [ ] `/api/src/database/models.py` - GrantVersions 模型
- [ ] `/api/src/routes/grant_versions.py` - 版本管理路由
- [ ] `/api/src/crud/grant_versions.py` - 版本管理業務邏輯
- [ ] `/api/src/schemas/grant_versions.py` - 版本管理 Schema

### 前端檔案
- [ ] `/dry-farm/src/services/grantVersionsService.ts` - API 服務
- [ ] `/dry-farm/src/stores/grants.ts` - Store 整合
- [ ] `/dry-farm/src/pages/grants/components/VersionManager.vue` - 主組件
- [ ] `/dry-farm/src/pages/grants/components/VersionComparison.vue` - 比較組件
- [ ] `/dry-farm/src/components/ui/LoadingSpinner.vue` - 載入指示器

## 🚨 緊急除錯

如果遇到嚴重問題，請按順序檢查：

1. **資料庫連線**
   ```bash
   # 檢查資料庫是否可連接
   # 確認 GrantVersions 表是否存在
   ```

2. **API 服務**
   ```bash
   # 檢查 FastAPI 是否正常運行
   # 訪問 http://localhost:8000/docs 查看 API 文件
   ```

3. **前端服務**
   ```bash
   # 檢查 Vue 開發伺服器是否正常
   # 查看瀏覽器控制台是否有錯誤
   ```

4. **權限設置**
   ```bash
   # 確認用戶已登入並有適當權限
   # 檢查 JWT Token 是否有效
   ```

## 📞 取得協助

如果仍有問題：

1. **查看詳細文件：** `VERSION_MANAGEMENT_GUIDE.md`
2. **執行測試腳本：** `python test_version_management.py`
3. **檢查控制台輸出** 獲取詳細錯誤信息
4. **聯絡開發團隊** 提供錯誤截圖和日誌

---

**一切準備就緒！開始使用版本管理功能吧！** 🎉

*設置指南更新：2025-06-06*
