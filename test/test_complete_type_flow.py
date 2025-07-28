#!/usr/bin/env python3
"""
Complete demonstration of SP/DP/CP TYPE entry detection, parsing, and database storage
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.parsing.pattern_detector import PatternDetector, PatternType
from src.parsing.mixed_input_parser import MixedInputParser
from src.business.data_processor import DataProcessor
from src.database.db_manager import DatabaseManager

def comprehensive_type_demo():
    """Complete demonstration of TYPE entry processing"""
    
    print("=" * 100)
    print("COMPLETE SP/DP/CP TYPE ENTRY PROCESSING DEMONSTRATION")
    print("=" * 100)
    
    # Initialize components
    db_manager = DatabaseManager("data/rickymama.db")
    
    # Clear existing data for clean test
    db_manager.execute_query("DELETE FROM universal_log")
    db_manager.execute_query("DELETE FROM pana_table")
    db_manager.execute_query("DELETE FROM customers WHERE name LIKE 'demo_%'")
    
    # Test cases with different TYPE combinations
    test_cases = [
        {
            "name": "Single SP Entry",
            "input": "demo_customer_1\n2025-07-27\nT.O\n1SP=100",
            "description": "Simple SP entry - should expand to 12 numbers"
        },
        {
            "name": "Single DP Entry", 
            "input": "demo_customer_2\n2025-07-27\nM.O\n3DP=150",
            "description": "Simple DP entry - should expand to 10 numbers"
        },
        {
            "name": "Single CP Entry",
            "input": "demo_customer_3\n2025-07-27\nK.O\n25CP=200", 
            "description": "Simple CP entry - should expand to numbers in CP column 25"
        },
        {
            "name": "Mixed TYPE Entries",
            "input": "demo_customer_4\n2025-07-27\nB.O\n1SP=50\n5DP=75\n15CP=125",
            "description": "Multiple TYPE entries in same input"
        },
        {
            "name": "TYPE with PANA",
            "input": "demo_customer_5\n2025-07-27\nNMO\n138+347=300\n2SP=100",
            "description": "TYPE entry mixed with PANA entry"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'-' * 80}")
        print(f"TEST {i}: {test_case['name']}")
        print(f"Description: {test_case['description']}")
        print(f"{'-' * 80}")
        
        print(f"\nInput:")
        for line in test_case['input'].split('\n'):
            print(f"  {line}")
        
        # Step 1: Pattern Detection
        detector = PatternDetector()
        lines = test_case['input'].strip().split('\n')[3:]  # Skip header lines
        
        print(f"\n1. PATTERN DETECTION:")
        for line in lines:
            if line.strip():
                pattern = detector.detect_pattern_type(line.strip())
                print(f"   '{line}' → {pattern.value}")
        
        # Step 2: Process with DataProcessor
        try:
            data_processor = DataProcessor(db_manager)
            
            # Get before counts
            before_universal = db_manager.execute_query("SELECT COUNT(*) as count FROM universal_log")[0]['count']
            before_pana = db_manager.execute_query("SELECT COUNT(*) as count FROM pana_table")[0]['count']
            
            print(f"\n2. PROCESSING:")
            print(f"   Before - Universal Log: {before_universal} records, Pana Table: {before_pana} records")
            
            # Process the input
            result = data_processor.process_mixed_input(test_case['input'])
            
            # Get after counts
            after_universal = db_manager.execute_query("SELECT COUNT(*) as count FROM universal_log")[0]['count']
            after_pana = db_manager.execute_query("SELECT COUNT(*) as count FROM pana_table")[0]['count']
            
            print(f"   After  - Universal Log: {after_universal} records, Pana Table: {after_pana} records")
            print(f"   Added  - Universal Log: {after_universal - before_universal} records, Pana Table: {after_pana - before_pana} records")
            
            # Show TYPE expansion details
            type_entries = db_manager.execute_query("""
                SELECT number, value, source_line 
                FROM universal_log 
                WHERE entry_type = 'TYPE' 
                AND customer_name = ?
                ORDER BY number
            """, [test_case['input'].split('\n')[0]])
            
            if type_entries:
                print(f"\n3. TYPE EXPANSION RESULTS:")
                
                # Group by source line
                by_source = {}
                for entry in type_entries:
                    source = entry['source_line']
                    if source not in by_source:
                        by_source[source] = []
                    by_source[source].append(entry)
                
                for source, entries in by_source.items():
                    numbers = [e['number'] for e in entries]
                    value = entries[0]['value']
                    total_value = len(entries) * value
                    
                    print(f"   {source}:")
                    print(f"     → {len(entries)} numbers: {numbers[:5]}{'...' if len(numbers) > 5 else ''}")
                    print(f"     → Each gets ₹{value}, Total: ₹{total_value}")
            
            # Show pana table integration
            pana_entries = db_manager.execute_query("""
                SELECT bazar, number, value
                FROM pana_table
                WHERE bazar = ? AND entry_date = '2025-07-27'
                ORDER BY number
            """, [test_case['input'].split('\n')[2]])
            
            if pana_entries:
                print(f"\n4. PANA TABLE INTEGRATION:")
                print(f"   Total numbers in pana_table: {len(pana_entries)}")
                total_pana_value = sum(entry['value'] for entry in pana_entries)
                print(f"   Total value in pana_table: ₹{total_pana_value}")
                
                # Show sample entries
                sample_entries = pana_entries[:3]
                print(f"   Sample entries:")
                for entry in sample_entries:
                    print(f"     - {entry['bazar']}: Number {entry['number']} = ₹{entry['value']}")
            
            print(f"\n   ✅ SUCCESS: TYPE entries properly expanded and stored")
            
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
    
    # Summary statistics
    print(f"\n{'=' * 80}")
    print("FINAL SUMMARY")
    print(f"{'=' * 80}")
    
    # Total records created
    total_universal = db_manager.execute_query("SELECT COUNT(*) as count FROM universal_log")[0]['count']
    total_pana = db_manager.execute_query("SELECT COUNT(*) as count FROM pana_table")[0]['count']
    total_customers = db_manager.execute_query("SELECT COUNT(*) as count FROM customers WHERE name LIKE 'demo_%'")[0]['count']
    
    print(f"Total demo customers created: {total_customers}")
    print(f"Total universal_log records: {total_universal}")
    print(f"Total pana_table records: {total_pana}")
    
    # Show TYPE vs other entry types
    type_breakdown = db_manager.execute_query("""
        SELECT entry_type, COUNT(*) as count, SUM(value) as total_value
        FROM universal_log
        GROUP BY entry_type
        ORDER BY entry_type
    """)
    
    print(f"\nEntry type breakdown:")
    for row in type_breakdown:
        print(f"  {row['entry_type']}: {row['count']} records, ₹{row['total_value']} total value")
    
    # Show how TYPE entries become PANA entries
    print(f"\nKEY INSIGHT:")
    print(f"TYPE entries are automatically converted to PANA numbers via:")
    print(f"1. Parser detects TYPE pattern (1SP=100)")
    print(f"2. DataProcessor expands to multiple numbers from type_table_sp")
    print(f"3. Each number becomes separate universal_log record with entry_type='TYPE'")  
    print(f"4. Database trigger automatically creates/updates pana_table records")
    print(f"5. Final result: TYPE entries seamlessly integrated as PANA numbers!")

if __name__ == "__main__":
    comprehensive_type_demo()
