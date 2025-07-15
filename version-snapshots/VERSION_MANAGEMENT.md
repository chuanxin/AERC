# AERC 版本管理策略

## 概述

AERC 使用雙版本策略來確保服務的穩定性和可靠性：

### 🛡️ 保守版本 (Conservative)
- **用途**: 生產環境和緊急恢復
- **特點**: 鎖定所有套件到已驗證的穩定版本
- **端口**: 5002
- **Dockerfile**: `Dockerfile.conservative`
- **Requirements**: `requirements-conservative.txt`
- **Docker Compose**: `docker-compose.conservative.yml`

### 🚀 最新版本 (Latest)  
- **用途**: 開發和測試新功能
- **特點**: 使用較新的套件版本
- **端口**: 5001
- **Dockerfile**: `Dockerfile`
- **Requirements**: `requirements-lock.txt`
- **Docker Compose**: `docker-compose.yml`

## 快速使用

### 立即切換到安全版本
```bash
./switch-version.sh safe
```

### 切換到最新版本
```bash
./switch-version.sh latest
```

### 檢查服務狀態
```bash
./switch-version.sh status
```

## 詳細管理

### 創建保守版本快照
當您的系統運行穩定時，創建快照以備未來使用：
```bash
./manage-versions.sh snapshot
```

### 比較版本差異
查看當前版本與保守版本的差異：
```bash
./manage-versions.sh compare
```

### 檢查完整狀態
```bash
./manage-versions.sh status
```

## 使用場景

### 🚨 緊急情況
當最新版本出現問題時：
1. `./switch-version.sh safe` - 立即切換到穩定版本
2. 在端口 5002 上繼續提供服務
3. 調試問題並修復最新版本

### 🔄 日常開發
1. 在最新版本上開發新功能
2. 定期創建穩定版本快照
3. 使用比較功能檢查套件變更

### 📦 套件更新
1. 更新套件後測試功能
2. 如果出現問題，切換到保守版本
3. 修復問題後重新創建快照

## 服務地址

- **保守版本**: http://localhost:5002
  - API 文檔: http://localhost:5002/docs
  - 字體測試: http://localhost:5002/test/check-fonts
  - PDF 測試: http://localhost:5002/test/generate-sample-pdf

- **最新版本**: http://localhost:5001
  - API 文檔: http://localhost:5001/docs
  - 字體測試: http://localhost:5001/test/check-fonts
  - PDF 測試: http://localhost:5001/test/generate-sample-pdf

## 文件結構

```
AERC/
├── manage-versions.sh              # 完整版本管理工具
├── switch-version.sh               # 快速切換工具
├── docker-compose.yml              # 最新版本配置
├── docker-compose.conservative.yml # 保守版本配置
├── version-snapshots/              # 版本快照存檔
└── api/
    ├── Dockerfile                  # 最新版本 Docker 檔案
    ├── Dockerfile.conservative     # 保守版本 Docker 檔案
    ├── requirements.txt            # 基本需求
    ├── requirements-lock.txt       # 最新版本鎖定
    ├── requirements-conservative.txt # 保守版本鎖定
    └── alpine-packages-lock.txt    # 系統套件鎖定
```

## 最佳實踐

1. **定期創建快照**: 每當系統穩定運行時
2. **使用保守版本**: 生產環境推薦使用保守版本
3. **測試後更新**: 在保守版本穩定的前提下測試新版本
4. **保留快照**: 版本快照會自動存檔，不要刪除
5. **監控差異**: 定期檢查版本差異，了解套件變更
