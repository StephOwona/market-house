from backend.app import create_app
from database.seed import seed
import os

# Initialiser la DB si elle n'existe pas
if not os.path.exists("market_house.db"):
    seed()

app = create_app()

if __name__ == "__main__":
    app.run()
