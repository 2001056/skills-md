#!/bin/sh
# ============================================================
# git-security-scan hooks 설치 스크립트 (Linux / macOS / Git Bash)
# 사용법: sh hooks/install.sh
# ============================================================

HOOKS_DIR="$(git rev-parse --git-dir)/hooks"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "🔧 git-security-scan 훅 설치 중..."

# pre-commit 설치
cp "$SCRIPT_DIR/pre-commit" "$HOOKS_DIR/pre-commit"
chmod +x "$HOOKS_DIR/pre-commit"

echo "✅ pre-commit 훅 설치 완료: $HOOKS_DIR/pre-commit"
echo ""
echo "이제 git commit 시 자동으로 보안 검사가 실행됩니다."
echo "훅 제거: rm $HOOKS_DIR/pre-commit"
