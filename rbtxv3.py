import tkinter as tk
from tkinter import messagebox, ttk
import pygame
import time
import os
import random
import sys
import math
import wave
import numpy as np
import pyaudio
import tempfile
import atexit
import threading
from PIL import Image, ImageTk

# Configuration
FUENTE_TITULO = ("Comic Sans MS", 24)
FUENTE_SUBTITULO = ("Arial", 16)
FUENTE_BOTON = ("Arial", 18)
COLOR_FONDO = "#E6E6FA"
COLOR_FONDO_BIENVENIDA = "#FFD1DC"
COLOR_BOTON_VOLVER = "#F08080"
COLOR_BOTON_VOLVER_ACTIVO = "#CD5C5C"
COLOR_BOTON_PRINCIPAL = "#3498DB"
COLOR_BOTON_PRINCIPAL_ACTIVO = "#2980B9"

class ResourceManager:
    """Gestiona recursos de audio y pygame de forma segura"""
    def __init__(self):
        self.pyaudio_instance = None
        self.pygame_initialized = False
        
    def get_pyaudio(self):
        if self.pyaudio_instance is None:
            try:
                self.pyaudio_instance = pyaudio.PyAudio()
                atexit.register(self.cleanup_pyaudio)
            except Exception as e:
                messagebox.showerror("Error de Audio", f"No se pudo inicializar PyAudio: {str(e)}")
        return self.pyaudio_instance
    
    def init_pygame(self):
        if not self.pygame_initialized:
            try:
                pygame.init()
                self.pygame_initialized = True
                atexit.register(self.cleanup_pygame)
            except Exception as e:
                messagebox.showerror("Error de Video", f"No se pudo inicializar Pygame: {str(e)}")
    
    def cleanup_pyaudio(self):
        if self.pyaudio_instance:
            try:
                self.pyaudio_instance.terminate()
                self.pyaudio_instance = None
            except:
                pass
    
    def cleanup_pygame(self):
        if self.pygame_initialized:
            try:
                pygame.quit()
                self.pygame_initialized = False
            except:
                pass

class FileManager:
    """Gestiona archivos y rutas de la aplicación"""
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.sounds_dir = os.path.join(self.base_dir, "sounds")
        self.images_dir = os.path.join(self.base_dir, "images")
        self.create_directories()
    
    def create_directories(self):
        os.makedirs(self.sounds_dir, exist_ok=True)
        os.makedirs(self.images_dir, exist_ok=True)
    
    def get_sound_path(self, filename):
        return os.path.join(self.sounds_dir, filename)
    
    def get_image_path(self, filename):
        return os.path.join(self.images_dir, filename)
    
    def sound_exists(self, filename):
        return os.path.exists(self.get_sound_path(filename))
    
    def image_exists(self, filename):
        return os.path.exists(self.get_image_path(filename))

# Instancias globales
resource_manager = ResourceManager()
file_manager = FileManager()

class SemicuadradoButton(tk.Canvas):
    def __init__(self, master=None, text="", bg="#3498DB", fg="white", 
                 active_bg="#2980B9", command=None, width=120, height=120, 
                 corner_radius=30, font=FUENTE_BOTON, **kwargs):
        self.width = width
        self.height = height
        self.corner_radius = corner_radius
        tk.Canvas.__init__(self, master, width=width, height=height, 
                          highlightthickness=0, bd=0, **kwargs)
        self.command = command
        self.bg = bg
        self.active_bg = active_bg
        self.fg = fg
        self.font = font
        
        self.bind("<Button-1>", self._on_press)
        self.bind("<ButtonRelease-1>", self._on_release)
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        
        self.draw_button(text)
        
    def draw_button(self, text):
        self.delete("all")
        self.create_rounded_rectangle(0, 0, self.width, self.height, 
                                    radius=self.corner_radius, 
                                    fill=self.bg, outline=self.bg)
        self.create_text(self.width//2, self.height//2, text=text, 
                        fill=self.fg, font=self.font, justify=tk.CENTER)
    
    def create_rounded_rectangle(self, x1, y1, x2, y2, radius=25, **kwargs):
        points = [x1+radius, y1,
                 x2-radius, y1,
                 x2, y1,
                 x2, y1+radius,
                 x2, y2-radius,
                 x2, y2,
                 x2-radius, y2,
                 x1+radius, y2,
                 x1, y2,
                 x1, y2-radius,
                 x1, y1+radius,
                 x1, y1]
        return self.create_polygon(points, **kwargs, smooth=True)
        
    def _on_press(self, event):
        self.itemconfig(1, fill=self.active_bg)
        
    def _on_release(self, event):
        self.itemconfig(1, fill=self.bg)
        if self.command:
            self.command()
    
    def _on_enter(self, event):
        self.config(cursor="hand2")
    
    def _on_leave(self, event):
        self.config(cursor="")

class AudioPlayer:
    @staticmethod
    def reproducir(audio_data, sample_rate=44100, sample_width=2, channels=1):
        try:
            p = resource_manager.get_pyaudio()
            if p is None:
                return
                
            stream = p.open(
                format=p.get_format_from_width(sample_width),
                channels=channels,
                rate=sample_rate,
                output=True
            )
            stream.write(audio_data)
            stream.stop_stream()
            stream.close()
        except Exception as e:
            messagebox.showerror("Error de Audio", f"No se pudo reproducir: {str(e)}")

