#!/usr/bin/env python3
"""
Test script to demonstrate how SP/DP/CP TYPE entries are detected, parsed, and stored in database
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.parsing.pattern_detector import PatternDetector, PatternType
from src.parsing.type_table_parser import TypeTableParser, TypeTableLoader
from src.parsing.mixed_input_parser import MixedInputParser
from src.business.calculation_engine import CalculationEngine, CalculationContext
from src.business.data_processor import DataProcessor
from src.database.db_manager import DatabaseManager
from datetime import date

def test_type_parsing_complete_flow():
    """Test complete flow from input to database storage"""
    
    print("=" * 80)
    print("TYPE ENTRY PARSING & STORAGE FLOW DEMONSTRATION")
    print("=" * 80)
    
    # Initialize database and components
    db_manager = DatabaseManager("data/rickymama.db")
    
    # Load type tables from database
    type_loader = TypeTableLoader(db_manager)
    sp_table, dp_table, cp_table = type_loader.load_all_tables()
    
    print(f"\n1. LOADED TYPE TABLES FROM DATABASE:")
    print(f"   SP Table: {len(sp_table)} columns, {sum(len(nums) for nums in sp_table.values())} total numbers")
    print(f"   DP Table: {len(dp_table)} columns, {sum(len(nums) for nums in dp_table.values())} total numbers") 
    print(f"   CP Table: {len(cp_table)} columns, {sum(len(nums) for nums in cp_table.values())} total numbers")
    
    # Sample TYPE entries to test
    test_inputs = [
        "1SP=50",      # SP column 1, value 50
        "5DP=100",     # DP column 5, value 100  
        "15CP=200",    # CP column 15, value 200
        "1SP=30\n3DP=75\n25CP=150"  # Multiple types
    ]
    
    for i, test_input in enumerate(test_inputs, 1):
        print(f"\n{'-' * 60}")
        print(f"TEST {i}: {repr(test_input)}")
        print(f"{'-' * 60}")
        
        # Step 1: Pattern Detection
        detector = PatternDetector()
        pattern_type = detector.detect_pattern_type(test_input)
        print(f"\n2. PATTERN DETECTION:")
        print(f"   Detected Pattern: {pattern_type.value}")
        
        # Step 2: Parsing
        type_validator = type_loader.create_validator()
        parser = TypeTableParser(type_validator)
        
        try:
            parsed_entries = parser.parse(test_input)
            print(f"\n3. PARSING RESULTS:")
            print(f"   Parsed {len(parsed_entries)} TYPE entries:")
            
            for entry in parsed_entries:
                print(f"     - Column {entry.column}, Table {entry.table_type}, Value ₹{entry.value}")
                
        except Exception as e:
            print(f"   Parsing failed: {e}")
            continue
        
        # Step 3: Number Expansion (show what numbers will be created)
        calculation_engine = CalculationEngine(sp_table, dp_table, cp_table)
        print(f"\n4. NUMBER EXPANSION:")
        
        total_numbers_generated = 0
        total_value_distributed = 0
        
        for entry in parsed_entries:
            if entry.table_type == 'SP':
                numbers = sp_table.get(entry.column, set())
            elif entry.table_type == 'DP':
                numbers = dp_table.get(entry.column, set())
            elif entry.table_type == 'CP':
                numbers = cp_table.get(entry.column, set())
            else:
                numbers = set()
            
            numbers_list = sorted(list(numbers))[:10]  # Show first 10 numbers
            remaining = len(numbers) - len(numbers_list)
            
            print(f"   {entry.table_type} Column {entry.column} → {len(numbers)} numbers")
            print(f"     Numbers: {numbers_list}{f' ... (+{remaining} more)' if remaining > 0 else ''}")
            print(f"     Each number gets value: ₹{entry.value}")
            print(f"     Total value: ₹{entry.value * len(numbers)}")
            
            total_numbers_generated += len(numbers)
            total_value_distributed += entry.value * len(numbers)
        
        print(f"\n   SUMMARY: {total_numbers_generated} pana numbers, Total value: ₹{total_value_distributed}")
        
        # Step 4: Database Storage Simulation
        print(f"\n5. DATABASE STORAGE:")
        
        # Show how entries are stored in universal_log
        print(f"   UNIVERSAL_LOG entries: {total_numbers_generated} records")
        print(f"     - Each with entry_type='TYPE'")
        print(f"     - customer_id, bazar, entry_date, number, value")
        
        # Show how entries are stored in pana_table via triggers
        print(f"   PANA_TABLE updates: {total_numbers_generated} records")
        print(f"     - Via tr_update_pana_table trigger")
        print(f"     - Groups by bazar, entry_date, number")
        print(f"     - Accumulates values for duplicate numbers")
        
        # Show example universal_log entries for first entry
        if parsed_entries:
            first_entry = parsed_entries[0]
            if first_entry.table_type == 'SP':
                sample_numbers = sorted(list(sp_table.get(first_entry.column, set())))[:3]
            elif first_entry.table_type == 'DP':
                sample_numbers = sorted(list(dp_table.get(first_entry.column, set())))[:3]
            elif first_entry.table_type == 'CP':
                sample_numbers = sorted(list(cp_table.get(first_entry.column, set())))[:3]
            else:
                sample_numbers = []
            
            print(f"\n   SAMPLE UNIVERSAL_LOG ENTRIES (first 3):")
            for num in sample_numbers:
                print(f"     - customer_id=1, bazar='T.O', number={num}, value={first_entry.value}, entry_type='TYPE'")

def show_type_table_samples():
    """Show sample data from each type table"""
    
    print(f"\n{'-' * 80}")
    print("TYPE TABLE REFERENCE DATA SAMPLES")
    print(f"{'-' * 80}")
    
    db_manager = DatabaseManager("data/rickymama.db")
    
    # SP Table samples
    print(f"\nSP TABLE (Single Patti) - Sample from Column 1:")
    sp_query = "SELECT number FROM type_table_sp WHERE column_number = 1 ORDER BY row_number LIMIT 5"
    sp_results = db_manager.execute_query(sp_query)
    sp_numbers = [row['number'] for row in sp_results]
    print(f"   Column 1 numbers: {sp_numbers} ...")
    
    # DP Table samples  
    print(f"\nDP TABLE (Double Patti) - Sample from Column 1:")
    dp_query = "SELECT number FROM type_table_dp WHERE column_number = 1 ORDER BY row_number LIMIT 5"
    dp_results = db_manager.execute_query(dp_query)
    dp_numbers = [row['number'] for row in dp_results]
    print(f"   Column 1 numbers: {dp_numbers} ...")
    
    # CP Table samples
    print(f"\nCP TABLE (Close Patti) - Sample from Column 11:")
    cp_query = "SELECT number FROM type_table_cp WHERE column_number = 11 ORDER BY row_number LIMIT 5"
    cp_results = db_manager.execute_query(cp_query)
    cp_numbers = [row['number'] for row in cp_results]
    print(f"   Column 11 numbers: {cp_numbers} ...")

def test_mixed_input_with_types():
    """Test mixed input containing TYPE entries with other patterns"""
    
    print(f"\n{'-' * 80}")
    print("MIXED INPUT WITH TYPE ENTRIES")
    print(f"{'-' * 80}")
    
    # Sample mixed input containing TYPE entries
    mixed_input = """
    soham
    27-07-2025
    T.O
    138+347+230 = 400
    1SP=50
    5DP=100
    7=80
    """
    
    print(f"Mixed Input:")
    print(mixed_input.strip())
    
    # Initialize components
    db_manager = DatabaseManager("data/rickymama.db")
    data_processor = DataProcessor(db_manager)
    
    try:
        # Process the mixed input
        result = data_processor.process_mixed_input(mixed_input)
        
        print(f"\n6. MIXED INPUT PROCESSING RESULTS:")
        print(f"   Total entries parsed: {result.total_entries}")
        print(f"   PANA entries: {result.pana_count}")
        print(f"   TYPE entries: {result.type_count}")
        print(f"   Direct entries: {result.direct_count}")
        print(f"   Total calculated value: ₹{result.calculated_total}")
        
        # Show breakdown by entry type
        print(f"\n   ENTRY TYPE BREAKDOWN:")
        if result.breakdown:
            for entry_type, details in result.breakdown.items():
                if isinstance(details, dict) and 'total' in details:
                    print(f"     {entry_type.upper()}: ₹{details['total']}")
        
    except Exception as e:
        print(f"   Processing failed: {e}")

if __name__ == "__main__":
    # Run all tests
    show_type_table_samples()
    test_type_parsing_complete_flow()
    test_mixed_input_with_types()
    
    print(f"\n{'=' * 80}")
    print("SUMMARY: TYPE ENTRY PROCESSING FLOW")
    print(f"{'=' * 80}")
    print("1. Pattern Detection: Recognizes 'XSP/DP/CP=VALUE' format")
    print("2. Parsing: Validates column ranges and table types")
    print("3. Number Expansion: Looks up all numbers in specified table column")
    print("4. Universal Log: Creates one entry per expanded number") 
    print("5. Pana Table: Triggers automatically aggregate values by number")
    print("6. Result: TYPE entries become multiple PANA numbers in database")
