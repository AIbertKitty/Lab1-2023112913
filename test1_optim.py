"""
软件工程 Lab3 实验代码
该模块实现了基于文本的单词有向图构建，
包含桥接词查询、最短路径计算以及随机游走等功能。
"""
import sys
import random
import os
import json
import math
import re
import heapq

import networkx as nx
import matplotlib.pyplot as plt


class TextGraph:

    '''
    这是一个用于表示单词有向图的类。
    用于存储文本解析后的节点（单词）和边（相邻关系及权重），
    并提供图的基础构建功能。
    '''
    # pylint: disable=too-many-instance-attributes

    def __init__(self, text_f: str, output_dir: str = "output"):
        '''
        text_f - text file 
        output_dir - graph enc page rank  
        length - num of word
        word_set - set of word
        word_enc - dict of word to encoding val
        enc_word - dict of encoding val to word  
        graph - connnect of the encs 
        node_b - B -> node - enc 
        L - L(v) - enc 
        tf - freq of word 
        注： 函数采取小写下划线命名 
        '''

        self.text = text_f.lower()
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        length, word_set, word_enc, enc_word, graph, node_b, l_v, tf = self._text_to_graph()
        self.length = length
        self.word_set = word_set
        self.word_enc = word_enc
        self.enc_word = enc_word
        self.graph = graph
        self.node_b = node_b
        self.l_v = l_v
        self.tf = tf
        self.pr = [None] * self.length
        for word in self.word_set:
            self.pr[self.word_enc[word]] = self.tf[word]

    def _text_to_graph(self):
        # pylint: disable=too-many-locals
        text_f = self.text
        sentence = re.split(r'[^\w\s]+', text_f)
        sentence = [s for s in sentence if s]
        words = []
        tf = {}
        for s in sentence:
            s = s.split()
            for w in s:
                words.append(w)
                if w not in tf:
                    tf[w] = 0
                tf[w] += 1
        word_set = set(words)
        length = len(word_set)
        idx = 0
        word_enc = {}
        enc_word = {}
        for w in word_set:
            word_enc[w] = idx
            enc_word[idx] = w
            idx += 1
        graph = []
        node_b = []
        l_v = [0] * length
        for _ in range(length):
            graph.append({})
            node_b.append(set())
        for i in range(len(words) - 1):
            node0 = words[i]
            node1 = words[i + 1]
            idx0 = word_enc[node0]
            idx1 = word_enc[node1]
            if idx1 not in graph[idx0]:
                graph[idx0][idx1] = 0
            graph[idx0][idx1] += 1
            node_b[idx1].add(idx0)
            l_v[idx0] += 1
        return length, word_set, word_enc, enc_word, graph, node_b, l_v, tf

    def _export_basic_data(self):

        enc_word_path = os.path.join(self.output_dir, 'enc_Word.json')
        word_enc_path = os.path.join(self.output_dir, "word_enc.json")
        graph_path = os.path.join(self.output_dir, "graph.json")
        with open(enc_word_path, "w", encoding="utf-8") as file_f:
            json.dump(self.enc_word, file_f, ensure_ascii=False, indent=2)
        with open(word_enc_path, "w", encoding="utf-8") as file_f:
            json.dump(self.word_enc, file_f, ensure_ascii=False, indent=2)
        with open(graph_path, "w", encoding="utf-8") as file_f:
            json.dump(self.graph, file_f, ensure_ascii=False, indent=2)

    def _get_top_nodes_by_degree(self, top_n: int = 50) -> list[int]:
        """
        取出入度之和前 top_n 的节点编号
        若总数不足 top_n，则全部返回

        这里的“度”采用：
        - 出度：len(graph[idx])
        - 入度：len(node_b[idx])
        """
        degree_info = []
        for idx in range(self.length):
            out_deg = len(self.graph[idx])
            in_deg = len(self.node_b[idx])
            total_deg = in_deg + out_deg
            degree_info.append((idx, total_deg, in_deg, out_deg))
        degree_info.sort(
            key=lambda x: (-x[1], -x[2], -x[3], self.enc_word[x[0]]))
        selected = [item[0] for item in degree_info[:min(top_n, self.length)]]
        return selected

    def show_directed_graph(self, top_n: int = 100, save_name: str = "graph_top50.png"):
        '''
        全量保存图结果
        '''

        self._export_basic_data()

        selected_nodes = set(self._get_top_nodes_by_degree(top_n=top_n))

        g = nx.DiGraph()

        for idx in selected_nodes:
            g.add_node(idx, label=self.enc_word[idx])

        for src in selected_nodes:
            for dst, weight in self.graph[src].items():
                if dst in selected_nodes:
                    g.add_edge(src, dst, weight=weight)

        if len(g.nodes) == 0:
            print("图为空，未生成图片。")
            return

        plt.figure(figsize=(20, 12))

        kconf = math.sqrt(self.length)
        pos = nx.spring_layout(g, k=kconf, iterations=100, seed=42)
        node_labels = {node: self.enc_word[node] for node in g.nodes}
        edge_labels = {(u, v): d["weight"] for u, v, d in g.edges(
            data=True) if d["weight"] >= math.log10(self.length) - 1}

        nx.draw_networkx_nodes(
            g,
            pos,
            node_color="skyblue",
            node_size=900,
            alpha=0.3
        )
        nx.draw_networkx_edges(
            g,
            pos,
            arrows=True,
            arrowstyle="->",
            arrowsize=15,
            edge_color="gray",
            width=1.2,
            alpha=0.7
        )
        nx.draw_networkx_labels(
            g,
            pos,
            labels=node_labels,
            font_size=9,
            font_family="sans-serif"
        )
        nx.draw_networkx_edge_labels(
            g,
            pos,
            edge_labels=edge_labels,
            font_size=8
        )

        plt.title(
            f"Directed Word Graph (Top {min(top_n, self.length)} by In + Out Degree)")
        plt.axis("off")
        plt.tight_layout()

        save_path = os.path.join(self.output_dir, save_name)
        plt.savefig(save_path, dpi=300, bbox_inches="tight")
        plt.show()

    def query_bridge_words(self, word_1: str, word_2: str):
        '''
        q b w
        '''

        word_1 = word_1.lower()
        word_2 = word_2.lower()
        if word_1 not in self.word_set and word_2 not in self.word_set:
            print(f'No "{word_1}" and "{word_2}" in the graph')
            return f'No "{word_1}" and "{word_2}" in the graph'
        if word_1 not in self.word_set:
            print(f'No "{word_1}" in the graph!')
            return f'No "{word_1}" in the graph!'
        if word_2 not in self.word_set:
            print(f'No "{word_2}" in the graph!')
            return f'No "{word_2}" in the graph!'
        bridge_encs = set()
        enc1 = self.word_enc[word_1]
        enc2 = self.word_enc[word_2]
        for enc in self.graph[enc1]:
            if enc2 in self.graph[enc]:
                bridge_encs.add(enc)
        if not bridge_encs:
            print(f'No bridge words from "{word_1}" to "{word_2}"!')
            return f'No bridge words from "{word_1}" to "{word_2}"!'
        if len(bridge_encs) == 1:
            e = bridge_encs.pop()
            bridge = self.enc_word[e]
            print(
                f'The bridge word from "{word_1}" to "{word_2}" is:"{bridge}."')
            return f'The bridge word from "{word_1}" to "{word_2}" is:"{bridge}."'
        return_val = ''
        print(f'The bridge words from "{word_1}" to "{word_2}" are', end=':')
        return_val += f'The bridge words from "{word_1}" to "{word_2}" are:'
        while len(bridge_encs) != 1:
            print(f'"{self.enc_word[bridge_encs.pop()]}', end='",')
            return_val += f'"{self.enc_word[bridge_encs.pop()]}",'
        print(f"{self.enc_word[bridge_encs.pop()]}.")
        return_val += f"{self.enc_word[bridge_encs.pop()]}."
        return return_val

    def _bridge(self, word_1: str, word_2: str):
        word_1 = word_1.lower()
        word_2 = word_2.lower()

        if word_1 not in self.word_set and word_2 not in self.word_set:
            return None
        if word_1 not in self.word_set:
            return None
        if word_2 not in self.word_set:
            return None
        bridge_encs = set()
        enc1 = self.word_enc[word_1]
        enc2 = self.word_enc[word_2]
        for enc in self.graph[enc1]:
            if enc2 in self.graph[enc]:
                bridge_encs.add(enc)
        if not bridge_encs:
            return None
        if len(bridge_encs) == 1:
            e = bridge_encs.pop()
            bridge = self.enc_word[e]
            return bridge
        bridge_encs = list(bridge_encs)
        bridge_encs = random.sample(bridge_encs, len(bridge_encs))
        return self.enc_word[bridge_encs.pop()]

    def generate_new_text(self, new_text: str):
        '''
        g n t
        '''

        new_text = new_text.lower()

        sentence = re.split(r'[^\w\s]+', new_text)
        words = []
        length = 0
        for s in sentence:
            s = s.split()
            for w in s:
                words.append(w)
                words.append(None)
                length += 2
        for i in range(0, length - 2, 2):
            words[i + 1] = self._bridge(words[i], words[i + 2])
        for i in range(length - 1):
            if words[i]:
                print(words[i], end=' ')
        print()

    def calc_shortest_path(self, inputwords: list[str]):
        '''
        heap optimize djikstra 

        inputwords - list, 1 or 2 word

        include optional 1 
        '''
        # pylint: disable=too-many-locals
        # pylint: disable=too-many-branches
        # pylint: disable=too-many-statements
        if len(inputwords) == 1:

            word = inputwords[0]
            word = word.lower()
            enc = self.word_enc[word]
            dist = [float('inf')] * self.length
            dist[enc] = 0
            pre = [enc] * self.length
            pq = [(0, enc)]
            while pq:
                min_dis, cur = heapq.heappop(pq)
                for i in range(self.length):
                    if dist[i] <= min_dis or i not in self.graph[cur]:
                        continue
                    d = min_dis + self.graph[cur][i]
                    if d < dist[i]:
                        dist[i] = d
                        pre[i] = cur
                        heapq.heappush(pq, (d, i))
            for e in range(self.length):
                print(f"Distance: {dist[e]}")
                if dist[e] == float('inf'):
                    print("No path")
                    continue
                path = []
                curr = e
                while True:
                    path.append(self.enc_word[curr])
                    if curr == enc:
                        break
                    curr = pre[curr]
                print(" -> ".join(reversed(path)))
        else:
            word_1, word_2 = inputwords[0], inputwords[1]
            word_1, word_2 = word_1.lower(), word_2.lower()
            enc1 = self.word_enc[word_1]
            enc2 = self.word_enc[word_2]
            src = enc1
            dst = enc2
            dist = [float('inf')] * self.length
            dist[src] = 0
            pre = [src] * self.length
            pq = [(0, src)]
            while pq:
                min_dis, cur = heapq.heappop(pq)
                if cur == dst:
                    break
                for i in range(self.length):
                    if dist[i] <= min_dis or i not in self.graph[cur]:
                        continue
                    d = min_dis + self.graph[cur][i]
                    if d < dist[i]:
                        dist[i] = d
                        pre[i] = cur
                        heapq.heappush(pq, (d, i))
            print(f"Distance: {dist[dst]}")
            if dist[dst] == float('inf'):
                print("No path")
            path = []
            curr = dst
            while True:
                path.append(self.enc_word[curr])
                if curr == src:
                    break
                curr = pre[curr]
            print(" -> ".join(reversed(path)))

    def cal_page_rank(self, d=0.85, top_n: int = 25):
        '''
        c p r
        '''

        conf = (1 - d) / self.length
        dl_v = []
        for l in self.l_v:
            if l:
                dl_v.append(d / l)
            else:

                dl_v.append(d / self.length)
        for _ in range(100):
            for u in range(self.length):
                self.pr[u] = conf
                for v in self.node_b[u]:
                    self.pr[u] += dl_v[v] * self.pr[v]

        ranked = [(idx, self.enc_word[idx], self.pr[idx])
                  for idx in range(self.length)]
        ranked.sort(key=lambda x: (-x[2], x[1]))
        print(f"Top {min(top_n, self.length)} PageRank:")
        for idx, word, score in ranked[:min(top_n, self.length)]:
            print(f"{word}: {score}")
        # 保存全量 PageRank
        pr_path = os.path.join(self.output_dir, "page_rank.json")
        pr_dump = {
            str(idx): {
                "word": self.enc_word[idx],
                "page_rank": self.pr[idx]
            }
            for idx in range(self.length)
        }
        with open(pr_path, "w", encoding="utf-8") as f:
            json.dump(pr_dump, f, ensure_ascii=False, indent=2)

    def random_walk(self):
        '''
        r w
        '''

        src = random.randint(0, self.length - 1)
        path = [src]
        visited_edges = set()
        while True:
            candidates = [nxt for nxt in self.graph[src] if nxt != src]
            if not candidates:
                break
            nxt = random.choice(candidates)
            edge = (src, nxt)
            if edge in visited_edges:
                path.append(nxt)
                break
            visited_edges.add(edge)
            path.append(nxt)
            src = nxt
        file = ' '.join(self.enc_word[p] for p in path) + '\n'
        print(file)
        with open("random_travel.txt", "w", encoding='utf-8') as f:
            f.write(file)


read = sys.stdin.readline
print('input complete path, enter:')
dest = read().rstrip()
with open(dest, 'r', encoding='utf-8') as file_x:
    text = file_x.read()
textgraph = TextGraph(text)
textgraph.show_directed_graph()
print('close the picture to continue')
print('input 2 words to query, enter:')
word_1x, word_2x = read().split()
textgraph.query_bridge_words(word_1x, word_2x)
print('print a line to pad, enter:')
text = read().rstrip()
textgraph.generate_new_text(text)
print('print one or two words, separated by space, enter:')
target = read().split()
textgraph.calc_shortest_path(target)
print('page rank:')
textgraph.cal_page_rank()
print('random_walk:')
textgraph.random_walk()
