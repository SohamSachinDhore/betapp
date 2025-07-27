"""Type table input parser for Type 2 patterns (1SP=100, 5DP=200, 15CP=300)"""

import re
from typing import List, Set, Optional, Dict, Any
from ..database.models import TypeTableEntry, ValidationResult
from ..utils.error_handler import ParseError, ValidationError
from ..utils.logger import get_logger

class TypeTableParser:
    """Type table input parser with SP/DP/CP table validation"""
    
    def __init__(self, type_table_validator: Optional['TypeTableValidator'] = None):
        self.validator = type_table_validator
        self.logger = get_logger(__name__)
        
        # Regex pattern for type table format
        self.pattern = re.compile(r'(\d+)(SP|DP|CP)\s*=\s*(\d+)', re.IGNORECASE)
    
    def parse(self, input_text: str) -> List[TypeTableEntry]:
        """
        Main parsing entry point for type table format
        
        Supported formats:
        - Single line: "1SP=100"
        - Multi-line: Multiple lines with different table types
        - Mixed table types: SP, DP, CP in same input
        
        Args:
            input_text: Raw input text to parse
            
        Returns:
            List of validated TypeTableEntry objects
            
        Raises:
            ParseError: If parsing fails
            ValidationError: If validation fails
        """
        try:
            lines = self.preprocess_input(input_text)
            entries = []
            
            for line in lines:
                line_entries = self.parse_line(line)
                
                if self.validator:
                    validated_entries = self.validator.validate_entries(line_entries)
                    entries.extend(validated_entries)
                else:
                    entries.extend(line_entries)
            
            self.logger.info(f"Successfully parsed {len(entries)} type table entries")
            return entries
            
        except Exception as e:
            self.logger.error(f"Type table parsing failed: {e}")
            raise ParseError(f"Failed to parse type table input: {str(e)}")
    
    def preprocess_input(self, input_text: str) -> List[str]:
        """Clean and normalize input text"""
        if not input_text:
            raise ParseError("Input text cannot be empty")
        
        lines = input_text.strip().split('\n')
        cleaned_lines = []
        
        for line in lines:
            # Remove extra whitespace
            line = ' '.join(line.split())
            
            # Remove currency indicators (Rs, R, Rs., Rs..)
            line = self.remove_currency_indicators(line)
            
            if line:
                cleaned_lines.append(line)
        
        if not cleaned_lines:
            raise ParseError("No valid lines found after preprocessing")
        
        return cleaned_lines
    
    def remove_currency_indicators(self, line: str) -> str:
        """Remove Rs, R, Rs., Rs.. patterns"""
        # Pattern to match currency after =
        pattern = r'(=\s*)(Rs\.{0,2}|R)\s*(\d+)'
        return re.sub(pattern, r'\1\3', line)
    
    def parse_line(self, line: str) -> List[TypeTableEntry]:
        """Parse single line format: 1SP=100"""
        matches = self.pattern.findall(line)
        
        if not matches:
            raise ParseError(f"No valid type table format found in line: {line}")
        
        entries = []
        for match in matches:
            column = int(match[0])
            table_type = match[1].upper()
            value = int(match[2])
            
            if value <= 0:
                raise ParseError(f"Invalid value: {value}")
            
            # Validate column range based on table type
            self._validate_column_range(column, table_type)
            
            try:
                entry = TypeTableEntry(
                    column=column,
                    table_type=table_type,
                    value=value
                )
                entries.append(entry)
            except ValueError as e:
                raise ValidationError(f"Invalid type table entry {column}{table_type}={value}: {e}")
        
        return entries
    
    def _validate_column_range(self, column: int, table_type: str):
        """Validate column range based on table type"""
        if table_type == 'SP':
            if not (1 <= column <= 10):
                raise ValidationError(f"SP table column must be 1-10, got: {column}")
        elif table_type == 'DP':
            if not (1 <= column <= 10):
                raise ValidationError(f"DP table column must be 1-10, got: {column}")
        elif table_type == 'CP':
            if not ((11 <= column <= 99) or column == 0):
                raise ValidationError(f"CP table column must be 11-99 or 0, got: {column}")
        else:
            raise ValidationError(f"Invalid table type: {table_type}")
    
    def extract_value(self, value_text: str) -> int:
        """Extract numeric value from text"""
        if not value_text:
            raise ParseError("Value text cannot be empty")
        
        # Extract first number found
        numbers = re.findall(r'\d+', value_text)
        if not numbers:
            raise ParseError(f"No numeric value found: {value_text}")
        
        value = int(numbers[0])
        if value <= 0:
            raise ParseError(f"Value must be positive: {value}")
        
        return value
    
    def get_supported_formats(self) -> List[str]:
        """Get list of supported input formats"""
        return [
            "1SP=100",      # Single Patti column 1, value 100
            "5DP=200",      # Double Patti column 5, value 200
            "15CP=300",     # Close Patti column 15, value 300
            "0CP=150",      # Close Patti column 0 (special case), value 150
            "1SP=100\n5DP=200",  # Multi-line format
            "1SP=100 5DP=200"    # Same line multiple entries
        ]
    
    def get_table_type_info(self) -> Dict[str, Dict[str, Any]]:
        """Get information about table types"""
        return {
            'SP': {
                'name': 'Single Patti',
                'column_range': '1-10',
                'description': 'Single digit patti table'
            },
            'DP': {
                'name': 'Double Patti',
                'column_range': '1-10', 
                'description': 'Double digit patti table'
            },
            'CP': {
                'name': 'Close Patti',
                'column_range': '11-99, 0',
                'description': 'Close patti table with special column 0'
            }
        }


