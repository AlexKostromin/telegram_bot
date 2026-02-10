#!/bin/bash
# Monitor both logs in real-time

cd /home/alex/Документы/telegram_bot

clear

while true; do
    clear

    echo "=================================================================================="
    echo "📊 LIVE LOG MONITORING - $(date '+%Y-%m-%d %H:%M:%S')"
    echo "=================================================================================="
    echo ""

    # Check if services are running
    BOT_RUNNING=$(pgrep -f "python main.py" | wc -l)
    ADMIN_RUNNING=$(pgrep -f "manage.py runserver" | wc -l)

    echo "🚀 SERVICE STATUS:"
    if [ $BOT_RUNNING -gt 0 ]; then
        echo "   📱 Bot:   ✅ RUNNING (PID: $(pgrep -f 'python main.py' | head -1))"
    else
        echo "   📱 Bot:   ❌ NOT RUNNING"
    fi

    if [ $ADMIN_RUNNING -gt 0 ]; then
        echo "   🔧 Admin: ✅ RUNNING (PID: $(pgrep -f 'manage.py runserver' | head -1))"
    else
        echo "   🔧 Admin: ❌ NOT RUNNING"
    fi

    echo ""
    echo "=================================================================================="
    echo "🤖 TELEGRAM BOT LOG (last 15 lines):"
    echo "=================================================================================="
    tail -15 bot.log

    echo ""
    echo "=================================================================================="
    echo "🔧 DJANGO ADMIN LOG (last 10 lines):"
    echo "=================================================================================="
    tail -10 admin_panel/admin.log

    echo ""
    echo "=================================================================================="
    echo "⏰ Next refresh in 5 seconds... (Press Ctrl+C to exit)"
    echo "=================================================================================="

    sleep 5
done
