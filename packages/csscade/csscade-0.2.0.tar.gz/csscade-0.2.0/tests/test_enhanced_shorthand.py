#!/usr/bin/env python3
"""Test the enhanced property merger with intelligent shorthand handling."""

from csscade.property_merger_enhanced import EnhancedPropertyMerger
from csscade.models import CSSProperty
from csscade.parser.css_parser import CSSParser


def test_enhanced_merger():
    """Test the enhanced property merger."""
    
    print("=" * 80)
    print("TESTING ENHANCED PROPERTY MERGER")
    print("=" * 80)
    
    parser = CSSParser()
    merger = EnhancedPropertyMerger()
    
    # Test 1: Longhand override on shorthand (should preserve other sides)
    print("\n### TEST 1: Preserve other sides when overriding one ###")
    print("-" * 60)
    
    source = parser.parse_properties_string("margin: 10px; color: blue;")
    override = parser.parse_properties_string("margin-top: 30px; color: red;")
    
    print("Source: margin: 10px; color: blue;")
    print("Override: margin-top: 30px; color: red;")
    
    result, info, warnings = merger.merge(source, override)
    
    print("\nResult:")
    for prop in result:
        important_str = " !important" if hasattr(prop, 'important') and prop.important else ""
        print(f"  {prop.name}: {prop.value}{important_str};")
    
    print("\nExpected: margin: 30px 10px 10px 10px; (or individual longhands)")
    
    # Test 2: Shorthand override on longhands (should replace all)
    print("\n\n### TEST 2: Shorthand should replace all longhands ###")
    print("-" * 60)
    
    source = parser.parse_properties_string("""
        margin-top: 5px;
        margin-right: 10px;
        margin-bottom: 15px;
        margin-left: 20px;
    """)
    override = parser.parse_properties_string("margin: 25px;")
    
    print("Source: margin-top: 5px; margin-right: 10px; margin-bottom: 15px; margin-left: 20px;")
    print("Override: margin: 25px;")
    
    result, info, warnings = merger.merge(source, override)
    
    print("\nResult:")
    for prop in result:
        print(f"  {prop.name}: {prop.value};")
    
    print("\nExpected: margin: 25px; (all sides now 25px)")
    
    # Test 3: Partial longhand override
    print("\n\n### TEST 3: Override specific longhands ###")
    print("-" * 60)
    
    source = parser.parse_properties_string("padding: 10px 20px;")
    override = parser.parse_properties_string("padding-left: 30px; padding-top: 5px;")
    
    print("Source: padding: 10px 20px;")
    print("Override: padding-left: 30px; padding-top: 5px;")
    
    result, info, warnings = merger.merge(source, override)
    
    print("\nResult:")
    for prop in result:
        print(f"  {prop.name}: {prop.value};")
    
    print("\nExpected: padding: 5px 20px 10px 30px; (or individual longhands)")
    
    # Test 4: Border shorthand complexity
    print("\n\n### TEST 4: Complex border handling ###")
    print("-" * 60)
    
    source = parser.parse_properties_string("border: 1px solid black;")
    override = parser.parse_properties_string("border-color: red; border-width: 2px;")
    
    print("Source: border: 1px solid black;")
    print("Override: border-color: red; border-width: 2px;")
    
    result, info, warnings = merger.merge(source, override)
    
    print("\nResult:")
    for prop in result:
        print(f"  {prop.name}: {prop.value};")
    
    print("\nExpected: border-width: 2px; border-style: solid; border-color: red;")
    
    # Test 5: Mixed !important handling
    print("\n\n### TEST 5: !important with shorthands ###")
    print("-" * 60)
    
    source = parser.parse_properties_string("margin: 10px !important;")
    override = parser.parse_properties_string("margin-top: 30px;")
    
    print("Source: margin: 10px !important;")
    print("Override: margin-top: 30px;")
    
    merger_respect = EnhancedPropertyMerger(important_strategy='respect')
    result, info, warnings = merger_respect.merge(source, override)
    
    print("\nResult (respect mode):")
    for prop in result:
        important_str = " !important" if hasattr(prop, 'important') and prop.important else ""
        print(f"  {prop.name}: {prop.value}{important_str};")
    
    print("\nExpected: margin: 10px !important; (not overridden due to !important)")
    
    # Test with match mode
    merger_match = EnhancedPropertyMerger(important_strategy='match')
    result, info, warnings = merger_match.merge(source, override)
    
    print("\nResult (match mode):")
    for prop in result:
        important_str = " !important" if hasattr(prop, 'important') and prop.important else ""
        print(f"  {prop.name}: {prop.value}{important_str};")
    
    print("\nExpected: margin-top: 30px !important; others: 10px !important;")
    
    # Test 6: Check if optimization works
    print("\n\n### TEST 6: Optimization to shorthand ###")
    print("-" * 60)
    
    source = parser.parse_properties_string("""
        padding-top: 10px;
        padding-right: 10px;
        padding-bottom: 10px;
        padding-left: 10px;
    """)
    override = parser.parse_properties_string("")  # No override
    
    print("Source: padding-top/right/bottom/left: all 10px;")
    print("Override: (none)")
    
    result, info, warnings = merger.merge(source, override)
    
    print("\nResult:")
    for prop in result:
        print(f"  {prop.name}: {prop.value};")
    
    print("\nExpected: padding: 10px; (optimized to shorthand)")
    
    if info:
        print("\nInfo messages:", info)


if __name__ == "__main__":
    test_enhanced_merger()