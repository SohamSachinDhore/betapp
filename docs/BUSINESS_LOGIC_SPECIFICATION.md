# RickyMama - Business Logic & Calculation Rules Specification

## Overview

This document defines the comprehensive business logic, calculation rules, and data processing workflows for the RickyMama data entry system. All calculations are deterministic and auditable.

## Core Business Rules

### 1. Data Entry Principles
- **Single Source of Truth**: Universal log serves as the authoritative record
- **Immutable Logs**: Once submitted, entries are never modified, only appended
- **Bazar-Date Isolation**: Pana table values are unique per bazar and date combination
- **Customer-Date Aggregation**: Time table and summary data aggregated per customer per date
- **Atomic Transactions**: All related updates succeed or fail together

### 2. Value Assignment Rules
- **Non-negative Values**: All monetary values must be zero or positive
- **Integer Precision**: All calculations use integer arithmetic (no decimals)
- **Additive Operations**: Multiple entries for same target accumulate values
- **Date-based Partitioning**: Data is partitioned by entry date for isolation

## Calculation Engine Specification

### Core Calculation Interface
```python
class CalculationEngine:
    """Master calculation engine for all input types"""
    
    def calculate_total(self, parsed_entries: ParsedInputResult) -> CalculationResult:
        """
        Master total calculation for mixed input types
        Returns: CalculationResult with breakdown by type
        """
        result = CalculationResult()
        
        # Calculate each type separately
        result.pana_total = self.calculate_pana_total(parsed_entries.pana_entries)
        result.type_total = self.calculate_type_total(parsed_entries.type_entries)
        result.time_total = self.calculate_time_total(parsed_entries.time_entries)
        result.multi_total = self.calculate_multi_total(parsed_entries.multi_entries)
        
        # Calculate grand total
        result.grand_total = (
            result.pana_total + 
            result.type_total + 
            result.time_total + 
            result.multi_total
        )
        
        return result

@dataclass
class CalculationResult:
    """Calculation result with type breakdown"""
    pana_total: int = 0
    type_total: int = 0
    time_total: int = 0
    multi_total: int = 0
    grand_total: int = 0
    calculation_details: Dict[str, Any] = field(default_factory=dict)
```

## Type-Specific Calculation Rules

### Type 1: Pana Table Calculations

**Supported Input Formats:**
- `128/129/120 = 100` (slash separated)
- `128+129+120 = 100` (plus separated)
- `128 129 120 = 100` (space separated)
- `128,129,120 = 100` (comma separated)
- `128*129*120 = 100` (star separated)

**Multiline Format Support:**
```
589,478,140,189,
145,147,370,269,
148,470,125,129,134,458,
569,679,180,236,
239,347= 260
```

Or with equals on separate line:
```
589,478,140,189,
145,147,370,269,
148,470,125,129,134,458,
569,679,180,236,
239,347
= 260
```

**Value Format Handling:**
- Supports `= 100`, `= Rs100`, `= R100`, `= Rs.100`, `= Rs. 100`
- Extracts only numeric value after equals sign

#### Single Line Calculation
```python
def calculate_pana_single_line(self, entries: List[PanaEntry]) -> int:
    """
    Single line: 128/129/120 = 100
    Rule: number_count × value
    Result: 3 × 100 = 300
    
    Preview Display:
    128 = 100
    129 = 100  
    120 = 100
    """
    if not entries:
        return 0
    
    # All entries in single line have same value
    value_per_number = entries[0].value
    number_count = len(entries)
    
    return number_count * value_per_number

# Example:
# Input: "128/129/120 = 100"
# Parsed: [PanaEntry(128, 100), PanaEntry(129, 100), PanaEntry(120, 100)]
# Calculation: 3 numbers × 100 = 300
# Preview: Each number displayed with value 100
```

