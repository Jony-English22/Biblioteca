import sys
import os
import traceback
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import subprocess
import platform as platform_module
from datetime import datetime

system_platform = platform_module.system().lower()

CURRENT_FILE_PATH = os.path.abspath(__file__)
GUI_STORE_DIR = os.path.dirname(CURRENT_FILE_PATH)
PROJECT_ROOT_DIR = os.path.dirname(GUI_STORE_DIR)
if PROJECT_ROOT_DIR not in sys.path:
    sys.path.append(PROJECT_ROOT_DIR)

try:
    from db.ConexionDB import db 
except ImportError as e:
    print(f"ERROR CRÍTICO: No se pudo importar 'db.ConexionDB'. Verifica tu sys.path y la estructura del proyecto.")
    print(f"PROJECT_ROOT_DIR actual (debería estar en sys.path): {PROJECT_ROOT_DIR}")
    print(f"sys.path actual: {sys.path}")
    print(f"Detalle del ImportError: {e}")
    try:
        GRANDPARENT_DIR = os.path.dirname(PROJECT_ROOT_DIR) 
        if GRANDPARENT_DIR not in sys.path:
            sys.path.append(GRANDPARENT_DIR)
        from db.ConexionDB import db
        print("DEBUG: Import alternativo de db.ConexionDB exitoso.")
    except ImportError:
        print("ERROR CRÍTICO: Falló también el import alternativo. Saliendo.")
        sys.exit(1)

BOOK_COVERS_DIR_STORE = os.path.join(PROJECT_ROOT_DIR, 'gui_management', 'book_covers')
print(f"DEBUG: ModernBookStore espera las portadas en: {BOOK_COVERS_DIR_STORE}")
if not os.path.isdir(BOOK_COVERS_DIR_STORE):
    print(f"ADVERTENCIA: El directorio de portadas '{BOOK_COVERS_DIR_STORE}' no existe.")

