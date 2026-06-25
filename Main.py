import tkinter as tk
import json
import os
import pygame



# ── MAPA ──────────────────────────────────────────────────────────────────────
FILAS     = 10
COLS      = 16
TAM_CELDA = 50
COL_BASE  = 0

COLORES_FILA = ["#5a8c35", "#4a7329"]


# ── CLASES ────────────────────────────────────────────────────────────────────

class Torres:
    def __init__(self, nombre, vida, atk, costo, alcance, vel_especial, color):
        self.nombre        = nombre
        self.vida          = vida
        self.vida_max      = vida
        self.atk           = atk
        self.costo         = costo
        self.alcance       = alcance
        self.vel_especial  = vel_especial
        self.color         = color
        self.contador_especial = 0

    def clonar(self):
        return Torres(self.nombre, self.vida, self.atk, self.costo,
                      self.alcance, self.vel_especial, self.color)

class Muro:
    def __init__(self):
        self.nombre = "Muro"
        self.vida   = 60
        self.vida_max = 60
        self.costo  = 30
        self.color  = "#7f8c8d"

    def clonar(self):
        return Muro()


# ── TIPOS DISPONIBLES ─────────────────────────────────────────

TIPOS_TORRE = [
    Torres("Básica", vida=60,  atk=10, costo=50,  alcance=6, vel_especial=5, color="#3498db"),
    Torres("Pesada", vida=200, atk=30, costo=120, alcance=4, vel_especial=4, color="#e74c3c"),
    Torres("Mágica", vida=50,  atk=8,  costo=90,  alcance=8, vel_especial=3, color="#9b59b6"),
]

MURO_TIPO = Muro()

# ── enemigo ──────────────────────────────────────────────────────────────────
class Enemigo:
    def __init__(self, nombre, vida, atk, costo, velocidad, habilidad, turnos_habilidad, color):
        self.nombre           = nombre
        self.vida             = vida
        self.vida_max         = vida
        self.atk              = atk
        self.costo            = costo
        self.velocidad        = velocidad
        self.habilidad        = habilidad
        self.turnos_habilidad = turnos_habilidad
        self.contador_hab     = 0
        self.escudo_activo    = False
        self.vel_boost        = 0
        self.color            = color

    def clonar(self):
        return Enemigo(self.nombre, self.vida, self.atk, self.costo,
                       self.velocidad, self.habilidad, self.turnos_habilidad, self.color)

    def activar_habilidad(self):
        if self.habilidad == "ataque_doble":
            return self.atk * 2
        elif self.habilidad == "escudo_temporal":
            self.escudo_activo = True
            return self.atk
        elif self.habilidad == "aumento_vel":
            self.vel_boost = 1
            return self.atk
        return self.atk

    def recibir_danio(self, danio):
        if self.escudo_activo:
            self.escudo_activo = False
            return
        self.vida -= danio

    def esta_vivo(self):
        return self.vida > 0

TIPOS_ENEMIGO = [
    Enemigo("Soldado", vida=60,  atk=10, costo=30, velocidad=1, habilidad="ataque_doble",    turnos_habilidad=3, color="#e67e22"),
    Enemigo("Tanque",  vida=180, atk=20, costo=80, velocidad=1, habilidad="escudo_temporal", turnos_habilidad=4, color="#c0392b"),
    Enemigo("Rapido",  vida=30,  atk=6,  costo=20, velocidad=2, habilidad="aumento_vel",     turnos_habilidad=3, color="#f1c40f"),
]

# ── DEFENSOR ──────────────────────────────────────────────────────────────────

class Defensor:
    DINERO_INICIAL = 400

    def __init__(self, jugador):
        self.jugador = jugador
        self.dinero  = jugador.get("dinero_batalla", self.DINERO_INICIAL)

    def colocar(self, mapa, tipo, fila, col):
        if mapa[fila][col] is not None:
            return False, "Celda ocupada"
        if self.dinero < tipo.costo:
            return False, "Dinero insuficiente"
        objeto = tipo.clonar()          # clon fresco del template
        self.dinero    -= tipo.costo
        mapa[fila][col] = objeto
        return True, objeto

    def borrar(self, mapa, fila, col):
        celda = mapa[fila][col]
        if celda is None or celda == "BASE":
            return False, "No hay nada que borrar"
        self.dinero    += celda.costo   // 2# reembolso de la mitad para balancear
        mapa[fila][col] = None
        return True, celda

class Atacante:
    DINERO_INICIAL = 400

    def __init__(self, jugador):
        self.jugador = jugador
        self.dinero  = jugador.get("dinero_batalla", self.DINERO_INICIAL)

    def colocar(self, mapa, tipo, fila, col):
        if mapa[fila][col] is not None:
            return False, "Celda ocupada"
        if self.dinero < tipo.costo:
            return False, "Dinero insuficiente"
        objeto = tipo.clonar()
        self.dinero    -= tipo.costo
        mapa[fila][col] = objeto
        return True, objeto

    def borrar(self, mapa, fila, col):
        celda = mapa[fila][col]
        if celda is None:
            return False, "No hay nada que borrar"
        self.dinero    += celda.costo
        mapa[fila][col] = None
        return True, celda

# ── ARCHIVO DE JUGADORES ──────────────────────────────────────────────────────
ARCHIVO_JUGADORES = "jugadores.json"

def cargar_jugadores():
    if not os.path.exists(ARCHIVO_JUGADORES):
        return {}
    with open(ARCHIVO_JUGADORES, "r") as f:
        return json.load(f)

def guardar_jugadores(jugadores):
    with open(ARCHIVO_JUGADORES, "w") as f:
        json.dump(jugadores, f, indent=4)

def registrar_jugador(username, password):
    jugadores = cargar_jugadores()
    if username in jugadores:
        return False, "El usuario ya existe."
    jugadores[username] = {
        "contrasena": password,
        "victorias_defensor": 0,
        "victorias_atacante": 0
    }
    guardar_jugadores(jugadores)
    return True, "Registro exitoso."

def iniciar_sesion(username, password):
    jugadores = cargar_jugadores()
    if username not in jugadores:
        return False, "El usuario no existe."
    if jugadores[username]["contrasena"] != password:
        return False, "Contraseña incorrecta."
    return True, jugadores[username]

