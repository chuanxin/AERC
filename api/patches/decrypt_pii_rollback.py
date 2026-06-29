"""
PII 欄位解密回滾腳本

緊急情境用途：將加密格式（ENC:v1:...）的 PII 欄位還原為明文。

⚠️  警告：
  - 此腳本執行後資料庫將恢復明文 PII，安全性保護隨即失效
  - 執行前需確認 DATA_ENCRYPTION_KEY 可用（金鑰即解密前提）
  - 僅在緊急情境（如需立即排除加密問題）才應使用

用法：
  # 只統計加密記錄數，不異動 DB
  python patches/decrypt_pii_rollback.py --dry-run

  # 正式回滾（需 DATA_ENCRYPTION_KEY 已設定於環境變數）
  python patches/decrypt_pii_rollback.py
"""
import argparse
import asyncio
import copy
import hashlib
import json
import logging
import os
import sys

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

DATABASE_URL = os.environ.get("DATABASE_URL", "")
BATCH_SIZE = 100

STEP1_PII_KEYS = {"applicant_name", "applicant_id", "applicant_phone", "applicant_phone2", "address"}


async def _init_db():
    from tortoise import Tortoise
    await Tortoise.init(
        db_url=DATABASE_URL,
        modules={"models": ["src.database.models", "src.database.geo_models", "src.database.audit_models"]},
    )


async def _close_db():
    from tortoise import Tortoise
    await Tortoise.close_connections()


def _calculate_hash(data: dict) -> str:
    serialized = json.dumps(data, ensure_ascii=False, sort_keys=True, default=str)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


async def _batches(total: int):
    offset = 0
    while offset < total:
        yield offset
        offset += BATCH_SIZE


async def count_encrypted() -> dict:
    from src.database.models import Users, Grants, UserRegistration, GrantVersions

    users_enc = 0
    async for batch_start in _batches(await Users.all().count()):
        for u in await Users.all().offset(batch_start).limit(BATCH_SIZE):
            if any(v and v.startswith("ENC:v1:") for v in [u.full_name, u.phone, u.phone_ext, u.mobile] if v):
                users_enc += 1

    grants_enc = 0
    async for batch_start in _batches(await Grants.all().count()):
        for g in await Grants.all().offset(batch_start).limit(BATCH_SIZE):
            if any(v and v.startswith("ENC:v1:") for v in [g.applicant_name, g.applicant_id, g.applicant_phone, g.address] if v):
                grants_enc += 1

    regs_enc = 0
    async for batch_start in _batches(await UserRegistration.all().count()):
        for r in await UserRegistration.all().offset(batch_start).limit(BATCH_SIZE):
            if r.application_reason and r.application_reason.startswith("ENC:v1:"):
                regs_enc += 1

    gv_enc = 0
    async for batch_start in _batches(await GrantVersions.all().count()):
        for gv in await GrantVersions.all().offset(batch_start).limit(BATCH_SIZE):
            steps = (gv.all_steps_data or {}).get("steps", {})
            step1 = steps.get("1", {})
            if any(isinstance(v, str) and v.startswith("ENC:v1:")
                   for k, v in step1.items() if k in STEP1_PII_KEYS):
                gv_enc += 1

    return {"users": users_enc, "grants": grants_enc, "user_registrations": regs_enc, "grant_versions": gv_enc}


