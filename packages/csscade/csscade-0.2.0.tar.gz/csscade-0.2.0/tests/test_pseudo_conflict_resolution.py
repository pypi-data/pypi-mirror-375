#!/usr/bin/env python3
"""Test pseudo conflict resolution - old vs new approach."""

from csscade import CSSMerger
import pprint


def test_pseudo_handling():
    """Test how pseudo selectors are handled with the new multi-rule system."""
    
    print("=" * 80)
    print("PSEUDO SELECTOR HANDLING - OLD vs NEW")
    print("=" * 80)
    
    source_css = """
    .btn {
        background: blue;
        color: white;
    }
    .btn:hover {
        background: darkblue;
        color: yellow;
    }
    """
    
    overrides = {"border": "2px solid red", "padding": "10px"}
    
    print("\nSource CSS:")
    print(source_css)
    print("\nOverrides:", overrides)
    
    # Test 1: OLD APPROACH - First rule only (would need conflict_resolution for pseudo)
    print("\n" + "=" * 80)
    print("OLD APPROACH (rule_selection='first' - default)")
    print("=" * 80)
    print("\nIn the old system, pseudo conflict resolution strategies would be:")
    print("- 'preserve': Keep pseudo selector as separate rule")
    print("- 'inline': Convert to inline styles for runtime")
    print("- 'ignore': Skip pseudo selectors entirely")
    print("- 'force_merge': Merge anyway (loses pseudo state)")
    print("- 'extract': Extract to separate object")
    
    merger = CSSMerger(
        mode='component',
        rule_selection='first',  # Old default
        conflict_resolution={'pseudo': 'preserve'}  # This doesn't do anything now!
    )
    result = merger.merge(source_css, overrides)
    
    print("\nResult with rule_selection='first':")
    print(f"CSS rules generated: {len(result['css'])}")
    print(f"Contains :hover? {':hover' in ''.join(result['css'])}")
    print("\n⚠️  Only first rule processed, :hover is lost!")
    
    # Test 2: NEW APPROACH - Multi-rule with apply_to
    print("\n" + "=" * 80)
    print("NEW APPROACH (rule_selection='all' + apply_to)")
    print("=" * 80)
    print("\nPseudo selectors are now handled through:")
    print("1. rule_selection='all' - Process all rules")
    print("2. apply_to parameter - Control where overrides apply")
    
    # Example 1: Process all, apply to all
    print("\n### Example 1: Apply overrides to all states ###")
    merger = CSSMerger(mode='component', rule_selection='all')
    result = merger.merge(source_css, overrides, apply_to='all')
    
    print(f"CSS rules generated: {len(result['css'])}")
    for i, css in enumerate(result['css']):
        has_border = 'border: 2px solid red' in css
        has_hover = ':hover' in css
        print(f"  Rule {i}: hover={has_hover}, has_border={has_border}")
    
    # Example 2: Apply only to base
    print("\n### Example 2: Apply overrides to base only ###")
    merger = CSSMerger(mode='component', rule_selection='all')
    result = merger.merge(source_css, overrides, apply_to='base')
    
    print(f"CSS rules generated: {len(result['css'])}")
    for i, css in enumerate(result['css']):
        has_border = 'border: 2px solid red' in css
        has_hover = ':hover' in css
        print(f"  Rule {i}: hover={has_hover}, has_border={has_border}")
    
    # Example 3: Apply only to hover
    print("\n### Example 3: Apply overrides to :hover only ###")
    merger = CSSMerger(mode='component', rule_selection='all')
    result = merger.merge(source_css, overrides, apply_to=':hover')
    
    print(f"CSS rules generated: {len(result['css'])}")
    for i, css in enumerate(result['css']):
        has_border = 'border: 2px solid red' in css
        has_hover = ':hover' in css
        print(f"  Rule {i}: hover={has_hover}, has_border={has_border}")
    
    print("\n" + "=" * 80)
    print("COMPARISON SUMMARY")
    print("=" * 80)
    print("\n🔴 OLD conflict_resolution['pseudo'] strategies:")
    print("   - Required complex configuration")
    print("   - Only worked with single rule at a time")
    print("   - Strategies like 'inline' and 'extract' were confusing")
    print("   - Lost pseudo states unless carefully configured")
    
    print("\n🟢 NEW multi-rule + apply_to approach:")
    print("   - Simple and intuitive")
    print("   - Preserves ALL pseudo states automatically")
    print("   - Fine-grained control with apply_to")
    print("   - Works consistently across all modes")
    
    print("\n💡 The pseudo conflict resolution is now OBSOLETE!")
    print("   The new system is more powerful and easier to use.")


def test_permanent_mode_pseudo():
    """Test permanent mode with pseudo selectors."""
    
    print("\n" + "=" * 80)
    print("PERMANENT MODE WITH PSEUDO SELECTORS")
    print("=" * 80)
    
    source_css = """
    .btn {
        background: blue;
    }
    .btn:hover {
        background: darkblue;
    }
    """
    
    merger = CSSMerger(mode='permanent', rule_selection='all')
    
    print("\n### Permanent mode - Apply to all ###")
    result = merger.merge(source_css, {"border": "1px solid black"}, apply_to='all')
    for css in result['css']:
        print(css.strip())
    
    print("\n### Permanent mode - Apply to :hover only ###")
    result = merger.merge(source_css, {"border": "1px solid black"}, apply_to=':hover')
    for css in result['css']:
        print(css.strip())


if __name__ == "__main__":
    test_pseudo_handling()
    test_permanent_mode_pseudo()
    
    print("\n" + "=" * 80)
    print("CONCLUSION: Pseudo conflict resolution is DEPRECATED")
    print("Use rule_selection='all' + apply_to parameter instead!")
    print("=" * 80)