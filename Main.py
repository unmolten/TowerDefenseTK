import tkinter as tk

"""
ESTADOS GLOBALES
"""
estado = {"textura": "predeterminado","volumen": 50,"musica_pausada": False,}

CICLO_TEXTURAS = ["predeterminado", "colores calidos", "colores frios"]

"""
VENTANA PRINCIPAL
"""
def abrir_menu_principal():
    ventana_principal = tk.Tk()
    ventana_principal.title("Menú Principal")
    ventana_principal.geometry("800x500")
    ventana_principal.resizable(False, False)

    tk.Label(ventana_principal, text="").pack(pady=80)

    frame_botones = tk.Frame(ventana_principal)
    frame_botones.pack()

    def ir_a_jugar():
        ventana_principal.destroy()
        abrir_juego()

    def ir_a_configuracion():
        ventana_principal.destroy()
        abrir_configuracion()

    btn_jugar = tk.Button(frame_botones, text="Jugar", width=18, height=3,command=ir_a_jugar)
    btn_jugar.grid(row=0, column=0, padx=60)

    btn_config = tk.Button(frame_botones, text="Configuración", width=18, height=3,command=ir_a_configuracion)
    btn_config.grid(row=0, column=1, padx=60)

    ventana_principal.mainloop()


"""
VENTANA DE JUEGO
"""
def abrir_juego():
    ventana_juego = tk.Tk()
    ventana_juego.title("Juego")
    ventana_juego.geometry("800x500")
    ventana_juego.resizable(False, False)

    #Menu de pausa
    frame_pausa = tk.Frame(ventana_juego)

    lbl_pausa = tk.Label(frame_pausa, text="PAUSA", font=("Arial", 18, "bold"))
    lbl_pausa.pack(pady=(140, 20))

    def reanudar():
        frame_pausa.place_forget()
        ventana_juego.focus_set()

    def volver_menu():
        ventana_juego.destroy()
        abrir_menu_principal()

    btn_reanudar = tk.Button(frame_pausa, text="Reanudar", width=20, height=2,command=reanudar)
    btn_reanudar.pack(pady=10)

    btn_menu = tk.Button(frame_pausa, text="Volver al Menú", width=20, height=2,command=volver_menu)
    btn_menu.pack(pady=10)

    #funcion del esc
    def toggle_pausa(event=None):
        if frame_pausa.winfo_ismapped():
            reanudar()
        else:
            frame_pausa.place(x=0, y=0, relwidth=1, relheight=1)

    ventana_juego.bind("<Escape>", toggle_pausa)
    ventana_juego.focus_set()

    ventana_juego.mainloop()


"""
VENTANA DE CONFIGURACION
"""
def abrir_configuracion():
    ventana_config = tk.Tk()
    ventana_config.title("Configuración")
    ventana_config.geometry("800x500")
    ventana_config.resizable(False, False)

    tk.Label(ventana_config, text="Configuración", font=("Arial", 16, "bold")).pack(pady=20)

    #fila 1: volver al meno y cerrar juego
    frame_fila1 = tk.Frame(ventana_config)
    frame_fila1.pack(pady=10)

    def volver_menu():
        ventana_config.destroy()
        abrir_menu_principal()

    def cerrar_juego():
        ventana_config.destroy()

    tk.Button(frame_fila1, text="Volver al Menú", width=18, height=2,command=volver_menu).grid(row=0, column=0, padx=40)

    tk.Button(frame_fila1, text="Cerrar Juego", width=18, height=2,command=cerrar_juego).grid(row=0, column=1, padx=40)

    #fila 2: funciones musica
    tk.Label(ventana_config, text="Música", font=("Arial", 11)).pack(pady=(20, 5))

    frame_fila2 = tk.Frame(ventana_config)
    frame_fila2.pack(pady=5)

    #Botón de pausar o reanudar música
    lbl_musica_estado = ["Pausar Música" if not estado["musica_pausada"] else "Reanudar Música"]

    btn_musica = tk.Button(frame_fila2, text=lbl_musica_estado[0], width=18, height=2)

    def toggle_musica():
        estado["musica_pausada"] = not estado["musica_pausada"]
        if estado["musica_pausada"]:
            btn_musica.config(text="Reanudar Música")
            #pygame.mixer.music.pause() *aqui lo ponemos cuando importemos la musica*
        else:
            btn_musica.config(text="Pausar Música")
            #pygame.mixer.music.unpause() *aqui lo ponemos cuando importemos la musica*

    btn_musica.config(command=toggle_musica)
    btn_musica.grid(row=0, column=0, padx=30)

    #Barra de volumen
    frame_volumen = tk.Frame(frame_fila2)
    frame_volumen.grid(row=0, column=1, padx=30)

    tk.Label(frame_volumen, text="Volumen").pack()

    lbl_vol_valor = tk.Label(frame_volumen, text=str(estado["volumen"]))
    lbl_vol_valor.pack()

    def cambiar_volumen(val):
        estado["volumen"] = int(float(val))
        lbl_vol_valor.config(text=str(estado["volumen"]))
        #pygame.mixer.music.set_volume(estado["volumen"] / 100)  *aqui lo ponemos cuando importemos la musica*

    slider_volumen = tk.Scale(frame_volumen, from_=0, to=100, orient="horizontal",length=200, command=cambiar_volumen, showvalue=False)
    slider_volumen.set(estado["volumen"])
    slider_volumen.pack()

    #fila 3: Texturas
    tk.Label(ventana_config, text="Texturas", font=("Arial", 11)).pack(pady=(20, 5))

    frame_fila3 = tk.Frame(ventana_config)
    frame_fila3.pack(pady=5)

    lbl_textura = tk.Label(frame_fila3,text=f"Textura actual: {estado['textura']}",font=("Arial", 10))
    lbl_textura.grid(row=0, column=0, padx=20)

    def ciclar_textura():
        idx_actual = CICLO_TEXTURAS.index(estado["textura"])
        siguiente = (idx_actual + 1) % len(CICLO_TEXTURAS)
        estado["textura"] = CICLO_TEXTURAS[siguiente]
        lbl_textura.config(text=f"Textura actual: {estado['textura']}")
        btn_textura.config(text=estado["textura"].capitalize())

    btn_textura = tk.Button(frame_fila3, text=estado["textura"].capitalize(),width=18, height=2, command=ciclar_textura)
    btn_textura.grid(row=0, column=1, padx=20)

    ventana_config.mainloop()


"""
PUNTO DE ENTRADA
"""
if __name__ == "__main__":
    abrir_menu_principal()