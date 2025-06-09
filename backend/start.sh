#!/bin/bash
set -e

echo "Starting application..."

# 檢查資料庫是否為空，如果是則重置到初始狀態
echo "Checking database state..."

# 嘗試創建所有表（從頭開始）
echo "Creating database tables from scratch..."
poetry run alembic upgrade head

# 如果上面失敗，嘗試重置到基礎版本
if [ $? -ne 0 ]; then
    echo "Migration failed, trying to reset database..."
    poetry run alembic stamp base
    poetry run alembic upgrade head
fi

# Start the FastAPI application
echo "Starting FastAPI server..."
exec poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000