def registrar_victoria(username, rol):
    jugadores = cargar_jugadores()
    
    if username in jugadores:
        if rol == "defensor":
            jugadores[username]["victorias_defensor"] += 1
        elif rol == "atacante":
            jugadores[username]["victorias_atacante"] += 1
            
        guardar_jugadores(jugadores)

# ───────────────────────── Logica de rondas ─────────────────────────
def procesar_fin_ronda(ventana_bat, ganador, mapa_final):
    ventana_bat.destroy()
    
    if ganador == "atacante":
        estado_partida["victorias_atacante"] += 1
    else:
        estado_partida["victorias_defensor"] += 1
        
    if estado_partida["victorias_atacante"] >= 3:
        registrar_victoria(jugadores_activos[1]["username"], "atacante")
        abrir_estadisticas("atacante", jugadores_activos[1]["username"])
    elif estado_partida["victorias_defensor"] >= 3:
        registrar_victoria(jugadores_activos[0]["username"], "defensor")
        abrir_estadisticas("defensor", jugadores_activos[0]["username"])
    else:
        estado_partida["ronda_actual"] += 1
        # Se añade el bono de 200 al dinero actual
        jugadores_activos[0]["dinero_batalla"] = jugadores_activos[0].get("dinero_batalla", 0) + 200
        jugadores_activos[1]["dinero_batalla"] = jugadores_activos[1].get("dinero_batalla", 0) + 200
        abrir_juego(mapa_final) # Pasamos el mapa

def abrir_estadisticas(ganador_rol, nombre_ganador):
    ventana_est = tk.Tk()
    ventana_est.title("Estadísticas Finales")
    ventana_est.geometry("500x400")
    ventana_est.config(bg="#1a1a2e")

    tk.Label(ventana_est, text="¡FIN DE LA PARTIDA!", font=("Arial", 20, "bold"), bg="#1a1a2e", fg="#f1c40f").pack(pady=20)
    
    color_ganador = "#2ecc71" if ganador_rol == "defensor" else "#e74c3c"
    tk.Label(ventana_est, text=f"Ganador: {nombre_ganador} ({ganador_rol.capitalize()})", 
             font=("Arial", 16, "bold"), bg="#1a1a2e", fg=color_ganador).pack(pady=10)

    # Mostrar rondas ganadas por cada uno
    frame_stats = tk.Frame(ventana_est, bg="#1a1a2e")
    frame_stats.pack(pady=20)
    
    tk.Label(frame_stats, text=f"Victorias Defensor ({jugadores_activos[0]['username']}): {estado_partida['victorias_defensor']}", 
             font=("Arial", 12), bg="#1a1a2e", fg="white").pack(pady=5)
    tk.Label(frame_stats, text=f"Victorias Atacante ({jugadores_activos[1]['username']}): {estado_partida['victorias_atacante']}", 
             font=("Arial", 12), bg="#1a1a2e", fg="white").pack(pady=5)

    def cerrar_y_volver():
        ventana_est.destroy()
        abrir_menu_principal()

    tk.Button(ventana_est, text="Continuar al Menú", width=20, height=2, 
              bg="#3498db", fg="white", font=("Arial", 10, "bold"), command=cerrar_y_volver).pack(pady=30)

    ventana_est.mainloop()

# ─ CONFIGURACIÓN DE AUDIO ─────────────────────────
pygame.mixer.init()

# Diccionario para cargar los sonidos de forma segura
sonidos = {}
archivos_audio = {
    "ataque_torre": "ataque_torre.wav",
    "dano_enemigo": "dano_enemigo.wav",
    "muerte_tropa": "muerte_tropa.wav"
}

for clave, ruta in archivos_audio.items():
    try:
        sonidos[clave] = pygame.mixer.Sound(ruta)
    except:
        sonidos[clave] = None  # Si el archivo no existe, lo ignora sin dar error

def reproducir_sonido(clave):
    if sonidos.get(clave) and not estado.get("musica_pausada", False):
        sonidos[clave].play()

# ── ESTADOS GLOBALES ──────────────────────────────────────────────────────────
estado = {
    "textura":        "predeterminado",
    "volumen":        50,
    "musica_pausada": False,
}
estado_partida = {
    "victorias_defensor": 0,
    "victorias_atacante": 0,
    "ronda_actual": 1
}

CICLO_TEXTURAS    = ["predeterminado", "animado", "realista"]
jugadores_activos = [None, None]

# ── FACCIONES Y TEXTURAS ──────────────────────────────────────────────────────
FACCIONES = {
    "Normal": {
        "Básica": "norm_t_basica.png", "Pesada": "norm_t_pesada.png", "Mágica": "norm_t_magica.png",
        "Soldado": "zombie_normal_p.png", "Tanque": "zombie_tanque_p.png", "Rapido": "zombie_rapido_p.png",
        "Muro": "norm_muro.png", "BASE": "norm_base.png"
    },
    "Animado": {
        "Básica": "anim_t_basica.png", "Pesada": "anim_t_pesada.png", "Mágica": "anim_t_magica.png",
        "Soldado": "zombie_normal_a.png", "Tanque": "zombie_tanque_a.png", "Rapido": "zombie_rapido_a.png",
        "Muro": "anim_muro.png", "BASE": "anim_base.png"
    },
    "Toxico": {
        "Básica": "tox_t_basica.png", "Pesada": "tox_t_pesada.png", "Mágica": "tox_t_magica.png",
        "Soldado": "zombie_normal_t.png", "Tanque": "zombie_tanque_t.png", "Rapido": "zombie_rapido_t.png",
        "Muro": "tox_muro.png", "BASE": "tox_base.png"
    }
}

cache_texturas = {}

def obtener_textura(nombre_archivo):
    if nombre_archivo not in cache_texturas:
        try:
            cache_texturas[nombre_archivo] = tk.PhotoImage(file=nombre_archivo)
        except:
            cache_texturas[nombre_archivo] = None
    return cache_texturas[nombre_archivo]

def procesar_eleccion_faccion(faccion_elegida, turno, ventana_actual):
    jugadores_activos[turno]["faccion"] = faccion_elegida
    ventana_actual.destroy()
    
    if turno == 0:
        abrir_seleccion_faccion(1) 
    else:
        abrir_juego()      

