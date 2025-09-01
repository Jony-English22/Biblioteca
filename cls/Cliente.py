class Cliente:
    def __init__(self):
        self.id = None
        self.nombre = None
        self.apellido = None
        self.direccion = None
        self.telefono = None
        self.email = None
        
    @property
    def nombre_completo(self):
        return f"{self.nombre} {self.apellido}"
    