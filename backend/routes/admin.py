from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from werkzeug.security import generate_password_hash
from database.db import SessionLocal
from database.models import User, Order, Assignment, Market, Product

admin_bp = Blueprint("admin", __name__)


def require_admin():
    claims = get_jwt()
    if claims.get("role") != "admin":
        return jsonify({"error": "Accès administrateur requis"}), 403
    return None


@admin_bp.route("/users", methods=["GET"])
@jwt_required()
def get_users():
    err = require_admin()
    if err:
        return err
    db = SessionLocal()
    try:
        users = db.query(User).order_by(User.created_at.desc()).all()
        return jsonify([{
            "id": u.id, "name": u.name, "email": u.email,
            "role": u.role, "created_at": u.created_at.isoformat()
        } for u in users]), 200
    finally:
        db.close()


@admin_bp.route("/users/<int:user_id>", methods=["DELETE"])
@jwt_required()
def delete_user(user_id):
    err = require_admin()
    if err:
        return err
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return jsonify({"error": "Utilisateur introuvable"}), 404
        if user.role == "admin":
            return jsonify({"error": "Impossible de supprimer un administrateur"}), 403
        db.delete(user)
        db.commit()
        return jsonify({"message": "Utilisateur supprimé"}), 200
    finally:
        db.close()


@admin_bp.route("/orders", methods=["GET"])
@jwt_required()
def get_all_orders():
    err = require_admin()
    if err:
        return err
    db = SessionLocal()
    try:
        orders = db.query(Order).order_by(Order.created_at.desc()).all()
        result = []
        for o in orders:
            courier_name = None
            courier_id = None
            if o.assignment:
                courier = db.query(User).filter(User.id == o.assignment.courier_id).first()
                courier_name = courier.name if courier else None
                courier_id = o.assignment.courier_id
            result.append({
                "id": o.id,
                "client_name": o.client.name,
                "client_email": o.client.email,
                "market": o.market.name,
                "status": o.status,
                "total_estimate": o.total_estimate,
                "notes": o.notes,
                "created_at": o.created_at.isoformat(),
                "courier_name": courier_name,
                "courier_id": courier_id,
                "items_count": len(o.items)
            })
        return jsonify(result), 200
    finally:
        db.close()


@admin_bp.route("/orders/<int:order_id>/assign", methods=["POST"])
@jwt_required()
def assign_order(order_id):
    err = require_admin()
    if err:
        return err
    data = request.get_json()
    courier_id = data.get("courier_id")
    if not courier_id:
        return jsonify({"error": "courier_id requis"}), 400

    db = SessionLocal()
    try:
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            return jsonify({"error": "Commande introuvable"}), 404

        courier = db.query(User).filter(User.id == courier_id, User.role == "courier").first()
        if not courier:
            return jsonify({"error": "Coursier introuvable"}), 404

        existing = db.query(Assignment).filter(Assignment.order_id == order_id).first()
        if existing:
            existing.courier_id = courier_id
        else:
            db.add(Assignment(order_id=order_id, courier_id=courier_id))

        order.status = "assigned"
        db.commit()
        return jsonify({"message": f"Commande assignée à {courier.name}"}), 200
    finally:
        db.close()


@admin_bp.route("/couriers", methods=["GET"])
@jwt_required()
def get_couriers():
    err = require_admin()
    if err:
        return err
    db = SessionLocal()
    try:
        couriers = db.query(User).filter(User.role == "courier").all()
        return jsonify([{"id": c.id, "name": c.name, "email": c.email} for c in couriers]), 200
    finally:
        db.close()


@admin_bp.route("/markets", methods=["POST"])
@jwt_required()
def add_market():
    err = require_admin()
    if err:
        return err
    data = request.get_json()
    name = data.get("name", "").strip()
    location = data.get("location", "").strip()
    if not name or not location:
        return jsonify({"error": "Nom et localisation requis"}), 400
    db = SessionLocal()
    try:
        market = Market(
            name=name, location=location,
            description=data.get("description", ""),
            opening_hours=data.get("opening_hours", ""),
            image_url=data.get("image_url", "")
        )
        db.add(market)
        db.commit()
        db.refresh(market)
        return jsonify({"message": "Marché ajouté", "id": market.id}), 201
    finally:
        db.close()


