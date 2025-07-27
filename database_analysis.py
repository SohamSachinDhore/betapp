#!/usr/bin/env python3
"""
Database Operations Summary Report
"""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def analyze_database_operations():
    """Analyze all database operations happening in the system"""
    
    print("🔍 DATABASE OPERATIONS ANALYSIS")
    print("=" * 70)
    
    try:
        from src.database.db_manager import create_database_manager
        from src.business.data_processor import DataProcessor
        
        # Create database manager
        db_manager = create_database_manager()
        
        print(f"📁 Database File: {db_manager.db_path}")
        print(f"📊 Database Size: {os.path.getsize(db_manager.db_path):,} bytes")
        
        # Analyze tables and their purposes
        print("\n📋 DATABASE SCHEMA ANALYSIS:")
        print("-" * 50)
        
        conn = db_manager.get_connection()
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = cursor.fetchall()
        
        for table in tables:
            table_name = table[0]
            if table_name == 'sqlite_sequence':
                continue
                
            print(f"\n🗃️  TABLE: {table_name}")
            
            # Get table info
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            
            print("   📊 Columns:")
            for col in columns:
                col_name, col_type, not_null, default, pk = col[1], col[2], col[3], col[4], col[5]
                pk_marker = " (PRIMARY KEY)" if pk else ""
                null_marker = " NOT NULL" if not_null else ""
                default_marker = f" DEFAULT {default}" if default else ""
                print(f"      • {col_name}: {col_type}{pk_marker}{null_marker}{default_marker}")
            
            # Get row count
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"   📈 Records: {count:,}")
            
            # Show purpose based on table name
            table_purposes = {
                'customers': 'Store customer information and IDs',
                'bazars': 'Store bazar/market names and display settings',
                'universal_log': 'Log all data entries with customer, date, bazar info',
                'pana_table': 'Store PANA number-value pairs by date+bazar',
                'time_table': 'Store time column values by customer+date+bazar',
                'customer_bazar_summary': 'Store customer summary by date',
                'pana_numbers': 'Reference table of valid PANA numbers',
                'type_table_sp': 'SP (Single Pana) table data',
                'type_table_dp': 'DP (Double Pana) table data',
                'type_table_cp': 'CP (Cross Pana) table data'
            }
            
            if table_name in table_purposes:
                print(f"   🎯 Purpose: {table_purposes[table_name]}")
        
        print("\n\n🔄 DATABASE OPERATIONS IN GUI WORKFLOW:")
        print("-" * 50)
        
        print("1️⃣  GUI STARTUP:")
        print("   • Creates DatabaseManager with './data/rickymama.db'")
        print("   • Initializes database schema if needed")
        print("   • Loads customers list for dropdown")
        print("   • Loads bazars list for dropdown")
        
        print("\n2️⃣  DATA VALIDATION (Real-time):")
        print("   • Creates DataProcessor with database")
        print("   • Loads SP/DP/CP table data for validation")
        print("   • Loads pana_numbers for reference validation")
        print("   • Parses input without saving")
        print("   • No database writes during validation")
        
        print("\n3️⃣  DATA SUBMISSION:")
        print("   • Validates customer exists or creates new one")
        print("   • Processes mixed input through MixedInputParser")
        print("   • Saves to multiple tables based on entry types:")
        print("     - universal_log: All entries for audit trail")
        print("     - pana_table: PANA entries (unique per date+bazar)")
        print("     - time_table: Time entries (unique per customer+date+bazar)")
        print("     - customer_bazar_summary: Aggregated summaries")
        
        print("\n4️⃣  TABLE VIEWING:")
        print("   • Queries data with filters (date, customer, bazar)")
        print("   • Real-time data refresh")
        print("   • Export operations")
        
        # Analyze specific database operations during parsing
        print("\n\n⚙️  PARSING DATABASE OPERATIONS:")
        print("-" * 50)
        
        # Test with database
        processor_with_db = DataProcessor(db_manager)
        print("✅ DataProcessor with database:")
        print("   • Loads SP table for TYPE validation")
        print("   • Loads DP table for TYPE validation") 
        print("   • Loads CP table for TYPE validation")
        print("   • Loads pana_numbers for PANA validation")
        print("   • Total database reads during initialization: ~4 queries")
        
        # Test without database (GUI fallback)
        print("\n❌ DataProcessor without database (GUI fallback):")
        print("   • Attempts to load tables but fails gracefully")
        print("   • Still parses input patterns correctly")
        print("   • Validation is pattern-based, not reference-based")
        print("   • No database dependency for basic parsing")
        
        # Show transaction behavior
        print("\n\n💾 TRANSACTION HANDLING:")
        print("-" * 50)
        print("• WAL (Write-Ahead Logging) mode enabled")
        print("• Thread-local connections for safety")
        print("• Automatic rollback on errors")
        print("• Foreign key constraints enabled")
        print("• Connection pooling with timeout (30s)")
        
        # Show current database status
        print("\n\n📊 CURRENT DATABASE STATUS:")
        print("-" * 50)
        
        customers = db_manager.get_all_customers()
        print(f"👥 Customers: {len(customers)}")
        
        bazars = db_manager.get_all_bazars()
        print(f"🏢 Bazars: {len(bazars)}")
        
        # Get universal log stats
        query = "SELECT COUNT(*) as count, SUM(value) as total_value FROM universal_log"
        result = db_manager.execute_query(query)[0]
        print(f"📝 Total Entries: {result['count']:,}")
        print(f"💰 Total Value: ₹{result['total_value'] or 0:,}")
        
        # Get recent activity
        query = """
        SELECT entry_date, COUNT(*) as entries, SUM(value) as daily_total 
        FROM universal_log 
        GROUP BY entry_date 
        ORDER BY entry_date DESC 
        LIMIT 5
        """
        recent = db_manager.execute_query(query)
        
        if recent:
            print(f"\n📅 Recent Activity:")
            for day in recent:
                print(f"   {day['entry_date']}: {day['entries']} entries, ₹{day['daily_total']:,}")
        
        print("\n\n🔧 DATABASE FILES:")
        print("-" * 50)
        data_dir = os.path.dirname(db_manager.db_path)
        for file in os.listdir(data_dir):
            if file.endswith(('.db', '.db-wal', '.db-shm')):
                path = os.path.join(data_dir, file)
                size = os.path.getsize(path)
                print(f"📄 {file}: {size:,} bytes")
        
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    analyze_database_operations()
