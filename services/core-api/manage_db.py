#!/usr/bin/env python3
"""
Database management script for ANZx.ai platform
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from app.models.database import init_db, check_db_health, engine
from app.models.user import *  # Import all models
from sqlalchemy import text


def run_migrations():
    """Run Alembic migrations"""
    print("🔄 Running database migrations...")
    try:
        # Use alembic command directly
        result = subprocess.run([
            sys.executable, "-c", 
            "import alembic.config; alembic.config.main(['upgrade', 'head'])"
        ], cwd=Path(__file__).parent, check=True, capture_output=True, text=True)
        
        print("✅ Migrations completed successfully")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Migration failed: {e}")
        if e.stdout:
            print("STDOUT:", e.stdout)
        if e.stderr:
            print("STDERR:", e.stderr)
        return False
    except Exception as e:
        print(f"❌ Migration error: {e}")
        return False


def create_migration(message: str):
    """Create a new migration"""
    print(f"📝 Creating migration: {message}")
    try:
        result = subprocess.run([
            sys.executable, "-c", 
            f"import alembic.config; alembic.config.main(['revision', '--autogenerate', '-m', '{message}'])"
        ], cwd=Path(__file__).parent, check=True, capture_output=True, text=True)
        
        print("✅ Migration created successfully")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Migration creation failed: {e}")
        if e.stdout:
            print("STDOUT:", e.stdout)
        if e.stderr:
            print("STDERR:", e.stderr)
        return False


def init_database():
    """Initialize database with tables and extensions"""
    print("🏗️  Initializing database...")
    try:
        init_db()
        print("✅ Database initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return False


def check_health():
    """Check database health"""
    print("🏥 Checking database health...")
    try:
        health = check_db_health()
        
        if health["status"] == "healthy":
            print("✅ Database is healthy")
            print(f"   Extensions: {', '.join(health['extensions'])}")
            print(f"   Pool size: {health['pool_size']}")
            print(f"   Checked out: {health['checked_out']}")
            print(f"   Overflow: {health['overflow']}")
            print(f"   Checked in: {health['checked_in']}")
        else:
            print(f"❌ Database is unhealthy: {health.get('error', 'Unknown error')}")
        
        return health["status"] == "healthy"
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False


def reset_database():
    """Reset database (DROP ALL TABLES - USE WITH CAUTION)"""
    print("⚠️  WARNING: This will DROP ALL TABLES!")
    confirm = input("Type 'RESET' to confirm: ")
    
    if confirm != "RESET":
        print("❌ Reset cancelled")
        return False
    
    print("🗑️  Dropping all tables...")
    try:
        # Drop all tables
        with engine.connect() as conn:
            # Get all table names
            result = conn.execute(text("""
                SELECT tablename FROM pg_tables 
                WHERE schemaname = 'public' 
                AND tablename NOT LIKE 'alembic%'
            """))
            tables = [row[0] for row in result]
            
            if tables:
                # Drop tables with CASCADE
                for table in tables:
                    conn.execute(text(f'DROP TABLE IF EXISTS "{table}" CASCADE'))
                conn.commit()
                print(f"✅ Dropped {len(tables)} tables")
            else:
                print("ℹ️  No tables to drop")
        
        return True
    except Exception as e:
        print(f"❌ Reset failed: {e}")
        return False


def seed_data():
    """Seed database with sample data"""
    print("🌱 Seeding database with sample data...")
    try:
        from sqlalchemy.orm import sessionmaker
        Session = sessionmaker(bind=engine)
        session = Session()
        
        # Create sample organization
        org = Organization(
            name="Demo Organization",
            description="Sample organization for testing",
            region="AU",
            subscription_plan="pro"
        )
        session.add(org)
        session.flush()
        
        # Create sample user
        user = User(
            firebase_uid="demo-user-123",
            email="demo@anzx.ai",
            display_name="Demo User",
            organization_id=org.id,
            role="admin",
            privacy_consent=True,
            email_verified=True
        )
        session.add(user)
        session.flush()
        
        # Create sample assistant
        assistant = Assistant(
            name="Demo Support Assistant",
            description="Sample support assistant",
            type="support",
            organization_id=org.id,
            system_prompt="You are a helpful customer support assistant.",
            is_active=True,
            deployment_status="deployed"
        )
        session.add(assistant)
        
        session.commit()
        session.close()
        
        print("✅ Sample data created successfully")
        print(f"   Organization: {org.name} ({org.id})")
        print(f"   User: {user.email} ({user.id})")
        print(f"   Assistant: {assistant.name} ({assistant.id})")
        
        return True
    except Exception as e:
        print(f"❌ Seeding failed: {e}")
        return False


def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(description="ANZx.ai Database Management")
    parser.add_argument("command", choices=[
        "migrate", "create-migration", "init", "health", "reset", "seed"
    ], help="Command to execute")
    parser.add_argument("-m", "--message", help="Migration message (for create-migration)")
    
    args = parser.parse_args()
    
    print("🗄️  ANZx.ai Database Management")
    print("=" * 40)
    
    # Set database URL if not set
    if not os.getenv("DATABASE_URL"):
        os.environ["DATABASE_URL"] = "postgresql://anzx_user:anzx_password@localhost:5432/anzx_platform"
        print(f"Using default DATABASE_URL: {os.environ['DATABASE_URL']}")
    
    success = False
    
    if args.command == "migrate":
        success = run_migrations()
    elif args.command == "create-migration":
        if not args.message:
            print("❌ Migration message required. Use -m 'message'")
            sys.exit(1)
        success = create_migration(args.message)
    elif args.command == "init":
        success = init_database()
    elif args.command == "health":
        success = check_health()
    elif args.command == "reset":
        success = reset_database()
    elif args.command == "seed":
        success = seed_data()
    
    if success:
        print("\n✅ Operation completed successfully")
        sys.exit(0)
    else:
        print("\n❌ Operation failed")
        sys.exit(1)


if __name__ == "__main__":
    main()