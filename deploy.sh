#!/bin/bash
# ============================================================
# DebateAI 快速部署腳本
# ============================================================

set -e

echo "🚀 DebateAI 部署腳本"
echo "===================="

# 後端 URL
BACKEND_URL="https://debate-api-1046434677262.asia-east1.run.app"

# 前端 URL（自訂網域）
FRONTEND_URL="https://debateai.roy422.ggff.net"

# 部署前端
echo ""
echo "📦 正在安裝依賴..."
cd "$(dirname "$0")/frontend"
npm ci --silent 2>/dev/null || npm install

echo ""
echo "📦 正在打包前端..."

# 清理舊的 .env.production（如果存在）
rm -f .env.production

# 設定環境變數並打包
echo "NEXT_PUBLIC_API_URL=$BACKEND_URL" > .env.production
npm run build

# 清理敏感的 .env.production
rm -f .env.production

echo ""
echo "☁️ 正在部署到 Cloudflare Pages..."
npx wrangler pages deploy out --project-name debate-ai

echo ""
echo "✅ 部署完成！"
echo "前端（自訂網域）: $FRONTEND_URL"
echo "前端（Pages）: https://debate-ai.pages.dev"
echo "後端: $BACKEND_URL"
