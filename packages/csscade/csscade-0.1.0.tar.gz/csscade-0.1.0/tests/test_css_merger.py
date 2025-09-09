"""Tests for the main CSSMerger API."""

import pytest
from csscade import CSSMerger, CSSProperty, CSSRule


class TestCSSMergerAPI:
    """Test cases for the main CSSMerger API."""
    
    def test_default_mode(self):
        """Test that default mode is component."""
        merger = CSSMerger()
        assert merger.get_mode() == "component"
    
    def test_permanent_mode(self):
        """Test permanent mode merging."""
        merger = CSSMerger(mode="permanent")
        
        result = merger.merge(
            source=".btn { color: red; margin: 5px; }",
            override={"color": "blue"}
        )
        
        assert "css" in result
        assert ".btn" in result["css"]
        assert "color: blue" in result["css"]
        assert "margin: 5px" in result["css"]
        assert "add" not in result
        assert "remove" not in result
    
    def test_component_mode(self):
        """Test component mode merging."""
        merger = CSSMerger(mode="component")
        
        result = merger.merge(
            source=".btn { color: red; margin: 5px; }",
            override={"color": "blue"}
        )
        
        assert "css" in result
        assert "add" in result
        assert "preserve" in result
        assert "color: blue" in result["css"]
        # Should not include non-conflicting properties
        assert "margin" not in result["css"]
    
    def test_replace_mode(self):
        """Test replace mode merging."""
        merger = CSSMerger(mode="replace")
        
        result = merger.merge(
            source=".btn { color: red; margin: 5px; }",
            override={"color": "blue"}
        )
        
        assert "css" in result
        assert "add" in result
        assert "remove" in result
        assert "color: blue" in result["css"]
        assert "margin: 5px" in result["css"]
    
    def test_mode_switching(self):
        """Test switching between modes."""
        merger = CSSMerger(mode="permanent")
        assert merger.get_mode() == "permanent"
        
        merger.set_mode("component")
        assert merger.get_mode() == "component"
        
        # Test that mode switch affects behavior
        result = merger.merge(
            source=".btn { color: red; }",
            override={"color": "blue"}
        )
        assert "add" in result  # Component mode should have add
    
    def test_component_id(self):
        """Test component ID parameter."""
        merger = CSSMerger(mode="component")
        
        result = merger.merge(
            source=".btn { color: red; }",
            override={"color": "blue"},
            component_id="header-123"
        )
        
        assert "header-123" in result["css"]
    
    def test_debug_mode(self):
        """Test debug mode adds debug information."""
        merger = CSSMerger(mode="permanent", debug=True)
        
        result = merger.merge(
            source=".btn { color: red; }",
            override={"color": "blue"},
            component_id="test-123"
        )
        
        assert "debug" in result
        assert result["debug"]["mode"] == "permanent"
        assert result["debug"]["strategy"] == "permanent"
        assert result["debug"]["component_id"] == "test-123"
    
    def test_invalid_mode(self):
        """Test that invalid mode raises error."""
        with pytest.raises(ValueError) as exc_info:
            CSSMerger(mode="invalid")
        assert "Unknown merge mode: invalid" in str(exc_info.value)
    
    def test_dict_source(self):
        """Test merging with dictionary source."""
        merger = CSSMerger(mode="permanent")
        
        result = merger.merge(
            source={"color": "red", "padding": "10px"},
            override={"color": "blue"},
            selector=".btn"
        )
        
        assert "css" in result
        assert ".btn" in result["css"]
        assert "color: blue" in result["css"]
        assert "padding: 10px" in result["css"]
    
    def test_property_list_source(self):
        """Test merging with property list source."""
        merger = CSSMerger(mode="permanent")
        
        source = [
            CSSProperty("color", "red"),
            CSSProperty("padding", "10px")
        ]
        
        result = merger.merge(
            source=source,
            override={"color": "blue"},
            selector=".btn"
        )
        
        assert "css" in result
        assert "color: blue" in result["css"]
        assert "padding: 10px" in result["css"]


class TestBatchMerger:
    """Test cases for BatchMerger."""
    
    def test_batch_operations(self):
        """Test batch merge operations."""
        merger = CSSMerger(mode="component")
        batch = merger.batch()
        
        batch.add(
            source=".btn { color: red; }",
            override={"color": "blue"},
            component_id="btn-1"
        )
        batch.add(
            source=".card { padding: 10px; }",
            override={"padding": "20px"},
            component_id="card-1"
        )
        
        results = batch.execute()
        
        assert len(results) == 2
        assert "css" in results[0]
        assert "css" in results[1]
        assert "btn-1" in results[0]["css"]
        assert "card-1" in results[1]["css"]
    
    def test_batch_chaining(self):
        """Test batch operation chaining."""
        merger = CSSMerger(mode="replace")
        
        results = (merger.batch()
            .add(".btn { color: red; }", {"color": "blue"})
            .add(".card { padding: 10px; }", {"margin": "5px"})
            .execute())
        
        assert len(results) == 2
        assert all("css" in r for r in results)
        assert all("add" in r for r in results)
        assert all("remove" in r for r in results)
    
    def test_batch_clear(self):
        """Test clearing batch operations."""
        merger = CSSMerger()
        batch = merger.batch()
        
        batch.add(".btn { color: red; }", {"color": "blue"})
        batch.add(".card { padding: 10px; }", {"padding": "20px"})
        
        batch.clear()
        results = batch.execute()
        
        assert len(results) == 0


class TestAPIExamples:
    """Test examples from the API documentation."""
    
    def test_simple_property_override(self):
        """Test simple property override example."""
        merger = CSSMerger()
        result = merger.merge(
            source={'color': 'red', 'padding': '10px'},
            override={'color': 'blue'}
        )
        # Component mode creates override class
        assert "css" in result
        assert "add" in result
    
    def test_mode_examples(self):
        """Test mode-specific examples from documentation."""
        # Mode 1: Permanent Merge
        merger = CSSMerger(mode='permanent')
        result = merger.merge(
            source='.btn { color: red; margin: 5px; }',
            override={'color': 'blue'}
        )
        assert "css" in result
        assert ".btn" in result["css"]
        assert "color: blue" in result["css"]
        
        # Mode 2: Component Isolation
        merger = CSSMerger(mode='component')
        result = merger.merge(
            source='.btn { color: red; margin: 5px; }',
            override={'color': 'blue'},
            component_id='header-123'
        )
        assert "css" in result
        assert "add" in result
        assert "preserve" in result
        assert "header-123" in result["css"]
        
        # Mode 3: Replace Mode
        merger = CSSMerger(mode='replace')
        result = merger.merge(
            source='.btn { color: red; margin: 5px; }',
            override={'color': 'blue'}
        )
        assert "css" in result
        assert "add" in result
        assert "remove" in result
        assert "color: blue" in result["css"]
        assert "margin: 5px" in result["css"]