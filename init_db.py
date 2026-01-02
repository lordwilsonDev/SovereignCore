#!/usr/bin/env python3
"""Initialize SovereignCore database with tables and default users."""
import sys
from database import init_db, create_default_users


def main():
    """Main initialization function."""
    print("="*50)
    print("SovereignCore Database Initialization")
    print("="*50)
    print()
    
    try:
        # Create tables
        print("Creating database tables...")
        init_db()
        print()
        
        # Create default users
        print("Creating default users...")
        create_default_users()
        print()
        
        print("="*50)
        print("✓ Database initialization successful!")
        print("="*50)
        print()
        print("Default credentials:")
        print("  Username: testuser")
        print("  Password: testpass123")
        print()
        print("  Username: admin")
        print("  Password: admin123")
        print()
        print("⚠️  IMPORTANT: Change these passwords before deploying to production!")
        print()
        
        return 0
        
    except Exception as e:
        print()
        print("="*50)
        print("✗ Database initialization failed!")
        print("="*50)
        print(f"Error: {e}")
        print()
        return 1


if __name__ == "__main__":
    sys.exit(main())
