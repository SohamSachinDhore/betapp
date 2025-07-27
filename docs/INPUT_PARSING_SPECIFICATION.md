# RickyMama - Input Parsing & Validation Specification

## Overview

The input parsing system is the core component responsible for interpreting user inputs and converting them into structured data. It handles 5 distinct pattern types with intelligent pattern recognition and robust validation.

## Pattern Recognition Algorithm

### Primary Pattern Detection
```python
class PatternDetector:
    """Intelligent pattern recognition for input classification"""
    
    PATTERNS = {
        'PANA_TABLE': r'(\d{3}[\/\+\s\,\*]+\d{3}.*=.*\d+)',
        'TYPE_TABLE': r'(\d+)(SP|DP|CP)\s*=\s*\d+',
        'TIME_DIRECT': r'^(\d[\s\d]*)\s*=\s*\d+$',
        'TIME_MULTIPLY': r'(\d{2})x(\d+)',
        'MIXED': 'multiple_patterns_detected'
    }
    
    def detect_pattern_type(self, line: str) -> PatternType:
        """
        Pattern detection priority:
        1. TYPE_TABLE (highest specificity)
        2. TIME_MULTIPLY (specific format)
        3. PANA_TABLE (complex separators)
        4. TIME_DIRECT (simple format)
        5. MIXED (fallback)
        """
        pass
```

## Type 1: Pana Table Pattern Parser

### Supported Input Formats
```python
PANA_FORMATS = [
    "128/129/120 = 100",      # Slash separator
    "128+129+120 = 100",      # Plus separator  
    "128 129 120 = 100",      # Space separator
    "128,129,120 = 100",      # Comma separator
    "128*129*120 = 100",      # Star separator
]

MULTILINE_FORMATS = [
    # Standard multiline
    """128/129/120 = 100
       145/147/148 = 200""",
    
    # Grouped assignment
    """128,129,120
       145,147,148
       150,160,170 = 100""",
    
    # Split assignment
    """128,129,120
       145,147,148
       = 150"""
]
```

### Parser Implementation
```python
class PanaTableParser:
    """Pana table input parser with validation"""
    
    def __init__(self, pana_validator: PanaValidator):
        self.validator = pana_validator
        self.separators = ['/', '+', ' ', ',', '*']
        
    def parse(self, input_text: str) -> List[PanaEntry]:
        """
        Main parsing entry point
        Returns: List of validated pana entries
        """
        lines = self.preprocess_input(input_text)
        entries = []
        
        for line_group in self.group_multiline_entries(lines):
            parsed_group = self.parse_line_group(line_group)
            validated_group = self.validator.validate_entries(parsed_group)
            entries.extend(validated_group)
            
        return entries
    
    def preprocess_input(self, input_text: str) -> List[str]:
        """Clean and normalize input text"""
        lines = input_text.strip().split('\n')
        cleaned_lines = []
        
        for line in lines:
            # Remove extra whitespace
            line = ' '.join(line.split())
            # Remove currency indicators
            line = self.remove_currency_indicators(line)
            if line:
                cleaned_lines.append(line)
                
        return cleaned_lines
    
    def remove_currency_indicators(self, line: str) -> str:
        """Remove Rs, R, Rs., Rs.. patterns"""
        import re
        # Pattern to match currency after =
        pattern = r'(=\s*)(Rs\.{0,2}|R)\s*(\d+)'
        return re.sub(pattern, r'\1\3', line)
    
    def group_multiline_entries(self, lines: List[str]) -> List[List[str]]:
        """Group related lines for multiline parsing"""
        groups = []
        current_group = []
        
        for line in lines:
            if '=' in line:
                if current_group:
                    # Previous group exists, add value line
                    current_group.append(line)
                    groups.append(current_group)
                    current_group = []
                else:
                    # Single line entry
                    groups.append([line])
            else:
                # Number line without value
                current_group.append(line)
        
        # Handle trailing group with separate value line
        if current_group:
            groups.append(current_group)
            
        return groups
    
    def parse_line_group(self, line_group: List[str]) -> List[PanaEntry]:
        """Parse a group of related lines"""
        if len(line_group) == 1:
            return self.parse_single_line(line_group[0])
        else:
            return self.parse_multiline_group(line_group)
    
    def parse_single_line(self, line: str) -> List[PanaEntry]:
        """Parse single line format: 128/129/120 = 100"""
        parts = line.split('=')
        if len(parts) != 2:
            raise ParseError(f"Invalid format: {line}")
        
        numbers_part = parts[0].strip()
        value_part = parts[1].strip()
        
        numbers = self.extract_numbers(numbers_part)
        value = self.extract_value(value_part)
        
        return [PanaEntry(number=num, value=value) for num in numbers]
    
    def parse_multiline_group(self, line_group: List[str]) -> List[PanaEntry]:
        """Parse multiline format with grouped assignment"""
        value_line = None
        number_lines = []
        
        # Separate number lines from value line
        for line in line_group:
            if '=' in line:
                value_line = line
            else:
                number_lines.append(line)
        
        # Extract value
        if value_line:
            value = self.extract_value_from_line(value_line)
        else:
            raise ParseError("No value assignment found in multiline group")
        
        # Extract all numbers
        all_numbers = []
        for line in number_lines:
            numbers = self.extract_numbers(line)
            all_numbers.extend(numbers)
        
        return [PanaEntry(number=num, value=value) for num in all_numbers]
    
    def extract_numbers(self, numbers_text: str) -> List[int]:
        """Extract numbers using multiple separator support"""
        import re
        
        # Try different separators
        for separator in self.separators:
            if separator in numbers_text:
                parts = numbers_text.split(separator)
                numbers = []
                for part in parts:
                    part = part.strip()
                    if part and part.isdigit():
                        numbers.append(int(part))
                return numbers
        
        # Space-separated fallback
        parts = numbers_text.split()
        numbers = []
        for part in parts:
            if part.isdigit():
                numbers.append(int(part))
        
        return numbers
    
    def extract_value(self, value_text: str) -> int:
        """Extract numeric value from text"""
        import re
        
        # Extract first number found
        numbers = re.findall(r'\d+', value_text)
        if not numbers:
            raise ParseError(f"No numeric value found: {value_text}")
        
        return int(numbers[0])
    
    def extract_value_from_line(self, line: str) -> int:
        """Extract value from line containing ="""
        if '=' in line:
            value_part = line.split('=')[1].strip()
            return self.extract_value(value_part)
        else:
            return self.extract_value(line)

@dataclass
class PanaEntry:
    """Pana table entry data structure"""
    number: int
    value: int
    
    def __post_init__(self):
        if not (100 <= self.number <= 999):
            raise ValueError(f"Invalid pana number: {self.number}")
        if self.value < 0:
            raise ValueError(f"Invalid value: {self.value}")
```

