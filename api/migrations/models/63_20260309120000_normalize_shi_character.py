from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        -- 正規化「巿」(U+5DFF) 為「市」(U+5E02)
        -- 部分舊資料輸入時使用外觀相似的錯誤字元，導致郵遞區號無法正確比對
        UPDATE grants
           SET county = REPLACE(county, chr(24063), chr(24066))
         WHERE county LIKE '%' || chr(24063) || '%';

        UPDATE grants
           SET town = REPLACE(town, chr(24063), chr(24066))
         WHERE town LIKE '%' || chr(24063) || '%';

        UPDATE grants
           SET address = REPLACE(address, chr(24063), chr(24066))
         WHERE address LIKE '%' || chr(24063) || '%';
    """


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        -- 無法還原（無法區分哪些原本是錯誤字元）
    """
