import math

class Vehiculo:
    def __init__(self, id_vehiculo, x, carril, v_deseada=20.0):
        self.id = id_vehiculo
        self.x = x                      # Posición longitudinal (m)
        self.carril = carril            # Carril objetivo
        self.v = v_deseada * 0.8         # Velocidad inicial (m/s)
        self.a = 0.0                    # Aceleración actual (m/s²)
        
        # Parámetros del Intelligent Driver Model (IDM)
        self.v0 = v_deseada             # Velocidad deseada (m/s)
        self.T = 1.2                    # Tiempo de reacción (s)
        self.a_max = 1.4                # Aceleración máxima (m/s²)
        self.b_comf = 2.0               # Desaceleración confortable (m/s²)
        self.delta = 4.0                # Exponente de aceleración
        self.s0 = 2.5                   # Distancia mínima de seguridad (m)
        self.longitud = 4.5             # Longitud del chasis (m)

    def calcular_idm(self, predecesor):
        """Calcula la aceleración según el modelo Car-Following IDM."""
        if predecesor is not None:
            s = predecesor.x - self.x - predecesor.longitud
            delta_v = self.v - predecesor.v
            s_star = self.s0 + max(0.0, self.v * self.T + (self.v * delta_v) / (2 * math.sqrt(self.a_max * self.b_comf)))
            if s <= 0:
                s = 0.1
            a_idm = self.a_max * (1 - (self.v / self.v0)**self.delta - (s_star / s)**2)
        else:
            a_idm = self.a_max * (1 - (self.v / self.v0)**self.delta)

        return max(-self.b_comf * 3, min(self.a_max, a_idm))

    def actualizar(self, dt, predecesor):
        """Actualiza el estado cinemático del agente vehicular."""
        self.a = self.calcular_idm(predecesor)
        self.v += self.a * dt
        self.v = max(0.0, self.v)
        self.x += self.v * dt