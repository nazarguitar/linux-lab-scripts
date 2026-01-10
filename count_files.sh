#!/bin/bash


TARGET_DIR="${1:-/etc}"
EXT="$2"                  

if [ ! -d "$TARGET_DIR" ]; then
    echo "Помилка: директорія '$TARGET_DIR' не існує"
    exit 1
fi

files_find_cmd=(find "$TARGET_DIR" -type f)

if [ -n "$EXT" ]; then
    files_find_cmd+=( -name "*.$EXT" )
fi


files_count=$("${files_find_cmd[@]}" 2>/dev/null | wc -l)


dirs_count=$(find "$TARGET_DIR" -type d 2>/dev/null | wc -l)
links_count=$(find "$TARGET_DIR" -type l 2>/dev/null | wc -l)

dirs_without_root=$((dirs_count - 1))

total_size_bytes=$("${files_find_cmd[@]}" -printf '%s\n' 2>/dev/null | \
    awk '{sum+=$1} END {print sum+0}')

total_size_kb=$(( total_size_bytes / 1024 ))

echo "Статистика директорії: $TARGET_DIR"
if [ -n "$EXT" ]; then
    echo "Фільтр за розширенням: .$EXT"
else
    echo "Фільтр за розширенням: (усі файли)"
fi
echo "-----------------------------------------"
echo "  Звичайні файли (з урахуванням фільтра): $files_count"
echo "  Директорії (рекурсивно, без кореневої): $dirs_without_root"
echo "  Символічні посилання (рекурсивно):      $links_count"
echo "-----------------------------------------"
echo "  Загальний розмір знайдених файлів:"
echo "    $total_size_bytes байт (~${total_size_kb} КБ)"
echo "-----------------------------------------"
echo "Дата виконання: $(date)"

exit 0

