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
    UMBRAL,
    PID_KP, PID_KI, PID_KD, PID_SETPOINT, PID_SALIDA_MIN, PID_SALIDA_MAX,
    VELOCIDADES_ESCALONADAS,
    DISTANCIA_MINIMA_PARADA,
    VELOCIDAD_MAXIMA,
    SENSIBILIDAD_GIRO_DIFERENCIAL, 
    VELOCIDAD_DIFERENCIAL_MAXIMA,
    PID_ALPHA, PID_SALIDA_MAX

)
from src.utils.lectores.sensor_reader import SensorReader
from src.utils.auxiliares.trilateracion import obtener_posicion_tag_3d
from src.utils.auxiliares.kalman_adapter import filtrar_mediciones_kalman
from src.utils.auxiliares.validador import verificar_distancias
from src.utils.auxiliares.validador import debe_corregir
from src.utils.auxiliares.uart_mediciones import obtener_distancias_uart
from src.utils.auxiliares.angulo_direccion import calcular_angulo_entre_tag_y_robot
from src.utils.auxiliares.control_velocidad import calcular_velocidad_escalonada
from src.utils.auxiliares.filtro_media_movil import FiltroMediaMovil  #<----2
from src.utils.auxiliares.control_diferencial import calcular_velocidades_diferenciales
from src.utils.graficadores.graficador_angulo import graficar_direccion_robot_y_tag
from src.utils.graficadores.graficador_tag import TagPlotter
from src.utils.controladores.pid_controller import PIDController
from src.utils.graficadores.izq_der import graficar_vel_izq_der
from src.utils.controladores.pwm_manager import PWMManager
from src.utils.controladores.pwm_manager import velocidad_a_pwm   
from src.utils.controladores.uart_motor_controller import UARTMotorController
import time
from time import sleep
import numpy as np
import matplotlib.pyplot as plt
plt.ion()  # Modo interactivo activado

def main():
    data_receiver = SensorReader(port=DATA_PORT, baudrate=BAUDRATE)
    motor_controller = UARTMotorController(port=DATA_PORT, baudrate=BAUDRATE)
    pwm_manager = PWMManager(motor_controller)
    filtro_angulo = FiltroMediaMovil(tamaño_ventana=MEDIA_MOVIL_VENTANA)

    if not data_receiver.connect():
        print(f"Error: No se pudo conectar al receptor de datos en {DATA_PORT}")
        return
    
    if not motor_controller.connect():
        print(f"Error: No se pudo conectar al controlador de motores en {DATA_PORT}")
        data_receiver.disconnect()
        return

    graficador = TagPlotter()
    pid = PIDController(
        kp=PID_KP,
        ki=PID_KI,
        kd=PID_KD,
        setpoint=PID_SETPOINT,
        alpha=PID_ALPHA,
        salida_maxima=PID_SALIDA_MAX
    )

    ciclo = 0
    tiempos = []
    historico_izq = []
    historico_der = []
    tiempo_inicio = time.time()
    
    while True:
        print(f"\nCiclo #{ciclo+1}")
        distancias = obtener_distancias_uart(data_receiver, N_SENSORES)
        valido = verificar_distancias(distancias, motor_controller)

        if valido:
            try:
                distancias_filtradas = filtrar_mediciones_kalman(distancias)
                anchors = posiciones_anchors[:len(distancias_filtradas)]

                posicion_tag, radio_error = obtener_posicion_tag_3d(distancias_filtradas, anchors)
                #graficador.actualizar(*posicion_tag, radio_error=radio_error)

                # Control de dirección angular
                sensor_1 = anchors[INDICES_SENSORES_ANGULO[0]]
                sensor_2 = anchors[INDICES_SENSORES_ANGULO[1]]
                angulo_raw = calcular_angulo_entre_tag_y_robot(posicion_tag, sensor_1, sensor_2)

                if APLICAR_MEDIA_MOVIL:
                    angulo_relativo = filtro_angulo.filtrar("tag_1", angulo_raw)
                    print(f"Ángulo relativo filtrado (media móvil): {angulo_relativo:.2f}°")
                else:
                    angulo_relativo = angulo_raw
                    print(f"Ángulo relativo sin filtrar: {angulo_relativo:.2f}°")

                if debe_corregir(angulo_relativo, umbral=UMBRAL):
                    correccion = pid.update(angulo_relativo)
                    correccion = np.clip(correccion, PID_SALIDA_MIN, PID_SALIDA_MAX)
                    motor_controller.send_motor_command(int(correccion), int(-correccion))
                else:
                    print(f"Corrección ignorada: ángulo de {angulo_relativo:.2f}° está dentro del umbral")

                #graficar_direccion_robot_y_tag(posicion_tag, sensor_1, sensor_2)

                # Control de velocidad lineal por distancia
                distancia_al_tag = np.linalg.norm(posicion_tag)
                velocidad_avance = calcular_velocidad_escalonada(
                    distancia=distancia_al_tag,
                    distancia_minima=DISTANCIA_MINIMA_PARADA,
                    velocidades_por_metro=VELOCIDADES_ESCALONADAS,
                    velocidad_maxima=VELOCIDAD_MAXIMA
                )

                if velocidad_avance > 0.0:
                    vel_izq, vel_der, giro_normalizado = calcular_velocidades_diferenciales(
                        v_lineal=velocidad_avance,
                        angulo_relativo=angulo_relativo,
                        #sensibilidad_giro=SENSIBILIDAD_GIRO_DIFERENCIAL,
                        max_v=VELOCIDAD_DIFERENCIAL_MAXIMA
                    )
                    ##### PARA DIFERENCIAL #############################
                    #uart_controller.send(f"VEL:{vel_izq},{vel_der}")
                    #tiempos.append(time.time() - tiempo_inicio)
                    #historico_izq.append(vel_izq)
                    #historico_der.append(vel_der)
                    ##### PARA PWM #############################
                    pwm_izq = velocidad_a_pwm(vel_izq)
                    pwm_der = velocidad_a_pwm(vel_der)

                    
                    tiempos.append(time.time() - tiempo_inicio)
                    historico_izq.append(pwm_izq)
                    historico_der.append(pwm_der)
                    pwm_manager.enviar_pwm(pwm_izq, pwm_der)
 
                else:
                    #uart_controller.send("STOP")
                    pwm_manager.enviar_pwm(0, 0)

            except Exception as e:
                print(f"Error en trilateración: {e}")
                pwm_manager.detener()
                #uart_controller.send("STOP")

        if ciclo % 10 == 0 and ciclo > 0:
            graficar_vel_izq_der(tiempos, historico_izq, historico_der)
        
        if TIEMPO_ESPERA:
            sleep(TIEMPO_ESPERA)

        ciclo += 1
        if NUM_CICLOS is not None and ciclo >= NUM_CICLOS:
            print(f"\nFinalizando ejecución tras {NUM_CICLOS} ciclos.")
            break
    
    # Desconectar controladores
    data_receiver.disconnect()
    motor_controller.disconnect()

if __name__ == "__main__":
    main()
    import matplotlib.pyplot as plt
    plt.ioff()
    plt.show()