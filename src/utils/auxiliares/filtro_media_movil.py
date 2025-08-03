from collections import deque

class FiltroMediaMovil:
    def __init__(self, tamaño_ventana=5):
        self.ventanas = {}  # Historial por sensor/tag
        self.tamaño = tamaño_ventana

    def filtrar(self, clave, nueva_medicion):
        if clave not in self.ventanas:
            self.ventanas[clave] = deque(maxlen=self.tamaño)
        self.ventanas[clave].append(nueva_medicion)
        return sum(self.ventanas[clave]) / len(self.ventanas[clave])