#### Multi-line Calculation
```python
def calculate_pana_multiline(self, line_groups: List[List[PanaEntry]]) -> int:
    """
    Multi-line format:
    589,478,140,189,
    145,147,370,269,
    148,470,125,129,134,458,
    569,679,180,236,
    239,347= 260
    
    Rule: total_number_count × value
    Result: 20 × 260 = 5,200
    
    Also supports equals on separate line:
    589,478,140,189,
    145,147,370,269,
    = 260
    """
    total = 0
    
    for group in line_groups:
        if not group:
            continue
            
        value_per_number = group[0].value
        number_count = len(group)
        group_total = number_count * value_per_number
        total += group_total
    
    return total

# Example:
# Input lines represent 20 numbers total with value 260 each
# Calculation: 20 numbers × 260 = 5,200
# Each number gets same value in pana table
```

#### Pana Calculation Algorithm
```python
def calculate_pana_total(self, entries: List[PanaEntry]) -> int:
    """
    Comprehensive pana calculation handling all formats
    Validates numbers against pana table before processing
    """
    if not entries:
        return 0
    
    # Validate all numbers exist in pana table
    for entry in entries:
        if not self.validate_pana_number(entry.number):
            raise ValidationError(f"Invalid pana number: {entry.number}")
    
    # Group entries by value (for mixed value scenarios)
    value_groups = {}
    for entry in entries:
        value = entry.value
        if value not in value_groups:
            value_groups[value] = []
        value_groups[value].append(entry)
    
    total = 0
    for value, group_entries in value_groups.items():
        # Each group: count × value
        count = len(group_entries)
        group_total = count * value
        total += group_total
    
    return total

def validate_pana_number(self, number: int) -> bool:
    """Validate if number exists in pana table"""
    return self.db_manager.pana_number_exists(number)
```

### Type 2: Type Table Calculations

**Supported Table Types:**
- **SP Table**: Columns 1-10
- **DP Table**: Columns 1-10  
- **CP Table**: Columns 11-99, then 0

**Input Format:** `Column_Number + Table_Type = Value`
- Example: `1SP=100`, `5DP=200`, `25CP=150`

#### Column Expansion Logic
```python
def calculate_type_total(self, entries: List[TypeEntry]) -> int:
    """
    Type table format: 1SP=100
    Rule: Expand column to all numbers, apply value to each
    Result: Sum of individual values (not count × value)
    
    Example: 1SP=100
    - Column 1 of SP table contains: [128, 137, 146, 236, 245, 290, 380, 470, 489, 560, 579, 678]
    - Each number gets value 100
    - Total: 12 × 100 = 1,200
    
    Preview Display:
    128 = 100
    137 = 100
    146 = 100
    ... (all numbers in column 1 of SP table)
    """
    total = 0
    
    for entry in entries:
        # Validate table type and column
        if not self.validate_type_table_column(entry.table_type, entry.column):
            raise ValidationError(f"Invalid {entry.table_type} column: {entry.column}")
            
        # Get all numbers from the specified column
        column_numbers = self.expand_type_column(entry.table_type, entry.column)
        entry.numbers = column_numbers  # Store for database updates
        
        # Each number in the column gets the full value
        number_count = len(column_numbers)
        entry_total = number_count * entry.value
        total += entry_total
    
    return total

def validate_type_table_column(self, table_type: str, column: int) -> bool:
    """Validate table type and column combination"""
    if table_type == 'SP' and 1 <= column <= 10:
        return True
    elif table_type == 'DP' and 1 <= column <= 10:
        return True
    elif table_type == 'CP' and (11 <= column <= 99 or column == 0):
        return True
    return False

# Implementation details:
def expand_type_column(self, table_type: str, column: int) -> List[int]:
    """
    Retrieve all numbers from specified table column
    """
    if table_type == 'SP':
        return self.db_manager.get_sp_column(column)
    elif table_type == 'DP':
        return self.db_manager.get_dp_column(column)
    elif table_type == 'CP':
        return self.db_manager.get_cp_column(column)
    else:
        raise ValueError(f"Invalid table type: {table_type}")
```

