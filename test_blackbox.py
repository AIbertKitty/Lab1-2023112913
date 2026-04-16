# import pytest
# from test1_optim import *  # 替换为你实际的函数名和导入方式

# read = sys.stdin.readline
# print('input complete path, enter:')
# dest = read().rstrip()
# with open(dest, 'r', encoding='utf-8') as file_x:
#     text = file_x.read()
# textgraph = TextGraph(text)

# def test_queryBridgeWords_valid():
#     # 测试用例1：正常情况，存在桥接词
#     assert textgraph.query_bridge_words("carefully", "the") == "analyzed"


# def test_queryBridgeWords_not_valid():
#     # 测试用例1：正常情况，不存在桥接词
#     assert textgraph.query_bridge_words("carefully", "wrote") == 'No bridge words from "carefully" to "wrote"!' 


# def test_queryBridgeWords_not_in_graph_1():
#     # 测试用例1：单词不在图中
#     assert textgraph.query_bridge_words("unknown", "the") == 'No "unknown" in the graph!'


# def test_queryBridgeWords_not_in_graph_2():
#     # 测试用例2：单词不在图中
#     assert textgraph.query_bridge_words("the", "unknown") == 'No "unknown" in the graph!'


# def test_queryBridgeWords_not_in_graph_3():
#     # 测试用例3：单词不在图中
#     assert textgraph.query_bridge_words("unknown", "unknown") == 'No "unknown" and "unknown" in the graph'
