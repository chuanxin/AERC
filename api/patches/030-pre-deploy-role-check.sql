-- 030-account-approval-flow 角色鍵名遷移腳本
-- 部署順序：
--   Step 1. 執行「確認查詢」，確認生產環境現有角色值
--   Step 2. 若有中文值，執行「遷移腳本」
--   Step 3. 再次執行「確認查詢」驗證結果（應全為英文）
--   Step 4. 部署程式碼（permission_service.py 改用英文鍵名）
--
-- ⚠️  CAUTION: 執行前請備份 users 表，或在非峰值時段操作

-- ============================================================
-- Step 1: 確認查詢（先執行此查詢，觀察輸出）
-- ============================================================

SELECT role, COUNT(*) as count
FROM users
GROUP BY role
ORDER BY role;

-- 預期輸出（無中文值）：
--   role   | count
--   -------|------
--   admin  | N
--   manager| N
--   staff  | N
--   user   | N
--
-- 若輸出包含中文（如「系統管理員」），繼續執行 Step 2。
-- 若全為英文，可跳過 Step 2，直接部署程式碼。

-- ============================================================
-- Step 2: 遷移腳本（僅在有中文值時執行）
-- ============================================================

BEGIN;

UPDATE users SET role = 'admin'   WHERE role = '系統管理員';
UPDATE users SET role = 'manager' WHERE role = '管理處主管';
UPDATE users SET role = 'staff'   WHERE role = '業務承辦人';
UPDATE users SET role = 'user'    WHERE role = '一般使用者';

-- 確認無遺漏（此查詢結果應全為英文鍵名）
SELECT role, COUNT(*) as count FROM users GROUP BY role ORDER BY role;

COMMIT;