### Type 3: Time Table Direct Calculations

**Table Structure:** Time table has columns 0-9 (0, 1, 2, 3, 4, 5, 6, 7, 8, 9)

**Input Formats:**
- Single column: `1=100` 
- Multiple columns: `0 1 3 5 = 900`
- Value format: Supports `= 100`, `= Rs100`, etc.

#### Single Column Assignment
```python
def calculate_time_direct_single(self, entry: TimeEntry) -> int:
    """
    Single column: 1=100
    Rule: Value × Number of columns
    Total contribution: 100 × 1 = 100
    
    Storage: Updates time table row for customer, column 1 with value 100
    """
    return entry.value * len(entry.columns)

# Example:
# Input: "1=100"
# Parsed: TimeEntry(columns=[1], value=100)
# Result: 100 × 1 = 100 (column 1 in customer's time table gets 100)
```

#### Multiple Column Assignment
```python
def calculate_time_direct_multiple(self, entry: TimeEntry) -> int:
    """
    Multiple columns: 0 1 3 5 = 900
    Rule: Value × Number of columns
    Total contribution: 900 × 4 = 3,600
    
    Distribution Logic: 900 ÷ 4 columns = 225 per column (for storage)
    Total calculation: 900 × 4 = 3,600
    """
    return entry.value * len(entry.columns)

# Example:
# Input: "0 1 3 5 = 900"
# Parsed: TimeEntry(columns=[0, 1, 3, 5], value=900)
# Distribution: Each column gets 900/4 = 225 (for storage)
# Total calculation: 900 × 4 = 3,600
```

#### Time Direct Calculation
```python
def calculate_time_total(self, entries: List[TimeEntry]) -> int:
    """
    Time table direct calculation
    Rule: Value × Number of columns for each entry
    
    Example:
    1=100 → 100 × 1 = 100
    0 1 3 5 = 900 → 900 × 4 = 3,600  
    Total: 100 + 3,600 = 3,700
    """
    total = 0
    for entry in entries:
        total += entry.value * len(entry.columns)
    return total
```

### Type 4: Multiplication Format Calculations

**Input Format:** `NumberxValue` (e.g., `38x700`, `83x700`)

**Processing Logic:**
- Extract tens digit and units digit from the number
- Add value to corresponding time table columns for the customer
- Contribute full value to total calculation

#### Multiplication Parsing and Calculation
```python
def calculate_multi_total(self, entries: List[MultiEntry]) -> int:
    """
    Multiplication format: 38x700, 83x700
    Rule: Each entry contributes its multiplication value
    Total: Sum of all multiplication results
    
    Example:
    38x700 → contributes 700 to total
    83x700 → contributes 700 to total
    Total: 700 + 700 = 1,400
    
    Time Table Updates:
    38x700 → Add 700 to column 3 (tens) and column 8 (units)
    83x700 → Add 700 to column 8 (tens) and column 3 (units)
    """
    return sum(entry.value for entry in entries)

# Digit extraction for time table updates:
def extract_digit_columns(self, entry: MultiEntry) -> Dict[int, int]:
    """
    Extract tens and units digits for time table column updates
    
    Example: 38x700
    - Number: 38
    - Tens digit: 3 → Add 700 to column 3
    - Units digit: 8 → Add 700 to column 8
    - Return: {3: 700, 8: 700}
    """
    number_str = str(entry.number).zfill(2)  # Ensure 2 digits
    tens_digit = int(number_str[0])
    units_digit = int(number_str[1])
    
    return {
        tens_digit: entry.value,
        units_digit: entry.value
    }
```

### Type 5: Mixed Input Format Support

**Comprehensive Mixed Input Example:**
```
6 8 9 0 = 3300
589,478,140,189,
145,147,370,269,
148,470,125,129,134,458,
569,679,180,236,
239,347= 260

267,560,378,489,
590,368,469,479,
570,580 = 260

124=400
147=250
4=24000
148=600
268=600
669=60

38x700
83x700
96x500
92x200
29x200
69x500
27x900
72x900
```

