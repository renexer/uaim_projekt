import os

from app import create_app
from app.extensions import db
from app.seed_data import seed_database

app = create_app()

# Lokalny entrypoint developerski. W Dockerze analogiczna inicjalizacja jest
# wykonywana w `docker-entrypoint.sh`, zanim aplikację przejmie Gunicorn.
with app.app_context():
    if os.getenv("INIT_DB", "true").lower() in {"1", "true", "yes"}:
        db.create_all()
        seed_database()

if __name__ == "__main__":
    app.run(
        host=os.getenv("FLASK_RUN_HOST", "0.0.0.0"),
        port=int(os.getenv("FLASK_RUN_PORT", "5000")),
        debug=os.getenv("FLASK_ENV", "development") == "development",
    )
