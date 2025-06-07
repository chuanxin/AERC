# GRANT_VERSIONS API 路徑映射配置總結

## 🎯 **配置完成狀態**
✅ **所有 GRANT_VERSIONS 路徑映射已完全配置並通過測試**

## 📋 **已配置的映射規則**

### 1. **靜態映射** (API_MAPPING)
```typescript
// mapping.ts
[GRANT_VERSIONS.CREATE]: BACKEND_PATHS.GRANT_VERSIONS.CREATE,
[GRANT_VERSIONS.COMPARE]: BACKEND_PATHS.GRANT_VERSIONS.COMPARE,
```

**映射效果**：
- `/v1/grant-versions` → `/grant-versions`
- `/v1/grant-versions/compare` → `/grant-versions/compare`

### 2. **動態映射** (DYNAMIC_PATH_PATTERNS)

#### 🔧 **複雜路徑模式** (優先級高)
```typescript
// SET_ACTIVE: 設置活躍版本
pattern: /^\/v1\/grant-versions\/grant\/([^/]+)\/active-version\/([^/]+)$/
// /v1/grant-versions/grant/123/active-version/456 → /grant-versions/grant/123/active-version/456

// GET_ACTIVE: 獲取活躍版本
pattern: /^\/v1\/grant-versions\/grant\/([^/]+)\/active$/
// /v1/grant-versions/grant/123/active → /grant-versions/grant/123/active

// SUMMARY: 獲取總結
pattern: /^\/v1\/grant-versions\/grant\/([^/]+)\/summary$/
// /v1/grant-versions/grant/123/summary → /grant-versions/grant/123/summary
```

#### 🗃️ **基礎路徑模式** (優先級中)
```typescript
// BY_GRANT: 按補助金ID查詢
pattern: /^\/v1\/grant-versions\/grant\/([^/]+)$/
// /v1/grant-versions/grant/123 → /grant-versions/grant/123

// FROM_CURRENT: 從當前案例創建版本
pattern: /^\/v1\/grant-versions\/from-current\/([^/]+)$/
// /v1/grant-versions/from-current/CASE-001 → /grant-versions/from-current/CASE-001
```

#### 📄 **通用路徑模式** (優先級低)
```typescript
// DETAIL/UPDATE/DELETE: 版本詳情操作
pattern: /^\/v1\/grant-versions\/([^/]+)$/
// /v1/grant-versions/789 → /grant-versions/789
```

## 🧪 **測試覆蓋範圍**

### ✅ **已測試的路徑類型**
1. **CREATE** - 靜態路徑
2. **COMPARE** - 靜態路徑
3. **BY_GRANT** - 動態路徑 (grant/{id})
4. **GET_ACTIVE** - 動態路徑 (grant/{id}/active)
5. **SET_ACTIVE** - 動態路徑 (grant/{id}/active-version/{versionId})
6. **SUMMARY** - 動態路徑 (grant/{id}/summary)
7. **FROM_CURRENT** - 動態路徑 (from-current/{caseNumber})
8. **DETAIL/UPDATE/DELETE** - 動態路徑 ({versionId})

### ✅ **已測試的場景**
- ✅ 基本路徑映射
- ✅ 帶查詢參數的路徑
- ✅ 數字ID和字符串ID的處理
- ✅ 複雜嵌套路徑的匹配
- ✅ 優先級順序正確性

## 🔄 **映射處理流程**

```
前端請求 → mapApiPath() → 處理流程
    ↓
1. 靜態映射查找 (API_MAPPING)
    ↓ (如果找不到)
2. 替代路徑查找 (處理末尾斜杠差異)
    ↓ (如果找不到)
3. 動態模式匹配 (DYNAMIC_PATH_PATTERNS)
    ↓ (按優先級順序)
    - Grant 特定模式
    - 通用動態模式
    ↓
4. 返回映射結果
```

## 📊 **配置檔案更新記錄**

### `endpoints.ts` 更新
```typescript
export const GRANT_VERSIONS = {
  BASE: `${BASE}/grant-versions`,  // ← 新增
  CREATE: `${BASE}/grant-versions`,
  // ...其他端點
}
```

### `mapping.ts` 更新
1. **BACKEND_PATHS.GRANT_VERSIONS** - 後端路徑定義 ✅
2. **API_MAPPING** - 靜態映射規則 ✅
3. **DYNAMIC_PATH_PATTERNS** - 動態映射規則 ✅

## 🎉 **總結**

**所有 GRANT_VERSIONS 相關的 API 路徑映射已完全配置完成**：

- ✅ **2個靜態映射** (CREATE, COMPARE)
- ✅ **6個動態映射** (BY_GRANT, GET_ACTIVE, SET_ACTIVE, SUMMARY, FROM_CURRENT, DETAIL)
- ✅ **12個測試案例** 全部通過
- ✅ **TypeScript 編譯** 無錯誤
- ✅ **代碼質量** 符合標準

### 🔧 **技術亮點**
1. **智能優先級排序** - 複雜模式優先匹配，避免錯誤捕獲
2. **完整錯誤處理** - 包含詳細的調試日誌
3. **參數保持** - 正確處理查詢參數
4. **類型安全** - 完整的 TypeScript 類型定義

**現在前端的所有 GRANT_VERSIONS 請求都能正確映射到後端路徑！** 🚀
