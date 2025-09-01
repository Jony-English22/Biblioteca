import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from customtkinter import *
from tkinter import *
import os
import subprocess
import bcrypt;
from db.ConexionDB import ConexionDB
from PIL import Image, ImageTk

# Colors
background_color = "#10181c"
entry_color = "#192028"
entry_focus_color = "#4272be"
button_color = "#4272be"

# Window
register_window = Tk()
register_window.resizable(False, False)
register_window.title("Crear cuenta")
register_window.config(bg=background_color)

# Main Frame
main_frame = Frame(register_window, bg=background_color)
main_frame.pack(expand=True, fill='both', padx=50, pady=50)

# Title
lbl_title = Label(main_frame,
                  text="Crear cuenta",
                  font=("Montserrat Bold", 18),
                  bg=background_color,
                  fg="white")
lbl_title.pack(pady=(0, 20))

# Name Entry
lbl_name = Label(main_frame,
                 text="Nombre",
                 font=("Montserrat", 12),
                 bg=background_color,
                 fg="white")
lbl_name.pack(anchor="w", pady=(10, 5))

entry_name = CTkEntry(main_frame,
                       width=300,
                       placeholder_text="Nombre y apellido",
                       border_width=0,
                       bg_color=background_color,
                       font=("Montserrat", 12),
                       text_color="white",
                       fg_color=entry_color)
entry_name.pack(pady=(0, 0)) # Adjusted padding

lbl_name_error = Label(main_frame, text="", font=("Montserrat", 10), bg=background_color, fg="red")
lbl_name_error.pack(anchor="w", padx=(0, 0), pady=(0, 10)) # Placeholder for error message

# Email Entry
lbl_email = Label(main_frame,
                  text="Correo electrónico",
                  font=("Montserrat", 12),
                  bg=background_color,
                  fg="white")
lbl_email.pack(anchor="w", pady=(10, 5))

entry_email = CTkEntry(main_frame,
                        width=300,
                        placeholder_text="Correo electrónico",
                        border_width=0,
                        bg_color=background_color,
                        font=("Montserrat", 12),
                        text_color="white",
                        fg_color=entry_color)
entry_email.pack(pady=(0, 0)) # Adjusted padding

lbl_email_error = Label(main_frame, text="", font=("Montserrat", 10), bg=background_color, fg="red")
lbl_email_error.pack(anchor="w", padx=(0, 0), pady=(0, 10)) # Placeholder for error message

# Password Entry
lbl_password = Label(main_frame,
                     text="Contraseña",
                     font=("Montserrat", 12),
                     bg=background_color,
                     fg="white")
lbl_password.pack(anchor="w", pady=(10, 5))

password_frame = Frame(main_frame, bg=background_color) # Frame to hold password entry and toggle button
password_frame.pack(anchor="w", fill="x")

entry_password = CTkEntry(password_frame,
                           width=270, # Adjusted width to make space for toggle button
                           placeholder_text="Al menos 6 caracteres",
                           show='*',
                           border_width=0,
                           bg_color=background_color,
                           font=("Montserrat", 12),
                           text_color="white",
                           fg_color=entry_color)
entry_password.pack(side=LEFT, pady=(0, 0), padx=(0, 5))

# Password visibility toggle button (text-based)
password_toggle_button = Button(password_frame,
                                text="Show",
                                font=("Montserrat", 10),
                                bg=background_color,
                                fg="#236cfe",
                                border=0,
                                cursor="hand2",
                                activebackground=background_color,
                                activeforeground="white",
                                command=lambda: toggle_password_visibility(entry_password, password_toggle_button))
password_toggle_button.pack(side=LEFT, pady=(0, 0))

lbl_password_error = Label(main_frame, text="", font=("Montserrat", 10), bg=background_color, fg="red")
lbl_password_error.pack(anchor="w", padx=(0, 0), pady=(0, 10)) # Placeholder for error message

# Confirm Password Entry
lbl_confirm_password = Label(main_frame,
                              text="Confirma tu contraseña",
                              font=("Montserrat", 12),
                              bg=background_color,
                              fg="white")
lbl_confirm_password.pack(anchor="w", pady=(10, 5))

confirm_password_frame = Frame(main_frame, bg=background_color) # Frame to hold confirm password entry and toggle button
confirm_password_frame.pack(anchor="w", fill="x")

entry_confirm_password = CTkEntry(confirm_password_frame,
                                   width=270, # Adjusted width
                                   placeholder_text="Confirma tu contraseña",
                                   show='*',
                                   border_width=0,
                                   bg_color=background_color,
                                   font=("Montserrat", 12),
                                   text_color="white",
                                   fg_color=entry_color)
