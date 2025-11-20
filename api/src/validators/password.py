"""
密碼驗證工具模組

提供可重用的密碼強度驗證函數
"""

import re


def validate_password_strength(password: str) -> str:
    """
    驗證密碼強度（可重用）

    規則：
    1. 至少 8 個字元
    2. 以下 4 項至少符合 3 項：
       - 包含數字
       - 包含英文大寫
       - 包含英文小寫
       - 包含特殊符號

    Args:
        password: 密碼明文

    Returns:
        str: 驗證通過後的密碼

    Raises:
        ValueError: 驗證失敗時拋出，包含具體錯誤訊息
    """
    if len(password) < 8:
        raise ValueError('密碼長度至少需要 8 個字元')

    # 檢查各項條件
    has_digit = any(c.isdigit() for c in password)
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_special = bool(re.search(r'[!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>\/?]', password))

    # 計算符合的項目數
    conditions_met = sum([has_digit, has_upper, has_lower, has_special])

    if conditions_met < 3:
        raise ValueError(
            '密碼需符合以下 4 項中的至少 3 項：包含數字、包含英文大寫、包含英文小寫、包含特殊符號'
        )

    return password


def check_password_requirements(password: str) -> dict:
    """
    檢查密碼是否符合各項要求（用於前端即時反饋）

    Args:
        password: 密碼明文

    Returns:
        dict: 包含各項檢查結果
        {
            "min_length": bool,
            "has_digit": bool,
            "has_upper": bool,
            "has_lower": bool,
            "has_special": bool,
            "types_count": int,
            "character_types_valid": bool
        }
    """
    has_digit = any(c.isdigit() for c in password)
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_special = bool(re.search(r'[!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>\/?]', password))
    types_count = sum([has_digit, has_upper, has_lower, has_special])

    return {
        "min_length": len(password) >= 8,
        "has_digit": has_digit,
        "has_upper": has_upper,
        "has_lower": has_lower,
        "has_special": has_special,
        "types_count": types_count,
        "character_types_valid": types_count >= 3
    }