class TerapiaAuditiva:
    def __init__(self, root, parent_window=None):
        self.root = root
        self.parent_window = parent_window
        self.root.title("Terapia Auditiva")
        self.root.geometry("1024x600")
        self.root.configure(bg=COLOR_FONDO)
        self.setup_ui()
        self.verificar_archivos()

    def setup_ui(self):
        # Frame principal
        main_frame = tk.Frame(self.root, bg=COLOR_FONDO)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Título
        tk.Label(main_frame, text="Terapia Auditiva", 
                font=FUENTE_TITULO, bg=COLOR_FONDO).pack(pady=40)
        
        # Frame para botones principales
        buttons_frame = tk.Frame(main_frame, bg=COLOR_FONDO)
        buttons_frame.pack(expand=True)
        
        # Botones de terapia
        SemicuadradoButton(buttons_frame, 
            text="Pre-Rehabilitación\n(Ruidos Terapéuticos)", 
            bg="#1ABC9C", active_bg="#16A085",
            width=300, height=120, corner_radius=30,
            command=self.abrir_ruidos_terapeuticos).pack(pady=15)

        SemicuadradoButton(buttons_frame, 
            text="Rehabilitación\n(Sonidos Ambientales)", 
            bg="#3498DB", active_bg="#2980B9",
            width=300, height=120, corner_radius=30,
            command=self.abrir_sonidos_ambientales).pack(pady=15)

        SemicuadradoButton(buttons_frame, 
            text="Pos-Rehabilitación\n(Sonidos de Animales)", 
            bg="#9B59B6", active_bg="#8E44AD",
            width=300, height=120, corner_radius=30,
            command=self.abrir_sonidos_animales).pack(pady=15)
        
        # Frame para botón volver
        bottom_frame = tk.Frame(main_frame, bg=COLOR_FONDO)
        bottom_frame.pack(side=tk.BOTTOM, pady=20)
        
        SemicuadradoButton(bottom_frame, 
            text="← Volver al Menú Principal", 
            bg=COLOR_BOTON_VOLVER, active_bg=COLOR_BOTON_VOLVER_ACTIVO,
            width=250, height=60, corner_radius=20,
            command=self.volver_menu_principal).pack()

    def volver_menu_principal(self):
        """Vuelve al menú principal"""
        self.root.destroy()
        if self.parent_window:
            self.parent_window.deiconify()

    def abrir_ruidos_terapeuticos(self):
        ventana = tk.Toplevel(self.root)
        ventana.title("Ruidos Terapéuticos")
        ventana.geometry("600x500")
        ventana.configure(bg=COLOR_FONDO)
        
        # Frame principal
        main_frame = tk.Frame(ventana, bg=COLOR_FONDO)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Título
        tk.Label(main_frame, text="Ruidos Terapéuticos", 
                font=FUENTE_TITULO, bg=COLOR_FONDO).pack(pady=20)
        
        # Frame para botones de sonidos
        sounds_frame = tk.Frame(main_frame, bg=COLOR_FONDO)
        sounds_frame.pack(expand=True)
        
        # Botones de ruidos
        SemicuadradoButton(sounds_frame, 
            text="Ruido Blanco", 
            bg="#1ABC9C", active_bg="#16A085",
            width=200, height=80, corner_radius=30,
            command=lambda: self.reproducir_sonido_con_pregunta("blanco", ventana)).pack(pady=10)
        
        SemicuadradoButton(sounds_frame, 
            text="Ruido Rosa", 
            bg="#3498DB", active_bg="#2980B9",
            width=200, height=80, corner_radius=30,
            command=lambda: self.reproducir_sonido_con_pregunta("rosa", ventana)).pack(pady=10)
        
        SemicuadradoButton(sounds_frame, 
            text="Ruido Marrón", 
            bg="#9B59B6", active_bg="#8E44AD",
            width=200, height=80, corner_radius=30,
            command=lambda: self.reproducir_sonido_con_pregunta("marrón", ventana)).pack(pady=10)
        
        # Frame para botones de navegación
        nav_frame = tk.Frame(main_frame, bg=COLOR_FONDO)
        nav_frame.pack(side=tk.BOTTOM, pady=20)
        
        SemicuadradoButton(nav_frame, 
            text="← Volver", 
            bg=COLOR_BOTON_VOLVER, active_bg=COLOR_BOTON_VOLVER_ACTIVO,
            width=150, height=60, corner_radius=20,
            command=ventana.destroy).pack()

    def abrir_sonidos_ambientales(self):
        ventana = tk.Toplevel(self.root)
        ventana.title("Sonidos Ambientales")
        ventana.geometry("600x500")
        ventana.configure(bg=COLOR_FONDO)
        
        # Frame principal
        main_frame = tk.Frame(ventana, bg=COLOR_FONDO)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Título
        tk.Label(main_frame, text="Sonidos Ambientales", 
                font=FUENTE_TITULO, bg=COLOR_FONDO).pack(pady=20)
        
        # Frame para botones de sonidos
        sounds_frame = tk.Frame(main_frame, bg=COLOR_FONDO)
        sounds_frame.pack(expand=True)
        
        # Botones de sonidos ambientales
        SemicuadradoButton(sounds_frame, 
            text="Lluvia", 
            bg="#1ABC9C", active_bg="#16A085",
            width=200, height=80, corner_radius=30,
            command=lambda: self.reproducir_sonido_con_pregunta("lluvia", ventana)).pack(pady=10)
        
        SemicuadradoButton(sounds_frame, 
            text="Olas del Mar", 
            bg="#3498DB", active_bg="#2980B9",
            width=200, height=80, corner_radius=30,
            command=lambda: self.reproducir_sonido_con_pregunta("olas", ventana)).pack(pady=10)
        
        SemicuadradoButton(sounds_frame, 
            text="Bosque", 
            bg="#9B59B6", active_bg="#8E44AD",
            width=200, height=80, corner_radius=30,
            command=lambda: self.reproducir_sonido_con_pregunta("bosque", ventana)).pack(pady=10)
        
        # Frame para botones de navegación
        nav_frame = tk.Frame(main_frame, bg=COLOR_FONDO)
        nav_frame.pack(side=tk.BOTTOM, pady=20)
        
        SemicuadradoButton(nav_frame, 
            text="← Volver", 
            bg=COLOR_BOTON_VOLVER, active_bg=COLOR_BOTON_VOLVER_ACTIVO,
            width=150, height=60, corner_radius=20,
            command=ventana.destroy).pack()

    def abrir_sonidos_animales(self):
        ventana = tk.Toplevel(self.root)
        ventana.title("Sonidos de Animales")
        ventana.geometry("600x500")
        ventana.configure(bg=COLOR_FONDO)
        
        # Frame principal
        main_frame = tk.Frame(ventana, bg=COLOR_FONDO)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Título
        tk.Label(main_frame, text="Sonidos de Animales", 
                font=FUENTE_TITULO, bg=COLOR_FONDO).pack(pady=20)
        
        # Frame para botones de sonidos
        sounds_frame = tk.Frame(main_frame, bg=COLOR_FONDO)
        sounds_frame.pack(expand=True)
        
        # Botones de sonidos de animales
        SemicuadradoButton(sounds_frame, 
            text="Perro", 
            bg="#1ABC9C", active_bg="#16A085",
            width=200, height=80, corner_radius=30,
            command=lambda: self.reproducir_sonido_con_pregunta("perro", ventana)).pack(pady=10)
        
        SemicuadradoButton(sounds_frame, 
            text="Gato", 
            bg="#3498DB", active_bg="#2980B9",
            width=200, height=80, corner_radius=30,
            command=lambda: self.reproducir_sonido_con_pregunta("gato", ventana)).pack(pady=10)
        
        SemicuadradoButton(sounds_frame, 
            text="Pájaro", 
            bg="#9B59B6", active_bg="#8E44AD",
            width=200, height=80, corner_radius=30,
            command=lambda: self.reproducir_sonido_con_pregunta("pajaro", ventana)).pack(pady=10)
        
        # Frame para botones de navegación
        nav_frame = tk.Frame(main_frame, bg=COLOR_FONDO)
        nav_frame.pack(side=tk.BOTTOM, pady=20)
        
        SemicuadradoButton(nav_frame, 
            text="← Volver", 
            bg=COLOR_BOTON_VOLVER, active_bg=COLOR_BOTON_VOLVER_ACTIVO,
            width=150, height=60, corner_radius=20,
            command=ventana.destroy).pack()

    def verificar_archivos(self):
        archivos_necesarios = ["perro.wav", "gato.wav", "pajaro.wav", 
                             "lluvia.wav", "olas.wav", "bosque.wav"]
        faltantes = [f for f in archivos_necesarios 
                    if not file_manager.sound_exists(f)]
        
        if faltantes:
            messagebox.showwarning("Archivos faltantes", 
                                 f"Faltan archivos en la carpeta 'sounds':\n"
                                 f"{', '.join(faltantes)}\n\n"
                                 f"Se generarán sonidos alternativos.")

    def generar_ruido(self, tipo, duracion=5, sample_rate=44100):
        samples = int(sample_rate * duracion)
        
        if tipo == "blanco":
            signal = np.random.uniform(-1, 1, samples)
        elif tipo == "rosa":
            # Ruido rosa mejorado
            white = np.random.randn(samples)
            b = np.array([0.049922035, -0.095993537, 0.050612699, -0.004408786])
            a = np.array([1, -2.494956002, 2.017265875, -0.522189400])
            signal = np.convolve(white, b, mode='same')
        else:  # marrón
            # Ruido marrón (browniano)
            white = np.random.randn(samples)
            signal = np.cumsum(white)
        
        # Normalizar
        signal = signal / np.max(np.abs(signal)) * 0.5
        signal = (signal * 32767).astype(np.int16)
        return signal.tobytes()

    def reproducir_ruido(self, tipo):
        try:
            audio_data = self.generar_ruido(tipo)
            AudioPlayer.reproducir(audio_data)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo generar el ruido {tipo}: {str(e)}")

    def reproducir_sonido(self, sonido):
        try:
            archivo = file_manager.get_sound_path(f"{sonido}.wav")
            if not os.path.exists(archivo):
                messagebox.showwarning("Archivo no encontrado", 
                                     f"El archivo {sonido}.wav no existe.\n"
                                     f"Colócalo en la carpeta 'sounds'.")
                return
                
            with wave.open(archivo, 'rb') as wf:
                audio_data = wf.readframes(wf.getnframes())
                AudioPlayer.reproducir(
                    audio_data,
                    sample_rate=wf.getframerate(),
                    sample_width=wf.getsampwidth(),
                    channels=wf.getnchannels()
                )
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo reproducir {sonido}: {str(e)}")

    def reproducir_sonido_con_pregunta(self, sonido, ventana_actual):
        # Reproducir sonido
        if sonido in ["blanco", "rosa", "marrón"]:
            self.reproducir_ruido(sonido)
        else:
            self.reproducir_sonido(sonido)
        
        # Crear ventana de pregunta
        ventana_pregunta = tk.Toplevel(ventana_actual)
        ventana_pregunta.title("¿Qué sonido escuchaste?")
        ventana_pregunta.geometry("600x500")
        ventana_pregunta.configure(bg=COLOR_FONDO)
        
        # Frame principal
        main_frame = tk.Frame(ventana_pregunta, bg=COLOR_FONDO)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Título
        tk.Label(main_frame, text="¿Qué sonido escuchaste?", 
                font=FUENTE_TITULO, bg=COLOR_FONDO).pack(pady=20)
        
        # Determinar opciones y respuesta correcta
        if sonido in ["blanco", "rosa", "marrón"]:
            opciones = ["Ruido Blanco", "Ruido Rosa", "Ruido Marrón"]
            respuesta_correcta = f"Ruido {'Blanco' if sonido == 'blanco' else 'Rosa' if sonido == 'rosa' else 'Marrón'}"
        elif sonido in ["lluvia", "olas", "bosque"]:
            opciones = ["Lluvia", "Olas del mar", "Bosque"]
            respuesta_correcta = "Lluvia" if sonido == "lluvia" else "Olas del mar" if sonido == "olas" else "Bosque"
        else:  # sonidos de animales
            opciones = ["Perro", "Gato", "Pájaro"]
            respuesta_correcta = "Perro" if sonido == "perro" else "Gato" if sonido == "gato" else "Pájaro"
        
        random.shuffle(opciones)
        seleccion = tk.StringVar()
        
        # Frame para opciones
        options_frame = tk.Frame(main_frame, bg=COLOR_FONDO)
        options_frame.pack(expand=True, pady=20)
        
        # Radiobuttons para opciones
        for opcion in opciones:
            tk.Radiobutton(options_frame, text=opcion, variable=seleccion,
                          value=opcion, font=FUENTE_BOTON, bg=COLOR_FONDO,
                          activebackground=COLOR_FONDO).pack(anchor=tk.W, padx=50, pady=10)
        
        def verificar():
            if not seleccion.get():
                messagebox.showwarning("Advertencia", "Por favor selecciona una opción")
                return
            
            if seleccion.get() == respuesta_correcta:
                mensaje = "¡Correcto! Has identificado bien el sonido."
                icon = "info"
            else:
                mensaje = f"Incorrecto. El sonido era: {respuesta_correcta}"
                icon = "warning"
            
            messagebox.showinfo("Resultado", mensaje) if icon == "info" else messagebox.showwarning("Resultado", mensaje)
            ventana_pregunta.destroy()
        
        def repetir_sonido():
            if sonido in ["blanco", "rosa", "marrón"]:
                self.reproducir_ruido(sonido)
            else:
                self.reproducir_sonido(sonido)
        
        # Frame para botones
        buttons_frame = tk.Frame(main_frame, bg=COLOR_FONDO)
        buttons_frame.pack(side=tk.BOTTOM, pady=20)
        
        # Botón repetir
        SemicuadradoButton(buttons_frame, 
            text="🔊 Repetir", 
            bg="#FFA500", active_bg="#FF8C00",
            width=120, height=60, corner_radius=20,
            command=repetir_sonido).pack(side=tk.LEFT, padx=10)
        
        # Botón verificar
        SemicuadradoButton(buttons_frame, 
            text="✓ Verificar", 
            bg="#2ECC71", active_bg="#27AE60",
            width=120, height=60, corner_radius=20,
            command=verificar).pack(side=tk.LEFT, padx=10)
        
        # Botón volver
        SemicuadradoButton(buttons_frame, 
            text="← Volver", 
            bg=COLOR_BOTON_VOLVER, active_bg=COLOR_BOTON_VOLVER_ACTIVO,
            width=120, height=60, corner_radius=20,
            command=ventana_pregunta.destroy).pack(side=tk.LEFT, padx=10)

