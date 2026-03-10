from backend.app import create_app
from database.seed import seed
from database.db import DB_PATH
import os

# Initialiser la DB si elle n'existe pas
if not os.path.exists(DB_PATH):
    seed()

app = create_app()

if __name__ == "__main__":
    app.run()
