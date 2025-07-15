#!/bin/bash
# AERC 套件版本管理腳本
# 支援保守版本和最新版本的管理

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
API_DIR="$SCRIPT_DIR/api"

echo "🔒 AERC API 套件版本管理工具"
echo "================================"

# 函數：創建保守版本快照
create_conservative_snapshot() {
    echo "📸 創建保守版本快照..."
    
    if ! docker ps | grep -q aerc-api-1; then
        echo "❌ 錯誤: aerc-api-1 容器未運行"
        echo "請先執行: docker-compose up -d"
        exit 1
    fi
    
    # 備份當前工作的套件版本
    echo "# AERC API 保守版本套件清單" > "$API_DIR/requirements-conservative.txt"
    echo "# 版本鎖定日期: $(date +%Y-%m-%d)" >> "$API_DIR/requirements-conservative.txt"
    echo "# 此檔案包含所有已驗證可正常運行的套件版本" >> "$API_DIR/requirements-conservative.txt"
    echo "# 當新版本套件導致問題時，請使用此檔案" >> "$API_DIR/requirements-conservative.txt"
    echo "" >> "$API_DIR/requirements-conservative.txt"
    
    # 分類整理套件
    echo "# 核心框架" >> "$API_DIR/requirements-conservative.txt"
    docker exec aerc-api-1 pip freeze | grep -E "(aerich|fastapi|tortoise-orm|uvicorn|asyncpg|bcrypt|passlib)" >> "$API_DIR/requirements-conservative.txt"
    
    echo "" >> "$API_DIR/requirements-conservative.txt"
    echo "# PDF 處理套件 (已驗證中文字體支援)" >> "$API_DIR/requirements-conservative.txt"
    docker exec aerc-api-1 pip freeze | grep -E "(pillow|PyMuPDF|pypdf|reportlab)" >> "$API_DIR/requirements-conservative.txt"
    
    echo "" >> "$API_DIR/requirements-conservative.txt"
    echo "# 其他依賴套件" >> "$API_DIR/requirements-conservative.txt"
    docker exec aerc-api-1 pip freeze | grep -v -E "(aerich|fastapi|tortoise-orm|uvicorn|asyncpg|bcrypt|passlib|pillow|PyMuPDF|pypdf|reportlab)" >> "$API_DIR/requirements-conservative.txt"
    
    echo "✅ 保守版本快照已保存到 requirements-conservative.txt"
    
    # 創建版本快照記錄
    local snapshot_file="$SCRIPT_DIR/version-snapshots/$(date +%Y%m%d_%H%M%S)_conservative.txt"
    mkdir -p "$SCRIPT_DIR/version-snapshots"
    cp "$API_DIR/requirements-conservative.txt" "$snapshot_file"
    echo "📁 版本快照已保存到: $snapshot_file"
}

# 函數：比較版本差異
compare_versions() {
    echo "🔍 比較版本差異..."
    
    if [ ! -f "$API_DIR/requirements-conservative.txt" ]; then
        echo "❌ 保守版本檔案不存在，請先創建快照"
        exit 1
    fi
    
    if ! docker ps | grep -q aerc-api-1; then
        echo "❌ 錯誤: aerc-api-1 容器未運行"
        exit 1
    fi
    
    local temp_current=$(mktemp)
    docker exec aerc-api-1 pip freeze > "$temp_current"
    
    echo "📊 版本差異報告:"
    echo "=================="
    
    # 檢查新增的套件
    echo ""
    echo "🆕 新增的套件:"
    diff <(grep -o '^[^=]*' "$API_DIR/requirements-conservative.txt" | sort) <(grep -o '^[^=]*' "$temp_current" | sort) | grep '^>' | sed 's/^> /  /' || echo "  無新增套件"
    
    # 檢查移除的套件
    echo ""
    echo "🗑️  移除的套件:"
    diff <(grep -o '^[^=]*' "$API_DIR/requirements-conservative.txt" | sort) <(grep -o '^[^=]*' "$temp_current" | sort) | grep '^<' | sed 's/^< /  /' || echo "  無移除套件"
    
    # 檢查版本變更
    echo ""
    echo "🔄 版本變更:"
    while IFS= read -r line; do
        if [[ $line =~ ^([^=]+)==(.+)$ ]]; then
            pkg="${BASH_REMATCH[1]}"
            old_ver="${BASH_REMATCH[2]}"
            new_ver=$(grep "^$pkg==" "$temp_current" | cut -d'=' -f3 || echo "")
            if [ -n "$new_ver" ] && [ "$old_ver" != "$new_ver" ]; then
                echo "  $pkg: $old_ver → $new_ver"
            fi
        fi
    done < <(grep -v '^#' "$API_DIR/requirements-conservative.txt" | grep -v '^$')
    
    rm "$temp_current"
}

