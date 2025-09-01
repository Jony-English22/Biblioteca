from customtkinter import *
from tkinter import *
from PIL import Image, ImageTk
import os
import subprocess
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db.ConexionDB import ConexionDB
import bcrypt
from tkinter import messagebox

# Colors
background_color = "#10181c"
entry_color = "#192028"
entry_focus_color = "#4272be"
button_color = "#4272be"  # Azul para el botón de login
google_button_color = "#2d3339"  # Color para el botón de Google

# Window
root = Tk()
root.resizable(False, False)
root.title("Biblioteca")
root.config(bg=background_color)

# Main Frame para centrar todo el contenido
main_frame = Frame(root, bg=background_color)
main_frame.pack(expand=True, fill='both', padx=50, pady=50)

logo = Label(main_frame,
             text="Biblioteca",
             font=("Montserrat Bold", 24),
             bg=background_color,
             fg="white")
logo.pack(pady=(0, 30))

# Email
txt_email = CTkEntry(main_frame,
                     width=300,
                     placeholder_text="Enter your user or email",
                     border_width=0,
                     bg_color=background_color,
                     font=("Montserrat", 16),
                     text_color="white",
                     fg_color=entry_color)
txt_email.pack(pady=10)

# Password
txt_password = CTkEntry(main_frame,
                        width=300,
                        placeholder_text="Enter your password",
                        show='*',
                        border_width=0,
                        bg_color=background_color,
                        font=('Montserrat', 16),
                        text_color="white",
                        fg_color=entry_color)
txt_password.pack(pady=10)

# Create initial placeholder for login button
btn_login = None

# Create Account / Sign Up
signup_frame = Frame(main_frame, bg=background_color)
signup_frame.pack(pady=5)

lbl_signup = Label(signup_frame,
                   bg=background_color,
                   fg="gray",
                   text="Don't have an account?",
                   font=("Montserrat Medium", 10))
lbl_signup.pack(side=LEFT)

btn_signup = Button(signup_frame,
                    border=0,
                    bg=background_color,
                    fg="#236cfe",
                    text="Sign Up",
                    font=("Monserrat Medium", 10),
                    cursor="hand2",
                    activebackground=background_color,
                    activeforeground="white",
                    command=lambda: [root.destroy(), subprocess.run(['python', os.path.join(file_path, 'Register.py')])])
btn_signup.pack(side=LEFT, padx=(5, 0))


# Forgot Password (Movido debajo del Sign Up)
btn_forgot_password = Button(main_frame,
                         border=0,
                         bg=background_color,
                         fg="#236cfe",
                         text="¿Olvidaste tu Contraseña?",
                         font=("Monserrat Medium", 10),
                         cursor="hand2",
                         activebackground=background_color,
                         activeforeground="white")
btn_forgot_password.pack(pady=5)

# Google Login
google_frame = Frame(main_frame, bg=background_color)
google_frame.pack(pady=10)

file_path = os.path.dirname(os.path.realpath(__file__))
google_logo = CTkImage(Image.open(os.path.join(os.path.dirname(file_path), "img", "google.png")), size=(20, 20))

btn_google = CTkButton(google_frame,
                       image=google_logo,
                       width=300,
                       height=45,
                       corner_radius=8,
                       text="Iniciar sesión con Google",
                       border_width=0,
                       bg_color=background_color,
                       font=("Montserrat", 14),
                       fg_color=google_button_color,
                       hover_color="#363b3f",
                       cursor="hand2")
btn_google.pack()

# ----- Funciones ----- #

def verificar_credenciales():
    user_input = txt_email.get()
    password = txt_password.get()
    
    if not user_input or not password:
        messagebox.showerror("Error", "Por favor ingrese todos los campos")
        return
    
    try:
        db = ConexionDB()
        # Buscar por email o username
        query = "SELECT cli_id, cli_password, cli_nombre FROM cliente WHERE cli_correo = %s OR cli_nombre = %s"
        cursor = db.ejecutar_query(query, (user_input, user_input))
        
        if cursor:
            result = cursor.fetchone()
            if result:
                user_id, hashed_password, name = result
                # Verificar la contraseña
                if bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8')):
                    messagebox.showinfo("Éxito", f"Bienvenido {name}")
                    root.destroy()
                    subprocess.run(['python', os.path.join(os.path.dirname(os.path.realpath(__file__)), 'modern_store.py'), name])
                else:
                    messagebox.showerror("Error", "Contraseña incorrecta")
            else:
                messagebox.showerror("Error", "Usuario no encontrado")
        
    except Exception as e:
        messagebox.showerror("Error", f"Error al verificar credenciales: {e}")
    finally:
        if 'db' in locals() and db.conexion and db.conexion.is_connected():
            db.cerrar()

# Email Function
def email_enter(event):
    txt_email.configure(border_color=entry_focus_color)

def email_leave(event):
    txt_email.configure(border_color=background_color)

# Password Function
def password_enter(event):
    txt_password.configure(border_color=entry_focus_color)

def password_leave(event):
    txt_password.configure(border_color=background_color)

# Lost Focus Function
def lost_focus(event):
    if event.widget == root:
        root.focus()

# Bind the events
txt_email.bind('<FocusIn>', email_enter)
txt_email.bind('<FocusOut>', email_leave)
txt_password.bind('<FocusIn>', password_enter)
txt_password.bind('<FocusOut>', password_leave)
root.bind("<Button-1>", lost_focus)

# Create login button after functions are defined
btn_login = CTkButton(main_frame,
                      width=300,
                      height=45,
                      corner_radius=8,
                      text="INICIAR SESIÓN",
                      border_width=0,
                      bg_color=background_color,
                      font=("Montserrat Medium", 16),
                      fg_color=button_color,
                      hover_color="#3462aa",
                      cursor="hand2",
                      command=verificar_credenciales)
if btn_login:  # Only pack if not already packed
    btn_login.pack(pady=10)

#Center window

root.update_idletasks()
width = 400  # Ancho fijo para la ventana
height = 500  # Alto fijo para la ventana
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

x = (screen_width - width) // 2
y = (screen_height - height) // 2

root.geometry(f'{width}x{height}+{x}+{y-30}')

root.mainloop()
