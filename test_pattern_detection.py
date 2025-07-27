#!/usr/bin/env python3
"""Test script to analyze pattern detection for the given input"""

import sys
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from src.parsing.pattern_detector import PatternDetector, PatternType

def test_pattern_detection():
    """Test the pattern detection with the given input"""
    
    # The input to test
    test_input = """138+347+230+349+269+

=RS,, 400


369+378+270+578+590+
128+380+129+670+580+
=150

239=150
456=150
279=150
170=150

668+677+488+299+

= RS,60

128=150
169=150
1=100
6=100"""
    
    print("🔍 TESTING PATTERN DETECTION")
    print("=" * 50)
    print("Input text:")
    print(test_input)
    print("\n" + "=" * 50)
    
    # Create pattern detector
    detector = PatternDetector()
    
    # Analyze the input
    overall_type, line_types, stats = detector.analyze_input(test_input)
    
    print(f"\n📊 ANALYSIS RESULTS")
    print(f"Overall Pattern Type: {overall_type.value}")
    print(f"Confidence: {stats['confidence']:.2%}")
    print(f"Total Lines: {stats['total_lines']}")
    print(f"Unknown Lines: {stats['unknown_lines']}")
    
    print(f"\n📋 PATTERN BREAKDOWN:")
    for pattern, count in stats['pattern_counts'].items():
        print(f"  {pattern.value}: {count} lines")
    
    print(f"\n🔎 LINE-BY-LINE ANALYSIS:")
    lines = [line.strip() for line in test_input.strip().split('\n') if line.strip()]
    
    for i, (line, pattern_type) in enumerate(zip(lines, line_types), 1):
        print(f"{i:2}. [{pattern_type.value:12}] {line}")
    
    # Test individual pattern detection
    print(f"\n🧪 INDIVIDUAL PATTERN TESTS:")
    test_lines = [
        "138+347+230+349+269+",
        "=RS,, 400", 
        "369+378+270+578+590+",
        "239=150",
        "1=100",
        "6=100"
    ]
    
    for line in test_lines:
        detected = detector.detect_pattern_type(line)
        print(f"  '{line}' → {detected.value}")
    
    # Test if it's detected as mixed
    print(f"\n✅ MIXED DETECTION TEST:")
    print(f"Is Mixed: {overall_type == PatternType.MIXED}")
    
    if overall_type == PatternType.MIXED:
        print("✅ SUCCESS: Input correctly detected as MIXED")
    else:
        print("❌ ISSUE: Input not detected as mixed")
        print(f"   Detected as: {overall_type.value}")
    
    return overall_type, line_types, stats

if __name__ == "__main__":
    test_pattern_detection()
