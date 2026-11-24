#!/usr/bin/env bash
set -euo pipefail

BASE="${BASE_URL:-http://localhost:8000/api}"

echo "Health check"
curl -fsS "$BASE/estado" | head -c 200
echo

echo "Rechazo sin token"
if curl -fsS "$BASE/lineas" >/dev/null 2>&1; then
  echo "ERROR: /lineas respondio sin token"
  exit 1
fi

echo "Login"
TOKEN=$(curl -fsS -X POST "$BASE/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"dni":"12345678","pin":"1234"}' \
  | sed -n 's/.*"token":"\([^"]*\)".*/\1/p')

if [ -z "$TOKEN" ]; then
  echo "ERROR: el login no devolvio token"
  exit 1
fi
echo "Token obtenido (${#TOKEN} caracteres)"
echo

auth() {
  curl -fsS -H "Authorization: Bearer $TOKEN" "$@"
}

echo "Listar lineas"
auth "$BASE/lineas" | head -c 200
echo

echo "Listar unidades"
auth "$BASE/unidades" | head -c 200
echo

echo "Listar solicitudes"
auth "$BASE/solicitudes-registro" | head -c 200
echo

echo "Smoke OK"
