class SegmentoVial:
    def __init__(self, longitud_total=600.0, inicio_cuello=300.0, fin_cuello=450.0):
        self.longitud_total = longitud_total   # Metros totales del tramo
        self.inicio_cuello = inicio_cuello     # Inicio de la reducción geométrica (m)
        self.fin_cuello = fin_cuello           # Fin de la zona de estrangulamiento (m)
        self.carriles_iniciales = 4            # Tránsito libre con 4 carriles
        self.carriles_cuello = 2               # Reducción a 2 carriles en el cuello de botella