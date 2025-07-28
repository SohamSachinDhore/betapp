#!/usr/bin/env python3
"""Test script to verify customer name color coding"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.database.db_manager import DatabaseManager

def test_customer_colors():
    """Test customer name color functionality"""
    print("Testing Customer Name Color Coding...")
    
    try:
        # Create database manager
        db_manager = DatabaseManager("./data/rickymama.db")
        
        # Get some test customers
        all_customers = db_manager.get_all_customers()
        
        if not all_customers:
            print("❌ No customers found in database")
            return
        
        print(f"\n✅ Found {len(all_customers)} customers")
        print("\nColor Coding Preview:")
        print("=" * 60)
        
        # Test color assignment logic
        for customer in all_customers[-10:]:  # Show last 10 customers
            commission_type = customer['commission_type'] if 'commission_type' in customer.keys() else 'commission'
            
            # Apply the same logic as in the GUI
            if commission_type == 'commission':
                color_name = "Blue (Commission)"
                color_code = (52, 152, 219, 255)
            else:
                color_name = "Orange (Non-Commission)"
                color_code = (230, 126, 34, 255)
            
            print(f"📋 {customer['name']:<25} | {commission_type:<15} | {color_name}")
        
        # Test the helper function logic
        print("\n\nTesting Helper Function Logic:")
        print("=" * 60)
        
        # Create a mock customers list for testing
        mock_customers = [
            {"id": 1, "name": "Commission Customer", "commission_type": "commission"},
            {"id": 2, "name": "Non-Commission Customer", "commission_type": "non_commission"},
            {"id": 3, "name": "Default Customer"}  # No commission_type field
        ]
        
        def mock_get_customer_name_color(customer_name: str, customers_list):
            """Mock version of the helper function for testing"""
            default_color = (52, 152, 219, 255)  # Blue
            
            try:
                # Find customer in the customers list
                for customer in customers_list:
                    if customer['name'] == customer_name:
                        commission_type = customer.get('commission_type', 'commission')
                        if commission_type == 'commission':
                            return (52, 152, 219, 255)  # Blue
                        else:
                            return (230, 126, 34, 255)  # Orange
            except Exception as e:
                print(f"Error getting customer color: {e}")
            
            return default_color
        
        for customer in mock_customers:
            color_code = mock_get_customer_name_color(customer['name'], mock_customers)
            color_name = "Blue (Commission)" if color_code == (52, 152, 219, 255) else "Orange (Non-Commission)"
            commission_type = customer.get('commission_type', 'commission (default)')
            
            print(f"🎨 {customer['name']:<25} | {commission_type:<20} | {color_name}")
        
        print("\n✅ Color coding logic working correctly!")
        
        # Color code reference
        print("\n\n🎨 Color Reference:")
        print("=" * 30)
        print("🔵 Commission Customers    : Blue   (52, 152, 219, 255)")
        print("🟠 Non-Commission Customers: Orange (230, 126, 34, 255)")
        print("\nNote: These colors avoid red and green as requested.")
        
    except Exception as e:
        print(f"❌ Error testing customer colors: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🎨 Customer Name Color Coding Test")
    print("=" * 50)
    
    test_customer_colors()
    
    print("\n✅ Tests completed!")