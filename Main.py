import tkinter as tk
import json
import os

# ── ARCHIVO DE JUGADORES ──────────────────────────────────────────────────────
# Todos los usuarios se guardan en este archivo JSON.
# Si no existe, se crea automaticamente cuando el primer jugador se registra.
ARCHIVO_JUGADORES = "jugadores.json"


# ── FUNCIONES DE ARCHIVO ──────────────────────────────────────────────────────

def cargar_jugadores():
    # Si el archivo no existe todavia, retorna un diccionario vacio
    if not os.path.exists(ARCHIVO_JUGADORES):
        return {}
    with open(ARCHIVO_JUGADORES, "r") as f:
        return json.load(f)
    # El archivo se ve asi por dentro:
    # {
    #   "gabo": {"contrasena": "1234", "victorias_defensor": 0, "victorias_atacante": 0},
    #   "mathi": {"contrasena": "1234", "victorias_defensor": 2, "victorias_atacante": 1}
    # }

def guardar_jugadores(jugadores):
    # Recibe el diccionario completo y lo sobreescribe en el archivo
    with open(ARCHIVO_JUGADORES, "w") as f:
        json.dump(jugadores, f, indent=4)  # indent=4 lo hace legible si abres el archivo

def registrar_jugador(username, password):
    jugadores = cargar_jugadores()

    if username in jugadores:
        return False, "El usuario ya existe."  # no permite duplicados

    # Crea la entrada del nuevo jugador con victorias en 0
    jugadores[username] = {
        "contrasena": password, #la Ñ se ve horrible en el json
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

    return True, jugadores[username]  # retorna los datos del jugador si todo esta bien


# ── ESTADOS GLOBALES ──────────────────────────────────────────────────────────
estado = {
    "textura": "predeterminado",
    "volumen": 50,
    "musica_pausada": False,
}

CICLO_TEXTURAS = ["predeterminado", "animado", "realista"]


# ── VENTANA DE LOGIN ──────────────────────────────────────────────────────────
# Primera pantalla que ve el usuario. Permite registrarse o iniciar sesion.

jugadores_activos = [None, None]

""" abrir_login(turno) maneja el login de ambos jugadores secuencialmente.
turno=0 es jugador 1, turno=1 es jugador 2.
cuando turno=0 termina exitosamente, se llama a si misma con turno=1.
uando turno=1 termina exitosamente, avanza al menu principal. """
def abrir_login(turno):
    ventana_login = tk.Tk()
    ventana_login.title(f"Login - Jugador {turno + 1}")
    ventana_login.geometry("800x500")
    ventana_login.resizable(False, False)

    # titulo dinamico segun que jugador esta logueando
    tk.Label(ventana_login, text=f"Jugador {turno + 1}", font=("Arial", 18, "bold")).pack(pady=40)

    tk.Label(ventana_login, text="Usuario").pack()
    entry_usuario = tk.Entry(ventana_login, width=30)
    entry_usuario.pack(pady=5)

    tk.Label(ventana_login, text="Contraseña").pack()
    # show="*" reemplaza cada caracter con un asterisco para ocultar la contrasena visualmente
    entry_password = tk.Entry(ventana_login, width=30, show="*")
    entry_password.pack(pady=5)

    # label vacio al inicio, se actualiza con mensajes de error o exito segun la accion
    lbl_mensaje = tk.Label(ventana_login, text="", font=("Arial", 9))
    lbl_mensaje.pack(pady=5)

    def intentar_login():
        # .strip() elimina espacios en blanco al inicio y al final del texto
        username = entry_usuario.get().strip()
        password = entry_password.get().strip()

        # validacion basica: ningun campo puede estar vacio
        if not username or not password:
            lbl_mensaje.config(text="Completa todos los campos.", fg="red")
            return 0

        # el jugador 2 no puede usar la misma cuenta que el jugador 1
        # jugadores_activos[0] ya existe porque el jugador 1 loguo primero
        if turno == 1 and username == jugadores_activos[0]["username"]:
            lbl_mensaje.config(text="El jugador 2 debe usar una cuenta diferente.", fg="red")
            return 0

        # iniciar_sesion() retorna (True, datos_del_jugador) o (False, mensaje_de_error)
        exito, resultado = iniciar_sesion(username, password)

        if exito:
            # **resultado desempaca el diccionario del JSON y lo mezcla con el username
            # queda: {"username": "gabo", "contrasena": "...", "victorias_defensor": 0, ...}
            jugadores_activos[turno] = {"username": username, **resultado}
            ventana_login.destroy()

            if turno == 0:
                # jugador 1 listo, abre inmediatamente el login del jugador 2
                abrir_login(1)
            else:
                # jugador 2 listo, ambos estan logueados, avanza al juego
                abrir_menu_principal()
        else:
            # resultado contiene el mensaje de error cuando exito=False
            lbl_mensaje.config(text=resultado, fg="red")

    def intentar_registro():
        username = entry_usuario.get().strip()
        password = entry_password.get().strip()

        if not username or not password:
            lbl_mensaje.config(text="Completa todos los campos.", fg="red")
            return 0

        # registrar_jugador() retorna (True, "Registro exitoso.") o (False, "El usuario ya existe.")
        exito, mensaje = registrar_jugador(username, password)
        # operador ternario: si exito es True usa verde, si no usa rojo
        lbl_mensaje.config(text=mensaje, fg="green" if exito else "red")

    frame_botones = tk.Frame(ventana_login)
    frame_botones.pack(pady=15)

    tk.Button(frame_botones, text="Iniciar Sesión", width=18, height=2, command=intentar_login).grid(row=0, column=0, padx=20)
    tk.Button(frame_botones, text="Registrarse", width=18, height=2, command=intentar_registro).grid(row=0, column=1, padx=20)

    ventana_login.mainloop()


# ── VENTANA PRINCIPAL ─────────────────────────────────────────────────────────
# Solo se abre si el login fue exitoso.

def abrir_menu_principal():
    ventana_principal = tk.Tk()  
    ventana_principal.title("Menú Principal")  
    ventana_principal.geometry("800x500")
    ventana_principal.resizable(False, False)

    #Se carga el archivo de imagen de fondo
    imagen_fondo = tk.PhotoImage(file="Fondo_principal.png")
    ventana_principal.imagen_fondo = imagen_fondo 

    #Se crea la capa del fondo estirada en toda la ventana
    lbl_fondo = tk.Label(ventana_principal, image=imagen_fondo)
    lbl_fondo.place(x=0, y=0, relwidth=1, relheight=1)

    def ir_a_jugar():
        ventana_principal.destroy()
        abrir_juego()

    def ir_a_configuracion():
        ventana_principal.destroy()
        abrir_configuracion()
    
    tk.Button(ventana_principal, text="JUGAR", width=16, height=2, command=ir_a_jugar,font=("Arial Black", 14), bg="#2B2B2B", fg="#A3E4D7", bd=5, relief="raised", activebackground="#404040", activeforeground="#A3E4D7").place(relx=0.35, rely=0.6, anchor="center")      
    tk.Button(ventana_principal, text="CONFIGURACIÓN", width=16, height=2, command=ir_a_configuracion,font=("Arial Black", 14), bg="#2B2B2B", fg="#A3E4D7", bd=5, relief="raised", activebackground="#404040", activeforeground="#A3E4D7").place(relx=0.65, rely=0.6, anchor="center")

    ventana_principal.mainloop()


# ── VENTANA DE JUEGO ──────────────────────────────────────────────────────────

def abrir_juego():
    ventana_juego = tk.Tk()
    ventana_juego.title("Juego")
    ventana_juego.geometry("800x500")
    ventana_juego.resizable(False, False)

    # El frame de pausa se crea aqui pero empieza oculto.
    # Cuando el usuario presiona Escape, se coloca encima de todo con .place()
    frame_pausa = tk.Frame(ventana_juego)

    tk.Label(frame_pausa, text="PAUSA", font=("Arial", 18, "bold")).pack(pady=(140, 20))

    def reanudar():
        frame_pausa.place_forget()  # place_forget() lo oculta sin destruirlo
        ventana_juego.focus_set()

    def volver_menu():
        ventana_juego.destroy()
        abrir_menu_principal()

    tk.Button(frame_pausa, text="Reanudar", width=20, height=2, command=reanudar).pack(pady=10)
    tk.Button(frame_pausa, text="Volver al Menú", width=20, height=2, command=volver_menu).pack(pady=10)

    def toggle_pausa(event=None):
        if frame_pausa.winfo_ismapped():  # winfo_ismapped() retorna True si el frame es visible
            reanudar()
        else:
            # relwidth=1, relheight=1 hace que cubra el 100% de la ventana
            frame_pausa.place(x=0, y=0, relwidth=1, relheight=1)

    ventana_juego.bind("<Escape>", toggle_pausa)  # bind conecta una tecla a una funcion
    ventana_juego.focus_set()

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

    tk.Button(frame_fila1, text="Volver al Menú", width=18, height=2, command=volver_menu).grid(row=0, column=0, padx=40)
    def ir_a_ranking():
        ventana_config.destroy()
        abrir_ranking()

    tk.Button(frame_fila1, text="VOLVER AL MENÚ", width=18, height=2, command=volver_menu,font=("Arial Black", 10), bg="#D1D5C4", fg="#2B2B2B", bd=4, relief="groove", activebackground="#C2C6B5", activeforeground="#2B2B2B").grid(row=0, column=0, padx=15)       
    tk.Button(frame_fila1, text="REGISTRO DE PUNTOS", width=18, height=2, command=ir_a_ranking,font=("Arial Black", 10), bg="#D1D5C4", fg="#2B2B2B", bd=4, relief="groove", activebackground="#C2C6B5", activeforeground="#2B2B2B").grid(row=0, column=1, padx=15) 
    tk.Button(frame_fila1, text="CERRAR JUEGO", width=18, height=2, command=ventana_config.destroy,font=("Arial Black", 10), bg="#D1D5C4", fg="#2B2B2B", bd=4, relief="groove", activebackground="#C2C6B5", activeforeground="#2B2B2B").grid(row=0, column=2, padx=15)

    frame_fila2 = tk.Frame(ventana_config)
    frame_fila2.pack(pady=5)

    btn_musica = tk.Button(frame_fila2, text="Pausar Música", width=18, height=2,font=("Arial Black", 10), bg="#D1D5C4", fg="#2B2B2B", bd=4, relief="groove")

    def toggle_musica():
        estado["musica_pausada"] = not estado["musica_pausada"]
        # El operador ternario elige el texto segun el estado actual
        btn_musica.config(text="Reanudar Música" if estado["musica_pausada"] else "Pausar Música")
        # pygame.mixer.music.pause() o .unpause() van aqui cuando agreguen audio

    btn_musica.config(command=toggle_musica)
    btn_musica.grid(row=0, column=0, padx=30)

    frame_volumen = tk.Frame(frame_fila2)
    frame_volumen.grid(row=0, column=1, padx=30)

    tk.Label(frame_volumen, text="Volumen").pack()
    lbl_vol_valor = tk.Label(frame_volumen, text=str(estado["volumen"]))
    lbl_vol_valor.pack()

    def cambiar_volumen(val):
        # val llega como string desde el Scale, por eso se convierte a int
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
        idx_actual = CICLO_TEXTURAS.index(estado["textura"])  # busca la posicion actual en la lista
        siguiente = (idx_actual + 1) % len(CICLO_TEXTURAS)    # % hace que vuelva al inicio al llegar al final
        estado["textura"] = CICLO_TEXTURAS[siguiente]
        lbl_textura.config(text=f"Textura actual: {estado['textura']}")
        btn_textura.config(text=estado["textura"].capitalize())

    btn_textura = tk.Button(frame_fila3, text=estado["textura"].capitalize(),width=18, height=2, command=ciclar_textura,font=("Arial Black", 10), bg="#D1D5C4", fg="#2B2B2B", bd=4, relief="groove")
    btn_textura.grid(row=0, column=1, padx=20)

    ventana_config.mainloop()

# ── VENTANA DE RANKING / REGISTRO DE PUNTOS ───────────────────────────────────
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
# El programa siempre arranca en el login, no en el menu principal.

if __name__ == "__main__":
    abrir_login(0)