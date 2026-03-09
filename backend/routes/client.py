from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from database.db import SessionLocal
from database.models import Market, Product, Order, OrderItem, User, Assignment, TrendComment
from datetime import datetime, timedelta

client_bp = Blueprint("client", __name__)


def require_client():
    claims = get_jwt()
    if claims.get("role") not in ("client", "admin"):
        return jsonify({"error": "Accès réservé aux clients"}), 403
    return None


@client_bp.route("/markets", methods=["GET"])
@jwt_required()
def get_markets():
    db = SessionLocal()
    try:
        markets = db.query(Market).all()
        return jsonify([{
            "id": m.id,
            "name": m.name,
            "location": m.location,
            "description": m.description,
            "image_url": m.image_url,
            "opening_hours": m.opening_hours
        } for m in markets]), 200
    finally:
        db.close()


@client_bp.route("/markets/<int:market_id>/products", methods=["GET"])
@jwt_required()
def get_products(market_id):
    db = SessionLocal()
    try:
        market = db.query(Market).filter(Market.id == market_id).first()
        if not market:
            return jsonify({"error": "Marché introuvable"}), 404

        products = db.query(Product).filter(Product.market_id == market_id).all()
        categories = {}
        for p in products:
            cat = p.category or "Autres"
            if cat not in categories:
                categories[cat] = []
            categories[cat].append({
                "id": p.id,
                "name": p.name,
                "unit": p.unit,
                "price": p.price,
                "category": p.category,
                "image_url": p.image_url
            })
        return jsonify({
            "market": {"id": market.id, "name": market.name, "location": market.location},
            "categories": categories,
            "products": [{
                "id": p.id, "name": p.name, "unit": p.unit,
                "price": p.price, "category": p.category, "image_url": p.image_url
            } for p in products]
        }), 200
    finally:
        db.close()


@client_bp.route("/orders", methods=["POST"])
@jwt_required()
def create_order():
    err = require_client()
    if err:
        return err

    user_id = int(get_jwt_identity())
    data = request.get_json()
    market_id = data.get("market_id")
    items = data.get("items", [])
    notes = data.get("notes", "")

    if not market_id or not items:
        return jsonify({"error": "Marché et articles requis"}), 400

    db = SessionLocal()
    try:
        market = db.query(Market).filter(Market.id == market_id).first()
        if not market:
            return jsonify({"error": "Marché introuvable"}), 404

        total = 0.0
        order = Order(client_id=user_id, market_id=market_id, notes=notes, status="pending")
        db.add(order)
        db.flush()

        for item in items:
            product = db.query(Product).filter(Product.id == item.get("product_id")).first()
            if not product:
                continue
            qty = float(item.get("quantity", 1))
            total += product.price * qty
            db.add(OrderItem(
                order_id=order.id,
                product_id=product.id,
                quantity=qty,
                note=item.get("note", "")
            ))

        order.total_estimate = round(total, 2)
        # Mocking an ETA (45 minutes from now)
        order.delivery_eta = datetime.utcnow() + timedelta(minutes=45)
        
        # Auto-Assign a random courier
        import random
        couriers = db.query(User).filter(User.role == "courier").all()
        courier_name = None
        if couriers:
            courier = random.choice(couriers)
            assignment = Assignment(order_id=order.id, courier_id=courier.id)
            db.add(assignment)
            order.status = "assigned"
            courier_name = courier.name

        db.commit()
        db.refresh(order)

        return jsonify({
            "message": "Commande soumise avec succès",
            "order": {
                "id": order.id, 
                "status": order.status, 
                "total_estimate": order.total_estimate,
                "courier_name": courier_name,
                "delivery_eta": order.delivery_eta.isoformat() if order.delivery_eta else None
            }
        }), 201
    finally:
        db.close()


