from fastapi import HTTPException


class AppError(HTTPException):
    """統一應用例外類別。

    - 4xx：detail 為刻意設計的使用者可讀訊息，全域 handler 直接 pass-through。
    - 5xx：diagnostic 攜帶診斷細節（僅寫入日誌），detail 為通用使用者訊息。

    使用範例::

        # 業務錯誤（4xx）
        raise AppError(404, "案件不存在")
        raise AppError(409, "此帳號已被使用")

        # 系統錯誤（5xx）—— diagnostic 進日誌，用戶只看到 detail
        raise AppError(500, "操作失敗，請稍後再試", diagnostic=str(e))
    """

    def __init__(self, status_code: int, detail: str, diagnostic: str | None = None):
        super().__init__(status_code=status_code, detail=detail)
        self.diagnostic = diagnostic
