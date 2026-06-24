import tkinter as tk
import json
import os

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
        self.vida   = 100
        self.costo  = 30
        self.color  = "#7f8c8d"

    def clonar(self):
        return Muro()


# ── TIPOS DISPONIBLES (sin subclases) ─────────────────────────────────────────
# Estos son los templates. Cuando el jugador coloca uno, se clona con copy.copy()

TIPOS_TORRE = [
    Torres("Básica", vida=60,  atk=10, costo=50,  alcance=3, vel_especial=5, color="#3498db"),
    Torres("Pesada", vida=200, atk=30, costo=120, alcance=2, vel_especial=4, color="#e74c3c"),
    Torres("Mágica", vida=50,  atk=8,  costo=90,  alcance=4, vel_especial=3, color="#9b59b6"),
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
        self.dinero  = self.DINERO_INICIAL

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
        self.dinero    += celda.costo   # reembolso completo
        mapa[fila][col] = None
        return True, celda

class Atacante:
    DINERO_INICIAL = 400

    def __init__(self, jugador):
        self.jugador = jugador
        self.dinero  = self.DINERO_INICIAL

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


# ── ESTADOS GLOBALES ──────────────────────────────────────────────────────────
estado = {
    "textura":        "predeterminado",
    "volumen":        50,
    "musica_pausada": False,
}
CICLO_TEXTURAS    = ["predeterminado", "animado", "realista"]
jugadores_activos = [None, None]


# ── VENTANA DE LOGIN ──────────────────────────────────────────────────────────
def abrir_login(turno):
    ventana_login = tk.Tk()
    ventana_login.title(f"Login - Jugador {turno + 1}")
    ventana_login.geometry("800x500")
    ventana_login.resizable(False, False)

    tk.Label(ventana_login, text=f"Jugador {turno + 1}", font=("Arial", 18, "bold")).pack(pady=40)

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

    tk.Button(ventana_principal, text="JUGAR", width=16, height=2, command=ir_a_jugar,
              font=("Arial Black", 14), bg="#2B2B2B", fg="#A3E4D7", bd=5, relief="raised",
              activebackground="#404040", activeforeground="#A3E4D7").place(relx=0.35, rely=0.6, anchor="center")
    tk.Button(ventana_principal, text="CONFIGURACIÓN", width=16, height=2, command=ir_a_configuracion,
              font=("Arial Black", 14), bg="#2B2B2B", fg="#A3E4D7", bd=5, relief="raised",
              activebackground="#404040", activeforeground="#A3E4D7").place(relx=0.65, rely=0.6, anchor="center")

    ventana_principal.mainloop()


# ── VENTANA DE JUEGO ──────────────────────────────────────────────────────────
def abrir_juego():
    mapa = [[None for _ in range(COLS)] for _ in range(FILAS)]
    for f in range(FILAS):
        mapa[f][COL_BASE] = "BASE"

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

    tk.Label(ventana_config, text="Texturas", font=("Arial", 11)).pack(pady=(20, 5))

    frame_fila3 = tk.Frame(ventana_config)
    frame_fila3.pack(pady=5)

    lbl_textura = tk.Label(frame_fila3, text=f"Textura actual: {estado['textura']}", font=("Arial", 10))
    lbl_textura.grid(row=0, column=0, padx=20)

    def ciclar_textura():
        idx = CICLO_TEXTURAS.index(estado["textura"])
        estado["textura"] = CICLO_TEXTURAS[(idx + 1) % len(CICLO_TEXTURAS)]
        lbl_textura.config(text=f"Textura actual: {estado['textura']}")
        btn_textura.config(text=estado["textura"].capitalize())

    btn_textura = tk.Button(frame_fila3, text=estado["textura"].capitalize(), width=18, height=2,
                            command=ciclar_textura, font=("Arial Black", 10), bg="#D1D5C4",
                            fg="#2B2B2B", bd=4, relief="groove")
    btn_textura.grid(row=0, column=1, padx=20)

    ventana_config.mainloop()


# ── VENTANA DE RANKING ────────────────────────────────────────────────────────
def abrir_ranking():
    ventana_ranking = tk.Tk()
    ventana_ranking.title("Registro de Puntos")
    ventana_ranking.geometry("800x500")
    ventana_ranking.resizable(False, False)

    tk.Label(ventana_ranking, text="Top Jugadores", font=("Arial", 16, "bold")).pack(pady=20)

    def volver_config():
        ventana_ranking.destroy()
        abrir_configuracion()

    tk.Button(ventana_ranking, text="Volver a Configuración", width=22, height=2, command=volver_config).pack(pady=20)

    ventana_ranking.mainloop()

def abrir_fase_ataque(mapa_defensor):
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
    dinero_atacante = {"valor": jugadores_activos[1].get("dinero_batalla", 0) if jugadores_activos[1] else 0}

    ventana_bat = tk.Tk()
    ventana_bat.title("Campo de Batalla")
    ventana_bat.resizable(False, False)

    canvas = tk.Canvas(ventana_bat, width=ancho_canvas, height=alto_canvas)
    canvas.pack()

    panel = tk.Frame(ventana_bat, pady=8, bg="#1a1a2e")
    panel.pack(fill="x")

    lbl_estado = tk.Label(panel, text="⚔️  Batalla en curso...", font=("Arial", 12, "bold"),
                          bg="#1a1a2e", fg="white")
    lbl_estado.grid(row=0, column=0, columnspan=3, pady=(0, 4))

    lbl_dinero_bat = tk.Label(panel, text="💰 Atacante: $0", font=("Arial", 10),
                               bg="#1a1a2e", fg="#f1c40f")
    lbl_dinero_bat.grid(row=1, column=0, padx=20)

    def volver_menu():
        juego_activo["corriendo"] = False
        ventana_bat.destroy()
        abrir_menu_principal()

    tk.Button(panel, text="Volver al Menú", width=16, height=1,
              bg="#c0392b", fg="white", font=("Arial", 9, "bold"),
              command=volver_menu).grid(row=1, column=2, padx=20)

    def dibujar():
        canvas.delete("all")
        for f in range(FILAS_BAT):
            for c in range(COLS_BAT):
                x0, y0 = c * TAM_CELDA, f * TAM_CELDA
                x1, y1 = x0 + TAM_CELDA, y0 + TAM_CELDA
                celda  = batalla[f][c]

                if celda == "BASE":
                    color_fondo = "#c4853a"
                elif celda is None:
                    color_fondo = COLORES_FILA[f % 2]
                elif isinstance(celda, Enemigo):
                    color_fondo = celda.color
                else:
                    color_fondo = celda.color

                canvas.create_rectangle(x0, y0, x1, y1, fill=color_fondo, outline="")

                if celda is not None and celda != "BASE":
                    # nombre
                    canvas.create_text(x0 + TAM_CELDA // 2, y0 + TAM_CELDA // 2 - 6,
                                       text=celda.nombre[:3], fill="white",
                                       font=("Arial", 7, "bold"))
                    # barra de vida solo para enemigos
                    if isinstance(celda, Enemigo):
                        pct = max(0, celda.vida / celda.vida_max)
                        canvas.create_rectangle(x0+2, y1-7, x1-2, y1-2, fill="#555", outline="")
                        canvas.create_rectangle(x0+2, y1-7, x0+2+int((TAM_CELDA-4)*pct), y1-2,
                                                fill="#2ecc71", outline="")

    def tick():
        if not juego_activo["corriendo"]:
            return

        gano_atacante = False
        gano_defensor = True  # asume que gana defensor salvo que queden enemigos

        for f in range(FILAS_BAT):
            # recorrer de izquierda a derecha para mover enemigos sin pisarse
            for c in range(COLS_BAT):
                celda = batalla[f][c]
                if not isinstance(celda, Enemigo):
                    continue
                if not celda.esta_vivo():
                    batalla[f][c] = None
                    continue

                gano_defensor = False  # hay al menos un enemigo vivo

                # habilidad por contador
                celda.contador_hab += 1
                atk_efectivo = celda.atk
                if celda.contador_hab >= celda.turnos_habilidad:
                    atk_efectivo = celda.activar_habilidad()
                    celda.contador_hab = 0

                pasos = celda.velocidad + celda.vel_boost
                celda.vel_boost = 0

                for _ in range(pasos):
                    dest = c - 1
                    if dest < 0:
                        # llegó a la base — atacante gana
                        batalla[f][c] = None
                        gano_atacante = True
                        break

                    objetivo = batalla[f][dest]

                    if objetivo == "BASE":
                        batalla[f][c] = None
                        gano_atacante = True
                        break

                    elif objetivo is None:
                        # moverse
                        batalla[f][dest] = celda
                        batalla[f][c]    = None
                        c = dest

                    elif isinstance(objetivo, Torres) or isinstance(objetivo, Muro):
                        # atacar torre/muro
                        objetivo.vida -= atk_efectivo
                        if objetivo.vida <= 0:
                            dinero_atacante["valor"] += objetivo.costo // 2
                            lbl_dinero_bat.config(text=f"💰 Atacante: ${dinero_atacante['valor']}")
                            batalla[f][dest] = None
                        break

                if gano_atacante:
                    break
            if gano_atacante:
                break

        # torres atacan a enemigos en su alcance
        for f in range(FILAS_BAT):
            for c in range(COLS_BAT):
                torre = batalla[f][c]
                if not isinstance(torre, Torres):
                    continue
                torre.contador_especial += 1
                atk_torre = torre.atk
                if torre.contador_especial >= torre.vel_especial:
                    torre.contador_especial = 0

                # buscar enemigo más cercano a la izquierda dentro del alcance
                for dc in range(1, torre.alcance + 1):
                    objetivo_c = c + dc  # enemigos vienen de la derecha
                    if objetivo_c >= COLS_BAT:
                        break
                    objetivo = batalla[f][objetivo_c]
                    if isinstance(objetivo, Enemigo):
                        objetivo.recibir_danio(atk_torre)
                        if not objetivo.esta_vivo():
                            dinero_atacante["valor"] += objetivo.costo // 2
                            lbl_dinero_bat.config(text=f"💰 Atacante: ${dinero_atacante['valor']}")
                            batalla[f][objetivo_c] = None
                        break

        dibujar()

        if gano_atacante:
            juego_activo["corriendo"] = False
            lbl_estado.config(text="💀 ¡El atacante ha ganado!", fg="#e74c3c")
            return

        if gano_defensor:
            juego_activo["corriendo"] = False
            lbl_estado.config(text="🏆 ¡El defensor ha ganado!", fg="#2ecc71")
            return

        ventana_bat.after(600, tick)

    dibujar()
    ventana_bat.after(600, tick)
    ventana_bat.mainloop()

# ── PUNTO DE ENTRADA ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    abrir_login(0)
