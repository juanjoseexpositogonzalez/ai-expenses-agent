"""Script to initialize the database."""
import logging
from app.database import init_db

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

if __name__ == "__main__":
    print("Initializing database...")
    init_db()
    print("Database initialized successfully!")

