import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from db.ConexionDB import db 
import traceback
from datetime import datetime
from PIL import Image, ImageTk
import shutil

BOOK_COVERS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'book_covers')
os.makedirs(BOOK_COVERS_DIR, exist_ok=True)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMG_DIR = os.path.join(BASE_DIR, 'img')

class BookManagementWindow(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Gestión de Libros")
        self.geometry("1200x700")
        self.configure(bg="#F5F5F5")

        self.current_view = None

        self.style = ttk.Style(self)
        self.configure_global_styles()

        self.back_arrow_icon = None
        try:
            back_arrow_path = os.path.join(IMG_DIR, 'flecader.png')
            if os.path.exists(back_arrow_path):
                img = Image.open(back_arrow_path)
                img = img.resize((20, 20), Image.Resampling.LANCZOS)
                self.back_arrow_icon = ImageTk.PhotoImage(img)
            else:
                print(f"Advertencia: No se encontró la imagen de flecha en {back_arrow_path}")
        except Exception as e:
            print(f"Error cargando imagen de flecha: {e}")

        self.header_bar = ttk.Frame(self, style='Header.TFrame', padding=(10,5))
        self.header_bar.pack(fill=tk.X, side=tk.TOP)

        self.view_title_label = ttk.Label(self.header_bar, text="Inventario de Libros", style='HeaderTitle.TLabel')
        self.view_title_label.pack(side=tk.LEFT, padx=(10,0))

        self.add_new_book_button = ttk.Button(
            self.header_bar,
            text="Agregar Nuevo Libro",
            command=self.show_form_view,
            style='Accent.TButton'
        )

        self.back_arrow_button = ttk.Button(
            self.header_bar,
            text="<- Volver",
            image=self.back_arrow_icon,
            compound=tk.LEFT if self.back_arrow_icon else tk.NONE,
            command=self.show_table_view,
            style='Accent.TButton'
        )

        self.main_area = ttk.Frame(self, style='Background.TFrame', padding=10)
        self.main_area.pack(expand=True, fill=tk.BOTH)

        self.form_outer_frame = ttk.Frame(self.main_area, style='Card.TFrame')
        self.form_frame = ttk.LabelFrame(self.form_outer_frame, text="Detalles del Libro", style='Card.TLabelframe')
        self.form_frame.pack(padx=15, pady=15, expand=True, fill=tk.BOTH)

        self.fields = [
            ("Título:", "titulo_entry"), ("Autor:", "autor_entry"),
            ("Editorial:", "editorial_entry"), ("Año de publicación (YYYY-MM-DD):", "año_publicacion_entry"),
            ("ISBN:", "isbn_entry"), ("Número de páginas:", "numpag_entry"),
            ("Precio:", "precio_entry"), ("Stock:", "stock_entry"),
            ("Género:", "genero_entry"), ("Descripción:", "descripcion_entry"),
            ("Formato:", "formato_entry")
        ]
        self.entries = {}
        current_row = 0
        for i, (label_text, entry_name) in enumerate(self.fields):
            label = ttk.Label(self.form_frame, text=label_text, style='FormLabel.TLabel')
            label.grid(row=current_row, column=0, padx=5, pady=6, sticky="w")
            if entry_name == "descripcion_entry":
                entry = tk.Text(self.form_frame, width=38, height=4, relief="solid", borderwidth=1, font=('Helvetica', 10), bg="#FFFFFF")
                entry.grid(row=current_row, column=1, padx=5, pady=6, sticky="ew")
            else:
                entry = ttk.Entry(self.form_frame, width=40, style='Form.TEntry')
                entry.grid(row=current_row, column=1, padx=5, pady=6, sticky="ew")
            self.entries[entry_name] = entry
            current_row += 1

        self.image_path_var = tk.StringVar()
        self.selected_image_path = None
        self.image_filename_for_db = None

        image_label = ttk.Label(self.form_frame, text="Imagen Portada:", style='FormLabel.TLabel')
        image_label.grid(row=current_row, column=0, padx=5, pady=6, sticky="w")

        self.image_path_display_frame = ttk.Frame(self.form_frame, style='FormInput.TFrame')
        self.image_path_display_frame.grid(row=current_row, column=1, padx=5, pady=6, sticky="ew")

        self.image_path_display = ttk.Entry(self.image_path_display_frame, textvariable=self.image_path_var, state="readonly", width=28, style='Form.TEntry')
        self.image_path_display.pack(side=tk.LEFT, expand=True, fill=tk.X)

        self.select_image_button = ttk.Button(self.image_path_display_frame, text="Seleccionar...", command=self.select_image_file, style='SmallAccent.TButton')
        self.select_image_button.pack(side=tk.LEFT, padx=(5,0))
        current_row += 1

        self.image_preview_label = ttk.Label(self.form_frame, text="Previsualización no disponible", style='ImagePreview.TLabel', relief="solid", borderwidth=1, anchor="center")
        self.image_preview_label.grid(row=current_row, column=0, columnspan=2, padx=5, pady=10, sticky="nsew")
        self.form_frame.grid_rowconfigure(current_row, minsize=150)
        self.preview_tk_image = None
        current_row += 1

        self.button_form_frame = ttk.Frame(self.form_frame, style='FormButton.TFrame')
        self.button_form_frame.grid(row=current_row, column=0, columnspan=2, pady=15)

        self.save_button = ttk.Button(self.button_form_frame, text="Guardar", command=self.save_book, style='Success.TButton')
        self.save_button.pack(side=tk.LEFT, padx=10)

        self.clear_button_form = ttk.Button(self.button_form_frame, text="Limpiar", command=self.clear_form, style='Secondary.TButton')
        self.clear_button_form.pack(side=tk.LEFT, padx=10)

        self.form_frame.grid_columnconfigure(1, weight=1)

        self.table_outer_frame = ttk.Frame(self.main_area, style='Card.TFrame')
        self.table_frame_content = ttk.Frame(self.table_outer_frame, style='Card.TFrame')
        self.table_frame_content.pack(padx=15, pady=15, expand=True, fill=tk.BOTH)

        self.tree_columns = ("ID", "Título", "Autor", "Editorial", "ISBN", "Precio", "Stock", "Género", "Formato")
        self.tree = ttk.Treeview(self.table_frame_content, columns=self.tree_columns, show="headings", style='Modern.Treeview', height=15)

        col_widths = {"ID": 40, "Título": 220, "Autor": 150, "Editorial": 120, "ISBN": 120, "Precio": 70, "Stock": 60, "Género": 100, "Formato": 100}
        col_anchors = {"ID": tk.CENTER, "Título": tk.W, "Autor": tk.W, "Editorial": tk.W, "ISBN": tk.CENTER, "Precio": tk.E, "Stock": tk.CENTER, "Género": tk.W, "Formato": tk.W}

        for col_name in self.tree_columns:
            heading_anchor = col_anchors.get(col_name, tk.W)
            content_anchor = col_anchors.get(col_name, tk.W)
            self.tree.heading(col_name, text=col_name, anchor=heading_anchor)
            self.tree.column(col_name, width=col_widths.get(col_name, 100), anchor=content_anchor, minwidth=40)

        self.configure_treeview_tags()

        self.tree_scrollbar_y = ttk.Scrollbar(self.table_frame_content, orient="vertical", command=self.tree.yview, style='Modern.Vertical.TScrollbar')
        self.tree.configure(yscrollcommand=self.tree_scrollbar_y.set)

        self.tree.pack(side=tk.LEFT, expand=True, fill="both")
        self.tree_scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.table_buttons_frame = ttk.Frame(self.table_outer_frame, style='Card.TFrame', padding=(0,10,0,0))
        self.table_buttons_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=15, pady=(0,15))

        self.delete_tree_button = ttk.Button(self.table_buttons_frame, text="Eliminar Seleccionado", command=self.delete_book, style='Danger.TButton')
        self.delete_tree_button.pack(side=tk.RIGHT, padx=5)

        self.show_table_view()
        self.load_books()

    def configure_global_styles(self):
        BG_COLOR = "#F5F5F5"; CARD_COLOR = "#FFFFFF"; TEXT_COLOR = "#333333"
        HEADER_BG_COLOR = "#FFFFFF"; HEADER_TEXT_COLOR = "#003366"
        PRIMARY_ACCENT_COLOR = "#007bff"; PRIMARY_ACCENT_HOVER = "#0056b3"
        SECONDARY_BUTTON_BG = "#6c757d"; SECONDARY_BUTTON_HOVER = "#545b62"
        SUCCESS_COLOR = "#28a745"; SUCCESS_HOVER = "#1e7e34"
        DANGER_COLOR = "#dc3545"; DANGER_HOVER = "#b02a37"
        ENTRY_BG = "#FFFFFF"; ENTRY_BORDER = "#CED4DA"
        TREE_HEADER_BG = "#E9ECEF"; TREE_HEADER_FG = "#495057"

        self.style.configure('Background.TFrame', background=BG_COLOR)
        self.style.configure('Header.TFrame', background=HEADER_BG_COLOR)
        self.style.configure('Card.TFrame', background=CARD_COLOR, relief="flat", borderwidth=0)
        
        self.style.configure('Card.TLabelframe', background=CARD_COLOR, foreground=TEXT_COLOR, relief="groove", borderwidth=1, font=('Helvetica', 11, 'bold'))
        self.style.configure('Card.TLabelframe.Label', background=CARD_COLOR, foreground=TEXT_COLOR, font=('Helvetica', 11, 'bold'), padding=(0,0,0,5))

        self.style.configure('HeaderTitle.TLabel', background=HEADER_BG_COLOR, foreground=HEADER_TEXT_COLOR, font=('Helvetica', 16, 'bold'))
        self.style.configure('FormLabel.TLabel', background=CARD_COLOR, foreground=TEXT_COLOR, font=('Helvetica', 10))
        self.style.configure('ImagePreview.TLabel', background=ENTRY_BG, foreground=TEXT_COLOR, font=('Helvetica', 9))

        self.style.configure('Form.TEntry', fieldbackground=ENTRY_BG, foreground=TEXT_COLOR, bordercolor=ENTRY_BORDER, borderwidth=1, relief="solid", padding=(5,5), font=('Helvetica', 10))
        self.style.map('Form.TEntry', bordercolor=[('focus', PRIMARY_ACCENT_COLOR)])
        
        self.style.configure('FormInput.TFrame', background=CARD_COLOR)
        self.style.configure('FormButton.TFrame', background=CARD_COLOR)

        button_font = ('Helvetica', 10, 'bold')
        self.style.configure('Accent.TButton', background=PRIMARY_ACCENT_COLOR, foreground='white', borderwidth=0, font=button_font, padding=(8,6))
        self.style.map('Accent.TButton', background=[('active', PRIMARY_ACCENT_HOVER), ('pressed', PRIMARY_ACCENT_HOVER)])
        
        self.style.configure('SmallAccent.TButton', background=PRIMARY_ACCENT_COLOR, foreground='white', borderwidth=0, font=('Helvetica', 9), padding=(4,3))
        self.style.map('SmallAccent.TButton', background=[('active', PRIMARY_ACCENT_HOVER), ('pressed', PRIMARY_ACCENT_HOVER)])

        self.style.configure('Secondary.TButton', background=SECONDARY_BUTTON_BG, foreground='white', borderwidth=0, font=button_font, padding=(8,6))
        self.style.map('Secondary.TButton', background=[('active', SECONDARY_BUTTON_HOVER), ('pressed', SECONDARY_BUTTON_HOVER)])

        self.style.configure('Success.TButton', background=SUCCESS_COLOR, foreground='white', borderwidth=0, font=button_font, padding=(8,6))
        self.style.map('Success.TButton', background=[('active', SUCCESS_HOVER), ('pressed', SUCCESS_HOVER)])
        
        self.style.configure('Danger.TButton', background=DANGER_COLOR, foreground='white', borderwidth=0, font=button_font, padding=(8,6))
        self.style.map('Danger.TButton', background=[('active', DANGER_HOVER), ('pressed', DANGER_HOVER)])

        self.style.configure('Modern.Treeview', background=CARD_COLOR, foreground=TEXT_COLOR, rowheight=30, fieldbackground=CARD_COLOR, borderwidth=1, relief="solid", bordercolor=ENTRY_BORDER)
        self.style.configure('Modern.Treeview.Heading', background=TREE_HEADER_BG, foreground=TREE_HEADER_FG, font=('Helvetica', 10, 'bold'), relief="flat", padding=(8,8))
        self.style.map('Modern.Treeview.Heading', background=[('active', TREE_HEADER_BG)])
        self.style.layout("Modern.Treeview", [('Modern.Treeview.treearea', {'sticky': 'nswe'})])

        self.style.configure('Modern.Vertical.TScrollbar', troughcolor=BG_COLOR, background=SECONDARY_BUTTON_BG, bordercolor=BG_COLOR, arrowcolor='white')
        self.style.map('Modern.Vertical.TScrollbar', background=[('active', SECONDARY_BUTTON_HOVER)])

    def configure_treeview_tags(self):
        colors = self.get_colors()
        self.tree.tag_configure('oddrow', background=colors.get('row_bg1', '#FFFFFF'))
        self.tree.tag_configure('evenrow', background=colors.get('row_bg2', '#F8F9FA'))
        
    def get_colors(self):
        return {
            'row_bg1': '#FFFFFF',
            'row_bg2': '#F8F9FA',
        }
    
    def show_table_view(self):
        if self.current_view == 'table':
            return
        self.form_outer_frame.pack_forget()
        self.back_arrow_button.pack_forget()
        self.view_title_label.configure(text="Inventario de Libros")
        self.add_new_book_button.pack(side=tk.RIGHT, padx=(0,10))
        self.table_outer_frame.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)
        self.current_view = 'table'
        self.load_books()

    def show_form_view(self, book_data=None):
        if self.current_view == 'form' and not book_data:
            if self.add_new_book_button.winfo_ismapped():
                 self.clear_form()

        self.table_outer_frame.pack_forget()
        self.add_new_book_button.pack_forget()
        self.view_title_label.configure(text="Detalles del Libro")
        self.back_arrow_button.pack(side=tk.RIGHT, padx=(0,10))
        self.form_outer_frame.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)
        
        if self.current_view != 'form':
            self.clear_form()
        self.current_view = 'form'

    def select_image_file(self):
        filepath = filedialog.askopenfilename(
            title="Seleccionar imagen de portada",
            filetypes=(("Archivos de imagen", "*.jpg *.jpeg *.png *.gif"), ("Todos los archivos", "*.*"))
        )
        if filepath:
            self.selected_image_path = filepath
            self.image_filename_for_db = os.path.basename(filepath)
            self.image_path_var.set(self.image_filename_for_db) 
            self.update_image_preview(filepath)

    def update_image_preview(self, filepath):
        if filepath and os.path.exists(filepath):
            try:
                img = Image.open(filepath)
                max_width = self.image_preview_label.winfo_width() - 10
                max_height = self.image_preview_label.winfo_height() - 10
                
                if max_width <=10 or max_height <=10:
                    max_width, max_height = 200, 140

                img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
                self.preview_tk_image = ImageTk.PhotoImage(img)
                self.image_preview_label.configure(image=self.preview_tk_image, text="")
            except Exception as e:
                self.preview_tk_image = None
                self.image_preview_label.configure(image=None, text="Error al cargar imagen")
                print(f"Error al previsualizar imagen: {e}")
        else:
            self.preview_tk_image = None
            self.image_preview_label.configure(image=None, text="Previsualización no disponible")

    def get_form_data(self):
        data = {}
        for name, widget in self.entries.items():
            if isinstance(widget, tk.Text):
                data[name] = widget.get("1.0", tk.END).strip()
            else:
                data[name] = widget.get().strip()
        return data

    def save_book(self):
        book_data = self.get_form_data()

        if not db.conexion or not db.conexion.is_connected():
            messagebox.showerror("Error", "No hay conexión a la base de datos.")
            return

        final_image_name_for_db = self.image_filename_for_db 

        if self.selected_image_path and self.image_filename_for_db:
            destination_path = os.path.join(BOOK_COVERS_DIR, self.image_filename_for_db)
            try:
                shutil.copy(self.selected_image_path, destination_path)
                print(f"Imagen copiada a: {destination_path}")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo guardar la imagen de portada: {e}")
                return

        try:
            db.conexion.start_transaction()
            autor_id = self._get_or_create_related_id('autor', 'aut_nombre', 'aut_id', book_data.get('autor_entry', ''))
            editorial_id = self._get_or_create_related_id('editorial', 'edit_nombre', 'edit_id', book_data.get('editorial_entry', ''))
            genero_id = self._get_or_create_related_id('genero', 'gen_nombre', 'gen_id', book_data.get('genero_entry', ''))

            if not book_data.get('titulo_entry'):
                 messagebox.showwarning("Advertencia", "El campo 'Título' es obligatorio.")
                 db.conexion.rollback(); return

            año_publicacion_db = self._validate_and_format_date(book_data.get('año_publicacion_entry', ''))
            if book_data.get('año_publicacion_entry', '') and año_publicacion_db is None:
                db.conexion.rollback(); return

            try:
                numpag = int(book_data.get('numpag_entry')) if book_data.get('numpag_entry') else None
                precio_str = book_data.get('precio_entry', '').replace(',', '.')
                precio = float(precio_str) if precio_str else None
                stock = int(book_data.get('stock_entry')) if book_data.get('stock_entry') else None
            except ValueError:
                messagebox.showerror("Error", "Número de páginas, precio o stock contienen valores no numéricos. Use '.' para decimales en precio.")
                db.conexion.rollback(); return
            
            query_insert_libro = """
            INSERT INTO libro (lib_nombre, lib_fkAutor, lib_fkEditorial, lib_añopublicacion,
                               lib_isbn, lib_numpag, lib_precio, lib_stock,
                               lib_descripcion, lib_formato, lib_ruta_imagen)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
            
            libro_values = (
                book_data.get('titulo_entry'), autor_id, editorial_id, año_publicacion_db,
                book_data.get('isbn_entry') or None, numpag, precio, stock,
                book_data.get('descripcion_entry') or None,
                book_data.get('formato_entry') or None,
                final_image_name_for_db
            )

            cursor_libro_insert = db.ejecutar_query(query_insert_libro, libro_values)
            
            libro_id = None
            if cursor_libro_insert and hasattr(cursor_libro_insert, 'lastrowid'):
                libro_id = cursor_libro_insert.lastrowid
            elif db.cursor and hasattr(db.cursor, 'lastrowid'):
                 libro_id = db.cursor.lastrowid

            if not libro_id and (hasattr(db.conexion, 'driver_name') and db.conexion.driver_name == 'mysql'):
                 db.conexion.rollback()
                 messagebox.showerror("Error", "No se pudo obtener el ID del libro insertado.")
                 return

            if libro_id and genero_id:
                db.ejecutar_query("INSERT INTO libro_genero (libgen_fkLibro, libgen_fkGenero) VALUES (%s, %s)", (libro_id, genero_id))

            db.conexion.commit()
            messagebox.showinfo("Guardar Libro", "Libro guardado exitosamente.")
            self.clear_form()
            self.show_table_view()
        except Exception as e:
            if db.conexion and db.conexion.is_connected():
                db.conexion.rollback()
            traceback.print_exc()
            messagebox.showerror("Error al Guardar", f"Ocurrió un error al guardar el libro: {e}")

    def _get_or_create_related_id(self, table_name, name_column, id_column, value):
        if not value:
            return None
        
        cursor_select = db.ejecutar_query(f"SELECT {id_column} FROM {table_name} WHERE {name_column} = %s", (value,))
        result = cursor_select.fetchone() if cursor_select else None
        
        if result:
            return result[0]
        else:
            cursor_insert = db.ejecutar_query(f"INSERT INTO {table_name} ({name_column}) VALUES (%s)", (value,))
            new_id = None
            if cursor_insert and hasattr(cursor_insert, 'lastrowid'):
                new_id = cursor_insert.lastrowid
            elif db.cursor and hasattr(db.cursor, 'lastrowid'):
                new_id = db.cursor.lastrowid
            return new_id

    def _validate_and_format_date(self, date_str):
        if not date_str:
            return None
        try:
            datetime.strptime(date_str, '%Y-%m-%d')
            return date_str
        except ValueError:
            messagebox.showerror("Error de Formato de Fecha", "La fecha de publicación debe estar en formato YYYY-MM-DD.")
            return None

    def clear_form(self):
        for name, widget in self.entries.items():
            if isinstance(widget, tk.Text):
                widget.delete("1.0", tk.END)
            else:
                widget.delete(0, tk.END)
        self.image_path_var.set("")
        self.selected_image_path = None
        self.image_filename_for_db = None
        self.update_image_preview(None)

    def load_books(self):
        print("--- Iniciando load_books ---")
        for item in self.tree.get_children():
            self.tree.delete(item)
        try:
            query = (
                "SELECT l.lib_id, l.lib_nombre, COALESCE(a.aut_nombre, '') AS autor_nombre, "
                "COALESCE(ed.edit_nombre, '') AS editorial_nombre, l.lib_isbn, l.lib_precio, l.lib_stock, "
                "GROUP_CONCAT(DISTINCT g.gen_nombre SEPARATOR ', ') AS generos, l.lib_formato "
                "FROM libro l "
                "LEFT JOIN autor a ON l.lib_fkAutor = a.aut_id "
                "LEFT JOIN editorial ed ON l.lib_fkEditorial = ed.edit_id "
                "LEFT JOIN libro_genero lg ON l.lib_id = lg.libgen_fkLibro "
                "LEFT JOIN genero g ON lg.libgen_fkGenero = g.gen_id "
                "GROUP BY l.lib_id, l.lib_nombre, a.aut_nombre, ed.edit_nombre, l.lib_isbn, l.lib_precio, l.lib_stock, l.lib_formato "
                "ORDER BY l.lib_nombre"
            )
            print(f"Ejecutando consulta: {query[:100]}...")
            cursor = db.ejecutar_query(query)
            if cursor:
                rows = cursor.fetchall()
                print(f"Filas obtenidas de la BD: {len(rows)}")
                if not rows:
                    print("No se obtuvieron filas de la base de datos.")
                    print("--- Finalizando load_books (sin datos) ---")
                    return

                for i, row_data in enumerate(rows):
                    try:
                        lib_id, title, autor, ed_nombre, isbn, precio, stock, genres, formato_libro = row_data
                    except ValueError as ve:
                        print(f"Error al desempaquetar fila {i}: {row_data} - {ve}")
                        continue

                    values_for_treeview = (
                        str(lib_id),
                        str(title or "N/D"),
                        str(autor or "N/D"),
                        str(ed_nombre or "N/D"),
                        str(isbn or "N/D"),
                        f"${precio:.2f}" if precio is not None else "N/D",
                        str(stock) if stock is not None else "N/D",
                        str(genres or "Sin Género"),
                        str(formato_libro or "N/D")
                    )
                    tag = 'evenrow' if i % 2 == 0 else 'oddrow'
                    self.tree.insert("", tk.END, iid=str(lib_id), values=values_for_treeview, tags=(tag,))
            else:
                print("El cursor es None después de ejecutar_query.")
        except Exception as e:
            print(f"EXCEPCION en load_books: {e}")
            traceback.print_exc()
            messagebox.showerror("Error de Carga", f"Ocurrió un error al cargar los libros: {e}")
        print("--- Finalizando load_books ---")

    def delete_book(self):
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning("Advertencia", "Por favor, seleccione un libro de la lista para eliminar.")
            return

        item_iid = selected_items[0]
        try:
            book_title = self.tree.item(item_iid, 'values')[1] 
            libro_id = int(item_iid)
        except (IndexError, ValueError) as e:
            messagebox.showerror("Error", f"No se pudo obtener la información del libro seleccionado: {e}")
            return

        confirm_delete = messagebox.askyesno("Confirmar Eliminación", 
                                            f"¿Está seguro de que desea eliminar el libro '{book_title}' (ID: {libro_id})?\n\n"
                                            "Esta acción es permanente y no se puede deshacer.\n"
                                            "El libro no se podrá eliminar si tiene ventas asociadas.")
        if not confirm_delete:
            return

        if not db.conexion or not db.conexion.is_connected():
            messagebox.showerror("Error de Conexión", "No hay conexión a la base de datos.")
            return

        try:
            db.conexion.start_transaction()

            query_check_sales = "SELECT COUNT(*) FROM venta_libro WHERE vlib_fkLibro = %s"
            cursor_sales = db.ejecutar_query(query_check_sales, (libro_id,))
            
            sales_count = 0
            if cursor_sales:
                result = cursor_sales.fetchone()
                if result:
                    sales_count = result[0]
            
            if sales_count > 0:
                db.conexion.rollback()
                messagebox.showerror("Error al Eliminar", 
                                     f"El libro '{book_title}' (ID: {libro_id}) no puede ser eliminado porque tiene {sales_count} venta(s) asociada(s).\n"
                                     "Considere marcarlo como 'no disponible' o gestionar las ventas primero.")
                return

            query_get_image = "SELECT lib_ruta_imagen FROM libro WHERE lib_id = %s"
            cursor_img = db.ejecutar_query(query_get_image, (libro_id,))
            image_filename_db = None
            if cursor_img:
                img_result = cursor_img.fetchone()
                if img_result and img_result[0]:
                    image_filename_db = img_result[0]

            query_delete_lg = "DELETE FROM libro_genero WHERE libgen_fkLibro = %s"
            db.ejecutar_query(query_delete_lg, (libro_id,)) 

            query_delete_book = "DELETE FROM libro WHERE lib_id = %s"
            cursor_book_delete = db.ejecutar_query(query_delete_book, (libro_id,))

            if cursor_book_delete and cursor_book_delete.rowcount > 0:
                db.conexion.commit()
                messagebox.showinfo("Éxito", f"El libro '{book_title}' (ID: {libro_id}) ha sido eliminado correctamente.")
                
                if image_filename_db:
                    full_image_path = os.path.join(BOOK_COVERS_DIR, image_filename_db)
                    if os.path.exists(full_image_path):
                        try:
                            os.remove(full_image_path)
                            print(f"Imagen {full_image_path} eliminada del sistema de archivos.")
                        except OSError as oe:
                            print(f"ADVERTENCIA: No se pudo eliminar el archivo de imagen {full_image_path}: {oe}")
                            messagebox.showwarning("Advertencia de Imagen", 
                                                   f"El libro fue eliminado de la BD, pero no se pudo borrar el archivo de imagen:\n{image_filename_db}\n\nError: {oe}")
                
                self.load_books()
            elif cursor_book_delete and cursor_book_delete.rowcount == 0:
                db.conexion.rollback()
                messagebox.showwarning("Advertencia", f"No se encontró el libro con ID {libro_id} para eliminar, o ya había sido eliminado.")
            else:
                db.conexion.rollback()
                messagebox.showerror("Error de Base de Datos", f"No se pudo eliminar el libro '{book_title}' (ID: {libro_id}) de la base de datos.")

        except Exception as e:
            if db.conexion and db.conexion.is_connected():
                try:
                    db.conexion.rollback()
                except Exception as rb_e:
                    print(f"Error al intentar hacer rollback: {rb_e}")
            messagebox.showerror("Error Crítico al Eliminar", f"Ocurrió un error inesperado: {e}")
            traceback.print_exc()


if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()

    app_window = BookManagementWindow(master=root)
    
    def on_main_window_close():
        is_real_db = True
        try:
            pass 
        except NameError: 
             pass

        if hasattr(db, 'conexion') and db.conexion and hasattr(db.conexion, 'is_connected') and db.conexion.is_connected():
            if hasattr(db, 'cerrar'):
                print("Cerrando conexión a la base de datos.")
                db.cerrar()
            else:
                print("Advertencia: La instancia 'db' no tiene un método 'cerrar'. La conexión podría no liberarse correctamente.")
        
        root.destroy()

    app_window.protocol("WM_DELETE_WINDOW", on_main_window_close)
    root.mainloop()