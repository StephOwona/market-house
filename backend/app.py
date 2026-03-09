from flask import Flask, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")


def create_app():
    app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path="")
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    app.config["SECRET_KEY"] = "market-house-super-secret-key-2024"
    app.config["JWT_SECRET_KEY"] = "jwt-market-house-secret-key-2024"

    JWTManager(app)

    # Register blueprints
    from backend.routes.auth import auth_bp
    from backend.routes.client import client_bp
    from backend.routes.courier import courier_bp
    from backend.routes.admin import admin_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(client_bp, url_prefix="/api")
    app.register_blueprint(courier_bp, url_prefix="/api/courier")
    app.register_blueprint(admin_bp, url_prefix="/api/admin")

    # Serve frontend for any path not matching API
    @app.route("/")
    def index():
        return send_from_directory(FRONTEND_DIR, "index.html")

    @app.route("/<path:path>")
    def serve_static(path):
        full_path = os.path.join(FRONTEND_DIR, path)
        if os.path.isfile(full_path):
            return send_from_directory(FRONTEND_DIR, path)
        return send_from_directory(FRONTEND_DIR, "index.html")

    return app
