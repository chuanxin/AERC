"""
結案文件合併 PDF 生成服務

依序合併切結書、領款收據、結案申報書為單一 PDF 檔案
"""
import io
from typing import Dict, Any, List

import pypdf

from src.services.declaration_pdf_generator import DeclarationPDFGenerator
from src.services.budget_statement_pdf_generator import BudgetStatementPDFGenerator
from src.services.completion_statement_pdf_generator import CompletionStatementPDFGenerator


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

    def generate_for_grant(
        self,
        declaration_data: Dict[str, Any],      # SSOT: extract_declaration_data
        receipt_data: Dict[str, Any],           # SSOT: extract_budget_statement_data
        land_data: List[Dict[str, Any]],        # SSOT: extract_completion_statement_data
        step4_data: Dict[str, Any],             # SSOT: extract_completion_statement_data
        step5_data: Dict[str, Any]              # SSOT: extract_completion_statement_data
    ) -> bytes:
        """
        生成單一案件的合併 PDF（切結書 + 收據 + 結案申報書）

        每份子文件使用各自的 SSOT 資料，呼叫端須分別透過對應的 extract_* 函數準備資料：
        - declaration_data: extract_declaration_data()
        - receipt_data:     extract_budget_statement_data()
        - land/step data:   extract_completion_statement_data()

        Returns:
            合併後的 PDF bytes
        """
        declaration_bytes = DeclarationPDFGenerator().generate(declaration_data)
        receipt_bytes = BudgetStatementPDFGenerator().generate_receipt(receipt_data)
        completion_bytes = CompletionStatementPDFGenerator().generate_completion_statement(
            receipt_data, land_data, step4_data, step5_data
        )
        return self.merge_pdfs([declaration_bytes, receipt_bytes, completion_bytes])
