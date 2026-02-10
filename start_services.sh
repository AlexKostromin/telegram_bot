#!/bin/bash

cd /home/alex/Документы/telegram_bot

echo "Starting Telegram Bot..."
python main.py > bot.log 2>&1 &
BOT_PID=$!
echo "✅ Bot started (PID: $BOT_PID)"

sleep 3

echo "Starting Django Admin..."
cd admin_panel
python manage.py runserver 0.0.0.0:8000 > admin.log 2>&1 &
ADMIN_PID=$!
echo "✅ Admin started (PID: $ADMIN_PID)"

sleep 2

cd ..

echo ""
echo "=========================================="
echo "✅ SERVICES READY"
echo "=========================================="
echo ""
echo "📱 Telegram Bot: http://t.me/YOUR_BOT"
echo "   PID: $BOT_PID"
echo "   Log: bot.log"
echo ""
echo "🔧 Django Admin: http://localhost:8000/admin"
echo "   PID: $ADMIN_PID"
echo "   User: admin"
echo "   Pass: admin"
echo "   Log: admin_panel/admin.log"
echo ""
echo "=========================================="
