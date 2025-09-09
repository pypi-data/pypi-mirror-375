from .novatrace import NovaTrace

# Initialize database with metrics collection when module is imported
def initialize_with_metrics():
    """Initialize NovaTrace with historical system metrics support"""
    try:
        from .database.init_db import init_database_with_metrics_collection
        init_database_with_metrics_collection(start_collection=False)  # API will start collection
        print("✅ NovaTrace initialized with historical metrics support")
    except Exception as e:
        print(f"⚠️  Warning: Could not initialize metrics support: {e}")
        # Fall back to regular initialization
        try:
            from .database.init_db import init_database
            init_database()
            print("✅ NovaTrace initialized (without historical metrics)")
        except Exception as e2:
            print(f"❌ Error initializing NovaTrace: {e2}")

# Auto-initialize when imported
initialize_with_metrics()
