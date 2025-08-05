# AERC Dryfarm 系統 - Windows 部署指引

本指引提供在 Windows 環境下部署 AERC Dryfarm 系統的詳細步驟說明。

## 系統需求

- Windows 10/11 且具備管理員權限
- 網際網路連線（用於下載套件）
- PowerShell 5.1 或更新版本

## 安裝步驟

### 1. 安裝 PowerShell 套件管理

安裝 winget-install 腳本以確保正確的套件管理：

```powershell
Install-Script -Name winget-install
```

### 2. 安裝 Windows Terminal

安裝現代化的 Windows Terminal 以獲得更好的命令列體驗：

```powershell
winget install --id Microsoft.WindowsTerminal -e
```

**注意**：安裝完成後，請重新啟動終端或使用 Windows Terminal 進行後續步驟。

### 3. 安裝 PostgreSQL 17

安裝 PostgreSQL 資料庫伺服器：

```powershell
winget install --id PostgreSQL.PostgreSQL.17 -e
```

**安裝後設定**：
- **預設帳號密碼**：使用者名稱 `postgres` / 密碼 `postgres`
- PostgreSQL 服務會自動啟動
- 資料庫伺服器將在 `localhost:5432` 上運行

**說明**：使用 winget 安裝 PostgreSQL 時，會自動建立預設的超級使用者帳號：
- 使用者名稱：`postgres`
- 密碼：`postgres`

您可以稍後使用以下命令變更密碼：
```powershell
psql -U postgres -c "ALTER USER postgres PASSWORD 'your_new_password';"
```

### 4. 安裝 PostGIS 擴展

1. 開啟 **開始功能表** → **PostgreSQL 17** → **Application Stack Builder**
2. 選擇您的 PostgreSQL 安裝
3. 導航至 **Spatial Extensions**
4. 選擇 **PostGIS**（最新版本）
5. 按照安裝精靈步驟進行
6. 完成 PostGIS 安裝

### 5. 安裝 UV 套件管理器

安裝 UV 以實現快速的 Python 套件管理：

```powershell
winget install --id astral-sh.uv -e
```

**重要**：安裝後請重新啟動 PowerShell/Terminal 以更新 PATH。

### 6. 安裝 Python 3.13

使用 UV 安裝 Python 3.13：

```powershell
uv python install 3.13
```

### 7. 更新 Shell 配置

更新 shell 以識別 UV Python 安裝：

```powershell
uv python update-shell
```

**重要**：執行此步驟後請重新啟動 PowerShell/Terminal。

### 8. 安裝 Node 版本管理器

安裝 NVM for Windows 來管理 Node.js 版本：

```powershell
winget install --id CoreyButler.NVMforWindows -e
```

**重要**：安裝後請重新啟動 PowerShell/Terminal。

### 9. 安裝 Node.js LTS

安裝最新的 LTS 版本 Node.js：

```powershell
nvm install lts
```

### 10. 使用 Node.js LTS

設定已安裝的 LTS 版本為啟用狀態：

```powershell
# 檢查已安裝的版本
nvm list

# 使用 LTS 版本（將 X.X.X 替換為實際版本號）
nvm use X.X.X
```

範例：
```powershell
nvm use 20.11.0
```

### 10.1. 安裝 NSSM 服務管理器

安裝 NSSM (Non-Sucking Service Manager) 以支援 Windows 服務功能：

```powershell
winget install --id NSSM.NSSM -e
```

**重要**：安裝後請重新啟動 PowerShell/Terminal 以更新 PATH。

**說明**：NSSM 是一個優秀的 Windows 服務管理工具，可讓 AERC 系統作為 Windows 服務運行，提供更穩定的生產環境部署。

## AERC 系統部署

### 11. 初始化 AERC 部署

導航至 AERC 部署目錄並執行初始化腳本：

