from tkinter import *
from PIL import ImageTk, Image
import random
import tkinter.messagebox as tmsg
import os

# Intentamos usar pygame para audio
try:
    import pygame
    PYGAME_AVAILABLE = True
except Exception:
    PYGAME_AVAILABLE = False

# --- Configuración inicial de la ventana ---
root = Tk()
root.title("CodeLearn Game")
root.geometry("900x560")
root.resizable(False, False)
root.config(bg="#1e1e1e")

# ----------------- Datos del juego -----------------
# Preguntas tipo quiz
preguntas_python = [
    {"pregunta": "¿Qué tipo de lenguaje es Python?",
     "opciones": ["Compilado", "Interpretado", "Ensamblador", "Binario"],
     "respuesta": "Interpretado"},
    {"pregunta": "¿Qué se usa para imprimir texto en pantalla?",
     "opciones": ["print()", "echo()", "mostrar()", "console.log()"],
     "respuesta": "print()"},
    {"pregunta": "¿Qué símbolo se usa para los comentarios en Python?",
     "opciones": ["//", "#", "/* */", "--"],
     "respuesta": "#"}
]

# Ejercicios de práctica (completar el fragmento)
practica_python = [
    {
        "enunciado": "Completa la instrucción para imprimir 'Hola':\nprint(___)",
        "solucion": " 'Hola' ",
        "pista": "Incluye las comillas alrededor del texto."
    },
    {
        "enunciado": "Completa la definición de una función vacía:\ndef saludo():\n    ___",
        "solucion": "pass",
        "pista": "Palabra que indica 'no hace nada' en Python."
    },
    {
        "enunciado": "Operador para sumar a y b: resultado = a ___ b",
        "solucion": "+",
        "pista": "Operador aritmético básico."
    }
]

# Variables globales de control
indice_pregunta = 0
puntaje = 0
jugador_global = ""
indice_practica = 0

# ----------------- Audio (pygame) -----------------
MUSIC_FILE = "background.mp3"   # Cambia la ruta si lo necesitas
SOUND_CORRECT = "correct.wav"
SOUND_INCORRECT = "incorrect.wav"

music_playing = False

def init_audio():
    global music_playing
    if not PYGAME_AVAILABLE:
        print("pygame no está disponible: la música no funcionará. Instala pygame con 'pip install pygame'.")
        return
    try:
        pygame.mixer.init()
        # Cargar música en modo stream
        if os.path.exists(MUSIC_FILE):
            pygame.mixer.music.load(MUSIC_FILE)
            pygame.mixer.music.set_volume(0.25)
            music_playing = False
        else:
            print(f"No se encontró {MUSIC_FILE} en la carpeta del script.")
    except Exception as e:
        print("Error inicializando pygame.mixer:", e)

def play_music(loop=True):
    global music_playing
    if not PYGAME_AVAILABLE: return
    try:
        if not pygame.mixer.music.get_busy():
            pygame.mixer.music.play(-1 if loop else 0)
        music_playing = True
    except Exception as e:
        print("No se pudo reproducir la música:", e)

def pause_music():
    global music_playing
    if not PYGAME_AVAILABLE: return
    try:
        pygame.mixer.music.pause()
        music_playing = False
    except:
        pass

def unpause_music():
    global music_playing
    if not PYGAME_AVAILABLE: return
    try:
        pygame.mixer.music.unpause()
        music_playing = True
    except:
        pass

def stop_music():
    global music_playing
    if not PYGAME_AVAILABLE: return
    try:
        pygame.mixer.music.stop()
        music_playing = False
    except:
        pass

def play_sound_effect(path):
    if not PYGAME_AVAILABLE: return
    try:
        if os.path.exists(path):
            s = pygame.mixer.Sound(path)
            s.set_volume(0.6)
            s.play()
    except Exception as e:
        print("Error reproducir efecto:", e)

# Inicializar audio al arrancar (intento silencioso)
init_audio()

