#!/usr/bin/env python3
"""Test script to verify time table data and formatting"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.database.db_manager import DatabaseManager

def test_time_table_data():
    """Test time table data retrieval and formatting"""
    print("Testing Time Table Data...")
    
    try:
        # Create database manager
        db_manager = DatabaseManager("./data/rickymama.db")
        
        # Get available bazars
        bazar_query = "SELECT DISTINCT bazar FROM time_table_by_bazar ORDER BY bazar"
        available_bazars = db_manager.execute_query(bazar_query)
        
        if available_bazars:
            print(f"\n✅ Available bazars: {[b['bazar'] for b in available_bazars]}")
            
            # Test with first available bazar
            test_bazar = available_bazars[0]['bazar']
            print(f"\nTesting with bazar: {test_bazar}")
            
            # Get recent time table data
            time_data = db_manager.get_time_table_by_bazar_date(test_bazar, "2025-01-27")
            
            if time_data:
                print(f"\n✅ Time Table Data Found for {test_bazar}:")
                print("=" * 120)
                print(f"{'Customer':<15} {'1':<8} {'2':<8} {'3':<8} {'4':<8} {'5':<8} {'6':<8} {'7':<8} {'8':<8} {'9':<8} {'0':<8} {'Total':<10}")
                print("-" * 120)
                
                for entry in time_data:
                    row = f"{entry['customer_name']:<15}"
                    for i in [1, 2, 3, 4, 5, 6, 7, 8, 9, 0]:
                        value = entry[f'col_{i}'] if entry[f'col_{i}'] > 0 else "-"
                        row += f" {str(value):<8}"
                    row += f" {entry['total']:<10}"
                    print(row)
                
                print(f"\n📊 Total Records: {len(time_data)}")
                
                # Check data structure
                if time_data:
                    print("\n📋 Time table record structure:")
                    first_record = time_data[0]
                    for key in first_record.keys():
                        print(f"  - {key}: {first_record[key]}")
            else:
                print(f"⚠️ No time table data found for {test_bazar} on 2025-01-27")
                
                # Check for any available data
                date_query = f"SELECT DISTINCT entry_date FROM time_table_by_bazar WHERE bazar = ? ORDER BY entry_date DESC LIMIT 5"
                available_dates = db_manager.execute_query(date_query, (test_bazar,))
                
                if available_dates:
                    print(f"\nAvailable dates for {test_bazar}:")
                    for date_row in available_dates:
                        print(f"  - {date_row['entry_date']}")
                    
                    # Test with latest date
                    latest_date = available_dates[0]['entry_date']
                    print(f"\nTesting with latest date: {latest_date}")
                    
                    latest_data = db_manager.get_time_table_by_bazar_date(test_bazar, latest_date)
                    if latest_data:
                        print(f"✅ Found {len(latest_data)} records for {latest_date}")
                        
                        # Show sample data
                        sample = latest_data[0]
                        print("\nSample record:")
                        for i in [1, 2, 3, 4, 5, 6, 7, 8, 9, 0]:
                            col_value = sample[f'col_{i}']
                            if col_value > 0:
                                print(f"  Column {i}: {col_value}")
        else:
            print("❌ No data found in time_table_by_bazar table")
        
    except Exception as e:
        print(f"❌ Error testing time table: {e}")
        import traceback
        traceback.print_exc()

def test_display_formats():
    """Test different display formats for values"""
    print("\n\nTesting Display Formats...")
    
    test_values = [0, 100, 1000, 12500, 105300]
    
    for value in test_values:
        print(f"\nValue: {value}")
        print(f"  Simple: {value}")
        print(f"  Comma: {value:,}")
        print(f"  String: {str(value)}")
        
        # Test conditional display
        display_value = value if value > 0 else "-"
        print(f"  Conditional: {display_value}")

def test_jodi_column_mapping():
    """Test jodi number to column mapping logic"""
    print("\n\nTesting Jodi Column Mapping...")
    
    # Test cases for jodi number to column mapping
    test_cases = [
        (0, 0),    # 00 -> column 0
        (1, 0),    # 01 -> column 0
        (9, 0),    # 09 -> column 0
        (10, 1),   # 10 -> column 1
        (11, 1),   # 11 -> column 1
        (19, 1),   # 19 -> column 1
        (20, 2),   # 20 -> column 2
        (25, 2),   # 25 -> column 2
        (30, 3),   # 30 -> column 3
        (40, 4),   # 40 -> column 4
        (50, 5),   # 50 -> column 5
        (60, 6),   # 60 -> column 6
        (70, 7),   # 70 -> column 7
        (80, 8),   # 80 -> column 8
        (90, 9),   # 90 -> column 9
        (99, 9),   # 99 -> column 9
    ]
    
    for jodi_number, expected_column in test_cases:
        # Apply the mapping logic from the GUI
        if jodi_number == 0:
            column = 0
        elif 1 <= jodi_number <= 9:
            column = 0
        elif jodi_number == 10:
            column = 1
        elif jodi_number == 20:
            column = 2
        elif jodi_number == 30:
            column = 3
        elif jodi_number == 40:
            column = 4
        elif jodi_number == 50:
            column = 5
        elif jodi_number == 60:
            column = 6
        elif jodi_number == 70:
            column = 7
        elif jodi_number == 80:
            column = 8
        elif jodi_number == 90:
            column = 9
        else:
            tens_digit = jodi_number // 10
            if tens_digit >= 1 and tens_digit <= 9:
                column = tens_digit
            else:
                column = -1
        
        status = "✅" if column == expected_column else "❌"
        print(f"{status} Jodi {jodi_number:02d} -> Column {column} (expected {expected_column})")

if __name__ == "__main__":
    print("🔍 Time Table Diagnostic Test")
    print("=" * 50)
    
    test_time_table_data()
    test_display_formats()
    test_jodi_column_mapping()
    
    print("\n✅ Tests completed!")