def abrir_seleccion_faccion(turno):
    ventana_faccion = tk.Tk()
    ventana_faccion.title(f"Seleccionar Facción - Jugador {turno + 1}")
    ventana_faccion.geometry("400x300")
    
    tk.Label(ventana_faccion, text=f"{jugadores_activos[turno]['username']}, elige tu facción:", font=("Arial", 12)).pack(pady=20)
    
    for nombre_faccion in FACCIONES.keys():
        estado_btn = tk.NORMAL
        if turno == 1 and jugadores_activos[0].get("faccion") == nombre_faccion:
            estado_btn = tk.DISABLED
            
        tk.Button(
            ventana_faccion, 
            text=nombre_faccion, 
            state=estado_btn, 
            width=20,
            command=lambda f=nombre_faccion, t=turno, v=ventana_faccion: procesar_eleccion_faccion(f, t, v)
        ).pack(pady=5)
        
    ventana_faccion.mainloop()

# ── VENTANA DE LOGIN ──────────────────────────────────────────────────────────
def abrir_login(turno):
    ventana_login = tk.Tk()
    ventana_login.title(f"Login - Jugador {turno + 1}")
    ventana_login.geometry("800x500")
    ventana_login.resizable(False, False)
    
    if turno == 0:
        tk.Label(ventana_login, text="Defensor", font=("Arial", 18, "bold")).pack(pady=40)
    else:
        tk.Label(ventana_login, text="Atacante", font=("Arial", 18, "bold")).pack(pady=40)

    tk.Label(ventana_login, text="Usuario").pack()
    entry_usuario = tk.Entry(ventana_login, width=30)
    entry_usuario.pack(pady=5)

    tk.Label(ventana_login, text="Contraseña").pack()
    entry_password = tk.Entry(ventana_login, width=30, show="*")
    entry_password.pack(pady=5)

    lbl_mensaje = tk.Label(ventana_login, text="", font=("Arial", 9))
    lbl_mensaje.pack(pady=5)

    def intentar_login():
        username = entry_usuario.get().strip()
        password = entry_password.get().strip()
        if not username or not password:
            lbl_mensaje.config(text="Completa todos los campos.", fg="red")
            return
        if turno == 1 and username == jugadores_activos[0]["username"]:
            lbl_mensaje.config(text="El jugador 2 debe usar una cuenta diferente.", fg="red")
            return
        exito, resultado = iniciar_sesion(username, password)
        if exito:
            jugadores_activos[turno] = {"username": username, **resultado}
            ventana_login.destroy()
            if turno == 0:
                abrir_login(1)
            else:
                abrir_menu_principal()
        else:
            lbl_mensaje.config(text=resultado, fg="red")

    def intentar_registro():
        username = entry_usuario.get().strip()
        password = entry_password.get().strip()
        if not username or not password:
            lbl_mensaje.config(text="Completa todos los campos.", fg="red")
            return
        exito, mensaje = registrar_jugador(username, password)
        lbl_mensaje.config(text=mensaje, fg="green" if exito else "red")

    frame_botones = tk.Frame(ventana_login)
    frame_botones.pack(pady=15)
    tk.Button(frame_botones, text="Iniciar Sesión", width=18, height=2, command=intentar_login).grid(row=0, column=0, padx=20)
    tk.Button(frame_botones, text="Registrarse",    width=18, height=2, command=intentar_registro).grid(row=0, column=1, padx=20)

    ventana_login.mainloop()

def iniciar_partida_desde_menu(ventana):
    ventana.destroy()
    estado_partida["victorias_defensor"] = 0
    estado_partida["victorias_atacante"] = 0
    estado_partida["ronda_actual"] = 1
    
    # Limpiar dinero de partidas anteriores
    if jugadores_activos[0]: jugadores_activos[0].pop("dinero_batalla", None)
    if jugadores_activos[1]: jugadores_activos[1].pop("dinero_batalla", None)
    
    abrir_seleccion_faccion(0)

# ── VENTANA PRINCIPAL ─────────────────────────────────────────────────────────
def abrir_menu_principal():
    ventana_principal = tk.Tk()
    ventana_principal.title("Menú Principal")
    ventana_principal.geometry("800x500")
    ventana_principal.resizable(False, False)

    try:
        imagen_fondo = tk.PhotoImage(file="Fondo_principal.png")
        ventana_principal.imagen_fondo = imagen_fondo
        tk.Label(ventana_principal, image=imagen_fondo).place(x=0, y=0, relwidth=1, relheight=1)
    except:
        ventana_principal.configure(bg="#2B2B2B")

    def ir_a_jugar():
        ventana_principal.destroy()
        abrir_juego()

    def ir_a_configuracion():
        ventana_principal.destroy()
        abrir_configuracion()

    tk.Button(ventana_principal, text="JUGAR", width=16, height=2, 
          command=lambda v=ventana_principal: iniciar_partida_desde_menu(v),
          font=("Arial Black", 14), bg="#2B2B2B", fg="#A3E4D7", bd=5, relief="raised").place(relx=0.35, rely=0.6, anchor="center")
    
    tk.Button(ventana_principal, text="CONFIGURACIÓN", width=16, height=2, command=ir_a_configuracion,
              font=("Arial Black", 14), bg="#2B2B2B", fg="#A3E4D7", bd=5, relief="raised",
              activebackground="#404040", activeforeground="#A3E4D7").place(relx=0.65, rely=0.6, anchor="center")

    ventana_principal.mainloop()


