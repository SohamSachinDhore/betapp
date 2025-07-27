"""Mixed input parser for Type 5 patterns (combinations of all pattern types)"""

from typing import List, Optional, Dict, Any, Tuple
from ..database.models import ParsedInputResult, ValidationResult
from ..utils.error_handler import ParseError, ValidationError
from ..utils.logger import get_logger

# Import individual parsers
from .pattern_detector import PatternDetector, PatternType
from .pana_parser import PanaTableParser, PanaValidator
from .type_table_parser import TypeTableParser, TypeTableValidator
from .time_table_parser import TimeTableParser, TimeTableValidator
from .multiplication_parser import MultiplicationParser, MultiplicationValidator
from .direct_number_parser import DirectNumberParser, DirectNumberValidator

class MixedInputParser:
    """Mixed input parser that handles multiple pattern types in single input"""
    
    def __init__(self, 
                 pana_validator: Optional[PanaValidator] = None,
                 type_validator: Optional[TypeTableValidator] = None,
                 time_validator: Optional[TimeTableValidator] = None,
                 multi_validator: Optional[MultiplicationValidator] = None,
                 direct_validator: Optional[DirectNumberValidator] = None):
        """
        Initialize with individual pattern validators
        
        Args:
            pana_validator: Validator for pana table entries
            type_validator: Validator for type table entries
            time_validator: Validator for time table entries
            multi_validator: Validator for multiplication entries
            direct_validator: Validator for direct number entries
        """
        self.pattern_detector = PatternDetector()
        
        # Initialize individual parsers
        self.pana_parser = PanaTableParser(pana_validator)
        self.type_parser = TypeTableParser(type_validator)
        self.time_parser = TimeTableParser(time_validator)
        self.multi_parser = MultiplicationParser(multi_validator)
        self.direct_parser = DirectNumberParser(direct_validator)
        
        self.logger = get_logger(__name__)
    
    def parse(self, input_text: str) -> ParsedInputResult:
        """
        Main parsing entry point for mixed input
        
        Analyzes input and routes lines to appropriate parsers based on detected patterns
        
        Args:
            input_text: Raw input text containing multiple pattern types
            
        Returns:
            ParsedInputResult containing all parsed entries by type
            
        Raises:
            ParseError: If parsing fails
            ValidationError: If validation fails
        """
        try:
            # Analyze input to detect overall pattern type
            overall_type, line_types, stats = self.pattern_detector.analyze_input(input_text)
            
            self.logger.info(f"Detected overall pattern: {overall_type.value}, "
                           f"confidence: {stats['confidence']:.2f}")
            
            if overall_type == PatternType.UNKNOWN:
                raise ParseError("No recognizable patterns found in input")
            
            # Process based on overall pattern type
            if overall_type == PatternType.MIXED:
                return self._parse_mixed_input(input_text, line_types)
            else:
                return self._parse_single_type_input(input_text, overall_type)
            
        except Exception as e:
            self.logger.error(f"Mixed input parsing failed: {e}")
            raise ParseError(f"Failed to parse mixed input: {str(e)}")
    
    def _parse_mixed_input(self, input_text: str, line_types: List[PatternType]) -> ParsedInputResult:
        """Parse input containing multiple pattern types"""
        lines = [line.strip() for line in input_text.strip().split('\n') if line.strip()]
        result = ParsedInputResult()
        
        # Group lines by pattern type
        pattern_groups = self._group_lines_by_pattern(lines, line_types)
        
        # Parse each pattern group
        for pattern_type, pattern_lines in pattern_groups.items():
            if not pattern_lines:
                continue
                
            combined_input = '\n'.join(pattern_lines)
            
            try:
                if pattern_type == PatternType.PANA_TABLE:
                    entries = self.pana_parser.parse(combined_input)
                    result.pana_entries.extend(entries)
                    
                elif pattern_type == PatternType.TYPE_TABLE:
                    entries = self.type_parser.parse(combined_input)
                    result.type_entries.extend(entries)
                    
                elif pattern_type == PatternType.TIME_DIRECT:
                    entries = self.time_parser.parse(combined_input)
                    result.time_entries.extend(entries)
                    
                elif pattern_type == PatternType.TIME_MULTIPLY:
                    entries = self.multi_parser.parse(combined_input)
                    result.multi_entries.extend(entries)
                    
                elif pattern_type == PatternType.DIRECT_NUMBER:
                    entries = self.direct_parser.parse(combined_input)
                    result.direct_entries.extend(entries)
                    
            except Exception as e:
                self.logger.warning(f"Failed to parse {pattern_type.value} lines: {e}")
                # Continue with other patterns instead of failing completely
        
        self.logger.info(f"Mixed parsing complete: {result.total_entries} total entries")
        return result
    
    def _parse_single_type_input(self, input_text: str, pattern_type: PatternType) -> ParsedInputResult:
        """Parse input containing single pattern type"""
        result = ParsedInputResult()
        
        try:
            if pattern_type == PatternType.PANA_TABLE:
                entries = self.pana_parser.parse(input_text)
                result.pana_entries = entries
                
            elif pattern_type == PatternType.TYPE_TABLE:
                entries = self.type_parser.parse(input_text)
                result.type_entries = entries
                
            elif pattern_type == PatternType.TIME_DIRECT:
                entries = self.time_parser.parse(input_text)
                result.time_entries = entries
                
            elif pattern_type == PatternType.TIME_MULTIPLY:
                entries = self.multi_parser.parse(input_text)
                result.multi_entries = entries
                
            elif pattern_type == PatternType.DIRECT_NUMBER:
                entries = self.direct_parser.parse(input_text)
                result.direct_entries = entries
                
        except Exception as e:
            raise ParseError(f"Failed to parse {pattern_type.value} input: {e}")
        
        self.logger.info(f"Single type parsing complete: {result.total_entries} total entries")
        return result
    
    def _group_lines_by_pattern(self, lines: List[str], line_types: List[PatternType]) -> Dict[PatternType, List[str]]:
        """Group lines by their detected pattern types"""
        pattern_groups = {}
        
        for line, pattern_type in zip(lines, line_types):
            if pattern_type == PatternType.UNKNOWN:
                self.logger.warning(f"Skipping unknown pattern line: {line}")
                continue
                
            if pattern_type not in pattern_groups:
                pattern_groups[pattern_type] = []
            pattern_groups[pattern_type].append(line)
        
        return pattern_groups
    
    def validate_mixed_result(self, result: ParsedInputResult) -> ValidationResult:
        """Validate the overall parsed result"""
        validation = ValidationResult(is_valid=True)
        
        # Check if any entries were parsed
        if result.is_empty:
            validation.add_error("No valid entries found in input")
            return validation
        
        # Validate entry counts
        total_entries = result.total_entries
        if total_entries == 0:
            validation.add_error("No entries parsed successfully")
        elif total_entries > 1000:  # Reasonable limit
            validation.add_warning(f"Large number of entries: {total_entries}")
        
        # Validate individual entry types
        if result.pana_entries:
            self._validate_pana_entries(result.pana_entries, validation)
        
        if result.type_entries:
            self._validate_type_entries(result.type_entries, validation)
        
        if result.time_entries:
            self._validate_time_entries(result.time_entries, validation)
        
        if result.multi_entries:
            self._validate_multi_entries(result.multi_entries, validation)
        
        if result.direct_entries:
            self._validate_direct_entries(result.direct_entries, validation)
        
        return validation
    
    def _validate_pana_entries(self, entries, validation: ValidationResult):
        """Validate pana entries"""
        for entry in entries:
            if not (0 <= entry.number <= 999):  # Updated range to include 0
                validation.add_error(f"Invalid pana number: {entry.number}")
            if entry.value <= 0:
                validation.add_error(f"Invalid pana value: {entry.value}")
    
    def _validate_type_entries(self, entries, validation: ValidationResult):
        """Validate type entries"""
        for entry in entries:
            if entry.table_type not in ['SP', 'DP', 'CP']:
                validation.add_error(f"Invalid table type: {entry.table_type}")
            if entry.value <= 0:
                validation.add_error(f"Invalid type value: {entry.value}")
    
    def _validate_time_entries(self, entries, validation: ValidationResult):
        """Validate time entries"""
        for entry in entries:
            for col in entry.columns:
                if not (0 <= col <= 9):
                    validation.add_error(f"Invalid time column: {col}")
            if entry.value <= 0:
                validation.add_error(f"Invalid time value: {entry.value}")
    
    def _validate_multi_entries(self, entries, validation: ValidationResult):
        """Validate multiplication entries"""
        for entry in entries:
            if not (0 <= entry.number <= 99):
                validation.add_error(f"Invalid multiplication number: {entry.number}")
            if entry.value <= 0:
                validation.add_error(f"Invalid multiplication value: {entry.value}")
    
    def _validate_direct_entries(self, entries, validation: ValidationResult):
        """Validate direct number entries"""
        for entry in entries:
            if not (1 <= entry.number <= 999):
                validation.add_error(f"Invalid direct number: {entry.number}")
            if entry.value <= 0:
                validation.add_error(f"Invalid direct value: {entry.value}")
    
    def get_parsing_statistics(self, result: ParsedInputResult) -> Dict[str, Any]:
        """Get comprehensive statistics about parsed result"""
        return {
            'total_entries': result.total_entries,
            'entry_breakdown': {
                'pana_entries': len(result.pana_entries),
                'type_entries': len(result.type_entries),
                'time_entries': len(result.time_entries),
                'multi_entries': len(result.multi_entries),
                'direct_entries': len(result.direct_entries)
            },
            'is_mixed_input': result.total_entries > 0 and sum([
                len(result.pana_entries) > 0,
                len(result.type_entries) > 0,
                len(result.time_entries) > 0,
                len(result.multi_entries) > 0,
                len(result.direct_entries) > 0
            ]) > 1,
            'total_values': {
                'pana_total': sum(entry.value for entry in result.pana_entries),
                'type_total': sum(entry.value for entry in result.type_entries),
                'time_total': sum(entry.value for entry in result.time_entries),
                'multi_total': sum(entry.value for entry in result.multi_entries),
                'direct_total': sum(entry.value for entry in result.direct_entries)
            },
            'grand_total': (
                sum(entry.value for entry in result.pana_entries) +
                sum(entry.value for entry in result.type_entries) +
                sum(entry.value for entry in result.time_entries) +
                sum(entry.value for entry in result.multi_entries) +
                sum(entry.value for entry in result.direct_entries)
            )
        }
    
    def get_supported_combinations(self) -> List[Dict[str, str]]:
        """Get examples of supported mixed input combinations"""
        return [
            {
                'name': 'Pana + Type Tables',
                'example': '128/129/120 = 100\n1SP=50\n5DP=75',
                'description': 'Pana table entries mixed with type table entries'
            },
            {
                'name': 'Time + Multiplication',
                'example': '1=100\n38x700\n0 1 3 5 = 900',
                'description': 'Time table entries mixed with multiplication entries'
            },
            {
                'name': 'All Types Mixed',
                'example': '128/129 = 100\n1SP=50\n1=75\n38x700',
                'description': 'All four pattern types in single input'
            },
            {
                'name': 'Multi-line Same Type',
                'example': '128/129 = 100\n130/140 = 200\n150/160 = 300',
                'description': 'Multiple lines of same pattern type'
            },
            {
                'name': 'Complex Mixed',
                'example': '128/129/120 = 100\n1SP=50 2DP=75\n0 1 3 = 200\n38x700 83x500',
                'description': 'Complex combination with multiple entries per type'
            }
        ]


