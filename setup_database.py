#!/usr/bin/env python3
"""
Simple database setup script for RickyMama Project

This script initializes a fresh database with all required tables and initial data.
Use this when setting up the application on a new computer.

Usage:
    python setup_database.py          # Create new database
    python setup_database.py --reset  # Reset existing database (WARNING: This will delete all data!)
"""

import os
import sys
import argparse
from datetime import datetime

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def setup_fresh_database():
    """Set up a completely fresh database"""
    print("🚀 RickyMama Database Setup")
    print("=" * 50)
    
    try:
        from src.database.db_manager import DatabaseManager
        
        db_path = "./data/rickymama.db"
        
        # Check if database already exists
        if os.path.exists(db_path):
            print(f"⚠️  Database already exists at: {db_path}")
            print("   This will create a NEW, EMPTY database.")
            print("   Your existing data will NOT be transferred.")
            
            response = input("\nDo you want to continue? (yes/no): ").lower().strip()
            if response not in ['yes', 'y']:
                print("❌ Setup cancelled.")
                return False
            
            # Backup existing database
            backup_path = f"{db_path}.backup.{int(datetime.now().timestamp())}"
            import shutil
            shutil.copy2(db_path, backup_path)
            print(f"✅ Backed up existing database to: {backup_path}")
            
            # Remove existing database
            os.remove(db_path)
            print("✅ Removed existing database")
        
        # Create database directory if needed
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        # Initialize fresh database
        print("🔄 Creating fresh database...")
        db_manager = DatabaseManager(db_path)
        db_manager.initialize_database()
        
        # Verify setup
        print("🔍 Verifying database setup...")
        
        # Check tables
        tables = db_manager.execute_query(
            "SELECT name FROM sqlite_master WHERE type='table'"
        )
        print(f"✅ Created {len(tables)} tables")
        
        # Check initial data
        customers = db_manager.execute_query("SELECT COUNT(*) as count FROM customers")
        bazars = db_manager.execute_query("SELECT COUNT(*) as count FROM bazars")
        pana_numbers = db_manager.execute_query("SELECT COUNT(*) as count FROM pana_numbers")
        
        print(f"✅ Initial data loaded:")
        print(f"   - Customers: {customers[0]['count']}")
        print(f"   - Bazars: {bazars[0]['count']}")
        print(f"   - Pana Numbers: {pana_numbers[0]['count']}")
        
        db_manager.close()
        
        print("\n🎉 DATABASE SETUP COMPLETE!")
        print("=" * 50)
        print("✅ Fresh database created successfully")
        print("✅ All tables and initial data loaded")
        print("✅ Ready to run the application")
        print("\nNext steps:")
        print("1. Run: python main_gui_working.py")
        print("2. Add your customers and start entering data")
        print("\n📝 Note: This is a FRESH database with NO existing data.")
        
        return True
        
    except Exception as e:
        print(f"❌ Database setup failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def reset_database():
    """Reset database (delete all data and recreate)"""
    print("⚠️  DATABASE RESET")
    print("=" * 50)
    print("This will DELETE ALL your existing data!")
    print("Make sure you have exported your data before proceeding.")
    
    response = input("\nAre you absolutely sure? Type 'DELETE ALL DATA' to confirm: ")
    if response != "DELETE ALL DATA":
        print("❌ Reset cancelled.")
        return False
    
    try:
        from src.database.db_manager import DatabaseManager
        
        db_path = "./data/rickymama.db"
        
        if os.path.exists(db_path):
            # Create backup
            backup_path = f"{db_path}.reset_backup.{int(datetime.now().timestamp())}"
            import shutil
            shutil.copy2(db_path, backup_path)
            print(f"✅ Created backup: {backup_path}")
            
            # Remove database
            os.remove(db_path)
            print("✅ Deleted existing database")
        
        # Create fresh database
        print("🔄 Creating fresh database...")
        db_manager = DatabaseManager(db_path)
        db_manager.initialize_database()
        db_manager.close()
        
        print("🎉 DATABASE RESET COMPLETE!")
        print("✅ All data has been deleted")
        print("✅ Fresh database created")
        
        return True
        
    except Exception as e:
        print(f"❌ Database reset failed: {e}")
        return False

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='RickyMama Database Setup')
    parser.add_argument('--reset', action='store_true', 
                       help='Reset database (WARNING: Deletes all data)')
    
    args = parser.parse_args()
    
    if args.reset:
        success = reset_database()
    else:
        success = setup_fresh_database()
    
    if success:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
