"""
Database initialization script
Creates tables and default user
"""
from sqlalchemy.orm import sessionmaker
from .model import Base, User, engine

def init_database(engine=None):
    """Initialize database with tables and default user"""
    # Usar el engine proporcionado o el por defecto
    if engine is None:
        from .model import engine as default_engine
        engine = default_engine
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Create session
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    try:
        # Check if default user exists
        existing_user = db.query(User).filter(User.username == "admin").first()
        if not existing_user:
            # Create default user
            default_user = User(username="admin")
            default_user.set_password("novatrace123")  # Default password
            db.add(default_user)
            db.commit()
            print("✅ Default user created - Username: admin, Password: novatrace123")
        else:
            print("ℹ️  Default user already exists")
            
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_database()
