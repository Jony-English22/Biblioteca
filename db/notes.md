# Consulta con parámetros
>>> El parametro(params) se usa cuando usamos condiciones en SQL usando el WHERE.

query = "SELECT * FROM libro WHERE lib_id = %s"
params = (1,)  # El ID del libro que buscamos
cursor = db.ejecutar_query(query, params)

# Consulta sin parámetros
query = "SELECT * FROM libro"
cursor = db.ejecutar_query(query)  # params es None por defecto

Crea un fichero nuevo creando el diseño UI/UX utilzando la libreria tkinter para una aplicación de escritorio de ventas de libros. En el diseño usa las tendecias actuales para que el usuario tenga una experiencia practica y agragable. En la carpeta img hay una imagen de carrito en formato png 

Quiero agregar en el método add_books una función que encuentro en el fichero ConexionDB (ejecutar_query) que permite pone una instrucción de sql y la ejecutar. El proposito es que los libros los extraiga de la base de datos, y los pongo en tipo diccionario cada uno, como esta comentara la idea mencionada.

Para eso necesito importar la función de el fichero antes mencionado.