class TerapiaVisual:
    def __init__(self, root, parent_window=None):
        self.root = root
        self.parent_window = parent_window
        self.root.title("Terapia Visual")
        self.root.geometry("1024x600")
        self.root.configure(bg=COLOR_FONDO)
        self.setup_ui()

    def setup_ui(self):
        # Frame principal
        main_frame = tk.Frame(self.root, bg=COLOR_FONDO)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Título
        tk.Label(main_frame, text="Terapia Visual", 
                font=FUENTE_TITULO, bg=COLOR_FONDO).pack(pady=40)
        
        # Frame para botones principales
        buttons_frame = tk.Frame(main_frame, bg=COLOR_FONDO)
        buttons_frame.pack(expand=True)
        
        # Botones de terapia
        SemicuadradoButton(buttons_frame, 
            text="Pre-Rehabilitación\n(Visualizador)", 
            bg="#1ABC9C", active_bg="#16A085",
            width=300, height=120, corner_radius=30,
            command=self.abrir_pre_rehabilitacion).pack(pady=15)

        SemicuadradoButton(buttons_frame, 
            text="Rehabilitación\n(Círculo Animado)", 
            bg="#3498DB", active_bg="#2980B9",
            width=300, height=120, corner_radius=30,
            command=self.abrir_rehabilitacion).pack(pady=15)

        SemicuadradoButton(buttons_frame, 
            text="Pos-Rehabilitación\n(Juego Visual)", 
            bg="#9B59B6", active_bg="#8E44AD",
            width=300, height=120, corner_radius=30,
            command=self.abrir_pos_rehabilitacion).pack(pady=15)
        
        # Frame para botón volver
        bottom_frame = tk.Frame(main_frame, bg=COLOR_FONDO)
        bottom_frame.pack(side=tk.BOTTOM, pady=20)
        
        SemicuadradoButton(bottom_frame, 
            text="← Volver al Menú Principal", 
            bg=COLOR_BOTON_VOLVER, active_bg=COLOR_BOTON_VOLVER_ACTIVO,
            width=250, height=60, corner_radius=20,
            command=self.volver_menu_principal).pack()

    def volver_menu_principal(self):
        """Vuelve al menú principal"""
        self.root.destroy()
        if self.parent_window:
            self.parent_window.deiconify()

    def abrir_pre_rehabilitacion(self):
        try:
            # Ventana de preparación
            ventana_espera = tk.Toplevel(self.root)
            ventana_espera.title("Pre-Rehabilitación")
            ventana_espera.geometry("500x300")
            ventana_espera.configure(bg=COLOR_FONDO)
            
            # Frame principal
            main_frame = tk.Frame(ventana_espera, bg=COLOR_FONDO)
            main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
            
            tk.Label(main_frame, text="Preparando sesión de relajación...", 
                    font=FUENTE_SUBTITULO, bg=COLOR_FONDO).pack(pady=20)
            
            progress = ttk.Progressbar(main_frame, orient="horizontal", 
                                     length=300, mode="indeterminate")
            progress.pack(pady=20)
            progress.start()
            
            # Botón para cancelar
            SemicuadradoButton(main_frame, 
                text="← Cancelar", 
                bg=COLOR_BOTON_VOLVER, active_bg=COLOR_BOTON_VOLVER_ACTIVO,
                width=150, height=60, corner_radius=20,
                command=ventana_espera.destroy).pack(pady=20)
            
            # Ejecutar pygame en hilo separado
            def ejecutar_pygame():
                try:
                    ventana_espera.destroy()
                    self.run_pygame_viewer()
                except Exception as e:
                    messagebox.showerror("Error", f"Error durante la visualización: {str(e)}")
            
            self.root.after(2000, ejecutar_pygame)
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo iniciar el visualizador: {str(e)}")

    def run_pygame_viewer(self):
        try:
            resource_manager.init_pygame()
            
            WIDTH, HEIGHT = 1024, 600
            screen = pygame.display.set_mode((WIDTH, HEIGHT))
            pygame.display.set_caption("Cascadas y Bosques - Relajación Visual")

            # Cargar imágenes o crear fondos alternativos
            image_files = ["cascada1.jpg", "bosque1.", "cascadabosque.jpg"]
            images = []
            
            for i, img_file in enumerate(image_files):
                try:
                    path = file_manager.get_image_path(img_file)
                    if file_manager.image_exists(img_file):
                        img = pygame.image.load(path)
                        img = pygame.transform.smoothscale(img, (WIDTH, HEIGHT))
                        images.append(img)
                    else:
                        # Crear imagen alternativa
                        colors = [(0, 100, 200), (0, 150, 0), (0, 120, 100)]
                        img = pygame.Surface((WIDTH, HEIGHT))
                        img.fill(colors[i])
                        images.append(img)
                except Exception:
                    # Fallback color
                    colors = [(0, 100, 200), (0, 150, 0), (0, 120, 100)]
                    img = pygame.Surface((WIDTH, HEIGHT))
                    img.fill(colors[i % len(colors)])
                    images.append(img)

            current_image = 0
            last_change = time.time()
            change_interval = 30
            start_time = time.time()
            duration = 90

            clock = pygame.time.Clock()
            running = True

            while running:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                        running = False
                
                # Cambiar imagen cada 30 segundos
                if time.time() - last_change >= change_interval and len(images) > 1:
                    current_image = (current_image + 1) % len(images)
                    last_change = time.time()
                
                screen.blit(images[current_image], (0, 0))
                
                # Mostrar información
                font = pygame.font.SysFont('Arial', 30)
                elapsed = time.time() - start_time
                remaining = max(0, duration - elapsed)
                mins, secs = divmod(int(remaining), 60)
                timer_text = font.render(f"Tiempo: {mins:02d}:{secs:02d}", True, (255, 255, 255))
                screen.blit(timer_text, (20, 20))
                
                if len(images) > 1:
                    img_text = font.render(f"Imagen {current_image + 1}/{len(images)}", True, (255, 255, 255))
                    screen.blit(img_text, (20, 60))
                
                # Instrucciones
                inst_text = font.render("Presiona ESC para salir", True, (255, 255, 255))
                screen.blit(inst_text, (20, HEIGHT - 40))
                
                pygame.display.flip()
                clock.tick(30)
                
                if elapsed >= duration:
                    running = False

            pygame.quit()
            
            self.mostrar_resultado(
                "¡Sesión de relajación completada!\n"
                "Esperamos que hayas disfrutado las imágenes", 
                None, self.root
            )
            
        except Exception as e:
            messagebox.showerror("Error", f"Error durante la visualización: {str(e)}")

    def abrir_rehabilitacion(self):
        self.animacion_circulo()

    def abrir_pos_rehabilitacion(self):
        self.abrir_juego_frutas()

    def animacion_circulo(self):
        ventana_anim = tk.Toplevel(self.root)
        ventana_anim.title("Círculo Animado")
        ventana_anim.geometry("1024x600")
        ventana_anim.configure(bg="black")
        
        # Frame para controles
        controls_frame = tk.Frame(ventana_anim, bg="black")
        controls_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)
        
        # Botón volver (esquina superior izquierda)
        SemicuadradoButton(controls_frame, text="← Volver", 
                          bg=COLOR_BOTON_VOLVER, active_bg=COLOR_BOTON_VOLVER_ACTIVO,
                          width=100, height=50, corner_radius=25,
                          command=ventana_anim.destroy).pack(side=tk.LEFT)
        
        # Label de tiempo (esquina superior derecha)
        label_tiempo = tk.Label(controls_frame, text="01:30", 
                              font=FUENTE_TITULO, bg="black", fg="white")
        label_tiempo.pack(side=tk.RIGHT)
        
        # Canvas para la animación
        canvas = tk.Canvas(ventana_anim, width=1024, height=550, highlightthickness=0, bg="black")
        canvas.pack()
        
        # Configuración del círculo
        radio = 30
        centro_x, centro_y = 512, 275
        amplitud_x, amplitud_y = 400, 200
        
        pos_x, pos_y = centro_x, centro_y
        direccion = "derecha"

        circulo = canvas.create_oval(pos_x-radio, pos_y-radio, pos_x+radio, pos_y+radio, 
                                   fill="blue", outline="white", width=2)
        
        # Colores para el fondo
        colores = ["#FF0000", "#FF7F00", "#FFFF00", "#00FF00", 
                  "#0000FF", "#4B0082", "#9400D3"]
        current_color_idx = 0
        next_color_idx = 1
        blend_factor = 0.0
        color_steps = 100
        
        def get_current_color():
            def hex_to_rgb(hex_color):
                return tuple(int(hex_color[i:i+2], 16) for i in (1, 3, 5))
            
            def rgb_to_hex(rgb):
                return '#%02x%02x%02x' % rgb
            
            rgb1 = hex_to_rgb(colores[current_color_idx])
            rgb2 = hex_to_rgb(colores[next_color_idx])
            new_rgb = tuple(int(rgb1[i] + (rgb2[i] - rgb1[i]) * blend_factor) for i in range(3))
            return rgb_to_hex(new_rgb)
        
        def mover_circulo():
            nonlocal pos_x, pos_y, direccion
            
            if direccion == "derecha":
                pos_x += 15
                if pos_x >= centro_x + amplitud_x:
                    direccion = "abajo"
            elif direccion == "abajo":
                pos_y += 15
                if pos_y >= centro_y + amplitud_y:
                    direccion = "izquierda"
            elif direccion == "izquierda":
                pos_x -= 15
                if pos_x <= centro_x - amplitud_x:
                    direccion = "arriba"
            elif direccion == "arriba":
                pos_y -= 15
                if pos_y <= centro_y - amplitud_y:
                    direccion = "derecha"
            
            canvas.coords(circulo, pos_x-radio, pos_y-radio, pos_x+radio, pos_y+radio)
            if ventana_anim.winfo_exists():
                ventana_anim.after(50, mover_circulo)
        
        def cambiar_fondo():
            nonlocal current_color_idx, next_color_idx, blend_factor
            
            blend_factor += 1.0/color_steps
            
            if blend_factor >= 1.0:
                blend_factor = 0.0
                current_color_idx = next_color_idx
                next_color_idx = (next_color_idx + 1) % len(colores)
            
            try:
                nuevo_color = get_current_color()
                ventana_anim.configure(bg=nuevo_color)
                canvas.configure(bg=nuevo_color)
                controls_frame.configure(bg=nuevo_color)
                label_tiempo.configure(bg=nuevo_color)
                if ventana_anim.winfo_exists():
                    ventana_anim.after(50, cambiar_fondo)
            except:
                pass
        
        # Timer
        tiempo_inicio = time.time()
        
        def actualizar_tiempo():
            try:
                tiempo_transcurrido = time.time() - tiempo_inicio
                tiempo_restante = max(0, 90 - int(tiempo_transcurrido))
                
                minutos = tiempo_restante // 60
                segundos = tiempo_restante % 60
                label_tiempo.config(text=f"{minutos:02d}:{segundos:02d}")
                
                if tiempo_restante <= 0:
                    ventana_anim.destroy()
                    self.mostrar_resultado("¡Tiempo completado!\nEl círculo terminó su recorrido", 
                                         ventana_anim, self.root)
                elif ventana_anim.winfo_exists():
                    ventana_anim.after(1000, actualizar_tiempo)
            except:
                pass
        
        # Iniciar animaciones
        mover_circulo()
        cambiar_fondo()
        actualizar_tiempo()

    def abrir_juego_frutas(self):
        ventana_juego = tk.Toplevel(self.root)
        ventana_juego.title("Encuentra las Manzanas")
        ventana_juego.geometry("1024x600")
        ventana_juego.configure(bg="lightyellow")

        # Frame para controles superiores
        top_frame = tk.Frame(ventana_juego, bg="lightyellow")
        top_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)
        
        # Botón volver
        SemicuadradoButton(top_frame, text="← Volver", 
                          bg=COLOR_BOTON_VOLVER, active_bg=COLOR_BOTON_VOLVER_ACTIVO,
                          width=100, height=50, corner_radius=25,
                          command=ventana_juego.destroy).pack(side=tk.LEFT)
        
        # Instrucciones
        tk.Label(top_frame, text="Observa atentamente y cuenta las manzanas rojas", 
                font=FUENTE_SUBTITULO, bg="lightyellow").pack(side=tk.RIGHT)

        # Canvas para el juego
        canvas = tk.Canvas(ventana_juego, width=1024, height=550, bg="lightyellow")
        canvas.pack()

        # Generar frutas
        total_manzanas = random.randint(3, 7)
        total_mandarinas = random.randint(5, 10)

        # Crear manzanas (rojas)
        for _ in range(total_manzanas):
            x = random.randint(50, 974)
            y = random.randint(50, 500)
            radio = 30
            canvas.create_oval(x - radio, y - radio, x + radio, y + radio, 
                             fill="red", outline="darkred", width=2)

        # Crear mandarinas (naranjas)
        for _ in range(total_mandarinas):
            x = random.randint(50, 974)
            y = random.randint(50, 500)
            radio = 30
            canvas.create_oval(x - radio, y - radio, x + radio, y + radio, 
                             fill="orange", outline="darkorange", width=2)

        def mostrar_pregunta():
            canvas.destroy()
            top_frame.destroy()
            
            # Frame principal para la pregunta
            main_frame = tk.Frame(ventana_juego, bg="lightyellow")
            main_frame.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)
            
            # Título
            tk.Label(main_frame, text="¿Cuántas manzanas rojas viste?", 
                     font=FUENTE_TITULO, bg="lightyellow").pack(pady=20)

            # Frame central para entrada y teclado
            center_frame = tk.Frame(main_frame, bg="lightyellow")
            center_frame.pack(expand=True)
            
            # Campo de entrada
            entrada = tk.Entry(center_frame, font=("Arial", 24), width=5, justify='center', bd=3)
            entrada.pack(pady=20)
            
            # Teclado numérico
            teclado_frame = tk.Frame(center_frame, bg="lightyellow")
            teclado_frame.pack()
            
            teclado_numeros = [
                ['7', '8', '9'],
                ['4', '5', '6'],
                ['1', '2', '3'],
                ['0', '⌫']
            ]
            
            def tecla_presionada(valor):
                if valor == '⌫':
                    current = entrada.get()
                    if current:
                        entrada.delete(len(current)-1, tk.END)
                else:
                    entrada.insert(tk.END, valor)
            
            # Crear botones del teclado
            for i, fila in enumerate(teclado_numeros):
                for j, numero in enumerate(fila):
                    btn = tk.Button(teclado_frame, text=numero, font=("Arial", 16), 
                                  width=4, height=2, bd=3,
                                  command=lambda v=numero: tecla_presionada(v),
                                  bg="#FF6B6B" if numero == '⌫' else "#F7FFF7",
                                  fg="white" if numero == '⌫' else "black")
                    
                    if numero == '0':
                        btn.grid(row=i, column=j, columnspan=2, padx=5, pady=5, sticky="nsew")
                    elif numero == '⌫':
                        btn.grid(row=i, column=j+1, padx=5, pady=5, sticky="nsew")
                    else:
                        btn.grid(row=i, column=j, padx=5, pady=5, sticky="nsew")
            
            # Frame para botones de acción
            bottom_frame = tk.Frame(main_frame, bg="lightyellow")
            bottom_frame.pack(side=tk.BOTTOM, pady=20)
            
            def verificar():
                try:
                    respuesta = int(entrada.get())
                    if respuesta == total_manzanas:
                        resultado = f"¡Excelente vista! Había exactamente {total_manzanas} manzanas."
                        icon = "info"
                    else:
                        resultado = f"Casi lo logras. Había {total_manzanas} manzanas, tú contaste {respuesta}."
                        icon = "warning"
                    
                    ventana_juego.destroy()
                    self.mostrar_resultado(resultado, ventana_juego, self.root)
                except ValueError:
                    messagebox.showwarning("Error", "Por favor escribe un número válido.")
            
            # Botones de acción
            SemicuadradoButton(bottom_frame, text="← Volver", 
                             bg=COLOR_BOTON_VOLVER, active_bg=COLOR_BOTON_VOLVER_ACTIVO,
                             width=120, height=60, corner_radius=30,
                             command=ventana_juego.destroy).pack(side=tk.LEFT, padx=10)
            
            SemicuadradoButton(bottom_frame, text="✓ Verificar", 
                             bg="#2ECC71", active_bg="#27AE60",
                             width=120, height=60, corner_radius=30,
                             command=verificar).pack(side=tk.LEFT, padx=10)

        # Mostrar pregunta después de 20 segundos
        ventana_juego.after(20000, mostrar_pregunta)

    def mostrar_resultado(self, mensaje, ventana_anterior, ventana_padre):
        ventana_resultado = tk.Toplevel()
        ventana_resultado.title("Resultado")
        ventana_resultado.geometry("600x400")
        ventana_resultado.configure(bg="lightblue")

        # Frame principal
        main_frame = tk.Frame(ventana_resultado, bg="lightblue")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Mensaje de resultado
        tk.Label(main_frame, text=mensaje, 
                font=FUENTE_TITULO, bg="lightblue", wraplength=500).pack(expand=True)

        # Frame para botones
        buttons_frame = tk.Frame(main_frame, bg="lightblue")
        buttons_frame.pack(side=tk.BOTTOM, pady=20)

        SemicuadradoButton(buttons_frame, text="Cerrar", 
                         bg="#E74C3C", active_bg="#C0392B",
                         width=150, height=80, corner_radius=40,
                         command=ventana_resultado.destroy).pack(side=tk.LEFT, padx=20)

        SemicuadradoButton(buttons_frame, text="← Volver a\nTerapia Visual", 
                         bg=COLOR_BOTON_PRINCIPAL, active_bg=COLOR_BOTON_PRINCIPAL_ACTIVO,
                         width=150, height=80, corner_radius=40,
                         command=lambda: [ventana_resultado.destroy(), 
                                        ventana_padre.deiconify() if ventana_padre else None]).pack(side=tk.LEFT, padx=20)

