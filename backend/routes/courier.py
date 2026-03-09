from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from database.db import SessionLocal
from database.models import Order, OrderItem, User, Assignment

courier_bp = Blueprint("courier", __name__)


def require_courier():
    claims = get_jwt()
    if claims.get("role") not in ("courier", "admin"):
        return jsonify({"error": "Accès réservé aux coursiers"}), 403
    return None


@courier_bp.route("/orders", methods=["GET"])
@jwt_required()
def get_assigned_orders():
    err = require_courier()
    if err:
        return err

    courier_id = int(get_jwt_identity())
    db = SessionLocal()
    try:
        assignments = db.query(Assignment).filter(Assignment.courier_id == courier_id).all()
        result = []
        for a in assignments:
            o = a.order
            client = db.query(User).filter(User.id == o.client_id).first()
            result.append({
                "id": o.id,
                "assignment_id": a.id,
                "client_name": client.name if client else "Inconnu",
                "client_email": client.email if client else "",
                "market": o.market.name,
                "market_location": o.market.location,
                "status": o.status,
                "total_estimate": o.total_estimate,
                "notes": o.notes,
                "assigned_at": a.assigned_at.isoformat(),
                "created_at": o.created_at.isoformat(),
                "items": [{
                    "product": item.product.name,
                    "quantity": item.quantity,
                    "unit": item.product.unit,
                    "price": item.product.price,
                    "note": item.note
                } for item in o.items]
            })
        result.sort(key=lambda x: x["created_at"], reverse=True)
        return jsonify(result), 200
    finally:
        db.close()


@courier_bp.route("/orders/<int:order_id>/status", methods=["PUT"])
@jwt_required()
def update_order_status(order_id):
    err = require_courier()
    if err:
        return err

    courier_id = int(get_jwt_identity())
    data = request.get_json()
    new_status = data.get("status")

    valid_statuses = ["in_progress", "delivered"]
    if new_status not in valid_statuses:
        return jsonify({"error": f"Statut invalide. Choisissez: {', '.join(valid_statuses)}"}), 400

    db = SessionLocal()
    try:
        assignment = db.query(Assignment).filter(
            Assignment.order_id == order_id,
            Assignment.courier_id == courier_id
        ).first()
        if not assignment:
            return jsonify({"error": "Commande non trouvée ou non assignée à vous"}), 404

        order = assignment.order
        order.status = new_status
        db.commit()
        return jsonify({"message": f"Statut mis à jour: {new_status}", "status": new_status}), 200
    finally:
        db.close()