```powershell
# 導航至您的 AERC 專案目錄
cd "C:\path\to\your\AERC\deploy\AERC-Deploy"

# 執行初始化腳本
.\scripts\Init-AERC-Deployment.ps1
```

**此腳本功能**：
- 建立必要的目錄結構
- 透過互動式提示產生 `.env` 配置檔案
- 設定專案環境變數

**需要提供的資訊**：
- 資料庫名稱（用於您的 AERC 應用程式）
- 資料庫使用者名稱（用於您的 AERC 應用程式）
- 資料庫密碼（用於您的 AERC 應用程式）
- API 配置設定

**說明**：這些設定與 PostgreSQL 超級使用者帳號（`postgres/postgres`）是分開的。初始化腳本將協助您建立應用程式專用的資料庫憑證。

### 12. 啟動資料庫

**以管理員身分**執行資料庫設定腳本：

```powershell
# 右鍵點擊 PowerShell → 以系統管理員身分執行
cd "C:\path\to\your\AERC\deploy\AERC-Deploy\scripts"

.\Bootstrap_DB.ps1
```

**此腳本功能**：
- 在系統 PATH 中配置 PostgreSQL CLI 工具
- 使用 PostgreSQL 超級使用者（`postgres`）建立應用程式資料庫和使用者
- 根據 `.env` 檔案建立資料庫使用者和資料庫
- 啟用 PostGIS 擴展
- 驗證資料庫設定

### 13. 啟動 API 服務

啟動 FastAPI 後端服務：

```powershell
cd "C:\path\to\your\AERC\deploy\AERC-Deploy\scripts"

.\Start_API.ps1
```

**互動式選項**：
- 選擇 `n` (預設)：在前台模式運行，適合開發和測試
- 選擇 `y`：安裝為 Windows 服務，適合生產環境

**此腳本功能**：
- 驗證 UV 和 Python 3.13 安裝
- 建立並啟用 Python 虛擬環境
- 安裝 Python 相依套件
- 執行資料庫遷移
- 在 `http://localhost:5000` 啟動 FastAPI 伺服器
- **可選**：安裝為 Windows 服務以實現持久化運行

### 14. 啟動前端開發伺服器

在**新的終端視窗**中，啟動 Vite 開發伺服器：

```powershell
cd "C:\path\to\your\AERC\deploy\AERC-Deploy\scripts"

.\Start_Vite.ps1
```

**互動式選項**：
- 選擇 `n` (預設)：在前台模式運行，適合開發和測試
- 選擇 `y`：安裝為 Windows 服務，適合生產環境

**此腳本功能**：
- 載入環境變數
- 設定共享的 Node.js 模組
- 為高效開發建立 junction 連結
- 在 `http://localhost:3000` 啟動 Vite 開發伺服器
- **可選**：安裝為 Windows 服務以實現持久化運行

### 15. 服務管理（可選）

如果您選擇安裝為 Windows 服務，可使用服務管理腳本：

```powershell
# 檢查所有服務狀態
.\Manage-Services.ps1 -Action status

# 啟動所有服務
.\Manage-Services.ps1 -Action start

# 停止所有服務
.\Manage-Services.ps1 -Action stop

# 重啟所有服務
.\Manage-Services.ps1 -Action restart

# 只管理特定服務
.\Manage-Services.ps1 -Action start -Service api
.\Manage-Services.ps1 -Action restart -Service frontend

# 移除服務
.\Manage-Services.ps1 -Action remove
```

**服務管理功能**：
- 統一管理 API 和前端服務
- 檢查服務運行狀態
- 啟動、停止、重啟服務
- 移除不需要的服務

## 驗證

完成所有步驟後，您應該會有：

1. **資料庫**：PostgreSQL 17 與 PostGIS 擴展正在運行
2. **API 服務**：FastAPI 在 `http://localhost:5000` 運行
3. **前端**：Vite 開發伺服器在 `http://localhost:3000` 運行

### 快速健康檢查