class MenuPrincipal:
    def __init__(self, root, parent_window=None):
        self.root = root
        self.parent_window = parent_window
        self.root.title("Sistema de Rehabilitación")
        self.root.geometry("1024x600")
        self.root.configure(bg=COLOR_FONDO)
        self.setup_ui()

    def setup_ui(self):
        # Frame principal
        main_frame = tk.Frame(self.root, bg=COLOR_FONDO)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Título
        tk.Label(main_frame, text="Sistema de Rehabilitación", 
                font=FUENTE_TITULO, bg=COLOR_FONDO).pack(pady=40)
        
        # Frame para botones principales (2x2)
        buttons_frame = tk.Frame(main_frame, bg=COLOR_FONDO)
        buttons_frame.pack(expand=True)
        
        # Primera fila
        row1_frame = tk.Frame(buttons_frame, bg=COLOR_FONDO)
        row1_frame.pack(pady=20)
        
        SemicuadradoButton(row1_frame, 
            text="VISUAL", 
            bg="#FFA07A", active_bg="#FF8C69",
            width=200, height=120, corner_radius=30, 
            command=self.abrir_terapia_visual).pack(side=tk.LEFT, padx=30)
        
        SemicuadradoButton(row1_frame, 
            text="AUDITIVA", 
            bg="#98FB98", active_bg="#90EE90",
            width=200, height=120, corner_radius=30, 
            command=self.abrir_terapia_auditiva).pack(side=tk.LEFT, padx=30)
        
        # Segunda fila
        row2_frame = tk.Frame(buttons_frame, bg=COLOR_FONDO)
        row2_frame.pack(pady=20)
        
        SemicuadradoButton(row2_frame, 
            text="VERBAL", 
            bg="#ADD8E6", active_bg="#87CEEB",
            width=200, height=120, corner_radius=30, 
            command=lambda: messagebox.showinfo("Próximamente", 
                                              "Terapia verbal en desarrollo")).pack(side=tk.LEFT, padx=30)
        
        SemicuadradoButton(row2_frame, 
            text="MOTRIZ", 
            bg="#DDA0DD", active_bg="#EE82EE",
            width=200, height=120, corner_radius=30, 
            command=lambda: messagebox.showinfo("Próximamente", 
                                              "Terapia motriz en desarrollo")).pack(side=tk.LEFT, padx=30)
        
        # Frame para botones de navegación
        nav_frame = tk.Frame(main_frame, bg=COLOR_FONDO)
        nav_frame.pack(side=tk.BOTTOM, pady=20)
        
        # Botón volver (si hay ventana padre)
        if self.parent_window:
            SemicuadradoButton(nav_frame, 
                text="← Volver", 
                bg=COLOR_BOTON_VOLVER, active_bg=COLOR_BOTON_VOLVER_ACTIVO,
                width=120, height=60, corner_radius=20, 
                command=self.volver_ventana_anterior).pack(side=tk.LEFT, padx=10)
        
        # Botón salir
        SemicuadradoButton(nav_frame, 
            text="Salir", 
            bg="#E74C3C", active_bg="#C0392B",
            width=120, height=60, corner_radius=20, 
            command=self.root.quit).pack(side=tk.LEFT, padx=10)

    def volver_ventana_anterior(self):
        """Vuelve a la ventana anterior"""
        self.root.destroy()
        if self.parent_window:
            self.parent_window.deiconify()

    def abrir_terapia_visual(self):
        self.root.withdraw()
        ventana_visual = tk.Toplevel()
        terapia_visual = TerapiaVisual(ventana_visual, self.root)
        ventana_visual.protocol("WM_DELETE_WINDOW", lambda: self.volver_al_menu(ventana_visual))

    def abrir_terapia_auditiva(self):
        self.root.withdraw()
        ventana_auditiva = tk.Toplevel()
        terapia_auditiva = TerapiaAuditiva(ventana_auditiva, self.root)
        ventana_auditiva.protocol("WM_DELETE_WINDOW", lambda: self.volver_al_menu(ventana_auditiva))

    def volver_al_menu(self, ventana):
        ventana.destroy()
        self.root.deiconify()

