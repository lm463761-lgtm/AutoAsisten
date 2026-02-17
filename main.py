import customtkinter as ctk
import os
import pyttsx3
import threading
import time
import serial # IMPORTANTE: pip install pyserial

ctk.set_appearance_mode("dark")

class AutoAsistApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Auto Asist Ultra v5.0 - Conexión BT Real")
        self.geometry("460x900")
        self.configure(fg_color=("#F1F5F9", "#020617")) 

        if not os.path.exists("usuarios"): os.makedirs("usuarios")

        # --- VARIABLES DE CONEXIÓN ---
        self.serial_port = None
        self.port_name = "" # Se definirá en el login

        # --- ESTADOS DEL VEHÍCULO ---
        self.esp32_connected = False 
        self.engine_on = False
        self.is_processing = False
        self.clima_on = False
        self.luces_ext = False
        self.luces_int = False
        self.latency = 0 

        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.pack(fill="both", expand=True)
        
        self.show_login()
        
        # Hilo de monitoreo (Ahora monitorea el puerto Serial real)
        threading.Thread(target=self.monitor_conexion_realtime, daemon=True).start()

    # --- GESTIÓN DE BLUETOOTH SERIAL ---
    def conectar_bluetooth(self):
        """Intenta conectar al puerto COM especificado"""
        try:
            if self.port_name:
                self.serial_port = serial.Serial(self.port_name, 115200, timeout=1)
                self.esp32_connected = True
                self.hablar(f"Conectado al puerto {self.port_name}")
                return True
        except Exception as e:
            print(f"Error de conexión: {e}")
            self.esp32_connected = False
            return False

    def enviar_comando(self, char_comando):
        """Envía un caracter al ESP32 vía Bluetooth"""
        if self.serial_port and self.serial_port.is_open:
            try:
                self.serial_port.write(char_comando.encode())
                print(f"Enviado: {char_comando}")
            except:
                self.esp32_connected = False
        else:
            print("No hay conexión para enviar comandos")

    # --- MONITOREO EN TIEMPO REAL ---
    def monitor_conexion_realtime(self):
        while True:
            time.sleep(2)
            # Verificamos si el puerto sigue abierto
            if self.serial_port:
                if self.serial_port.is_open:
                    self.esp32_connected = True
                    self.latency = 15 # Latencia estimada en Bluetooth Serial
                else:
                    self.esp32_connected = False
            else:
                self.esp32_connected = False
            
            self.after(0, self.actualizar_ui_conexion)

    def actualizar_ui_conexion(self):
        if hasattr(self, 'status_btn'):
            if self.esp32_connected:
                color_bg, color_led = "#065f46", "#34d399"
                texto = f"● BT CONECTADO ({self.port_name})"
            else:
                color_bg, color_led = "#7f1d1d", "#f87171"
                texto = "○ DESCONECTADO"

            self.hud_frame.configure(fg_color=color_bg)
            self.status_btn.configure(text=texto, text_color=color_led)

    # --- LOGIN ---
    def show_login(self):
        self.clear_frame()
        # ... (Código visual igual) ...
        header = ctk.CTkFrame(self.container, fg_color="transparent")
        header.pack(fill="x", padx=10, pady=5)
        
        self.btn_tema = ctk.CTkButton(header, text="☀️", width=40, fg_color="transparent", 
                                     text_color=("#0F172A", "#38BDF8"), command=self.toggle_tema)
        self.btn_tema.pack(side="right")
        
        ctk.CTkLabel(self.container, text="AUTO ASIST", font=("Arial Bold", 40), text_color=("#0F172A", "#38BDF8")).pack(pady=(20, 10))
        
        # CAMPO EXTRA: PUERTO COM
        self.com_input = ctk.CTkEntry(self.container, placeholder_text="PUERTO COM (Ej: COM5)", width=320, justify="center")
        self.com_input.pack(pady=5)

        self.user_input = ctk.CTkEntry(self.container, placeholder_text="USUARIO", width=320, justify="center"); self.user_input.pack(pady=10)
        self.pass_input = ctk.CTkEntry(self.container, placeholder_text="CONTRASEÑA", show="*", width=320, justify="center"); self.pass_input.pack(pady=10)

        ctk.CTkButton(self.container, text="INICIAR Y CONECTAR", fg_color="#38BDF8", text_color="#020617", width=320, height=60, font=("Arial Bold", 16), command=self.validar_acceso).pack(pady=20)
        
        # Botones de registro (simplificados para el ejemplo)
        ctk.CTkButton(self.container, text="Registrar unidad", fg_color="transparent", text_color="#38BDF8", command=self.show_register).pack()

    # --- DASHBOARD ---
    def show_home(self, nombre, saludar=False):
        self.clear_frame()
        if saludar: self.hablar(f"Bienvenido {nombre}")

        # HUD
        self.hud_frame = ctk.CTkFrame(self.container, fg_color="#7f1d1d", height=50, corner_radius=0)
        self.hud_frame.pack(fill="x")
        
        self.status_btn = ctk.CTkButton(self.hud_frame, text="ESPERANDO...", font=("Arial Bold", 11), fg_color="transparent", command=self.conectar_bluetooth)
        self.status_btn.pack(side="right", padx=10)
        
        ctk.CTkButton(self.hud_frame, text="SALIR", width=50, fg_color="transparent", command=self.cerrar_sesion).pack(side="left")

        scroll = ctk.CTkScrollableFrame(self.container, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=10)

        # Botón Motor
        ctk.CTkLabel(scroll, text="IGNICIÓN", font=("Arial Bold", 12), text_color="#64748B").pack(pady=(10, 5))
        self.btn_motor = ctk.CTkButton(scroll, text="START\nENGINE", width=140, height=140, corner_radius=70, 
                                      fg_color=("#CBD5E1", "#1E293B"), border_width=5, border_color="#334155", 
                                      font=("Arial Bold", 18), command=self.secuencia_motor); self.btn_motor.pack(pady=10)

        # Accesos (Modificado con comandos reales)
        ctk.CTkLabel(scroll, text="ACCESOS", font=("Arial Bold", 12), text_color="#64748B").pack(pady=(20, 5))
        sec_frame = ctk.CTkFrame(scroll, fg_color="transparent"); sec_frame.pack()
        btn_st = {"fg_color": ("#E2E8F0", "#1e293b"), "text_color": ("#0F172A", "white"), "border_width": 1}
        
        # BOTONES QUE ENVÍAN COMANDOS: 'S' (Cerrar), 's' (Abrir), 'C' (Cajuela)
        ctk.CTkButton(sec_frame, text="🔒 CERRAR", border_color="#EF4444", width=130, command=lambda: self.ejecutar_accion("Seguros puestos", "S"), **btn_st).grid(row=0, column=0, padx=5, pady=5)
        ctk.CTkButton(sec_frame, text="🔓 ABRIR", border_color="#10B981", width=130, command=lambda: self.ejecutar_accion("Seguros quitados", "s"), **btn_st).grid(row=0, column=1, padx=5, pady=5)
        ctk.CTkButton(sec_frame, text="📦 CAJUELA", border_color="#38BDF8", width=270, command=lambda: self.ejecutar_accion("Abriendo maletero", "C"), **btn_st).grid(row=1, column=0, columnspan=2, pady=5)

        # Clima y Luces
        ctk.CTkLabel(scroll, text="CLIMA Y LUCES", font=("Arial Bold", 12), text_color="#64748B").pack(pady=(20, 5))
        conf_frame = ctk.CTkFrame(scroll, fg_color="transparent"); conf_frame.pack()
        self.btn_lext = ctk.CTkButton(conf_frame, text="🔆 FAROS", width=130, command=self.toggle_luces_ext, **btn_st); self.btn_lext.grid(row=0, column=0, padx=5, pady=5)
        self.btn_lint = ctk.CTkButton(conf_frame, text="💡 INTERIOR", width=130, command=self.toggle_luces_int, **btn_st); self.btn_lint.grid(row=0, column=1, padx=5, pady=5)
        self.btn_clima = ctk.CTkButton(conf_frame, text="❄️ CLIMA: OFF", width=270, command=self.toggle_clima, **btn_st); self.btn_clima.grid(row=1, column=0, columnspan=2, pady=5)

    # --- LÓGICA DE FUNCIONES ---
    def ejecutar_accion(self, msj, comando_bt):
        if not self.esp32_connected: self.hablar("Sin conexión"); return
        self.enviar_comando(comando_bt)
        self.hablar(msj)

    def toggle_luces_ext(self):
        if not self.esp32_connected: self.hablar("Sin conexión"); return
        self.luces_ext = not self.luces_ext
        # Enviar 'F' (On) o 'f' (Off)
        self.enviar_comando('F' if self.luces_ext else 'f')
        self.btn_lext.configure(fg_color="#38BDF8" if self.luces_ext else ("#E2E8F0", "#0F172A"))

    def toggle_luces_int(self):
        if not self.esp32_connected: return
        self.luces_int = not self.luces_int
        # Enviar 'I' (On) o 'i' (Off)
        self.enviar_comando('I' if self.luces_int else 'i')
        self.btn_lint.configure(fg_color="#F59E0B" if self.luces_int else ("#E2E8F0", "#0F172A"))

    def toggle_clima(self):
        if not self.esp32_connected: return
        self.clima_on = not self.clima_on
        # Enviar 'K' (On) o 'k' (Off)
        self.enviar_comando('K' if self.clima_on else 'k')
        self.btn_clima.configure(text="❄️ CLIMA: ACTIVO" if self.clima_on else "❄️ CLIMA: OFF", 
                                fg_color="#2563EB" if self.clima_on else ("#E2E8F0", "#0F172A"))

    def secuencia_motor(self):
        if not self.esp32_connected: self.hablar("Vehículo desconectado"); return
        if self.is_processing: return
        
        self.is_processing = True
        self.hablar("Iniciando motor") if not self.engine_on else self.hablar("Apagando motor")
        
        def proceso():
            time.sleep(1.0)
            self.engine_on = not self.engine_on
            # Enviar 'M' (On) o 'm' (Off)
            self.enviar_comando('M' if self.engine_on else 'm')
            
            self.btn_motor.configure(text="RUNNING" if self.engine_on else "START", fg_color="#DC2626" if self.engine_on else ("#CBD5E1", "#1E293B"))
            self.is_processing = False
        threading.Thread(target=proceso, daemon=True).start()

    def validar_acceso(self):
        u, p = self.user_input.get().strip(), self.pass_input.get().strip()
        puerto = self.com_input.get().strip().upper()
        
        # Sistema de login simple (archivos)
        ruta = f"usuarios/{u}.txt"
        login_exitoso = False
        
        if os.path.exists(ruta) and u != "":
            with open(ruta, "r") as f:
                datos = dict(line.split(": ", 1) for line in f.read().splitlines())
            if p == datos['Pass']: 
                login_exitoso = True

        if login_exitoso:
            self.port_name = puerto # Guardamos el puerto (ej COM5)
            self.conectar_bluetooth() # Intentamos conectar
            self.show_home(u, True)
        else:
            self.hablar("Acceso denegado")

    def cerrar_sesion(self):
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()
        self.show_login()

    # --- REGISTRO Y RECUPERACIÓN (Mantenidos igual para funcionalidad) ---
    def show_register(self):
        self.clear_frame()
        ctk.CTkLabel(self.container, text="REGISTRO", font=("Arial Bold", 25), text_color="#38BDF8").pack(pady=30)
        u = ctk.CTkEntry(self.container, placeholder_text="USUARIO", width=320); u.pack(pady=5)
        p = ctk.CTkEntry(self.container, placeholder_text="PASS", show="*", width=320); p.pack(pady=5)
        pre = ctk.CTkEntry(self.container, placeholder_text="PREGUNTA", width=320); pre.pack(pady=5)
        res = ctk.CTkEntry(self.container, placeholder_text="RESPUESTA", width=320); res.pack(pady=5)
        def registrar():
            if u.get():
                with open(f"usuarios/{u.get()}.txt", "w") as f: f.write(f"Pass: {p.get()}\nPreg: {pre.get()}\nResp: {res.get().lower()}")
                self.show_login()
        ctk.CTkButton(self.container, text="REGISTRAR", fg_color="#10B981", command=registrar).pack(pady=20)
        ctk.CTkButton(self.container, text="VOLVER", command=self.show_login).pack()

    def toggle_tema(self):
        mode = "light" if ctk.get_appearance_mode() == "Dark" else "dark"
        ctk.set_appearance_mode(mode)

    def hablar(self, texto):
        def speaking():
            try:
                engine = pyttsx3.init()
                engine.setProperty('rate', 215); engine.say(texto); engine.runAndWait()
            except: pass
        threading.Thread(target=speaking, daemon=True).start()

    def clear_frame(self):
        for widget in self.container.winfo_children(): widget.destroy()

if __name__ == "__main__":
    app = AutoAsistApp()
    app.mainloop()