#!/usr/bin/env python3
"""Test the fix via the actual GUI validation function"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.database.db_manager import DatabaseManager
from datetime import date

def test_gui_fix():
    """Test the fix through the actual GUI flow"""
    
    print("=" * 80)
    print("TESTING FIXED GUI FLOW FOR 4SP=100")
    print("=" * 80)
    
    # Import the actual validation function from the GUI
    sys.path.append('.')
    
    try:
        from main import validate_input
        
        db_manager = DatabaseManager("data/rickymama.db")
        
        # Clear test data
        test_date = date.today().isoformat()
        test_bazar = 'T.O'
        
        db_manager.execute_query("DELETE FROM universal_log WHERE bazar = ? AND entry_date = ?", (test_bazar, test_date))
        db_manager.execute_query("DELETE FROM pana_table WHERE bazar = ? AND entry_date = ?", (test_bazar, test_date))
        
        # Test the validation function (this processes and stores data)
        print("1. TESTING GUI VALIDATION FUNCTION:")
        print("   Input: '4SP=100'")
        print("   Customer: TestGUI")
        print(f"   Bazar: {test_bazar}")
        
        # Call the actual GUI validation function
        result = validate_input("TestGUI", test_bazar, "4SP=100")
        
        print(f"   Validation result: {result}")
        
        # Check results
        universal_total = db_manager.execute_query("""
            SELECT COUNT(*) as count, SUM(value) as total 
            FROM universal_log 
            WHERE bazar = ? AND entry_date = ? AND entry_type = 'TYPE'
        """, (test_bazar, test_date))[0]
        
        pana_total = db_manager.execute_query("""
            SELECT COUNT(*) as count, SUM(value) as total 
            FROM pana_table 
            WHERE bazar = ? AND entry_date = ?
        """, (test_bazar, test_date))[0]
        
        print(f"\\n2. RESULTS:")
        print(f"   Universal_log: {universal_total['count']} entries, ₹{universal_total['total']} total")
        print(f"   Pana_table: {pana_total['count']} entries, ₹{pana_total['total']} total")
        
        # Check individual pana values
        sample_pana = db_manager.execute_query("""
            SELECT number, value FROM pana_table 
            WHERE bazar = ? AND entry_date = ? 
            ORDER BY number LIMIT 3
        """, (test_bazar, test_date))
        
        print(f"   Sample pana values: {[(p['number'], p['value']) for p in sample_pana]}")
        
        expected_count = 12  # SP4 has 12 numbers
        expected_total = 12 * 100  # 12 × ₹100
        
        if (universal_total['count'] == expected_count and 
            universal_total['total'] == expected_total and
            pana_total['count'] == expected_count and 
            pana_total['total'] == expected_total):
            print(f"\\n   ✅ GUI FIX SUCCESSFUL!")
            print(f"   ✅ Each SP4 number correctly gets ₹100")
            print(f"   ✅ Total is ₹{expected_total} as expected")
        else:
            print(f"\\n   ❌ Issue still exists")
            print(f"   Expected: {expected_count} entries, ₹{expected_total} total")
            
    except Exception as e:
        print(f"Error testing GUI: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_gui_fix()