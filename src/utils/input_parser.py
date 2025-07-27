"""Smart input parser for RickyMama - detects format and extracts data"""

import re
from typing import List, Dict, Any, Tuple
from enum import Enum

class InputType(Enum):
    PANA = "PANA"
    TYPE = "TYPE" 
    TIME_DIRECT = "TIME_DIRECT"
    TIME_MULTI = "TIME_MULTI"
    UNKNOWN = "UNKNOWN"

class InputParser:
    """Smart parser that detects input format and extracts structured data"""
    
    def __init__(self):
        # PANA format patterns
        self.pana_patterns = [
            r'(\d+)[/,\s+*]+(\d+)[/,\s+*]+(\d+)\s*=\s*(\d+)',  # 128/129/120 = 100
            r'(\d+)[,\s]+(\d+)[,\s]+(\d+)\s*=\s*(\d+)',        # 128,129,120 = 100
            r'(\d+)\s+(\d+)\s+(\d+)\s*=\s*(\d+)',              # 128 129 120 = 100
            r'(\d+),(\d+)=(\d+)'                               # 239,347=260
        ]
        
        # Type format pattern
        self.type_pattern = r'(\d+)(SP|DP|CP)\s*=\s*(\d+)'     # 1SP=100
        
        # Time direct patterns
        self.time_direct_patterns = [
            r'^(\d+)\s*=\s*(\d+)$',                            # 1=100
            r'^([\d\s]+)\s*=\s*(\d+)$'                         # 0 1 3 5 = 900
        ]
        
        # Time multiply pattern
        self.time_multiply_pattern = r'(\d+)x(\d+)'            # 38x700
    
    def parse_input(self, input_text: str) -> List[Dict[str, Any]]:
        """Parse input and return structured data entries"""
        entries = []
        
        # Split into lines and process each
        lines = [line.strip() for line in input_text.split('\n') if line.strip()]
        
        # Handle multi-line PANA format
        accumulated_numbers = []
        pending_value = None
        
        for line in lines:
            # Check for value assignment at end
            if '=' in line and not any(pattern in line for pattern in ['SP=', 'DP=', 'CP=', 'x']):
                if accumulated_numbers:
                    # This is the value for accumulated numbers
                    value_match = re.search(r'=\s*(\d+)', line)
                    if value_match:
                        value = int(value_match.group(1))
                        # Create entries for all accumulated numbers
                        for number in accumulated_numbers:
                            entries.append({
                                'type': InputType.PANA,
                                'number': number,
                                'value': value,
                                'entry_type': 'PANA'
                            })
                        accumulated_numbers = []
                        continue
                
                # Regular PANA format with = in same line
                pana_entry = self._parse_pana_line(line)
                if pana_entry:
                    entries.extend(pana_entry)
                    continue
            
            # Check for number accumulation (lines without =)
            if not '=' in line and not 'x' in line:
                numbers = self._extract_numbers_from_line(line)
                accumulated_numbers.extend(numbers)
                continue
            
            # Parse other formats
            entry = self._parse_single_line(line)
            if entry:
                entries.extend(entry)
        
        return entries
    
    def _parse_pana_line(self, line: str) -> List[Dict[str, Any]]:
        """Parse a PANA format line"""
        entries = []
        
        for i, pattern in enumerate(self.pana_patterns):
            match = re.search(pattern, line)
            if match:
                if i == 3:  # 2-number format: 239,347=260
                    numbers = [int(match.group(1)), int(match.group(2))]
                    value = int(match.group(3))
                else:  # 3-number format
                    numbers = [int(match.group(1)), int(match.group(2)), int(match.group(3))]
                    value = int(match.group(4))
                
                for number in numbers:
                    entries.append({
                        'type': InputType.PANA,
                        'number': number,
                        'value': value,
                        'entry_type': 'PANA'
                    })
                return entries
        
        return entries
    
    def _parse_single_line(self, line: str) -> List[Dict[str, Any]]:
        """Parse a single line for non-PANA formats"""
        entries = []
        
        # Type format
        type_match = re.search(self.type_pattern, line)
        if type_match:
            column = int(type_match.group(1))
            table_type = type_match.group(2)
            value = int(type_match.group(3))
            
            entries.append({
                'type': InputType.TYPE,
                'column': column,
                'table_type': table_type,
                'value': value,
                'entry_type': 'TYPE'
            })
            return entries
        
        # Time multiply format
        multiply_match = re.search(self.time_multiply_pattern, line)
        if multiply_match:
            number = multiply_match.group(1)
            value = int(multiply_match.group(2))
            
            # Extract tens and units digits
            tens_digit = int(number[0]) if len(number) >= 2 else 0
            units_digit = int(number[-1])
            
            entries.append({
                'type': InputType.TIME_MULTI,
                'tens_digit': tens_digit,
                'units_digit': units_digit,
                'value': value,
                'entry_type': 'TIME_MULTI'
            })
            return entries
        
        # Time direct format
        for pattern in self.time_direct_patterns:
            match = re.search(pattern, line)
            if match:
                columns_str = match.group(1)
                value = int(match.group(2))
                
                # Parse columns
                if ' ' in columns_str:
                    columns = [int(x) for x in columns_str.split() if x.isdigit()]
                else:
                    columns = [int(columns_str)]
                
                for column in columns:
                    entries.append({
                        'type': InputType.TIME_DIRECT,
                        'column': column,
                        'value': value,
                        'entry_type': 'TIME_DIRECT'
                    })
                return entries
        
        return entries
    
    def _extract_numbers_from_line(self, line: str) -> List[int]:
        """Extract numbers from a line (for multi-line PANA format)"""
        numbers = []
        
        # Remove common separators and extract numbers
        cleaned = re.sub(r'[,/+*\s]+', ' ', line)
        for match in re.finditer(r'\d+', cleaned):
            number = int(match.group())
            if 100 <= number <= 999:  # Valid pana numbers
                numbers.append(number)
        
        return numbers
    
    def calculate_total(self, entries: List[Dict[str, Any]]) -> int:
        """Calculate total value for all entries"""
        total = 0
        
        for entry in entries:
            if entry['type'] == InputType.PANA:
                total += entry['value']
            elif entry['type'] == InputType.TYPE:
                # For type tables, value applies to all numbers in that column
                # This would need actual type table data to calculate correctly
                total += entry['value']
            elif entry['type'] in [InputType.TIME_DIRECT, InputType.TIME_MULTI]:
                total += entry['value']
        
        return total
    
    def get_preview_text(self, entries: List[Dict[str, Any]]) -> str:
        """Generate preview text for the entries"""
        if not entries:
            return "No valid entries detected"
        
        preview_lines = []
        total = 0
        
        entry_counts = {}
        for entry in entries:
            entry_type = entry['type']
            if entry_type not in entry_counts:
                entry_counts[entry_type] = 0
            entry_counts[entry_type] += 1
            total += entry.get('value', 0)
        
        # Summary by type
        for entry_type, count in entry_counts.items():
            preview_lines.append(f"{entry_type.value}: {count} entries")
        
        preview_lines.append(f"Total Value: {total}")
        
        # Show first few entries as examples
        preview_lines.append("\nSample entries:")
        for i, entry in enumerate(entries[:3]):
            if entry['type'] == InputType.PANA:
                preview_lines.append(f"  {entry['number']} = {entry['value']}")
            elif entry['type'] == InputType.TYPE:
                preview_lines.append(f"  {entry['column']}{entry['table_type']} = {entry['value']}")
            elif entry['type'] == InputType.TIME_DIRECT:
                preview_lines.append(f"  Column {entry['column']} = {entry['value']}")
            elif entry['type'] == InputType.TIME_MULTI:
                preview_lines.append(f"  {entry['tens_digit']}{entry['units_digit']}x{entry['value']}")
        
        if len(entries) > 3:
            preview_lines.append(f"  ... and {len(entries) - 3} more")
        
        return "\n".join(preview_lines)


def create_input_parser() -> InputParser:
    """Factory function to create input parser"""
    return InputParser()


# Test the parser
if __name__ == "__main__":
    parser = create_input_parser()
    
    test_inputs = [
        "128/129/120 = 100",
        "1SP=100",
        "1=100",
        "38x700",
        """128,129,120
128,129,120
128,129,120 = 100"""
    ]
    
    for test_input in test_inputs:
        print(f"\nInput: {test_input}")
        entries = parser.parse_input(test_input)
        print(f"Entries: {len(entries)}")
        print(f"Preview: {parser.get_preview_text(entries)}")
        print("-" * 40)