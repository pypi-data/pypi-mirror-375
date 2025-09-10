#!/usr/bin/env python3
"""Debug border handling to find the issue."""

from csscade.property_merger import PropertyMerger
from csscade.parser.css_parser import CSSParser


def debug_border():
    """Debug the border handling issue."""
    
    print("DEBUG: Border Property Handling")
    print("=" * 60)
    
    parser = CSSParser()
    merger = PropertyMerger()
    
    # Parse source and override
    source = parser.parse_properties_string("border: 1px solid red;")
    override = parser.parse_properties_string("border-width: 3px;")
    
    print("\n1. Parsed source properties:")
    for prop in source:
        print(f"  {prop.name}: {prop.value}")
    
    print("\n2. Parsed override properties:")
    for prop in override:
        print(f"  {prop.name}: {prop.value}")
    
    # Test expansion
    print("\n3. Expanded source:")
    expanded_source = merger._expand_all_properties(source)
    for name, prop in expanded_source.items():
        print(f"  {name}: {prop.value}")
    
    print("\n4. Expanded override:")
    expanded_override = merger._expand_all_properties(override)
    for name, prop in expanded_override.items():
        print(f"  {name}: {prop.value}")
    
    # Test merge
    print("\n5. Merged longhands:")
    merged = merger._merge_longhands(expanded_source, expanded_override, 'match')
    for name, prop in merged.items():
        print(f"  {name}: {prop.value}")
    
    # Test optimization
    print("\n6. Optimized result:")
    result = merger._optimize_to_shorthands(merged)
    for prop in result:
        print(f"  {prop.name}: {prop.value}")
    
    # Full merge
    print("\n7. Full merge result:")
    final_result, info, warnings = merger.merge(source, override)
    for prop in final_result:
        print(f"  {prop.name}: {prop.value}")
    
    if info:
        print("\nInfo:", info)
    if warnings:
        print("\nWarnings:", warnings)


if __name__ == "__main__":
    debug_border()