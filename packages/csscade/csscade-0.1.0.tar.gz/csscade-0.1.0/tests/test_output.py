"""Tests for the output formatter."""

import pytest
from csscade.generator.output import OutputFormatter
from csscade.models import CSSProperty, CSSRule


class TestOutputFormatter:
    """Test cases for OutputFormatter class."""
    
    def test_format_properties_as_css(self):
        """Test formatting properties as CSS string."""
        formatter = OutputFormatter()
        props = [
            CSSProperty("color", "blue"),
            CSSProperty("padding", "10px")
        ]
        
        result = formatter.format_properties(props, format="css")
        
        assert "color: blue" in result
        assert "padding: 10px" in result
        assert result.endswith(";")
    
    def test_format_properties_as_dict(self):
        """Test formatting properties as dictionary."""
        formatter = OutputFormatter()
        props = [
            CSSProperty("color", "blue"),
            CSSProperty("padding", "10px", important=True)
        ]
        
        result = formatter.format_properties(props, format="dict")
        
        assert result == {
            "color": "blue",
            "padding": "10px !important"
        }
    
    def test_format_properties_as_list(self):
        """Test formatting properties as list of dicts."""
        formatter = OutputFormatter()
        props = [
            CSSProperty("color", "blue"),
            CSSProperty("padding", "10px", important=True)
        ]
        
        result = formatter.format_properties(props, format="list")
        
        assert len(result) == 2
        assert result[0] == {"name": "color", "value": "blue", "important": False}
        assert result[1] == {"name": "padding", "value": "10px", "important": True}
    
    def test_format_properties_empty(self):
        """Test formatting empty properties list."""
        formatter = OutputFormatter()
        
        assert formatter.format_properties([], format="css") == ""
        assert formatter.format_properties([], format="dict") == {}
        assert formatter.format_properties([], format="list") == []
    
    def test_format_rule_as_css(self):
        """Test formatting rule as CSS."""
        formatter = OutputFormatter()
        rule = CSSRule(".btn", [
            CSSProperty("color", "blue"),
            CSSProperty("padding", "10px")
        ])
        
        result = formatter.format_rule(rule, format="css")
        
        assert ".btn" in result
        assert "{" in result and "}" in result
        assert "color: blue" in result
        assert "padding: 10px" in result
    
    def test_format_rule_as_css_formatted(self):
        """Test formatted (non-compact) CSS output."""
        formatter = OutputFormatter(indent="  ", compact=False)
        rule = CSSRule(".btn", [
            CSSProperty("color", "blue"),
            CSSProperty("padding", "10px")
        ])
        
        result = formatter.format_rule(rule, format="css")
        
        lines = result.split("\n")
        assert len(lines) == 4  # selector, 2 properties, closing brace
        assert lines[0] == ".btn {"
        assert "  color: blue;" in result
        assert "  padding: 10px;" in result
        assert lines[-1] == "}"
    
    def test_format_rule_compact(self):
        """Test compact CSS output."""
        formatter = OutputFormatter(compact=True)
        rule = CSSRule(".btn", [
            CSSProperty("color", "blue"),
            CSSProperty("padding", "10px")
        ])
        
        result = formatter.format_rule(rule, format="css")
        
        # Should be all on one line with no spaces
        assert result == ".btn{color: blue; padding: 10px;}"
    
    def test_format_rule_as_dict(self):
        """Test formatting rule as dictionary."""
        formatter = OutputFormatter()
        rule = CSSRule(".btn", [
            CSSProperty("color", "blue"),
            CSSProperty("padding", "10px")
        ])
        
        result = formatter.format_rule(rule, format="dict")
        
        assert result == {
            "selector": ".btn",
            "properties": {
                "color": "blue",
                "padding": "10px"
            }
        }
    
    def test_format_empty_rule(self):
        """Test formatting empty rule."""
        formatter = OutputFormatter()
        rule = CSSRule(".btn", [])
        
        result = formatter.format_rule(rule, format="css")
        assert result == ".btn {}"
    
    def test_format_stylesheet(self):
        """Test formatting multiple rules as stylesheet."""
        formatter = OutputFormatter()
        rules = [
            CSSRule(".btn", [CSSProperty("color", "blue")]),
            CSSRule(".card", [CSSProperty("padding", "20px")])
        ]
        
        result = formatter.format_stylesheet(rules)
        
        assert ".btn" in result
        assert ".card" in result
        assert "color: blue" in result
        assert "padding: 20px" in result
    
    def test_format_stylesheet_minified(self):
        """Test minified stylesheet output."""
        formatter = OutputFormatter()
        rules = [
            CSSRule(".btn", [CSSProperty("color", "blue")]),
            CSSRule(".card", [CSSProperty("padding", "20px")])
        ]
        
        result = formatter.format_stylesheet(rules, minify=True)
        
        # Should be compact with no line breaks
        assert "\n" not in result
        assert result == ".btn{color: blue;}.card{padding: 20px;}"
    
    def test_format_inline_styles(self):
        """Test formatting for HTML inline styles."""
        formatter = OutputFormatter()
        props = [
            CSSProperty("color", "blue"),
            CSSProperty("padding", "10px")
        ]
        
        result = formatter.format_inline_styles(props)
        
        assert result == "color: blue; padding: 10px;"
    
    def test_format_inline_styles_from_dict(self):
        """Test formatting inline styles from dictionary."""
        formatter = OutputFormatter()
        props = {
            "color": "blue",
            "padding": "10px !important"
        }
        
        result = formatter.format_inline_styles(props)
        
        assert "color: blue;" in result
        assert "padding: 10px !important;" in result
    
    def test_format_merge_result_complete(self):
        """Test formatting complete merge result."""
        formatter = OutputFormatter()
        
        result = formatter.format_merge_result(
            css=".btn-override { color: blue; }",
            add_classes=[".btn-override"],
            remove_classes=[".btn"],
            preserve_classes=[".container"],
            inline_styles={"margin": "5px"},
            important_styles={"color": "red"},
            warnings=["Some warning"]
        )
        
        assert result["css"] == ".btn-override { color: blue; }"
        assert result["add"] == [".btn-override"]
        assert result["remove"] == [".btn"]
        assert result["preserve"] == [".container"]
        assert result["inline"] == {"margin": "5px"}
        assert result["important"] == {"color": "red"}
        assert result["warnings"] == ["Some warning"]
    
    def test_format_merge_result_partial(self):
        """Test formatting partial merge result."""
        formatter = OutputFormatter()
        
        result = formatter.format_merge_result(
            css=".btn { color: blue; }",
            add_classes=[".btn"]
        )
        
        assert result == {
            "css": ".btn { color: blue; }",
            "add": [".btn"]
        }
        # Should not include None values
        assert "remove" not in result
        assert "inline" not in result
    
    def test_invalid_format(self):
        """Test invalid format parameter."""
        formatter = OutputFormatter()
        props = [CSSProperty("color", "blue")]
        
        with pytest.raises(ValueError) as exc_info:
            formatter.format_properties(props, format="invalid")
        
        assert "Unknown format: invalid" in str(exc_info.value)