### Validation Logic
```python
class PanaValidator:
    """Validates pana table entries against reference table"""
    
    def __init__(self, pana_reference_table: Set[int]):
        self.valid_numbers = pana_reference_table
        
    def validate_entries(self, entries: List[PanaEntry]) -> List[PanaEntry]:
        """Validate all entries against pana table"""
        validated_entries = []
        
        for entry in entries:
            if self.is_valid_pana_number(entry.number):
                validated_entries.append(entry)
            else:
                raise ValidationError(
                    f"Invalid pana number: {entry.number} not found in pana table"
                )
        
        return validated_entries
    
    def is_valid_pana_number(self, number: int) -> bool:
        """Check if number exists in pana reference table"""
        return number in self.valid_numbers
```

## Type 2: Type Table Pattern Parser

### Format Specification
```python
TYPE_TABLE_FORMATS = [
    "1SP=100",    # Single-digit column, SP table
    "10DP=200",   # Double-digit column, DP table
    "25CP=300",   # CP table format
    "0CP=150",    # Special case: 0 column in CP
]

TABLE_DEFINITIONS = {
    'SP': {'columns': range(1, 11), 'size': (12, 10)},      # 1-10
    'DP': {'columns': range(1, 11), 'size': (9, 10)},       # 1-10  
    'CP': {'columns': list(range(11, 100)) + [0], 'size': (10, 90)},  # 11-99, 0
}
```

