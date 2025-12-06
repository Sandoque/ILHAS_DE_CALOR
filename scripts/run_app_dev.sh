#!/usr/bin/env bash
# Run Flask app in development mode
# If using a virtualenv, activate it here:
# source venv/bin/activate

export FLASK_APP=app:create_app
export FLASK_ENV=development
export FLASK_RUN_HOST=0.0.0.0
export FLASK_RUN_PORT=5000

cd "$(dirname "$0")/../backend" || exit 1
flask run --debug
