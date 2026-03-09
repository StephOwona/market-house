from werkzeug.security import generate_password_hash
from database.db import SessionLocal, init_db
from database.models import User, Market, Product


def seed():
    init_db()
    db = SessionLocal()
    try:
        # Admin account
        if not db.query(User).filter(User.email == "admin@market.com").first():
            db.add(User(
                name="Administrateur",
                email="admin@market.com",
                password_hash=generate_password_hash("Admin123!"),
                role="admin"
            ))
            print("✅ Admin créé: admin@market.com / Admin123!")

        # Markets
        markets_data = [
            {
                "name": "Marché Mokolo",
                "location": "Yaoundé, Cameroun",
                "description": "Le plus grand marché de Yaoundé, réputé pour ses vivres frais et épices locales.",
                "opening_hours": "Lun-Sam: 6h-18h",
                "products": [
                    {"name": "Plantains", "unit": "régime", "price": 2500, "category": "Fruits & Légumes"},
                    {"name": "Ndolé (feuilles)", "unit": "tas", "price": 500, "category": "Fruits & Légumes"},
                    {"name": "Macabo", "unit": "tas", "price": 1000, "category": "Céréales & Féculents"},
                    {"name": "Ignames", "unit": "tubercule", "price": 1500, "category": "Céréales & Féculents"},
                    {"name": "Tomates", "unit": "tas", "price": 500, "category": "Fruits & Légumes"},
                    {"name": "Oignons", "unit": "tas", "price": 300, "category": "Fruits & Légumes"},
                    {"name": "Poireaux", "unit": "botte", "price": 200, "category": "Fruits & Légumes"},
                    {"name": "Piment Bec d'Oiseau", "unit": "tas", "price": 200, "category": "Épices"},
                    {"name": "Djansan", "unit": "verre", "price": 1000, "category": "Épices"},
                    {"name": "Pèbè", "unit": "verre", "price": 500, "category": "Épices"},
                    {"name": "Gingembre frais", "unit": "tas", "price": 300, "category": "Épices"},
                    {"name": "Bar (Poisson fumé)", "unit": "pièce", "price": 3500, "category": "Poissons & Viandes"},
                    {"name": "Viande de Bœuf (avec os)", "unit": "kg", "price": 2500, "category": "Poissons & Viandes"},
                    {"name": "Huile de palme rouge", "unit": "litre", "price": 1200, "category": "Épicerie"},
                    {"name": "Arachides décortiquées", "unit": "verre", "price": 150, "category": "Épicerie"},
                    {"name": "Pâte d'arachide", "unit": "pot", "price": 500, "category": "Épicerie"},
                ]
            },
            {
                "name": "Marché Central",
                "location": "Douala, Cameroun",
                "description": "Le cœur commerçant de Douala, offrant une grande variété de produits et textiles.",
                "opening_hours": "Lun-Dim: 7h-20h",
                "products": [
                    {"name": "Tapioca (Garri)", "unit": "seau", "price": 2500, "category": "Céréales & Féculents"},
                    {"name": "Bâtons de manioc (Bobolo)", "unit": "pièce", "price": 250, "category": "Céréales & Féculents"},
                    {"name": "Riz parfumé", "unit": "sac 5kg", "price": 4500, "category": "Céréales & Féculents"},
                    {"name": "Maïs", "unit": "seau", "price": 2000, "category": "Céréales & Féculents"},
                    {"name": "Poisson frais (Capitaine)", "unit": "kg", "price": 4000, "category": "Poissons & Viandes"},
                    {"name": "Poulet de chair", "unit": "pièce", "price": 3500, "category": "Poissons & Viandes"},
                    {"name": "Safou (Prunes)", "unit": "tas", "price": 1000, "category": "Fruits & Légumes"},
                    {"name": "Ananas", "unit": "pièce", "price": 500, "category": "Fruits & Légumes"},
                    {"name": "Citron", "unit": "tas", "price": 300, "category": "Fruits & Légumes"},
                    {"name": "Pagnes classiques", "unit": "pièce", "price": 8000, "category": "Textile"},
                    {"name": "Savon de Marseille", "unit": "morceau", "price": 400, "category": "Hygiène"},
                    {"name": "Eau de Javel", "unit": "bouteille", "price": 600, "category": "Hygiène"},
                ]
            },
            {
                "name": "Marché Mboppi",
                "location": "Douala, Cameroun",
                "description": "Le plus grand marché de gros et détail de la sous-région, idéal pour l'épicerie et les boissons.",
                "opening_hours": "Lun-Sam: 7h-19h",
                "products": [
                    {"name": "Lait concentré", "unit": "boîte", "price": 800, "category": "Produits laitiers"},
                    {"name": "Lait en poudre", "unit": "sachet 500g", "price": 2500, "category": "Produits laitiers"},
                    {"name": "Sucre en poudre", "unit": "kg", "price": 800, "category": "Épicerie"},
                    {"name": "Sel fin", "unit": "sachet", "price": 200, "category": "Épicerie"},
                    {"name": "Cube Maggi", "unit": "paquet", "price": 1000, "category": "Épicerie"},
                    {"name": "Tomate concentrée", "unit": "boîte 400g", "price": 500, "category": "Épicerie"},
                    {"name": "Pain baguette", "unit": "pièce", "price": 150, "category": "Boulangerie"},
                    {"name": "Œufs", "unit": "alvéole (30)", "price": 2000, "category": "Œufs & Produits frais"},
                    {"name": "Jus de fruits Foléré (Bissap)", "unit": "bouteille 1L", "price": 1000, "category": "Boissons"},
                    {"name": "Eau Minérale (Supermont)", "unit": "bouteille 1.5L", "price": 300, "category": "Boissons"},
                    {"name": "Bière locale", "unit": "bouteille 65cl", "price": 600, "category": "Boissons"},
                    {"name": "Lessive en poudre (Omo)", "unit": "sachet 1kg", "price": 1200, "category": "Ménager"},
                ]
            }
        ]

        for mdata in markets_data:
            existing_market = db.query(Market).filter(Market.name == mdata["name"]).first()
            if not existing_market:
                market = Market(
                    name=mdata["name"],
                    location=mdata["location"],
                    description=mdata["description"],
                    opening_hours=mdata["opening_hours"]
                )
                db.add(market)
                db.flush()
                for pdata in mdata["products"]:
                    db.add(Product(
                        market_id=market.id,
                        name=pdata["name"],
                        unit=pdata["unit"],
                        price=pdata["price"],
                        category=pdata["category"]
                    ))
                print(f"✅ Marché ajouté: {mdata['name']}")

        db.commit()
        print("🎉 Base de données initialisée avec succès!")
    finally:
        db.close()


if __name__ == "__main__":
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    seed()
