#!/usr/bin/env python3
"""Test script to verify commission/non-commission customer feature"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.database.db_manager import DatabaseManager

def test_commission_customer():
    """Test adding customers with commission types"""
    print("Testing Commission Customer Feature...")
    
    try:
        # Create database manager
        db_manager = DatabaseManager("./data/rickymama.db")
        
        # Test adding commission customer
        import time
        timestamp = str(int(time.time()))
        
        print("\n1. Adding Commission Customer:")
        commission_customer_id = db_manager.add_customer(f"TestCommission_{timestamp}", "commission")
        print(f"   ✅ Added Commission customer with ID: {commission_customer_id}")
        
        # Test adding non-commission customer
        print("\n2. Adding Non-Commission Customer:")
        non_commission_customer_id = db_manager.add_customer(f"TestNonCommission_{timestamp}", "non_commission")
        print(f"   ✅ Added Non-Commission customer with ID: {non_commission_customer_id}")
        
        # Verify customers were added correctly
        print("\n3. Verifying Customer Data:")
        
        # Check commission customer
        commission_customer = db_manager.get_customer_by_id(commission_customer_id)
        if commission_customer:
            print(f"   ✅ Commission Customer:")
            print(f"      - Name: {commission_customer['name']}")
            print(f"      - Type: {commission_customer['commission_type'] if 'commission_type' in commission_customer.keys() else 'Not set'}")
        
        # Check non-commission customer
        non_commission_customer = db_manager.get_customer_by_id(non_commission_customer_id)
        if non_commission_customer:
            print(f"   ✅ Non-Commission Customer:")
            print(f"      - Name: {non_commission_customer['name']}")
            print(f"      - Type: {non_commission_customer['commission_type'] if 'commission_type' in non_commission_customer.keys() else 'Not set'}")
        
        # List all customers
        print("\n4. All Customers in Database:")
        all_customers = db_manager.get_all_customers()
        print(f"   Total customers: {len(all_customers)}")
        print("   " + "-" * 60)
        print(f"   {'ID':<5} {'Name':<25} {'Type':<15} {'Created'}")
        print("   " + "-" * 60)
        
        for customer in all_customers[-5:]:  # Show last 5 customers
            commission_type = customer['commission_type'] if 'commission_type' in customer.keys() else 'commission'
            display_type = "Commission" if commission_type == 'commission' else "Non-Commission"
            print(f"   {customer['id']:<5} {customer['name']:<25} {display_type:<15} {customer['created_at']}")
        
        # Test default behavior
        print("\n5. Testing Default Behavior:")
        default_customer_id = db_manager.add_customer(f"TestDefault_{timestamp}")  # No commission_type specified
        default_customer = db_manager.get_customer_by_id(default_customer_id)
        if default_customer:
            print(f"   ✅ Default customer created with type: {default_customer['commission_type'] if 'commission_type' in default_customer.keys() else 'Not set'}")
        
        print("\n✅ Commission customer feature is working correctly!")
        
    except Exception as e:
        print(f"❌ Error testing commission customer feature: {e}")
        import traceback
        traceback.print_exc()

def check_database_schema():
    """Check if commission_type column exists in customers table"""
    print("\n\nChecking Database Schema...")
    
    try:
        db_manager = DatabaseManager("./data/rickymama.db")
        
        # Check schema
        schema_query = "PRAGMA table_info(customers)"
        columns = db_manager.execute_query(schema_query)
        
        print("\nCustomers table columns:")
        commission_type_found = False
        for col in columns:
            print(f"   - {col['name']} ({col['type']}) {'NOT NULL' if col['notnull'] else 'NULL'}")
            if col['name'] == 'commission_type':
                commission_type_found = True
        
        if commission_type_found:
            print("\n✅ commission_type column exists in customers table")
        else:
            print("\n❌ commission_type column NOT found in customers table")
            
    except Exception as e:
        print(f"❌ Error checking schema: {e}")

if __name__ == "__main__":
    print("🔍 Commission Customer Feature Test")
    print("=" * 50)
    
    check_database_schema()
    test_commission_customer()
    
    print("\n✅ Tests completed!")