from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.engine import Engine
from typing import Generator
import logging

from server.app.config import settings

logger = logging.getLogger(__name__)

# Create the SQLAlchemy engine
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,
    echo=settings.DEBUG,
)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class
Base = declarative_base()


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """Set SQLite pragmas for better performance and features."""
    if 'sqlite' in settings.DATABASE_URL:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA synchronous=NORMAL")
        cursor.execute("PRAGMA cache_size=1000")
        cursor.execute("PRAGMA temp_store=memory")
        cursor.close()


def get_db() -> Generator[Session, None, None]:
    """
    Dependency function to get database session.
    
    Yields:
        Session: SQLAlchemy database session
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def create_tables():
    """Create all tables in the database."""
    try:
        # Import models to register them with Base
        from server.app.models import User, Store, Product, Price, PriceHistory
        
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        raise


def drop_tables():
    """Drop all tables in the database."""
    try:
        Base.metadata.drop_all(bind=engine)
        logger.info("Database tables dropped successfully")
    except Exception as e:
        logger.error(f"Error dropping database tables: {e}")
        raise


def init_db():
    """Initialize the database with default data."""
    try:
        create_tables()
        
        # Create default stores
        from server.app.models import Store
        db = SessionLocal()
        
        default_stores = [
            {
                "name": "Gourmet",
                "url": "https://gourmet.com.eg",
                "type": "supermarket",
                "scraper_class": "GourmetScraper",
                "description": "Premium supermarket chain"
            },
            {
                "name": "Metro",
                "url": "https://metro.com.eg",
                "type": "supermarket", 
                "scraper_class": "MetroScraper",
                "description": "International supermarket chain"
            },
            {
                "name": "Spinneys",
                "url": "https://spinneys.com",
                "type": "supermarket",
                "scraper_class": "SpinneysScraper",
                "description": "Premium grocery store"
            }
        ]
        
        for store_data in default_stores:
            existing_store = db.query(Store).filter(Store.name == store_data["name"]).first()
            if not existing_store:
                store = Store(**store_data)
                db.add(store)
        
        db.commit()
        db.close()
        
        logger.info("Database initialized with default data")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise


class DatabaseManager:
    """Database management utilities."""
    
    @staticmethod
    def health_check() -> bool:
        """Check if database connection is healthy."""
        try:
            db = SessionLocal()
            db.execute("SELECT 1")
            db.close()
            return True
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False
    
    @staticmethod
    def get_connection_info() -> dict:
        """Get database connection information."""
        return {
            "url": settings.DATABASE_URL.split("@")[-1] if "@" in settings.DATABASE_URL else "local",
            "engine": str(engine.url.drivername),
            "pool_size": engine.pool.size(),
            "checked_out": engine.pool.checkedout(),
        }
    
    @staticmethod
    def reset_database():
        """Reset database by dropping and recreating all tables."""
        logger.warning("Resetting database - all data will be lost!")
        drop_tables()
        init_db()


# Database instance
db_manager = DatabaseManager()