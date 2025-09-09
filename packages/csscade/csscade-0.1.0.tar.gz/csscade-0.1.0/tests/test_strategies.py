"""Tests for merge strategies."""

import pytest
from csscade.strategies.permanent import PermanentMergeStrategy
from csscade.strategies.component import ComponentMergeStrategy
from csscade.strategies.replace import ReplaceMergeStrategy
from csscade.models import CSSProperty, CSSRule


class TestPermanentMergeStrategy:
    """Test cases for PermanentMergeStrategy."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.strategy = PermanentMergeStrategy()
    
    def test_merge_with_rule_source(self):
        """Test merging with a CSS rule as source."""
        source_rule = CSSRule(".btn", [
            CSSProperty("color", "red"),
            CSSProperty("padding", "10px")
        ])
        override = {"color": "blue"}
        
        result = self.strategy.merge(source_rule, override)
        
        assert "css" in result
        assert ".btn" in result["css"]
        assert "color: blue" in result["css"]
        assert "padding: 10px" in result["css"]
        assert result.get("inline") is None
        assert result.get("important") is None
    
    def test_merge_with_string_source(self):
        """Test merging with a CSS string as source."""
        source = ".btn { color: red; margin: 5px; }"
        override = {"color": "blue"}
        
        result = self.strategy.merge(source, override)
        
        assert "css" in result
        assert ".btn" in result["css"]
        assert "color: blue" in result["css"]
        assert "margin: 5px" in result["css"]
    
    def test_merge_with_dict_source(self):
        """Test merging with a dictionary as source."""
        source = {"color": "red", "padding": "10px"}
        override = {"color": "blue", "margin": "5px"}
        
        result = self.strategy.merge(source, override, selector=".btn")
        
        assert "css" in result
        assert ".btn" in result["css"]
        assert "color: blue" in result["css"]
        assert "padding: 10px" in result["css"]
        assert "margin: 5px" in result["css"]
    
    def test_merge_preserves_selector(self):
        """Test that permanent merge preserves the original selector."""
        source = ".custom-btn { color: red; }"
        override = {"color": "blue"}
        
        result = self.strategy.merge(source, override)
        
        assert ".custom-btn" in result["css"]
        assert ".btn-override" not in result["css"]
    
    def test_get_strategy_name(self):
        """Test getting strategy name."""
        assert self.strategy.get_strategy_name() == "permanent"


class TestComponentMergeStrategy:
    """Test cases for ComponentMergeStrategy."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.strategy = ComponentMergeStrategy()
    
    def test_merge_creates_override_class(self):
        """Test that component merge creates an override class."""
        source = ".btn { color: red; margin: 5px; }"
        override = {"color": "blue"}
        
        result = self.strategy.merge(source, override)
        
        assert "css" in result
        assert "add" in result
        assert "preserve" in result
        assert len(result["add"]) == 1
        assert result["preserve"] == ["btn"]
        # Override class should contain all merged properties
        assert "color: blue" in result["css"]
        assert "margin: 5px" in result["css"]
    
    def test_merge_with_component_id(self):
        """Test merging with a component ID."""
        source = ".btn { color: red; }"
        override = {"color": "blue"}
        
        result = self.strategy.merge(source, override, component_id="header-123")
        
        assert "css" in result
        assert "add" in result
        assert "header-123" in result["css"]
    
    def test_merge_no_conflicts(self):
        """Test merging when there are no conflicts."""
        source = ".btn { color: red; }"
        override = {"padding": "10px"}
        
        result = self.strategy.merge(source, override)
        
        # Component mode now always creates a merged class
        assert "css" in result
        assert "add" in result
        assert result["preserve"] == ["btn"]
        # Should contain both original and new properties
        assert "color: red" in result["css"]
        assert "padding: 10px" in result["css"]
    
    def test_merge_with_shorthand_conflicts(self):
        """Test merging with shorthand/longhand conflicts."""
        source_rule = CSSRule(".btn", [
            CSSProperty("margin-top", "10px"),
            CSSProperty("margin-bottom", "20px")
        ])
        override = {"margin": "5px"}
        
        result = self.strategy.merge(source_rule, override)
        
        assert "css" in result
        assert "margin: 5px" in result["css"]
        assert "add" in result
        assert "preserve" in result
    
    def test_merge_multiple_conflicts(self):
        """Test merging with multiple conflicting properties."""
        source = ".btn { color: red; padding: 10px; margin: 5px; }"
        override = {"color": "blue", "padding": "20px", "border": "1px solid"}
        
        result = self.strategy.merge(source, override)
        
        assert "css" in result
        assert "color: blue" in result["css"]
        assert "padding: 20px" in result["css"]
        # Component mode now includes all properties (merged)
        assert "margin: 5px" in result["css"]
        assert "border: 1px solid" in result["css"]
    
    def test_get_strategy_name(self):
        """Test getting strategy name."""
        assert self.strategy.get_strategy_name() == "component"


