import os
from pathlib import Path

class UploadMappingsConfig:
    """環境配置 - 統一路徑管理"""
    
    def __init__(self):
        self.environment = self._detect_environment()
        self._setup_paths()
        self._setup_file_settings()
    
    def _detect_environment(self) -> str:
        """環境檢測"""
        if os.path.exists("/.dockerenv"):
            return "docker"
        elif os.name == 'nt':  # Windows系統
            return "production"
        else:
            return "development"
        
    def _setup_paths(self):
        """根據環境設置路徑"""
        if self.environment == "production":
            # Windows 部署環境
            self.data_root = Path("C:/AERC-Data")
        elif self.environment == "development":
            # 開發環境 (相對於專案根目錄)
            project_root = Path(__file__).parent.parent.parent.parent
            self.data_root = project_root / "data"
        else:
            # Docker 或其他環境
            self.data_root = Path("/app/data")
        
        # 統一的子目錄結構
        self.uploads_dir = self.data_root / "uploads"
        self.backups_dir = self.data_root / "backups"
        self.temp_dir = self.data_root / "temp"
        
        # 確保目錄存在
        self._ensure_directories()
    
    def _ensure_directories(self):
        """確保目錄存在"""
        for directory in [self.uploads_dir, self.backups_dir, self.temp_dir]:
            directory.mkdir(parents=True, exist_ok=True)
    
    def _setup_file_settings(self):
        """檔案上傳設定"""
        self.max_file_size = int(os.getenv("MAX_FILE_SIZE", "10485760"))
        self.max_files_per_upload = int(os.getenv("MAX_FILES_PER_UPLOAD", "5"))
        self.allowed_extensions = {'.jpg', '.jpeg', '.png', '.pdf', '.doc', '.docx'}
    
    def get_upload_path(self, grant_id: int) -> Path:
        """取得特定案件的上傳目錄"""
        path = self.uploads_dir / "grants" / str(grant_id) / "attachments"
        path.mkdir(parents=True, exist_ok=True)
        return path
    
    def get_absolute_path(self, relative_path: str) -> Path:
        """將相對路徑轉為絕對路徑 - 跨平台相容"""
        # 將Unix風格路徑分隔符轉換為當前系統適用的格式
        normalized_path = relative_path.replace('/', os.sep)
        return self.data_root / normalized_path

# 全域配置實例
settings = UploadMappingsConfig()