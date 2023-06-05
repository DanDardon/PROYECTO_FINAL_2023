import tkinter as tk
import tkinter.filedialog as fd
import tkinter.messagebox as mb
import keyword
import xml.dom.minidom as minidom
from anytree import Node, RenderTree
from graphviz import Digraph
import tkinter.simpledialog as sd
from pygments import lex
from pygments.lexers import HtmlLexer
from pygments.styles import get_style_by_name
from pygments.token import Token
import re

class TextEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Editor de Texto HTML")
        self.container = tk.Frame(self.root)
        self.container.pack(fill=tk.BOTH, expand=True)

        self.line_numbers = tk.Text(self.container, width=4, padx=3, takefocus=0, border=0, background='lightgray', state=tk.DISABLED)
        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)

        self.text_area = tk.Text(self.container, wrap=tk.WORD, bg='dimgray', fg='Black')  # Tonos de azul más suave
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

        self.current_file_path = ""

    def display_line_numbers(self, event=None):
        line_count = self.text_area.get('1.0', tk.END).count('\n')
        self.line_numbers.config(state=tk.NORMAL)
        self.line_numbers.delete('1.0', tk.END)
        for line in range(1, line_count + 2):
            self.line_numbers.insert(tk.END, f'{line}\n')
        self.line_numbers.config(state=tk.DISABLED)

    def new_file(self):
        self.text_area.delete('1.0', tk.END)
        self.current_file_path = ""

    def open_file(self):
        file_path = fd.askopenfilename(filetypes=[("HTML Files", "*.html"), ("All Files", "*.*")])
        if file_path:
            self.text_area.delete('1.0', tk.END)
            with open(file_path, 'r') as file:
                self.text_area.insert(tk.END, file.read())
            self.display_line_numbers()
            self.current_file_path = file_path

    def save_file(self):
        if self.current_file_path:
            with open(self.current_file_path, 'w') as file:
                file.write(self.text_area.get('1.0', tk.END))
        else:
            self.save_file_as()

    def save_file_as(self):
        file_path = fd.asksaveasfilename(defaultextension=".html", filetypes=[("HTML Files", "*.html"), ("All Files", "*.*")])
        if file_path:
            with open(file_path, 'w') as file:
                file.write(self.text_area.get('1.0', tk.END))
            self.current_file_path = file_path
            mb.showinfo("Guardar como", "El archivo se guardó correctamente.")

    def search_text(self):
        search_query = sd.askstring("Buscar", "Ingrese el texto a buscar:")
        if search_query:
            # Eliminar resaltado previo
            self.text_area.tag_remove('search', '1.0', tk.END)
            start_index = '1.0'
        while True:
            start_index = self.text_area.search(search_query, start_index, stopindex=tk.END)
            if not start_index:
                break
            end_index = f"{start_index}+{len(search_query)}c"
            self.text_area.tag_add('search', start_index, end_index)
            start_index = end_index
            self.text_area.tag_config('search', background='yellow')

            # Configurar evento de clic para eliminar resaltado
            self.text_area.bind('<Button-1>', self.remove_search_highlight)

    def replace_text(self):
        search_query = sd.askstring("Reemplazar", "Ingrese el texto a buscar:")
        if search_query:
            replace_query = sd.askstring("Reemplazar", "Ingrese el texto de reemplazo:")
            if replace_query:
                text_content = self.text_area.get('1.0', tk.END)
                new_content = text_content.replace(search_query, replace_query)
                self.text_area.delete('1.0', tk.END)
                self.text_area.insert(tk.END, new_content)
                mb.showinfo("Reemplazar", "La operación de reemplazo se completó.")

    def goto_line(self):
        line_number = sd.askinteger("Ir a", "Ingrese el número de línea:")
        if line_number:
            # Eliminar resaltado previo
            self.text_area.tag_remove('line', '1.0', tk.END)
            line_start = f"{line_number}.0"
            line_end = f"{line_number}.end"
            self.text_area.tag_add('line', line_start, line_end)
            self.text_area.tag_config('line', background='lightblue')
            self.text_area.mark_set(tk.INSERT, line_start)
            self.text_area.see(tk.INSERT)

        # Configurar evento de escritura para eliminar resaltado
            self.text_area.bind('<Button-1>', self.remove_line_highlight)


    def remove_search_highlight(self, event=None):
    # Eliminar resaltado de búsqueda
        self.text_area.tag_remove('search', '1.0', tk.END)

    def remove_line_highlight(self, event=None):
     # Eliminar resaltado de línea
        self.text_area.tag_remove('line', '1.0', tk.END)

    def highlight_html_syntax(self, event=None):
        html = self.text_area.get('1.0', tk.END)
        tags = self.get_html_tags(html)
        self.text_area.tag_config('html', foreground='blue')
        for tag in tags:
            start_index = '1.0'
            while True:
                start_index = self.text_area.search(tag, start_index, stopindex=tk.END)
                if not start_index:
                    break
                end_index = f"{start_index}+{len(tag)}c"
                self.text_area.tag_add('html', start_index, end_index)
                start_index = end_index

    def get_html_tags(self, html):
        tags = []
        pattern = r'<\s*(\w+)'
        matches = re.finditer(pattern, html)
        for match in matches:
            tag = match.group(1)
            if tag not in tags:
                tags.append(tag)
        return tags

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
            self.highlight_html_syntax()
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

    def create_dom_graph(self, node, parent=None):
        node_name = f"{node.name}_{id(node)}"  # Agregar un identificador único al nombre del nodo
        self.graph.node(node_name, label=node.name)  # Usar el nombre del nodo con identificador único como etiqueta
        if parent:
            self.graph.edge(parent, node_name)  # Conectar el nodo al nodo padre

        for child in node.children:
            self.create_dom_graph(child, parent=node_name)  # Pasar el nombre del nodo con identificador único como padre


    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    root = tk.Tk()
    editor = TextEditor(root)
    editor.dom_graph.pack(fill=tk.BOTH, expand=True)
    editor.run()