class TypeTableValidator:
    """Validates type table entries against reference tables"""
    
    def __init__(self, sp_table: Dict[int, Set[int]], 
                 dp_table: Dict[int, Set[int]], 
                 cp_table: Dict[int, Set[int]]):
        """
        Initialize with reference tables
        
        Args:
            sp_table: SP table mapping {column: {valid_numbers}}
            dp_table: DP table mapping {column: {valid_numbers}}
            cp_table: CP table mapping {column: {valid_numbers}}
        """
        self.sp_table = sp_table
        self.dp_table = dp_table
        self.cp_table = cp_table
        self.logger = get_logger(__name__)
    
    def validate_entries(self, entries: List[TypeTableEntry]) -> List[TypeTableEntry]:
        """Validate all entries against type tables"""
        if not self._has_reference_data():
            self.logger.warning("No type table reference data available, skipping validation")
            return entries
        
        validated_entries = []
        
        for entry in entries:
            if self.is_valid_type_table_entry(entry):
                validated_entries.append(entry)
            else:
                raise ValidationError(
                    f"Invalid type table entry: {entry.column}{entry.table_type}={entry.value} "
                    f"- column {entry.column} not found in {entry.table_type} table"
                )
        
        self.logger.info(f"Validated {len(validated_entries)} type table entries")
        return validated_entries
    
    def is_valid_type_table_entry(self, entry: TypeTableEntry) -> bool:
        """Check if entry is valid for its table type"""
        if entry.table_type == 'SP':
            return entry.column in self.sp_table
        elif entry.table_type == 'DP':
            return entry.column in self.dp_table
        elif entry.table_type == 'CP':
            return entry.column in self.cp_table
        return False
    
    def get_valid_numbers_for_column(self, column: int, table_type: str) -> Set[int]:
        """Get valid numbers for a specific column and table type"""
        if table_type == 'SP':
            return self.sp_table.get(column, set())
        elif table_type == 'DP':
            return self.dp_table.get(column, set())
        elif table_type == 'CP':
            return self.cp_table.get(column, set())
        return set()
    
    def _has_reference_data(self) -> bool:
        """Check if reference data is available"""
        return bool(self.sp_table or self.dp_table or self.cp_table)
    
    def get_validation_stats(self) -> dict:
        """Get validation statistics"""
        return {
            'sp_columns': len(self.sp_table),
            'dp_columns': len(self.dp_table),
            'cp_columns': len(self.cp_table),
            'sp_total_numbers': sum(len(numbers) for numbers in self.sp_table.values()),
            'dp_total_numbers': sum(len(numbers) for numbers in self.dp_table.values()),
            'cp_total_numbers': sum(len(numbers) for numbers in self.cp_table.values())
        }


class TypeTableLoader:
    """Loads type table reference data from database"""
    
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.logger = get_logger(__name__)
    
    def load_all_tables(self) -> tuple:
        """Load all type tables from database"""
        sp_table = self.load_sp_table()
        dp_table = self.load_dp_table()  
        cp_table = self.load_cp_table()
        
        return sp_table, dp_table, cp_table
    
    def load_sp_table(self) -> Dict[int, Set[int]]:
        """Load SP table from database"""
        try:
            query = "SELECT column_number, number FROM type_table_sp"
            results = self.db_manager.execute_query(query)
            
            sp_table = {}
            for row in results:
                column = row['column_number']
                number = row['number']
                
                if column not in sp_table:
                    sp_table[column] = set()
                sp_table[column].add(number)
            
            self.logger.info(f"Loaded SP table with {len(sp_table)} columns")
            return sp_table
            
        except Exception as e:
            self.logger.error(f"Failed to load SP table: {e}")
            return {}
    
    def load_dp_table(self) -> Dict[int, Set[int]]:
        """Load DP table from database"""
        try:
            query = "SELECT column_number, number FROM type_table_dp"
            results = self.db_manager.execute_query(query)
            
            dp_table = {}
            for row in results:
                column = row['column_number']
                number = row['number']
                
                if column not in dp_table:
                    dp_table[column] = set()
                dp_table[column].add(number)
            
            self.logger.info(f"Loaded DP table with {len(dp_table)} columns")
            return dp_table
            
        except Exception as e:
            self.logger.error(f"Failed to load DP table: {e}")
            return {}
    
    def load_cp_table(self) -> Dict[int, Set[int]]:
        """Load CP table from database"""
        try:
            query = "SELECT column_number, number FROM type_table_cp"
            results = self.db_manager.execute_query(query)
            
            cp_table = {}
            for row in results:
                column = row['column_number']
                number = row['number']
                
                if column not in cp_table:
                    cp_table[column] = set()
                cp_table[column].add(number)
            
            self.logger.info(f"Loaded CP table with {len(cp_table)} columns")
            return cp_table
            
        except Exception as e:
            self.logger.error(f"Failed to load CP table: {e}")
            return {}
    
    def create_validator(self) -> TypeTableValidator:
        """Create validator with loaded reference data"""
        sp_table, dp_table, cp_table = self.load_all_tables()
        return TypeTableValidator(sp_table, dp_table, cp_table)