# ----------------- Pie de página -----------------
def crear_footer(mostrar_musica=True):
    footer = Frame(root, bg="#111111", height=60)
    footer.pack(fill=X, side=BOTTOM)
    footer.pack_propagate(False)

    Label(footer,
          text="Universidad del Norte – Lenguajes Visuales II – 2025",
          font=("Arial", 9, "bold"),
          fg="gray", bg="#111111").pack(side=LEFT, padx=10)

    Label(footer,
          text=f"Desarrollado por : Brahian S.S.E",
          font=("Arial", 9, "italic"),
          fg="#00ff99", bg="#111111").pack(side=LEFT, padx=10)

    Label(footer,
          text="Versión 1.1",
          font=("Arial", 9, "bold"),
          fg="gray", bg="#111111").pack(side=RIGHT, padx=10)

    # Controles de música
    if mostrar_musica:
        ctrl_frame = Frame(footer, bg="#111111")
        ctrl_frame.pack(side=RIGHT, padx=140)
        def toggle_music_btn():
            global music_playing
            if not PYGAME_AVAILABLE:
                tmsg.showinfo("Audio no disponible", "Instala pygame: pip install pygame")
                return
            if music_playing:
                pause_music()
                btn_music.config(text="▶ Música")
            else:
                # si pausado, reanudar; si no ha empezado, iniciar
                try:
                    if pygame.mixer.music.get_busy():
                        unpause_music()
                    else:
                        play_music()
                    btn_music.config(text="⏸ Pausa")
                except:
                    play_music()
                    btn_music.config(text="⏸ Pausa")
        btn_music = Button(ctrl_frame, text=("⏸ Pausa" if music_playing else "▶ Música"),
                           font=("Arial", 10), bg="#222", fg="#00ff99",
                           command=toggle_music_btn)
        btn_music.pack(side=LEFT, padx=6)

# ----------------- Pantalla de inicio -----------------
def pantalla_inicio():
    for widget in root.winfo_children():
        widget.destroy()

    titulo = Label(root, text="👩‍💻 CodeLearn Game",
                   font=("Arial", 32, "bold"), fg="#00ff99", bg="#1e1e1e")
    titulo.pack(pady=16)

    subtitulo = Label(root, text="Aprende programación jugando",
                      font=("Arial", 14), fg="white", bg="#1e1e1e")
    subtitulo.pack(pady=2)

    Label(root, text="Nombre del jugador:", font=("Arial", 12), fg="white", bg="#1e1e1e").pack(pady=8)
    nombre_entry = Entry(root, font=("Arial", 12), width=36)
    nombre_entry.pack(pady=4)

    # recordar nombre si ya se ingresó
    nombre_entry.insert(0, jugador_global)

    def comenzar_juego():
        global jugador_global
        jugador = nombre_entry.get().strip()
        if jugador == "":
            tmsg.showwarning("Atención", "Por favor ingresa tu nombre antes de comenzar.")
        else:
            jugador_global = jugador
            pantalla_bienvenida(jugador)

    Button(root, text="Comenzar", font=("Arial", 14, "bold"),
           bg="#00ff99", fg="black", width=16, command=comenzar_juego).pack(pady=18)

    # Mostrar botón de ayuda / instrucciones
    def mostrar_instrucciones():
        tmsg.showinfo("Instrucciones",
                      "Selecciona 'Quiz' para preguntas de opción múltiple.\n"
                      "Selecciona 'Práctica' para ejercicios interactivos de completar código.\n\n"
                      "Usa el control de música en el pie para activar/pausar la ambientación.")
    Button(root, text="¿Cómo funciona?", font=("Arial", 10),
           bg="#333", fg="white", command=mostrar_instrucciones).pack()

    crear_footer(mostrar_musica=True)

# ----------------- Pantalla de bienvenida -----------------
def pantalla_bienvenida(nombre):
    for widget in root.winfo_children():
        widget.destroy()

    Label(root, text=f"¡Hola, {nombre}!",
          font=("Comic Sans MS", 26, "bold"),
          fg="#00ff99", bg="#1e1e1e").pack(pady=20)

    Label(root, text="Prepárate para aprender y jugar",
          font=("Arial", 14, "bold"), fg="white", bg="#1e1e1e").pack(pady=6)

    Label(root, text="[ Modo de práctica y desafíos activos ]",
          font=("Arial", 11, "italic"), fg="gray", bg="#1e1e1e").pack(pady=4)

    Button(root, text="Comenzar ahora ▶",
           font=("Arial", 13, "bold"),
           bg="#00ff99", fg="black", width=22, height=2,
           command=pantalla_lenguajes).pack(pady=36)

