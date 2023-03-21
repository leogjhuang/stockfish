SHELLS = 0
SNOWBALL = 1
WASABI = 2
PIZZA = 3


class Graph:
    def __init__(self, n):
        self.n = n
        self.edges = [[] for _ in range(n)]

    def add_edge(self, u, v, w, x):
        self.edges[u].append((v, w))
        self.edges[v].append((u, x))

    def dfs(self, u, count, profit=1.0, max_count=5):
        if count == max_count:
            return profit
        if count + 1 == max_count:
            for v, w in self.edges[u]:
                if v == SHELLS:
                    return profit * w
        for v, w in self.edges[u]:
            profit = max(profit, w * self.dfs(v, count + 1))
        return profit

    def bfs(self, u, count, profit=1.0, max_count=5):
        queue = []
        for v, w in self.edges[u]:
            pass


graph = Graph(4)
graph.add_edge(SHELLS, SNOWBALL, 1.98, 0.48)
graph.add_edge(SHELLS, WASABI, 0.64, 1.49)
graph.add_edge(SHELLS, PIZZA, 1.34, 0.75)
graph.add_edge(SNOWBALL, WASABI, 0.31, 3.1)
graph.add_edge(SNOWBALL, PIZZA, 0.67, 1.45)
graph.add_edge(WASABI, PIZZA, 1.95, 0.5)
print(graph.dfs(SHELLS, 0))
