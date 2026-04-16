N1：函数开始，输入 word_1, word_2
N2：word_1 = word_1.lower(); word_2 = word_2.lower()
N3：判断 word_1 not in self.word_set and word_2 not in self.word_set
N4：返回 No "word1" and "word2" in the graph
N5：判断 word_1 not in self.word_set
N6：返回 No "word1" in the graph!
N7：判断 word_2 not in self.word_set
N8：返回 No "word2" in the graph!
N9：初始化 bridge_encs、enc1、enc2
N10：循环 for enc in self.graph[enc1]
N11：判断 if enc2 in self.graph[enc]
N12：bridge_encs.add(enc)
N13：判断 if not bridge_encs
N14：返回 No bridge words from ...
N15：返回桥接词结果（虽然你发来的代码后半段被截断了，但逻辑上必然有“返回桥接词字符串”这一出口）


N1 → N2 → N3
N3 为真 → N4
N3 为假 → N5
N5 为真 → N6
N5 为假 → N7
N7 为真 → N8
N7 为假 → N9 → N10
N10 进入循环体 → N11
N11 为真 → N12 → 回到 N10
N11 为假 → 回到 N10
循环结束 → N13
N13 为真 → N14
N13 为假 → N15



开始
  ↓
转小写
  ↓
word1和word2都不在图中？
  ├─是→ 返回“两个词都不在图中”
  └─否
      ↓
word1不在图中？
  ├─是→ 返回“word1不在图中”
  └─否
      ↓
word2不在图中？
  ├─是→ 返回“word2不在图中”
  └─否
      ↓
遍历word1的所有后继节点
      ↓
某后继节点是否能到word2？
  ├─是→ 加入桥接词集合
  └─否→ 继续遍历
      ↓
桥接词集合为空？
  ├─是→ 返回“没有桥接词”
  └─否→ 返回桥接词结果

圈复杂度公式：

V(G)=判定节点数+1

在这个函数里，判定节点有：

if word_1 not in self.word_set and word_2 not in self.word_set
if word_1 not in self.word_set
if word_2 not in self.word_set
for enc in self.graph[enc1]
if enc2 in self.graph[enc]
if not bridge_encs
所以判定节点数 = 6

V(G)=6+1=7

这个函数理论上需要设计 7 条基本独立路径。

对 query_bridge_words() 进行控制流分析后，该函数包含 6 个判定节点，因此其圈复杂度为 7。这说明至少需要设计 7 条独立路径，才能较充分覆盖该函数的主要逻辑分支。

路径 P1：两个词都不在图中
N1 → N2 → N3(True) → N4
路径 P2：只有第一个词不在图中
N1 → N2 → N3(False) → N5(True) → N6
路径 P3：只有第二个词不在图中
N1 → N2 → N3(False) → N5(False) → N7(True) → N8
路径 P4：两个词都在图中，但 word_1 没有后继节点/循环不进入有效桥接
N1 → N2 → N3(False) → N5(False) → N7(False) → N9 → N10(结束) → N13(True) → N14
路径 P5：循环进入，但每次 if enc2 in self.graph[enc] 都为假
N1 → N2 → N3(False) → N5(False) → N7(False) → N9 → N10 → N11(False) → N10 → ... → N13(True) → N14
路径 P6：循环中至少一次命中桥接词
N1 → N2 → N3(False) → N5(False) → N7(False) → N9 → N10 → N11(True) → N12 → N10 → N13(False) → N15
路径 P7：多个后继，既有不命中也有命中
N1 → N2 → N3(False) → N5(False) → N7(False) → N9 → N10 → N11(False) → N10 → N11(True) → N12 → N10 → N13(False) → N15

case:

a b c
a d c
f g h
a e

那么：

query_bridge_words("a", "c") 的桥接词应为 b 和 d
query_bridge_words("a", "e") 不一定有桥接词，因为需要找的是 a -> x -> e
query_bridge_words("b", "c") 没有桥接词，因为是直连，不是中间隔一个词
query_bridge_words("x", "y") 两个词都不存在
这个文本非常适合白盒测试。

word_1 = "x"
word_2 = "y"

'No "x" and "y" in the graph'

word_1 = "x"
word_2 = "c"

'No "x" in the graph!'

word_1 = "a"
word_2 = "y"

'No "y" in the graph!'

word_1 = "b"
word_2 = "c"

'No bridge words from "b" to "c"!'



word_1 = "f"
word_2 = "h" 

'The bridge words from "f" to "h" is: g.'

word_1 = "a"
word_2 = "c"

'The bridge words from "a" to "c" are: "b","d".'
'The bridge words from "a" to "c" are: "d","b".'