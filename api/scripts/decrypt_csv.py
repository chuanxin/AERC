import os
import sys
import json
import base64
import pandas as pd
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

# ================= 設定區 =================
# 你可以從環境變數讀取，或直接在此處填入金鑰（注意勿外流）
DATA_ENCRYPTION_KEY = os.environ.get("DATA_ENCRYPTION_KEY", "your-key")
PREFIX = "ENC:v1:"
# ==========================================


def parse_key(raw: str) -> bytes:
    """解析 32-byte 金鑰 (hex 或 base64)"""
    raw = raw.strip()
    if len(raw) == 64 and all(c in "0123456789abcdefABCDEF" for c in raw):
        return bytes.fromhex(raw)
    padding_needed = (4 - len(raw) % 4) % 4
    return base64.b64decode(raw + "=" * padding_needed)


# 初始化 AESGCM
try:
    key_bytes = parse_key(DATA_ENCRYPTION_KEY)
    if len(key_bytes) != 32:
        raise ValueError(f"金鑰長度不正確：期望 32 bytes，實際 {len(key_bytes)} bytes")
    aesgcm = AESGCM(key_bytes)
except Exception as e:
    print(f"[錯誤] 金鑰初始化失敗: {e}")
    sys.exit(1)


def decrypt_value(val: str) -> str:
    """單一字串解密；若不是 ENC:v1: 開頭或解密失敗則返回原值"""
    if not isinstance(val, str) or not val.startswith(PREFIX):
        return val

    try:
        payload_b64 = val[len(PREFIX):]
        padding_needed = (4 - len(payload_b64) % 4) % 4
        payload = base64.urlsafe_b64decode(payload_b64 + "=" * padding_needed)
        nonce = payload[:12]
        ciphertext_with_tag = payload[12:]
        plaintext_bytes = aesgcm.decrypt(nonce, ciphertext_with_tag, None)
        return plaintext_bytes.decode("utf-8")
    except Exception as exc:
        print(f"[警告] 解密失敗，保留原值: {val[:20]}... 錯誤: {exc}")
        return val


def decrypt_recursive(data):
    """遞迴處理 JSON 結構（支援 dict, list 與字串）"""
    if isinstance(data, dict):
        return {k: decrypt_recursive(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [decrypt_recursive(item) for item in data]
    elif isinstance(data, str):
        # 先嘗試直接解密字串
        decrypted = decrypt_value(data)
        if decrypted != data:
            return decrypted
        # 若原字串是巢狀 JSON 字串，嘗試 parse 後再解密
        stripped = data.strip()
        if (stripped.startswith("{") and stripped.endswith("}")) or (stripped.startswith("[") and stripped.endswith("]")):
            try:
                parsed = json.loads(stripped)
                return json.dumps(decrypt_recursive(parsed), ensure_ascii=False)
            except Exception:
                return data
        return data
    return data


def process_cell(cell):
    """處理單個 CSV 單元格"""
    if pd.isna(cell):
        return cell

    cell_str = str(cell)

    # 1. 如果單元格直接是 ENC:v1:...
    if cell_str.startswith(PREFIX):
        return decrypt_value(cell_str)

    # 2. 如果單元格是 JSON 物件或陣列字串 (常見於 JSONB 欄位匯出)
    stripped = cell_str.strip()
    if (stripped.startswith("{") and stripped.endswith("}")) or (stripped.startswith("[") and stripped.endswith("]")):
        try:
            parsed = json.loads(stripped)
            unpacked = decrypt_recursive(parsed)
            return json.dumps(unpacked, ensure_ascii=False)
        except Exception:
            return cell

    return cell


def decrypt_csv_file(input_file: str, output_file: str):
    print(f"正在讀取檔案: {input_file} ...")
    
    # 嘗試讀取，優先 utf-8-sig (避免繁中 BOM 問題) 或 big5/cp950
    try:
        df = pd.read_csv(input_file, dtype=str, encoding="utf-8-sig")
    except UnicodeDecodeError:
        try:
            df = pd.read_csv(input_file, dtype=str, encoding="utf-8")
        except UnicodeDecodeError:
            df = pd.read_csv(input_file, dtype=str, encoding="cp950")

    print(f"資料筆數: {len(df)} 筆，欄位數: {len(df.columns)}。開始逐格掃描與解密...")

    # 逐格處理（applymap 在舊版 pandas，map 在新版 pandas）
    if hasattr(df, "map"):
        decrypted_df = df.map(process_cell)
    else:
        decrypted_df = df.applymap(process_cell)

    # 匯出為 utf-8-sig，讓 Excel 開啟時中文不會變成亂碼
    decrypted_df.to_csv(output_file, index=False, encoding="utf-8-sig")
    print(f"解密完成！已另存為: {output_file}")


if __name__ == "__main__":
    # 使用方式 1：命令列參數 python decrypt_csv.py input.csv output.csv
    # 使用方式 2：直接修改下列預設檔名
    input_path = sys.argv[1] if len(sys.argv) > 1 else "encrypted_data.csv"
    output_path = sys.argv[2] if len(sys.argv) > 2 else "decrypted_data.csv"

    if not os.path.exists(input_path):
        print(f"[錯誤] 找不到輸入檔案: {input_path}")
    else:
        decrypt_csv_file(input_path, output_path)