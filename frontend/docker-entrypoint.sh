#!/bin/sh
set -eu

API_BASE_URL="${NEXT_PUBLIC_API_BASE_URL:-http://127.0.0.1:8010}"
export AIDBOT_RUNTIME_API_BASE_URL="$API_BASE_URL"

node <<'NODE'
const fs = require("fs");

const apiBaseUrl = process.env.AIDBOT_RUNTIME_API_BASE_URL || "http://127.0.0.1:8010";
const runtimeConfig = `window.__AIDBOT_CONFIG__ = ${JSON.stringify({ apiBaseUrl })};\n`;

fs.writeFileSync("/app/public/runtime-config.js", runtimeConfig);
NODE

exec "$@"
