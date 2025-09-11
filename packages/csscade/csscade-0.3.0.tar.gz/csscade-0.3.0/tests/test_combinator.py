"""Tests for the CSScade Combinator functionality."""

import pytest
from csscade.combinator import Combinator


class TestCombinator:
    """Test suite for the Combinator class."""
    
    def test_basic_conflict_detection(self):
        """Test basic conflict detection with Bootstrap-like classes."""
        combinator = Combinator()
        
        # Load some test CSS
        test_css = """
        .bg-primary { background-color: #007bff; }
        .p-3 { padding: 1rem; }
        .text-white { color: white; }
        .col-lg-6 { width: 50%; }
        """
        
        combinator.load_css([test_css])
        
        # Process overrides
        result = combinator.process(
            element_classes=['col-lg-6', 'bg-primary', 'p-3', 'text-white'],
            overrides={
                'background-color': '#00ff00',
                'padding': '2rem'
            },
            element_id='test123'
        )
        
        # Check results
        assert 'bg-primary' in result['remove_classes']
        assert 'p-3' in result['remove_classes']
        assert 'col-lg-6' in result['keep_classes']
        assert 'text-white' in result['keep_classes']
        assert result['add_classes'] == ['csso-test123']
        assert 'background-color: #00ff00 !important' in result['generated_css']
        assert 'padding: 2rem !important' in result['generated_css']
    
    def test_pseudo_selector_handling(self):
        """Test handling of pseudo-selectors in overrides."""
        combinator = Combinator()
        
        test_css = """
        .btn { 
            background-color: blue;
            padding: 10px;
        }
        .btn:hover {
            background-color: darkblue;
        }
        """
        
        combinator.load_css([test_css])
        
        result = combinator.process(
            element_classes=['btn'],
            overrides={
                'background-color': '#00ff00',
                ':hover': {
                    'background-color': '#00cc00',
                    'transform': 'scale(1.05)'
                }
            },
            element_id='btn123'
        )
        
        # Check CSS generation
        assert '.csso-btn123 {' in result['generated_css']
        assert '.csso-btn123:hover {' in result['generated_css']
        assert 'transform: scale(1.05)' in result['generated_css']
        assert 'background-color: #00ff00 !important' in result['generated_css']
        assert 'background-color: #00cc00 !important' in result['generated_css']
    
    def test_shorthand_conflict_detection(self):
        """Test that shorthand properties conflict correctly."""
        combinator = Combinator()
        
        test_css = """
        .m-3 { margin: 1rem; }
        .p-2 { padding-top: 0.5rem; padding-bottom: 0.5rem; }
        """
        
        combinator.load_css([test_css])
        
        result = combinator.process(
            element_classes=['m-3', 'p-2'],
            overrides={
                'margin-top': '2rem',  # Should conflict with margin
                'padding': '1rem'      # Should conflict with padding-top/bottom
            },
            element_id='test456'
        )
        
        # Both classes should be removed due to conflicts
        assert 'm-3' in result['remove_classes']
        assert 'p-2' in result['remove_classes']
    
    def test_inline_fallback_generation(self):
        """Test generation of inline style fallback."""
        combinator = Combinator()
        combinator.load_css([''])  # Empty CSS is fine for this test
        
        result = combinator.process(
            element_classes=[],
            overrides={
                'background-color': '#ff0000',
                'padding-top': '10px',
                'font-size': '16px',
                ':hover': {
                    'color': 'blue'  # Should not be in inline fallback
                }
            },
            element_id='test789'
        )
        
        # Check inline fallback
        assert result['fallback_inline']['backgroundColor'] == '#ff0000'
        assert result['fallback_inline']['paddingTop'] == '10px'
        assert result['fallback_inline']['fontSize'] == '16px'
        assert 'color' not in result['fallback_inline']
    
    def test_process_element_html(self):
        """Test processing an HTML element string."""
        combinator = Combinator()
        
        test_css = """
        .btn { background: blue; }
        .btn-primary { background: #007bff; }
        """
        
        combinator.load_css([test_css])
        
        result = combinator.process_element(
            html='<button class="btn btn-primary">Click me</button>',
            overrides={'background': 'red'},
            element_id='btn001'
        )
        
        # Both btn classes should conflict
        assert 'btn' in result['remove_classes']
        assert 'btn-primary' in result['remove_classes']
    
    def test_no_conflicts(self):
        """Test when there are no conflicts."""
        combinator = Combinator()
        
        test_css = """
        .text-center { text-align: center; }
        .font-bold { font-weight: bold; }
        """
        
        combinator.load_css([test_css])
        
        result = combinator.process(
            element_classes=['text-center', 'font-bold'],
            overrides={
                'color': 'red',
                'margin': '10px'
            },
            element_id='noconflict'
        )
        
        # No classes should be removed
        assert result['remove_classes'] == []
        assert 'text-center' in result['keep_classes']
        assert 'font-bold' in result['keep_classes']
        # Properties should not have !important
        assert 'color: red;' in result['generated_css']
        assert 'margin: 10px;' in result['generated_css']
        assert '!important' not in result['generated_css']
    
    def test_batch_processing(self):
        """Test batch processing of multiple elements."""
        combinator = Combinator()
        
        test_css = """
        .bg-red { background: red; }
        .text-blue { color: blue; }
        """
        
        combinator.load_css([test_css])
        
        elements = [
            {
                'element_classes': ['bg-red'],
                'overrides': {'background': 'green'},
                'element_id': 'elem1'
            },
            {
                'element_classes': ['text-blue'],
                'overrides': {'color': 'black'},
                'element_id': 'elem2'
            }
        ]
        
        results = combinator.process_batch(elements)
        
        assert len(results) == 2
        assert results[0]['remove_classes'] == ['bg-red']
        assert results[1]['remove_classes'] == ['text-blue']
    
    def test_error_no_css_loaded(self):
        """Test that error is raised when no CSS is loaded."""
        combinator = Combinator()
        
        with pytest.raises(RuntimeError, match="No CSS loaded"):
            combinator.process(
                element_classes=['test'],
                overrides={'color': 'red'},
                element_id='test'
            )
    
    def test_clear_cache(self):
        """Test clearing the CSS cache."""
        combinator = Combinator()
        
        test_css = ".test { color: red; }"
        combinator.load_css([test_css])
        
        # Should work after loading
        result = combinator.process(
            element_classes=['test'],
            overrides={'color': 'blue'},
            element_id='test'
        )
        assert 'test' in result['remove_classes']
        
        # Clear cache
        combinator.clear_cache()
        
        # Should fail after clearing
        with pytest.raises(RuntimeError):
            combinator.process(
                element_classes=['test'],
                overrides={'color': 'blue'},
                element_id='test'
            )