# ----------------- Pantalla de selección -----------------
def pantalla_lenguajes():
    for widget in root.winfo_children():
        widget.destroy()

    Label(root, text="🧠 Elige un modo para comenzar",
          font=("Arial", 22, "bold"), fg="#00ff99", bg="#1e1e1e").pack(pady=26)

    # Separar quiz y práctica
    Button(root, text="🐍 Quiz - Preguntas Python", font=("Arial", 14, "bold"),
           bg="#00ff99", fg="black", width=26, height=2,
           command=iniciar_quiz).pack(pady=10)

    Button(root, text="🛠️ Práctica - Completa el código", font=("Arial", 14, "bold"),
           bg="#00ff99", fg="black", width=26, height=2,
           command=iniciar_practica).pack(pady=10)

    Button(root, text="⬅ Volver", font=("Arial", 12, "bold"),
           bg="#555", fg="white", width=14,
           command=pantalla_inicio).pack(pady=28)

# ----------------- Quiz (Preguntas) -----------------
def iniciar_quiz():
    global indice_pregunta, puntaje
    indice_pregunta = 0
    puntaje = 0
    random.shuffle(preguntas_python)  # mezclar preguntas
    mostrar_pregunta()

def mostrar_pregunta():
    global indice_pregunta
    for widget in root.winfo_children():
        widget.destroy()

    pregunta = preguntas_python[indice_pregunta]

    Label(root, text=f"Pregunta {indice_pregunta + 1}/{len(preguntas_python)}",
          font=("Arial", 14), fg="#00ff99", bg="#1e1e1e").pack(pady=8)

    Label(root, text=pregunta["pregunta"], font=("Arial", 18, "bold"),
          fg="white", bg="#1e1e1e", wraplength=760, justify=CENTER).pack(pady=16)

    opciones = pregunta["opciones"][:]
    random.shuffle(opciones)
    for opcion in opciones:
        Button(root, text=opcion, font=("Arial", 14, "bold"), width=36,
               bg="#222", fg="white",
               command=lambda o=opcion: verificar_respuesta(o)).pack(pady=8)

    Button(root, text="⟲ Mezclar preguntas", font=("Arial", 10),
           bg="#333", fg="white", command=lambda: (random.shuffle(preguntas_python), reiniciar_quiz())).pack(pady=12)
    Button(root, text="⬅ Volver", font=("Arial", 12, "bold"),
           bg="#555", fg="white", width=12,
           command=pantalla_lenguajes).pack(pady=8)
    crear_footer(mostrar_musica=True)

def reiniciar_quiz():
    global indice_pregunta, puntaje
    indice_pregunta = 0
    puntaje = 0
    mostrar_pregunta()

def verificar_respuesta(opcion_elegida):
    global indice_pregunta, puntaje
    correcta = preguntas_python[indice_pregunta]["respuesta"]

    if opcion_elegida == correcta:
        puntaje += 1
        play_sound_effect(SOUND_CORRECT)
        tmsg.showinfo("✅ Correcto", "¡Bien hecho!")
    else:
        play_sound_effect(SOUND_INCORRECT)
        tmsg.showerror("❌ Incorrecto", f"La respuesta correcta era: {correcta}")

    indice_pregunta += 1
    if indice_pregunta < len(preguntas_python):
        mostrar_pregunta()
    else:
        mostrar_resultado()

# ----------------- Práctica (completar) -----------------
def iniciar_practica():
    global indice_practica
    indice_practica = 0
    random.shuffle(practica_python)
    mostrar_practica()

