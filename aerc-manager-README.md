# AERC - Windows 部署指南

這是 AERC 專案的 Windows 部署分支，專門針對 Windows 作業系統環境進行最佳化。

## 系統需求

- **作業系統**: Windows 10/11
- **PowerShell**: 5.1 或更高版本
- **容器運行時**: 
  - Podman 4.0+ (推薦) 或
  - Docker Desktop

## 快速開始

1. **檢查系統環境**
   ```powershell
   .\aerc-manager-simple.ps1 help
   ```

2. **啟動所有服務**
   ```powershell
   .\aerc-manager-simple.ps1 start
   ```

3. **檢查服務狀態**
   ```powershell
   .\aerc-manager-simple.ps1 status
   ```

4. **首次部署後執行資料庫遷移**
   ```powershell
   podman exec aerc-api-1 aerich upgrade
   ```

## 可用命令

| 命令 | 功能 | 說明 |
|------|------|------|
| `start` | 啟動服務 | 啟動所有 AERC 服務容器 |
| `stop` | 停止服務 | 停止並移除所有容器 |
| `rebuild` | 重建服務 | 停止 → 重建映像 → 重新啟動 |
| `status` | 查看狀態 | 顯示所有容器的運行狀態 |
| `logs [n]` | 查看日誌 | 顯示服務日誌（預設100行）|
| `help` | 顯示幫助 | 顯示所有可用命令 |

## 服務端點

- **前端**: http://localhost:3001
- **API 文檔**: http://localhost:5001/docs
- **資料庫**: localhost:5433

## Windows 特定修改

### 1. PowerShell 管理腳本
- `aerc-manager-simple.ps1`: 主要管理腳本
- 支援 Docker 和 Podman 自動檢測
- 純文字狀態指示器（相容所有終端）

### 2. 前端配置修改
- 禁用 HTTPS 配置（開發環境）
- 移除主機限制，支援本地開發

### 3. 容器支援
- 優先支援 Podman 原生 `podman compose`
- 完整支援 Docker 和 Docker Compose
- 自動檢測可用的容器工具

## 故障排除

### 容器無法啟動
1. 檢查容器運行時是否正常：
   ```powershell
   podman version
   # 或
   docker version
   ```

2. 檢查服務日誌：
   ```powershell
   .\aerc-manager-simple.ps1 logs
   ```

### 前端 SSL 憑證錯誤
已在此分支中修復 - Vite 配置已調整為開發模式，無需 SSL 憑證。

### 資料庫連接問題
確保 `.env` 檔案中的資料庫配置正確，並且已執行遷移：
```powershell
podman exec aerc-api-1 aerich upgrade
```

## 版本管理

- **主分支**: `main` - 原始 Mac/Linux 環境
- **Windows 分支**: `windows-deployment` - Windows 最佳化版本

此分支專門維護 Windows 環境的相容性和最佳化功能。
