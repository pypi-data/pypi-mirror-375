#!/usr/bin/env python3
"""Test media query handling in CSScade."""

from csscade import CSSMerger


def test_media_queries():
    """Test if media queries are handled."""
    
    print("=" * 80)
    print("MEDIA QUERY HANDLING TEST")
    print("=" * 80)
    
    # Test 1: Basic media query in source
    print("\n### TEST 1: Media query in source CSS ###")
    print("-" * 60)
    
    source_css = """
    .card {
        padding: 10px;
        background: white;
    }
    
    @media (min-width: 768px) {
        .card {
            padding: 20px;
            background: lightgray;
        }
    }
    """
    
    overrides = {"border": "1px solid black"}
    
    print("Source CSS (with media query):")
    print(source_css)
    print("\nOverrides:", overrides)
    
    merger = CSSMerger(mode='permanent')
    
    try:
        result = merger.merge(source_css, overrides)
        print("\nResult:")
        for css in result.get('css', []):
            print(css)
        if result.get('warnings'):
            print("\nWarnings:", result['warnings'])
    except Exception as e:
        print(f"\nError: {e}")
    
    # Test 2: Regular CSS without media queries
    print("\n\n### TEST 2: Regular CSS (no media queries) ###")
    print("-" * 60)
    
    source_css = """
    .card {
        padding: 10px;
        background: white;
    }
    """
    
    print("Source CSS:")
    print(source_css)
    print("\nOverrides:", overrides)
    
    result = merger.merge(source_css, overrides)
    print("\nResult:")
    for css in result.get('css', []):
        print(css)
    
    # Test 3: Check if media queries are even parsed
    print("\n\n### TEST 3: Direct parser test ###")
    print("-" * 60)
    
    from csscade.parser.css_parser import CSSParser
    
    parser = CSSParser()
    
    css_with_media = """
    .btn {
        color: blue;
    }
    
    @media (min-width: 768px) {
        .btn {
            color: red;
        }
    }
    """
    
    print("CSS to parse:")
    print(css_with_media)
    
    try:
        rules = parser.parse_rule_string(css_with_media)
        print(f"\nParsed {len(rules)} rule(s):")
        for rule in rules:
            print(f"  Selector: {rule.selector}")
            for prop in rule.properties:
                print(f"    {prop.name}: {prop.value}")
    except Exception as e:
        print(f"\nParser error: {e}")


if __name__ == "__main__":
    test_media_queries()
    
    print("\n" + "=" * 80)
    print("MEDIA QUERY TEST COMPLETE")
    print("=" * 80)