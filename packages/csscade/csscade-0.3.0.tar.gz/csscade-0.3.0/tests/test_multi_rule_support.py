#!/usr/bin/env python3
"""Comprehensive test for multi-rule support with apply_to parameter."""

from csscade import CSSMerger


def test_multi_rule_with_apply_to():
    """Test the new multi-rule support with various apply_to configurations."""
    
    # Test source with multiple rules including pseudo-selectors
    source_css = """
    .btn {
        background: blue;
        color: white;
        padding: 10px;
    }
    .btn:hover {
        background: darkblue;
        color: yellow;
    }
    .btn:active {
        background: navy;
    }
    """
    
    overrides = {"border": "2px solid red"}
    
    print("=" * 80)
    print("COMPREHENSIVE MULTI-RULE SUPPORT TEST")
    print("=" * 80)
    print("\nSource CSS:")
    print(source_css)
    print("\nOverride properties:", overrides)
    print("\n" + "=" * 80)
    
    # Test 1: Default behavior (backward compatibility)
    print("\n### TEST 1: Default Behavior (rule_selection='first') ###")
    print("-" * 50)
    merger = CSSMerger(mode='permanent')  # Default is rule_selection='first'
    result = merger.merge(source_css, overrides)
    print_result(result, "Should only process first rule (.btn)")
    
    # Test 2: Process all rules with apply_to='all' (default)
    print("\n### TEST 2: Process All Rules (rule_selection='all', apply_to='all') ###")
    print("-" * 50)
    merger = CSSMerger(mode='permanent', rule_selection='all')
    result = merger.merge(source_css, overrides)  # apply_to='all' is default
    print_result(result, "Should process all rules with overrides")
    
    # Test 3: Process all rules but apply only to base
    print("\n### TEST 3: Apply to Base Only (apply_to='base') ###")
    print("-" * 50)
    merger = CSSMerger(mode='permanent', rule_selection='all')
    result = merger.merge(source_css, overrides, apply_to='base')
    print_result(result, "Should only add border to .btn, not to :hover or :active")
    
    # Test 4: Apply only to hover state
    print("\n### TEST 4: Apply to Hover Only (apply_to=':hover') ###")
    print("-" * 50)
    merger = CSSMerger(mode='permanent', rule_selection='all')
    result = merger.merge(source_css, overrides, apply_to=':hover')
    print_result(result, "Should only add border to .btn:hover")
    
    # Test 5: Apply to multiple specific selectors
    print("\n### TEST 5: Apply to Multiple (apply_to=['base', ':hover']) ###")
    print("-" * 50)
    merger = CSSMerger(mode='permanent', rule_selection='all')
    result = merger.merge(source_css, overrides, apply_to=['base', ':hover'])
    print_result(result, "Should add border to .btn and .btn:hover, but not :active")
    
    # Test 6: Wildcard - all hover states
    print("\n### TEST 6: Wildcard for Hover States (apply_to='*:hover') ###")
    print("-" * 50)
    merger = CSSMerger(mode='permanent', rule_selection='all')
    result = merger.merge(source_css, overrides, apply_to='*:hover')
    print_result(result, "Should add border to any :hover state")
    
    # Test 7: Apply to specific full selector
    print("\n### TEST 7: Specific Selector (apply_to=['.btn:active']) ###")
    print("-" * 50)
    merger = CSSMerger(mode='permanent', rule_selection='all')
    result = merger.merge(source_css, overrides, apply_to=['.btn:active'])
    print_result(result, "Should only add border to .btn:active")
    
    # Test 8: States only
    print("\n### TEST 8: States Only (apply_to='states') ###")
    print("-" * 50)
    merger = CSSMerger(mode='permanent', rule_selection='all')
    result = merger.merge(source_css, overrides, apply_to='states')
    print_result(result, "Should add border to :hover and :active, but not base")
    
    print("\n" + "=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)


def print_result(result, description):
    """Helper to print test results in a readable format."""
    print(f"\n📋 {description}")
    print(f"\n🔍 Result structure:")
    print(f"   - CSS entries: {len(result.get('css', []))}")
    print(f"   - Warnings: {len(result.get('warnings', []))}")
    print(f"   - Info: {len(result.get('info', []))}")
    
    print(f"\n📝 CSS Output:")
    for i, css in enumerate(result.get('css', [])):
        print(f"   [{i}] {css.strip()}")
    
    if result.get('warnings'):
        print(f"\n⚠️  Warnings:")
        for warning in result['warnings']:
            print(f"   - {warning}")
    
    if result.get('info'):
        print(f"\nℹ️  Info:")
        for info in result['info']:
            print(f"   - {info}")
    
    # Verify the output
    css_list = result.get('css', [])
    css_combined = '\n'.join(css_list)
    
    print(f"\n✅ Verification:")
    print(f"   - Contains 'border: 2px solid red': {('border: 2px solid red' in css_combined)}")
    print(f"   - Number of rules with border: {css_combined.count('border: 2px solid red')}")
    print(f"   - CSS is list: {isinstance(result.get('css'), list)}")
    print(f"   - Warnings is list: {isinstance(result.get('warnings'), list)}")
    print(f"   - Info is list: {isinstance(result.get('info'), list)}")


if __name__ == "__main__":
    test_multi_rule_with_apply_to()