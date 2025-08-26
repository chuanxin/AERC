from src.config.upload_mappings import settings
from pathlib import Path
import uuid

class FileStorageService:
    """跨平台文件存儲服務"""
    
    def __init__(self):
        self.settings = settings
        self.base_path = settings.uploads_dir
    
    def generate_file_info(self, grant_id: int, filename: str) -> tuple[str, str, str]:
        """
        生成檔案存儲資訊 - 跨平台相容
        Returns: (absolute_path, internal_filename, relative_path)
        """
        # 安全的檔案處理
        original_ext = Path(filename).suffix.lower()
        self._validate_file_extension(original_ext)
        
        # UUID 檔名
        unique_id = str(uuid.uuid4())
        internal_filename = f"{unique_id}{original_ext}"
        
        # 跨平台路徑處理
        grant_upload_dir = settings.get_upload_path(grant_id)
        absolute_path = grant_upload_dir / internal_filename
        
        # 資料庫存儲用相對路徑 (統一使用 /)
        relative_path = f"uploads/grants/{grant_id}/attachments/{internal_filename}"
        
        return str(absolute_path), internal_filename, relative_path
    
    async def save_file(self, file_content: bytes, absolute_path: str) -> str:
        """跨平台檔案保存"""
        file_path = Path(absolute_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 寫入檔案 - Windows/Linux 通用
        with open(file_path, 'wb') as f:
            f.write(file_content)
        
        # 計算校驗和
        import hashlib
        return hashlib.sha256(file_content).hexdigest()
    
    def _validate_file_extension(self, extension: str) -> None:
        """驗證檔案副檔名"""
        if extension not in settings.allowed_extensions:
            allowed = ', '.join(settings.allowed_extensions)
            raise ValueError(f"不支援的檔案格式 {extension}。允許的格式: {allowed}")
    
    def validate_file_size(self, file_size: int) -> None:
        """驗證檔案大小"""
        if file_size > settings.max_file_size:
            max_size_mb = settings.max_file_size // (1024 * 1024)
            raise ValueError(f"檔案過大。最大允許 {max_size_mb}MB")
    
    def get_mime_type(self, filename: str) -> str:
        """根據檔案副檔名取得 MIME 類型"""
        import mimetypes
        mime_type, _ = mimetypes.guess_type(filename)
        return mime_type or "application/octet-stream"
    
    async def delete_file(self, absolute_path: str) -> bool:
        """刪除檔案"""
        try:
            file_path = Path(absolute_path)
            if file_path.exists():
                file_path.unlink()
            return True
        except Exception as e:
            print(f"[ERROR] 刪除檔案失敗 {absolute_path}: {e}")
            return False