#### Mixed Input Processing
```python
def process_mixed_input(self, input_text: str) -> ParsedInputResult:
    """
    Process mixed input containing multiple format types
    Automatically detects and routes each line to appropriate parser
    """
    result = ParsedInputResult()
    lines = input_text.strip().split('
')
    
    current_multiline_group = []
    i = 0
    
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue
            
        # Detect input type and process accordingly
        if self.is_multiplication_format(line):
            # Type 4: Multiplication format
            entry = self.parse_multiplication_line(line)
            result.multi_entries.append(entry)
            
        elif self.is_type_table_format(line):
            # Type 2: Type table format
            entry = self.parse_type_table_line(line)
            result.type_entries.append(entry)
            
        elif self.is_time_direct_format(line):
            # Type 3: Time table direct format  
            entry = self.parse_time_direct_line(line)
            result.time_entries.append(entry)
            
        elif self.is_single_pana_format(line):
            # Type 1: Single line pana format
            entries = self.parse_single_pana_line(line)
            result.pana_entries.extend(entries)
            
        elif self.is_multiline_pana_start(line):
            # Type 1: Multiline pana format - collect all lines
            multiline_group = self.collect_multiline_pana_group(lines, i)
            entries = self.parse_multiline_pana_group(multiline_group)
            result.pana_entries.extend(entries)
            i += len(multiline_group) - 1  # Skip processed lines
            
        i += 1
    
    return result

def calculate_mixed_total(self, result: ParsedInputResult) -> int:
    """
    Calculate total for mixed input following specific rules:
    
    Time Direct: 6 8 9 0 = 3300 → 3300 × 4 = 13,200
    
    Multiline Pana: 20 numbers = 260 → 20 × 260 = 5,200
    
    Single Pana: 124=400 → 400 (single number gets full value)
    
    Multiplication: 38x700 → 700 (value contribution)
    """
    total = 0
    
    # Time entries: value × number of columns
    for entry in result.time_entries:
        total += entry.value * len(entry.columns)
    
    # Pana entries: count × value for each value group
    total += self.calculate_pana_total(result.pana_entries)
    
    # Type entries: count × value for expanded numbers
    total += self.calculate_type_total(result.type_entries)
    
    # Multiplication entries: sum values
    total += sum(entry.value for entry in result.multi_entries)
    
    return total
```

def parse_multiplication_entry(self, input_str: str) -> MultiEntry:
    """
    Parse multiplication format input
    
    Example: "38x700"
    Returns: MultiEntry(number=38, value=700, tens_digit=3, units_digit=8)
    """
    parts = input_str.split('x')
    if len(parts) != 2:
        raise ValidationError(f"Invalid multiplication format: {input_str}")
    
    number = int(parts[0])
    value = int(parts[1])
    
    number_str = str(number).zfill(2)
    tens_digit = int(number_str[0])
    units_digit = int(number_str[1])
    
    return MultiEntry(
        number=number,
        value=value,
        tens_digit=tens_digit,
        units_digit=units_digit
    )
```

## Data Processing Workflows

### 1. Main Entry Processing Pipeline
```python
class DataProcessor:
    """Master data processing orchestrator"""
    
    def process_submission(self, submission: EntrySubmission) -> ProcessingResult:
        """
        Main entry processing pipeline
        1. Parse and validate input
        2. Calculate totals
        3. Update database tables
        4. Generate audit trail
        """
        try:
            # Step 1: Parse input
            parsed_result = self.input_parser.parse(submission.input_text)
            
            # Step 2: Calculate totals
            calc_result = self.calculation_engine.calculate_total(parsed_result)
            
            # Step 3: Validate calculated total matches preview
            if calc_result.grand_total != submission.expected_total:
                raise ValidationError(
                    f"Calculated total {calc_result.grand_total} "
                    f"doesn't match expected {submission.expected_total}"
                )
            
            # Step 4: Begin database transaction
            with self.db_manager.transaction():
                # Update universal log
                log_entries = self.create_universal_log_entries(
                    submission, parsed_result
                )
                self.db_manager.insert_universal_log_entries(log_entries)
                
                # Update specific tables
                self.update_pana_table(submission, parsed_result.pana_entries)
                self.update_time_table(submission, parsed_result.time_entries, parsed_result.multi_entries)
                self.update_customer_summary(submission)
            
            return ProcessingResult(success=True, total=calc_result.grand_total)
            
        except Exception as e:
            return ProcessingResult(success=False, error=str(e))
