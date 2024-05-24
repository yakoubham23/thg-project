class KruskalMax:
    def __init__(self, vertices):
        self.vertices = vertices
        self.parent = {}
        self.rank = {}

    def find(self, vertex):
        if self.parent[vertex] != vertex:
            self.parent[vertex] = self.find(self.parent[vertex])
        return self.parent[vertex]

    def union(self, root1, root2):
        if self.rank[root1] > self.rank[root2]:
            self.parent[root2] = root1
        else:
            self.parent[root1] = root2
            if self.rank[root1] == self.rank[root2]:
                self.rank[root2] += 1

    def kruskal_max(self, edges):
        mst = []
        for vertex in self.vertices:
            self.parent[vertex] = vertex
            self.rank[vertex] = 0

        edges.sort(key=lambda x: -x[2])  # Sort edges in descending order
        
        for edge in edges:
            vertex1, vertex2, weight = edge
            root1 = self.find(vertex1)
            root2 = self.find(vertex2)

            if root1 != root2:
                self.union(root1, root2)
                mst.append(edge)
        
        return mst
