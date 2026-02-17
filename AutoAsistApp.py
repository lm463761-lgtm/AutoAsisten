import serial

# Dentro de tu __init__
try:
    # Cambia 'COM4' por el puerto Bluetooth de tu PC
    esp32 = serial.Serial('COM4', 115200) 
    print("Conectado al vehículo")
except:
    print("Error: No se encontró el Bluetooth del auto")

    def enviar_comando(self, comando):
        if self.bt_connected:
            self.bluetooth.write(comando.encode())

    # Modifica tu función toggle_engine
    def toggle_engine(self):
        self.engine_on = not self.engine_on
        self.enviar_comando('S') # Envía la 'S' al ESP32
        
        color = "#1F618D" if self.engine_on else "#4A0000"
        self.btn_star.configure(fg_color=color, text="ON" if self.engine_on else "STAR")