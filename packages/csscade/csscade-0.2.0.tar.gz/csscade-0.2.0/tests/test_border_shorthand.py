#!/usr/bin/env python3
"""Test border shorthand handling with various value orders."""

from csscade import CSSMerger
import pprint


def test_border_variations():
    """Test border shorthand with different value orders and combinations."""
    
    print("=" * 80)
    print("BORDER SHORTHAND HANDLING - VARIOUS FORMATS")
    print("=" * 80)
    
    # Test 1: Different orders of border values
    print("\n### TEST 1: Different border value orders ###")
    print("-" * 60)
    
    test_cases = [
        ("border: 1px solid red;", "Standard order: width style color"),
        ("border: solid 1px red;", "Style first: style width color"),
        ("border: red 1px solid;", "Color first: color width style"),
        ("border: solid red 1px;", "Mixed order: style color width"),
        ("border: 1px red solid;", "Another mix: width color style"),
        ("border: red solid 1px;", "Another mix: color style width"),
    ]
    
    override = {"border-width": "3px"}
    
    for source_css, description in test_cases:
        print(f"\n{description}")
        print(f"Source: {source_css}")
        print(f"Override: border-width: 3px")
        
        merger = CSSMerger(mode='permanent')
        full_css = f".test {{ {source_css} }}"
        result = merger.merge(full_css, override)
        
        # Extract just the properties part
        css_output = result['css'][0]
        props_start = css_output.find('{') + 1
        props_end = css_output.find('}')
        props = css_output[props_start:props_end].strip()
        
        print(f"Result: {props}")
    
    # Test 2: Partial border values
    print("\n\n### TEST 2: Partial border values ###")
    print("-" * 60)
    
    partial_cases = [
        ("border: solid;", "Only style"),
        ("border: 2px;", "Only width"),
        ("border: blue;", "Only color"),
        ("border: 2px solid;", "Width and style"),
        ("border: solid blue;", "Style and color"),
        ("border: 2px blue;", "Width and color (ambiguous?)"),
    ]
    
    for source_css, description in partial_cases:
        print(f"\n{description}")
        print(f"Source: {source_css}")
        
        merger = CSSMerger(mode='permanent')
        full_css = f".test {{ {source_css} }}"
        override = {"padding": "10px"}  # Non-conflicting override
        result = merger.merge(full_css, override)
        
        # Extract properties
        css_output = result['css'][0]
        props_start = css_output.find('{') + 1
        props_end = css_output.find('}')
        props = css_output[props_start:props_end].strip()
        
        print(f"Expanded to: {props}")
    
    # Test 3: Complex border override scenarios
    print("\n\n### TEST 3: Complex border override scenarios ###")
    print("-" * 60)
    
    # Scenario A: Override border color when source has full border
    print("\nScenario A: Override color on full border")
    source_css = ".btn { border: solid 1px red; }"
    override = {"border-color": "blue"}
    
    print(f"Source: border: solid 1px red;")
    print(f"Override: border-color: blue")
    
    merger = CSSMerger(mode='permanent')
    result = merger.merge(source_css, override)
    print(f"Result: {result['css'][0]}")
    
    # Scenario B: Override full border when source has partials
    print("\nScenario B: Full border override on partial longhands")
    source_css = """
    .btn {
        border-width: 2px;
        border-style: dashed;
        border-color: green;
    }
    """
    override = {"border": "solid 3px blue"}
    
    print(f"Source: border-width: 2px; border-style: dashed; border-color: green;")
    print(f"Override: border: solid 3px blue")
    
    result = merger.merge(source_css, override)
    print(f"Result: {result['css'][0]}")
    
    # Scenario C: Individual side overrides
    print("\nScenario C: Override specific border side")
    source_css = ".card { border: 1px solid black; }"
    override = {"border-left": "3px solid red"}
    
    print(f"Source: border: 1px solid black;")
    print(f"Override: border-left: 3px solid red")
    
    result = merger.merge(source_css, override)
    print(f"Result: {result['css'][0]}")
    
    # Test 4: Check the actual expansion
    print("\n\n### TEST 4: Direct expansion test ###")
    print("-" * 60)
    
    from csscade.handlers.shorthand import ShorthandResolver
    
    resolver = ShorthandResolver()
    
    border_values = [
        "solid 1px red",
        "1px solid red",
        "red solid 1px",
        "solid",
        "2px",
        "blue",
        "2px dashed",
        "solid blue",
    ]
    
    for value in border_values:
        print(f"\nborder: {value}")
        props = resolver.expand_shorthand("border", value)
        for prop in props:
            print(f"  {prop.name}: {prop.value}")
    
    # Test 5: Multi-rule with border variations
    print("\n\n### TEST 5: Multi-rule with border variations ###")
    print("-" * 60)
    
    source_css = """
    .btn {
        border: solid 1px red;
    }
    .btn:hover {
        border: dashed 2px blue;
    }
    """
    
    override = {"border-width": "3px"}
    
    print("Source CSS:")
    print(source_css)
    print("\nOverride: border-width: 3px")
    
    merger = CSSMerger(mode='permanent', rule_selection='all')
    result = merger.merge(source_css, override, apply_to='all')
    
    print("\nResult with apply_to='all':")
    for i, css in enumerate(result['css']):
        print(f"\nRule {i}:")
        print(css)


if __name__ == "__main__":
    test_border_variations()
    
    print("\n" + "=" * 80)
    print("BORDER SHORTHAND TEST COMPLETE")
    print("=" * 80)