# CSSCade 🎨

**Intelligent CSS merging with conflict resolution and multiple strategies**

CSSCade is a Python library that intelligently merges CSS properties from different sources, handling conflicts, preserving specificity, and supporting various merge strategies. Perfect for theme customization, runtime CSS manipulation, and CSS-in-JS implementations.

I was looking for something like this in the Python ecosystem but couldn't find anything, so here it is.

## Features ✨

- **3 Merge Modes**: Permanent, Component, and Replace strategies
- **Intelligent Conflict Resolution**: Handle pseudo selectors, !important, shorthands, and media queries
- **Smart Property Merging**: Understands CSS semantics and property relationships
- **Production Ready**: Used in real-world applications for dynamic theming
- **Fully Typed**: Complete type hints for better IDE support

## Installation

### For Users
```bash
pip install csscade
```

This installs only the minimal runtime dependency (`cssutils`).

### For Developers
```bash
# Clone the repository
git clone https://github.com/yourusername/csscade.git
cd csscade

# Install development dependencies
pip install -r requirements-dev.txt
```

**Minimal Dependencies:** CSSCade has only ONE runtime dependency (`cssutils`) making it lightweight and fast to install!

## Quick Start 🚀

### Basic Usage

```python
from csscade import CSSMerger

# Create a merger with your preferred mode
merger = CSSMerger(mode='component')

# Merge CSS
source_css = ".btn { color: red; padding: 10px; }"
overrides = {"color": "blue", "margin": "5px"}

result = merger.merge(source_css, overrides)

print(result['css'])        # The generated CSS
print(result['add'])        # Classes to add: ['btn-override-xxx']
print(result['preserve'])   # Classes to keep: ['btn']
```

## Merge Modes

CSSCade offers three different merge strategies, each suited for different use cases:

### 1. Permanent Mode
Directly modifies the original CSS rule. Best for build-time CSS generation.

```python
merger = CSSMerger(mode='permanent')

result = merger.merge(
    ".card { color: red; padding: 10px; }",
    {"color": "blue", "margin": "20px"}
)

# Output CSS:
# .card {
#   color: blue;      /* Changed */
#   padding: 10px;    /* Preserved */
#   margin: 20px;     /* Added */
# }
```

### 2. Component Mode
Creates an override class while preserving the original. Perfect for theming systems.

```python
merger = CSSMerger(mode='component')

result = merger.merge(
    ".btn { color: red; padding: 10px; }",
    {"color": "blue", "margin": "5px"}
)

# Output:
# - CSS: .btn-override-xxx { color: blue; margin: 5px; }
# - Add class: 'btn-override-xxx'
# - Preserve class: 'btn'
# Usage: <button class="btn btn-override-xxx">
```

### 3. Replace Mode
Creates a complete replacement class with all properties merged (if you no longer want or need the original class).

```python
merger = CSSMerger(mode='replace')

result = merger.merge(
    ".btn { color: red; padding: 10px; }",
    {"color": "blue", "margin": "5px"}
)

# Output:
# - CSS: .btn-replaced-xxx { color: blue; padding: 10px; margin: 5px; }
# - Add class: 'btn-replaced-xxx'
# - Remove class: 'btn'
# Usage: <button class="btn-replaced-xxx">
```

## Conflict Resolution 🔧

CSSCade can intelligently handle various CSS conflicts:

### Pseudo Selectors

```python
# Preserve hover states
merger = CSSMerger(
    mode='component',
    conflict_resolution={'pseudo': 'preserve'}
)

result = merger.merge(
    ".btn:hover { color: red; }",
    {"color": "blue", "padding": "10px"}
)
# Creates: .btn-new:hover with merged properties

# Convert to inline for JavaScript
merger = CSSMerger(
    mode='component',
    conflict_resolution={'pseudo': 'inline'}
)
# Returns inline styles for runtime application
```

### !important Handling

```python
# Respect !important declarations
merger = CSSMerger(
    mode='permanent',
    conflict_resolution={'important': 'respect'}
)

result = merger.merge(
    ".alert { color: red !important; }",
    {"color": "blue"}  # Won't override !important
)

# Force override
merger = CSSMerger(
    mode='permanent',
    conflict_resolution={'important': 'override'}
)
# Blue will win regardless of !important
```

