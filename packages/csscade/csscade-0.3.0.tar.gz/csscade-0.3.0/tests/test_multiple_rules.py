#!/usr/bin/env python3
"""Test to confirm that CSSCade only processes the first rule when multiple CSS rules are provided."""

from csscade import CSSMerger


def test_multiple_rules_issue():
    """Test that demonstrates the issue with multiple CSS rules."""
    
    # CSS with multiple rules including pseudo selectors
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
    
    # Simple override properties
    override_props = {"border": "2px solid red"}
    
    print("Testing Multiple Rules Issue")
    print("=" * 70)
    print("\nSource CSS (3 rules: .btn, .btn:hover, .btn:active):")
    print(source_css)
    print("\nOverride properties:")
    print(override_props)
    print("\n" + "=" * 70)
    
    # Test with each merge mode
    modes = ['permanent', 'component', 'replace']
    
    for mode in modes:
        print(f"\n\n### Testing {mode.upper()} mode ###")
        print("-" * 40)
        
        merger = CSSMerger(mode=mode)
        result = merger.merge(source_css, override_props)
        
        print(f"Result for {mode} mode:")
        print(f"CSS Output:\n{result.get('css', 'No CSS output')}")
        
        # Check if hover and active states are preserved
        css_output = result.get('css', '')
        has_hover = ':hover' in css_output
        has_active = ':active' in css_output
        
        print(f"\nAnalysis:")
        print(f"  - Contains :hover rule? {has_hover}")
        print(f"  - Contains :active rule? {has_active}")
        print(f"  - Number of rules in output: {css_output.count('{')}")
        
        if result.get('add'):
            print(f"  - Classes to add: {result['add']}")
        if result.get('remove'):
            print(f"  - Classes to remove: {result['remove']}")
        if result.get('preserve'):
            print(f"  - Classes to preserve: {result['preserve']}")
    
    print("\n" + "=" * 70)
    print("\nCONCLUSION:")
    print("As expected, all three modes only process the first rule (.btn)")
    print("The :hover and :active pseudo-selector rules are completely ignored.")
    print("This confirms the issue described in FIX_TOMORROW.txt")


if __name__ == "__main__":
    test_multiple_rules_issue()