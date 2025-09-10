#!/usr/bin/env python3
"""Test and demonstrate different shorthand strategies."""

from csscade import CSSMerger
import pprint


def test_shorthand_strategies():
    """Test different shorthand handling strategies."""
    
    print("=" * 80)
    print("SHORTHAND HANDLING STRATEGIES DEMONSTRATION")
    print("=" * 80)
    
    # Test data
    source_css = """
    .card {
        margin: 10px;
        padding: 20px;
        border: 1px solid red;
        background: linear-gradient(to right, blue, green);
    }
    """
    
    overrides = {
        "margin-top": "30px",      # Partial margin override
        "padding": "15px 25px",    # Full padding override
        "border-width": "3px",     # Partial border override
        "background-color": "yellow"  # Partial background override
    }
    
    print("Source CSS:")
    print(source_css)
    print("\nOverrides:")
    for k, v in overrides.items():
        print(f"  {k}: {v}")
    
    # Test 1: CASCADE mode (default)
    print("\n" + "=" * 80)
    print("STRATEGY 1: CASCADE MODE (Default - Simple & Fast)")
    print("=" * 80)
    print("Properties are simply added, CSS cascade handles conflicts")
    
    merger = CSSMerger(
        mode='permanent',
        shorthand_strategy='cascade'  # Default
    )
    result = merger.merge(source_css, overrides)
    
    print("\nResult:")
    print(result['css'][0])
    print("\n✅ Simple and predictable - just like standard CSS!")
    print("   border stays as 'border: 1px solid red' + 'border-width: 3px'")
    print("   CSS cascade will apply border-width: 3px")
    
    # Test 2: SMART mode
    print("\n" + "=" * 80)
    print("STRATEGY 2: SMART MODE (Intelligent for simple properties)")
    print("=" * 80)
    print("Margin/padding expanded & merged, complex properties cascade")
    
    merger = CSSMerger(
        mode='permanent',
        shorthand_strategy='smart'
    )
    result = merger.merge(source_css, overrides)
    
    print("\nResult:")
    print(result['css'][0])
    print("\n✅ Best of both worlds!")
    print("   margin intelligently merged: margin: 30px 10px 10px")
    print("   border stays simple: border + border-width (cascade)")
    
    # Test 3: EXPAND mode
    print("\n" + "=" * 80)
    print("STRATEGY 3: EXPAND MODE (Full intelligent merging)")
    print("=" * 80)
    print("All shorthands expanded and intelligently merged")
    
    merger = CSSMerger(
        mode='permanent',
        shorthand_strategy='expand'
    )
    result = merger.merge(source_css, overrides)
    
    print("\nResult:")
    print(result['css'][0])
    print("\n⚠️  Most thorough but creates many properties")
    print("   Everything expanded and merged at longhand level")
    
    # Test 4: Real-world example with cascade
    print("\n" + "=" * 80)
    print("REAL-WORLD EXAMPLE: Why CASCADE is often best")
    print("=" * 80)
    
    source_css = """
    .btn {
        border: 1px solid #ccc;
        transition: all 0.3s ease;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .btn:hover {
        border-color: #007bff;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    """
    
    overrides = {
        "border-style": "dashed",
        "transition-duration": "0.5s"
    }
    
    print("Complex real-world CSS with hover states:")
    print(source_css)
    print("\nOverrides:", overrides)
    
    merger = CSSMerger(
        mode='component',
        rule_selection='all',
        shorthand_strategy='cascade'
    )
    result = merger.merge(source_css, overrides, apply_to='all')
    
    print("\nResult with CASCADE strategy:")
    for i, css in enumerate(result['css']):
        print(f"\nRule {i}:")
        print(css)
    
    print("\n✅ Clean and simple - exactly what you'd expect from CSS!")
    
    # Test 5: When to use each strategy
    print("\n" + "=" * 80)
    print("RECOMMENDATION SUMMARY")
    print("=" * 80)
    
    print("""
📌 Use CASCADE (default) when:
   - You want standard CSS behavior
   - Working with complex properties (border, background, animation)
   - Performance is important
   - Output size matters

📌 Use SMART when:
   - You need intelligent margin/padding merging
   - But want to keep complex properties simple
   - Good balance of features and simplicity

📌 Use EXPAND when:
   - You need complete control over every longhand
   - Working with property analysis tools
   - Don't mind larger output size
   - Need to ensure specific longhands are set
    """)


if __name__ == "__main__":
    test_shorthand_strategies()
    
    print("\n" + "=" * 80)
    print("DEMONSTRATION COMPLETE")
    print("=" * 80)