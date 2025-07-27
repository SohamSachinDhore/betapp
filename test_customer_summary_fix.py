#!/usr/bin/env python3
"""Test script to verify customer summary table fixes"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.database.db_manager import DatabaseManager

def test_customer_summary_data():
    """Test customer summary data retrieval"""
    print("Testing Customer Summary Data...")
    
    try:
        # Create database manager
        db_manager = DatabaseManager("./data/rickymama.db")
        
        # Get recent data
        summary_data = db_manager.get_customer_bazar_summary_by_date("2025-01-27")
        
        if summary_data:
            print("\n✅ Customer Summary Data Found:")
            print("=" * 80)
            print(f"{'Customer':<15} {'T.O':<8} {'T.K':<8} {'M.O':<8} {'M.K':<8} {'K.O':<8} {'K.K':<8} {'NMO':<8} {'NMK':<8} {'B.O':<8} {'B.K':<8} {'Total':<10}")
            print("-" * 80)
            
            for entry in summary_data:
                print(f"{entry['customer_name']:<15} {entry['to_total']:<8} {entry['tk_total']:<8} {entry['mo_total']:<8} {entry['mk_total']:<8} {entry['ko_total']:<8} {entry['kk_total']:<8} {entry['nmo_total']:<8} {entry['nmk_total']:<8} {entry['bo_total']:<8} {entry['bk_total']:<8} {entry['grand_total']:<10}")
            
            print(f"\n📊 Total Records: {len(summary_data)}")
            
            # Check for K.K column specifically
            if 'kk_total' in summary_data[0].keys():
                print("✅ K.K column (kk_total) exists in database")
            else:
                print("❌ K.K column (kk_total) missing from database")
                
        else:
            print("⚠️ No data found for 2025-01-27")
            
            # Try with latest available data
            print("\nChecking for any available data...")
            query = "SELECT DISTINCT entry_date FROM customer_bazar_summary ORDER BY entry_date DESC LIMIT 5"
            available_dates = db_manager.execute_query(query)
            
            if available_dates:
                print("Available dates:")
                for date_row in available_dates:
                    print(f"  - {date_row['entry_date']}")
                
                # Test with latest available date
                latest_date = available_dates[0]['entry_date']
                print(f"\nTesting with latest date: {latest_date}")
                
                latest_data = db_manager.get_customer_bazar_summary_by_date(latest_date)
                if latest_data:
                    print(f"✅ Found {len(latest_data)} records for {latest_date}")
                    
                    # Show first record structure
                    first_record = latest_data[0]
                    print("\n📋 Record structure:")
                    for key in first_record.keys():
                        print(f"  - {key}: {first_record[key]}")
            else:
                print("❌ No data found in customer_bazar_summary table")
        
    except Exception as e:
        print(f"❌ Error testing customer summary: {e}")
        import traceback
        traceback.print_exc()

def test_display_formatting():
    """Test display formatting to check for question mark issues"""
    print("\n\nTesting Display Formatting...")
    
    # Test different formatting approaches
    test_values = [0, 1000, 12500, 105300]
    
    for value in test_values:
        try:
            # Original format with rupee symbol
            rupee_format = f"₹{value:,}"
            print(f"₹ format: {rupee_format}")
            
            # Simple comma format
            comma_format = f"{value:,}"
            print(f"Comma format: {comma_format}")
            
            # Simple format
            simple_format = str(value)
            print(f"Simple format: {simple_format}")
            
            print()
            
        except Exception as e:
            print(f"❌ Formatting error for {value}: {e}")

if __name__ == "__main__":
    print("🔍 Customer Summary Table Diagnostic Test")
    print("=" * 50)
    
    test_customer_summary_data()
    test_display_formatting()
    
    print("\n✅ Tests completed!")