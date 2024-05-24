class PrimMax:
    def __init__(self, vertices):
        self.vertices = vertices
        self.edges = {}

    def add_edge(self, u, v, weight):
        if u not in self.edges:
            self.edges[u] = []
        if v not in self.edges:
            self.edges[v] = []
        self.edges[u].append((v, weight))
        self.edges[v].append((u, weight))

    def prim_max(self, start_vertex):
        mst = []
        visited = {start_vertex}
        edges = [(weight, start_vertex, v) for v, weight in self.edges[start_vertex]]

        while edges:
            weight, u, v = max(edges)
            edges.remove((weight, u, v))
            if v not in visited:
                visited.add(v)
                mst.append((u, v, weight))
                for to_vertex, to_weight in self.edges[v]:
                    if to_vertex not in visited:
                        edges.append((to_weight, v, to_vertex))
        
        return mst