```

### 2. Pana Table Update Logic
```python
def update_pana_table(self, submission: EntrySubmission, entries: List[PanaEntry]):
    """
    Update pana table with new entries
    
    Business Rules:
    - Pana table is unique per bazar (different bazars have separate pana values)
    - Common across all customers (not customer-specific)
    - Values accumulate for same bazar/date/number combination
    - Each entry also goes to universal log with customer info
    """
    for entry in entries:
        # Update bazar-specific pana table
        self.db_manager.upsert_pana_entry(
            bazar=submission.bazar,
            date=submission.date,
            number=entry.number,
            value=entry.value  # This will be added to existing value
        )
        
        # Also create universal log entry for audit trail
        self.db_manager.insert_universal_log_entry(
            customer_id=submission.customer_id,
            bazar=submission.bazar,
            date=submission.date,
            number=entry.number,
            value=entry.value,
            entry_type='PANA'
        )
```

### 3. Time Table Update Logic
```python
def update_time_table(self, submission: EntrySubmission, 
                     time_entries: List[TimeEntry], 
                     multi_entries: List[MultiEntry]):
    """
    Update time table with direct and multiplication entries
    
    Business Rules:
    - Time table is customer-specific (each customer has their own row)
    - Columns 0-9 represent different time slots
    - Values accumulate in customer's specific columns
    - Both direct entries and multiplication entries update time table
    """
    column_updates = {}
    
    # Process direct time entries (Type 3)
    for entry in time_entries:
        for column in entry.columns:
            if column not in column_updates:
                column_updates[column] = 0
            # Distribute value across specified columns
            column_updates[column] += entry.value // len(entry.columns)
        
        # Create universal log entries for each column
        for column in entry.columns:
            self.db_manager.insert_universal_log_entry(
                customer_id=submission.customer_id,
                bazar=submission.bazar,
                date=submission.date,
                number=column,  # Column number as identifier
                value=entry.value // len(entry.columns),
                entry_type='TIME_DIRECT'
            )
    
    # Process multiplication entries (Type 4)
    for entry in multi_entries:
        # Extract digits and update corresponding columns
        digit_columns = self.extract_digit_columns(entry)
        
        for column, value in digit_columns.items():
            if column not in column_updates:
                column_updates[column] = 0
            column_updates[column] += value
            
            # Create universal log entry
            self.db_manager.insert_universal_log_entry(
                customer_id=submission.customer_id,
                bazar=submission.bazar,
                date=submission.date,
                number=entry.number,  # Original number (e.g., 38)
                value=value,
                entry_type='MULTIPLICATION'
            )
    
    # Apply all column updates to customer's time table row
    if column_updates:
        self.db_manager.update_time_table_columns(
            customer_id=submission.customer_id,
            bazar=submission.bazar,
            date=submission.date,
            column_updates=column_updates
        )
```

### 4. Customer Summary Update Logic
```python
def update_customer_summary(self, submission: EntrySubmission):
    """
    Update customer's daily summary across all bazars
    """
    # Get all universal log entries for customer on this date
    daily_entries = self.db_manager.get_customer_daily_entries(
        customer_id=submission.customer_id,
        date=submission.date
    )
    
    # Calculate totals by bazar
    bazar_totals = {}
    for entry in daily_entries:
        bazar = entry.bazar
        if bazar not in bazar_totals:
            bazar_totals[bazar] = 0
        bazar_totals[bazar] += entry.value
    
    # Update summary table
    self.db_manager.upsert_customer_summary(
        customer_id=submission.customer_id,
        date=submission.date,
        bazar_totals=bazar_totals
    )
