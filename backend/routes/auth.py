from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token
from database.db import SessionLocal
from database.models import User
from datetime import timedelta

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    name = data.get("name", "").strip()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")
    role = data.get("role", "client")

    if not name or not email or not password:
        return jsonify({"error": "Nom, email et mot de passe sont requis"}), 400

    if role not in ("client", "courier"):
        return jsonify({"error": "Rôle invalide. Choisissez 'client' ou 'courier'"}), 400

    if len(password) < 6:
        return jsonify({"error": "Le mot de passe doit contenir au moins 6 caractères"}), 400

    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.email == email).first()
        if existing:
            return jsonify({"error": "Un compte avec cet email existe déjà"}), 409

        user = User(
            name=name,
            email=email,
            password_hash=generate_password_hash(password),
            role=role
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        token = create_access_token(
            identity=str(user.id),
            additional_claims={"role": user.role, "name": user.name},
            expires_delta=timedelta(hours=24)
        )
        return jsonify({
            "message": "Compte créé avec succès",
            "token": token,
            "user": {"id": user.id, "name": user.name, "email": user.email, "role": user.role}
        }), 201
    finally:
        db.close()


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not email or not password:
        return jsonify({"error": "Email et mot de passe requis"}), 400

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        if not user or not check_password_hash(user.password_hash, password):
            return jsonify({"error": "Email ou mot de passe incorrect"}), 401

        token = create_access_token(
            identity=str(user.id),
            additional_claims={"role": user.role, "name": user.name},
            expires_delta=timedelta(hours=24)
        )
        return jsonify({
            "message": "Connexion réussie",
            "token": token,
            "user": {"id": user.id, "name": user.name, "email": user.email, "role": user.role}
        }), 200
    finally:
        db.close()
