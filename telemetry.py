import matplotlib.pyplot as plt

class Telemetria:
    def __init__(self):
        self.tiempos = []
        self.flujos = []       # q (vehículos / hora)
        self.densidades = []   # K (vehículos / km)
        self.velocidades = []  # V (km/h)
        self.longitudes_cola = []

    def registrar_paso(self, t, vehiculos, segmento):
        """Captura métricas instantáneas del sistema en cada ciclo."""
        vehiculos_en_tramo = [v for v in vehiculos if 0 <= v.x <= segmento.longitud_total]
        n_vehiculos = len(vehiculos_en_tramo)
        
        # Densidad (K) en veh/km
        densidad_km = (n_vehiculos / (segmento.longitud_total / 1000.0))
        
        # Velocidad media (V) en km/h
        vel_media_m_s = sum(v.v for v in vehiculos_en_tramo) / max(1, n_vehiculos)
        vel_media_kmh = vel_media_m_s * 3.6
        
        # Flujo fundamental (q = K * V)
        flujo_q = densidad_km * vel_media_kmh
        
        # Vehículos detenidos antes del cuello de botella (Cola / Shockwave)
        en_cola = sum(1 for v in vehiculos if v.x < segmento.inicio_cuello and v.v < 1.4)

        self.tiempos.append(t)
        self.flujos.append(flujo_q)
        self.densidades.append(densidad_km)
        self.velocidades.append(vel_media_kmh)
        self.longitudes_cola.append(en_cola)

    def graficar_reporte(self):
        """Genera y muestra el reporte estadístico final con resumen explicativo."""
        if not self.tiempos:
            return
        
        # Cálculo de métricas consolidadas
        duracion_total = self.tiempos[-1]
        flujo_promedio = sum(self.flujos) / len(self.flujos)
        densidad_promedio = sum(self.densidades) / len(self.densidades)
        vel_promedio = sum(self.velocidades) / len(self.velocidades)
        max_cola = max(self.longitudes_cola)
        
        # Diagnóstico del estado del sistema
        if max_cola > 18:
            diagnostico = "COLAPSO CRÍTICO por cuello de botella (Onda de choque retrógrada masiva)."
        elif max_cola > 7:
            diagnostico = "FLUJO INESTABLE con formación periódica de turbulencias y frenados."
        else:
            diagnostico = "SISTEMA FLUIDO y optimizado con baja fricción en la reducción de carriles."

        resumen_texto = (
            f"RESUMEN EJECUTIVO Y DIAGNÓSTICO SISTÉMICO\n"
            f"───────────────────────────────────────────────────────────\n"
            f"• Tiempo Evaluado: {duracion_total:.1f} segundos\n"
            f"• Flujo Promedio de Salida (q): {int(flujo_promedio)} veh/h\n"
            f"• Densidad Media del Tramo (K): {densidad_promedio:.1f} veh/km\n"
            f"• Velocidad Promedio (V): {vel_promedio:.1f} km/h\n"
            f"• Máxima Cola Registrada (L_cola): {max_cola} vehículos detenidos\n\n"
            f"EVALUACIÓN SISTÉMICA:\n"
            f"{diagnostico}"
        )

        # Configuración visual en Matplotlib
        plt.style.use('dark_background')
        fig = plt.figure(figsize=(12, 8))
        fig.suptitle("SISTRAF-CB // Reporte Estadístico Final de Telemetría Vial", fontsize=14, fontweight='bold', color='#ffffff')

        # Subplot 1: Flujo vs Densidad
        ax1 = fig.add_subplot(3, 1, 1)
        ax1.plot(self.tiempos, self.flujos, label="Flujo q (veh/h)", color="#3b82f6", linewidth=2)
        ax1.plot(self.tiempos, self.densidades, label="Densidad K (veh/km)", color="#eab308", linewidth=2)
        ax1.set_ylabel("Magnitud", color="#8b8fa3")
        ax1.set_title("Evolución Dinámica del Flujo y la Densidad", color="#ffffff", fontsize=11)
        ax1.legend(loc="upper right", facecolor="#161822", edgecolor="none")
        ax1.grid(True, linestyle="--", alpha=0.3)

        # Subplot 2: Longitud de Cola
        ax2 = fig.add_subplot(3, 1, 2)
        ax2.plot(self.tiempos, self.longitudes_cola, label="Vehículos en Cola (L_cola)", color="#ef4444", linewidth=2)
        ax2.set_ylabel("Vehículos Detenidos", color="#8b8fa3")
        ax2.set_title("Propagación Retrógrada de Cola (Efecto Acordeón / Shockwaves)", color="#ffffff", fontsize=11)
        ax2.legend(loc="upper right", facecolor="#161822", edgecolor="none")
        ax2.grid(True, linestyle="--", alpha=0.3)

        # Subplot 3: Cuadro de Texto con Diagnóstico
        ax3 = fig.add_subplot(3, 1, 3)
        ax3.axis('off')
        
        props_caja = dict(boxstyle='round,pad=0.8', facecolor='#161822', edgecolor='#3b82f6', alpha=0.9, linewidth=1.5)
        ax3.text(0.02, 0.90, resumen_texto, transform=ax3.transAxes, fontsize=10,
                 color='#ffffff', verticalalignment='top', fontfamily='monospace', bbox=props_caja)

        plt.tight_layout()
        plt.show()