### Shorthand Properties

```python
# Smart shorthand merging
merger = CSSMerger(
    mode='permanent',
    conflict_resolution={'shorthand': 'smart'}
)

result = merger.merge(
    ".box { margin: 10px; }",
    {"margin-top": "20px"}
)
# Result: margin: 20px 10px 10px 10px;

# Use cascade strategy for complex shorthands
merger = CSSMerger(
    mode='permanent',
    conflict_resolution={'shorthand': 'cascade'}
)
```

## Advanced Usage 🎯

### Real-World Example: Bootstrap Customization

```python
# Customizing Bootstrap components while preserving functionality
merger = CSSMerger(
    mode='component',
    conflict_resolution={
        'pseudo': 'preserve',      # Keep hover/focus states
        'important': 'respect',    # Respect Bootstrap's !important
        'shorthand': 'smart',      # Smart margin/padding merge
        'media': 'preserve'        # Keep responsive breakpoints
    }
)

bootstrap_btn = """
.btn-primary {
    display: inline-block;
    font-weight: 400;
    color: #fff !important;
    background-color: #007bff;
    border: 1px solid #007bff;
    padding: 0.375rem 0.75rem;
    transition: all 0.15s ease-in-out;
}
.btn-primary:hover {
    background-color: #0056b3;
}
"""

brand_overrides = {
    "background-color": "#28a745",  # Green instead of blue
    "padding": "0.5rem 1.5rem",     # Larger padding
    "border-radius": "50px"         # Pill shape
}

result = merger.merge(bootstrap_btn, brand_overrides)
# Preserves hover states while applying brand customization
```

### Fallback Chains

Use multiple strategies with automatic fallback:

```python
merger = CSSMerger(
    mode='component',
    conflict_resolution={
        'pseudo': ['preserve', 'inline', 'force_merge'],  # Try in order
        'important': ['respect', 'warn', 'override'],     # Fallback chain
        'shorthand': ['smart', 'expand', 'cascade']       # Multiple strategies
    }
)
```

### Runtime CSS Manipulation

For JavaScript-based styling:

```python
merger = CSSMerger(
    mode='component',
    conflict_resolution={
        'pseudo': 'inline',      # Convert for JS handling
        'media': 'inline',       # Handle breakpoints in JS
        'important': 'override'  # Dynamic styles win
    }
)

result = merger.merge(source, overrides)
# Returns inline styles and instructions for runtime application
```

## API Reference 📚

### CSSMerger Constructor

```python
merger = CSSMerger(
    mode='component',           # Required: 'permanent'|'component'|'replace'
    conflict_resolution={...},  # Optional: Resolution strategies
    naming={...},              # Optional: Class naming configuration
    validation={...},          # Optional: Validation settings
    performance={...},         # Optional: Performance tuning
    debug=False                # Optional: Enable debug output
)
```

### Configuration Options

#### Naming Configuration
Control how generated class names are created:

```python
naming={
    'strategy': 'semantic',    # 'hash'| 'semantic' | 'sequential'
    'prefix': 'csscade-',      # Prefix for all generated classes
    'suffix': '-override',     # Suffix for all generated classes
    'hash_length': 8           # Length of hash when using hash strategy
}
```

**Examples:**
```python
# Custom prefix for your app
merger = CSSMerger(
    mode='component',
    naming={'prefix': 'myapp-'}
)
# Generates: .myapp-btn-override-xxx

# Hash-based names with custom length
merger = CSSMerger(
    mode='replace',
    naming={'strategy': 'hash', 'hash_length': 12}
)
# Generates: .css-a1b2c3d4e5f6

# Semantic names with prefix and suffix
merger = CSSMerger(
    mode='component',
    naming={
        'strategy': 'semantic',
        'prefix': 'brand-',
        'suffix': '-custom'
    }
)
# Generates: .brand-btn-override-custom
```

#### Validation Configuration
Control CSS validation behavior:

```python
validation={
    'strict': True,            # Strict CSS syntax validation
    'allow_vendor': True,      # Allow vendor prefixes (-webkit-, -moz-, etc.)
    'check_duplicates': True   # Check for duplicate properties
}
```

