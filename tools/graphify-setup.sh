#!/usr/bin/env bash
# Cài graphify + gắn git hook tự cập nhật đồ thị. Chạy được trên macOS, Linux, Windows (Git Bash).
# Dùng: bash tools/graphify-setup.sh        (máy mới, chạy 1 lần)
#       bash tools/graphify-setup.sh --quiet (Claude Code tự gọi khi mở phiên)
QUIET=0; [ "$1" = "--quiet" ] && QUIET=1
say() { [ $QUIET = 1 ] || echo "$@"; }
ROOT="$(cd "$(dirname "$0")/.." && pwd)"; cd "$ROOT" || exit 0

if ! command -v graphify >/dev/null 2>&1; then
  say "Cài graphify..."
  if command -v uv >/dev/null 2>&1; then uv tool install -q "graphifyy[gemini]" >/dev/null 2>&1
  elif command -v pipx >/dev/null 2>&1; then pipx install -q "graphifyy[gemini]" >/dev/null 2>&1
  else
    PY=$(command -v python3 || command -v python || command -v py)
    [ -n "$PY" ] && { "$PY" -m pip install -q --user "graphifyy[gemini]" >/dev/null 2>&1 \
      || "$PY" -m pip install -q --user --break-system-packages "graphifyy[gemini]" >/dev/null 2>&1; }
  fi
fi
command -v graphify >/dev/null 2>&1 || { say "Không cài được graphify (cần Python 3.10+)."; exit 0; }

# Git hook: sau mỗi commit/pull tự cập nhật phần code của đồ thị (không tốn API)
[ -d .git ] && ! graphify hook status 2>/dev/null | grep -q "post-commit: installed" && graphify hook install >/dev/null 2>&1
say "graphify sẵn sàng: $(graphify --version 2>/dev/null || echo ok)"
say "Vault Obsidian: $ROOT/graphify-out/obsidian  (Obsidian > Open folder as vault)"
