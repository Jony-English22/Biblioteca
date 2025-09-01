class VentaDetalle:
    def __init__(self):
        self.id_venta = None
        self.libro = None
        self.cantidad = None
        self.precio_unitario = None

    @property
    def subtotal(self):
        if self.cantidad and self.precio_unitario:
            return self.cantidad * self.precio_unitario
        return 0.00