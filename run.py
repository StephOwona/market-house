#!/usr/bin/env python3
"""Market House - Point d'entrée principal"""
import sys
import os

# Ajouter le répertoire racine au path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.db import init_db
from database.seed import seed
from backend.app import create_app

if __name__ == "__main__":
    print("🛵 Market House - Démarrage...")
    print("📦 Initialisation de la base de données...")
    seed()
    print("🚀 Démarrage du serveur Flask...")
    app = create_app()
    print("✅ Application disponible sur: http://localhost:3001")
    app.run(host="0.0.0.0", port=3001, debug=True, use_reloader=False)
