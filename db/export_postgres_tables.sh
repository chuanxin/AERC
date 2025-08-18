#!/bin/zsh
# filepath: /Users/cxin/dev/AERC/db/export_postgres_tables.sh

# 🧩 基本參數
container_name="aerc-db-1"     # 你的 Docker container 名稱
db_name="hello_fastapi_dev"    # PostgreSQL 資料庫名稱
db_user="hello_fastapi"        # 使用者名稱
export_folder="./exports"      # 匯出目的地資料夾

# 📁 建立匯出資料夾（如不存在）
if [[ ! -d "$export_folder" ]]; then
    mkdir -p "$export_folder"
    echo "📁 建立匯出資料夾: $export_folder"
fi

echo "🔍 正在取得資料表清單..."

# 🗃️ 取得所有 public schema 的資料表名稱並存成陣列
declare -a table_names
while IFS= read -r table; do
    if [[ -n "$table" && "$table" != " " ]]; then
        table_names+=("$table")
    fi
done < <(docker exec -i "$container_name" \
    psql -U "$db_user" -d "$db_name" -t -A -c \
    "SELECT table_name FROM information_schema.tables WHERE table_schema='public' AND table_type='BASE TABLE' ORDER BY table_name;" \
    2>/dev/null)

# 檢查是否成功取得表格清單
if [[ ${#table_names[@]} -eq 0 ]]; then
    echo "❌ 錯誤：無法取得資料表清單，請檢查："
    echo "   - Docker 容器 '$container_name' 是否運行中"
    echo "   - 資料庫 '$db_name' 是否存在"
    echo "   - 使用者 '$db_user' 是否有權限"
    exit 1
fi

echo "📋 發現 ${#table_names[@]} 個資料表："
printf "   - %s\n" "${table_names[@]}"
echo ""

# 📤 逐一匯出 CSV
success_count=0
error_count=0

for table in "${table_names[@]}"; do
    # 清理表格名稱（移除可能的空白字元）
    table=$(echo "$table" | tr -d '[:space:]')
    
    if [[ -z "$table" ]]; then
        continue
    fi
    
    csv_file="${export_folder}/${table}.csv"
    echo "📤 匯出中: $table → $csv_file"
    
    # 執行匯出並檢查結果
    if docker exec -i "$container_name" \
        psql -U "$db_user" -d "$db_name" -c "COPY \"$table\" TO STDOUT WITH CSV HEADER;" \
        > "$csv_file" 2>/dev/null; then
        
        # 檢查檔案是否成功建立且不為空
        if [[ -s "$csv_file" ]]; then
            file_size=$(du -h "$csv_file" | cut -f1)
            row_count=$(( $(wc -l < "$csv_file") - 1 ))  # 減去標題行
            echo "   ✅ 成功 ($row_count 筆記錄, $file_size)"
            ((success_count++))
        else
            echo "   ⚠️  空檔案 (0 筆記錄)"
            ((success_count++))
        fi
    else
        echo "   ❌ 失敗：無法匯出 $table"
        rm -f "$csv_file"  # 清理失敗的檔案
        ((error_count++))
    fi
done

echo ""
echo "📊 匯出完成摘要："
echo "   ✅ 成功: $success_count 個表格"
echo "   ❌ 失敗: $error_count 個表格"
echo "   📁 匯出位置: $(realpath "$export_folder")"

if [[ $error_count -eq 0 ]]; then
    echo "🎉 所有表格已成功匯出！"
else
    echo "⚠️  部分表格匯出失敗，請檢查錯誤訊息"
fi