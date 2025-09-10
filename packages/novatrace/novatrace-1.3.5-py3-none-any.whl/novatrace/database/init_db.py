"""
Database initialization script
Creates tables and default user
"""
from sqlalchemy.orm import sessionmaker
from .model import Base, User, engine

def init_database(engine=None, debug=False):
    """Initialize database with tables and default user"""
    # Usar el engine proporcionado o el por defecto
    if engine is None:
        from .model import engine as default_engine
        engine = default_engine
    
    # Create all tables (including new SystemMetrics table)
    Base.metadata.create_all(bind=engine)
    if debug:
        print("✅ Database tables created (including SystemMetrics for historical data)")
    
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
            if debug:
                print("✅ Default user created - Username: admin, Password: novatrace123")
        else:
            if debug:
                print("ℹ️  Default user already exists")
            
    except Exception as e:
        if debug:
            print(f"❌ Error initializing database: {e}")
        db.rollback()
    finally:
        db.close()

def init_database_with_metrics_collection(engine=None, start_collection=True, debug=False):
    """
    Initialize database and optionally start metrics collection
    
    Args:
        engine: Database engine to use
        start_collection: Whether to start the background metrics collection
        debug: Whether to show debug messages
    """
    # Initialize the database first
    init_database(engine, debug=debug)
    
    if start_collection:
        try:
            # Start metrics collection
            from ..system.metrics_collector import start_metrics_collection
            task = start_metrics_collection(engine=engine, interval_seconds=300)  # 5 minutes
            if debug:
                print("✅ System metrics collection started (5-minute intervals)")
                print("📊 Historical system data will be available at:")
                print("   - /api/system/metrics/historical")
                print("   - /api/system/metrics/timerange")
                print("   - /api/system/metrics/compare")
            return task
        except Exception as e:
            if debug:
                print(f"⚠️  Warning: Could not start metrics collection: {e}")
                print("   Historical metrics will not be available until collection is started")
            return None
    
    return None

if __name__ == "__main__":
    init_database_with_metrics_collection(debug=True)
