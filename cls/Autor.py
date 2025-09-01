class Autor:
    def __init__(self):
        self.id = None
        self.nombre = None
        self.apellido = None
        self.fecha_nacimiento = None
        self.nacionalidad = None

    @property
    def nombre_completo(self):
        return f"{self.nombre}{self.apellido}" 
    