class ModernBookStore:
    def __init__(self, user_name="Usuario"):
        self.root = tk.Tk()
        self.root.title("Modern BookStore")

        self.user_name = user_name
        self.cart_items = []
        self.current_books_data = []
        self.cart_window = None
        self.final_confirmation_window = None 

        self.colors = {
            'primary': '#4272be', 'secondary': '#2d3339', 'accent': '#236cfe',
            'text': 'white', 'background': '#10181c', 'card': '#2d3339',
            'hover': '#3462aa', 'entry_bg': '#192028', 'entry_focus_border': '#4272be'
        }

        self.root.configure(bg=self.colors['background'])
        self.configure_styles()
        self.create_layout()
        
        try:
            self.root.state('zoomed')
        except tk.TclError:
            print("ADVERTENCIA: No se pudo maximizar la ventana usando state('zoomed'). Usando fallback si es posible.")
            if system_platform == "win32":
                try:
                    import ctypes
                    self.root.geometry("1200x800") 
                    self.center_window(self.root, 1200, 800)
                except Exception as e_win_max:
                    print(f"Error intentando maximizar en Windows con fallback: {e_win_max}")
                    self.root.geometry("1200x800") 
                    self.center_window(self.root, 1200, 800)
            else:
                 self.root.geometry("1200x800") 
                 self.center_window(self.root, 1200, 800)
        self.root.after_idle(self.add_books)

    def configure_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Modern.TFrame', background=self.colors['background'])
        style.configure('Card.TFrame', background=self.colors['card'], relief="solid", borderwidth=1)
        style.configure('Modern.TLabel', background=self.colors['background'], foreground=self.colors['text'], font=('Helvetica', 10))
        style.configure('Header.TLabel', background=self.colors['background'], foreground=self.colors['text'], font=('Helvetica', 24, 'bold'))
        style.configure('Modern.TButton', background=self.colors['primary'], foreground=self.colors['text'], font=('Helvetica', 10, 'bold'), borderwidth=0, padding=5, relief="flat")
        style.map('Modern.TButton', background=[('active', self.colors['hover']), ('pressed', self.colors['hover'])], relief=[('pressed', 'sunken')])
        style.configure('Modern.TEntry',
                        fieldbackground=self.colors['entry_bg'],
                        foreground=self.colors['text'],
                        insertbackground=self.colors['text'],
                        font=('Helvetica', 12),
                        borderwidth=0, relief='flat', highlightthickness=0)
        style.configure('CardTitle.TLabel', background=self.colors['card'], foreground=self.colors['text'], font=('Helvetica', 11, 'bold'))
        style.configure('CardAuthor.TLabel', background=self.colors['card'], foreground=self.colors['text'], font=('Helvetica', 9, 'italic'))
        style.configure('CardPrice.TLabel', background=self.colors['card'], foreground=self.colors['accent'], font=('Helvetica', 10, 'bold'))

        style.configure('Modern.TCombobox', 
                        selectbackground=[('readonly', self.colors['entry_bg'])],
                        fieldbackground=[('readonly', self.colors['entry_bg'])],
                        foreground=[('readonly', self.colors['text'])],
                        arrowcolor=self.colors['text'],
                        bordercolor=self.colors['entry_bg'], 
                        relief='flat',
                        padding=(5,4) 
                       )
        style.map('Modern.TCombobox', 
                  bordercolor=[('focus', self.colors['entry_focus_border']), ('!focus', self.colors['entry_bg'])],
                  fieldbackground=[('readonly','focus', self.colors['entry_bg'])],
                 )

    def create_layout(self):
        self.main_container = ttk.Frame(self.root, style='Modern.TFrame')
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        self.create_header()
        self.create_filters()
        self.create_books_display()

    def create_header(self):
        header = ttk.Frame(self.main_container, style='Modern.TFrame')
        header.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(header, text="BookStore", style='Header.TLabel').pack(side=tk.LEFT, padx=(0,20))
        search_frame = ttk.Frame(header, style='Modern.TFrame')
        search_frame.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=20)
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, style='Modern.TEntry', width=50)
        search_entry.insert(0, "Buscar libro, autor...")
        search_entry.bind("<FocusIn>", lambda event: event.widget.delete(0, tk.END) if event.widget.get() == "Buscar libro, autor..." else None)
        search_entry.bind("<FocusOut>", lambda event: event.widget.insert(0, "Buscar libro, autor...") if not event.widget.get() else None)
        search_entry.bind("<Return>", lambda event: self.perform_search(self.search_var.get()))
        search_entry.pack(side=tk.LEFT, expand=True, fill=tk.X, ipady=5)
        ttk.Button(search_frame, text="Buscar", style='Modern.TButton', command=lambda: self.perform_search(self.search_var.get())).pack(side=tk.LEFT, padx=(10, 0))
        user_cart_frame = ttk.Frame(header, style='Modern.TFrame')
        user_cart_frame.pack(side=tk.RIGHT)
        user_frame = ttk.Frame(user_cart_frame, style='Modern.TFrame')
        user_frame.pack(side=tk.LEFT, padx=(10, 0))
        self.user_icon = self.load_general_image('user.png', size=(24, 24))
        user_icon_label = ttk.Label(user_frame, image=self.user_icon, style='Modern.TLabel')
        user_icon_label.image = self.user_icon
        user_icon_label.pack(side=tk.LEFT)
        self.username_label = ttk.Label(user_frame, text=f"Hola, {self.user_name}", style='Modern.TLabel', cursor="hand2")
        self.username_label.pack(side=tk.LEFT, padx=(5, 0))
        self.username_label.bind("<Button-1>", self.show_user_menu)
        self.user_menu = tk.Menu(self.root, tearoff=0, background=self.colors['card'], foreground=self.colors['text'], activebackground=self.colors['primary'], activeforeground=self.colors['text'])
        self.user_menu.add_command(label="Mi perfil", command=lambda: print("Abrir perfil"))
        self.user_menu.add_separator()
        self.user_menu.add_command(label="Compras", command=lambda: print("Ver compras"))
        book_manage_path = os.path.join(PROJECT_ROOT_DIR, 'gui', 'BookManage.py')
        if not os.path.exists(book_manage_path): book_manage_path = os.path.join(PROJECT_ROOT_DIR, 'gui', 'BookManage.py') # Corregido: ruta duplicada, probable typo.
        if os.path.exists(book_manage_path): self.user_menu.add_command(label="Vender/Gestionar Libros", command=lambda: subprocess.run([sys.executable, book_manage_path]))
        else: self.user_menu.add_command(label="Vender/Gestionar Libros (No encontrado)", state="disabled")
        self.user_menu.add_separator()
        login_script_path = os.path.join(PROJECT_ROOT_DIR, 'Login.py')
        self.user_menu.add_command(label="Salir", command=lambda: [self.root.destroy(), subprocess.run([sys.executable, login_script_path])])
        self.cart_icon = self.load_general_image('carrito.png', size=(24, 24))
        self.cart_button = ttk.Button(user_cart_frame, image=self.cart_icon, text=" Cart (0)", compound=tk.LEFT, style='Modern.TButton', command=self.show_cart)
        self.cart_button.image = self.cart_icon
        self.cart_button.pack(side=tk.LEFT, padx=(10, 0))

    def create_filters(self):
        filter_frame = ttk.Frame(self.main_container, style='Modern.TFrame')
        filter_frame.pack(fill=tk.X, pady=(0, 20))
        ttk.Button(filter_frame, text="Refrescar Libros", style='Modern.TButton', command=self.add_books).pack(side=tk.RIGHT, padx=(10,0))
        postal_code_frame = ttk.Frame(filter_frame, style='Modern.TFrame')
        postal_code_frame.pack(side=tk.LEFT, padx=(0, 20))
        self.location_icon = self.load_general_image('ubicacion.png', size=(20, 20))
        location_label = ttk.Label(postal_code_frame, image=self.location_icon, style='Modern.TLabel')
        location_label.image = self.location_icon
        location_label.pack(side=tk.LEFT)
        ttk.Label(postal_code_frame, text="Ingresa tu\ncódigo postal", style='Modern.TLabel', justify=tk.LEFT).pack(side=tk.LEFT, padx=(5, 0))
        category_frame = ttk.Frame(filter_frame, style='Modern.TFrame')
        category_frame.pack(side=tk.LEFT, padx=(10, 0))
        self.category_label = ttk.Label(category_frame, text="Categorías ▼", style='Modern.TLabel', cursor="hand2")
        self.category_label.pack(side=tk.LEFT)
        self.category_label.bind("<Button-1>", self.show_category_menu)
        self.category_menu = tk.Menu(self.root, tearoff=0, background=self.colors['card'], foreground=self.colors['text'], activebackground=self.colors['primary'], activeforeground=self.colors['text'])
        categories = ['Todos']
        try:
            if db.conexion and db.conexion.is_connected():
                cursor_cat = db.ejecutar_query("SELECT DISTINCT gen_nombre FROM genero WHERE gen_nombre IS NOT NULL AND gen_nombre != '' ORDER BY gen_nombre")
                if cursor_cat:
                    fetched_categories = [row[0] for row in cursor_cat.fetchall() if row[0]]
                    if fetched_categories: categories.extend(fetched_categories)
        except Exception as e: print(f"Error al cargar categorías de la BD: {e}")
        if len(categories) == 1: categories.extend(['Fiction', 'Non-Fiction', 'Science', 'History', 'Art']) 
        for category in categories: self.category_menu.add_command(label=category, command=lambda cat=category: self.filter_books_by_category(cat))

    def show_category_menu(self, event):
        try: self.category_menu.tk_popup(event.x_root, event.y_root + 5)
        except Exception as e: print(f"Error mostrando menú de categorías: {e}")

    def filter_books_by_category(self, category):
        search_val = self.search_var.get()
        if search_val == "Buscar libro, autor...": search_val = ""
        self.perform_search(search_val, category_filter=category)

    def perform_search(self, search_term, category_filter="Todos"):
        current_search = search_term if search_term != "Buscar libro, autor..." else ""
        self.add_books(search_query=current_search, category_filter=category_filter)

    def create_books_display(self):
        self.canvas = tk.Canvas(self.main_container, bg=self.colors['background'], highlightthickness=0)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar = ttk.Scrollbar(self.main_container, orient=tk.VERTICAL, command=self.canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.configure(yscrollcommand=scrollbar.set)
        self.books_frame = ttk.Frame(self.canvas, style='Modern.TFrame')
        self.canvas_frame_id = self.canvas.create_window((0, 0), window=self.books_frame, anchor='nw')
        self.books_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind('<Configure>', self.on_canvas_configure)
        self.root.bind_all("<MouseWheel>", self._on_mousewheel, add="+")
        self.root.bind_all("<Button-4>", self._on_mousewheel, add="+") 
        self.root.bind_all("<Button-5>", self._on_mousewheel, add="+") 

    def on_canvas_configure(self, event):
        if event.width > 1 :
            self.canvas.itemconfig(self.canvas_frame_id, width=event.width)
            self.regrid_books()

    def regrid_books(self):
        for widget in self.books_frame.winfo_children(): widget.destroy()
        if not self.current_books_data:
            ttk.Label(self.books_frame, text="No se encontraron libros.", style='Modern.TLabel', font=('Helvetica', 12)).grid(row=0, column=0, pady=20, padx=20)
            self.books_frame.update_idletasks(); self.canvas.configure(scrollregion=self.canvas.bbox("all"))
            return
        canvas_width = self.canvas.winfo_width()
        if canvas_width <= 1: return
        num_cols = max(1, canvas_width // 200) 
        for i, book_data in enumerate(self.current_books_data):
            self.create_book_card(book_data).grid(row=i // num_cols, column=i % num_cols, padx=10, pady=10, sticky='n')
        for i in range(num_cols): self.books_frame.grid_columnconfigure(i, weight=1)
        self.books_frame.update_idletasks()
        bbox = self.canvas.bbox("all")
        if bbox: self.canvas.configure(scrollregion=bbox)

    def add_books(self, search_query=None, category_filter="Todos"):
        print(f"DEBUG: Iniciando add_books. Búsqueda: '{search_query}', Categoría: '{category_filter}'")
        self.current_books_data = []
        try:
            if not db.conexion or not db.conexion.is_connected():
                messagebox.showerror("Error de Conexión", "No se puede conectar a la base de datos.")
                self.regrid_books(); return
            author_concat_sql = "CONCAT_WS(' ', a.aut_nombre, a.aut_apellido)"
            base_query = (f"SELECT l.lib_id, l.lib_nombre, {author_concat_sql} AS author, "
                          f"l.lib_precio, GROUP_CONCAT(DISTINCT g.gen_nombre SEPARATOR ', ') AS category_list, "
                          f"l.lib_ruta_imagen FROM libro l "
                          f"LEFT JOIN autor a ON l.lib_fkAutor = a.aut_id "
                          f"LEFT JOIN libro_genero lg ON l.lib_id = lg.libgen_fkLibro "
                          f"LEFT JOIN genero g ON lg.libgen_fkGenero = g.gen_id")
            conditions, params = [], []
            if search_query and search_query.strip():
                conditions.append(f"(l.lib_nombre LIKE %s OR {author_concat_sql} LIKE %s)"); term = f"%{search_query.strip()}%"; params.extend([term, term])
            if category_filter and category_filter != "Todos":
                 conditions.append("l.lib_id IN (SELECT libgen_fkLibro FROM libro_genero lg_f JOIN genero g_f ON lg_f.libgen_fkGenero = g_f.gen_id WHERE g_f.gen_nombre = %s)"); params.append(category_filter)
            final_query = base_query
            if conditions: final_query += " WHERE " + " AND ".join(conditions)
            final_query += " GROUP BY l.lib_id, l.lib_nombre, author, l.lib_precio, l.lib_ruta_imagen ORDER BY l.lib_nombre"
            print(f"DEBUG SQL Query: {final_query}"); print(f"DEBUG SQL Params: {params}")
            cursor = db.ejecutar_query(final_query, tuple(params))
            if cursor:
                results = cursor.fetchall()
                print(f"DEBUG: {len(results)} libros encontrados en la BD.")
                for row in results: self.current_books_data.append({"id": row[0], "title": row[1] or "N/A", "author": (row[2] if row[2] and row[2].strip() else "N/A"), "price": f"${row[3]:.2f}" if row[3] is not None else "$0.00", "category": row[4] or "N/A", "image_file": row[5]})
            self.regrid_books()
        except Exception as e: messagebox.showerror("Error", f"Error al cargar libros: {e}"); traceback.print_exc(); self.current_books_data = []; self.regrid_books()

    def create_book_card(self, book_data):
        card = ttk.Frame(self.books_frame, style='Card.TFrame', width=180, height=330); card.pack_propagate(False)
        cover_image_tk = None
        if book_data.get("image_file"):
            full_image_path = os.path.join(BOOK_COVERS_DIR_STORE, book_data["image_file"])
            if os.path.exists(full_image_path):
                try: cover_image_tk = ImageTk.PhotoImage(Image.open(full_image_path).resize((120, 170), Image.Resampling.LANCZOS))
                except Exception as e: print(f"Error img {book_data['image_file']}: {e}")
        if not cover_image_tk: cover_image_tk = self.get_placeholder_cover((120, 170))
        cover_label = ttk.Label(card, image=cover_image_tk, background=self.colors['card'], anchor="center"); cover_label.image = cover_image_tk; cover_label.pack(pady=(10,5), fill=tk.X)
        title_text = book_data.get('title', 'N/A'); author_text = book_data.get('author', 'N/A'); category_text = book_data.get('category', 'N/A'); price_text = book_data.get('price', '$0.00')
        ttk.Label(card,text=title_text,style='CardTitle.TLabel',wraplength=160,anchor="center",justify="center").pack(fill=tk.X,padx=10,pady=(5,2))
        ttk.Label(card,text=author_text,style='CardAuthor.TLabel',wraplength=160,anchor="center",justify="center").pack(fill=tk.X,padx=10,pady=2)
        ttk.Label(card,text=category_text,style='CardAuthor.TLabel',wraplength=160,anchor="center",justify="center", font=('Helvetica', 8)).pack(fill=tk.X,padx=10,pady=2)
        ttk.Label(card, text=str(price_text), style='CardPrice.TLabel', anchor="center").pack(pady=5)
        ttk.Button(card, text="Añadir al carrito", style='Modern.TButton', command=lambda b=book_data: self.add_to_cart(b), width=20).pack(pady=(1,10),padx=10,fill=tk.X)
        return card

    def get_placeholder_cover(self, size=(120, 170)): return ImageTk.PhotoImage(Image.new('RGB', size, color=self.colors['secondary']))

    def show_cart(self):
        if self.cart_window is None or not self.cart_window.winfo_exists():
            self.cart_window = tk.Toplevel(self.root); self.cart_window.title("Resumen de compra"); self.cart_window.geometry("500x600"); self.cart_window.configure(bg=self.colors['background']); self.cart_window.resizable(False, False); self.center_window(self.cart_window, 500, 600)
            main_frame = ttk.Frame(self.cart_window, style='Modern.TFrame', padding=20); main_frame.pack(fill=tk.BOTH, expand=True)
            ttk.Label(main_frame, text="Resumen de compra", style='Header.TLabel', font=('Helvetica', 16, 'bold')).pack(pady=(0, 20))
            self.cart_items_frame = ttk.Frame(main_frame, style='Modern.TFrame'); self.cart_items_frame.pack(fill=tk.BOTH, expand=True)
            self.summary_frame = ttk.Frame(main_frame, style='Modern.TFrame'); self.summary_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=(20, 0))
            self.update_cart_display()
        else: self.cart_window.lift()

    def remove_item_from_cart(self, item_data_ref):
        item_id_to_remove = item_data_ref.get('id')
        if item_id_to_remove is None:
            print("DEBUG: remove_item_from_cart llamado sin ID de item.")
            return
        original_length = len(self.cart_items)
        self.cart_items = [item for item in self.cart_items if item.get('id') != item_id_to_remove]
        if len(self.cart_items) < original_length:
            self.update_cart_button(); self.update_cart_display() 
        else:
            print(f"DEBUG: Item ID {item_id_to_remove} no encontrado para eliminar.")

    def update_cart_display(self):
        if not self.cart_window or not self.cart_window.winfo_exists(): return
        for widget in self.cart_items_frame.winfo_children(): widget.destroy()
        for widget in self.summary_frame.winfo_children(): widget.destroy()
        
        if not self.cart_items:
            ttk.Label(self.cart_items_frame, text="Tu carrito está vacío.", style='Modern.TLabel', wraplength=400, justify=tk.CENTER).pack(pady=20, expand=True)
            ttk.Button(self.summary_frame, text="Continuar compra", style='Modern.TButton', state=tk.DISABLED).pack(fill=tk.X, pady=(10,0))
            self.cart_window.title(f"Resumen de compra ({len(self.cart_items)} items)")
            return
        
        total_price = 0
        for item_data in self.cart_items:
            try: price_str = str(item_data.get('price','$0.00')).replace('$', ''); price = float(price_str)
            except ValueError: price = 0.0
            quantity = item_data.get('quantity', 1); item_total = price * quantity; total_price += item_total
            
            item_frame = ttk.Frame(self.cart_items_frame, style='Card.TFrame', padding=10); item_frame.pack(fill=tk.X, pady=5)
            info_frame = tk.Frame(item_frame, background=self.colors['card']); info_frame.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 5))
            
            title_text=item_data.get('title','N/A'); author_text=item_data.get('author','N/A')
            ttk.Label(info_frame, text=title_text, style='Modern.TLabel', background=self.colors['card'], font=('Helvetica',10,'bold')).pack(anchor='w')
            ttk.Label(info_frame, text=author_text, style='Modern.TLabel', background=self.colors['card'], font=('Helvetica',9,'italic')).pack(anchor='w',pady=(0,3))
            
            controls_frame = tk.Frame(item_frame, background=self.colors['card']); controls_frame.pack(side=tk.RIGHT, fill=tk.Y)
            btn_font=('Helvetica',10)
            ttk.Button(controls_frame, text="-", width=2, command=lambda current_item=item_data: self.change_quantity(current_item,-1), style='Modern.TButton').pack(side=tk.LEFT,padx=(0,2),pady=(0,2))
            ttk.Label(controls_frame, text=str(quantity), style='Modern.TLabel', background=self.colors['card'], width=2,anchor='center',font=btn_font).pack(side=tk.LEFT,padx=5,pady=(0,2))
            ttk.Button(controls_frame, text="+", width=2, command=lambda current_item=item_data: self.change_quantity(current_item,1), style='Modern.TButton').pack(side=tk.LEFT,padx=(2,5),pady=(0,2))
            ttk.Label(controls_frame, text=f"${item_total:.2f}", style='Modern.TLabel', background=self.colors['card'], font=('Helvetica',10,'bold'),width=8,anchor='e').pack(side=tk.LEFT,padx=(5,10),pady=(0,2))
            delete_button = ttk.Button(controls_frame, text="Eliminar", command=lambda current_item=item_data: self.remove_item_from_cart(current_item), style='Modern.TButton', width=8) 
            delete_button.pack(side=tk.LEFT, padx=(5,0), pady=(0,2))
            
        total_frame = ttk.Frame(self.summary_frame, style='Modern.TFrame'); total_frame.pack(fill=tk.X, pady=(10,10))
        ttk.Label(total_frame, text="Total", style='Header.TLabel',font=('Helvetica',14,'bold')).pack(side=tk.LEFT)
        ttk.Label(total_frame, text=f"${total_price:.2f}", style='Header.TLabel',font=('Helvetica',14,'bold')).pack(side=tk.RIGHT)
        ttk.Button(self.summary_frame, text="Continuar compra", style='Modern.TButton', command=self.checkout).pack(fill=tk.X, pady=(10,0))
        self.cart_window.title(f"Resumen de compra ({len(self.cart_items)} items)")

    def add_to_cart(self, book_data):
        try:
            if 'price' not in book_data or book_data['price'] is None: messagebox.showerror("Error", f"Libro '{book_data.get('title','N/A')}' sin precio."); return
            float(str(book_data['price']).replace('$', ''))
            if 'id' not in book_data: messagebox.showerror("Error", f"Libro '{book_data.get('title','N/A')}' sin ID."); return
        except ValueError: messagebox.showerror("Error", f"Libro '{book_data.get('title','N/A')}' precio inválido."); return
        for item in self.cart_items:
            if item.get('id') == book_data.get('id'): item['quantity'] = item.get('quantity', 1) + 1; self.update_cart_button(); 
            if self.cart_window and self.cart_window.winfo_exists(): self.update_cart_display(); return
        book_copy = book_data.copy(); book_copy['quantity'] = 1; self.cart_items.append(book_copy); self.update_cart_button()
        if self.cart_window and self.cart_window.winfo_exists(): self.update_cart_display()

    def change_quantity(self, item_data_ref, delta):
        for i, cart_item in enumerate(self.cart_items):
            if cart_item.get('id') == item_data_ref.get('id'):
                cart_item['quantity'] = max(0, cart_item.get('quantity', 1) + delta)
                if cart_item['quantity'] == 0: del self.cart_items[i]
                self.update_cart_button(); self.update_cart_display(); break
    
    def checkout(self):
        if not self.cart_items:
            messagebox.showinfo("Info", "Carrito vacío.")
            return
        self.show_final_confirmation_screen()

    def get_customer_full_name(self, username):
        try:
            if db.conexion and db.conexion.is_connected():
                query_nombre_apellidos = "SELECT usu_nombre, usu_apellidos FROM usuario WHERE usu_usuario = %s"
                cursor = db.ejecutar_query(query_nombre_apellidos, (username,))
                if cursor:
                    result = cursor.fetchone()
                    if result:
                        nombre = result[0] if result[0] else ""
                        apellidos = result[1] if result[1] else ""
                        full_name = f"{nombre} {apellidos}".strip()
                        if full_name: return full_name
                try:
                    query_nombre_completo = "SELECT usu_nombre_completo FROM usuario WHERE usu_usuario = %s"
                    cursor_nc = db.ejecutar_query(query_nombre_completo, (username,))
                    if cursor_nc:
                        result_nc = cursor_nc.fetchone()
                        if result_nc and result_nc[0]: return result_nc[0].strip()
                except Exception: pass
            return username 
        except Exception as e:
            print(f"Error al obtener nombre completo del cliente: {e}")
            traceback.print_exc()
            return username

    def get_client_id(self, username):
        client_id = None
        try:
            if not db.conexion or not db.conexion.is_connected():
                print("Error: Sin conexión a la BD para obtener client_id.")
                return None

            query_user_id = "SELECT usu_id FROM usuario WHERE usu_usuario = %s"
            cursor_user = db.ejecutar_query(query_user_id, (username,))
            user_result = cursor_user.fetchone() if cursor_user else None

            if user_result:
                user_id = user_result[0]
                query_client_id = "SELECT cli_id FROM cliente WHERE cli_fkUsuario = %s"
                cursor_client = db.ejecutar_query(query_client_id, (user_id,))
                client_result = cursor_client.fetchone() if cursor_client else None
                
                if client_result:
                    client_id = client_result[0]
                else:
                    print(f"ADVERTENCIA: No se encontró un registro en la tabla 'cliente' para el usu_id {user_id} (usuario: '{username}').")
            else:
                print(f"ADVERTENCIA: No se encontró usu_id para el usuario '{username}' en la tabla 'usuario'.")
            
            return client_id
        except Exception as e:
            if "Unknown column" in str(e) or "no such table" in str(e).lower():
                 print(f"ERROR ESTRUCTURA BD: Parece que la tabla 'cliente' o 'usuario', o las columnas 'cli_fkUsuario', 'usu_id', 'usu_usuario' no existen o tienen nombres diferentes.")
            print(f"Error detallado al obtener ID de cliente para '{username}': {e}")
            traceback.print_exc()
            return None

    def show_final_confirmation_screen(self):
        if self.final_confirmation_window and self.final_confirmation_window.winfo_exists():
            self.final_confirmation_window.lift()
            return

        self.final_confirmation_window = tk.Toplevel(self.root)
        self.final_confirmation_window.title("Confirmación de Pedido")
        self.final_confirmation_window.geometry("600x700")
        self.final_confirmation_window.configure(bg=self.colors['background'])
        self.final_confirmation_window.resizable(False, False)
        self.center_window(self.final_confirmation_window, 600, 700)
        
        parent_window = self.cart_window if self.cart_window and self.cart_window.winfo_exists() else self.root
        self.final_confirmation_window.transient(parent_window)
        self.final_confirmation_window.grab_set()

        main_frame = ttk.Frame(self.final_confirmation_window, style='Modern.TFrame', padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        customer_name = self.get_customer_full_name(self.user_name)
        current_date_display = datetime.now().strftime("%d/%m/%Y")
        
        ttk.Label(main_frame, text=f"Cliente: {customer_name}", style='Modern.TLabel', font=('Helvetica', 12, 'bold')).pack(anchor='w', pady=(0, 2))
        ttk.Label(main_frame, text=f"Fecha: {current_date_display}", style='Modern.TLabel', font=('Helvetica', 10)).pack(anchor='w', pady=(0, 10))

        ttk.Separator(main_frame, orient='horizontal').pack(fill='x', pady=(5,10))
        
        ttk.Label(main_frame, text="Resumen del Pedido:", style='Modern.TLabel', font=('Helvetica', 11, 'bold')).pack(anchor='w', pady=(0, 5))

        products_header_frame = ttk.Frame(main_frame, style='Modern.TFrame')
        products_header_frame.pack(fill=tk.X, pady=(0,5))
        ttk.Label(products_header_frame, text="Producto", style='Modern.TLabel', font=('Helvetica', 10, 'bold')).pack(side=tk.LEFT, expand=True, fill=tk.X)
        ttk.Label(products_header_frame, text="Cant.", style='Modern.TLabel', font=('Helvetica', 10, 'bold'), width=5, anchor='c').pack(side=tk.LEFT, padx=5)
        ttk.Label(products_header_frame, text="Precio Unit.", style='Modern.TLabel', font=('Helvetica', 10, 'bold'), width=10, anchor='e').pack(side=tk.LEFT, padx=5)
        ttk.Label(products_header_frame, text="Subtotal", style='Modern.TLabel', font=('Helvetica', 10, 'bold'), width=10, anchor='e').pack(side=tk.LEFT, padx=5)

        products_area_frame = ttk.Frame(main_frame, style='Modern.TFrame') 
        products_area_frame.pack(fill=tk.BOTH, expand=True, pady=(0,10))

        confirm_products_canvas = tk.Canvas(products_area_frame, bg=self.colors['background'], highlightthickness=0)
        confirm_products_scrollbar = ttk.Scrollbar(products_area_frame, orient="vertical", command=confirm_products_canvas.yview)
        self.confirm_products_list_frame = ttk.Frame(confirm_products_canvas, style='Modern.TFrame')

        self.confirm_products_list_frame.bind("<Configure>", lambda e: confirm_products_canvas.configure(scrollregion=confirm_products_canvas.bbox("all")))
        confirm_canvas_window = confirm_products_canvas.create_window((0, 0), window=self.confirm_products_list_frame, anchor="nw")
        confirm_products_canvas.configure(yscrollcommand=confirm_products_scrollbar.set)
        
        confirm_products_canvas.pack(side="left", fill="both", expand=True)
        confirm_products_scrollbar.pack(side="right", fill="y")
        confirm_products_canvas.bind('<Configure>', lambda e, canvas=confirm_products_canvas, frame_id=confirm_canvas_window: canvas.itemconfig(frame_id, width=e.width))

        total_purchase_price = 0
        for item_data in self.cart_items:
            item_display_frame = ttk.Frame(self.confirm_products_list_frame, style='Modern.TFrame', padding=(0, 3))
            item_display_frame.pack(fill=tk.X)

            title = item_data.get('title', 'N/A')
            quantity = item_data.get('quantity', 1)
            price_str = str(item_data.get('price', '$0.00')).replace('$', '')
            try: unit_price = float(price_str)
            except ValueError: unit_price = 0.0
            subtotal = unit_price * quantity
            total_purchase_price += subtotal

            ttk.Label(item_display_frame, text=title, style='Modern.TLabel', wraplength=220).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0,5)) 
            ttk.Label(item_display_frame, text=str(quantity), style='Modern.TLabel', width=5, anchor='c').pack(side=tk.LEFT, padx=5)
            ttk.Label(item_display_frame, text=f"${unit_price:.2f}", style='Modern.TLabel', width=10, anchor='e').pack(side=tk.LEFT, padx=5)
            ttk.Label(item_display_frame, text=f"${subtotal:.2f}", style='Modern.TLabel', width=10, anchor='e').pack(side=tk.LEFT, padx=5)
        
        ttk.Separator(main_frame, orient='horizontal').pack(fill='x', pady=10)
        
        total_frame = ttk.Frame(main_frame, style='Modern.TFrame')
        total_frame.pack(fill=tk.X, pady=(5, 10))
        ttk.Label(total_frame, text="Total de la compra:", style='Modern.TLabel', font=('Helvetica', 12, 'bold')).pack(side=tk.LEFT)
        ttk.Label(total_frame, text=f"${total_purchase_price:.2f}", style='Modern.TLabel', font=('Helvetica', 12, 'bold')).pack(side=tk.RIGHT)

        payment_frame = ttk.Frame(main_frame, style='Modern.TFrame')
        payment_frame.pack(fill=tk.X, pady=(5, 15))
        ttk.Label(payment_frame, text="Forma de pago:", style='Modern.TLabel', font=('Helvetica', 10, 'bold')).pack(side=tk.LEFT, anchor='w', padx=(0,10))
        
        payment_options = ["Efectivo al recibir", "Tarjeta de Crédito (Online)", "Transferencia Bancaria"]
        self.payment_method_var = tk.StringVar(value=payment_options[0])
        payment_combo = ttk.Combobox(payment_frame, textvariable=self.payment_method_var, values=payment_options, 
                                     state="readonly", style='Modern.TCombobox', font=('Helvetica', 10), width=30)
        payment_combo.pack(side=tk.LEFT, expand=True, fill=tk.X)

        buttons_frame = ttk.Frame(main_frame, style='Modern.TFrame')
        buttons_frame.pack(fill=tk.X, pady=(20, 0), side=tk.BOTTOM)

        ttk.Button(buttons_frame, text="Confirmar Pedido", style='Modern.TButton', 
                   command=lambda: self.process_final_purchase(total_purchase_price)).pack(side=tk.RIGHT)
        ttk.Button(buttons_frame, text="Cancelar", style='Modern.TButton', 
                   command=self.final_confirmation_window.destroy).pack(side=tk.RIGHT, padx=(0,10))
        
    def process_final_purchase(self, total_value):
        payment_method = self.payment_method_var.get()
        num_items = sum(item['quantity'] for item in self.cart_items)
        customer_display_name = self.get_customer_full_name(self.user_name)
        
        client_id = self.get_client_id(self.user_name)
       
        current_date_db = datetime.now().strftime("%Y-%m-%d")

        print(f"DEBUG: Iniciando procesamiento de compra. Cliente: {self.user_name} (ID BD: {client_id}), Items: {num_items}, Total: ${total_value:.2f}, Método de pago: {payment_method}, Fecha BD: {current_date_db}")
        
        try:
            if not db.conexion or not db.conexion.is_connected():
                messagebox.showerror("Error de Conexión", "No se puede conectar a la base de datos para procesar la compra.")
                return
            
            db.conexion.start_transaction() 

            query_venta = """
                INSERT INTO venta (ven_fkCliente, ven_fecha, ven_metodoPago, ven_total) 
                VALUES (%s, %s, %s, %s)
            """
            params_venta = (client_id, current_date_db, payment_method, total_value)
            
            # MODIFICADO: Eliminado commit=False
            cursor_venta = db.ejecutar_query(query_venta, params_venta) 
            
            if not cursor_venta: 
                db.conexion.rollback()
                messagebox.showerror("Error de Base de Datos", "No se pudo registrar la cabecera de la venta (cursor nulo).")
                return

            venta_id = cursor_venta.lastrowid 
            
            if not venta_id: 
                db.conexion.rollback()
                messagebox.showerror("Error de Base de Datos", "No se pudo obtener el ID de la venta registrada.")
                return
            
            print(f"DEBUG: Venta registrada con ID: {venta_id}")

            query_detalle = """
                INSERT INTO venta_libro (vlib_fkVenta, vlib_fkLibro, vlib_cant, vlib_punit) 
                VALUES (%s, %s, %s, %s)
            """
            for item in self.cart_items:
                book_id = item.get('id')
                quantity = item.get('quantity')
                unit_price_str = str(item.get('price','$0.00')).replace('$','')
                try:
                    unit_price = float(unit_price_str)
                except ValueError:
                    print(f"Error: Precio inválido para el libro ID {book_id} en el carrito. Saltando este ítem en detalle de venta.")
                    continue 

                params_detalle = (venta_id, book_id, quantity, unit_price)
                # MODIFICADO: Eliminado commit=False
                cursor_detalle = db.ejecutar_query(query_detalle, params_detalle)
                if not cursor_detalle:
                    db.conexion.rollback()
                    messagebox.showerror("Error de Base de Datos", f"No se pudo registrar el detalle del libro ID {book_id}.")
                    return
            
            db.conexion.commit() 
            print("DEBUG: Venta y detalles registrados exitosamente en la base de datos.")

            self.cart_items.clear()
            self.update_cart_button()
            
            if self.final_confirmation_window and self.final_confirmation_window.winfo_exists():
                self.final_confirmation_window.destroy()
            
            if self.cart_window and self.cart_window.winfo_exists():
                self.cart_window.destroy()

            messagebox.showinfo("Compra Exitosa", f"¡Gracias por tu compra, {customer_display_name}!\n\nTotal: ${total_value:.2f}\nMétodo de pago: {payment_method}\nFecha: {datetime.now().strftime('%d/%m/%Y')}\n\nTu pedido (ID: {venta_id}) ha sido procesado.")

        except Exception as e:
            if db.conexion and db.conexion.is_connected(): 
                try:
                    db.conexion.rollback()
                    print("DEBUG: Transacción revertida debido a un error.")
                except Exception as rb_e:
                    print(f"Error al intentar hacer rollback: {rb_e}")
            messagebox.showerror("Error Crítico Durante la Compra", f"No se pudo completar la compra: {e}")
            traceback.print_exc()
            return

    def update_cart_button(self): 
        self.cart_button.configure(text=f" Cart ({sum(item.get('quantity',1) for item in self.cart_items)})")
    
    def load_general_image(self, image_name, size=(100,150)):
        img_path = os.path.join(PROJECT_ROOT_DIR,'img',image_name)
        try: return ImageTk.PhotoImage(Image.open(img_path).resize(size,Image.Resampling.LANCZOS))
        except FileNotFoundError: print(f"WARN: Img {image_name} not found at {img_path}."); return self.get_placeholder_cover(size)
        except Exception as e: print(f"WARN: Img {image_name} err: {e}."); return self.get_placeholder_cover(size)

    def _on_mousewheel(self, event):
        delta_scroll = 0
        if system_platform == "win32" or system_platform == "darwin":
            delta_scroll = -1 if event.delta > 0 else 1
        elif event.num == 4: delta_scroll = -1
        elif event.num == 5: delta_scroll = 1
        
        if self.canvas and delta_scroll != 0:
            self.canvas.yview_scroll(delta_scroll, "units")
            
    def show_user_menu(self, event):
        try: self.user_menu.tk_popup(event.x_root, event.y_root + 5)
        except Exception as e: print(f"Error user menu: {e}")
        
    def center_window(self, window, width, height):
        window.update_idletasks(); screen_width = window.winfo_screenwidth(); screen_height = window.winfo_screenheight()
        x = (screen_width // 2) - (width // 2); y = (screen_height // 2) - (height // 2); window.geometry(f"{width}x{height}+{x}+{y-30}")
    
    def run(self): self.root.mainloop()

if __name__ == "__main__":
    user_name = sys.argv[1] if len(sys.argv) > 1 else "Invitado"
    try: app = ModernBookStore(user_name); app.run()
    except Exception as e: messagebox.showerror("Error Crítico", f"Error: {e}"); traceback.print_exc()