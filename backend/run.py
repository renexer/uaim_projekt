from app import create_app
from app.extensions import db
from app.seed_data import seed_database

app = create_app()

with app.app_context():
    db.create_all()
    seed_database()

if __name__ == "__main__":
    app.run(debug=True)