# ── VENTANA DE JUEGO ──────────────────────────────────────────────────────────
def abrir_juego(mapa_existente=None):
    cache_texturas.clear()
    if mapa_existente is None:
        mapa = [[None for _ in range(COLS)] for _ in range(FILAS)]
        for f in range(FILAS):
            mapa[f][COL_BASE] = "BASE"
    else:
        mapa = mapa_existente

    defensor  = Defensor(jugadores_activos[0])
    seleccion = {"tipo": TIPOS_TORRE[0]}

    ancho_canvas = COLS * TAM_CELDA
    alto_canvas  = FILAS * TAM_CELDA

    ventana_juego = tk.Tk()
    ventana_juego.title(f"Construcción - {jugadores_activos[0]['username']} (Defensor)")
    ventana_juego.resizable(False, False)

    canvas = tk.Canvas(ventana_juego, width=ancho_canvas, height=alto_canvas)
    canvas.pack()

    panel = tk.Frame(ventana_juego, pady=10, bg="#1a1a2e")
    panel.pack(fill="x")

    lbl_dinero = tk.Label(panel, text=f"💰 {defensor.dinero}", font=("Arial", 13, "bold"),
                          bg="#1a1a2e", fg="#f1c40f")
    lbl_dinero.grid(row=0, column=0, columnspan=5, pady=(0, 6))

    def seleccionar(tipo):
        seleccion["tipo"] = tipo
        lbl_seleccion.config(text=f"Seleccionado: {tipo.nombre}  (${tipo.costo})")

    # botones generados desde las listas, sin hardcodear nada
    todos_los_tipos = TIPOS_TORRE + [MURO_TIPO]
    for i, tipo in enumerate(todos_los_tipos):
        tk.Button(panel, text=f"{tipo.nombre}  ${tipo.costo}", width=16, height=2,
                  bg=tipo.color, fg="white", font=("Arial", 9, "bold"), relief="flat",
                  command=lambda t=tipo: seleccionar(t)).grid(row=1, column=i, padx=8)

    lbl_seleccion = tk.Label(panel,
                             text=f"Seleccionado: {TIPOS_TORRE[0].nombre}  (${TIPOS_TORRE[0].costo})",
                             font=("Arial", 9), bg="#1a1a2e", fg="white")
    lbl_seleccion.grid(row=2, column=0, columnspan=5, pady=4)

    def ir_a_fase_ataque():
        jugadores_activos[0]["dinero_batalla"] = defensor.dinero
        ventana_juego.destroy()
        abrir_fase_ataque(mapa)

    btn_jugar = tk.Button(panel, text="Jugar  0/2", width=14, height=2,
                          font=("Arial Black", 10), bg="#2ecc71", fg="white",
                          relief="raised", bd=4, command=ir_a_fase_ataque)
    btn_jugar.grid(row=1, column=4, padx=8)

    lbl_mensaje = tk.Label(panel,
                           text="Clic izquierdo: colocar  |  Clic derecho: borrar (reembolso completo)",
                           font=("Arial", 8), bg="#1a1a2e", fg="#aaaaaa")
    lbl_mensaje.grid(row=3, column=0, columnspan=5)

    # overlay de pausa
    frame_pausa = tk.Frame(ventana_juego, bg="#2c3e50")
    tk.Label(frame_pausa, text="PAUSA", font=("Arial", 18, "bold"), bg="#2c3e50", fg="white").pack(pady=(80, 20))

    def reanudar():
        frame_pausa.place_forget()
        ventana_juego.focus_set()

    def volver_menu():
        ventana_juego.destroy()
        abrir_menu_principal()

    tk.Button(frame_pausa, text="Reanudar",       width=20, height=2, command=reanudar).pack(pady=10)
    tk.Button(frame_pausa, text="Volver al Menú", width=20, height=2, command=volver_menu).pack(pady=10)

    def toggle_pausa(event=None):
        if frame_pausa.winfo_ismapped():
            reanudar()
        else:
            frame_pausa.place(x=0, y=0, relwidth=1, relheight=1)

    ventana_juego.bind("<Escape>", toggle_pausa)
    ventana_juego.focus_set()

    def dibujar_mapa():
        canvas.delete("all")
        for f in range(FILAS):
            for c in range(COLS):
                x0, y0 = c * TAM_CELDA, f * TAM_CELDA
                x1, y1 = x0 + TAM_CELDA, y0 + TAM_CELDA
                celda  = mapa[f][c]

                if celda == "BASE":
                    color_fondo = "#c4853a"
                elif celda is None:
                    color_fondo = COLORES_FILA[f % 2]
                else:
                    color_fondo = celda.color

                canvas.create_rectangle(x0, y0, x1, y1, fill=color_fondo, outline="")

                if celda is not None and celda != "BASE":
                    canvas.create_text(x0 + TAM_CELDA // 2, y0 + TAM_CELDA // 2,
                                       text=celda.nombre[:3], fill="white",
                                       font=("Arial", 9, "bold"))

    def click_colocar(event):
        col  = event.x // TAM_CELDA
        fila = event.y // TAM_CELDA
        if fila >= FILAS or col >= COLS:
            return
        exito, resultado = defensor.colocar(mapa, seleccion["tipo"], fila, col)
        if exito:
            lbl_mensaje.config(text=f"Colocado: {resultado.nombre}  |  Dinero restante: ${defensor.dinero}", fg="#2ecc71")
            lbl_dinero.config(text=f"💰 {defensor.dinero}")
        else:
            lbl_mensaje.config(text=resultado, fg="#e74c3c")
        dibujar_mapa()

    def click_borrar(event):
        col  = event.x // TAM_CELDA
        fila = event.y // TAM_CELDA
        if fila >= FILAS or col >= COLS:
            return
        exito, resultado = defensor.borrar(mapa, fila, col)
        if exito:
            lbl_mensaje.config(text=f"Eliminado: {resultado.nombre}  |  +${resultado.costo} reembolsado  |  Dinero: ${defensor.dinero}", fg="#f39c12")
            lbl_dinero.config(text=f"💰 {defensor.dinero}")
        else:
            lbl_mensaje.config(text=resultado, fg="#aaaaaa")
        dibujar_mapa()

    canvas.bind("<Button-1>", click_colocar)
    canvas.bind("<Button-3>", click_borrar)
    dibujar_mapa()
    ventana_juego.mainloop()


