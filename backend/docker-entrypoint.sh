#!/bin/sh
set -e

if [ "${INIT_DB:-true}" = "true" ] || [ "${INIT_DB:-true}" = "1" ]; then
  python - <<'PY'
from app import create_app
from app.extensions import db
from app.seed_data import seed_database

app = create_app()
with app.app_context():
    db.create_all()
    seed_database()
PY
fi

exec gunicorn --bind 0.0.0.0:${FLASK_RUN_PORT:-5000} --workers ${GUNICORN_WORKERS:-2} --threads ${GUNICORN_THREADS:-2} app.wsgi:app
