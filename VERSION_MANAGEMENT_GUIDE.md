# 農業灌溉設施補助申請系統 - 版本管理功能指南

## 🎯 功能概述

本系統實作了完整的版本管理機制，將原本僅儲存於 localStorage 的申請案資料，整合到資料庫中並提供版本控制功能。支援專案建立、編輯、版本變更等完整工作流程。

## 🏗️ 架構設計

### 前端架構
- **Pinia Store**: 統一的狀態管理，整合版本管理功能
- **LocalStorage**: 作為暫存和快取使用
- **版本管理組件**: 提供直觀的版本管理界面
- **API 服務層**: 處理與後端的版本管理 API 通信

### 後端架構
- **GrantVersions 模型**: 儲存版本資料的主要資料表
- **Grants 模型**: 補助申請案件主檔，包含 active_version_id 字段
- **版本管理 API**: 完整的 CRUD 操作和版本比較功能

## 📊 資料流程

### 1. 專案建立流程
```
1. 用戶填寫申請人資料 (Step 1)
2. 資料同時儲存到 API 和 localStorage
3. 繼續填寫其他步驟 (Steps 2-8)
4. 資料儲存到 localStorage
5. 完成後可建立第一個版本
```

### 2. 版本建立流程
```
1. 用戶點擊「建立新版本」
2. 系統收集所有 localStorage 中的步驟資料
3. 資料打包傳送到後端 API
4. 後端建立新版本並計算雜湊值
5. 更新現行版本指標
6. 前端重新載入版本摘要
```

### 3. 版本切換流程
```
1. 用戶選擇特定版本
2. 從資料庫載入版本資料
3. 清空目前表單資料
4. 載入版本資料到表單
5. 切換到「版本檢視」模式
```

## 🔧 實作細節

### 前端關鍵檔案

#### 1. `/src/stores/grants.ts`
- 新增版本管理相關狀態
- 實作版本 CRUD 操作
- 處理 localStorage 與資料庫同步

```typescript
// 新增的版本管理狀態
const versionSummary = ref<GrantVersionSummary | null>(null)
const activeVersion = ref<GrantVersionDetail | null>(null)
const currentVersionMode = ref<'local' | 'database'>('local')

// 主要方法
const createVersionFromLocalData = async (comment?: string)
const switchToVersionMode = async (versionId: number)
const switchToLocalMode = async ()
```

#### 2. `/src/services/grantVersionsService.ts`
- 版本管理 API 服務層
- 處理所有版本相關的 HTTP 請求

#### 3. `/src/pages/grants/components/VersionManager.vue`
- 版本管理主界面組件
- 提供版本列表、建立、比較等功能

### 後端關鍵檔案

#### 1. `/api/src/database/models.py`
```python
class GrantVersions(models.Model):
    grant = fields.ForeignKeyField("models.Grants")
    version = fields.IntField()
    all_steps_data = fields.JSONField()
    all_steps_data_hash = fields.CharField(max_length=64)
    comment = fields.CharField(max_length=255, null=True)
```

#### 2. `/api/src/routes/grant_versions.py`
- 完整的版本管理 API 端點
- 支援版本 CRUD、比較、設定現行版本等功能

#### 3. `/api/src/crud/grant_versions.py`
- 版本管理業務邏輯
- 資料雜湊計算、版本比較演算法

## 📱 使用說明

### 1. 建立新版本

1. 在申請案編輯頁面，找到「版本管理」區塊
2. 點擊「建立新版本」按鈕
3. 在對話框中輸入版本說明（選填）
4. 確認建立，系統會將目前所有步驟資料儲存為新版本

### 2. 檢視版本歷史

1. 點擊「檢視版本列表」按鈕
2. 在版本列表中可以看到：
   - 版本號碼
   - 建立時間
   - 版本說明
   - 建立者
   - 是否為現行版本

### 3. 切換版本檢視

1. 在版本列表中點擊特定版本的「檢視」按鈕
2. 系統會載入該版本的資料到表單中
3. 切換到「版本檢視」模式，此時資料為唯讀

### 4. 設定現行版本

1. 在版本列表中點擊「設為現行」按鈕
2. 該版本會成為案件的現行版本
3. 現行版本會影響後續的資料處理和報告生成

### 5. 版本比較

1. 在版本比較區域選擇兩個版本
2. 點擊「比較」按鈕
3. 系統會顯示兩個版本之間的差異

### 6. 回到編輯模式

1. 在版本檢視模式下，點擊「切換到編輯模式」
2. 系統會重新載入 localStorage 中的資料
3. 回到正常的編輯模式

## ⚠️ 重要注意事項

### 資料同步
- localStorage 與資料庫不會自動同步
- 用戶需要主動建立版本來保存資料到資料庫
- 切換版本模式時會暫時覆蓋 localStorage 資料

### 版本命名
- 版本號碼由系統自動產生（v1, v2, v3...）
- 版本說明是選填的，但建議填寫以便識別

### 權限管理
- 只有建立案件的用戶或管理員可以管理版本
- 刪除版本功能受到嚴格限制（不能刪除現行版本）

### 效能考量
- 版本資料儲存為 JSON 格式，大量版本可能影響效能
- 建議定期清理過時的版本
- 版本比較功能僅適用於資料量適中的情況

## 🚀 未來擴展

### 計劃中的功能
1. **版本標籤**: 為版本添加自定義標籤
2. **版本分支**: 支援從特定版本建立分支
3. **版本合併**: 合併不同分支的變更
4. **版本備份**: 自動備份重要版本
5. **版本權限**: 更細緻的版本存取權限控制

### 技術改進
1. **增量版本**: 只儲存變更的部分，減少儲存空間
2. **版本壓縮**: 對版本資料進行壓縮
3. **快取優化**: 改善版本載入效能
4. **並發控制**: 處理多用戶同時編輯的情況

## 🔍 疑難排解

### 常見問題

#### 1. 版本建立失敗
- 檢查網路連線
- 確認用戶權限
- 檢查資料格式是否正確

#### 2. 版本載入緩慢
- 檢查版本資料大小
- 清理瀏覽器快取
- 檢查伺服器效能

#### 3. 版本資料不一致
- 重新載入頁面
- 清空 localStorage
- 聯絡系統管理員

### 開發者除錯

#### 前端除錯
```javascript
// 檢查版本管理狀態
console.log(grantsStore.versionSummary)
console.log(grantsStore.currentVersionMode)

// 檢查 localStorage 資料
console.log(GrantStorage.getAllGrants())
```

#### 後端除錯
```python
# 檢查版本資料
version = await GrantVersions.get(id=version_id)
print(version.all_steps_data)

# 檢查雜湊值
import hashlib
import json
data_hash = hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()
```

## 📞 技術支援

如有任何問題或建議，請聯絡開發團隊：
- 開發者: [開發者姓名]
- 電子郵件: [support@example.com]
- 文件更新日期: 2025-06-06

---

*本指南會持續更新，請定期查看最新版本。*
