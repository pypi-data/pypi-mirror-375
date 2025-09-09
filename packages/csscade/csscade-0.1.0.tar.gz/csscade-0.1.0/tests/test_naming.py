"""Tests for the class name generator."""

import pytest
from csscade.generator.naming import ClassNameGenerator
from csscade.models import CSSProperty


class TestClassNameGenerator:
    """Test cases for ClassNameGenerator class."""
    
    def test_hash_strategy_basic(self):
        """Test hash-based name generation."""
        generator = ClassNameGenerator(strategy="hash", prefix="css-", hash_length=8)
        
        props = [CSSProperty("color", "blue")]
        name = generator.generate_from_properties(props)
        
        assert name.startswith("css-")
        assert len(name) == 12  # "css-" (4) + 8 hash chars
        
        # Same properties should generate same name
        name2 = generator.generate_from_properties(props)
        assert name == name2
    
    def test_hash_strategy_consistent(self):
        """Test that hash strategy produces consistent results."""
        generator = ClassNameGenerator(strategy="hash")
        
        props1 = [
            CSSProperty("color", "blue"),
            CSSProperty("padding", "10px")
        ]
        props2 = [
            CSSProperty("padding", "10px"),
            CSSProperty("color", "blue")
        ]
        
        # Different order but same properties should produce same hash
        name1 = generator.generate_from_properties(props1)
        name2 = generator.generate_from_properties(props2)
        assert name1 == name2
    
    def test_hash_strategy_different_props(self):
        """Test that different properties produce different hashes."""
        generator = ClassNameGenerator(strategy="hash")
        
        props1 = [CSSProperty("color", "blue")]
        props2 = [CSSProperty("color", "red")]
        
        name1 = generator.generate_from_properties(props1)
        name2 = generator.generate_from_properties(props2)
        assert name1 != name2
    
    def test_semantic_strategy_basic(self):
        """Test semantic name generation."""
        generator = ClassNameGenerator(strategy="semantic", prefix="")
        
        props = [CSSProperty("color", "blue")]
        name = generator.generate_from_properties(props, base_name="btn")
        
        assert "btn" in name
        assert "override" in name
        # Should have a short hash at the end for uniqueness
        parts = name.split("-")
        assert len(parts[-1]) == 4  # 4-char hash
    
    def test_semantic_strategy_with_component_id(self):
        """Test semantic name generation with component ID."""
        generator = ClassNameGenerator(strategy="semantic", prefix="css-")
        
        props = [CSSProperty("color", "blue")]
        name = generator.generate_from_properties(
            props,
            base_name="btn",
            component_id="header-123"
        )
        
        assert name.startswith("css-")
        assert "btn" in name
        assert "override" in name
        assert "header-123" in name
    
    def test_sequential_strategy(self):
        """Test sequential name generation."""
        generator = ClassNameGenerator(strategy="sequential", prefix="style-")
        
        name1 = generator.generate_from_properties([])
        name2 = generator.generate_from_properties([])
        name3 = generator.generate_from_properties([])
        
        assert name1 == "style-1"
        assert name2 == "style-2"
        assert name3 == "style-3"
        
        # Reset counter
        generator.reset_counter()
        name4 = generator.generate_from_properties([])
        assert name4 == "style-1"
    
    def test_prefix_suffix(self):
        """Test prefix and suffix options."""
        generator = ClassNameGenerator(
            strategy="sequential",
            prefix="pre-",
            suffix="-post"
        )
        
        name = generator.generate_from_properties([])
        assert name == "pre-1-post"
    
    def test_generate_from_string(self):
        """Test generation from CSS string."""
        generator = ClassNameGenerator(strategy="hash")
        
        css_string = "color: blue; padding: 10px"
        name = generator.generate_from_properties(css_string)
        
        assert name.startswith("css-")
        assert len(name) > 4
    
    def test_cache_functionality(self):
        """Test that caching works for hash strategy."""
        generator = ClassNameGenerator(strategy="hash")
        
        props = [CSSProperty("color", "blue")]
        
        # Generate name multiple times
        name1 = generator.generate_from_properties(props)
        name2 = generator.generate_from_properties(props)
        
        # Should be cached
        assert name1 == name2
        assert len(generator._name_cache) == 1
        
        # Clear cache
        generator.clear_cache()
        assert len(generator._name_cache) == 0
        
        # Should still generate same name
        name3 = generator.generate_from_properties(props)
        assert name3 == name1
    
    def test_generate_for_mode_permanent(self):
        """Test mode-based generation for permanent mode."""
        generator = ClassNameGenerator()
        
        name = generator.generate_for_mode(
            mode="permanent",
            base_selector=".btn",
            properties=[CSSProperty("color", "blue")]
        )
        
        assert name == ".btn"
    
    def test_generate_for_mode_component(self):
        """Test mode-based generation for component mode."""
        generator = ClassNameGenerator(strategy="semantic")
        
        name = generator.generate_for_mode(
            mode="component",
            base_selector=".btn",
            properties=[CSSProperty("color", "blue")],
            component_id="header-123"
        )
        
        assert name.startswith(".")
        assert "btn" in name
        assert "override" in name
        assert "header-123" in name
    
    def test_generate_for_mode_replace(self):
        """Test mode-based generation for replace mode."""
        generator = ClassNameGenerator(strategy="semantic")  # Use semantic to include base name
        
        name = generator.generate_for_mode(
            mode="replace",
            base_selector=".btn",
            properties=[CSSProperty("color", "blue")]
        )
        
        assert name.startswith(".")
        assert "btn-replace" in name
    
    def test_clean_base_selector(self):
        """Test that base selector is cleaned properly."""
        generator = ClassNameGenerator(strategy="semantic")
        
        # Test with class selector
        name1 = generator.generate_for_mode(
            mode="component",
            base_selector=".btn",
            properties=[CSSProperty("color", "blue")]
        )
        
        # Test with ID selector
        name2 = generator.generate_for_mode(
            mode="component",
            base_selector="#btn",
            properties=[CSSProperty("color", "blue")]
        )
        
        # Both should have "btn" without the prefix
        assert "btn" in name1
        assert "btn" in name2
        assert not ".btn" in name1
        assert not "#btn" in name2