class TestReplaceMergeStrategy:
    """Test cases for ReplaceMergeStrategy."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.strategy = ReplaceMergeStrategy()
    
    def test_merge_creates_replacement_class(self):
        """Test that replace merge creates a complete replacement class."""
        source = ".btn { color: red; margin: 5px; }"
        override = {"color": "blue"}
        
        result = self.strategy.merge(source, override)
        
        assert "css" in result
        assert "add" in result
        assert "remove" in result
        assert len(result["add"]) == 1
        assert result["remove"] == ["btn"]
        # Replacement class should have all properties
        assert "color: blue" in result["css"]
        assert "margin: 5px" in result["css"]
    
    def test_merge_with_component_id(self):
        """Test merging with a component ID."""
        source = ".btn { color: red; padding: 10px; }"
        override = {"color": "blue"}
        
        result = self.strategy.merge(source, override, component_id="modal-456")
        
        assert "css" in result
        assert "add" in result
        assert "remove" in result
        # Class name should include component ID influence
        css_class = result["add"][0]
        assert css_class != "btn"
    
    def test_merge_adds_new_properties(self):
        """Test that new properties are added to replacement class."""
        source = ".btn { color: red; }"
        override = {"color": "blue", "padding": "10px", "margin": "5px"}
        
        result = self.strategy.merge(source, override)
        
        assert "css" in result
        assert "color: blue" in result["css"]
        assert "padding: 10px" in result["css"]
        assert "margin: 5px" in result["css"]
    
    def test_merge_with_dict_source(self):
        """Test merging with dictionary source."""
        source = {"color": "red", "font-size": "14px"}
        override = {"color": "blue", "font-weight": "bold"}
        
        result = self.strategy.merge(source, override, selector=".text")
        
        assert "css" in result
        assert "add" in result
        assert "remove" in result
        assert result["remove"] == ["text"]
        assert "color: blue" in result["css"]
        assert "font-size: 14px" in result["css"]
        assert "font-weight: bold" in result["css"]
    
    def test_get_strategy_name(self):
        """Test getting strategy name."""
        assert self.strategy.get_strategy_name() == "replace"


class TestStrategyValidation:
    """Test input validation for all strategies."""
    
    def test_permanent_strategy_validation(self):
        """Test input validation for permanent strategy."""
        strategy = PermanentMergeStrategy()
        
        with pytest.raises(ValueError) as exc_info:
            strategy.merge(None, {"color": "blue"})
        assert "Source cannot be None" in str(exc_info.value)
        
        with pytest.raises(ValueError) as exc_info:
            strategy.merge(".btn { color: red; }", None)
        assert "Override cannot be None" in str(exc_info.value)
    
    def test_component_strategy_validation(self):
        """Test input validation for component strategy."""
        strategy = ComponentMergeStrategy()
        
        with pytest.raises(ValueError):
            strategy.merge(None, {"color": "blue"})
        
        with pytest.raises(ValueError):
            strategy.merge(".btn { color: red; }", None)
    
    def test_replace_strategy_validation(self):
        """Test input validation for replace strategy."""
        strategy = ReplaceMergeStrategy()
        
        with pytest.raises(ValueError):
            strategy.merge(None, {"color": "blue"})
        
        with pytest.raises(ValueError):
            strategy.merge(".btn { color: red; }", None)