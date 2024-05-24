class WelchPowell:
    def __init__(self, vertices):
        self.vertices = vertices
        self.edges = {}

    def add_edge(self, u, v):
        if u not in self.edges:
            self.edges[u] = []
        if v not in self.edges:
            self.edges[v] = []
        self.edges[u].append(v)
        self.edges[v].append(u)

    def welch_powell(self):
        degree_list = sorted(self.vertices, key=lambda v: len(self.edges[v]), reverse=True)
        color = {}
        current_color = 0

        for vertex in degree_list:
            if vertex not in color:
                current_color += 1
                color[vertex] = current_color
                for neighbor in self.edges[vertex]:
                    if neighbor not in color:
                        valid_color = True
                        for adj in self.edges[neighbor]:
                            if adj in color and color[adj] == current_color:
                                valid_color = False
                                break
                        if valid_color:
                            color[neighbor] = current_color
        
        return color