# ── VENTANA DE CONFIGURACION ──────────────────────────────────────────────────
def abrir_configuracion():
    ventana_config = tk.Tk()
    ventana_config.title("Configuración")
    ventana_config.geometry("800x500")
    ventana_config.resizable(False, False)

    tk.Label(ventana_config, text="Configuración", font=("Arial", 16, "bold")).pack(pady=20)

    frame_fila1 = tk.Frame(ventana_config)
    frame_fila1.pack(pady=10)

    def volver_menu():
        ventana_config.destroy()
        abrir_menu_principal()

    def ir_a_ranking():
        ventana_config.destroy()
        abrir_ranking()

    tk.Button(frame_fila1, text="VOLVER AL MENÚ",     width=18, height=2, command=volver_menu,
              font=("Arial Black", 10), bg="#D1D5C4", fg="#2B2B2B", bd=4, relief="groove",
              activebackground="#C2C6B5").grid(row=0, column=0, padx=15)
    tk.Button(frame_fila1, text="REGISTRO DE PUNTOS", width=18, height=2, command=ir_a_ranking,
              font=("Arial Black", 10), bg="#D1D5C4", fg="#2B2B2B", bd=4, relief="groove",
              activebackground="#C2C6B5").grid(row=0, column=1, padx=15)
    tk.Button(frame_fila1, text="CERRAR JUEGO",        width=18, height=2, command=ventana_config.destroy,
              font=("Arial Black", 10), bg="#D1D5C4", fg="#2B2B2B", bd=4, relief="groove",
              activebackground="#C2C6B5").grid(row=0, column=2, padx=15)

    frame_fila2 = tk.Frame(ventana_config)
    frame_fila2.pack(pady=5)

    btn_musica = tk.Button(frame_fila2, text="Pausar Música", width=18, height=2,
                           font=("Arial Black", 10), bg="#D1D5C4", fg="#2B2B2B", bd=4, relief="groove")

    def toggle_musica():
        estado["musica_pausada"] = not estado["musica_pausada"]
        btn_musica.config(text="Reanudar Música" if estado["musica_pausada"] else "Pausar Música")

    btn_musica.config(command=toggle_musica)
    btn_musica.grid(row=0, column=0, padx=30)

    frame_volumen = tk.Frame(frame_fila2)
    frame_volumen.grid(row=0, column=1, padx=30)

    tk.Label(frame_volumen, text="Volumen").pack()
    lbl_vol_valor = tk.Label(frame_volumen, text=str(estado["volumen"]))
    lbl_vol_valor.pack()

    def cambiar_volumen(val):
        estado["volumen"] = int(float(val))
        lbl_vol_valor.config(text=str(estado["volumen"]))

    slider_volumen = tk.Scale(frame_volumen, from_=0, to=100, orient="horizontal",
                              length=200, command=cambiar_volumen, showvalue=False)
    slider_volumen.set(estado["volumen"])
    slider_volumen.pack()

    ventana_config.mainloop()


# ── VENTANA DE RANKING ────────────────────────────────────────────────────────
def abrir_ranking():
    ventana_ranking = tk.Tk()
    ventana_ranking.title("Top Jugadores")
    ventana_ranking.geometry("800x500")
    ventana_ranking.config(bg="#1a1a2e")

    tk.Label(ventana_ranking, text="🏆 Top 5 Jugadores 🏆", font=("Arial", 20, "bold"), bg="#1a1a2e", fg="#f1c40f").pack(pady=10)

    frame_listas = tk.Frame(ventana_ranking, bg="#1a1a2e")
    frame_listas.pack(pady=10)
    
    # Contenedores para las dos columnas
    frame_defensores = tk.Frame(frame_listas, bg="#1a1a2e")
    frame_defensores.grid(row=0, column=0, padx=30)
    tk.Label(frame_defensores, text="🛡️ Mejores Defensores", font=("Arial", 14, "bold"), bg="#1a1a2e", fg="#2ecc71").pack()
    
    frame_atacantes = tk.Frame(frame_listas, bg="#1a1a2e")
    frame_atacantes.grid(row=0, column=1, padx=30)
    tk.Label(frame_atacantes, text="⚔️ Mejores Atacantes", font=("Arial", 14, "bold"), bg="#1a1a2e", fg="#e74c3c").pack()

    jugadores = cargar_jugadores()
    
    # Ordenar y tomar solo los primeros 5
    top_defensores = sorted(jugadores.items(), key=lambda x: x[1].get("victorias_defensor", 0), reverse=True)[:5]
    top_atacantes = sorted(jugadores.items(), key=lambda x: x[1].get("victorias_atacante", 0), reverse=True)[:5]

    for i, (user, datos) in enumerate(top_defensores, 1):
        tk.Label(frame_defensores, text=f"{i}. {user} - {datos.get('victorias_defensor', 0)} wins", font=("Arial", 11), bg="#1a1a2e", fg="white").pack(pady=2)
        
    for i, (user, datos) in enumerate(top_atacantes, 1):
        tk.Label(frame_atacantes, text=f"{i}. {user} - {datos.get('victorias_atacante', 0)} wins", font=("Arial", 11), bg="#1a1a2e", fg="white").pack(pady=2)

    def volver_config():
        ventana_ranking.destroy()
        abrir_configuracion()

    tk.Button(ventana_ranking, text="Volver a Configuración", width=22, height=2, bg="#3498db", fg="white", font=("Arial", 10, "bold"), command=volver_config).pack(pady=30)
    ventana_ranking.mainloop()