entry_confirm_password.pack(side=LEFT, pady=(0, 0), padx=(0, 5))

# Confirm Password visibility toggle button (text-based)
confirm_password_toggle_button = Button(confirm_password_frame,
                                        text="Show",
                                        font=("Montserrat", 10),
                                        bg=background_color,
                                        fg="#236cfe",
                                        border=0,
                                        cursor="hand2",
                                        activebackground=background_color,
                                        activeforeground="white",
                                        command=lambda: toggle_password_visibility(entry_confirm_password, confirm_password_toggle_button))
confirm_password_toggle_button.pack(side=LEFT, pady=(0, 0))

lbl_confirm_password_error = Label(main_frame, text="", font=("Montserrat", 10), bg=background_color, fg="red")
lbl_confirm_password_error.pack(anchor="w", padx=(0, 0), pady=(0, 20)) # Placeholder for error message

#Encript password 
def encrypt_password(password):
    salt = bcrypt.gensalt()
    encript = bcrypt.hashpw(password.encode('utf-8'), salt)
    return encript

# Function to save user data to the database
def save_user_to_db(name, email, password, username):
    try:
        db = ConexionDB()
        
        query = "INSERT INTO cliente (cli_nombre, cli_correo, cli_usuario, cli_password) VALUES (%s, %s, %s, %s)"
        params = (name, email, username, encrypt_password(password))

        cursor = db.ejecutar_query(query, params)
        if cursor:
            db.conexion.commit()
            #print("Usuario guardado en la base de datos.")
            return True
        else:
            #print("Error al ejecutar la consulta.")
            return False
            
    except Exception as e:
        #print(f"Error al guardar el usuario: {e}")
        return False
    finally:
        if db and db.conexion and db.conexion.is_connected():
            db.cerrar()

# Variables to store registration data temporarily
registration_name = ""
registration_email = ""
registration_password = ""

# Function to toggle password visibility
def toggle_password_visibility(entry, button):
    if entry.cget('show') == '*' :
        entry.configure(show='')
        button.configure(text='Hide')
    else:
        entry.configure(show='*')
        button.configure(text='Show')

# Function to validate input fields and transition
def validate_and_transition():
    global registration_name, registration_email, registration_password
    is_valid = True

    # Clear previous error messages
    lbl_name_error.configure(text="")
    lbl_email_error.configure(text="")
    lbl_password_error.configure(text="")
    lbl_confirm_password_error.configure(text="")

    # Validate fields
    if not entry_name.get():
        lbl_name_error.configure(text="Campo obligatorio")
        is_valid = False

    if not entry_email.get():
        lbl_email_error.configure(text="Campo obligatorio")
        is_valid = False

    if not entry_password.get():
        lbl_password_error.configure(text="Campo obligatorio")
        is_valid = False

    if not entry_confirm_password.get():
        lbl_confirm_password_error.configure(text="Campo obligatorio")
        is_valid = False

    # Check if passwords match
    if entry_password.get() != entry_confirm_password.get():
        lbl_confirm_password_error.configure(text="La contraseña no coincide")
        is_valid = False

    # If all fields are valid, store data and transition to username page
    if is_valid:
        registration_name = entry_name.get()
        registration_email = entry_email.get()
        registration_password = entry_password.get()
        transition_to_username_page()

# Next Button
btn_next = CTkButton(main_frame,
                     width=300,
                     height=45,
                     corner_radius=8,
                     text="Siguiente",
                     border_width=0,
                     bg_color=background_color,
                     font=("Montserrat Medium", 14),
                     fg_color=button_color,
                     hover_color="#3462aa",
                     cursor="hand2",
                     command=validate_and_transition) # Call the validation function
btn_next.pack(pady=(10, 0))

# Agregar texto y botón "¿Ya tiene una cuenta? Siguiente"
account_frame = Frame(main_frame, bg=background_color)
account_frame.pack(pady=(20, 0))

lbl_account = Label(account_frame,
                    text="¿Ya tiene una cuenta?",
                    font=("Montserrat", 10),
                    bg=background_color,
                    fg="white")
lbl_account.pack(side=LEFT)

btn_account = Button(account_frame,
                     text="Siguiente",
                     font=("Montserrat Medium", 10),
                     bg=background_color,
                     fg="#236cfe",
                     border=0,
                     cursor="hand2",
                     activebackground=background_color,
                     activeforeground="white",
                     command=lambda: [register_window.destroy(), 
                        subprocess.run(['python', os.path.join(os.path.dirname(os.path.realpath(__file__)), 'Login.py')])])
btn_account.pack(side=LEFT, padx=(5, 0))

