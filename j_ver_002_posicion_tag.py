from src.config.variables import N_SENSORES, posiciones_anchors, DATA_PORT, BAUDRATE, TIEMPO_ESPERA, NUM_CICLOS
from src.utils.lectores.sensor_reader import SensorReader
from src.utils.auxiliares.trilateracion import obtener_posicion_tag_3d
from src.utils.auxiliares.validador import verificar_distancias
from src.utils.auxiliares.uart_mediciones import obtener_distancias_uart
from src.utils.graficadores.graficador_tag import TagPlotter
from time import sleep
import numpy as np
 
 
 
# ###########################################################
# Controlador UART
# ###########################################################
class UARTController:
    def __init__(self, port):
        self.port = port

    def send(self, msg):
        print(f"UART enviado: {msg}")
        # Implementación UART real

 # ###########################################################
# Loop principal inicial
# ###########################################################
def main():

    data_receiver = SensorReader(port=DATA_PORT, baudrate=BAUDRATE)
    uart_controller = UARTController(port=DATA_PORT)

    if not data_receiver.connect():
        print(f"Error: No se pudo conectar al receptor de datos en {DATA_PORT}")
        return

    graficador = TagPlotter()
    
    ciclo = 0
    while True:
        print(f"\nCiclo #{ciclo+1}")
        distancias = obtener_distancias_uart(data_receiver, N_SENSORES)
        valido = verificar_distancias(distancias, uart_controller)
        #print(f"Distancias: {distancias} | Válido: {valido}")

        if valido:
            try:
                anchors = posiciones_anchors[:len(distancias)]
                posicion_tag, radio_error = obtener_posicion_tag_3d(distancias, anchors)
                graficador.actualizar(*posicion_tag, radio_error=radio_error)

                print(f"Posición estimada del tag: X={posicion_tag[0]:.1f}, Y={posicion_tag[1]:.1f}, Z={posicion_tag[2]:.1f}")
                print(f"Error promedio en posición estimada: ±{radio_error:.5f} mm")
            except Exception as e:
                print(f"Error en trilateración: {e}")
                uart_controller.send("STOP")

        if TIEMPO_ESPERA:
            sleep(TIEMPO_ESPERA)

        ciclo += 1
        if NUM_CICLOS is not None and ciclo >= NUM_CICLOS:
            print(f"\nFinalizando ejecución tras {NUM_CICLOS} ciclos.")
            break

if __name__ == "__main__":
    main()