async def run_rollback(enc) -> dict:
    from src.database.models import Users, Grants, UserRegistration, GrantVersions

    stats = {
        "users": {"ok": 0, "skip": 0, "fail": 0},
        "grants": {"ok": 0, "skip": 0, "fail": 0},
        "user_registrations": {"ok": 0, "skip": 0, "fail": 0},
        "grant_versions": {"ok": 0, "skip": 0, "fail": 0},
    }

    # ── Users ──
    async for batch_start in _batches(await Users.all().count()):
        for u in await Users.all().offset(batch_start).limit(BATCH_SIZE):
            try:
                changed = False
                for field in ("full_name", "phone", "phone_ext", "mobile"):
                    val = getattr(u, field, None)
                    if val and enc.is_encrypted(val):
                        setattr(u, field, enc.decrypt(val))
                        changed = True
                if changed:
                    await u.save()
                    stats["users"]["ok"] += 1
                else:
                    stats["users"]["skip"] += 1
            except Exception as e:
                logger.error("Users id=%s 失敗: %s", u.id, e)
                stats["users"]["fail"] += 1

    # ── Grants ──
    async for batch_start in _batches(await Grants.all().count()):
        for g in await Grants.all().offset(batch_start).limit(BATCH_SIZE):
            try:
                changed = False
                for field in ("applicant_name", "applicant_id", "applicant_phone", "applicant_phone2", "address"):
                    val = getattr(g, field, None)
                    if val and enc.is_encrypted(val):
                        setattr(g, field, enc.decrypt(val))
                        changed = True
                if changed:
                    await g.save()
                    stats["grants"]["ok"] += 1
                else:
                    stats["grants"]["skip"] += 1
            except Exception as e:
                logger.error("Grants id=%s 失敗: %s", g.id, e)
                stats["grants"]["fail"] += 1

    # ── UserRegistration ──
    async for batch_start in _batches(await UserRegistration.all().count()):
        for r in await UserRegistration.all().offset(batch_start).limit(BATCH_SIZE):
            try:
                if r.application_reason and enc.is_encrypted(r.application_reason):
                    r.application_reason = enc.decrypt(r.application_reason)
                    await r.save()
                    stats["user_registrations"]["ok"] += 1
                else:
                    stats["user_registrations"]["skip"] += 1
            except Exception as e:
                logger.error("UserRegistration id=%s 失敗: %s", r.id, e)
                stats["user_registrations"]["fail"] += 1

    # ── GrantVersions ──
    async for batch_start in _batches(await GrantVersions.all().count()):
        for gv in await GrantVersions.all().offset(batch_start).limit(BATCH_SIZE):
            try:
                if not gv.all_steps_data:
                    stats["grant_versions"]["skip"] += 1
                    continue
                steps = gv.all_steps_data.get("steps", {})
                step1 = steps.get("1", {})
                if not any(isinstance(v, str) and enc.is_encrypted(v)
                           for k, v in step1.items() if k in STEP1_PII_KEYS):
                    stats["grant_versions"]["skip"] += 1
                    continue

                new_all_steps = copy.deepcopy(gv.all_steps_data)
                new_steps = copy.deepcopy(new_all_steps.get("steps", {}))
                new_step1 = dict(new_steps.get("1", {}))
                for key in STEP1_PII_KEYS:
                    val = new_step1.get(key)
                    if val and isinstance(val, str) and enc.is_encrypted(val):
                        new_step1[key] = enc.decrypt(val)
                new_steps["1"] = new_step1
                new_all_steps["steps"] = new_steps

                # hash 基於解密後的明文
                plaintext_hash = _calculate_hash(new_all_steps)
                gv.all_steps_data = new_all_steps
                gv.all_steps_data_hash = plaintext_hash
                await gv.save()
                stats["grant_versions"]["ok"] += 1
            except Exception as e:
                logger.error("GrantVersions id=%s 失敗: %s", gv.id, e)
                stats["grant_versions"]["fail"] += 1

    return stats


async def main():
    parser = argparse.ArgumentParser(description="PII 欄位解密回滾腳本")
    parser.add_argument("--dry-run", action="store_true", help="只統計加密記錄數，不異動資料庫")
    args = parser.parse_args()

    if not DATABASE_URL:
        logger.error("DATABASE_URL 環境變數未設定")
        sys.exit(1)

    if not os.environ.get("DATA_ENCRYPTION_KEY"):
        logger.error("DATA_ENCRYPTION_KEY 環境變數未設定（回滾需要金鑰以解密）")
        sys.exit(1)

    from src.services.data_encryption import DataEncryptionService
    enc = DataEncryptionService()

    await _init_db()
    try:
        if args.dry_run:
            logger.info("=== DRY-RUN 模式：僅統計加密記錄數 ===")
            counts = await count_encrypted()
            for table, count in counts.items():
                logger.info("  %-25s %d 筆已加密", table, count)
        else:
            logger.info("=== 正式回滾：將加密欄位還原為明文 ===")
            stats = await run_rollback(enc)
            for table, s in stats.items():
                logger.info("  %-25s 成功=%d 跳過=%d 失敗=%d", table, s["ok"], s["skip"], s["fail"])
            total_fail = sum(s["fail"] for s in stats.values())
            if total_fail:
                logger.warning("有 %d 筆失敗，請查看日誌", total_fail)
                sys.exit(1)
    finally:
        await _close_db()


if __name__ == "__main__":
    asyncio.run(main())
