#!/usr/bin/env python3
"""Test if values are being accumulated incorrectly"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.database.db_manager import DatabaseManager

def test_accumulation():
    """Test if 1300 comes from accumulated values"""
    
    print("=" * 80)
    print("TESTING ACCUMULATION ISSUE")
    print("=" * 80)
    
    db_manager = DatabaseManager("data/rickymama.db")
    
    # Check if there are any numbers that appear in multiple TYPE table columns
    print("1. CHECKING FOR NUMBERS IN MULTIPLE COLUMNS:")
    
    # Get all SP table numbers by column
    sp_columns = {}
    for col in range(1, 11):
        query = "SELECT number FROM type_table_sp WHERE column_number = ?"
        results = db_manager.execute_query(query, (col,))
        sp_columns[col] = {row['number'] for row in results}
    
    # Check SP column 4 numbers
    sp4_numbers = sp_columns[4]
    print(f"\n   SP Column 4 has {len(sp4_numbers)} numbers")
    
    # Check if any SP4 numbers appear in other columns
    print(f"\n2. CHECKING IF SP4 NUMBERS APPEAR IN OTHER COLUMNS:")
    
    for number in sorted(sp4_numbers):
        appears_in = []
        for col in range(1, 11):
            if col != 4 and number in sp_columns[col]:
                appears_in.append(col)
        
        if appears_in:
            print(f"   Number {number} also appears in columns: {appears_in}")
    
    # Check a specific case
    print(f"\n3. DETAILED CHECK FOR NUMBER 130 (first in SP4):")
    
    # Check all SP columns for 130
    for col in range(1, 11):
        if 130 in sp_columns[col]:
            print(f"   130 appears in SP column {col}")
    
    # Check DP and CP tables too
    dp_query = "SELECT column_number FROM type_table_dp WHERE number = 130"
    dp_results = db_manager.execute_query(dp_query, ())
    if dp_results:
        print(f"   130 appears in DP columns: {[r['column_number'] for r in dp_results]}")
    
    cp_query = "SELECT column_number FROM type_table_cp WHERE number = 130"
    cp_results = db_manager.execute_query(cp_query, ())
    if cp_results:
        print(f"   130 appears in CP columns: {[r['column_number'] for r in cp_results]}")
    
    # Check if 1300 = 13 * 100
    print(f"\n4. CHECKING IF 1300 = 13 × 100:")
    print(f"   This would mean 13 entries are being created instead of 12")
    print(f"   SP4 has exactly {len(sp4_numbers)} numbers")
    
    # Check for any duplicates in SP column 4
    sp4_list = db_manager.execute_query("""
        SELECT number, COUNT(*) as count 
        FROM type_table_sp 
        WHERE column_number = 4 
        GROUP BY number 
        HAVING count > 1
    """)
    
    if sp4_list:
        print(f"   ❌ FOUND DUPLICATES IN SP COLUMN 4:")
        for row in sp4_list:
            print(f"      Number {row['number']} appears {row['count']} times")
    else:
        print(f"   ✅ No duplicates in SP column 4")

if __name__ == "__main__":
    test_accumulation()