"""
PII 欄位加密遷移腳本

將 Users、Grants、UserRegistration、GrantVersions 表的 PII 欄位
從明文轉換為 AES-256-GCM 加密格式（ENC:v1:...）。

用法：
  # 只統計待遷移筆數，不異動 DB（不需 DATA_ENCRYPTION_KEY）
  python patches/encrypt_pii_migration.py --dry-run

  # 正式執行（需 DATA_ENCRYPTION_KEY 已設定於環境變數）
  python patches/encrypt_pii_migration.py

安全要求：
  - 執行前必須備妥 DB 備份
  - DATA_ENCRYPTION_KEY 離線副本必須可用（金鑰遺失將導致資料永久無法解密）
  - 建議在維護時間窗口、低流量期間執行
"""
import argparse
import asyncio
import copy
import hashlib
import json
import logging
import os
import sys
from typing import Optional

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

DATABASE_URL = os.environ.get("DATABASE_URL", "")
BATCH_SIZE = 100


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


# ─────────────────────────────────────────────────────────────────────────────
# dry-run: count plaintext records only
# ─────────────────────────────────────────────────────────────────────────────

async def count_pending(dry_run: bool) -> dict:
    from src.database.models import Users, Grants, UserRegistration, GrantVersions

    users_pending = 0
    async for batch_start in _batches(await Users.all().count()):
        batch = await Users.all().offset(batch_start).limit(BATCH_SIZE)
        for u in batch:
            if any(v and not v.startswith("ENC:v1:") for v in [u.full_name, u.phone, u.phone_ext, u.mobile] if v):
                users_pending += 1

    grants_pending = 0
    async for batch_start in _batches(await Grants.all().count()):
        batch = await Grants.all().offset(batch_start).limit(BATCH_SIZE)
        for g in batch:
            if any(v and not v.startswith("ENC:v1:") for v in [g.applicant_name, g.applicant_id, g.applicant_phone, g.address] if v):
                grants_pending += 1

    regs_pending = 0
    async for batch_start in _batches(await UserRegistration.all().count()):
        batch = await UserRegistration.all().offset(batch_start).limit(BATCH_SIZE)
        for r in batch:
            if r.application_reason and not r.application_reason.startswith("ENC:v1:"):
                regs_pending += 1

    gv_pending = 0
    async for batch_start in _batches(await GrantVersions.all().count()):
        batch = await GrantVersions.all().offset(batch_start).limit(BATCH_SIZE)
        for gv in batch:
            steps = (gv.all_steps_data or {}).get("steps", {})
            step1 = steps.get("1", {})
            if any(v and isinstance(v, str) and not v.startswith("ENC:v1:")
                   for k, v in step1.items()
                   if k in {"applicant_name", "applicant_id", "applicant_phone", "applicant_phone2", "address"}):
                gv_pending += 1

    return {
        "users": users_pending,
        "grants": grants_pending,
        "user_registrations": regs_pending,
        "grant_versions": gv_pending,
    }


# ─────────────────────────────────────────────────────────────────────────────
# actual migration
# ─────────────────────────────────────────────────────────────────────────────

