#!/usr/bin/env python3
"""Test shorthand property handling with the new multi-rule system."""

from csscade import CSSMerger
import pprint

def test_shorthand_with_multi_rules():
    """Test how shorthand properties work with multiple rules."""
    
    print("=" * 80)
    print("SHORTHAND PROPERTY HANDLING WITH MULTI-RULE SYSTEM")
    print("=" * 80)
    
    # Test 1: Shorthand in source, longhand in override
    print("\n### TEST 1: Source has shorthand, override has longhand ###")
    print("-" * 60)
    
    source_css = """
    .card {
        margin: 10px;
        padding: 20px;
        border: 1px solid black;
    }
    .card:hover {
        margin: 15px;
        border: 2px solid blue;
    }
    """
    
    overrides = {
        "margin-top": "30px",  # Longhand overriding shorthand
        "border-color": "red"   # Another longhand
    }
    
    print("Source CSS:")
    print(source_css)
    print("\nOverrides:", overrides)
    
    merger = CSSMerger(mode='permanent', rule_selection='all')
    result = merger.merge(source_css, overrides)
    
    print("\nResult with rule_selection='all':")
    for i, css in enumerate(result['css']):
        print(f"\nRule {i}:")
        print(css)
    
    if result.get('warnings'):
        print("\nWarnings:", result['warnings'])
    if result.get('info'):
        print("\nInfo:", result['info'])
    
    # Test 2: Shorthand in override, longhand in source
    print("\n\n### TEST 2: Source has longhands, override has shorthand ###")
    print("-" * 60)
    
    source_css = """
    .box {
        margin-top: 5px;
        margin-right: 10px;
        margin-bottom: 5px;
        margin-left: 10px;
    }
    .box:focus {
        margin-top: 10px;
        border-left: 3px solid green;
    }
    """
    
    overrides = {
        "margin": "20px",      # Shorthand overriding longhands
        "border": "2px solid black"  # Shorthand
    }
    
    print("Source CSS:")
    print(source_css)
    print("\nOverrides:", overrides)
    
    merger = CSSMerger(mode='permanent', rule_selection='all')
    result = merger.merge(source_css, overrides)
    
    print("\nResult:")
    for i, css in enumerate(result['css']):
        print(f"\nRule {i}:")
        print(css)
    
    # Test 3: Shorthand with apply_to parameter
    print("\n\n### TEST 3: Shorthand with apply_to parameter ###")
    print("-" * 60)
    
    source_css = """
    .btn {
        padding: 10px 20px;
        margin: 5px;
    }
    .btn:hover {
        padding: 12px 22px;
        margin: 7px;
    }
    """
    
    overrides = {
        "padding-left": "30px",  # Only override left padding
        "margin": "15px"         # Override all margins
    }
    
    print("Source CSS:")
    print(source_css)
    print("\nOverrides:", overrides)
    
    print("\n--- Apply to base only ---")
    merger = CSSMerger(mode='component', rule_selection='all')
    result = merger.merge(source_css, overrides, apply_to='base')
    
    for i, css in enumerate(result['css']):
        print(f"\nRule {i}:")
        print(css)
    
    print("\n--- Apply to :hover only ---")
    result = merger.merge(source_css, overrides, apply_to=':hover')
    
    for i, css in enumerate(result['css']):
        print(f"\nRule {i}:")
        print(css)
    
    # Test 4: Complex border shorthand
    print("\n\n### TEST 4: Complex border shorthand handling ###")
    print("-" * 60)
    
    source_css = """
    .widget {
        border-top: 1px solid red;
        border-right: 2px dashed blue;
        border-bottom: 1px solid red;
        border-left: 2px dashed blue;
    }
    .widget:active {
        border: 3px double green;
    }
    """
    
    overrides = {
        "border": "4px solid orange"  # Shorthand replacing all sides
    }
    
    print("Source CSS:")
    print(source_css)
    print("\nOverrides:", overrides)
    
    merger = CSSMerger(mode='replace', rule_selection='all')
    result = merger.merge(source_css, overrides, apply_to='all')
    
    print("\nResult with apply_to='all':")
    for i, css in enumerate(result['css']):
        print(f"\nRule {i}:")
        print(css)
    
    # Test 5: Check if longhands are properly overridden
    print("\n\n### TEST 5: Longhand override behavior ###")
    print("-" * 60)
    
    source_css = """
    .element {
        margin: 10px;
    }
    """
    
    # Override with specific longhand
    overrides = {"margin-top": "50px"}
    
    print("Source: margin: 10px")
    print("Override: margin-top: 50px")
    
    merger = CSSMerger(mode='permanent')
    result = merger.merge(source_css, overrides)
    
    print("\nResult:")
    print(result['css'][0])
    print("\nExpected: margin-top should be 50px, others should remain 10px")
    
    # Check the actual properties
    if "margin-top: 50px" in result['css'][0]:
        print("✅ margin-top correctly overridden")
    else:
        print("❌ margin-top NOT correctly overridden")
    
    if "margin: 10px" in result['css'][0] and "margin-top: 50px" not in result['css'][0]:
        print("❌ Shorthand not properly expanded")
    elif "margin-top: 50px" in result['css'][0]:
        print("✅ Shorthand properly handled")


def test_shorthand_expansion():
    """Test the shorthand expansion functionality."""
    
    print("\n\n" + "=" * 80)
    print("TESTING SHORTHAND EXPANSION")
    print("=" * 80)
    
    from csscade.handlers.shorthand import ShorthandResolver
    
    resolver = ShorthandResolver()
    
    # Test margin expansion
    print("\n### Margin Expansion ###")
    test_cases = [
        ("10px", "All sides 10px"),
        ("10px 20px", "Vertical 10px, Horizontal 20px"),
        ("10px 20px 30px", "Top 10px, Horizontal 20px, Bottom 30px"),
        ("10px 20px 30px 40px", "Top Right Bottom Left")
    ]
    
    for value, desc in test_cases:
        props = resolver.expand_shorthand("margin", value)
        print(f"\nmargin: {value} ({desc})")
        for prop in props:
            print(f"  {prop.name}: {prop.value}")
    
    # Test border expansion
    print("\n### Border Expansion ###")
    border_tests = [
        "1px solid black",
        "2px dashed red",
        "solid",
        "3px",
        "blue"
    ]
    
    for value in border_tests:
        props = resolver.expand_shorthand("border", value)
        print(f"\nborder: {value}")
        for prop in props:
            print(f"  {prop.name}: {prop.value}")


if __name__ == "__main__":
    test_shorthand_with_multi_rules()
    test_shorthand_expansion()
    
    print("\n" + "=" * 80)
    print("SHORTHAND HANDLING TEST COMPLETE")
    print("=" * 80)