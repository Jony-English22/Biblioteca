from typing import List
from datetime import datetime
from .Cliente import Cliente
from .VentaDetalle import VentaDetalle

class Venta:
    def __init__(self):
        self.id = None
        self.cliente: Cliente = None
        self.fecha = datetime.now()
        self.total = 0.00
        self.metodo_pago = None
        self.estado_pago = None
        self.detalles: List[VentaDetalle] = []

    def agregar_detalle(self, detalle: VentaDetalle):
        self.detalles.append(detalle)
        self._calcular_total()

    def eliminar_detalle(self, detalle: VentaDetalle):
        if detalle in self.detalles:
            self.detalles.remove(detalle)
            self._calcular_total()

    def _calcular_total(self):
        self.total = sum(detalle.subtotal for detalle in self.detalles)

    @property
    def cantidad_items(self):
        return sum(detalle.cantidad for detalle in self.detalles if detalle.cantidad)
