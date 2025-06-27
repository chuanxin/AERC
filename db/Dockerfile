FROM postgres:17

# 設置時區
ENV TZ=Asia/Taipei
ENV PGTZ=Asia/Taipei

# 更新套件清單並安裝 PostGIS 及相依套件
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    postgresql-17-postgis-3 \
    postgresql-17-postgis-3-scripts \
    postgis \
    gdal-bin \
    proj-bin \
    && rm -rf /var/lib/apt/lists/*

# 驗證 PostGIS 套件安裝
RUN find /usr -name 'postgis.control' -type f && \
    echo "✅ PostGIS control files found successfully"

# 複製初始化腳本
COPY init-postgis.sql /docker-entrypoint-initdb.d/

# 設置環境變數
ENV POSTGRES_INITDB_ARGS="--encoding=UTF-8 --lc-collate=C --lc-ctype=C"

# 設置語系
RUN localedef -i en_US -c -f UTF-8 -A /usr/share/locale/locale.alias en_US.UTF-8
ENV LANG=en_US.utf8