```

## Input Parsing & Format Detection

### Format Detection Patterns
```python
class InputPatternDetector:
    """Detect input format patterns for proper routing"""
    
    def is_multiplication_format(self, line: str) -> bool:
        """Detect: 38x700, 83x700"""
        import re
        pattern = r'^\d+x\d+$'
        return bool(re.match(pattern, line.strip()))
    
    def is_type_table_format(self, line: str) -> bool:
        """Detect: 1SP=100, 5DP=200, 25CP=150"""
        import re
        pattern = r'^\d+(SP|DP|CP)\s*=\s*.*\d+.*$'
        return bool(re.match(pattern, line.strip(), re.IGNORECASE))
    
    def is_time_direct_format(self, line: str) -> bool:
        """Detect: 1=100, 0 1 3 5 = 900"""
        import re
        # Single or multiple digits followed by equals
        pattern = r'^[\d\s]+\s*=\s*.*\d+.*$'
        if re.match(pattern, line.strip()):
            # Must not contain letters (to exclude type table format)
            return not re.search(r'[a-zA-Z]', line)
        return False
    
    def is_single_pana_format(self, line: str) -> bool:
        """Detect: 128/129/120 = 100, 128,129,120 = 100"""
        import re
        # Numbers separated by delimiters, followed by equals
        pattern = r'^[\d\s/+,*]+\s*=\s*.*\d+.*$'
        if re.match(pattern, line.strip()):
            # Should contain multiple numbers
            numbers = re.findall(r'\d+', line.split('=')[0])
            return len(numbers) > 1
        return False
    
    def is_multiline_pana_start(self, line: str) -> bool:
        """Detect start of multiline pana: numbers without equals"""
        import re
        # Line with numbers and delimiters but no equals
        pattern = r'^[\d\s/+,*]+$'
        if re.match(pattern, line.strip()):
            numbers = re.findall(r'\d+', line)
            return len(numbers) > 0
        return False

### Value Extraction
```python
def extract_value_from_string(self, value_str: str) -> int:
    """
    Extract numeric value from various formats:
    - "100" → 100
    - "Rs100" → 100  
    - "R100" → 100
    - "Rs.100" → 100
    - "Rs. 100" → 100
    """
    import re
    # Remove currency symbols and extract digits
    cleaned = re.sub(r'[^\d]', '', value_str)
    if cleaned:
        return int(cleaned)
    raise ValidationError(f"No numeric value found in: {value_str}")

### Number Parsing
```python
def parse_numbers_from_line(self, line: str) -> List[int]:
    """
    Parse numbers from various delimiter formats:
    - "128/129/120" → [128, 129, 120]
    - "128+129+120" → [128, 129, 120]  
    - "128 129 120" → [128, 129, 120]
    - "128,129,120" → [128, 129, 120]
    - "128*129*120" → [128, 129, 120]
    """
    import re
    # Extract all numbers from the line
    numbers = re.findall(r'\d+', line)
    return [int(num) for num in numbers]
```

## Validation Rules

### 1. Input Validation
```python
class BusinessValidator:
    """Business rule validation"""
    
    def validate_submission(self, submission: EntrySubmission) -> ValidationResult:
        """Comprehensive business validation"""
        errors = []
        warnings = []
        
        # Rule: Customer must exist
        if not self.db_manager.customer_exists(submission.customer_id):
            errors.append(f"Customer ID {submission.customer_id} not found")
        
        # Rule: Bazar must be valid
        if not self.db_manager.bazar_exists(submission.bazar):
            errors.append(f"Bazar {submission.bazar} not found")
        
        # Rule: Date cannot be in future
        if submission.date > datetime.date.today():
            errors.append("Entry date cannot be in the future")
        
        # Rule: Total must be positive
        if submission.expected_total < 0:
            errors.append("Total value cannot be negative")
        
        # Rule: Check for potential duplicates
        recent_entries = self.db_manager.get_recent_entries(
            customer_id=submission.customer_id,
            bazar=submission.bazar,
            date=submission.date,
            minutes=5
        )
        
        if recent_entries:
            warnings.append("Similar entry was made recently")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )

def validate_input_format(self, input_text: str) -> ValidationResult:
    """Additional input format validation"""
    errors = []
    
    lines = input_text.strip().split('\n')
    for i, line in enumerate(lines, 1):
        if not line.strip():
            continue
            
        # Check if line matches any known format
        if not (self.is_multiplication_format(line) or
                self.is_type_table_format(line) or
                self.is_time_direct_format(line) or
                self.is_single_pana_format(line) or
                self.is_multiline_pana_start(line)):
            errors.append(f"Line {i}: Unrecognized format - {line}")
    
    return ValidationResult(
        is_valid=len(errors) == 0,
        errors=errors,
        warnings=[]
    )
```

## Comprehensive Example Walkthrough

### Input Example:
```
6 8 9 0 = 3300
589,478,140,189,
145,147,370,269,
148,470,125,129,134,458,
569,679,180,236,
239,347= 260

124=400
147=250
4=24000

38x700
83x700
```

### Processing Breakdown:

#### 1. Line: `6 8 9 0 = 3300`
- **Type**: Time Direct (Type 3)
- **Processing**: Distribute 3300 across columns 6, 8, 9, 0
- **Column Updates**: Each gets 3300/4 = 825
- **Total Contribution**: 3300 × 4 = 13,200 (value × number of columns)

#### 2. Lines: Multiline Pana Block
```
589,478,140,189,
145,147,370,269,
148,470,125,129,134,458,
569,679,180,236,
239,347= 260
```
- **Type**: Pana Multiline (Type 1)
- **Count**: 20 numbers total
- **Processing**: Each number gets value 260 in pana table
- **Total Contribution**: 20 × 260 = 5,200

#### 3. Lines: Single Pana Entries
```
124=400
147=250  
4=24000
```
- **Type**: Single Pana (Type 1)
- **Processing**: Each number gets its specified value
- **Total Contribution**: 400 + 250 + 24000 = 24,650

#### 4. Lines: Multiplication Entries
```
38x700
83x700
```
- **Type**: Multiplication (Type 4)
- **Processing**: 
  - 38x700: Add 700 to columns 3 and 8 in time table
  - 83x700: Add 700 to columns 8 and 3 in time table
- **Total Contribution**: 700 + 700 = 1,400

### Final Calculations:
- **Time Direct Total**: 13,200 (3,300 × 4 columns)
- **Pana Total**: 5,200 + 24,650 = 29,850
- **Multiplication Total**: 1,400
- **Grand Total**: 13,200 + 29,850 + 1,400 = **44,450**

### Database Updates:

#### Universal Log Entries:
- Customer entries for all input types with individual values
- Audit trail for every number and value combination

#### Pana Table Updates:
- 23 numbers updated with their respective values (bazar-specific)
- Values accumulate if numbers already exist

#### Time Table Updates:
- Customer's row updated with column values:
  - Columns 6,8,9,0: +825 each (from direct entry)
  - Column 3: +1400 (from 38x700 + 83x700)
  - Column 8: +1400 (from 38x700 + 83x700)

#### Customer Summary:
- Daily total updated with grand total for the bazar
```

