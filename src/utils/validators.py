"""Input validation utilities for RickyMama application"""

import re
from datetime import datetime, date
from typing import List, Optional, Set, Tuple
from .error_handler import ValidationError

class InputValidator:
    """Input validation and sanitization"""
    
    def __init__(self, pana_reference_table: Optional[Set[int]] = None):
        self.pana_numbers = pana_reference_table or set()
        
        # Regex patterns for validation
        self.patterns = {
            'pana_table': r'(\d{3}[\/\+\s\,\*]+.*=.*\d+)',
            'type_table': r'(\d+)(SP|DP|CP)\s*=\s*\d+',
            'time_direct': r'^([\d\s]+)\s*=\s*\d+$',
            'time_multiply': r'(\d{2})x(\d+)',
            'currency': r'(=\s*)(Rs\.{0,2}|R)\s*(\d+)',
            'number': r'\d+',
            'value': r'=\s*\d+'
        }
    
    def validate_customer_name(self, name: str) -> bool:
        """Validate customer name"""
        if not name or not isinstance(name, str):
            raise ValidationError("Customer name cannot be empty")
        
        name = name.strip()
        if len(name) < 1 or len(name) > 100:
            raise ValidationError("Customer name must be between 1 and 100 characters")
        
        # Check for valid characters (letters, numbers, spaces, basic punctuation)
        if not re.match(r'^[a-zA-Z0-9\s\.\-\_]+$', name):
            raise ValidationError("Customer name contains invalid characters")
        
        return True
    
    def validate_date(self, date_str: str) -> bool:
        """Validate date string"""
        if not date_str:
            raise ValidationError("Date cannot be empty")
        
        # Try different date formats
        date_formats = ['%d-%m-%Y', '%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y']
        
        for fmt in date_formats:
            try:
                parsed_date = datetime.strptime(date_str, fmt).date()
                
                # Check if date is reasonable (not too far in past/future)
                today = date.today()
                if abs((parsed_date - today).days) > 3650:  # 10 years
                    raise ValidationError("Date is too far in the past or future")
                
                return True
            except ValueError:
                continue
        
        raise ValidationError(f"Invalid date format: {date_str}")
    
    def validate_bazar(self, bazar: str) -> bool:
        """Validate bazar name"""
        if not bazar or not isinstance(bazar, str):
            raise ValidationError("Bazar name cannot be empty")
        
        bazar = bazar.strip()
        if len(bazar) < 1 or len(bazar) > 10:
            raise ValidationError("Bazar name must be between 1 and 10 characters")
        
        # Check for valid characters
        if not re.match(r'^[a-zA-Z0-9\.]+$', bazar):
            raise ValidationError("Bazar name contains invalid characters")
        
        return True
    
    def validate_number_input(self, line: str) -> Tuple[bool, List[str]]:
        """Validate a single line of number input
        
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        if not line or not line.strip():
            errors.append("Empty input line")
            return False, errors
        
        line = line.strip()
        
        # Check line length
        if len(line) > 1000:
            errors.append("Input line too long (max 1000 characters)")
        
        # Check for basic format patterns
        has_equals = '=' in line
        if not has_equals:
            errors.append("No value assignment found (missing '=')")
        
        # Check for numbers
        numbers = re.findall(r'\d+', line)
        if not numbers:
            errors.append("No numbers found in input")
        
        # Validate specific patterns
        try:
            self._validate_pattern_specific(line)
        except ValidationError as e:
            errors.append(str(e))
        
        return len(errors) == 0, errors
    
    def _validate_pattern_specific(self, line: str):
        """Validate specific input patterns"""
        line = line.strip()
        
        # Check for type table pattern
        if re.search(self.patterns['type_table'], line, re.IGNORECASE):
            self._validate_type_table_line(line)
        
        # Check for multiplication pattern
        elif re.search(self.patterns['time_multiply'], line):
            self._validate_multiplication_line(line)
        
        # Check for pana table pattern
        elif re.search(self.patterns['pana_table'], line):
            self._validate_pana_table_line(line)
        
        # Check for time direct pattern
        elif re.search(self.patterns['time_direct'], line):
            self._validate_time_direct_line(line)
        
        else:
            raise ValidationError("Unrecognized input pattern")
    
    def _validate_type_table_line(self, line: str):
        """Validate type table format line"""
        match = re.search(self.patterns['type_table'], line, re.IGNORECASE)
        if not match:
            raise ValidationError("Invalid type table format")
        
        column = int(match.group(1))
        table_type = match.group(2).upper()
        
        # Validate column ranges for each table type
        if table_type in ['SP', 'DP'] and not (1 <= column <= 10):
            raise ValidationError(f"Invalid column {column} for {table_type} table (must be 1-10)")
        elif table_type == 'CP' and not ((11 <= column <= 99) or column == 0):
            raise ValidationError(f"Invalid column {column} for CP table (must be 11-99 or 0)")
    
    def _validate_multiplication_line(self, line: str):
        """Validate multiplication format line"""
        match = re.search(self.patterns['time_multiply'], line)
        if not match:
            raise ValidationError("Invalid multiplication format")
        
        number = match.group(1)
        value = int(match.group(2))
        
        if len(number) != 2:
            raise ValidationError("Multiplication number must be 2 digits")
        
        if value <= 0:
            raise ValidationError("Multiplication value must be positive")
    
    def _validate_pana_table_line(self, line: str):
        """Validate pana table format line"""
        # Extract numbers from the line
        parts = line.split('=')
        if len(parts) != 2:
            raise ValidationError("Invalid pana table format (missing or multiple '=')")
        
        numbers_part = parts[0].strip()
        value_part = parts[1].strip()
        
        # Extract numbers using different separators
        separators = ['/', '+', ',', '*']
        numbers = []
        
        for sep in separators:
            if sep in numbers_part:
                parts_list = numbers_part.split(sep)
                for part in parts_list:
                    part = part.strip()
                    if part.isdigit():
                        num = int(part)
                        if 100 <= num <= 999:
                            numbers.append(num)
                break
        else:
            # Space-separated fallback
            parts_list = numbers_part.split()
            for part in parts_list:
                if part.isdigit():
                    num = int(part)
                    if 100 <= num <= 999:
                        numbers.append(num)
        
        if not numbers:
            raise ValidationError("No valid pana numbers found")
        
        # Validate against pana reference table if available
        if self.pana_numbers:
            invalid_numbers = [num for num in numbers if num not in self.pana_numbers]
            if invalid_numbers:
                raise ValidationError(f"Invalid pana numbers: {invalid_numbers}")
    
    def _validate_time_direct_line(self, line: str):
        """Validate time direct format line"""
        parts = line.split('=')
        if len(parts) != 2:
            raise ValidationError("Invalid time direct format")
        
        columns_part = parts[0].strip()
        value_part = parts[1].strip()
        
        # Extract column numbers
        columns = []
        for part in columns_part.split():
            if part.isdigit():
                col = int(part)
                if 0 <= col <= 9:
                    columns.append(col)
                else:
                    raise ValidationError(f"Invalid time table column: {col} (must be 0-9)")
        
        if not columns:
            raise ValidationError("No valid column numbers found")
        
        # Validate value
        if not value_part.isdigit() or int(value_part) <= 0:
            raise ValidationError("Time direct value must be a positive number")
    
    def sanitize_input(self, input_text: str) -> str:
        """Sanitize and clean input text"""
        if not input_text:
            return ""
        
        # Remove excessive whitespace
        lines = input_text.strip().split('\n')
        cleaned_lines = []
        
        for line in lines:
            # Remove extra spaces
            line = ' '.join(line.split())
            
            # Remove currency indicators
            line = re.sub(self.patterns['currency'], r'\1\3', line)
            
            if line:
                cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)
    
    def validate_batch_input(self, input_text: str, max_lines: int = 1000) -> Tuple[bool, List[str]]:
        """Validate entire batch input
        
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        if not input_text or not input_text.strip():
            errors.append("Input cannot be empty")
            return False, errors
        
        lines = input_text.strip().split('\n')
        
        # Check line count
        if len(lines) > max_lines:
            errors.append(f"Too many lines (max {max_lines})")
        
        # Validate each line
        for i, line in enumerate(lines, 1):
            line = line.strip()
            if not line:
                continue  # Skip empty lines
            
            is_valid, line_errors = self.validate_number_input(line)
            if not is_valid:
                for error in line_errors:
                    errors.append(f"Line {i}: {error}")
        
        return len(errors) == 0, errors
    
    def load_pana_reference(self, pana_numbers: Set[int]):
        """Load pana reference numbers for validation"""
        self.pana_numbers = pana_numbers