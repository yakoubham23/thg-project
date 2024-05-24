import tkinter as tk
import tkinter.filedialog as fd
import json

class GraphApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Application de Graphes")
        self.geometry("800x600")

        # Initialisation du canevas, non visible au début
        self.canvas = tk.Canvas(self, bg="white", width=800, height=600)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.vertices = []
        self.edges = []
        self.selected_vertex = None
        self.selected_edge = None
        self.is_directed = None  # Initié à None, l'utilisateur doit choisir
        self.move_vertex_mode = False
        self.add_vertex_mode = True
        self.action_stack = []
        self.redo_stack = []
        self.temp_line = None

        # Center frame
        center_frame = tk.Frame(self)
        center_frame.pack(expand=True)

        # Button to create a new graph
        self.btn_new_graph = tk.Button(center_frame, text="Nouveau Graphe", command=self.create_new_graph)
        self.btn_new_graph.pack(pady=10)

        # Button to load a graph
        self.btn_load_graph = tk.Button(center_frame, text="Charger le Graphe", command=self.load_graph)
        self.btn_load_graph.pack(pady=10)

        # Button to exit the application
        self.btn_exit = tk.Button(center_frame, text="Quitter", command=self.quit)
        self.btn_exit.pack(pady=10)
        # Boutons pour le choix du type du graphe, visibles au début
        self.btn_directed = tk.Button(self, text="Graphe orienté", command=lambda: self.init_graph(True))
        self.btn_directed.pack(side=tk.TOP, pady=(20, 10))

        self.btn_undirected = tk.Button(self, text="Graphe non orienté", command=lambda: self.init_graph(False))
        self.btn_undirected.pack(side=tk.TOP, pady=10)

        # Boutons pour ajouter des sommets et des arêtes
        self.btn_add_vertex = tk.Button(self, text="Ajouter un sommet", command=self.activate_add_vertex_mode)
        self.btn_add_vertex.pack(side=tk.TOP, padx=5, pady=5)

        self.btn_add_edge = tk.Button(self, text="Ajouter une arête", command=self.activate_add_edge_mode)
        self.btn_add_edge.pack(side=tk.TOP, padx=5, pady=5)

        # Bouton pour supprimer un sommet
        self.btn_remove_vertex = tk.Button(self, text="Supprimer un sommet", command=self.on_remove_vertex)
        self.btn_remove_vertex.pack(side=tk.TOP, padx=5, pady=5)

        # Bouton pour supprimer une arête
        self.btn_remove_edge = tk.Button(self, text="Supprimer une arête", command=self.on_remove_edge)
        self.btn_remove_edge.pack(side=tk.TOP, padx=5, pady=5)

        # Bouton pour réinitialiser le graphe
        self.btn_reset_graph = tk.Button(self, text="Réinitialiser le graphe", command=self.reset_graph)
        self.btn_reset_graph.pack(side=tk.TOP, padx=5, pady=5)

        # Bouton pour déplacer un sommet
        self.btn_move_vertex = tk.Button(self, text="Déplacer un sommet", command=self.toggle_move_vertex_mode)
        self.btn_move_vertex.pack(side=tk.TOP, padx=5, pady=5)

        # Bouton pour annuler/refaire
        self.btn_undo = tk.Button(self, text="Undo", command=self.undo)
        self.btn_undo.pack(side=tk.TOP, padx=5, pady=5)

        self.btn_redo = tk.Button(self, text="Redo", command=self.redo)
        self.btn_redo.pack(side=tk.TOP, padx=5, pady=5)

        # Save and Load buttons
        self.btn_save_graph = tk.Button(self, text="Enregistrer le Graphe", command=self.save_graph)
        self.btn_save_graph.pack(side=tk.TOP, padx=5, pady=5)

        self.btn_load_graph = tk.Button(self, text="Charger le Graphe", command=self.load_graph)
        self.btn_load_graph.pack(side=tk.TOP, padx=5, pady=5)

    # Additional buttons for graph manipulation can be added below

    def create_new_graph(self):
        # Implement the logic to create a new graph here
        pass

    def load_graph(self):
        # Implement the logic to load a graph here
        pass
    def init_graph(self, is_directed):
        self.is_directed = is_directed

        # Retirer les boutons du choix de graphe
        self.btn_directed.pack_forget()
        self.btn_undirected.pack_forget()

        # Afficher le canevas et activer la création de sommets et d'arêtes
        self.canvas.bind("<Button-1>", self.canvas_click)
        self.canvas.bind("<B1-Motion>", self.canvas_drag)
        self.canvas.bind("<ButtonRelease-1>", self.canvas_release)

    def canvas_click(self, event):
        if self.move_vertex_mode:
            self.select_vertex(event.x, event.y)
        elif self.add_vertex_mode:
            clicked_vertex = self.get_vertex_at(event.x, event.y)
            if not clicked_vertex:
                self.create_vertex(event.x, event.y)
        elif self.add_edge_mode:  # Check if in add edge mode
            clicked_vertex = self.get_vertex_at(event.x, event.y)
            if clicked_vertex:
                self.selected_vertex = clicked_vertex  # Select the clicked vertex
                self.start_edge_x = event.x  # Store the x coordinate of the click
                self.start_edge_y = event.y  # Store the y coordinate of the click

    def canvas_drag(self, event):
        if self.move_vertex_mode and self.selected_vertex:
            self.move_vertex(event.x, event.y)
        elif self.add_edge_mode and self.selected_vertex:
            self.canvas.delete("temp_edge")  # Remove previous temporary edge
            # Draw a temporary edge from the selected vertex to the current mouse position
            self.canvas.create_line(self.selected_vertex[0], self.selected_vertex[1], event.x, event.y,tags="temp_edge", fill="gray", width=2)

    def canvas_release(self, event):
        if self.move_vertex_mode:
            self.selected_vertex = None

    def create_vertex(self, x, y):
        vertex_id = len(self.vertices) + 1
        vertex = (x, y, vertex_id)
        self.vertices.append(vertex)
        self.canvas.create_oval(x - 10, y - 10, x + 10, y + 10, fill="white", outline="black", tags=f"vertex_{vertex_id}")
        self.canvas.create_text(x, y, text=str(vertex_id), fill="black", tags=f"vertex_{vertex_id}")
        self.action_stack.append(("create_vertex", vertex))

    def create_edge(self, start, end, weight=None):
        x0, y0, _ = start
        x1, y1, _ = end
        if self.is_directed: 
            edge = self.canvas.create_line(x0, y0, x1, y1, arrow=tk.LAST, tags=f"edge_{start[2]}_{end[2]}", width=2)
        else:
            edge = self.canvas.create_line(x0, y0, x1, y1, tags=f"edge_{start[2]}_{end[2]}", width=2)
        self.edges.append((start, end, weight))
        if weight is not None:
            mid_x = (x0 + x1) / 2
            mid_y = (y0 + y1) / 2
            self.canvas.create_text(mid_x, mid_y, text=str(weight), fill="black", tags=f"weight_{start[2]}_{end[2]}")
        self.action_stack.append(("create_edge", (start, end, weight)))

    def get_vertex_at(self, x, y):
        for vertex in self.vertices:
            vx, vy, _ = vertex
            if (x - vx) ** 2 + (y - vy) ** 2 <= 100:
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
        """Check if a point (px, py) is near a line segment from (x0, y0) to (x1, y1)."""
        if x0 == x1:
            return abs(px - x0) <= tolerance and min(y0, y1) <= py <= max(y0, y1)
        elif y0 == y1:
            return abs(py - y0) <= tolerance and min(x0, x1) <= px <= max(x0, x1)
        else:
            slope = (y1 - y0) / (x1 - x0)
            intercept = y0 - slope * x0
            expected_y = slope * px + intercept
            return abs(py - expected_y) <= tolerance and min(x0, x1) <= px <= max(x0, x1)

    def select_edge(self, edge):
        self.selected_edge = edge
        self.canvas.itemconfig(self.get_edge_tag(edge), fill="red")

    def get_edge_tag(self, edge):
        start, end, _ = edge
        return f"edge_{start[2]}_{end[2]}"

    def on_remove_vertex(self):
        if self.selected_vertex:
            self.remove_vertex(self.selected_vertex)
            self.selected_vertex = None

    def remove_vertex(self, vertex):
        vertex_id = vertex[2]
        self.canvas.delete(f"vertex_{vertex_id}")
        self.vertices.remove(vertex)
        self.edges = [edge for edge in self.edges if vertex not in edge]
        self.redraw_edges()
        self.action_stack.append(("remove_vertex", vertex))

    def activate_add_vertex_mode(self):
        self.add_vertex_mode = True
        self.move_vertex_mode = False

    def on_remove_edge(self):
        if self.selected_edge:
            self.remove_edge(self.selected_edge)
            self.selected_edge = None
    def remove_edge(self, edge):
        start, end, weight = edge
        self.canvas.delete(self.get_edge_tag(edge))
        self.edges.remove(edge)
        self.canvas.delete(f"weight_{start[2]}_{end[2]}")
        self.action_stack.append(("remove_edge", edge))

    def reset_graph(self):
        self.canvas.delete("all")
        self.vertices = []
        self.edges = []
        self.selected_vertex = None
        self.selected_edge = None
        self.is_directed = None
        self.btn_directed.pack(side=tk.TOP, pady=(20, 10))
        self.btn_undirected.pack(side=tk.TOP, pady=10)
        self.action_stack = []
        self.redo_stack = []

    def toggle_move_vertex_mode(self):
        self.move_vertex_mode = not self.move_vertex_mode
        self.add_vertex_mode = False

    def undo(self):
        if self.action_stack:
            action = self.action_stack.pop()
            if action[0] == "create_vertex":
                _, vertex = action
                self.remove_vertex(vertex)
            elif action[0] == "create_edge":
                _, edge = action
                self.remove_edge(edge)
            elif action[0] == "remove_vertex":
                self.restore_vertex(*action[1])
            elif action[0] == "remove_edge":
                self.restore_edge(*action[1])

    def redo(self):
        if self.redo_stack:
            action = self.redo_stack.pop()
            if action[0] == "create_vertex":
                _, vertex = action
                self.create_vertex(*vertex)
            elif action[0] == "create_edge":
                _, edge = action
                self.create_edge(*edge)
            elif action[0] == "remove_vertex":
                self.remove_vertex(*action[1])
            elif action[0] == "remove_edge":
                self.remove_edge(*action[1])

    def restore_vertex(self, x, y, vertex_id):
        vertex = (x, y, vertex_id)
        self.vertices.append(vertex)
        self.canvas.create_oval(x - 10, y - 10, x + 10, y + 10, fill="white", outline="black",tags=f"vertex_{vertex_id}")
        self.canvas.create_text(x, y, text=str(vertex_id), fill="black", tags=f"vertex_{vertex_id}")

    def restore_edge(self, start, end, weight):
        x0, y0, _ = start
        x1, y1, _ = end
        if self.is_directed:
            edge = self.canvas.create_line(x0, y0, x1, y1, arrow=tk.LAST, tags=f"edge_{start[2]}_{end[2]}", width=2)
        else:
            edge = self.canvas.create_line(x0, y0, x1, y1, tags=f"edge_{start[2]}_{end[2]}", width=2)
        self.edges.append((start, end, weight))
        if weight is not None:
            mid_x = (x0 + x1) / 2
            mid_y = (y0 + y1) / 2
            self.canvas.create_text(mid_x, mid_y, text=str(weight), fill="black", tags=f"weight_{start[2]}_{end[2]}")

    def save_graph(self):
        file_path = fd.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if not file_path:
            return

        graph_data = {
            "vertices": self.vertices,
            "edges": [(start[2], end[2], weight) for start, end, weight in self.edges],
            "is_directed": self.is_directed
        }

        with open(file_path, "w") as f:
            json.dump(graph_data, f)

    def load_graph(self):
        file_path = fd.askopenfilename(filetypes=[("JSON files", "*.json")])
        if not file_path:
            return
        with open(file_path, "r") as f:
            graph_data = json.load(f)
        self.reset_graph()

        self.is_directed = graph_data["is_directed"]
        for x, y, vertex_id in graph_data["vertices"]:
            self.create_vertex(x, y)

        vertex_dict = {v[2]: v for v in self.vertices}
        for start_id, end_id, weight in graph_data["edges"]:
            self.create_edge(vertex_dict[start_id], vertex_dict[end_id], weight)

        self.redraw_edges()

    def redraw_edges(self):
        self.canvas.delete("edges")
        for start, end, weight in self.edges:
            x0, y0, _ = start
            x1, y1, _ = end
            if self.is_directed:
                edge = self.canvas.create_line(x0, y0, x1, y1, arrow=tk.LAST, tags="edges", width=2)
            else:
                edge = self.canvas.create_line(x0, y0, x1, y1, tags="edges", width=2)
            if weight is not None:
                mid_x = (x0 + x1) / 2
                mid_y = (y0 + y1) / 2
                self.canvas.create_text(mid_x, mid_y, text=str(weight), fill="black", tags="edges")
    def activate_add_edge_mode(self):
        self.add_vertex_mode = False
        self.move_vertex_mode = False
        # Clear any previously selected vertex
        self.selected_vertex = None
        # Assuming there's an attribute to keep track of adding edge mode
        self.add_edge_mode = True



if __name__ == "__main__":
    app = GraphApp()
    app.mainloop()

            