def abrir_fase_ataque(mapa_defensor):
    cache_texturas.clear()
    FILAS_ATK = 10
    COLS_ATK  = 5

    mapa_atk  = [[None for _ in range(COLS_ATK)] for _ in range(FILAS_ATK)]
    atacante  = Atacante(jugadores_activos[1])
    seleccion = {"tipo": TIPOS_ENEMIGO[0]}

    ancho_canvas = COLS_ATK * TAM_CELDA
    alto_canvas  = FILAS_ATK * TAM_CELDA

    ventana_atk = tk.Tk()
    ventana_atk.title(f"Fase de Ataque - {jugadores_activos[1]['username']} (Atacante)")
    ventana_atk.resizable(False, False)

    canvas = tk.Canvas(ventana_atk, width=ancho_canvas, height=alto_canvas)
    canvas.pack()

    panel = tk.Frame(ventana_atk, pady=10, bg="#1a1a2e")
    panel.pack(fill="x")

    lbl_dinero = tk.Label(panel, text=f"💰 {atacante.dinero}", font=("Arial", 13, "bold"),
                          bg="#1a1a2e", fg="#f1c40f")
    lbl_dinero.grid(row=0, column=0, columnspan=5, pady=(0, 6))

    def seleccionar(tipo):
        seleccion["tipo"] = tipo
        lbl_seleccion.config(text=f"Seleccionado: {tipo.nombre}  (${tipo.costo})")

    for i, tipo in enumerate(TIPOS_ENEMIGO):
        tk.Button(panel, text=f"{tipo.nombre}  ${tipo.costo}", width=16, height=2,
                  bg=tipo.color, fg="white", font=("Arial", 9, "bold"), relief="flat",
                  command=lambda t=tipo: seleccionar(t)).grid(row=1, column=i, padx=8)

    lbl_seleccion = tk.Label(panel,
                             text=f"Seleccionado: {TIPOS_ENEMIGO[0].nombre}  (${TIPOS_ENEMIGO[0].costo})",
                             font=("Arial", 9), bg="#1a1a2e", fg="white")
    lbl_seleccion.grid(row=2, column=0, columnspan=5, pady=4)

    lbl_mensaje = tk.Label(panel,
                           text="Clic izquierdo: colocar  |  Clic derecho: borrar (reembolso completo)",
                           font=("Arial", 8), bg="#1a1a2e", fg="#aaaaaa")
    lbl_mensaje.grid(row=3, column=0, columnspan=5)

    def ir_a_batalla():
        jugadores_activos[1]["dinero_batalla"] = atacante.dinero
        ventana_atk.destroy()
        abrir_batalla(mapa_defensor, mapa_atk)

    btn_jugar = tk.Button(panel, text="Jugar  1/2", width=14, height=2,
                          font=("Arial Black", 10), bg="#2ecc71", fg="white",
                          relief="raised", bd=4, command=ir_a_batalla)
    btn_jugar.grid(row=1, column=4, padx=8)

    frame_pausa = tk.Frame(ventana_atk, bg="#2c3e50")
    tk.Label(frame_pausa, text="PAUSA", font=("Arial", 18, "bold"), bg="#2c3e50", fg="white").pack(pady=(80, 20))

    def reanudar():
        frame_pausa.place_forget()
        ventana_atk.focus_set()

    def volver_menu():
        ventana_atk.destroy()
        abrir_menu_principal()

    tk.Button(frame_pausa, text="Reanudar",       width=20, height=2, command=reanudar).pack(pady=10)
    tk.Button(frame_pausa, text="Volver al Menú", width=20, height=2, command=volver_menu).pack(pady=10)

    def toggle_pausa(event=None):
        if frame_pausa.winfo_ismapped():
            reanudar()
        else:
            frame_pausa.place(x=0, y=0, relwidth=1, relheight=1)

    ventana_atk.bind("<Escape>", toggle_pausa)
    ventana_atk.focus_set()

    def dibujar_mapa():
        canvas.delete("all")
        for f in range(FILAS_ATK):
            for c in range(COLS_ATK):
                x0, y0 = c * TAM_CELDA, f * TAM_CELDA
                x1, y1 = x0 + TAM_CELDA, y0 + TAM_CELDA
                celda  = mapa_atk[f][c]
                color_fondo = celda.color if celda else COLORES_FILA[f % 2]
                canvas.create_rectangle(x0, y0, x1, y1, fill=color_fondo, outline="")
                if celda:
                    canvas.create_text(x0 + TAM_CELDA // 2, y0 + TAM_CELDA // 2,
                                       text=celda.nombre[:3], fill="white",
                                       font=("Arial", 9, "bold"))

    def click_colocar(event):
        col  = event.x // TAM_CELDA
        fila = event.y // TAM_CELDA
        if fila >= FILAS_ATK or col >= COLS_ATK:
            return
        exito, resultado = atacante.colocar(mapa_atk, seleccion["tipo"], fila, col)
        if exito:
            lbl_mensaje.config(text=f"Colocado: {resultado.nombre}  |  Dinero restante: ${atacante.dinero}", fg="#2ecc71")
            lbl_dinero.config(text=f"💰 {atacante.dinero}")
        else:
            lbl_mensaje.config(text=resultado, fg="#e74c3c")
        dibujar_mapa()

    def click_borrar(event):
        col  = event.x // TAM_CELDA
        fila = event.y // TAM_CELDA
        if fila >= FILAS_ATK or col >= COLS_ATK:
            return
        exito, resultado = atacante.borrar(mapa_atk, fila, col)
        if exito:
            lbl_mensaje.config(text=f"Eliminado: {resultado.nombre}  |  +${resultado.costo} reembolsado  |  Dinero: ${atacante.dinero}", fg="#f39c12")
            lbl_dinero.config(text=f"💰 {atacante.dinero}")
        else:
            lbl_mensaje.config(text=resultado, fg="#aaaaaa")
        dibujar_mapa()

    canvas.bind("<Button-1>", click_colocar)
    canvas.bind("<Button-3>", click_borrar)
    dibujar_mapa()
    ventana_atk.mainloop()

