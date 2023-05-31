import tkinter as tk
import tkinter.filedialog as fd
import keyword
import xml.dom.minidom as minidom
from anytree import Node, RenderTree
from graphviz import Digraph

class TextEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Editor de Texto HTML")
        self.container = tk.Frame(self.root)
        self.container.pack(fill=tk.BOTH, expand=True)

        self.line_numbers = tk.Text(self.container, width=4, padx=3, takefocus=0, border=0, background='lightgray', state=tk.DISABLED)
        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)

        self.text_area = tk.Text(self.container, wrap=tk.WORD, bg='dimgray', fg='gold')  # Tonos de azul más suave
        self.text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.text_area.bind('<Key>', self.display_line_numbers)
        self.text_area.bind('<KeyRelease>', self.update_dom_view)

        self.scrollbar = tk.Scrollbar(self.root, command=self.text_area.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.text_area.configure(yscrollcommand=self.scrollbar.set)

        self.reserved_words = keyword.kwlist

        self.menu_bar = tk.Menu(root)
        self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.file_menu.add_command(label="Nuevo", command=self.new_file)
        self.file_menu.add_command(label="Abrir", command=self.open_file)
        self.file_menu.add_command(label="Guardar", command=self.save_file)
        self.file_menu.add_command(label="Guardar Como", command=self.save_file_as)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Salir", command=self.root.quit)
        self.menu_bar.add_cascade(label="Archivo", menu=self.file_menu)
        self.edit_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.edit_menu.add_command(label="Buscar", command=self.search_text)
        self.edit_menu.add_command(label="Reemplazar", command=self.replace_text)
        self.edit_menu.add_command(label="Ir a", command=self.goto_line)
        self.menu_bar.add_cascade(label="Editar", menu=self.edit_menu)
        self.menu_bar.add_command(label="Imprimir", command=self.print_file)
        self.root.config(menu=self.menu_bar)

        self.graph = Digraph(format='png')
        self.dom_graph = tk.Label(self.root)

    def display_line_numbers(self, event=None):
        line_count = self.text_area.get('1.0', tk.END).count('\n')
        self.line_numbers.config(state=tk.NORMAL)
        self.line_numbers.delete('1.0', tk.END)
        for line in range(1, line_count + 2):
            self.line_numbers.insert(tk.END, f'{line}\n')
        self.line_numbers.config(state=tk.DISABLED)

    def new_file(self):
        self.text_area.delete('1.0', tk.END)

    def open_file(self):
        file_path = fd.askopenfilename(filetypes=[("HTML Files", "*.html"), ("All Files", "*.*")])
        if file_path:
            self.text_area.delete('1.0', tk.END)
            with open(file_path, 'r') as file:
                self.text_area.insert(tk.END, file.read())
            self.display_line_numbers()

    def save_file(self):
        # Implement your save file logic here
        pass

    def save_file_as(self):
        # Implement your save file as logic here
        pass

    def search_text(self):
        # Implement your search text logic here
        pass

    def replace_text(self):
        # Implement your replace text logic here
        pass

    def goto_line(self):
        # Implement your go to line logic here
        pass

    def print_file(self):
        # Implement your print file logic here
        pass

    def update_dom_view(self, event=None):
        html = self.text_area.get('1.0', tk.END)
        try:
            dom = minidom.parseString(html)
            root_node = self.create_dom_tree(dom.documentElement)
            self.graph.clear()
            self.create_dom_graph(root_node)
            self.graph.render(filename='dom_graph', format='png', cleanup=True)
            self.dom_graph.config(image='')
            self.dom_graph.image = tk.PhotoImage(file='dom_graph.png')
            self.dom_graph.config(image=self.dom_graph.image)
        except Exception as e:
            # Error al analizar el HTML
            self.dom_graph.config(image='')
            self.dom_graph.image = None
            self.dom_graph.config(text=str(e))

    def create_dom_tree(self, element, parent=None):
        node = Node(element.nodeName, parent=parent)
        for child_element in element.childNodes:
            if child_element.nodeType == child_element.ELEMENT_NODE:
                self.create_dom_tree(child_element, parent=node)
        return node

    def create_dom_graph(self, node):
        self.graph.node(node.name)
        for child in node.children:
            self.graph.edge(node.name, child.name)
            self.create_dom_graph(child)

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    root = tk.Tk()
    editor = TextEditor(root)
    editor.dom_graph.pack(fill=tk.BOTH, expand=True)
    editor.run()
