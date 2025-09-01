from typing import List
from Genero import Genero

class Libro:
    def __init__(self):
        self.id = None
        self.titulo = None
        self.autor = None
        self.editorial = None
        self.año = None
        self.isbn = None
        self.paginas = None
        self.precio = None
        self.stock = None
        self.descripcion = None
        self.generos: List[Genero] = []

    def agregar_genero(self, genero: Genero):
        if genero not in self.generos:
            self.generos.append(genero)
        else:
            print(f"El género {genero.nombre} ya está en la lista.")

    def eliminar_genero(self, genero: Genero):
        if genero in self.generos:
            self.generos.remove(genero)
            print(f"Género {genero.nombre} eliminado.")
       