# 函數：切換到保守版本
switch_to_conservative() {
    echo "🔄 切換到保守版本..."
    
    if [ ! -f "$SCRIPT_DIR/docker-compose.conservative.yml" ]; then
        echo "❌ 保守版本 docker-compose 檔案不存在"
        exit 1
    fi
    
    echo "停止當前服務..."
    docker-compose down || true
    
    echo "啟動保守版本服務..."
    docker-compose -f docker-compose.conservative.yml up -d --build
    
    echo "等待服務啟動..."
    sleep 15
    
    echo "測試保守版本服務..."
    if curl -f http://localhost:5002/test/check-fonts > /dev/null 2>&1; then
        echo "✅ 保守版本服務啟動成功！"
        echo "🌐 服務地址: http://localhost:5002"
        echo "📊 字體檢查: http://localhost:5002/test/check-fonts"
        echo "📄 PDF 測試: http://localhost:5002/test/generate-sample-pdf"
    else
        echo "❌ 保守版本服務啟動失敗！"
        exit 1
    fi
}

# 函數：切換到最新版本
switch_to_latest() {
    echo "🔄 切換到最新版本..."
    
    echo "停止保守版本服務..."
    docker-compose -f docker-compose.conservative.yml down || true
    
    echo "啟動最新版本服務..."
    docker-compose up -d --build
    
    echo "等待服務啟動..."
    sleep 15
    
    echo "測試最新版本服務..."
    if curl -f http://localhost:5001/test/check-fonts > /dev/null 2>&1; then
        echo "✅ 最新版本服務啟動成功！"
        echo "🌐 服務地址: http://localhost:5001"
    else
        echo "❌ 最新版本服務啟動失敗！"
        exit 1
    fi
}

# 函數：顯示服務狀態
show_status() {
    echo "📊 服務狀態報告"
    echo "================"
    
    echo ""
    echo "🐳 Docker 容器狀態:"
    docker ps --format "table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}" | grep -E "(aerc|NAMES)" || echo "無 AERC 相關容器運行"
    
    echo ""
    echo "🌐 服務可用性測試:"
    
    # 測試最新版本
    if curl -f http://localhost:5001/test/check-fonts > /dev/null 2>&1; then
        echo "  ✅ 最新版本 (port 5001): 正常運行"
    else
        echo "  ❌ 最新版本 (port 5001): 無法連接"
    fi
    
    # 測試保守版本
    if curl -f http://localhost:5002/test/check-fonts > /dev/null 2>&1; then
        echo "  ✅ 保守版本 (port 5002): 正常運行"
    else
        echo "  ❌ 保守版本 (port 5002): 無法連接"
    fi
    
    echo ""
    echo "📁 版本檔案狀態:"
    [ -f "$API_DIR/requirements-conservative.txt" ] && echo "  ✅ 保守版本檔案存在" || echo "  ❌ 保守版本檔案不存在"
    [ -f "$SCRIPT_DIR/docker-compose.conservative.yml" ] && echo "  ✅ 保守版本 docker-compose 存在" || echo "  ❌ 保守版本 docker-compose 不存在"
    
    if [ -d "$SCRIPT_DIR/version-snapshots" ]; then
        local snapshot_count=$(ls "$SCRIPT_DIR/version-snapshots"/*.txt 2>/dev/null | wc -l)
        echo "  📸 版本快照數量: $snapshot_count"
    else
        echo "  📸 版本快照數量: 0"
    fi
}

# 函數：更新 Python 套件鎖定檔案
update_python_locks() {
    echo "📦 更新 Python 套件版本鎖定檔案..."
    
    if ! docker ps | grep -q aerc-api-1; then
        echo "❌ 錯誤: aerc-api-1 容器未運行"
        echo "請先執行: docker-compose up -d"
        exit 1
    fi
    
    # 獲取當前套件版本
    docker exec aerc-api-1 pip freeze > "$API_DIR/requirements-lock.txt"
    
    # 添加標頭註釋
    local temp_file=$(mktemp)
    cat > "$temp_file" << EOF
# 完整的套件版本鎖定檔案
# 生成日期: $(date +%Y-%m-%d)
# 用於確保 Docker 構建的可重現性

EOF
    cat "$API_DIR/requirements-lock.txt" >> "$temp_file"
    mv "$temp_file" "$API_DIR/requirements-lock.txt"
    
    echo "✅ Python 套件版本已更新到 requirements-lock.txt"
}

# 函數：更新 Alpine 套件鎖定檔案
update_alpine_locks() {
    echo "🐧 更新 Alpine 套件版本鎖定檔案..."
    
    if ! docker ps | grep -q aerc-api-1; then
        echo "❌ 錯誤: aerc-api-1 容器未運行"
        exit 1
    fi
    
    # 獲取系統套件版本
    docker exec aerc-api-1 apk list --installed | grep -E "(build-base|linux-headers|clang-dev|wqy-zenhei|fontconfig|ttf-dejavu)" | \
    awk '{
        split($1, parts, "-");
        name = parts[1];
        for(i=2; i<length(parts); i++) {
            if(parts[i] !~ /^[0-9]/) {
                name = name "-" parts[i];
            } else {
                break;
            }
        }
        version = "";
        for(j=i; j<=length(parts); j++) {
            if(j==i) version = parts[j];
            else version = version "-" parts[j];
        }
        sub(/ .*/, "", version);
        print name "=" version;
    }' > "$API_DIR/alpine-packages-lock.txt"
    
    # 添加標頭註釋
    local temp_file=$(mktemp)
    cat > "$temp_file" << EOF
