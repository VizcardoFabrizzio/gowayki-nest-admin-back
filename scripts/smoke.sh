#!/usr/bin/env bash
set -euo pipefail

BASE="${BASE_URL:-http://localhost:8000/api}"

echo "Health check"
curl -fsS "$BASE/estado" | head -c 200
echo

echo "Login"
curl -fsS -X POST "$BASE/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"dni":"12345678","pin":"1234"}' | head -c 200
echo

echo "Listar lineas"
curl -fsS "$BASE/lineas" | head -c 200
echo

echo "Listar unidades"
curl -fsS "$BASE/unidades" | head -c 200
echo

echo "Listar solicitudes"
curl -fsS "$BASE/solicitudes-registro?rol=ADMIN" | head -c 200
echo

echo "Smoke OK"