@admin_bp.route("/markets/<int:market_id>", methods=["PUT"])
@jwt_required()
def update_market(market_id):
    err = require_admin()
    if err:
        return err
    data = request.get_json()
    db = SessionLocal()
    try:
        market = db.query(Market).filter(Market.id == market_id).first()
        if not market:
            return jsonify({"error": "Marché introuvable"}), 404
        
        if "name" in data: market.name = data["name"].strip()
        if "location" in data: market.location = data["location"].strip()
        if "description" in data: market.description = data["description"]
        if "opening_hours" in data: market.opening_hours = data["opening_hours"]
        if "image_url" in data: market.image_url = data["image_url"]
        
        db.commit()
        return jsonify({"message": "Marché mis à jour"}), 200
    finally:
        db.close()


@admin_bp.route("/markets/<int:market_id>", methods=["DELETE"])
@jwt_required()
def delete_market(market_id):
    err = require_admin()
    if err:
        return err
    db = SessionLocal()
    try:
        market = db.query(Market).filter(Market.id == market_id).first()
        if not market:
            return jsonify({"error": "Marché introuvable"}), 404
        db.delete(market)
        db.commit()
        return jsonify({"message": "Marché supprimé"}), 200
    finally:
        db.close()


@admin_bp.route("/markets/<int:market_id>/products", methods=["POST"])
@jwt_required()
def add_product(market_id):
    err = require_admin()
    if err:
        return err
    data = request.get_json()
    name = data.get("name", "").strip()
    if not name:
        return jsonify({"error": "Nom du produit requis"}), 400
    db = SessionLocal()
    try:
        market = db.query(Market).filter(Market.id == market_id).first()
        if not market:
            return jsonify({"error": "Marché introuvable"}), 404
        product = Product(
            market_id=market_id,
            name=name,
            unit=data.get("unit", "pièce"),
            price=float(data.get("price", 0)),
            category=data.get("category", "Autres"),
            image_url=data.get("image_url", "")
        )
        db.add(product)
        db.commit()
        db.refresh(product)
        return jsonify({"message": "Produit ajouté", "id": product.id}), 201
    finally:
        db.close()


@admin_bp.route("/products/<int:product_id>", methods=["PUT"])
@jwt_required()
def update_product(product_id):
    err = require_admin()
    if err:
        return err
    data = request.get_json()
    db = SessionLocal()
    try:
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            return jsonify({"error": "Produit introuvable"}), 404
        
        if "name" in data: product.name = data["name"].strip()
        if "price" in data: product.price = float(data["price"])
        if "unit" in data: product.unit = data["unit"]
        if "category" in data: product.category = data["category"]
        if "image_url" in data: product.image_url = data["image_url"]
        
        db.commit()
        return jsonify({"message": "Produit mis à jour"}), 200
    finally:
        db.close()


@admin_bp.route("/products/<int:product_id>", methods=["DELETE"])
@jwt_required()
def delete_product(product_id):
    err = require_admin()
    if err:
        return err
    db = SessionLocal()
    try:
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            return jsonify({"error": "Produit introuvable"}), 404
        db.delete(product)
        db.commit()
        return jsonify({"message": "Produit supprimé"}), 200
    finally:
        db.close()


@admin_bp.route("/stats", methods=["GET"])
@jwt_required()
def get_stats():
    err = require_admin()
    if err:
        return err
    db = SessionLocal()
    try:
        total_users = db.query(User).count()
        total_clients = db.query(User).filter(User.role == "client").count()
        total_couriers = db.query(User).filter(User.role == "courier").count()
        total_orders = db.query(Order).count()
        pending_orders = db.query(Order).filter(Order.status == "pending").count()
        delivered_orders = db.query(Order).filter(Order.status == "delivered").count()
        total_markets = db.query(Market).count()
        return jsonify({
            "users": total_users,
            "clients": total_clients,
            "couriers": total_couriers,
            "orders": total_orders,
            "pending": pending_orders,
            "delivered": delivered_orders,
            "markets": total_markets
        }), 200
    finally:
        db.close()
