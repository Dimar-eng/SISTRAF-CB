import tkinter as tk
from tkinter import ttk
import random
import math
from vehicle import Vehiculo
from road import SegmentoVial
from telemetry import Telemetria

class SISTRAFCBEngine:
    def __init__(self, root):
        self.root = root
        self.root.title("SISTRAF-CB | Modelación Sistémica de Tráfico")
        self.root.geometry("1350x850")
        self.root.configure(bg="#0f111a")

        # Configuración del segmento vial y telemetría
        self.segmento = SegmentoVial(longitud_total=600.0, inicio_cuello=300.0, fin_cuello=450.0)
        self.telemetria = Telemetria()
        
        # Configuración dinámica de carriles
        self.num_carriles_inicio = 4  # Carriles de entrada
        self.num_carriles_cuello = 2  # Carriles en cuello de botella

        self.vehiculos = []
        self.id_contador = 0
        self.tiempo_simulacion = 0.0
        self.dt = 0.1
        self.tasa_inyeccion = 0.28  
        self.pausado = False

        # Evento de cierre de la ventana para mostrar reporte
        self.root.protocol("WM_DELETE_WINDOW", self.cerrar_aplicacion)

        # Interfaz Gráfica
        self.crear_encabezado()
        self.crear_panel_metrica()
        self.crear_canvas_vial()
        self.crear_panel_controles()

        # Bucle de animación
        self.actualizar_simulacion()

    def crear_encabezado(self):
        frame_header = tk.Frame(self.root, bg="#161822")
        frame_header.pack(fill=tk.X, pady=12, padx=20)

        titulo = tk.Label(
            frame_header, 
            text="SISTRAF-CB", 
            font=("Segoe UI", 18, "bold"), fg="#ffffff", bg="#161822"
        )
        titulo.pack(side=tk.LEFT)

        subtitulo = tk.Label(
            frame_header, 
            text="Teoría General de Sistemas & Dinámica de Ondas de Choque", 
            font=("Segoe UI", 10, "italic"), fg="#8b8fa3", bg="#161822"
        )
        subtitulo.pack(side=tk.RIGHT)

    def crear_panel_metrica(self):
        self.frame_metrics = tk.Frame(self.root, bg="#0f111a")
        self.frame_metrics.pack(fill=tk.X, padx=20, pady=5)

        self.lbl_flujo = self.crear_tarjeta(self.frame_metrics, "FLUJO DE ENTRADA (q_in)", "0 veh/h", "#3b82f6")
        self.lbl_densidad = self.crear_tarjeta(self.frame_metrics, "DENSIDAD VIAL (K)", "0 veh/km", "#eab308")
        self.lbl_velocidad = self.crear_tarjeta(self.frame_metrics, "VELOCIDAD MEDIA (V)", "0 km/h", "#22c55e")
        self.lbl_cola = self.crear_tarjeta(self.frame_metrics, "LONGITUD DE COLA (L_cola)", "0 vehs", "#ef4444")
        self.lbl_entropia = self.crear_tarjeta(self.frame_metrics, "ESTADO SISTÉMICO", "FLUIDO", "#22c55e")

    def crear_tarjeta(self, parent, titulo, valor_inicial, color_acento):
        card = tk.Frame(parent, bg="#1a1d2d", highlightbackground=color_acento, highlightthickness=1)
        card.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=6, pady=5)
        
        lbl_title = tk.Label(card, text=titulo, font=("Segoe UI", 8, "bold"), fg="#8b8fa3", bg="#1a1d2d")
        lbl_title.pack(anchor=tk.W, padx=12, pady=(8, 2))
        
        lbl_val = tk.Label(card, text=valor_inicial, font=("Segoe UI", 13, "bold"), fg="#ffffff", bg="#1a1d2d")
        lbl_val.pack(anchor=tk.W, padx=12, pady=(0, 8))
        return lbl_val

    def crear_canvas_vial(self):
        frame_canvas = tk.Frame(self.root, bg="#0f111a")
        frame_canvas.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        self.canvas = tk.Canvas(frame_canvas, bg="#090a0f", highlightthickness=1, highlightbackground="#2a2e43")
        self.canvas.pack(fill=tk.BOTH, expand=True)

    def crear_panel_controles(self):
        frame_controls = tk.Frame(self.root, bg="#161822")
        frame_controls.pack(fill=tk.X, padx=0, pady=0)

        inner_controls = tk.Frame(frame_controls, bg="#161822")
        inner_controls.pack(fill=tk.X, padx=20, pady=12)

        # Botones de control básico
        btn_perturbar = tk.Button(
            inner_controls, text="⚡ Inyectar Frenado Súbito", 
            command=self.inyectar_perturbar, font=("Segoe UI", 9, "bold"),
            bg="#ef4444", fg="#ffffff", activebackground="#dc2626", padx=10, pady=5, bd=0, cursor="hand2"
        )
        btn_perturbar.pack(side=tk.LEFT, padx=5)

        self.btn_pausa = tk.Button(
            inner_controls, text="⏸ Pausar", command=self.conmutar_pausa, 
            font=("Segoe UI", 9, "bold"), bg="#3b82f6", fg="#ffffff", padx=10, pady=5, bd=0, cursor="hand2"
        )
        self.btn_pausa.pack(side=tk.LEFT, padx=5)

        # Controles manuales para agregar/quitar carriles de entrada
        frame_carriles_in = tk.Frame(inner_controls, bg="#1a1d2d", padx=8, pady=3)
        frame_carriles_in.pack(side=tk.LEFT, padx=10)
        
        lbl_cin = tk.Label(frame_carriles_in, text="Carriles Entrada:", font=("Segoe UI", 8, "bold"), fg="#8b8fa3", bg="#1a1d2d")
        lbl_cin.pack(side=tk.LEFT, padx=3)
        
        btn_dec_in = tk.Button(frame_carriles_in, text="-", command=lambda: self.modificar_carriles('inicio', -1),
                               font=("Segoe UI", 9, "bold"), bg="#2a2e43", fg="#ffffff", bd=0, width=2)
        btn_dec_in.pack(side=tk.LEFT, padx=2)
        
        self.lbl_val_cin = tk.Label(frame_carriles_in, text=str(self.num_carriles_inicio), font=("Segoe UI", 9, "bold"), fg="#ffffff", bg="#1a1d2d")
        self.lbl_val_cin.pack(side=tk.LEFT, padx=4)
        
        btn_inc_in = tk.Button(frame_carriles_in, text="+", command=lambda: self.modificar_carriles('inicio', 1),
                               font=("Segoe UI", 9, "bold"), bg="#2a2e43", fg="#ffffff", bd=0, width=2)
        btn_inc_in.pack(side=tk.LEFT, padx=2)

        # Controles manuales para agregar/quitar carriles de cuello
        frame_carriles_cuello = tk.Frame(inner_controls, bg="#1a1d2d", padx=8, pady=3)
        frame_carriles_cuello.pack(side=tk.LEFT, padx=10)
        
        lbl_ccuello = tk.Label(frame_carriles_cuello, text="Carriles Cuello:", font=("Segoe UI", 8, "bold"), fg="#8b8fa3", bg="#1a1d2d")
        lbl_ccuello.pack(side=tk.LEFT, padx=3)
        
        btn_dec_c = tk.Button(frame_carriles_cuello, text="-", command=lambda: self.modificar_carriles('cuello', -1),
                              font=("Segoe UI", 9, "bold"), bg="#2a2e43", fg="#ffffff", bd=0, width=2)
        btn_dec_c.pack(side=tk.LEFT, padx=2)
        
        self.lbl_val_ccuello = tk.Label(frame_carriles_cuello, text=str(self.num_carriles_cuello), font=("Segoe UI", 9, "bold"), fg="#ffffff", bg="#1a1d2d")
        self.lbl_val_ccuello.pack(side=tk.LEFT, padx=4)
        
        btn_inc_c = tk.Button(frame_carriles_cuello, text="+", command=lambda: self.modificar_carriles('cuello', 1),
                              font=("Segoe UI", 9, "bold"), bg="#2a2e43", fg="#ffffff", bd=0, width=2)
        btn_inc_c.pack(side=tk.LEFT, padx=2)

        # Slider de demanda
        lbl_slider = tk.Label(inner_controls, text="Demanda:", font=("Segoe UI", 9, "bold"), fg="#ffffff", bg="#161822")
        lbl_slider.pack(side=tk.LEFT, padx=(10, 5))

        self.slider_demanda = ttk.Scale(inner_controls, from_=0.05, to=0.80, value=0.28, command=self.cambiar_demanda)
        self.slider_demanda.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

    def modificar_carriles(self, zona, delta):
        if zona == 'inicio':
            nuevo_val = self.num_carriles_inicio + delta
            if 2 <= nuevo_val <= 6 and nuevo_val >= self.num_carriles_cuello:
                self.num_carriles_inicio = nuevo_val
                self.lbl_val_cin.config(text=str(self.num_carriles_inicio))
        elif zona == 'cuello':
            nuevo_val = self.num_carriles_cuello + delta
            if 1 <= nuevo_val <= 4 and nuevo_val <= self.num_carriles_inicio:
                self.num_carriles_cuello = nuevo_val
                self.lbl_val_ccuello.config(text=str(self.num_carriles_cuello))

    def cambiar_demanda(self, val):
        self.tasa_inyeccion = float(val)

    def conmutar_pausa(self):
        self.pausado = not self.pausado
        self.btn_pausa.config(text="▶ Reanudar" if self.pausado else "⏸ Pausar")

    def inyectar_perturbar(self):
        if self.vehiculos:
            idx = len(self.vehiculos) // 2
            self.vehiculos[idx].v = 0.0

    def obtener_posicion_y(self, carril_index, total_carriles, h):
        """Calcula la coordenada Y para centrar dinámicamente cualquier número de carriles."""
        alto_carril = 35.0
        centro_y = h / 2.0
        inicio_y = centro_y - (total_carriles * alto_carril) / 2.0
        return inicio_y + carril_index * alto_carril + alto_carril / 2.0

    def actualizar_simulacion(self):
        if not self.pausado:
            # 1. Inyección de vehículos según número actual de carriles de entrada
            if random.random() < self.tasa_inyeccion:
                carril_nuevo = random.randint(0, self.num_carriles_inicio - 1)
                conflictos = [v for v in self.vehiculos if v.carril == carril_nuevo and v.x < 22.0]
                if not conflictos:
                    self.id_contador += 1
                    nuevo_v = Vehiculo(self.id_contador, x=0.0, carril=carril_nuevo, v_deseada=random.uniform(18.0, 22.0))
                    nuevo_v.carril_origen = carril_nuevo
                    nuevo_v.carril_actual_y = float(carril_nuevo)
                    self.vehiculos.append(nuevo_v)

            # 2. Física y convergencia dinámica
            self.vehiculos.sort(key=lambda v: v.x, reverse=True)
            for i, v in enumerate(self.vehiculos):
                carril_orig = getattr(v, 'carril_origen', v.carril)
                carril_orig = min(carril_orig, self.num_carriles_inicio - 1)
                
                # Mapeo proporcional hacia los carriles disponibles en el cuello
                if v.x >= self.segmento.inicio_cuello - 50.0:
                    ratio = carril_orig / max(1, self.num_carriles_inicio - 1)
                    v.carril = min(self.num_carriles_cuello - 1, int(round(ratio * (self.num_carriles_cuello - 1))))
                else:
                    v.carril = carril_orig

                if not hasattr(v, 'carril_actual_y'):
                    v.carril_actual_y = float(v.carril)
                
                v.carril_actual_y += (v.carril - v.carril_actual_y) * 0.12

                predecesor = None
                for j in range(i - 1, -1, -1):
                    otro = self.vehiculos[j]
                    if otro.carril == v.carril or abs(otro.carril_actual_y - v.carril_actual_y) < 0.5:
                        predecesor = otro
                        break

                v.actualizar(self.dt, predecesor)

            self.vehiculos = [v for v in self.vehiculos if v.x <= self.segmento.longitud_total]
            self.tiempo_simulacion += self.dt

            # 3. Registrar datos
            self.telemetria.registrar_paso(self.tiempo_simulacion, self.vehiculos, self.segmento)

            self.renderizar()
            self.actualizar_telemetria()

        self.root.after(35, self.actualizar_simulacion)

    def renderizar(self):
        self.canvas.delete("all")
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()

        if w < 10: w = 1200
        if h < 10: h = 500

        escala_x = w / self.segmento.longitud_total
        x_cuello = self.segmento.inicio_cuello * escala_x
        x_fin_cuello = self.segmento.fin_cuello * escala_x

        # Calcular coordenadas Y dinámicas para entrada y cuello
        y_in = [self.obtener_posicion_y(i, self.num_carriles_inicio, h) for i in range(self.num_carriles_inicio)]
        y_cuel = [self.obtener_posicion_y(i, self.num_carriles_cuello, h) for i in range(self.num_carriles_cuello)]

        alto_carril = 35.0

        # Carretera Entrada
        self.canvas.create_rectangle(0, y_in[0] - alto_carril/2, x_cuello, y_in[-1] + alto_carril/2, fill="#13151f", outline="")
        # Carretera Cuello
        self.canvas.create_rectangle(x_cuello, y_cuel[0] - alto_carril/2, w, y_cuel[-1] + alto_carril/2, fill="#13151f", outline="")

        # Líneas de carril entrada
        for y in y_in:
            self.canvas.create_line(0, y, x_cuello, y, fill="#2a2e43", dash=(6, 6), width=1)

        # Bordes
        self.canvas.create_line(0, y_in[0] - alto_carril/2, x_cuello, y_in[0] - alto_carril/2, fill="#ffffff", width=2)
        self.canvas.create_line(0, y_in[-1] + alto_carril/2, x_cuello, y_in[-1] + alto_carril/2, fill="#ffffff", width=2)

        # Embudo dinámico
        self.canvas.create_line(x_cuello - 50 * escala_x, y_in[0] - alto_carril/2, x_cuello, y_cuel[0] - alto_carril/2, fill="#ef4444", width=3)
        self.canvas.create_line(x_cuello - 50 * escala_x, y_in[-1] + alto_carril/2, x_cuello, y_cuel[-1] + alto_carril/2, fill="#ef4444", width=3)

        # Bordes en el cuello
        self.canvas.create_line(x_cuello, y_cuel[0] - alto_carril/2, w, y_cuel[0] - alto_carril/2, fill="#ffffff", width=2)
        self.canvas.create_line(x_cuello, y_cuel[-1] + alto_carril/2, w, y_cuel[-1] + alto_carril/2, fill="#ffffff", width=2)

        for y in y_cuel:
            self.canvas.create_line(x_cuello, y, w, y, fill="#2a2e43", dash=(6, 6), width=1)

        # Zona Sombreada del Cuello de Botella
        self.canvas.create_rectangle(x_cuello, y_cuel[0] - alto_carril/2, x_fin_cuello, y_cuel[-1] + alto_carril/2, fill="#ef4444", stipple="gray25", outline="")

        # Vehículos (Agentes)
        for v in self.vehiculos:
            px = v.x * escala_x
            
            if v.x >= self.segmento.inicio_cuello:
                idx_cuel = min(v.carril, self.num_carriles_cuello - 1)
                py = y_cuel[idx_cuel]
            else:
                c_y = getattr(v, 'carril_actual_y', float(v.carril))
                idx_inf = max(0, min(self.num_carriles_inicio - 1, int(math.floor(c_y))))
                idx_sup = max(0, min(self.num_carriles_inicio - 1, int(math.ceil(c_y))))
                frac = c_y - idx_inf
                py = y_in[idx_inf] + (y_in[idx_sup] - y_in[idx_inf]) * frac

            if v.v > 14.0:
                color = "#22c55e"  
            elif v.v > 4.0:
                color = "#eab308"  
            else:
                color = "#ef4444"  

            self.canvas.create_rectangle(px - 8, py - 6, px + 8, py + 6, fill=color, outline="#090a0f", width=1)
            self.canvas.create_line(px + 8, py - 4, px + 8, py + 4, fill="#ffffff", width=2)

    def actualizar_telemetria(self):
        n_vehs = len(self.vehiculos)
        densidad_k = (n_vehs / (self.segmento.longitud_total / 1000.0))
        vel_prom = (sum(v.v for v in self.vehiculos) / max(1, n_vehs)) * 3.6
        flujo_q = densidad_k * vel_prom

        cola = sum(1 for v in self.vehiculos if v.x < self.segmento.inicio_cuello and v.v < 1.4)

        self.lbl_flujo.config(text=f"{int(flujo_q)} veh/h")
        self.lbl_densidad.config(text=f"{densidad_k:.1f} veh/km")
        self.lbl_velocidad.config(text=f"{vel_prom:.1f} km/h")
        self.lbl_cola.config(text=f"{cola} vehs")

        if cola > 18:
            self.lbl_entropia.config(text="COLAPSO / ONDA DE CHOQUE", fg="#ef4444")
        elif cola > 7:
            self.lbl_entropia.config(text="TRANSICIÓN INESTABLE", fg="#eab308")
        else:
            self.lbl_entropia.config(text="FLUJO ESTABLE", fg="#22c55e")

    def cerrar_aplicacion(self):
        """Genera el reporte estadístico y cierra la simulación."""
        print("--- GENERANDO REPORTE ESTADÍSTICO FINAL ---")
        self.root.destroy()
        self.telemetria.graficar_reporte()

if __name__ == "__main__":
    root = tk.Tk()
    app = SISTRAFCBEngine(root)
    root.mainloop()