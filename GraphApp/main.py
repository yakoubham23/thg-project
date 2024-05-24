import tkinter as tk
import tkinter.filedialog as fd
import json

class GraphApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Application de Graphes")
        self.geometry("800x600")

        # Initialize the canvas, not visible at the beginning
        self.canvas = tk.Canvas(self, bg="white", width=800, height=600)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.vertices = []
        self.edges = []
        self.selected_vertex = None
        self.selected_edge = None
        self.is_directed = None  # Initiated to None, user must choose
        self.move_vertex_mode = False
        self.add_vertex_mode = True
        self.add_edge_mode = False
        self.action_stack = []
        self.redo_stack = []
        self.temp_line = None

        # Display initial buttons
        self.display_initial_buttons()

    def display_initial_buttons(self):
        # Create buttons for loading, creating new graph, and exiting
        self.btn_load_graph = tk.Button(self, text="Charger le Graphe", command=self.load_graph)
        self.btn_load_graph.pack(side=tk.TOP, pady=10)

        self.btn_new_graph = tk.Button(self, text="Nouveau Graphe", command=self.choose_graph_type)
        self.btn_new_graph.pack(side=tk.TOP, pady=10)

        self.btn_exit = tk.Button(self, text="Quitter", command=self.quit)
        self.btn_exit.pack(side=tk.TOP, pady=10)

    def choose_graph_type(self):
        # Remove initial buttons
        self.btn_load_graph.pack_forget()
        self.btn_new_graph.pack_forget()
        self.btn_exit.pack_forget()

        # Display buttons for choosing graph type
        self.btn_directed = tk.Button(self, text="Graphe orienté", command=lambda: self.init_graph(True))
        self.btn_directed.pack(side=tk.TOP, pady=(20, 10))

        self.btn_undirected = tk.Button(self, text="Graphe non orienté", command=lambda: self.init_graph(False))
        self.btn_undirected.pack(side=tk.TOP, pady=10)

    def init_graph(self, is_directed):
        self.is_directed = is_directed

        # Remove buttons for choosing graph type
        self.btn_directed.pack_forget()
        self.btn_undirected.pack_forget()

        # Display buttons for graph manipulation
        if self.is_directed:
            self.display_directed_graph_buttons()
        else:
            self.display_undirected_graph_buttons()

    def display_directed_graph_buttons(self):
        # Display buttons for directed graph manipulation
        self.btn_add_vertex = tk.Button(self, text="Ajouter un sommet", command=self.activate_add_vertex_mode)
        self.btn_add_vertex.pack(side=tk.TOP, padx=5, pady=5)

        self.btn_remove_vertex = tk.Button(self, text="Supprimer un sommet", command=self.on_remove_vertex)
        self.btn_remove_vertex.pack(side=tk.TOP, padx=5, pady=5)

        self.btn_add_edge = tk.Button(self, text="Ajouter un arc", command=self.activate_add_edge_mode)
        self.btn_add_edge.pack(side=tk.TOP, padx=5, pady=5)

        self.btn_remove_edge = tk.Button(self, text="Supprimer un arc", command=self.on_remove_edge)
        self.btn_remove_edge.pack(side=tk.TOP, padx=5, pady=5)

        self.btn_modify_edge = tk.Button(self, text="Modification des Arêtes", command=self.modify_edge)
        self.btn_modify_edge.pack(side=tk.TOP, padx=5, pady=5)

        self.btn_move_vertex = tk.Button(self, text="Déplacement de Sommets", command=self.move_vertex)
        self.btn_move_vertex.pack(side=tk.TOP, padx=5, pady=5)

        self.btn_canvas_zoom = tk.Button(self, text="Zoom et Déplacement du Canevas", command=self.canvas_zoom)
        self.btn_canvas_zoom.pack(side=tk.TOP, padx=5, pady=5)
        self.add_back_button()

    def display_undirected_graph_buttons(self):
        # Display buttons for undirected graph manipulation
        self.btn_add_vertex = tk.Button(self, text="Ajouter un sommet", command=self.activate_add_vertex_mode)
        self.btn_add_vertex.pack(side=tk.TOP, padx=5, pady=5)

        self.btn_remove_vertex = tk.Button(self, text="Supprimer un sommet", command=self.on_remove_vertex)
        self.btn_remove_vertex.pack(side=tk.TOP, padx=5, pady=5)

        self.btn_add_edge = tk.Button(self, text="Ajouter une arête", command=self.activate_add_edge_mode)
        self.btn_add_edge.pack(side=tk.TOP, padx=5, pady=5)

        self.btn_modify_edge = tk.Button(self, text="Modification des Arêtes", command=self.modify_edge)
        self.btn_modify_edge.pack(side=tk.TOP, padx=5, pady=5)

        self.btn_move_vertex = tk.Button(self, text="Déplacement de Sommets", command=self.move_vertex)
        self.btn_move_vertex.pack(side=tk.TOP, padx=5, pady=5)

        self.btn_canvas_zoom = tk.Button(self, text="Zoom et Déplacement du Canevas", command=self.canvas_zoom)
        self.btn_canvas_zoom.pack(side=tk.TOP, padx=5, pady=5)
        self.add_back_button()
    def add_back_button(self):
        self.btn_back = tk.Button(self, text="Retour", command=self.go_back_to_initial)
        self.btn_back.pack(side=tk.TOP, padx=5, pady=5)

    def go_back_to_initial(self):
        # Remove graph manipulation buttons
        self.btn_add_vertex.pack_forget()
        self.btn_remove_vertex.pack_forget()
        self.btn_add_edge.pack_forget()
        self.btn_modify_edge.pack_forget()
        self.btn_move_vertex.pack_forget()
        self.btn_canvas_zoom.pack_forget()
        self.btn_remove_edge.pack_forget() if hasattr(self, 'btn_remove_edge') else None
        self.btn_back.pack_forget() 
        # Reset canvas and internal state
        self.canvas.delete("all")
        self.vertices = []
        self.edges = []
        self.selected_vertex = None
        self.selected_edge = None
        self.is_directed = None
        self.action_stack = []
        self.redo_stack = []
        self.temp_line = None  
        self.display_initial_buttons() 
    
    def activate_add_vertex_mode(self):
        self.add_vertex_mode = True
        self.move_vertex_mode = False

    def activate_add_edge_mode(self):
        self.add_vertex_mode = False
        self.move_vertex_mode = False
        # Clear any previously selected vertex
        self.selected_vertex = None
        # Assuming there's an attribute to keep track of adding edge mode
        self.add_edge_mode = True

    
    def load_graph(self):
        # Implement the logic to load a graph here
        pass

    def on_remove_vertex(self):
        if self.selected_vertex:
            self.remove_vertex(self.selected_vertex)
            self.selected_vertex = None

    def on_remove_edge(self):
        if self.selected_edge:
            self.remove_edge(self.selected_edge)
            self.selected_edge = None

    def remove_vertex(self, vertex):
        # Implement the logic to remove a vertex here
        pass

    def remove_edge(self, edge):
        # Implement the logic to remove an edge here
        pass

    def modify_edge(self):
        # Implement the logic to modify edge direction and weight here
        pass

    def move_vertex(self):
        # Implement the logic to move vertices here
        pass

    def canvas_zoom(self):
        # Implement the logic for canvas zoom and pan here
        pass


if __name__ == "__main__":
    app = GraphApp()
    app.mainloop()