class Bienvenida:
    def __init__(self, root):
        self.root = root
        self.root.title("Bienvenida - Sistema de Rehabilitación")
        self.root.geometry("1024x600")
        self.root.configure(bg=COLOR_FONDO_BIENVENIDA)
        self.setup_ui()

    def setup_ui(self):
        # Frame principal
        main_frame = tk.Frame(self.root, bg=COLOR_FONDO_BIENVENIDA)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Título principal
        tk.Label(main_frame, text="Bienvenido a tu Rehabilitación", 
                font=("Comic Sans MS", 28), bg=COLOR_FONDO_BIENVENIDA).pack(pady=50)
        
        # Subtítulo
        tk.Label(main_frame, text="Sistema Integral de Terapias", 
                font=FUENTE_SUBTITULO, bg=COLOR_FONDO_BIENVENIDA).pack(pady=10)
        
        # Descripción
        descripcion = ("Este sistema te ayudará en tu proceso de rehabilitación\n"
                      "a través de terapias visuales y auditivas especializadas.")
        tk.Label(main_frame, text=descripcion, 
                font=("Arial", 14), bg=COLOR_FONDO_BIENVENIDA, 
                justify=tk.CENTER).pack(pady=20)
        
        # Frame para botones
        buttons_frame = tk.Frame(main_frame, bg=COLOR_FONDO_BIENVENIDA)
        buttons_frame.pack(expand=True)
        
        # Botón comenzar
        SemicuadradoButton(buttons_frame, 
            text="Comenzar", 
            bg="#3498DB", active_bg="#2980B9",
            width=220, height=100, corner_radius=25, 
            command=self.abrir_menu_principal).pack(pady=30)
        
        # Frame para botón salir
        bottom_frame = tk.Frame(main_frame, bg=COLOR_FONDO_BIENVENIDA)
        bottom_frame.pack(side=tk.BOTTOM, pady=20)
        
        SemicuadradoButton(bottom_frame, 
            text="Salir", 
            bg="#E74C3C", active_bg="#C0392B",
            width=120, height=60, corner_radius=20, 
            command=self.root.quit).pack()

    def abrir_menu_principal(self):
        self.root.withdraw()
        ventana_principal = tk.Toplevel()
        menu_principal = MenuPrincipal(ventana_principal, self.root)
        ventana_principal.protocol("WM_DELETE_WINDOW", lambda: self.volver_a_bienvenida(ventana_principal))

    def volver_a_bienvenida(self, ventana):
        ventana.destroy()
        self.root.deiconify()

