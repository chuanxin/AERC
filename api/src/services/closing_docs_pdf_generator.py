"""
結案文件合併 PDF 生成服務

依序合併切結書、領款收據、結案申報書為單一 PDF 檔案
"""
import io
from typing import Any, List, Mapping

import pypdf

from src.services.declaration_pdf_generator import DeclarationPDFGenerator
from src.services.budget_statement_pdf_generator import BudgetStatementPDFGenerator
from src.services.completion_statement_pdf_generator import CompletionStatementPDFGenerator


# 合併順序固定：切結書 → 收據 → 結案申報書（與勾選順序無關）
CLOSING_DOC_KEYS = ("declaration", "receipt", "completion")


class ClosingDocsPDFGenerator:
    def merge_pdfs(self, pdf_bytes_list: List[bytes]) -> bytes:
        """
        使用 pypdf 合併多個 PDF bytes 為單一 PDF

        Args:
            pdf_bytes_list: PDF bytes 列表，依序合併

        Returns:
            合併後的 PDF bytes
        """
        writer = pypdf.PdfWriter()
        for pdf_bytes in pdf_bytes_list:
            reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
            writer.append(reader)
        output = io.BytesIO()
        writer.write(output)
        output.seek(0)
        return output.getvalue()

    def generate_for_grant(self, payloads: Mapping[str, Any]) -> bytes:
        """
        生成單一案件的合併 PDF；字典有哪些鍵，就產生哪些文件（依 CLOSING_DOC_KEYS 固定順序，
        與字典插入順序無關）。未選取的文件不在字典裡，不存在「佔位值」。

        payloads 的值（各文件資料須分別透過對應的 SSOT extract_* 函數準備）：
        - "declaration": declaration_data               ← extract_declaration_data()
        - "receipt":     receipt_data                   ← extract_budget_statement_data()
        - "completion":  四元組，位置即語意（解包順序須與 generate_completion_statement 參數一致）
            [0] receipt_data  ← extract_budget_statement_data()（與 "receipt" 共用同一份）
            [1] land_data     ← extract_completion_statement_data()
            [2] step4_data    ← extract_completion_statement_data()
            [3] step5_data    ← extract_completion_statement_data()

        Raises:
            ValueError: payloads 為空或含 CLOSING_DOC_KEYS 以外的鍵（否則 merge_pdfs([]) 會
                        靜默產出 0 頁 PDF）

        Returns:
            合併後的 PDF bytes
        """
        if not payloads or set(payloads) - set(CLOSING_DOC_KEYS):
            raise ValueError("結案文件選擇不合法：不得為空，且僅接受 declaration／receipt／completion")
        builders = {
            "declaration": lambda p: DeclarationPDFGenerator().generate(p),
            "receipt": lambda p: BudgetStatementPDFGenerator().generate_receipt(p),
            "completion": lambda p: CompletionStatementPDFGenerator().generate_completion_statement(*p),
        }
        parts = [builders[key](payloads[key]) for key in CLOSING_DOC_KEYS if key in payloads]
        return self.merge_pdfs(parts)
