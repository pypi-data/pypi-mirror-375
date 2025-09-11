#!/usr/bin/env python3
"""Test !important handling functionality."""

from csscade import CSSMerger
import pprint


def test_important_strategies():
    """Test different !important handling strategies."""
    
    print("=" * 80)
    print("!IMPORTANT HANDLING TEST")
    print("=" * 80)
    
    # Source with !important
    source_css = """
    .alert {
        color: red !important;
        background: yellow;
        padding: 10px;
    }
    """
    
    # Test 1: MATCH strategy (default)
    print("\n### TEST 1: MATCH Strategy (Default) ###")
    print("-" * 50)
    print("Source has 'color: red !important'")
    print("Override with 'color: blue' (no !important)")
    
    merger = CSSMerger(mode='permanent', rule_selection='all')  # Default is 'match'
    result = merger.merge(source_css, {"color": "blue", "margin": "5px"})
    
    print("\nResult:")
    pprint.pprint(result)
    print("\nExpected: color should be 'blue !important' (matched original)")
    
    # Test 2: RESPECT strategy
    print("\n### TEST 2: RESPECT Strategy ###")
    print("-" * 50)
    print("Should NOT override !important properties")
    
    merger = CSSMerger(
        mode='permanent',
        rule_selection='all',
        conflict_resolution={'important': 'respect'}
    )
    result = merger.merge(source_css, {"color": "blue", "background": "green"})
    
    print("\nResult:")
    pprint.pprint(result)
    print("\nExpected: color stays 'red !important', background changes to 'green'")
    
    # Test 3: OVERRIDE strategy
    print("\n### TEST 3: OVERRIDE Strategy ###")
    print("-" * 50)
    print("Override without adding !important")
    
    merger = CSSMerger(
        mode='permanent',
        rule_selection='all',
        conflict_resolution={'important': 'override'}
    )
    result = merger.merge(source_css, {"color": "blue", "background": "green"})
    
    print("\nResult:")
    pprint.pprint(result)
    print("\nExpected: color becomes 'blue' (no !important), with warning")
    
    # Test 4: FORCE strategy
    print("\n### TEST 4: FORCE Strategy ###")
    print("-" * 50)
    print("Add !important to ALL overrides")
    
    merger = CSSMerger(
        mode='permanent',
        rule_selection='all',
        conflict_resolution={'important': 'force'}
    )
    result = merger.merge(source_css, {"color": "blue", "margin": "5px"})
    
    print("\nResult:")
    pprint.pprint(result)
    print("\nExpected: Both color and margin should have !important")
    
    # Test 5: STRIP strategy
    print("\n### TEST 5: STRIP Strategy ###")
    print("-" * 50)
    print("Remove all !important declarations")
    
    merger = CSSMerger(
        mode='permanent',
        rule_selection='all',
        conflict_resolution={'important': 'strip'}
    )
    result = merger.merge(source_css, {"color": "blue"})
    
    print("\nResult:")
    pprint.pprint(result)
    print("\nExpected: color becomes 'blue' without !important")
    
    # Test 6: Explicit !important in override
    print("\n### TEST 6: Explicit !important in Override ###")
    print("-" * 50)
    print("Override value includes !important")
    
    merger = CSSMerger(mode='permanent', rule_selection='all')
    result = merger.merge(
        ".btn { color: green; }",
        {"color": "blue !important", "padding": "20px"}
    )
    
    print("\nResult:")
    pprint.pprint(result)
    print("\nExpected: color is 'blue !important', padding is '20px' (no !important)")
    
    # Test 7: Match with explicit !important override
    print("\n### TEST 7: Match Strategy with Explicit !important ###")
    print("-" * 50)
    print("Match strategy but override has explicit !important")
    
    merger = CSSMerger(mode='permanent', rule_selection='all')  # Default match
    result = merger.merge(
        ".btn { color: red; }",  # No !important in source
        {"color": "blue !important"}  # Explicit !important
    )
    
    print("\nResult:")
    pprint.pprint(result)
    print("\nExpected: color is 'blue !important' (explicit takes precedence)")


def test_component_mode_important():
    """Test !important handling in component mode."""
    
    print("\n" + "=" * 80)
    print("COMPONENT MODE WITH !IMPORTANT")
    print("=" * 80)
    
    source_css = """
    .warning {
        color: orange !important;
        border: 1px solid orange;
    }
    """
    
    print("\n### Component Mode with Match Strategy ###")
    print("-" * 50)
    
    merger = CSSMerger(
        mode='component',
        rule_selection='all',
        conflict_resolution={'important': 'match'}
    )
    
    result = merger.merge(source_css, {"color": "red", "border": "2px solid red"})
    
    print("\nResult:")
    pprint.pprint(result)
    print("\nExpected: Override class should have 'color: red !important' to match original")


def check_css_for_important(css_list):
    """Helper to check which properties have !important."""
    important_props = []
    for css in css_list:
        if '!important' in css:
            # Extract properties with !important
            lines = css.split(';')
            for line in lines:
                if '!important' in line:
                    prop = line.split(':')[0].split('{')[-1].strip()
                    important_props.append(prop)
    return important_props


if __name__ == "__main__":
    test_important_strategies()
    test_component_mode_important()
    
    print("\n" + "=" * 80)
    print("!IMPORTANT HANDLING TEST COMPLETE")
    print("=" * 80)