### Parser Implementation
```python
class TypeTableParser:
    """Type table query parser (1SP=100, 5DP=200, etc.)"""
    
    def __init__(self, type_table_data: Dict[str, List[List[int]]]):
        self.table_data = type_table_data
        self.valid_tables = ['SP', 'DP', 'CP']
        
    def parse(self, line: str) -> TypeEntry:
        """Parse type table format"""
        import re
        
        # Pattern: number + table_type + = + value
        pattern = r'(\d+)(SP|DP|CP)\s*=\s*(\d+)'
        match = re.match(pattern, line.strip(), re.IGNORECASE)
        
        if not match:
            raise ParseError(f"Invalid type table format: {line}")
        
        column = int(match.group(1))
        table_type = match.group(2).upper()
        value = int(match.group(3))
        
        # Validate column for table type
        if not self.is_valid_column(table_type, column):
            raise ValidationError(
                f"Invalid column {column} for table {table_type}"
            )
        
        # Get all numbers in the column
        column_numbers = self.get_column_numbers(table_type, column)
        
        return TypeEntry(
            table_type=table_type,
            column=column,
            value=value,
            numbers=column_numbers
        )
    
    def is_valid_column(self, table_type: str, column: int) -> bool:
        """Validate column number for table type"""
        valid_columns = TABLE_DEFINITIONS[table_type]['columns']
        return column in valid_columns
    
    def get_column_numbers(self, table_type: str, column: int) -> List[int]:
        """Retrieve all numbers from specified table column"""
        table = self.table_data[table_type]
        column_index = column - 1 if table_type in ['SP', 'DP'] else self.get_cp_column_index(column)
        
        numbers = []
        for row in table:
            if column_index < len(row):
                numbers.append(row[column_index])
        
        return numbers
    
    def get_cp_column_index(self, column: int) -> int:
        """Get CP table column index (special handling for 0)"""
        if column == 0:
            return 89  # Last column
        else:
            return column - 11  # Offset for 11-99 range

@dataclass
class TypeEntry:
    """Type table entry data structure"""
    table_type: str
    column: int
    value: int
    numbers: List[int]
```

## Type 3: Time Table Direct Parser

### Format Specification
```python
TIME_DIRECT_FORMATS = [
    "1=100",          # Single column
    "0 1 3 5 = 900",  # Multiple columns
    "2 4 6 8 = 1200", # Even columns
    "1 3 5 7 9 = 500", # Odd columns
]
```

### Parser Implementation
```python
class TimeTableParser:
    """Time table direct entry parser"""
    
    def __init__(self):
        self.valid_columns = list(range(10))  # 0-9
        
    def parse(self, line: str) -> TimeEntry:
        """Parse time table direct format"""
        parts = line.split('=')
        if len(parts) != 2:
            raise ParseError(f"Invalid time table format: {line}")
        
        columns_part = parts[0].strip()
        value_part = parts[1].strip()
        
        columns = self.extract_columns(columns_part)
        value = int(value_part)
        
        # Validate columns
        for col in columns:
            if col not in self.valid_columns:
                raise ValidationError(f"Invalid time table column: {col}")
        
        return TimeEntry(columns=columns, value=value)
    
    def extract_columns(self, columns_text: str) -> List[int]:
        """Extract column numbers from text"""
        columns = []
        for part in columns_text.split():
            if part.isdigit() and 0 <= int(part) <= 9:
                columns.append(int(part))
        
        return columns

@dataclass
class TimeEntry:
    """Time table entry data structure"""
    columns: List[int]
    value: int
```

## Type 4: Multiplication Pattern Parser

### Format Specification
```python
MULTIPLICATION_FORMATS = [
    "38x700",  # Tens=3, Units=8, Value=700
    "83x700",  # Tens=8, Units=3, Value=700
    "05x100",  # Tens=0, Units=5, Value=100
    "90x200",  # Tens=9, Units=0, Value=200
]
```

### Parser Implementation
```python
class MultiplicationParser:
    """Multiplication format parser (38x700)"""
    
    def parse(self, line: str) -> MultiEntry:
        """Parse multiplication format"""
        import re
        
        pattern = r'(\d{2})x(\d+)'
        match = re.match(pattern, line.strip())
        
        if not match:
            raise ParseError(f"Invalid multiplication format: {line}")
        
        number = match.group(1)
        value = int(match.group(2))
        
        # Extract tens and units digits
        tens_digit = int(number[0])
        units_digit = int(number[1])
        
        return MultiEntry(
            number=int(number),
            tens_digit=tens_digit,
            units_digit=units_digit,
            value=value
        )

@dataclass
class MultiEntry:
    """Multiplication entry data structure"""
    number: int
    tens_digit: int
    units_digit: int
    value: int
```

## Type 5: Mixed Input Parser

