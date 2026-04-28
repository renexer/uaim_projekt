import os

from flask import Flask, jsonify

from app.api import all_blueprints
from app.cli.reminders import send_due_reminders_command
from app.cli.seed import seed_command
from app.config import DevelopmentConfig, ProductionConfig, TestingConfig
from app.extensions import cors, db, jwt, migrate
from app.utils.errors import AppError


CONFIG_MAP = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}


def create_app(config_name=None):
    app = Flask(__name__)

    config_key = config_name or os.getenv("FLASK_ENV", "development")
    app.config.from_object(CONFIG_MAP.get(config_key, DevelopmentConfig))

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    @jwt.unauthorized_loader
    def handle_missing_jwt(reason):
        return jsonify({"error": {"code": "UNAUTHORIZED", "message": "Brak tokenu autoryzacyjnego.", "details": reason}}), 401

    @jwt.invalid_token_loader
    def handle_invalid_jwt(reason):
        return jsonify({"error": {"code": "UNAUTHORIZED", "message": "Nieprawidłowy token.", "details": reason}}), 401

    @jwt.expired_token_loader
    def handle_expired_jwt(jwt_header, jwt_payload):
        return jsonify({"error": {"code": "TOKEN_EXPIRED", "message": "Token wygasł.", "details": {"type": jwt_payload.get("type")}}}), 401

    cors.init_app(
        app,
        resources={r"/api/*": {"origins": app.config["CORS_ORIGINS"]}},
        supports_credentials=True,
    )

    for blueprint in all_blueprints:
        app.register_blueprint(blueprint)

    @app.errorhandler(AppError)
    def handle_app_error(exc):
        payload = {"error": {"code": exc.code, "message": exc.message}}
        if exc.details is not None:
            payload["error"]["details"] = exc.details
        return jsonify(payload), exc.status_code

    @app.errorhandler(404)
    def handle_not_found(_):
        return jsonify({"error": {"code": "NOT_FOUND", "message": "Zasób nie istnieje."}}), 404

    @app.errorhandler(405)
    def handle_not_allowed(_):
        return jsonify({"error": {"code": "METHOD_NOT_ALLOWED", "message": "Metoda nie jest dozwolona."}}), 405

    @app.errorhandler(Exception)
    def handle_unexpected_error(exc):
        if app.config.get("TESTING"):
            raise exc
        return jsonify({"error": {"code": "INTERNAL_SERVER_ERROR", "message": "Wewnętrzny błąd serwera."}}), 500

    @app.cli.command("seed")
    def seed_cli():
        seed_command()

    @app.cli.group("reminders")
    def reminders_group():
        pass

    @reminders_group.command("send-due")
    def send_due_cli():
        send_due_reminders_command()

    return app
