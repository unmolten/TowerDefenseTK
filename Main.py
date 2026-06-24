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


# ── PUNTO DE ENTRADA ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    abrir_login(0)