async def run_migration(enc) -> dict:
    from src.database.models import Users, Grants, UserRegistration, GrantVersions

    stats = {
        "users": {"ok": 0, "skip": 0, "fail": 0},
        "grants": {"ok": 0, "skip": 0, "fail": 0},
        "user_registrations": {"ok": 0, "skip": 0, "fail": 0},
        "grant_versions": {"ok": 0, "skip": 0, "fail": 0},
    }

    # ── Users ──
    async for batch_start in _batches(await Users.all().count()):
        batch = await Users.all().offset(batch_start).limit(BATCH_SIZE)
        for u in batch:
            try:
                changed = False
                for field in ("full_name", "phone", "phone_ext", "mobile"):
                    val = getattr(u, field, None)
                    if val and not enc.is_encrypted(val):
                        setattr(u, field, enc.encrypt(val))
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
        batch = await Grants.all().offset(batch_start).limit(BATCH_SIZE)
        for g in batch:
            try:
                changed = False
                for field in ("applicant_name", "applicant_id", "applicant_phone", "applicant_phone2", "address"):
                    val = getattr(g, field, None)
                    if val and not enc.is_encrypted(val):
                        setattr(g, field, enc.encrypt(val))
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
        batch = await UserRegistration.all().offset(batch_start).limit(BATCH_SIZE)
        for r in batch:
            try:
                if r.application_reason and not enc.is_encrypted(r.application_reason):
                    r.application_reason = enc.encrypt(r.application_reason)
                    await r.save()
                    stats["user_registrations"]["ok"] += 1
                else:
                    stats["user_registrations"]["skip"] += 1
            except Exception as e:
                logger.error("UserRegistration id=%s 失敗: %s", r.id, e)
                stats["user_registrations"]["fail"] += 1

    # ── GrantVersions ──
    STEP1_PII_KEYS = {"applicant_name", "applicant_id", "applicant_phone", "applicant_phone2", "address"}
    async for batch_start in _batches(await GrantVersions.all().count()):
        batch = await GrantVersions.all().offset(batch_start).limit(BATCH_SIZE)
        for gv in batch:
            try:
                if not gv.all_steps_data:
                    stats["grant_versions"]["skip"] += 1
                    continue
                steps = gv.all_steps_data.get("steps", {})
                step1 = steps.get("1", {})
                if not step1:
                    stats["grant_versions"]["skip"] += 1
                    continue
                needs_encrypt = any(
                    v and isinstance(v, str) and not enc.is_encrypted(v)
                    for k, v in step1.items() if k in STEP1_PII_KEYS
                )
                if not needs_encrypt:
                    stats["grant_versions"]["skip"] += 1
                    continue

                # ① 確認明文狀態，計算 hash（基於明文）
                new_all_steps = copy.deepcopy(gv.all_steps_data)
                plaintext_hash = _calculate_hash(new_all_steps)

                # ② 加密 step1 PII
                new_steps = copy.deepcopy(new_all_steps.get("steps", {}))
                new_step1 = dict(new_steps.get("1", {}))
                for key in STEP1_PII_KEYS:
                    val = new_step1.get(key)
                    if val and isinstance(val, str) and not enc.is_encrypted(val):
                        new_step1[key] = enc.encrypt(val)
                new_steps["1"] = new_step1
                new_all_steps["steps"] = new_steps

                gv.all_steps_data = new_all_steps
                gv.all_steps_data_hash = plaintext_hash
                await gv.save()
                stats["grant_versions"]["ok"] += 1
            except Exception as e:
                logger.error("GrantVersions id=%s 失敗: %s", gv.id, e)
                stats["grant_versions"]["fail"] += 1

    return stats


# ─────────────────────────────────────────────────────────────────────────────
# helpers
# ─────────────────────────────────────────────────────────────────────────────

async def _batches(total: int):
    offset = 0
    while offset < total:
        yield offset
        offset += BATCH_SIZE


async def main():
    parser = argparse.ArgumentParser(description="PII 欄位加密遷移腳本")
    parser.add_argument("--dry-run", action="store_true", help="只統計待遷移筆數，不異動資料庫")
    args = parser.parse_args()

    if not DATABASE_URL:
        logger.error("DATABASE_URL 環境變數未設定")
        sys.exit(1)

    await _init_db()
    try:
        if args.dry_run:
            logger.info("=== DRY-RUN 模式：僅統計，不異動資料庫 ===")
            pending = await count_pending(dry_run=True)
            logger.info("待遷移筆數統計：")
            for table, count in pending.items():
                logger.info("  %-25s %d 筆", table, count)
            total = sum(pending.values())
            logger.info("總計待遷移：%d 筆", total)
        else:
            if not os.environ.get("DATA_ENCRYPTION_KEY"):
                logger.error("DATA_ENCRYPTION_KEY 環境變數未設定（正式執行模式必須）")
                sys.exit(1)
            # 條件式初始化（dry-run 不初始化，正式執行才載入）
            from src.services.data_encryption import DataEncryptionService
            enc = DataEncryptionService()
            logger.info("=== 正式執行：開始加密 PII 欄位 ===")
            stats = await run_migration(enc)
            logger.info("遷移完成，統計結果：")
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