### Mixed Pattern Detection
```python
class MixedInputParser:
    """Handles inputs containing multiple pattern types"""
    
    def __init__(self, individual_parsers: Dict[str, Any]):
        self.parsers = individual_parsers
        
    def parse(self, input_text: str) -> MixedParseResult:
        """Parse mixed input with multiple pattern types"""
        lines = input_text.strip().split('\n')
        results = {
            'pana_entries': [],
            'type_entries': [],
            'time_entries': [],
            'multi_entries': []
        }
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            pattern_type = self.detect_line_pattern(line)
            
            try:
                if pattern_type == 'PANA_TABLE':
                    results['pana_entries'].extend(
                        self.parsers['pana'].parse(line)
                    )
                elif pattern_type == 'TYPE_TABLE':
                    results['type_entries'].append(
                        self.parsers['type'].parse(line)
                    )
                elif pattern_type == 'TIME_DIRECT':
                    results['time_entries'].append(
                        self.parsers['time'].parse(line)
                    )
                elif pattern_type == 'TIME_MULTIPLY':
                    results['multi_entries'].append(
                        self.parsers['multi'].parse(line)
                    )
                else:
                    raise ParseError(f"Unknown pattern: {line}")
                    
            except (ParseError, ValidationError) as e:
                # Collect parsing errors for user feedback
                results.setdefault('errors', []).append({
                    'line': line,
                    'error': str(e)
                })
        
        return MixedParseResult(**results)
    
    def detect_line_pattern(self, line: str) -> str:
        """Detect pattern type for individual line"""
        import re
        
        # Priority-based detection
        if re.search(r'\d+(SP|DP|CP)\s*=', line, re.IGNORECASE):
            return 'TYPE_TABLE'
        elif re.search(r'\d{2}x\d+', line):
            return 'TIME_MULTIPLY'
        elif re.search(r'\d{3}[\/\+\s\,\*]+.*=', line):
            return 'PANA_TABLE'
        elif re.search(r'^[\d\s]+\s*=\s*\d+$', line):
            return 'TIME_DIRECT'
        else:
            return 'UNKNOWN'

@dataclass
class MixedParseResult:
    """Result of mixed input parsing"""
    pana_entries: List[PanaEntry]
    type_entries: List[TypeEntry]
    time_entries: List[TimeEntry]
    multi_entries: List[MultiEntry]
    errors: List[Dict[str, str]] = None
```

## Input Validation Framework

### Comprehensive Validator
```python
class InputValidator:
    """Master input validator"""
    
    def __init__(self, pana_table: Set[int], type_tables: Dict):
        self.pana_validator = PanaValidator(pana_table)
        self.type_validator = TypeTableValidator(type_tables)
        self.time_validator = TimeTableValidator()
        
    def validate_input(self, input_text: str) -> ValidationResult:
        """Comprehensive input validation"""
        errors = []
        warnings = []
        
        # Basic format validation
        if not input_text.strip():
            errors.append("Input cannot be empty")
            return ValidationResult(False, errors, warnings)
        
        # Line count validation
        lines = input_text.strip().split('\n')
        if len(lines) > 1000:
            errors.append("Input exceeds maximum line limit (1000)")
        
        # Character validation
        if len(input_text) > 50000:
            warnings.append("Input is very large, processing may be slow")
        
        # Pattern-specific validation
        for line in lines:
            line_errors = self.validate_line(line.strip())
            errors.extend(line_errors)
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )
    
    def validate_line(self, line: str) -> List[str]:
        """Validate individual line"""
        if not line:
            return []
        
        errors = []
        
        # Detect pattern and validate accordingly
        pattern = self.detect_pattern(line)
        
        try:
            if pattern == 'PANA_TABLE':
                self.validate_pana_line(line)
            elif pattern == 'TYPE_TABLE':
                self.validate_type_line(line)
            elif pattern == 'TIME_DIRECT':
                self.validate_time_line(line)
            elif pattern == 'TIME_MULTIPLY':
                self.validate_multi_line(line)
            else:
                errors.append(f"Unrecognized pattern: {line}")
        except ValidationError as e:
            errors.append(str(e))
        
        return errors

@dataclass
class ValidationResult:
    """Validation result data structure"""
    is_valid: bool
    errors: List[str]
    warnings: List[str]
```

## Error Handling

### Custom Exceptions
```python
class ParseError(Exception):
    """Raised when input cannot be parsed"""
    pass

class ValidationError(Exception):
    """Raised when input fails validation"""
    pass

class PatternError(Exception):
    """Raised when pattern cannot be detected"""
    pass
```

### Error Recovery Strategies
```python
class ErrorRecovery:
    """Input error recovery strategies"""
    
    def suggest_corrections(self, error: ParseError, line: str) -> List[str]:
        """Suggest possible corrections for parsing errors"""
        suggestions = []
        
        if "Invalid format" in str(error):
            suggestions.extend(self.format_suggestions(line))
        elif "Invalid number" in str(error):
            suggestions.extend(self.number_suggestions(line))
        
        return suggestions
    
    def format_suggestions(self, line: str) -> List[str]:
        """Suggest format corrections"""
        suggestions = []
        
        if '=' not in line:
            suggestions.append("Add '=' to specify value assignment")
        
        if not any(sep in line for sep in ['/', '+', ',', '*', ' ']):
            suggestions.append("Use separators: /, +, comma, *, or space")
        
        return suggestions
```

This comprehensive input parsing specification provides robust pattern recognition, validation, and error handling for all 5 input types while maintaining flexibility and user-friendly error recovery.