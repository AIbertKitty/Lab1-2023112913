import sys
class TextGraph:
    def __init__(self, text: str, output_dir: str = "output"):
        '''
        text - text file 
        output_dir - graph enc page rank  
        length - num of word
        wordSet - set of word
        wordEnc - dict of word to encoding val
        encWord - dict of encoding val to word  
        graph - connnect of the encs 
        nodeB - B -> node - enc 
        L - L(v) - enc 
        tf - freq of word 
        注： 函数采取小写下划线命名 
        '''
        import os
        self.text = text.lower()
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        length, wordSet, wordEnc, encWord, graph, nodeB, Lv, tf = self._text_to_graph()
        self.length = length
        self.wordSet = wordSet
        self.wordEnc = wordEnc
        self.encWord = encWord
        self.graph = graph
        self.nodeB = nodeB
        self.Lv = Lv
        self.tf = tf
        self.pr = [None] * self.length
        for word in self.wordSet:
            self.pr[self.wordEnc[word]] = self.tf[word]

    def _text_to_graph(self):
        import re
        text = self.text
        sentence = re.split(r'[^\w\s]+', text)
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
        wordSet = set(words)
        length = len(wordSet)
        idx = 0
        wordEnc = {}
        encWord = {}
        for w in wordSet:
            wordEnc[w] = idx
            encWord[idx] = w
            idx += 1
        graph = []
        nodeB = []
        Lv = [0] * length
        for _ in range(length):
            graph.append({})
            nodeB.append(set())
        for i in range(len(words) - 1):
            node0 = words[i]
            node1 = words[i + 1]
            idx0 = wordEnc[node0]
            idx1 = wordEnc[node1]
            if idx1 not in graph[idx0]:
                graph[idx0][idx1] = 0
            graph[idx0][idx1] += 1
            nodeB[idx1].add(idx0)
            Lv[idx0] += 1
        return length, wordSet, wordEnc, encWord, graph, nodeB, Lv, tf

    def _export_basic_data(self):
        import os
        import json
        enc_word_path = os.path.join(self.output_dir, 'enc_Word.json')
        word_enc_path = os.path.join(self.output_dir, "wordEnc.json")
        graph_path = os.path.join(self.output_dir, "graph.json")
        with open(enc_word_path, "w", encoding="utf-8") as f:
            json.dump(self.encWord, f, ensure_ascii=False, indent=2)
        with open(word_enc_path, "w", encoding="utf-8") as f:
            json.dump(self.wordEnc, f, ensure_ascii=False, indent=2)
        with open(graph_path, "w", encoding="utf-8") as f:
            json.dump(self.graph, f, ensure_ascii=False, indent=2)

    def _get_top_nodes_by_degree(self, top_n: int = 50) -> list[int]:
        """
        取出入度之和前 top_n 的节点编号
        若总数不足 top_n，则全部返回

        这里的“度”采用：
        - 出度：len(graph[idx])
        - 入度：len(nodeB[idx])
        """
        degree_info = []
        for idx in range(self.length):
            out_deg = len(self.graph[idx])
            in_deg = len(self.nodeB[idx])
            total_deg = in_deg + out_deg
            degree_info.append((idx, total_deg, in_deg, out_deg))
        degree_info.sort(
            key=lambda x: (-x[1], -x[2], -x[3], self.encWord[x[0]]))
        selected = [item[0] for item in degree_info[:min(top_n, self.length)]]
        return selected

    def show_directed_graph(self, top_n: int = 100, save_name: str = "graph_top50.png"):
        '''
        全量保存图结果 
        '''
        
        self._export_basic_data()
        """
        仅绘制出入度之和前 top_n 的节点，并保存图片。
        只打印1以上的边
        不在终端打印图结构， show。
        """
        import networkx as nx
        import matplotlib.pyplot as plt
        import os
        selected_nodes = set(self._get_top_nodes_by_degree(top_n=top_n))

        G = nx.DiGraph()

        for idx in selected_nodes:
            G.add_node(idx, label=self.encWord[idx])

        for src in selected_nodes:
            for dst, weight in self.graph[src].items():
                if dst in selected_nodes:
                    G.add_edge(src, dst, weight=weight)

        if len(G.nodes) == 0:
            print("图为空，未生成图片。")
            return

        plt.figure(figsize=(20, 12))
        import math 
        kconf = math.sqrt(self.length) 
        pos = nx.spring_layout(G, k= kconf, iterations=100, seed=42)
        node_labels = {node: self.encWord[node] for node in G.nodes}
        edge_labels = {(u, v): d["weight"] for u, v, d in G.edges(data=True) if d["weight"] >= math.log10(self.length) - 1} 

        nx.draw_networkx_nodes(
            G,
            pos,
            node_color="skyblue",
            node_size=900,
            alpha=0.3
        )
        nx.draw_networkx_edges(
            G,
            pos,
            arrows=True,
            arrowstyle="->",
            arrowsize=15,
            edge_color="gray",
            width=1.2,
            alpha=0.7
        )
        nx.draw_networkx_labels(
            G,
            pos,
            labels=node_labels,
            font_size=9,
            font_family="sans-serif"
        )
        nx.draw_networkx_edge_labels(
            G,
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

    def query_bridge_words(self, word1: str, word2: str):
        word1 = word1.lower()
        word2 = word2.lower()
        if word1 not in self.wordSet and word2 not in self.wordSet:
            print(f'No "{word1}" and "{word2}" in the graph')
            return
        if word1 not in self.wordSet:
            print(f'No "{word1}" in the graph!')
            return
        if word2 not in self.wordSet:
            print(f'No "{word2}" in the graph!')
            return
        bridgeEncs = set()
        enc1 = self.wordEnc[word1]
        enc2 = self.wordEnc[word2]
        for enc in self.graph[enc1]:
            if enc2 in self.graph[enc]:
                bridgeEncs.add(enc)
        if not bridgeEncs:
            print(f'No bridge words from "{word1}" to "{word2}"!')
            return
        if len(bridgeEncs) == 1:
            e = bridgeEncs.pop()
            bridge = self.encWord[e]
            print(
                f'The bridge word from "{word1}" to "{word2}" is:"{bridge}."')
            return
        print(f'The bridge words from "{word1}" to "{word2}" are', end=':')
        while len(bridgeEncs) != 1:
            print(f'"{self.encWord[bridgeEncs.pop()]}', end='",')
        print(f"{self.encWord[bridgeEncs.pop()]}.")
        return

    def _bridge(self, word1: str, word2: str):
        word1 = word1.lower()
        word2 = word2.lower()
        import random
        if word1 not in self.wordSet and word2 not in self.wordSet:
            return None
        if word1 not in self.wordSet:
            return None
        if word2 not in self.wordSet:
            return None
        bridgeEncs = set()
        enc1 = self.wordEnc[word1]
        enc2 = self.wordEnc[word2]
        for enc in self.graph[enc1]:
            if enc2 in self.graph[enc]:
                bridgeEncs.add(enc)
        if not bridgeEncs:
            return None
        if len(bridgeEncs) == 1:
            e = bridgeEncs.pop()
            bridge = self.encWord[e]
            return bridge
        bridgeEncs = list(bridgeEncs)
        bridgeEncs = random.sample(bridgeEncs, len(bridgeEncs))
        return self.encWord[bridgeEncs.pop()] 

    def generate_new_text(self, newText: str):
        newText = newText.lower()
        import re
        sentence = re.split(r'[^\w\s]+', newText)
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
        import heapq
        if len(inputwords) == 1:

            word = inputwords[0]
            word = word.lower()
            enc = self.wordEnc[word]
            dist = [float('inf')] * self.length
            dist[enc] = 0
            pre = [enc] * self.length
            pq = [(0, enc)]
            while pq:
                minDis, cur = heapq.heappop(pq)
                for i in range(self.length):
                    if dist[i] <= minDis or i not in self.graph[cur]:
                        continue
                    d = minDis + self.graph[cur][i]
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
                    path.append(self.encWord[curr])
                    if curr == enc:
                        break
                    curr = pre[curr]
                print(" -> ".join(reversed(path)))
        else:
            word1, word2 = inputwords[0], inputwords[1]
            word1, word2 = word1.lower(), word2.lower()
            enc1 = self.wordEnc[word1]
            enc2 = self.wordEnc[word2]
            src = enc1
            dst = enc2
            dist = [float('inf')] * self.length
            dist[src] = 0
            pre = [src] * self.length
            pq = [(0, src)]
            while pq:
                minDis, cur = heapq.heappop(pq)
                if cur == dst:
                    break
                for i in range(self.length):
                    if dist[i] <= minDis or i not in self.graph[cur]:
                        continue
                    d = minDis + self.graph[cur][i]
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
                path.append(self.encWord[curr])
                if curr == src:
                    break
                curr = pre[curr]
            print(" -> ".join(reversed(path)))

    def cal_page_rank(self, d=0.85, iter=100, top_n: int = 25):
        import json
        import os
        conf = (1 - d) / self.length
        dLv = []
        for l in self.Lv:
            if l:
                dLv.append(d / l)
            else:
                '''
                l = 0, l = length 
                '''

                dLv.append(d / self.length)
        for _ in range(iter):
            for u in range(self.length):
                self.pr[u] = conf
                for v in self.nodeB[u]:
                    self.pr[u] += dLv[v] * self.pr[v]
        '''
        optim - only show top 20 
        '''
        ranked = [(idx, self.encWord[idx], self.pr[idx])
                  for idx in range(self.length)]
        ranked.sort(key=lambda x: (-x[2], x[1]))
        print(f"Top {min(top_n, self.length)} PageRank:")
        for idx, word, score in ranked[:min(top_n, self.length)]:
            print(f"{word}: {score}")
        # 保存全量 PageRank
        pr_path = os.path.join(self.output_dir, "page_rank.json")
        pr_dump = {
            str(idx): {
                "word": self.encWord[idx],
                "page_rank": self.pr[idx]
            }
            for idx in range(self.length)
        }
        with open(pr_path, "w", encoding="utf-8") as f:
            json.dump(pr_dump, f, ensure_ascii=False, indent=2)

    def random_walk(self):
        import random
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
        file = ' '.join(self.encWord[p] for p in path) + '\n'
        print(file)
        with open("random_travel.txt", "w", encoding='utf-8') as f:
            f.write(file)


read = sys.stdin.readline
print('input complete path, enter:')
dest = read().rstrip()
with open(dest, 'r', encoding='utf-8') as f:
    text = f.read()
textgraph = TextGraph(text)
textgraph.show_directed_graph()
print('close the picture to continue')
print('input 2 words to query, enter:')
word1, word2 = read().split()
textgraph.query_bridge_words(word1, word2)
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