import tkinter as tk
from algorithms import Kruskal, Prim, KruskalMax, PrimMax, Dijkstra, BellmanFord, WelchPowell

class GraphApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Application de Graphes")
        self.geometry("800x600")
        self.create_widgets()
    

    def create_widgets(self):
        self.canvas = tk.Canvas(self, width=600, height=400, bg="white")
        self.canvas.pack()

        self.kruskal_button = tk.Button(self, text="Kruskal", command=self.run_kruskal)
        self.kruskal_button.pack()

        self.prim_button = tk.Button(self, text="Prim", command=self.run_prim)
        self.prim_button.pack()

        # Add buttons for other algorithms here

    def run_kruskal(self):
        vertices = ['A', 'B', 'C', 'D']
        edges = [('A', 'B', 1), ('B', 'C', 2), ('C', 'D', 3), ('A', 'C', 4)]
        kruskal = Kruskal(vertices)
        mst = kruskal.kruskal(edges)
        self.display_result(mst)

    def run_prim(self):
        vertices = ['A', 'B', 'C', 'D']
        prim = Prim(vertices)
        prim.add_edge('A', 'B', 1)
        prim.add_edge('B', 'C', 2)
        prim.add_edge('C', 'D', 3)
        prim.add_edge('A', 'C', 4)
        mst = prim.prim('A')
        self.display_result(mst)

    def display_result(self, result):
        self.canvas.delete("all")
        for edge in result:
            self.canvas.create_line(edge[0], edge[1], fill="black")

if __name__ == "__main__":
    app = GraphApp()
    app.mainloop()