def verificar_dependencias():
    """Verifica que todas las dependencias estén instaladas"""
    dependencias = {
        'pyaudio': 'pyaudio',
        'numpy': 'numpy', 
        'pygame': 'pygame',
        'PIL': 'pillow'
    }
    
    faltantes = []
    for modulo, paquete in dependencias.items():
        try:
            __import__(modulo)
        except ImportError:
            faltantes.append(paquete)
    
    if faltantes:
        mensaje = (f"Faltan las siguientes dependencias:\n"
                  f"{', '.join(faltantes)}\n\n"
                  f"Por favor instálalas con:\n"
                  f"pip install {' '.join(faltantes)}")
        messagebox.showerror("Dependencias faltantes", mensaje)
        return False
    
    return True

def main():
    # Verificar dependencias
    if not verificar_dependencias():
        sys.exit(1)
    
    # Crear ventana principal
    root = tk.Tk()
    
    # Configurar el cierre de la aplicación
    def on_closing():
        resource_manager.cleanup_pyaudio()
        resource_manager.cleanup_pygame()
        root.quit()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    # Iniciar aplicación
    app = Bienvenida(root)
    
    try:
        root.mainloop()
    except KeyboardInterrupt:
        print("\nCerrando aplicación...")
    finally:
        resource_manager.cleanup_pyaudio()
        resource_manager.cleanup_pygame()

if __name__ == "__main__":
    main()