class MixedInputValidator:
    """Comprehensive validator for mixed input results"""
    
    def __init__(self, max_total_entries: int = 1000, max_total_value: int = 1000000):
        """
        Initialize mixed input validator
        
        Args:
            max_total_entries: Maximum total entries across all types
            max_total_value: Maximum total value across all types
        """
        self.max_total_entries = max_total_entries
        self.max_total_value = max_total_value
        self.logger = get_logger(__name__)
    
    def validate_result(self, result: ParsedInputResult) -> ValidationResult:
        """Comprehensive validation of mixed input result"""
        validation = ValidationResult(is_valid=True)
        
        # Check total entry count
        if result.total_entries > self.max_total_entries:
            validation.add_error(f"Too many entries: {result.total_entries} > {self.max_total_entries}")
        
        # Check total value
        total_value = self._calculate_total_value(result)
        if total_value > self.max_total_value:
            validation.add_error(f"Total value too large: {total_value} > {self.max_total_value}")
        
        # Check for reasonable distribution
        entry_types = [
            ('pana', len(result.pana_entries)),
            ('type', len(result.type_entries)),
            ('time', len(result.time_entries)),
            ('multi', len(result.multi_entries)),
            ('direct', len(result.direct_entries))
        ]
        
        # Warn if heavily skewed towards one type
        max_type_count = max(count for _, count in entry_types)
        if max_type_count > 0.8 * result.total_entries and result.total_entries > 10:
            validation.add_warning("Input heavily skewed towards one pattern type")
        
        return validation
    
    def _calculate_total_value(self, result: ParsedInputResult) -> int:
        """Calculate total value across all entry types"""
        return (
            sum(entry.value for entry in result.pana_entries) +
            sum(entry.value for entry in result.type_entries) +
            sum(entry.value for entry in result.time_entries) +
            sum(entry.value for entry in result.multi_entries) +
            sum(entry.value for entry in result.direct_entries)
        )
    
    def get_validation_report(self, result: ParsedInputResult) -> Dict[str, Any]:
        """Get detailed validation report"""
        total_value = self._calculate_total_value(result)
        
        return {
            'total_entries': result.total_entries,
            'max_entries_allowed': self.max_total_entries,
            'entries_within_limit': result.total_entries <= self.max_total_entries,
            'total_value': total_value,
            'max_value_allowed': self.max_total_value,
            'value_within_limit': total_value <= self.max_total_value,
            'pattern_distribution': {
                'pana_percentage': (len(result.pana_entries) / result.total_entries * 100) if result.total_entries > 0 else 0,
                'type_percentage': (len(result.type_entries) / result.total_entries * 100) if result.total_entries > 0 else 0,
                'time_percentage': (len(result.time_entries) / result.total_entries * 100) if result.total_entries > 0 else 0,
                'multi_percentage': (len(result.multi_entries) / result.total_entries * 100) if result.total_entries > 0 else 0,
                'direct_percentage': (len(result.direct_entries) / result.total_entries * 100) if result.total_entries > 0 else 0
            },
            'is_mixed_input': sum([
                len(result.pana_entries) > 0,
                len(result.type_entries) > 0,
                len(result.time_entries) > 0,
                len(result.multi_entries) > 0,
                len(result.direct_entries) > 0
            ]) > 1
        }