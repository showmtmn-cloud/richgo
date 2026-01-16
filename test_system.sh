
#!/bin/bash



echo "=== PoE2 Profit Optimizer System Test ==="

echo ""



BASE_URL="http://localhost:8001"



echo "1. Health Check"

curl -s $BASE_URL/health | python3 -m json.tool

echo ""



echo "2. System Stats"

curl -s $BASE_URL/api/stats | python3 -m json.tool

echo ""



echo "3. Exchange Rates"

curl -s $BASE_URL/api/exchange-rates | python3 -m json.tool

echo ""



echo "4. Scheduler Status"

curl -s $BASE_URL/api/scheduler/status | python3 -m json.tool

echo ""



echo "5. Currencies (first 5)"

curl -s "$BASE_URL/api/currencies" | python3 -c "import sys, json; d=json.load(sys.stdin); print(json.dumps({'count': d['count'], 'currencies': d['currencies'][:5]}, indent=2))"

echo ""



echo "=== Test Complete ==="

