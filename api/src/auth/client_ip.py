import ipaddress

from fastapi import Request

from src.database.models import IPWhitelistEntry


def get_client_ip(request: Request) -> str:
    """抽取來源 IP 字串，不驗證格式（格式驗證交給 is_ip_whitelisted）"""
    header_ip = request.headers.get("X-Real-IP", "")
    if header_ip:
        return header_ip
    return request.client.host if request.client else ""


async def is_ip_whitelisted(client_ip: str) -> bool:
    """比對來源 IP 是否命中任一啟用中的白名單網段；判讀失敗一律回傳 False（FR-019 fail-open）"""
    if not client_ip:
        return False
    try:
        ip = ipaddress.ip_address(client_ip)
    except ValueError:
        return False

    async for entry in IPWhitelistEntry.filter(is_active=True):
        try:
            network = ipaddress.ip_network(entry.cidr, strict=True)
        except ValueError:
            continue
        if ip in network:
            return True
    return False
