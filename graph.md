```mermaid
graph TD
    A[开始: 输入 startNode, endNode] --> B[初始化: dist 字典所有键为 ∞, pre 字典为空]
    B --> C[设置 dist[startNode] = 0]
    C --> D[创建未访问集合 Q, 包含图中所有节点]
    D --> E{Q 是否为空?}
    E -- 否 --> F[从 Q 中寻找 dist 最小的节点 u]
    F --> G{dist[u] == ∞ ?}
    G -- 是 --> H[剩余节点不可达, 跳出循环]
    G -- 否 --> I[从 Q 中移除 u]
    I --> J[遍历 u 的每一个邻居 v]
    J --> K[计算 newDist = dist[u] + weight(u, v)]
    K --> L{newDist < dist[v]?}
    L -- 是 --> M[更新 dist[v] = newDist, pre[v] = u]
    L -- 否 --> N[保持不变]
    M --> O{邻居遍历完?}
    N --> O
    O -- 否 --> J
    O -- 是 --> E
    E -- 是 --> P{用户是否输入了 endNode?}
    P -- 是 --> Q{dist[endNode] == ∞?}
    Q -- 是 --> R[提示: 两词之间不可达]
    Q -- 否 --> S[根据 pre 字典从 endNode 回溯至 startNode, 得到路径]
    P -- 否 --> T[遍历 dist 字典, 输出 startNode 到所有 dist < ∞ 节点的路径]
    S --> U[输出路径及总权重]
    T --> U
    U --> V[结束]
```