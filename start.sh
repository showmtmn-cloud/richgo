
#!/bin/bash

cd ~/poe2-profit-optimizer

source venv/bin/activate



echo "������ PoE2 Profit Optimizer 시작 중..."



# 백엔드 시작 (백그라운드)

cd backend

nohup uvicorn main:app --host 0.0.0.0 --port 8000 > ../logs/backend.log 2>&1 &

BACKEND_PID=$!



echo "✅ 백엔드 시작됨 (PID: $BACKEND_PID)"

echo "������ 백엔드: http://54.206.165.124:8000"

echo "������ 로그: ~/poe2-profit-optimizer/logs/backend.log"

echo ""

echo "중지하려면: kill $BACKEND_PID"

