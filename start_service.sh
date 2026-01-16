
#!/bin/bash



echo "Ì†ΩÌ∫Ä PoE2 Profit Optimizer Starting..."

echo ""



cd ~/poe2-profit-optimizer/backend

source ../venv/bin/activate



# Í∏∞Ï°¥ ÌîÑÎ°úÏÑ∏Ïä§ Ï¢ÖÎ£å

pkill -f "uvicorn main:app" 2>/dev/null



# ÏÑúÎ≤Ñ ÏãúÏûë (Î∞±Í∑∏ÎùºÏö¥Îìú)

nohup uvicorn main:app --host 0.0.0.0 --port 8001 > ../logs/server.log 2>&1 &

PID=$!



echo "‚úÖ Server started (PID: $PID)"

echo "Ì†ΩÌ≥ä API: http://54.206.165.124:8001"

echo "Ì†ΩÌ≥ù Logs: ~/poe2-profit-optimizer/logs/server.log"

echo ""

echo "To stop: pkill -f 'uvicorn main:app'"