### 2. Data Integrity Rules
```python
def validate_data_integrity(self) -> IntegrityReport:
    """
    Validate data integrity across all tables
    """
    issues = []
    
    # Rule: Universal log totals should match summary totals
    universal_totals = self.db_manager.get_universal_daily_totals()
    summary_totals = self.db_manager.get_summary_daily_totals()
    
    for (customer_id, date), universal_total in universal_totals.items():
        summary_total = summary_totals.get((customer_id, date), 0)
        if universal_total != summary_total:
            issues.append(
                f"Mismatch for customer {customer_id} on {date}: "
                f"Universal={universal_total}, Summary={summary_total}"
            )
    
    # Rule: Pana table values should sum correctly
    pana_totals = self.db_manager.get_pana_totals_by_date()
    universal_pana_totals = self.db_manager.get_universal_pana_totals_by_date()
    
    for date, pana_total in pana_totals.items():
        universal_total = universal_pana_totals.get(date, 0)
        if pana_total != universal_total:
            issues.append(
                f"Pana table mismatch on {date}: "
                f"Pana={pana_total}, Universal={universal_total}"
            )
    
    return IntegrityReport(issues=issues)
```

## Business Intelligence & Reporting

### 1. Daily Summary Calculations
```python
def calculate_daily_summary(self, date: datetime.date) -> DailySummary:
    """Calculate comprehensive daily summary"""
    
    # Customer activity
    active_customers = self.db_manager.get_active_customers(date)
    
    # Bazar activity
    bazar_totals = self.db_manager.get_bazar_totals(date)
    
    # Overall totals
    grand_total = sum(bazar_totals.values())
    
    # Entry statistics
    entry_count = self.db_manager.get_entry_count(date)
    unique_numbers = self.db_manager.get_unique_numbers_count(date)
    
    return DailySummary(
        date=date,
        active_customers=len(active_customers),
        bazar_totals=bazar_totals,
        grand_total=grand_total,
        entry_count=entry_count,
        unique_numbers=unique_numbers
    )
```

### 2. Customer Performance Metrics
```python
def calculate_customer_metrics(self, customer_id: int, 
                             start_date: datetime.date, 
                             end_date: datetime.date) -> CustomerMetrics:
    """Calculate customer performance metrics"""
    
    entries = self.db_manager.get_customer_entries(
        customer_id, start_date, end_date
    )
    
    total_value = sum(entry.value for entry in entries)
    active_days = len(set(entry.date for entry in entries))
    avg_daily_value = total_value / max(active_days, 1)
    
    # Bazar distribution
    bazar_distribution = {}
    for entry in entries:
        bazar = entry.bazar
        if bazar not in bazar_distribution:
            bazar_distribution[bazar] = 0
        bazar_distribution[bazar] += entry.value
    
    return CustomerMetrics(
        customer_id=customer_id,
        period_start=start_date,
        period_end=end_date,
        total_value=total_value,
        active_days=active_days,
        avg_daily_value=avg_daily_value,
        bazar_distribution=bazar_distribution
    )
```

## Error Handling & Recovery

### 1. Transaction Recovery
```python
def handle_transaction_failure(self, submission: EntrySubmission, error: Exception):
    """Handle failed transactions with rollback and logging"""
    
    # Log the failure
    self.error_logger.log_submission_failure(
        submission=submission,
        error=error,
        timestamp=datetime.datetime.now()
    )
    
    # Attempt to identify the cause
    if isinstance(error, ValidationError):
        return self.handle_validation_failure(submission, error)
    elif isinstance(error, DatabaseError):
        return self.handle_database_failure(submission, error)
    else:
        return self.handle_unknown_failure(submission, error)
```

### 2. Data Reconciliation
```python
def reconcile_data_discrepancies(self, date: datetime.date):
    """Reconcile and fix data discrepancies"""
    
    # Find discrepancies
    integrity_report = self.validate_data_integrity()
    
    for issue in integrity_report.issues:
        # Attempt automatic resolution
        if "Universal log totals" in issue:
            self.reconcile_summary_totals(date)
        elif "Pana table" in issue:
            self.reconcile_pana_totals(date)
    
    # Re-validate after reconciliation
    return self.validate_data_integrity()
```

This comprehensive business logic specification ensures accurate calculations, data integrity, and robust error handling across all system operations.