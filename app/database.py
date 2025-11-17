"""Database configuration and session management."""
import logging
from sqlmodel import SQLModel, create_engine, Session, select
from app.config import settings
from app.models import Category, Expense

logger = logging.getLogger(__name__)

# Create engine
engine = create_engine(settings.DATABASE_URL, echo=False)


def init_db() -> None:
    """Initialize database by creating all tables."""
    logger.info("Creating database tables...")
    SQLModel.metadata.create_all(engine)
    logger.info("Database tables created successfully")
    
    # Create predefined categories
    create_predefined_categories()


def create_predefined_categories() -> None:
    """Create predefined categories if they don't exist."""
    logger.info("Creating predefined categories...")
    
    predefined_categories = [
        ("Comida", "Gastos en restaurantes, supermercados y alimentos"),
        ("Transporte", "Taxi, autobús, metro, gasolina, peajes"),
        ("Alojamiento", "Hoteles, Airbnb, hospedaje"),
        ("Entretenimiento", "Cine, conciertos, eventos, hobbies"),
        ("Salud", "Medicinas, consultas médicas, seguro"),
        ("Compras", "Ropa, electrónicos, artículos varios"),
        ("Servicios", "Luz, agua, internet, suscripciones"),
        ("Otros", "Gastos varios no categorizados"),
    ]
    
    with get_session() as session:
        for name, description in predefined_categories:
            # Check if category already exists
            statement = select(Category).where(Category.name == name)
            existing = session.exec(statement).first()
            
            if not existing:
                category = Category(
                    name=name,
                    description=description,
                    is_system=True
                )
                session.add(category)
                logger.info(f"Created category: {name}")
            else:
                logger.debug(f"Category already exists: {name}")
        
        session.commit()
        logger.info("Predefined categories initialized")


def get_session() -> Session:
    """Get a database session."""
    return Session(engine)