# Alpine Linux 套件版本鎖定檔案
# 生成日期: $(date +%Y-%m-%d)
# Alpine 版本: $(docker exec aerc-api-1 cat /etc/alpine-release)
# 用於確保系統套件版本的可重現性

# 編譯工具套件
EOF
    grep -E "(build-base|linux-headers|clang-dev)" "$API_DIR/alpine-packages-lock.txt" >> "$temp_file"
    echo "" >> "$temp_file"
    echo "# 中文字體套件" >> "$temp_file"
    grep -E "(wqy-zenhei|fontconfig|ttf-dejavu)" "$API_DIR/alpine-packages-lock.txt" >> "$temp_file"
    
    mv "$temp_file" "$API_DIR/alpine-packages-lock.txt"
    
    echo "✅ Alpine 套件版本已更新到 alpine-packages-lock.txt"
}

# 函數：顯示當前版本
show_versions() {
    echo "📋 當前套件版本狀態:"
    echo ""
    echo "🐧 Alpine 套件:"
    if [ -f "$API_DIR/alpine-packages-lock.txt" ]; then
        grep -v "^#" "$API_DIR/alpine-packages-lock.txt" | grep -v "^$"
    else
        echo "❌ alpine-packages-lock.txt 不存在"
    fi
    
    echo ""
    echo "🐍 Python 套件數量:"
    if [ -f "$API_DIR/requirements-lock.txt" ]; then
        local count=$(grep -v "^#" "$API_DIR/requirements-lock.txt" | grep -v "^$" | wc -l)
        echo "總計: $count 個套件"
        echo ""
        echo "📦 主要套件:"
        grep -E "(fastapi|tortoise-orm|reportlab|PyMuPDF|pillow)" "$API_DIR/requirements-lock.txt" || echo "未找到主要套件"
    else
        echo "❌ requirements-lock.txt 不存在"
    fi
}

# 函數：測試構建
test_build() {
    echo "🔨 測試 Docker 映像構建..."
    cd "$SCRIPT_DIR"
    
    echo "停止現有容器..."
    docker-compose down || true
    
    echo "構建新映像..."
    docker-compose build --no-cache api
    
    echo "啟動容器..."
    docker-compose up -d
    
    echo "等待服務啟動..."
    sleep 10
    
    echo "測試 API 響應..."
    if curl -f http://localhost:5001/test/check-fonts > /dev/null 2>&1; then
        echo "✅ 構建測試成功！"
    else
        echo "❌ 構建測試失敗！"
        exit 1
    fi
}

# 主選單
case "${1:-}" in
    "snapshot")
        create_conservative_snapshot
        ;;
    "compare")
        compare_versions
        ;;
    "conservative")
        switch_to_conservative
        ;;
    "latest")
        switch_to_latest
        ;;
    "status")
        show_status
        ;;
    "update-python")
        update_python_locks
        ;;
    "update-alpine")
        update_alpine_locks
        ;;
    "update-all")
        update_python_locks
        update_alpine_locks
        ;;
    "show")
        show_versions
        ;;
    "test")
        test_build
        ;;
    *)
        echo "使用方法: $0 {snapshot|compare|conservative|latest|status|update-all|show|test}"
        echo ""
        echo "🔒 保守版本管理:"
        echo "  snapshot       - 創建當前版本的保守快照"
        echo "  compare        - 比較當前版本與保守版本的差異"
        echo "  conservative   - 切換到保守版本服務 (port 5002)"
        echo "  latest         - 切換到最新版本服務 (port 5001)"
        echo "  status         - 顯示所有服務狀態"
        echo ""
        echo "📦 套件版本管理:"
        echo "  update-python  - 更新 Python 套件版本鎖定"
        echo "  update-alpine  - 更新 Alpine 套件版本鎖定"
        echo "  update-all     - 更新所有套件版本鎖定"
        echo "  show           - 顯示當前版本狀態"
        echo "  test           - 測試構建映像"
        echo ""
        echo "📋 使用範例:"
        echo "  $0 snapshot        # 創建保守版本快照"
        echo "  $0 conservative    # 切換到穩定的保守版本"
        echo "  $0 latest          # 切換回最新版本"
        echo "  $0 status          # 查看所有服務狀態"
        echo "  $0 compare         # 比較版本差異"
        exit 1
        ;;
esac