#### Performance Configuration
Optimize for your use case:

```python
performance={
    'optimize': True,          # Enable performance optimizations
    'cache': True,            # Cache parsed CSS rules
    'batch_size': 100         # Batch size for bulk operations
}
```

### Conflict Resolution Options

| Conflict Type | Strategies | Description |
|--------------|------------|-------------|
| `pseudo` | `preserve`, `inline`, `ignore`, `force_merge`, `extract` | Handle :hover, :focus, etc. |
| `important` | `respect`, `override`, `warn`, `strip` | Handle !important declarations |
| `shorthand` | `smart`, `expand`, `cascade`, `preserve` | Handle margin, padding, border, etc. |
| `media` | `preserve`, `inline`, `duplicate`, `extract` | Handle @media queries |
| `multiple_rules` | `first`, `all`, `most_specific` | Handle multiple matching rules |

### Result Dictionary

The `merge()` method returns a dictionary with:

```python
{
    'css': str,              # Generated CSS string
    'add': List[str],        # Classes to add to element
    'remove': List[str],     # Classes to remove from element
    'preserve': List[str],   # Classes to keep on element
    'inline_styles': Dict,   # Inline styles (if applicable)
    'warnings': List[str],   # Warning messages
    'info': List[str]        # Informational messages
}
```

## Use Cases 💡

### 1. Theme Customization
Apply brand colors and styles to third-party components while preserving their functionality.

### 2. Runtime Theming
Allow users to customize UI elements dynamically without rebuilding CSS.

### 3. CSS-in-JS Libraries
Merge styles from different sources with proper conflict resolution.

### 4. Design System Overrides
Override design system defaults while maintaining consistency.

### 5. A/B Testing
Create variant styles without duplicating entire CSS rules.

## Examples

### Simple Property Override

```python
from csscade import CSSMerger

# Simple override
merger = CSSMerger(mode='permanent')
result = merger.merge(
    ".text { color: black; font-size: 14px; }",
    {"color": "blue"}
)
print(result['css'])
# Output: .text { color: blue; font-size: 14px; }
```

### Component Composition

```python
# Combining multiple style sources
merger = CSSMerger(mode='component')

base_styles = ".card { padding: 20px; border: 1px solid #ccc; }"
theme_overrides = {"border-color": "#007bff", "box-shadow": "0 2px 4px rgba(0,0,0,0.1)"}

result = merger.merge(base_styles, theme_overrides)
# Apply both classes to get combined styles
```

### Handling Edge Cases

```python
# Empty source
merger = CSSMerger(mode='permanent')
result = merger.merge("", {"color": "blue"})

# Empty overrides
result = merger.merge(".btn { color: red; }", {})

# Properties only (no selector)
result = merger.merge(
    {"color": "red", "padding": "10px"},
    {"color": "blue", "margin": "5px"}
)
```

## Complete Configuration Examples 🎯

### Production Configuration
Full configuration for production use:

```python
merger = CSSMerger(
    mode='component',
    
    # Custom class naming
    naming={
        'strategy': 'semantic',
        'prefix': 'myapp-',
        'suffix': ''
    },
    
    # Conflict resolution
    conflict_resolution={
        'pseudo': 'preserve',
        'important': 'respect',
        'shorthand': 'smart',
        'media': 'preserve'
    },
    
    # Performance optimizations
    performance={
        'optimize': True,
        'cache': True
    },
    
    # Validation
    validation={
        'strict': False,
        'allow_vendor': True
    }
)
```

### Development Configuration
Configuration for development with debugging:

```python
merger = CSSMerger(
    mode='component',
    naming={'prefix': 'dev-'},
    conflict_resolution={
        'pseudo': ['preserve', 'inline'],  # Fallback chains
        'important': 'warn'
    },
    debug=True  # Enable debug output
)
```

### Minimal Configuration
Just the essentials:

```python
# Only mode is required
merger = CSSMerger(mode='permanent')

# With one customization
merger = CSSMerger(
    mode='component',
    naming={'prefix': 'custom-'}
)
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - see LICENSE file for details.

## Support

For bug reports, issues or suggestions, please open an issue on GitHub.

## Author

[sebieire](https://github.com/sebieire/)