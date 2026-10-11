#!/usr/bin/env bash
# Запуск приложения ship-map-maker
set -e

cd "$(dirname "$(readlink -f "$0")")"

exec python scripts/main.py "$@"