@client_bp.route("/orders", methods=["GET"])
@jwt_required()
def get_my_orders():
    user_id = int(get_jwt_identity())
    db = SessionLocal()
    try:
        orders = db.query(Order).filter(Order.client_id == user_id).order_by(Order.created_at.desc()).all()
        result = []
        for o in orders:
            courier_name = None
            if o.assignment:
                courier = db.query(User).filter(User.id == o.assignment.courier_id).first()
                courier_name = courier.name if courier else None
            result.append({
                "id": o.id,
                "market": o.market.name,
                "status": o.status,
                "total_estimate": o.total_estimate,
                "notes": o.notes,
                "created_at": o.created_at.isoformat(),
                "courier": courier_name,
                "items": [{
                    "product": item.product.name,
                    "quantity": item.quantity,
                    "unit": item.product.unit,
                    "price": item.product.price,
                    "note": item.note
                } for item in o.items],
                "delivery_eta": o.delivery_eta.isoformat() if o.delivery_eta else None
            })
        return jsonify(result), 200
    finally:
        db.close()


@client_bp.route("/orders/<int:order_id>/items", methods=["PUT"])
@jwt_required()
def update_order_items(order_id):
    err = require_client()
    if err: return err

    user_id = int(get_jwt_identity())
    data = request.get_json()
    items_data = data.get("items", [])

    if not items_data:
        return jsonify({"error": "La liste des articles ne peut pas être vide"}), 400

    db = SessionLocal()
    try:
        order = db.query(Order).filter(Order.id == order_id, Order.client_id == user_id).first()
        if not order:
            return jsonify({"error": "Commande introuvable"}), 404
        
        if order.status not in ("assigned", "in_progress", "pending"):
            return jsonify({"error": "Impossible de modifier la commande à cette étape"}), 400

        # Effacer les anciens articles
        db.query(OrderItem).filter(OrderItem.order_id == order.id).delete()

        # Insérer les nouveaux
        total = 0.0
        for item in items_data:
            product = db.query(Product).filter(Product.id == item.get("product_id")).first()
            if not product: continue
            qty = float(item.get("quantity", 1))
            total += product.price * qty
            db.add(OrderItem(order_id=order.id, product_id=product.id, quantity=qty))

        order.total_estimate = round(total, 2)
        db.commit()

        return jsonify({
            "message": "Commande mise à jour avec succès",
            "total_estimate": order.total_estimate
        }), 200
    finally:
        db.close()


@client_bp.route("/orders/<int:order_id>/complete", methods=["POST"])
@jwt_required()
def complete_order(order_id):
    err = require_client()
    if err: return err

    user_id = int(get_jwt_identity())
    db = SessionLocal()
    try:
        order = db.query(Order).filter(Order.id == order_id, Order.client_id == user_id).first()
        if not order:
            return jsonify({"error": "Commande introuvable"}), 404
        
        if order.status != "delivered":
            return jsonify({"error": "La commande doit être livrée (delivered) par le coursier d'abord"}), 400
        
        order.status = "completed"
        db.commit()
        return jsonify({"message": "Réception confirmée avec succès"}), 200
    finally:
        db.close()


@client_bp.route("/trends", methods=["GET"])
@jwt_required()
def get_trends():
    db = SessionLocal()
    try:
        trends = db.query(TrendComment).order_by(TrendComment.created_at.desc()).limit(50).all()
        return jsonify([{
            "id": t.id,
            "author_name": t.author_name or "Anonyme",
            "text": t.text,
            "trend_type": t.trend_type,
            "created_at": t.created_at.isoformat()
        } for t in trends]), 200
    finally:
        db.close()


@client_bp.route("/trends", methods=["POST"])
@jwt_required()
def post_trend():
    data = request.get_json()
    text = data.get("text")
    if not text:
        return jsonify({"error": "Texte manquant"}), 400
    
    is_anonymous = data.get("is_anonymous", False)
    trend_type = data.get("trend_type", "general")
    
    db = SessionLocal()
    try:
        user_id = int(get_jwt_identity())
        user = db.query(User).filter(User.id == user_id).first()
        author_name = "Anonyme" if is_anonymous or not user else user.name
        author_id = None if is_anonymous else user_id

        trend = TrendComment(
            author_id=author_id,
            author_name=author_name,
            text=text,
            trend_type=trend_type
        )
        db.add(trend)
        db.commit()
        db.refresh(trend)
        
        return jsonify({
            "message": "Avis publié avec succès",
            "trend": {
                "id": trend.id,
                "author_name": trend.author_name,
                "text": trend.text,
                "trend_type": trend.trend_type,
                "created_at": trend.created_at.isoformat()
            }
        }), 201
    finally:
        db.close()
