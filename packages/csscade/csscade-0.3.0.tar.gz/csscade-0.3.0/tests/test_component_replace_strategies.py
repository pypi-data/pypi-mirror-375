#!/usr/bin/env python3
"""Test component and replace strategies with multi-rule support."""

from csscade import CSSMerger


def test_component_strategy():
    """Test component strategy with multi-rule support."""
    
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
    
    overrides = {"border": "2px solid red", "margin": "5px"}
    
    print("=" * 80)
    print("COMPONENT STRATEGY TEST")
    print("=" * 80)
    print("\nSource CSS:")
    print(source_css)
    print("\nOverride properties:", overrides)
    print("\n" + "=" * 80)
    
    # Test 1: Component mode with all rules, apply_to='all'
    print("\n### TEST 1: Component Mode - Apply to All ###")
    print("-" * 50)
    merger = CSSMerger(mode='component', rule_selection='all')
    result = merger.merge(source_css, overrides, apply_to='all')
    print_result(result, "Should create ONE override class with ALL states, all with overrides")
    
    # Test 2: Component mode with all rules, apply_to='base'
    print("\n### TEST 2: Component Mode - Apply to Base Only ###")
    print("-" * 50)
    merger = CSSMerger(mode='component', rule_selection='all')
    result = merger.merge(source_css, overrides, apply_to='base')
    print_result(result, "Should create ONE override class with ALL states, only base has overrides")
    
    # Test 3: Component mode with all rules, apply_to=[':hover']
    print("\n### TEST 3: Component Mode - Apply to Hover Only ###")
    print("-" * 50)
    merger = CSSMerger(mode='component', rule_selection='all')
    result = merger.merge(source_css, overrides, apply_to=[':hover'])
    print_result(result, "Should create ONE override class with ALL states, only hover has overrides")
    
    # Test 4: Component mode with no base rule
    print("\n### TEST 4: Component Mode - No Base Rule ###")
    print("-" * 50)
    source_no_base = """
    .btn:hover {
        background: darkblue;
        color: yellow;
    }
    .btn:active {
        background: navy;
    }
    """
    merger = CSSMerger(mode='component', rule_selection='all')
    result = merger.merge(source_no_base, overrides, apply_to='all')
    print_result(result, "Should create empty base class with warning, preserve pseudo states")


def test_replace_strategy():
    """Test replace strategy with multi-rule support."""
    
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
    
    overrides = {"border": "2px solid red", "margin": "5px"}
    
    print("\n" + "=" * 80)
    print("REPLACE STRATEGY TEST")
    print("=" * 80)
    print("\nSource CSS:")
    print(source_css)
    print("\nOverride properties:", overrides)
    print("\n" + "=" * 80)
    
    # Test 1: Replace mode with all rules, apply_to='all'
    print("\n### TEST 1: Replace Mode - Apply to All ###")
    print("-" * 50)
    merger = CSSMerger(mode='replace', rule_selection='all')
    result = merger.merge(source_css, overrides, apply_to='all')
    print_result(result, "Should create ONE replacement class with ALL states, all with overrides")
    
    # Test 2: Replace mode with all rules, apply_to='base'
    print("\n### TEST 2: Replace Mode - Apply to Base Only ###")
    print("-" * 50)
    merger = CSSMerger(mode='replace', rule_selection='all')
    result = merger.merge(source_css, overrides, apply_to='base')
    print_result(result, "Should create ONE replacement class with ALL states, only base has overrides")
    
    # Test 3: Replace mode with all rules, apply_to=['base', ':active']
    print("\n### TEST 3: Replace Mode - Apply to Base and Active ###")
    print("-" * 50)
    merger = CSSMerger(mode='replace', rule_selection='all')
    result = merger.merge(source_css, overrides, apply_to=['base', ':active'])
    print_result(result, "Should create ONE replacement class, base and active have overrides, hover doesn't")


def print_result(result, description):
    """Helper to print test results in a readable format."""
    print(f"\n📋 {description}")
    
    print(f"\n🔍 Result structure:")
    print(f"   - CSS entries: {len(result.get('css', []))}")
    print(f"   - Add: {result.get('add', [])}")
    print(f"   - Remove: {result.get('remove', [])}")
    print(f"   - Preserve: {result.get('preserve', [])}")
    print(f"   - Warnings: {len(result.get('warnings', []))}")
    print(f"   - Info: {len(result.get('info', []))}")
    
    print(f"\n📝 CSS Output:")
    for i, css in enumerate(result.get('css', [])):
        # Clean up for display
        css_clean = css.strip().replace('\n', '\n   ')
        print(f"   [{i}] {css_clean}")
    
    if result.get('warnings'):
        print(f"\n⚠️  Warnings:")
        for warning in result['warnings']:
            print(f"   - {warning}")
    
    # Verify key aspects
    css_list = result.get('css', [])
    css_combined = '\n'.join(css_list)
    
    print(f"\n✅ Verification:")
    print(f"   - Number of CSS rules: {len(css_list)}")
    print(f"   - Contains border override: {('border: 2px solid red' in css_combined)}")
    print(f"   - Contains margin override: {('margin: 5px' in css_combined)}")
    print(f"   - Pseudo states preserved: {(':hover' in css_combined and ':active' in css_combined)}")
    
    # Count unique class names
    class_names = set()
    for css in css_list:
        if '{' in css:
            selector = css.split('{')[0].strip()
            base_class = selector.split(':')[0] if ':' in selector else selector
            class_names.add(base_class)
    print(f"   - Unique class names generated: {len(class_names)} ({', '.join(class_names)})")


if __name__ == "__main__":
    test_component_strategy()
    test_replace_strategy()
    
    print("\n" + "=" * 80)
    print("ALL TESTS COMPLETE")
    print("=" * 80)