#!/usr/bin/env python3
"""
Fix for PANA parsing to handle complex multi-line PANA entries
"""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_improved_pana_parsing():
    """Test the improved PANA parsing logic"""
    
    print("🔧 TESTING IMPROVED PANA PARSING")
    print("=" * 60)
    
    # Test input from GUI that failed
    test_pana_input = """138+347+230+349+269+
=RS,, 400


369+378+270+578+590+
128+380+129+670+580+
=150

668+677+488+299+

= RS,60"""

    print("📝 TEST INPUT:")
    print("-" * 30)
    for i, line in enumerate(test_pana_input.split('\n'), 1):
        if line.strip():
            print(f"{i:2d}. '{line}'")
        else:
            print(f"{i:2d}. (empty line)")
    
    # Analyze the parsing requirements
    print("\n🔍 PARSING REQUIREMENTS:")
    print("-" * 30)
    print("1. Handle multi-line PANA format:")
    print("   - Number combinations: 138+347+230+349+269+")
    print("   - Result assignments: =RS,, 400")
    print("   - Empty lines between groups")
    
    print("\n2. Parse result formats:")
    print("   - =RS,, 400 → value = 400")
    print("   - =150 → value = 150") 
    print("   - = RS,60 → value = 60")
    
    print("\n3. Expected results:")
    print("   Group 1: 5 numbers × ₹400 = ₹2,000")
    print("   Group 2: 10 numbers × ₹150 = ₹1,500")
    print("   Group 3: 4 numbers × ₹60 = ₹240")
    print("   Total PANA: ₹3,740")
    
    # Test current parsing
    try:
        from src.parsing.pana_parser import PanaTableParser
        from src.parsing.pana_parser import PanaValidator
        from src.database.db_manager import create_database_manager
        
        print("\n🧪 CURRENT PARSING TEST:")
        print("-" * 30)
        
        # Create validator
        db_manager = create_database_manager()
        
        # Load pana numbers for validation
        try:
            query = "SELECT number FROM pana_numbers"
            results = db_manager.execute_query(query)
            pana_numbers = {row['number'] for row in results}
            print(f"✅ Loaded {len(pana_numbers)} pana reference numbers")
        except:
            pana_numbers = set()
            print("⚠️ Using empty pana reference set")
        
        validator = PanaValidator(pana_numbers)
        parser = PanaTableParser(validator)
        
        # Try current parsing
        try:
            entries = parser.parse(test_pana_input)
            print(f"✅ Current parser result: {len(entries)} entries")
            
            total_value = sum(entry.value for entry in entries)
            print(f"💰 Current total: ₹{total_value:,}")
            
            # Show entries
            for entry in entries[:10]:  # Show first 10
                print(f"   {entry.number} = ₹{entry.value}")
            if len(entries) > 10:
                print(f"   ... and {len(entries) - 10} more")
                
        except Exception as e:
            print(f"❌ Current parser failed: {e}")
            
    except Exception as e:
        print(f"❌ Setup failed: {e}")

def analyze_pana_parsing_issues():
    """Analyze specific issues with PANA parsing"""
    
    print("\n\n🔍 ANALYZING PANA PARSING ISSUES")
    print("=" * 60)
    
    print("📋 IDENTIFIED ISSUES:")
    print("-" * 30)
    
    print("1. PATTERN DETECTION:")
    print("   - Complex PANA patterns not properly recognized")
    print("   - Result lines (=RS,, 400) not handled correctly")
    print("   - Multi-line grouping fails")
    
    print("\n2. PARSING LOGIC:")
    print("   - Number extraction from 138+347+230+349+269+ format")
    print("   - Value extraction from =RS,, 400 format")
    print("   - Grouping multi-line entries correctly")
    
    print("\n3. VALIDATION:")
    print("   - Number validation against pana_numbers table")
    print("   - Complex currency format handling")
    
    print("\n💡 PROPOSED FIXES:")
    print("-" * 30)
    
    print("1. IMPROVE PATTERN DETECTION:")
    print("   - Better regex for complex PANA patterns")
    print("   - Handle =RS,, and = RS, formats")
    print("   - Recognize number combination lines")
    
    print("2. ENHANCE PARSING LOGIC:")
    print("   - Better multi-line grouping")
    print("   - Robust number extraction")
    print("   - Improved value parsing")
    
    print("3. FALLBACK HANDLING:")
    print("   - Continue parsing other patterns if PANA fails")
    print("   - Better error reporting")
    print("   - Graceful degradation")

def create_improved_pana_fixes():
    """Create improved PANA parsing fixes"""
    
    print("\n\n🔧 PROPOSED PANA PARSING IMPROVEMENTS")
    print("=" * 60)
    
    print("📝 IMPROVED PATTERN DETECTION:")
    print("-" * 40)
    
    improved_pana_pattern = r'''
    # Improved PANA pattern detection
    PANA_PATTERNS = [
        r'^\d{3}[+\/\*\,\s]+(\d{3}[+\/\*\,\s]+)*\d{3}[+\/\*\,\s]*$',  # Number combinations
        r'^\s*=\s*(RS?\.{0,3}\s*[\,\.\s]*)*\d+\s*$',                    # Result assignments
        r'^\d{3}\s*=\s*\d+$',                                          # Direct PANA assignments
        r'^\d{3}[+\/\*\,\s]+.*$',                                      # PANA number lines
    ]
    '''
    
    print(improved_pana_pattern)
    
    print("\n📝 IMPROVED VALUE EXTRACTION:")
    print("-" * 40)
    
    improved_value_extraction = '''
    def extract_value_robust(self, value_text: str) -> int:
        """Robust value extraction handling complex formats"""
        # Remove various currency indicators
        patterns = [
            r'RS\.{0,3}\s*[\,\.\s]*',   # RS..., RS. ., RS, etc.
            r'R\s*[\,\.\s]*',           # R with optional spacing/punctuation
            r'₹\s*',                     # Rupee symbol
        ]
        
        cleaned = value_text.strip()
        for pattern in patterns:
            cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE)
        
        # Extract numeric value
        numbers = re.findall(r'\d+', cleaned)
        if numbers:
            return int(numbers[0])
        
        raise ValueError(f"No numeric value found in: {value_text}")
    '''
    
    print(improved_value_extraction)
    
    print("\n📝 IMPROVED GROUPING LOGIC:")
    print("-" * 40)
    
    improved_grouping = '''
    def group_pana_entries_robust(self, lines: List[str]) -> List[List[str]]:
        """Robust grouping for multi-line PANA entries"""
        groups = []
        current_group = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue  # Skip empty lines
                
            if line.startswith('='):
                # Result line - completes current group
                if current_group:
                    current_group.append(line)
                    groups.append(current_group)
                    current_group = []
                else:
                    # Standalone result line
                    groups.append([line])
            else:
                # Number line - add to current group
                current_group.append(line)
        
        # Handle any remaining group
        if current_group:
            groups.append(current_group)
            
        return groups
    '''
    
    print(improved_grouping)

if __name__ == "__main__":
    test_improved_pana_parsing()
    analyze_pana_parsing_issues()
    create_improved_pana_fixes()
