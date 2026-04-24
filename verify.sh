#!/bin/bash

# Machine Gap - System Verification Script
# Run this to verify everything is working

echo "🔍 Machine Gap System Check"
echo "================================"
echo ""

# Check 1: Server responds
echo "1️⃣  Checking if server is running on port 8000..."
if curl -s http://localhost:8000 | grep -q "Machine Gap"; then
    echo "   ✅ Server is running!"
else
    echo "   ❌ Server not responding on port 8000"
    echo "   Run: cd /Users/peppe/Documents/AI\ Design/Machine\ Gap\ VScode && uv run uvicorn server:app --reload"
    exit 1
fi

# Check 2: Ollama is available
echo ""
echo "2️⃣  Checking if Ollama is running on port 11434..."
if curl -s http://localhost:11434/api/tags >/dev/null 2>&1; then
    echo "   ✅ Ollama is running!"
else
    echo "   ❌ Ollama not responding"
    echo "   Run: ollama serve"
    exit 1
fi

# Check 3: HTML loads
echo ""
echo "3️⃣  Checking if HTML loads..."
if curl -s http://localhost:8000 | grep -q "Machine Gap"; then
    echo "   ✅ HTML loads correctly"
else
    echo "   ❌ HTML not loading properly"
    exit 1
fi

# Check 4: JavaScript files load
echo ""
echo "4️⃣  Checking if JavaScript files load..."
SCRIPTS=("logging.js" "chat.js" "api.js" "main.js")
for script in "${SCRIPTS[@]}"; do
    if curl -s http://localhost:8000/static/scripts/$script | grep -q "console.log"; then
        echo "   ✅ $script loads correctly"
    else
        echo "   ❌ $script not loading"
        exit 1
    fi
done

# Check 5: Streaming endpoint works
echo ""
echo "5️⃣  Checking if /stream_chat endpoint works..."
RESPONSE=$(curl -s -X POST http://localhost:8000/stream_chat \
  -H "Content-Type: application/json" \
  -d '{"prompt": "test"}' | head -1)

if echo "$RESPONSE" | grep -q "turn"; then
    echo "   ✅ /stream_chat endpoint is working!"
    echo "   First turn: $(echo $RESPONSE | cut -c1-80)..."
else
    echo "   ❌ /stream_chat endpoint not working"
    exit 1
fi

echo ""
echo "================================"
echo "✅ All systems operational!"
echo ""
echo "🌐 Open http://localhost:8000 in your browser"
echo "📝 Enter a prompt and click Submit"
echo "🎭 Watch the dialogue unfold in real-time"
echo ""
