#!/bin/sh
set -eu

APP_DIR="${APP_DIR:-/app}"
if [ ! -d "$APP_DIR/dist" ]; then
  APP_DIR="$(pwd)"
fi

API_BASE_URL="${API_BASE_URL:-${VITE_API_BASE_URL:-/api}}"
ESCAPED_API_BASE_URL=$(printf '%s' "$API_BASE_URL" | sed 's/[&/]/\\&/g')

cat >"$APP_DIR/dist/runtime-config.js" <<CONFIG
window.__AION_CONFIG__ = {
  API_BASE_URL: "__AION_API_BASE_URL__"
}
CONFIG

sed -i "s/__AION_API_BASE_URL__/${ESCAPED_API_BASE_URL}/g" "$APP_DIR/dist/runtime-config.js"

exec serve -s "$APP_DIR/dist" -l "tcp://0.0.0.0:${PORT:-4173}"