# Function to transition to the previous page (initial registration form)
def transition_to_previous_page():
    # Clear the current frame
    for widget in main_frame.winfo_children():
        widget.destroy()

    # Recreate the initial registration form
    # Title
    lbl_title = Label(main_frame,
                      text="Crear cuenta",
                      font=("Montserrat Bold", 18),
                      bg=background_color,
                      fg="white")
    lbl_title.pack(pady=(0, 20))

    # Name Entry
    lbl_name = Label(main_frame,
                     text="Nombre",
                     font=("Montserrat", 12),
                     bg=background_color,
                     fg="white")
    lbl_name.pack(anchor="w", pady=(10, 5))

    entry_name = CTkEntry(main_frame,
                          width=300,
                          placeholder_text="Nombre y apellido",
                          border_width=0,
                          bg_color=background_color,
                          font=("Montserrat", 12),
                          text_color="white",
                          fg_color=entry_color)
    entry_name.pack(pady=(0, 0))

    lbl_name_error = Label(main_frame, text="", font=("Montserrat", 10), bg=background_color, fg="red")
    lbl_name_error.pack(anchor="w", padx=(0, 0), pady=(0, 10))

    # Email Entry
    lbl_email = Label(main_frame,
                      text="Correo electrónico",
                      font=("Montserrat", 12),
                      bg=background_color,
                      fg="white")
    lbl_email.pack(anchor="w", pady=(10, 5))

    entry_email = CTkEntry(main_frame,
                           width=300,
                           placeholder_text="Correo electrónico",
                           border_width=0,
                           bg_color=background_color,
                           font=("Montserrat", 12),
                           text_color="white",
                           fg_color=entry_color)
    entry_email.pack(pady=(0, 0))

    lbl_email_error = Label(main_frame, text="", font=("Montserrat", 10), bg=background_color, fg="red")
    lbl_email_error.pack(anchor="w", padx=(0, 0), pady=(0, 10))

    # Password Entry
    lbl_password = Label(main_frame,
                         text="Contraseña",
                         font=("Montserrat", 12),
                         bg=background_color,
                         fg="white")
    lbl_password.pack(anchor="w", pady=(10, 5))

    password_frame = Frame(main_frame, bg=background_color)
    password_frame.pack(anchor="w", fill="x")

    entry_password = CTkEntry(password_frame,
                              width=270,
                              placeholder_text="Al menos 6 caracteres",
                              show='*',
                              border_width=0,
                              bg_color=background_color,
                              font=("Montserrat", 12),
                              text_color="white",
                              fg_color=entry_color)
    entry_password.pack(side=LEFT, pady=(0, 0), padx=(0, 5))

    password_toggle_button = Button(password_frame,
                                    text="Show",
                                    font=("Montserrat", 10),
                                    bg=background_color,
                                    fg="#236cfe",
                                    border=0,
                                    cursor="hand2",
                                    activebackground=background_color,
                                    activeforeground="white",
                                    command=lambda: toggle_password_visibility(entry_password, password_toggle_button))
    password_toggle_button.pack(side=LEFT, pady=(0, 0))

    lbl_password_error = Label(main_frame, text="", font=("Montserrat", 10), bg=background_color, fg="red")
    lbl_password_error.pack(anchor="w", padx=(0, 0), pady=(0, 10))

    # Confirm Password Entry
    lbl_confirm_password = Label(main_frame,
                                 text="Confirma tu contraseña",
                                 font=("Montserrat", 12),
                                 bg=background_color,
                                 fg="white")
    lbl_confirm_password.pack(anchor="w", pady=(10, 5))

    confirm_password_frame = Frame(main_frame, bg=background_color)
    confirm_password_frame.pack(anchor="w", fill="x")

    entry_confirm_password = CTkEntry(confirm_password_frame,
                                      width=270,
                                      placeholder_text="Confirma tu contraseña",
                                      show='*',
                                      border_width=0,
                                      bg_color=background_color,
                                      font=("Montserrat", 12),
                                      text_color="white",
                                      fg_color=entry_color)
    entry_confirm_password.pack(side=LEFT, pady=(0, 0), padx=(0, 5))

    confirm_password_toggle_button = Button(confirm_password_frame,
                                            text="Show",
                                            font=("Montserrat", 10),
                                            bg=background_color,
                                            fg="#236cfe",
                                            border=0,
                                            cursor="hand2",
                                            activebackground=background_color,
                                            activeforeground="white",
                                            command=lambda: toggle_password_visibility(entry_confirm_password, confirm_password_toggle_button))
    confirm_password_toggle_button.pack(side=LEFT, pady=(0, 0))

    lbl_confirm_password_error = Label(main_frame, text="", font=("Montserrat", 10), bg=background_color, fg="red")
    lbl_confirm_password_error.pack(anchor="w", padx=(0, 0), pady=(0, 20))

    # Next Button
    btn_next = CTkButton(main_frame,
                         width=300,
                         height=45,
                         corner_radius=8,
                         text="Siguiente",
                         border_width=0,
                         bg_color=background_color,
                         font=("Montserrat Medium", 14),
                         fg_color=button_color,
                         hover_color="#3462aa",
                         cursor="hand2",
                         command=validate_and_transition) # Call the validation function
    btn_next.pack(pady=(10, 0))


    lbl_account = Label(account_frame,
                        text="¿Ya tiene una cuenta?",
                        font=("Montserrat", 10),
                        bg=background_color,
                        fg="white",
                        cursor="hand2",
                         activebackground=background_color,
                         activeforeground="white",
                         command=lambda: [register_window.destroy(), subprocess.run(['python', os.path.join(os.path.dirname(os.path.realpath(__file__)), 'Login.py')])])
    lbl_account.pack(side=LEFT)

    btn_account = Button(account_frame,
                         text="Siguiente",
                         font=("Montserrat Medium", 10),
                         bg=background_color,
                         fg="#236cfe",
                         border=0,
                         cursor="hand2",
                         activebackground=background_color,
                         activeforeground="white",
                         command=lambda: [register_window.destroy(), subprocess.run(['python', os.path.join(os.path.dirname(os.path.realpath(__file__)), 'Login.py')])])
    btn_account.pack(side=LEFT, padx=(5, 0))


    # Agregar texto y botón "¿Ya tiene una cuenta? Siguiente"
    account_frame = Frame(main_frame, bg=background_color)
    account_frame.pack(pady=(20, 0))
    
