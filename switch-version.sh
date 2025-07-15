#!/bin/bash
# AERC 快速版本切換腳本

case "${1:-}" in
    "safe"|"conservative")
        echo "🛡️  切換到保守安全版本..."
        ./manage-versions.sh conservative
        ;;
    "latest"|"new")
        echo "🚀 切換到最新版本..."
        ./manage-versions.sh latest
        ;;
    "status"|"check")
        ./manage-versions.sh status
        ;;
    *)
        echo "AERC 快速版本切換"
        echo "=================="
        echo ""
        echo "使用方法: $0 {safe|latest|status}"
        echo ""
        echo "  safe     - 切換到保守安全版本 (推薦用於生產環境)"
        echo "  latest   - 切換到最新版本"
        echo "  status   - 檢查服務狀態"
        echo ""
        echo "端口說明:"
        echo "  保守版本: http://localhost:5002"
        echo "  最新版本: http://localhost:5001"
        ;;
esac
