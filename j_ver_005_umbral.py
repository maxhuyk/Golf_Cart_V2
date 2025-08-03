from src.config.variables import (
    N_SENSORES,
    posiciones_anchors,
    DATA_PORT,
    BAUDRATE,
    TIEMPO_ESPERA,
    NUM_CICLOS,
    INDICES_SENSORES_ANGULO,
    MEDIA_MOVIL_VENTANA, 
    APLICAR_MEDIA_MOVIL,
    UMBRAL
)
from src.utils.lectores.sensor_reader import SensorReader
from src.utils.auxiliares.trilateracion import obtener_posicion_tag_3d
from src.utils.auxiliares.kalman_adapter import filtrar_mediciones_kalman
from src.utils.auxiliares.validador import verificar_distancias
from src.utils.auxiliares.validador import debe_corregir
from src.utils.auxiliares.uart_mediciones import obtener_distancias_uart
from src.utils.auxiliares.angulo_direccion import calcular_angulo_entre_tag_y_robot
from src.utils.auxiliares.filtro_media_movil import FiltroMediaMovil  #<----2
from src.utils.graficadores.graficador_angulo import graficar_direccion_robot_y_tag
from src.utils.graficadores.graficador_tag import TagPlotter
from time import sleep
import numpy as np

class UARTController:
    def __init__(self, port):
        self.port = port

    def send(self, msg):
        print(f"UART enviado: {msg}")

def main():

    data_receiver = SensorReader(port=DATA_PORT, baudrate=BAUDRATE)
    uart_controller = UARTController(port=DATA_PORT)
    filtro_angulo = FiltroMediaMovil(tamaño_ventana=MEDIA_MOVIL_VENTANA)  #<----2
    if not data_receiver.connect():
        print(f"Error: No se pudo conectar al receptor de datos en {DATA_PORT}")
        return

    graficador = TagPlotter()

    ciclo = 0
    while True:
        print(f"\nCiclo #{ciclo+1}")
        distancias = obtener_distancias_uart(data_receiver, N_SENSORES)
        valido = verificar_distancias(distancias, uart_controller)

        if valido:
            try:
                distancias_filtradas = filtrar_mediciones_kalman(distancias)
                anchors = posiciones_anchors[:len(distancias_filtradas)]

                posicion_tag, radio_error = obtener_posicion_tag_3d(distancias_filtradas, anchors)
                graficador.actualizar(*posicion_tag, radio_error=radio_error)

                print(f"Posición estimada del tag: X={posicion_tag[0]:.1f}, Y={posicion_tag[1]:.1f}, Z={posicion_tag[2]:.1f}")
                print(f"Error promedio en posición estimada: ±{radio_error:.5f} mm")

                sensor_1 = anchors[INDICES_SENSORES_ANGULO[0]]
                sensor_2 = anchors[INDICES_SENSORES_ANGULO[1]]

                angulo_raw = calcular_angulo_entre_tag_y_robot(posicion_tag, sensor_1, sensor_2)

                #>>>>>>>>>>>>>>>>>>>>>>>>
                """
                angulo_relativo = calcular_angulo_entre_tag_y_robot(posicion_tag, sensor_1, sensor_2)
                print(f"Ángulo relativo respecto al frente del robot: {angulo_relativo:.2f}°")
                """
                if APLICAR_MEDIA_MOVIL:
                    angulo_relativo = filtro_angulo.filtrar("tag_1", angulo_raw)
                    print(f"Ángulo relativo filtrado (media móvil): {angulo_relativo:.2f}°")
                else:
                    angulo_relativo = angulo_raw
                    print(f"Ángulo relativo sin filtrar: {angulo_relativo:.2f}°")
                #<<<<<<<<<<<<<

                if debe_corregir(angulo_relativo, umbral=UMBRAL):  #<----3
                    uart_controller.send(f"TURN:{angulo_relativo:.2f}")
                else:
                    print(f"Corrección ignorada: ángulo de {angulo_relativo:.2f}° está dentro del umbral")


                graficar_direccion_robot_y_tag(posicion_tag, sensor_1, sensor_2)
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