1. **資料庫連線**：
   ```powershell
   # 測試 PostgreSQL 超級使用者連線
   psql -U postgres -h localhost
   
   # 測試應用程式資料庫連線
   psql -U [your_db_user] -d [your_db_name] -h localhost
   ```

2. **API 健康狀態**：
   開啟瀏覽器：`http://localhost:5000/docs`

3. **前端存取**：
   開啟瀏覽器：`http://localhost:3000`

## 故障排除

### 常見問題

1. **PowerShell 執行政策**：
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```

2. **安裝後 PATH 未更新**：
   - 重新啟動 PowerShell/Terminal
   - 如果問題持續，請重新啟動電腦

3. **資料庫連線錯誤**：
   - 驗證 PostgreSQL 服務正在運行
   - 檢查 `.env` 檔案中的資料庫憑證（用於應用程式資料庫）
   - 確保 PostGIS 擴展已正確安裝
   - PostgreSQL 預設超級使用者是 `postgres/postgres`
   - 測試連線：`psql -U postgres -h localhost`

4. **找不到 UV 或 Python**：
   - UV 安裝後重新啟動終端
   - 驗證安裝：`uv --version`
   - 如需要請手動新增至 PATH

5. **Node.js/NPM 問題**：
   - 驗證 NVM 安裝：`nvm version`
   - 列出可用版本：`nvm list`
   - 切換至正確版本：`nvm use [version]`

### 服務疑難排解

1. **服務權限問題**
   - 確保以管理員身分執行 PowerShell
   - 檢查服務帳戶是否有適當權限

2. **環境變數問題**
   - 服務環境變數與互動模式不同
   - 檢查服務配置中的環境變數設定

3. **Port 被佔用問題**
   ```powershell
   # 檢查使用該 port 的程序
   netstat -ano | findstr :5000
   netstat -ano | findstr :5173
   
   # 終止佔用程序（替換 PID）
   taskkill /F /PID <PID>
   ```

### 取得協助

1. 檢查腳本輸出的具體錯誤訊息
2. 驗證所有先決條件已正確安裝
3. 確保在需要時以管理員身分執行 PowerShell
4. 檢查 `.env` 檔案的正確配置

## 目錄結構

成功部署後，您的目錄結構應該如下所示：

```
AERC-Deploy/
├── .env                          # 環境配置
├── app/
│   ├── api/                      # FastAPI 後端
│   └── dry-farm/                 # 前端應用程式
├── runtime/
│   ├── .venv/                    # Python 虛擬環境
│   └── node_modules/             # 共享的 Node.js 模組
└── scripts/
    ├── Init-AERC-Deployment.ps1  # 初始化腳本
    ├── Bootstrap_DB.ps1          # 資料庫設定
    ├── Start_API.ps1             # API 伺服器啟動器
    └── Start_Vite.ps1            # 前端開發伺服器啟動器
```

## 安全注意事項

- 安全地儲存資料庫密碼
- 在提交至版本控制前檢查 `.env` 檔案內容
- 僅在適當的權限下執行資料庫腳本
- 保持您的系統和相依套件更新

## 技術支援

如果在部署過程中遇到問題：

1. **檢查日誌**：仔細閱讀腳本輸出的錯誤訊息
2. **驗證環境**：確保所有必要軟體已正確安裝
3. **權限問題**：確保在需要時使用管理員權限
4. **配置檢查**：驗證 `.env` 檔案的設定是否正確
5. **網路連線**：確保有穩定的網際網路連線用於下載套件

## 效能最佳化建議

1. **SSD 硬碟**：建議在 SSD 上安裝以獲得更好的效能
2. **記憶體**：建議至少 8GB RAM 用於開發環境
3. **防毒軟體**：將專案目錄加入防毒軟體的例外清單
4. **Windows Defender**：考慮將開發目錄加入 Windows Defender 例外

---

**最後更新**：2025年8月  
**AERC 版本**：Windows 部署分支  
**文件版本**：1.1 中文版
