import tkinter as tk
from tkinter import simpledialog, filedialog as fd
import json

class GraphApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Graph Editor")

        self.canvas = tk.Canvas(self.root, width=800, height=600, bg="white")
        self.canvas.pack()

        self.vertices = []
        self.edges = []
        self.selected_vertex = None
        self.temp_line = None

        self.add_vertex_mode = False
        self.add_edge_mode = False
        self.move_vertex_mode = False

        self.create_ui()

    def create_ui(self):
        self.btn_add_vertex = tk.Button(self.root, text="Ajouter un sommet", command=self.on_add_vertex)
        self.btn_add_vertex.pack(side=tk.LEFT)

        self.btn_remove_vertex = tk.Button(self.root, text="Supprimer un sommet", command=self.on_remove_vertex)
        self.btn_remove_vertex.pack(side=tk.LEFT)

        self.btn_add_edge = tk.Button(self.root, text="Ajouter une arête", command=self.on_add_edge)
        self.btn_add_edge.pack(side=tk.LEFT)

        self.btn_remove_edge = tk.Button(self.root, text="Supprimer une arête", command=self.on_remove_edge)
        self.btn_remove_edge.pack(side=tk.LEFT)

        self.btn_modify_edge = tk.Button(self.root, text="Modifier une arête", command=self.modify_edge)
        self.btn_modify_edge.pack(side=tk.LEFT)

        self.btn_move_vertex = tk.Button(self.root, text="Déplacer un sommet", command=self.on_move_vertex)
        self.btn_move_vertex.pack(side=tk.LEFT)

        self.btn_save = tk.Button(self.root, text="Sauvegarder", command=self.save_graph)
        self.btn_save.pack(side=tk.LEFT)

        self.btn_load = tk.Button(self.root, text="Charger", command=self.load_graph)
        self.btn_load.pack(side=tk.LEFT)

        self.btn_back = tk.Button(self.root, text="Réinitialiser", command=self.reset_graph)
        self.btn_back.pack(side=tk.LEFT)

    def reset_modes(self):
        self.add_vertex_mode = False
        self.add_edge_mode = False
        self.move_vertex_mode = False
        self.selected_vertex = None
        self.temp_line = None
        self.canvas.bind("<Button-1>", lambda event: None)
        self.canvas.unbind("<Motion>")
        self.canvas.unbind("<B1-Motion>")
        self.canvas.unbind("<ButtonRelease-1>")

    def on_add_vertex(self):
        self.reset_modes()
        self.add_vertex_mode = True
        self.canvas.bind("<Button-1>", self.add_vertex)

    def add_vertex(self, event):
        vertex_id = len(self.vertices) + 1
        self.vertices.append((event.x, event.y, vertex_id))
        self.canvas.create_oval(event.x - 20, event.y - 20, event.x + 20, event.y + 20, fill="white", outline="black", tags=f"vertex_{vertex_id}")
        self.canvas.create_text(event.x, event.y, text=str(vertex_id), tags=f"text_{vertex_id}")

    def on_remove_vertex(self):
        self.reset_modes()
        self.canvas.bind("<Button-1>", self.remove_vertex)

    def remove_vertex(self, event):
        vertex = self.get_vertex_at(event.x, event.y)
        if vertex:
            vertex_id = vertex[2]
            self.canvas.delete(f"vertex_{vertex_id}")
            self.canvas.delete(f"text_{vertex_id}")
            self.vertices.remove(vertex)
            edges_to_remove = [edge for edge in self.edges if edge[0][2] == vertex_id or edge[1][2] == vertex_id]
            for edge in edges_to_remove:
                start, end, _ = edge
                self.canvas.delete(f"edge_{start[2]}_{end[2]}")
                if edge[2] is not None:
                    self.canvas.delete(f"weight_{start[2]}_{end[2]}")
                self.edges.remove(edge)

    def on_add_edge(self):
        self.reset_modes()
        self.add_edge_mode = True
        self.canvas.bind("<Button-1>", self.start_edge)

    def start_edge(self, event):
        vertex = self.get_vertex_at(event.x, event.y)
        if vertex:
            if not self.selected_vertex:
                self.selected_vertex = vertex
                self.temp_line = self.canvas.create_line(event.x, event.y, event.x, event.y, fill="black")
                self.canvas.bind("<Motion>", self.temp_line_motion)
                self.canvas.bind("<Button-1>", self.end_edge)
            else:
                self.end_edge(event)

    def temp_line_motion(self, event):
        self.canvas.coords(self.temp_line, self.selected_vertex[0], self.selected_vertex[1], event.x, event.y)

    def end_edge(self, event):
        vertex = self.get_vertex_at(event.x, event.y)
        if vertex:
            start = self.selected_vertex
            end = vertex
            weight = self.prompt_for_weight()
            self.edges.append((start, end, weight))
            if start[2] == end[2]:
                loop_radius = 20
                self.canvas.create_oval(start[0] - loop_radius, start[1] - loop_radius, start[0] + loop_radius, start[1] + loop_radius, outline="black", width=2, tags=f"edge_{start[2]}_{end[2]}")
                mid_x, mid_y = start[0] + loop_radius, start[1] - loop_radius
            else:
                self.canvas.create_line(start[0], start[1], end[0], end[1], tags=f"edge_{start[2]}_{end[2]}", width=2)
                mid_x = (start[0] + end[0]) / 2
                mid_y = (start[1] + end[1]) / 2
            if weight is not None:
                self.canvas.create_text(mid_x, mid_y, text=str(weight), fill="black", tags=f"weight_{start[2]}_{end[2]}")
        self.canvas.delete(self.temp_line)
        self.selected_vertex = None
        self.temp_line = None
        self.canvas.bind("<Button-1>", self.start_edge)
        self.canvas.unbind("<Motion>")

    def on_remove_edge(self):
        self.reset_modes()
        self.canvas.bind("<Button-1>", self.remove_edge)

    def remove_edge(self, event):
        edge = self.get_edge_at(event.x, event.y)
        if edge:
            start, end, weight = edge
            self.canvas.delete(f"edge_{start[2]}_{end[2]}")
            if weight is not None:
                self.canvas.delete(f"weight_{start[2]}_{end[2]}")
            self.edges.remove(edge)

    def get_vertex_at(self, x, y):
        for vertex in self.vertices:
            vx, vy, vid = vertex
            if (vx - x) ** 2 + (vy - y) ** 2 <= 20 ** 2:
                return vertex
        return None

    def get_edge_at(self, x, y):
        for edge in self.edges:
            start, end, _ = edge
            x0, y0, _ = start
            x1, y1, _ = end
            if self.is_point_near_line(x, y, x0, y0, x1, y1):
                return edge
        return None

    def is_point_near_line(self, px, py, x0, y0, x1, y1, tolerance=10):
        if x0 == x1:
            return abs(px - x0) <= tolerance and min(y0, y1) <= py <= max(y0, y1)
        elif y0 == y1:
            return abs(py - y0) <= tolerance and min(x0, x1) <= px <= max(x0, x1)
        else:
            slope = (y1 - y0) / (x1 - x0)
            intercept = y0 - slope * x0
            expected_y = slope * px + intercept
            return abs(py - expected_y) <= tolerance and min(x0, x1) <= px <= max(x0, x1)

    def modify_edge(self):
        self.reset_modes()
        self.canvas.bind("<Button-1>", self.modify_edge_weight)

    def modify_edge_weight(self, event):
        edge = self.get_edge_at(event.x, event.y)
        if edge:
            start, end, _ = edge
            new_weight = self.prompt_for_weight()
            if new_weight is not None:
                edge_index = self.edges.index(edge)
                self.edges[edge_index] = (start, end, new_weight)
                if start[2] == end[2]:
                    mid_x, mid_y = start[0] + 20, start[1] - 20
                else:
                    mid_x = (start[0] + end[0]) / 2
                    mid_y = (start[1] + end[1]) / 2
                self.canvas.delete(f"weight_{start[2]}_{end[2]}")
                self.canvas.create_text(mid_x, mid_y, text=str(new_weight), fill="black", tags=f"weight_{start[2]}_{end[2]}")

    def on_move_vertex(self):
        self.reset_modes()
        self.move_vertex_mode = True
        self.canvas.bind("<Button-1>", self.start_moving_vertex)

    def start_moving_vertex(self, event):
        vertex = self.get_vertex_at(event.x, event.y)
        if vertex:
            self.selected_vertex = vertex
            self.canvas.bind("<B1-Motion>", self.move_vertex)
            self.canvas.bind("<ButtonRelease-1>", self.stop_moving_vertex)

    def move_vertex(self, event):
        if self.selected_vertex:
            dx = event.x - self.selected_vertex[0]
            dy = event.y - self.selected_vertex[1]
            self.selected_vertex = (event.x, event.y, self.selected_vertex[2])
            self.canvas.coords(f"vertex_{self.selected_vertex[2]}", event.x - 20, event.y - 20, event.x + 20, event.y + 20)
            self.canvas.coords(f"text_{self.selected_vertex[2]}", event.x, event.y)
            for edge in self.edges:
                start, end, weight = edge
                if start[2] == self.selected_vertex[2]:
                    self.canvas.coords(f"edge_{start[2]}_{end[2]}", event.x, event.y, end[0], end[1])
                    if weight is not None:
                        self.canvas.coords(f"weight_{start[2]}_{end[2]}", (event.x + end[0]) / 2, (event.y + end[1]) / 2)
                elif end[2] == self.selected_vertex[2]:
                    self.canvas.coords(f"edge_{start[2]}_{end[2]}", start[0], start[1], event.x, event.y)
                    if weight is not None:
                        self.canvas.coords(f"weight_{start[2]}_{end[2]}", (start[0] + event.x) / 2, (start[1] + event.y) / 2)

    def stop_moving_vertex(self, event):
        self.canvas.unbind("<B1-Motion>")
        self.canvas.unbind("<ButtonRelease-1>")
        self.selected_vertex = None

    def prompt_for_weight(self):
        weight = simpledialog.askstring("Poids de l'arête", "Entrez le poids de l'arête (ou laissez vide pour aucune):")
        return weight if weight else None

    def save_graph(self):
        graph_data = {
            "vertices": self.vertices,
            "edges": self.edges
        }
        file_path = fd.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if file_path:
            with open(file_path, 'w') as f:
                json.dump(graph_data, f)

    def load_graph(self):
        file_path = fd.askopenfilename(filetypes=[("JSON files", "*.json")])
        if file_path:
            with open(file_path, 'r') as f:
                graph_data = json.load(f)
            self.reset_graph()
            self.vertices = graph_data["vertices"]
            self.edges = graph_data["edges"]
            for vertex in self.vertices:
                x, y, vertex_id = vertex
                self.canvas.create_oval(x - 20, y - 20, x + 20, y + 20, fill="white", outline="black", tags=f"vertex_{vertex_id}")
                self.canvas.create_text(x, y, text=str(vertex_id), tags=f"text_{vertex_id}")
            for edge in self.edges:
                start, end, weight = edge
                if start[2] == end[2]:
                    loop_radius = 20
                    self.canvas.create_oval(start[0] - loop_radius, start[1] - loop_radius, start[0] + loop_radius, start[1] + loop_radius, outline="black", width=2, tags=f"edge_{start[2]}_{end[2]}")
                    mid_x, mid_y = start[0] + loop_radius, start[1] - loop_radius
                else:
                    self.canvas.create_line(start[0], start[1], end[0], end[1], tags=f"edge_{start[2]}_{end[2]}", width=2)
                    mid_x = (start[0] + end[0]) / 2
                    mid_y = (start[1] + end[1]) / 2
                if weight is not None:
                    self.canvas.create_text(mid_x, mid_y, text=str(weight), fill="black", tags=f"weight_{start[2]}_{end[2]}")

    def reset_graph(self):
        self.canvas.delete("all")
        self.vertices = []
        self.edges = []

    def go_back_to_initial(self):
        self.reset_graph()
        self.reset_modes()

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = GraphApp()
    app.run()