def abrir_batalla(mapa_defensor, mapa_atacante):

    cache_texturas.clear()

    FILAS_BAT  = 10
    COLS_BAT   = 16
    COLS_DEF   = 11   # columnas 0-10 son del defensor (col 0 = BASE)
    COLS_ENE   = 5    # columnas 11-15 son donde empiezan enemigos

    ancho_canvas = COLS_BAT * TAM_CELDA
    alto_canvas  = FILAS_BAT * TAM_CELDA

    # ── Construir mapa de batalla ──────────────────────────────────────────
    batalla = [[None for _ in range(COLS_BAT)] for _ in range(FILAS_BAT)]

    # Copiar defensas (mapa_defensor es 10x16, columnas 0-15)
    for f in range(FILAS_BAT):
        for c in range(COLS_BAT):
            batalla[f][c] = mapa_defensor[f][c]

    # Copiar enemigos en las últimas 5 columnas (mapa_atacante es 10x5)
    for f in range(FILAS_BAT):
        for c in range(COLS_ENE):
            if mapa_atacante[f][c] is not None:
                batalla[f][COLS_DEF + c] = mapa_atacante[f][c]

    juego_activo = {"corriendo": True}

    ventana_bat = tk.Tk()
    ventana_bat.title("Campo de Batalla")
    ventana_bat.resizable(False, False)

    canvas = tk.Canvas(ventana_bat, width=ancho_canvas, height=alto_canvas)
    canvas.pack()

    panel = tk.Frame(ventana_bat, bg="#1a1a2e")
    panel.pack(side=tk.TOP, fill=tk.X, pady=10)

    dinero_atacante = {"valor": jugadores_activos[1].get("dinero_batalla", 0) if jugadores_activos[1] else 0}
    dinero_defensor = {"valor": jugadores_activos[0].get("dinero_batalla", 0) if jugadores_activos[0] else 0}

    lbl_dinero_atk = tk.Label(panel, text=f"⚔️ Atacante: ${dinero_atacante['valor']}", font=("Arial", 10, "bold"), bg="#1a1a2e", fg="#e74c3c")
    lbl_dinero_atk.grid(row=1, column=3, padx=10)

    lbl_dinero_def = tk.Label(panel, text=f"🛡️ Defensor: ${dinero_defensor['valor']}", font=("Arial", 10, "bold"), bg="#1a1a2e", fg="#2ecc71")
    lbl_dinero_def.grid(row=1, column=4, padx=10)

    lbl_estado = tk.Label(panel, text="⚔️  Batalla en curso...", font=("Arial", 12, "bold"),
                          bg="#1a1a2e", fg="white")
    lbl_estado.grid(row=0, column=0, columnspan=3, pady=(0, 4))

    lbl_dinero_bat = tk.Label(panel, text="💰 Atacante: $0", font=("Arial", 10),
                               bg="#1a1a2e", fg="#f1c40f")
    lbl_dinero_bat.grid(row=1, column=0, padx=20)

    def dibujar():
        canvas.delete("all")
        
        # Obtener facciones elegidas por los jugadores
        faccion_def = jugadores_activos[0].get("faccion", "Normal")
        faccion_atk = jugadores_activos[1].get("faccion", "Normal")

        for f in range(FILAS_BAT):
            for c in range(COLS_BAT):
                x0, y0 = c * TAM_CELDA, f * TAM_CELDA
                x1, y1 = x0 + TAM_CELDA, y0 + TAM_CELDA
                celda  = batalla[f][c]

                # 1. Dibujar el fondo base (pasto/suelo)
                color_fondo = COLORES_FILA[f % 2]
                canvas.create_rectangle(x0, y0, x1, y1, fill=color_fondo, outline="")

                # 2. Determinar textura y dibujar la celda
                if celda is not None:
                    textura_img = None
                    color_fallback = "#c4853a" if celda == "BASE" else celda.color
                    
                    if celda == "BASE":
                        textura_img = obtener_textura(FACCIONES[faccion_def]["BASE"])
                    elif isinstance(celda, Enemigo):
                        textura_img = obtener_textura(FACCIONES[faccion_atk][celda.nombre])
                    elif isinstance(celda, (Torres, Muro)):
                        textura_img = obtener_textura(FACCIONES[faccion_def][celda.nombre])

                    # Dibuja la imagen si existe, si no, usa el color de fallback
                    if textura_img:
                        canvas.create_image(x0 + TAM_CELDA//2, y0 + TAM_CELDA//2, image=textura_img)
                    else:
                        canvas.create_rectangle(x0, y0, x1, y1, fill=color_fallback, outline="")
                        texto = "BAS" if celda == "BASE" else celda.nombre[:3]
                        canvas.create_text(x0 + TAM_CELDA // 2, y0 + TAM_CELDA // 2 - 6,
                                           text=texto, fill="white", font=("Arial", 7, "bold"))

                    # 3. Dibujar la barra de vida (solo enemigos)
                    if isinstance(celda, Enemigo):
                        pct = max(0, celda.vida / celda.vida_max)
                        ancho_barra = 26
                        offset_x = (TAM_CELDA - ancho_barra) // 2
                        canvas.create_rectangle(x0 + offset_x, y1 - 6, x0 + offset_x + ancho_barra, y1 - 3, fill="#555", outline="")
                        canvas.create_rectangle(x0 + offset_x, y1 - 6, x0 + offset_x + int(ancho_barra * pct), y1 - 3, fill="#2ecc71", outline="")

                    if isinstance(celda, Torres):
                        canvas.create_text(x0 + TAM_CELDA // 2, y1 - 12, 
                                           text=f"{celda.vida}", 
                                           fill="white", font=("Arial", 8, "bold"))

    def dibujar_rayo(f_origen, c_origen, f_destino, c_destino, color):
        x1 = c_origen * TAM_CELDA + 25
        y1 = f_origen * TAM_CELDA + 25
        x2 = c_destino * TAM_CELDA + 25
        y2 = f_destino * TAM_CELDA + 25
        
        # Dibujamos y forzamos actualización
        rayo = canvas.create_line(x1, y1, x2, y2, fill=color, width=4, arrow=tk.LAST)
        canvas.update() 
        
        # Aumentamos a 300ms para que el ojo humano alcance a ver el disparo
        ventana_bat.after(500, lambda: canvas.delete(rayo))

    def tick():
        if not juego_activo["corriendo"]:
            return

        gano_atacante = False
        gano_defensor = True

        # --- FASE 1: MOVIMIENTO Y ATAQUE DE ENEMIGOS ---
        for f in range(FILAS_BAT):
            for c in range(COLS_BAT):
                celda = batalla[f][c]
                if not isinstance(celda, Enemigo):
                    continue
                if not celda.esta_vivo():
                    batalla[f][c] = None
                    continue

                gano_defensor = False

                # Habilidad de enemigo
                celda.contador_hab += 1
                atk_efectivo = celda.atk
                if celda.contador_hab >= celda.turnos_habilidad:
                    atk_efectivo = celda.activar_habilidad()
                    celda.contador_hab = 0

                # Congelamiento (Habilidad de Torre Mágica)
                if getattr(celda, "congelado", False):
                    celda.congelado = False
                    continue  # Pierde el turno de movimiento/ataque

                pasos = celda.velocidad + celda.vel_boost
                celda.vel_boost = 0

                for _ in range(pasos):
                    dest = c - 1
                    if dest < 0:
                        batalla[f][c] = None
                        gano_atacante = True
                        break

                    objetivo = batalla[f][dest]

                    if objetivo == "BASE":
                        batalla[f][c] = None
                        gano_atacante = True
                        break

                    elif objetivo is None:
                        batalla[f][dest] = celda
                        batalla[f][c] = None
                        c = dest

                    elif isinstance(objetivo, (Torres, Muro)):
                        # Atacar Defensa
                        reproducir_sonido("ataque_torre")
                        objetivo.vida -= atk_efectivo
                        
                        # Economía Atacante: gana dinero por hacer daño
                        dinero_atacante["valor"] += 10
                        lbl_dinero_atk.config(text=f"⚔️ Atacante: ${dinero_atacante['valor']}")

                        if objetivo.vida <= 0:
                            dinero_atacante["valor"] += objetivo.costo // 2
                            lbl_dinero_atk.config(text=f"⚔️ Atacante: ${dinero_atacante['valor']}")
                            batalla[f][dest] = None
                        break

                if gano_atacante:
                    break
            if gano_atacante:
                break

        # --- FASE 2: ATAQUE DE TORRES ---
        for f in range(FILAS_BAT):
            for c in range(COLS_BAT):
                torre = batalla[f][c]
                if not isinstance(torre, Torres):
                    continue
                    
                torre.contador_especial += 1
                habilidad_activada = False

                if torre.contador_especial >= torre.vel_especial:
                    habilidad_activada = True
                    torre.contador_especial = 0

                # Habilidad Mágica: Curación en área
                if torre.nombre == "Mágica" and habilidad_activada:
                    for df in range(-torre.alcance, torre.alcance + 1):
                        for dc in range(-torre.alcance, torre.alcance + 1):
                            vf, vc = f + df, c + dc
                            if 0 <= vf < FILAS_BAT and 0 <= vc < COLS_BAT:
                                aliado = batalla[vf][vc]
                                if isinstance(aliado, (Torres, Muro)):
                                    if aliado.vida < aliado.vida_max:
                                        aliado.vida += 20  # Cura 20 puntos
                                    dibujar_rayo(f, c, vf, vc, "green")  # Rayo verde curativo
                    continue  # Si curó, ya usó su turno y no ataca

                enemigo_atacado = False
                
                # Búsqueda de objetivos en rango
                for df in range(-torre.alcance, torre.alcance + 1):
                    for dc in range(-torre.alcance, torre.alcance + 1):
                        if abs(df) + abs(dc) <= torre.alcance:
                            objetivo_f = f + df
                            objetivo_c = c + dc
                            
                            if 0 <= objetivo_f < FILAS_BAT and 0 <= objetivo_c < COLS_BAT:
                                objetivo = batalla[objetivo_f][objetivo_c]
                                
                                if isinstance(objetivo, Enemigo):
                                    reproducir_sonido("dano_enemigo")
                                    
                                    # Habilidad Básica: Disparo Doble
                                    if torre.nombre == "Básica" and habilidad_activada:
                                        objetivo.recibir_danio(torre.atk * 2)
                                        dibujar_rayo(f, c, objetivo_f, objetivo_c, "blue") # Rayo azul doble daño
                                    else:
                                        objetivo.recibir_danio(torre.atk)
                                        dibujar_rayo(f, c, objetivo_f, objetivo_c, "yellow") # Rayo normal
                                        
                                    # Habilidad Pesada: Daño Explosivo (Área)
                                    if torre.nombre == "Pesada" and habilidad_activada:
                                        for ef in [-1, 0, 1]:
                                            for ec in [-1, 0, 1]:
                                                af, ac = objetivo_f + ef, objetivo_c + ec
                                                if 0 <= af < FILAS_BAT and 0 <= ac < COLS_BAT:
                                                    adyacente = batalla[af][ac]
                                                    if isinstance(adyacente, Enemigo) and adyacente != objetivo:
                                                        adyacente.recibir_danio(torre.atk)
                                                        dibujar_rayo(objetivo_f, objetivo_c, af, ac, "red") # Explosión roja
                                    
                                    enemigo_atacado = True
                                    break 
                    if enemigo_atacado:
                        break

        # Limpieza general de enemigos muertos (necesario por el daño en área)
        for f_b in range(FILAS_BAT):
            for c_b in range(COLS_BAT):
                entidad = batalla[f_b][c_b]
                if isinstance(entidad, Enemigo) and not entidad.esta_vivo():
                    reproducir_sonido("muerte_tropa")
                    dinero_defensor["valor"] += entidad.costo
                    lbl_dinero_def.config(text=f"🛡️ Defensor: ${dinero_defensor['valor']}")
                    batalla[f_b][c_b] = None

        dibujar()

        def extraer_mapa_persistente():
            nuevo_mapa = [[None for _ in range(16)] for _ in range(10)]
            for f_map in range(10):
                for c_map in range(16):
                    # Guardar solo Torres, Muros y la BASE
                    if isinstance(batalla[f_map][c_map], (Torres, Muro)) or batalla[f_map][c_map] == "BASE":
                        nuevo_mapa[f_map][c_map] = batalla[f_map][c_map]
            return nuevo_mapa

        if gano_atacante:
            juego_activo["corriendo"] = False
            lbl_estado.config(text="💀 ¡El atacante ha ganado esta ronda!", fg="#e74c3c")
            jugadores_activos[1]["dinero_batalla"] = dinero_atacante["valor"]
            jugadores_activos[0]["dinero_batalla"] = dinero_defensor["valor"]
            mapa_guardado = extraer_mapa_persistente()
            ventana_bat.after(2500, lambda: procesar_fin_ronda(ventana_bat, "atacante", mapa_guardado))
            return

        if gano_defensor:
            juego_activo["corriendo"] = False
            lbl_estado.config(text="🏆 ¡El defensor ha ganado esta ronda!", fg="#2ecc71")
            jugadores_activos[1]["dinero_batalla"] = dinero_atacante["valor"]
            jugadores_activos[0]["dinero_batalla"] = dinero_defensor["valor"]
            mapa_guardado = extraer_mapa_persistente()
            ventana_bat.after(2500, lambda: procesar_fin_ronda(ventana_bat, "defensor", mapa_guardado))
            return

        ventana_bat.after(600, tick)

    dibujar()
    ventana_bat.after(600, tick)
    ventana_bat.mainloop()

# ── PUNTO DE ENTRADA ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    abrir_login(0)
