#!/usr/bin/env python3
"""Test and demonstrate conflict resolution strategies."""

from csscade import CSSMerger


def print_header(text):
    """Print a formatted header."""
    print(f"\n{'=' * 60}")
    print(f"  {text}")
    print('=' * 60)


def print_result(result):
    """Print merge result in a readable format."""
    if 'css' in result:
        print(f"CSS Output:\n{result['css']}")
    if 'warnings' in result:
        print(f"\nWarnings:")
        for warning in result['warnings']:
            print(f"  ⚠️  {warning}")
    if 'add' in result:
        print(f"\nClasses to add: {result['add']}")
    if 'preserve' in result:
        print(f"Classes to preserve: {result['preserve']}")
    if 'inline_styles' in result:
        print(f"\nInline styles: {result['inline_styles']}")


def test_pseudo_preserve():
    """Test preserving pseudo selectors."""
    print_header("Test 1: Preserve Pseudo Selectors")
    
    merger = CSSMerger(
        mode='component',
        conflict_resolution={'pseudo': 'preserve'}
    )
    
    source = ".btn:hover { color: red; background: blue; }"
    override = {"color": "green", "padding": "10px"}
    
    print(f"Source: {source}")
    print(f"Override: {override}")
    print("\nResult:")
    
    result = merger.merge(source, override)
    print_result(result)


def test_pseudo_inline():
    """Test converting pseudo selectors to inline."""
    print_header("Test 2: Convert Pseudo to Inline")
    
    merger = CSSMerger(
        mode='component',
        conflict_resolution={'pseudo': 'inline'}
    )
    
    source = ".btn:hover { color: red; background: blue; }"
    override = {"color": "green", "padding": "10px"}
    
    print(f"Source: {source}")
    print(f"Override: {override}")
    print("\nResult:")
    
    result = merger.merge(source, override)
    print_result(result)


def test_pseudo_force_merge():
    """Test force merging (dropping pseudo)."""
    print_header("Test 3: Force Merge (Drop Pseudo)")
    
    merger = CSSMerger(
        mode='component',
        conflict_resolution={'pseudo': 'force_merge'}
    )
    
    source = ".btn:hover { color: red; background: blue; }"
    override = {"color": "green", "padding": "10px"}
    
    print(f"Source: {source}")
    print(f"Override: {override}")
    print("\nResult:")
    
    result = merger.merge(source, override)
    print_result(result)


def test_important_respect():
    """Test respecting !important declarations."""
    print_header("Test 4: Respect !important")
    
    merger = CSSMerger(
        mode='permanent',
        conflict_resolution={'important': 'respect'}
    )
    
    source = ".important { color: red !important; padding: 10px; }"
    override = {"color": "blue", "padding": "20px"}
    
    print(f"Source: {source}")
    print(f"Override: {override}")
    print("\nResult:")
    
    result = merger.merge(source, override)
    print_result(result)


def test_important_override():
    """Test overriding !important declarations."""
    print_header("Test 5: Override !important")
    
    merger = CSSMerger(
        mode='permanent',
        conflict_resolution={'important': 'override'}
    )
    
    source = ".important { color: red !important; padding: 10px; }"
    override = {"color": "blue", "padding": "20px"}
    
    print(f"Source: {source}")
    print(f"Override: {override}")
    print("\nResult:")
    
    result = merger.merge(source, override)
    print_result(result)


def test_shorthand_smart():
    """Test smart shorthand merging."""
    print_header("Test 6: Smart Shorthand Merge")
    
    merger = CSSMerger(
        mode='permanent',
        conflict_resolution={'shorthand': 'smart'}
    )
    
    source = ".card { margin: 10px; border: 1px solid black; }"
    override = {"margin-top": "20px", "border-color": "red"}
    
    print(f"Source: {source}")
    print(f"Override: {override}")
    print("\nResult:")
    
    result = merger.merge(source, override)
    print_result(result)


def test_shorthand_cascade():
    """Test cascade strategy for shorthands."""
    print_header("Test 7: Cascade Shorthand Strategy")
    
    merger = CSSMerger(
        mode='permanent',
        conflict_resolution={'shorthand': 'cascade'}
    )
    
    source = ".card { border: 1px solid black; }"
    override = {"border-color": "red", "border-width": "2px"}
    
    print(f"Source: {source}")
    print(f"Override: {override}")
    print("\nResult:")
    
    result = merger.merge(source, override)
    print_result(result)


def test_fallback_chain():
    """Test fallback chain for strategies."""
    print_header("Test 8: Fallback Chain")
    
    # Using a list of strategies - if first fails, try next
    merger = CSSMerger(
        mode='component',
        conflict_resolution={
            'pseudo': ['preserve', 'inline'],  # Try preserve, fallback to inline
            'important': ['respect', 'warn']   # Try respect, fallback to warn
        }
    )
    
    source = ".btn:hover { color: red !important; }"
    override = {"color": "blue", "background": "yellow"}
    
    print(f"Source: {source}")
    print(f"Override: {override}")
    print("\nResult:")
    
    result = merger.merge(source, override)
    print_result(result)


def test_no_conflict_resolution():
    """Test behavior without conflict resolution."""
    print_header("Test 9: No Conflict Resolution (Default)")
    
    merger = CSSMerger(mode='component')  # No conflict_resolution
    
    source = ".btn:hover { color: red; }"
    override = {"color": "blue"}
    
    print(f"Source: {source}")
    print(f"Override: {override}")
    print("\nResult:")
    
    result = merger.merge(source, override)
    print_result(result)


def test_complex_scenario():
    """Test complex real-world scenario."""
    print_header("Test 10: Complex Real-World Scenario")
    
    merger = CSSMerger(
        mode='component',
        conflict_resolution={
            'pseudo': 'preserve',
            'media': 'preserve',
            'important': 'respect',
            'shorthand': 'smart'
        }
    )
    
    source = """
    .btn {
        padding: 0.375rem 0.75rem;
        border: 1px solid transparent;
        color: #333;
    }
    """
    
    override = {
        "padding": "0.5rem 1rem",
        "border-color": "#007bff",
        "color": "#fff",
        "background": "#007bff"
    }
    
    print(f"Source: Bootstrap-style button")
    print(f"Override: Brand customization")
    print("\nResult:")
    
    result = merger.merge(source, override)
    print_result(result)


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("  CSS CONFLICT RESOLUTION DEMONSTRATION")
    print("=" * 60)
    
    # Run all tests
    test_pseudo_preserve()
    test_pseudo_inline()
    test_pseudo_force_merge()
    test_important_respect()
    test_important_override()
    test_shorthand_smart()
    test_shorthand_cascade()
    test_fallback_chain()
    test_no_conflict_resolution()
    test_complex_scenario()
    
    print("\n" + "=" * 60)
    print("  All tests completed!")
    print("=" * 60)