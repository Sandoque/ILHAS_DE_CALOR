#!/usr/bin/env bash
# Run backend via Docker Compose (ensure Postgres is up)
cd "$(dirname "$0")/.." || exit 1

docker compose up --build web
