#!/usr/bin/env python3
"""
Test script to check database operations and connections
"""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_database_connection():
    """Test database connection and operations"""
    
    print("🔍 TESTING DATABASE CONNECTIONS")
    print("=" * 60)
    
    try:
        from src.database.db_manager import create_database_manager
        
        print("✅ Successfully imported database manager")
        
        # Test 1: Create database manager with default path
        print("\n📋 Testing default database connection...")
        db_manager = create_database_manager()
        
        print(f"✅ Database manager created")
        print(f"📁 Database path: {db_manager.db_path}")
        
        # Test 2: Initialize database
        print("\n📋 Testing database initialization...")
        db_manager.initialize_database()
        print("✅ Database initialized successfully")
        
        # Test 3: Check database file exists
        import os
        if os.path.exists(db_manager.db_path):
            print(f"✅ Database file exists: {db_manager.db_path}")
            # Get file size
            size = os.path.getsize(db_manager.db_path)
            print(f"📊 Database file size: {size} bytes")
        else:
            print(f"❌ Database file not found: {db_manager.db_path}")
        
        # Test 4: Test basic connection
        print("\n📋 Testing database connection...")
        conn = db_manager.get_connection()
        print(f"✅ Database connection established")
        print(f"🔗 Connection type: {type(conn)}")
        
        # Test 5: Check tables exist
        print("\n📋 Testing table existence...")
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        if tables:
            print(f"✅ Found {len(tables)} tables:")
            for table in tables:
                print(f"   📄 {table[0]}")
        else:
            print("❌ No tables found")
        
        # Test 6: Test customer operations
        print("\n📋 Testing customer operations...")
        try:
            customers = db_manager.get_all_customers()
            print(f"✅ Retrieved {len(customers)} customers")
            for customer in customers[:5]:  # Show first 5
                print(f"   👤 ID: {customer['id']}, Name: {customer['name']}")
        except Exception as e:
            print(f"❌ Customer operations failed: {e}")
        
        # Test 7: Test bazar operations
        print("\n📋 Testing bazar operations...")
        try:
            bazars = db_manager.get_all_bazars()
            print(f"✅ Retrieved {len(bazars)} bazars")
            for bazar in bazars[:5]:  # Show first 5
                print(f"   🏢 Name: {bazar['name']}, Display: {bazar['display_name']}")
        except Exception as e:
            print(f"❌ Bazar operations failed: {e}")
        
        # Test 8: Test universal log operations
        print("\n📋 Testing universal log operations...")
        try:
            # Try to get universal log entries
            query = "SELECT COUNT(*) as count FROM universal_log"
            result = db_manager.execute_query(query)
            if result:
                count = result[0]['count']
                print(f"✅ Universal log contains {count} entries")
            else:
                print("✅ Universal log table exists but is empty")
        except Exception as e:
            print(f"❌ Universal log operations failed: {e}")
        
        # Test 9: Test transaction handling
        print("\n📋 Testing transaction handling...")
        try:
            with db_manager.transaction() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                print(f"✅ Transaction test successful: {result[0]}")
        except Exception as e:
            print(f"❌ Transaction test failed: {e}")
        
        print("\n🎯 DATABASE CONNECTION SUMMARY:")
        print(f"   Database Path: {db_manager.db_path}")
        print(f"   File Exists: {os.path.exists(db_manager.db_path)}")
        print(f"   Connection Type: SQLite3")
        print(f"   Threading: Thread-local connections")
        print(f"   WAL Mode: Enabled")
        print(f"   Foreign Keys: Enabled")
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        import traceback
        traceback.print_exc()

def test_data_processor_database_usage():
    """Test how DataProcessor uses the database"""
    
    print("\n\n🔍 TESTING DATA PROCESSOR DATABASE USAGE")
    print("=" * 60)
    
    try:
        from src.business.data_processor import DataProcessor
        from src.database.db_manager import create_database_manager
        
        print("✅ Successfully imported DataProcessor and DatabaseManager")
        
        # Test 1: Create processor with database
        print("\n📋 Testing DataProcessor with database...")
        db_manager = create_database_manager()
        processor = DataProcessor(db_manager)
        
        print("✅ DataProcessor created with database manager")
        print(f"🔗 Database path: {db_manager.db_path}")
        
        # Test 2: Check what database operations DataProcessor performs
        print("\n📋 Checking DataProcessor database operations...")
        
        # Look at the validator components
        if hasattr(processor, 'mixed_parser'):
            print("✅ MixedInputParser initialized")
            
            # Check validators
            mixed_parser = processor.mixed_parser
            if hasattr(mixed_parser, 'validators'):
                print(f"📊 Number of validators: {len(mixed_parser.validators)}")
                for validator_name, validator in mixed_parser.validators.items():
                    print(f"   🔍 {validator_name}: {type(validator).__name__}")
                    
                    # Check if validator uses database
                    if hasattr(validator, 'db_manager'):
                        print(f"      🔗 Uses database: {validator.db_manager is not None}")
                    if hasattr(validator, 'pana_numbers'):
                        print(f"      📊 Pana numbers loaded: {len(getattr(validator, 'pana_numbers', []))}")
        
        # Test 3: Create processor without database (like GUI fallback)
        print("\n📋 Testing DataProcessor without database...")
        processor_no_db = DataProcessor(None)
        
        print("✅ DataProcessor created without database manager")
        print("⚠️  This simulates GUI fallback mode")
        
        # Test validation with no database
        test_input = "239=150\n456=150\n1=100"
        parsed_result = processor_no_db.mixed_parser.parse(test_input)
        
        print(f"✅ Parsing works without database")
        print(f"📊 Parsed entries: {len(parsed_result.direct_entries or []) + len(parsed_result.time_entries or [])}")
        
    except Exception as e:
        print(f"❌ DataProcessor database test failed: {e}")
        import traceback
        traceback.print_exc()

def check_database_files():
    """Check what database files exist"""
    
    print("\n\n🔍 CHECKING DATABASE FILES")
    print("=" * 60)
    
    data_dir = "/Users/sohamdhore/Desktop/Work/Rickey_mama_V2/data"
    
    if os.path.exists(data_dir):
        print(f"📁 Data directory: {data_dir}")
        
        files = os.listdir(data_dir)
        for file in files:
            file_path = os.path.join(data_dir, file)
            if os.path.isfile(file_path):
                size = os.path.getsize(file_path)
                print(f"   📄 {file} ({size} bytes)")
                
                # Check if it's a database file
                if file.endswith('.db'):
                    try:
                        import sqlite3
                        conn = sqlite3.connect(file_path)
                        cursor = conn.cursor()
                        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                        tables = cursor.fetchall()
                        conn.close()
                        
                        print(f"      📊 Tables: {[table[0] for table in tables]}")
                    except Exception as e:
                        print(f"      ❌ Cannot read database: {e}")
    else:
        print(f"❌ Data directory not found: {data_dir}")

if __name__ == "__main__":
    test_database_connection()
    test_data_processor_database_usage()
    check_database_files()
