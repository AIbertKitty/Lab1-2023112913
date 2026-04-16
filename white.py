import pytest
from test1_optim import TextGraph

@pytest.fixture
def graph_basic():
    text = "a b c a d c f g h a e" 
    return TextGraph(text)

def test_query_bridge_words_both_missing(graph_basic):
    result = graph_basic.query_bridge_words("x", "y")
    assert result == 'No "x" and "y" in the graph'

def test_query_bridge_words_first_missing(graph_basic):
    result = graph_basic.query_bridge_words("x", "c")
    assert result == 'No "x" in the graph!'

def test_query_bridge_words_second_missing(graph_basic):
    result = graph_basic.query_bridge_words("a", "y")
    assert result == 'No "y" in the graph!'

def test_query_bridge_words_no_bridge(graph_basic):
    result = graph_basic.query_bridge_words("b", "c")
    assert result == 'No bridge words from "b" to "c"!'

def test_query_bridge_words_has_bridge_single(graph_basic):
    result = graph_basic.query_bridge_words("f", "h")
    assert result == 'The bridge word from "f" to "h" is:"g."'

def test_query_bridge_words_has_bridge_multiple(graph_basic): 
    result = graph_basic.query_bridge_words("a", "c")
    assert result == 'The bridge words from "a" to "c" are: "b","d".' or 'The bridge words from "a" to "c" are: "d","b".' 

def test_query_bridge_words_case_insensitive(graph_basic):
    result = graph_basic.query_bridge_words("F", "H") 
    assert result == 'The bridge word from "f" to "h" is:"g."' 