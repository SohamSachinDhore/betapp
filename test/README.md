# Test Directory

This directory contains all test files, analysis scripts, and debugging utilities for the RickyMama project.

## Test Files

### Core Functionality Tests
- `test_database_operations.py` - Database connection and basic operations
- `test_database_storage_retrieval.py` - Comprehensive data storage/retrieval tests
- `test_gui_database_integration.py` - GUI database integration tests
- `test_calculation_logic.py` - Calculation engine tests
- `test_full_flow.py` - End-to-end flow tests
- `test_complete_type_flow.py` - Complete type processing tests

### Parsing and Entry Tests
- `test_all_entry_types.py` - All entry type parsing tests
- `test_pana_table_values.py` - Pana table specific tests
- `test_time_entries.py` - Time entry parsing tests
- `test_direct_calculation.py` - Direct calculation tests
- `test_type_parsing_flow.py` - Type parsing flow tests
- `test_parsing_issue.py` - Parsing issue debugging
- `test_pattern_detection.py` - Pattern detection tests

### GUI Tests
- `test_gui_functionality.py` - GUI functionality tests
- `test_gui_integration.py` - GUI integration tests
- `test_gui_fix.py` - GUI fix verification tests

### Specific Bug Tests
- `test_4sp_bug.py` - 4SP bug fix tests
- `test_double_entries.py` - Double entry handling tests
- `test_double_processing.py` - Double processing prevention tests
- `test_trigger_issue.py` - Database trigger tests
- `test_accumulation.py` - Value accumulation tests
- `test_entry_count.py` - Entry counting tests

### Database Tests
- `test_jodi_debug.py` - Jodi table debugging
- `test_time_table_fix.py` - Time table fix tests
- `test_customer_summary_fix.py` - Customer summary fix tests
- `test_customer_colors.py` - Customer color feature tests
- `test_commission_customer.py` - Commission customer tests

### Analysis and Utilities
- `analyze_gui_calculation.py` - GUI calculation analysis
- `calculation_logic_analysis.py` - Calculation logic analysis
- `database_analysis.py` - Database structure analysis
- `database_storage_analysis.py` - Storage pattern analysis
- `database_health_report.py` - Database health reporting
- `debug_type_values.py` - Type value debugging
- `type_analysis_summary.py` - Type analysis summary
- `verify_color_implementation.py` - Color feature verification

### Database Utilities
- `check_db_constraint.py` - Database constraint checking
- `fix_database_constraint.py` - Database constraint fixes
- `fix_pana_parsing.py` - Pana parsing fixes
- `reinitialize_db.py` - Database reinitialization
- `live_storage_demo.py` - Live storage demonstration

## Running Tests

To run any test file:

```bash
cd /Users/sohamdhore/Desktop/Work/Rickey_mama_V2
python test/test_filename.py
```

## Adding New Tests

When adding new test files:
1. Use the `test_` prefix for test files
2. Use descriptive names that indicate what is being tested
3. Add appropriate documentation at the top of the file
4. Update this README if adding a new category of tests