def mostrar_practica():
    global indice_practica
    for widget in root.winfo_children():
        widget.destroy()

    ejercicio = practica_python[indice_practica]

    Label(root, text=f"Práctica {indice_practica + 1}/{len(practica_python)}",
          font=("Arial", 14), fg="#00ff99", bg="#1e1e1e").pack(pady=8)

    txt_frame = Frame(root, bg="#1e1e1e")
    txt_frame.pack(pady=8)

    Label(txt_frame, text=ejercicio["enunciado"],
          font=("Consolas", 14), fg="white", bg="#1e1e1e", justify=LEFT, wraplength=800).pack(pady=6)

    Label(root, text="Tu respuesta:", font=("Arial", 12), fg="white", bg="#1e1e1e").pack(pady=(10,2))
    respuesta_entry = Entry(root, font=("Arial", 14), width=40)
    respuesta_entry.pack(pady=4)

    def mostrar_pista():
        tmsg.showinfo("Pista", ejercicio.get("pista", "Sin pista disponible."))

    def chequear_respuesta():
        user = respuesta_entry.get().strip()
        solucion = practica_python[indice_practica]["solucion"].strip()
        # comparar de forma sencilla (ignorar mayúsc/minúsc y espacios)
        if user.lower().strip() == solucion.lower().strip():
            play_sound_effect(SOUND_CORRECT)
            tmsg.showinfo("✅ Correcto", "Respuesta correcta. ¡Buen trabajo!")
            siguiente_practica()
        else:
            play_sound_effect(SOUND_INCORRECT)
            tmsg.showerror("❌ Incorrecto", f"Respuesta incorrecta.\nPista: pulsa 'Pista' para ayuda.")

    Button(root, text="Comprobar", font=("Arial", 12, "bold"),
           bg="#00ff99", fg="black", width=14, command=chequear_respuesta).pack(pady=10)
    Button(root, text="Pista", font=("Arial", 10), bg="#333", fg="white", command=mostrar_pista).pack()
    nav_frame = Frame(root, bg="#1e1e1e")
    nav_frame.pack(pady=14)
    Button(nav_frame, text="⬅ Anterior", font=("Arial", 10), bg="#555", fg="white",
           command=anterior_practica).pack(side=LEFT, padx=8)
    Button(nav_frame, text="Siguiente ➜", font=("Arial", 10), bg="#555", fg="white",
           command=siguiente_practica).pack(side=LEFT, padx=8)
    Button(root, text="⬅ Volver", font=("Arial", 12, "bold"),
           bg="#444", fg="white", width=12,
           command=pantalla_lenguajes).pack(pady=8)

    crear_footer(mostrar_musica=True)

def siguiente_practica():
    global indice_practica
    indice_practica += 1
    if indice_practica >= len(practica_python):
        indice_practica = 0
        tmsg.showinfo("¡Buen trabajo!", "Has completado los ejercicios. Volviendo al inicio de prácticas.")
    mostrar_practica()

def anterior_practica():
    global indice_practica
    indice_practica -= 1
    if indice_practica < 0:
        indice_practica = len(practica_python) - 1
    mostrar_practica()

# ----------------- Resultado final -----------------
def mostrar_resultado():
    for widget in root.winfo_children():
        widget.destroy()

    Label(root, text=f"🏁 ¡Juego terminado, {jugador_global}!",
          font=("Arial", 24, "bold"), fg="#00ff99", bg="#1e1e1e").pack(pady=24)

    Label(root, text=f"Puntaje final: {puntaje}/{len(preguntas_python)}",
          font=("Arial", 18), fg="white", bg="#1e1e1e").pack(pady=8)

    Button(root, text="↩ Volver al inicio",
           font=("Arial", 14, "bold"),
           bg="#555", fg="white", width=18,
           command=pantalla_inicio).pack(pady=18)

    crear_footer(mostrar_musica=True)

# ----------------- Ejecutar pantalla inicial -----------------
pantalla_inicio()

# Si pygame está disponible, empezamos la música automáticamente (opcional)
if PYGAME_AVAILABLE and os.path.exists(MUSIC_FILE):
    try:
        play_music(loop=True)
    except:
        pass

root.mainloop()