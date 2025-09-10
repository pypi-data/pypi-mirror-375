#!/usr/bin/env python3
"""Simplified verification that apply_to works correctly."""

from csscade import CSSMerger


def verify_apply_to(mode, apply_to, expected_description):
    """Verify apply_to behavior by checking where margin appears."""
    source_css = """
    .btn {
        background: blue;
    }
    .btn:hover {
        background: darkblue;
    }
    .btn:active {
        background: navy;
    }
    """
    
    overrides = {"margin": "5px"}
    
    merger = CSSMerger(mode=mode, rule_selection='all')
    result = merger.merge(source_css, overrides, apply_to=apply_to)
    
    # Check where margin appears in the CSS
    css_combined = '\n'.join(result.get('css', []))
    
    # Count margin in each type of rule
    base_has_margin = False
    hover_has_margin = False
    active_has_margin = False
    
    for css in result.get('css', []):
        if ':hover' not in css and ':active' not in css and 'margin: 5px' in css:
            base_has_margin = True
        if ':hover' in css and 'margin: 5px' in css:
            hover_has_margin = True
        if ':active' in css and 'margin: 5px' in css:
            active_has_margin = True
    
    return {
        'mode': mode,
        'apply_to': apply_to,
        'expected': expected_description,
        'base': base_has_margin,
        'hover': hover_has_margin,
        'active': active_has_margin,
        'total_margin_count': css_combined.count('margin: 5px')
    }


def main():
    print("APPLY_TO PARAMETER VERIFICATION")
    print("=" * 80)
    print("Checking where 'margin: 5px' appears based on apply_to parameter")
    print()
    
    test_cases = [
        # (apply_to, expected_description, expected_base, expected_hover, expected_active)
        ('all', "All rules should have margin", True, True, True),
        ('base', "Only base should have margin", True, False, False),
        ('states', "Only states should have margin", False, True, True),
        (['.btn'], "Only base .btn should have margin", True, False, False),
        (['.btn:hover'], "Only :hover should have margin", False, True, False),
        (['.btn:active'], "Only :active should have margin", False, False, True),
        (['.btn', '.btn:hover'], "Base and :hover should have margin", True, True, False),
        ([':hover'], "Only :hover should have margin", False, True, False),
        ([':active'], "Only :active should have margin", False, False, True),
        (['*'], "All should have margin", True, True, True),
        (['.*'], "Only base should have margin", True, False, False),
        (['*:hover'], "Only :hover should have margin", False, True, False),
        (['*:active'], "Only :active should have margin", False, False, True),
        (['base', ':active'], "Base and :active should have margin", True, False, True),
    ]
    
    all_pass = True
    
    for mode in ['permanent', 'component', 'replace']:
        print(f"\n{mode.upper()} MODE:")
        print("-" * 40)
        
        for apply_to, expected_desc, exp_base, exp_hover, exp_active in test_cases:
            result = verify_apply_to(mode, apply_to, expected_desc)
            
            # Check if results match expectations
            pass_test = (
                result['base'] == exp_base and
                result['hover'] == exp_hover and
                result['active'] == exp_active
            )
            
            status = "✅" if pass_test else "❌"
            
            if not pass_test:
                all_pass = False
                print(f"{status} apply_to={str(apply_to):<20} Expected: base={exp_base}, hover={exp_hover}, active={exp_active}")
                print(f"   Got: base={result['base']}, hover={result['hover']}, active={result['active']}")
            else:
                # Show succinct success message
                margin_locations = []
                if result['base']: margin_locations.append('base')
                if result['hover']: margin_locations.append('hover')
                if result['active']: margin_locations.append('active')
                location_str = ', '.join(margin_locations) if margin_locations else 'none'
                print(f"{status} apply_to={str(apply_to):<20} → margin in: {location_str}")
    
    print("\n" + "=" * 80)
    if all_pass:
        print("🎉 ALL TESTS PASSED! The apply_to parameter works correctly across all modes.")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
    print("=" * 80)


if __name__ == "__main__":
    main()