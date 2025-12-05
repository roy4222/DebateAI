#!/bin/bash
# DebateAI 快速部署腳本

set -e

echo "🚀 DebateAI 部署腳本"
echo "===================="

# 後端 URL
BACKEND_URL="https://debate-api-1046434677262.asia-east1.run.app"

# 部署前端
echo ""
echo "📦 正在打包前端..."
cd "$(dirname "$0")/frontend"

# 設定環境變數並打包
echo "NEXT_PUBLIC_API_URL=$BACKEND_URL" > .env.production
npm run build

echo ""
echo "☁️ 正在部署到 Cloudflare Pages..."
npx wrangler pages deploy out --project-name debate-ai

echo ""
echo "✅ 部署完成！"
echo "前端: https://debate-ai.pages.dev"
echo "後端: $BACKEND_URL"
