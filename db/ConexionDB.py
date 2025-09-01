import mysql.connector
from mysql.connector import Error

try:
    from .config import DB_CPUBLIC as DB_CONFIG
except ImportError:
    from config import DB_CPUBLIC as DB_CONFIG


class ConexionDB:
    def __init__(self):
        self.config = DB_CONFIG
        self.conexion = None
        self.cursor = None
        self.conectar()

    def conectar(self):
        try:
            self.conexion = mysql.connector.connect(**self.config)
            self.cursor = self.conexion.cursor()
            print("Conexión exitosa a la base de datos")
        except Error as err:
            err
            #print(f"Error al conectar: {err}")

    def reconectar(self):
        try:
            self.conexion.ping(reconnect=True, attempts=3, delay=1)
            if not self.cursor or self.cursor.is_closed():
                self.cursor = self.conexion.cursor()
            return True
        except Error as err:
            #print(f"Error al reconectar: {err}")
            self.conectar()  # Intenta una nueva conexión
            return self.conexion and self.conexion.is_connected()

    def ejecutar_query(self, query, params=None):
        """
        Ejecuta una consulta asegurándose de que la conexión esté activa
        """
        try:
            if not self.conexion or not self.conexion.is_connected():
                self.reconectar()
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            
            return self.cursor
        except Error as err:
            #print(f"Error en la consulta: {err}")
            if "MySQL Connection not available" in str(err):
                if self.reconectar():
                    return self.ejecutar_query(query, params)
            return None

    def cerrar(self):
        if self.conexion and self.conexion.is_connected():
            self.cursor.close()
            self.conexion.close()
            #print("Conexión cerrada")

# Crear una instancia global de la conexión
db = ConexionDB()