# Function to transition to the username creation page
def transition_to_username_page():
    # Clear the current frame
    for widget in main_frame.winfo_children():
        widget.destroy()

    # Add a back button with an image to return to the previous page
    back_image_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../img/fechader.png')
    back_photo = None # Initialize back_photo to None
    if os.path.exists(back_image_path):
        try:
            back_image = Image.open(back_image_path)
            back_image = back_image.resize((20, 20), Image.Resampling.LANCZOS) # Use LANCZOS for resizing
            back_photo = ImageTk.PhotoImage(back_image)

            btn_back = Button(main_frame,
                              image=back_photo,
                              bg=background_color,
                              border=0,
                              cursor="hand2",
                              activebackground=background_color,
                              command=transition_to_previous_page)
            btn_back.image = back_photo  # Keep a reference to avoid garbage collection
            btn_back.pack(anchor="nw", padx=(10, 0), pady=(10, 0)) # Use pack and anchor
        except Exception as e:
            e
            #print(f"Error loading back button image: {e}")

    # Title for username creation
    lbl_username_title = Label(main_frame,
                                text="Crea tu nombre de usuario",
                                font=("Montserrat Bold", 18),
                                bg=background_color,
                                fg="white")
    lbl_username_title.pack(pady=(10, 20))

    # Username Entry
    lbl_username = Label(main_frame,
                         text="Nombre de usuario",
                         font=("Montserrat", 12),
                         bg=background_color,
                         fg="white")
    lbl_username.pack(anchor="w", pady=(10, 5))

    entry_username = CTkEntry(main_frame,
                               width=300,
                               placeholder_text="Elige un nombre de usuario",
                               border_width=0,
                               bg_color=background_color,
                               font=("Montserrat", 12),
                               text_color="white",
                               fg_color=entry_color)
    entry_username.pack(pady=(0, 20))

    # Save Button
    btn_save = CTkButton(main_frame,
                         width=300,
                         height=45,
                         corner_radius=8,
                         text="Guardar",
                         border_width=0,
                         bg_color=button_color,
                         font=("Montserrat Medium", 14),
                         fg_color=button_color,
                         hover_color="#3462aa",
                         cursor="hand2",
                         command=lambda: [
                             save_user_to_db(
                                 registration_name,
                                 registration_email,
                                 registration_password,
                                 entry_username.get()
                             ),
                             #print("Usuario Creado"),
                             register_window.destroy(),
                             subprocess.run(['python', os.path.join(os.path.dirname(os.path.realpath(__file__)), 'Login.py')])
                         ])
    btn_save.pack(pady=(10, 0))

# Center window
register_window.update_idletasks()
width = 400
height = 600
screen_width = register_window.winfo_screenwidth()
screen_height = register_window.winfo_screenheight()

x = (screen_width - width) // 2
y = (screen_height - height) // 2

register_window.geometry(f'{width}x{height}+{x}+{y-30}')

register_window.mainloop()