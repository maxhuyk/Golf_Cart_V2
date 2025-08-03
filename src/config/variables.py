import numpy as np
from src.utils.auxiliares.mi_kalman import KalmanFilter

# #################################################################
# NÚMERO DE CICLOS
# #################################################################
NUM_CICLOS = 350

# #################################################################
# TIEMPO DE ESPERA
# #################################################################
TIEMPO_ESPERA = 0.1

# #################################################################
# COMUNICACIÓN UART
# #################################################################
DATA_PORT = '/dev/ttyAMA0'
BAUDRATE = 500000


# #################################################################
# CONFIGURACIÓN DE SENSORES
# #################################################################
N_SENSORES = 3

SENSOR_POSICIONES = [(280, 0, 0), (-280, 0, 0), (0, 200, 500)]

# #################################################################
# POSICIÓN DE REFERENCIA (anchors)
# #################################################################
posiciones_anchors = np.array([
    [0, 0, 0],
    [500, 0, 0],
    [0, 500, 0],
    [0, 0, 1000]
])

# #################################################################
# PARÁMETROS KALMAN
# #################################################################
# Parámetros del filtro Kalman
KALMAN_Q = 0.02
KALMAN_R = 0.2
KALMAN_ESTIMADO_INICIAL = 0.0
kalman_sensores = [
    KalmanFilter(q=KALMAN_Q, r=KALMAN_R, initial_estimate=KALMAN_ESTIMADO_INICIAL)
    for _ in range(N_SENSORES)
]

# Debugging
DEBUG_UART = True
DEBUG_TRILATERACION = False

# #################################################################
# CÁLCULO DE ÁNGULO ENTRE ROBOT Y TAG
# #################################################################
# Índices dentro de posiciones_anchors que representan la orientación del robot
INDICES_SENSORES_ANGULO = (0, 1)

# #################################################################
# FILTRO DE MEDIA ACUMULADA
# #################################################################
# Número máximo de muestras consideradas en la media móvil
MEDIA_MOVIL_VENTANA = 5

# Aplicar filtrado por media móvil antes de Kalman (True/False)
APLICAR_MEDIA_MOVIL = True


# #################################################################
# UMBRAL A PARTIR DEL CUAL SE CORRIGE
# #################################################################
UMBRAL = 1

# #################################################################
# PARÁMETROS DEL CONTROLADOR PID
# #################################################################
PID_KP = 1.2
PID_KI = 0.2
PID_KD = 0.1
PID_SETPOINT = 0.0  # Generalmente 0 si se desea mantener alineación

# Límites para la corrección de giro
PID_SALIDA_MIN = -30.0
PID_SALIDA_MAX = 30.0

"""
Ejemplo práctico
Supongamos que el ángulo es 5°:
- debe_corregir(5.0) devuelve True, porque está fuera del umbral de ±1.0. <--------UMBRAL
- Se calcula la corrección con PID: da correccion = 47.3.
- np.clip(correccion, -30, 30) lo reduce a 30.0, evitando una acción excesiva. <-------PID
- Se envía TURN:30.00 por UART.
Ahora si el ángulo fuera 0.5°:
- debe_corregir(0.5) devuelve False, entonces no se aplica PID ni corrección.

"""

# Parámetros de suavizado para el PID
PID_ALPHA = 0.3            # Factor de suavizado exponencial del error (entre 0 y 1) ---> Con valor 1 no se aplica
PID_SALIDA_MAX = 30.0      # Límite máximo de corrección PID (saturación) ----> Con valor None no se aplica


# #################################################################
# CONTROL DE VELOCIDAD LINEAL
# #################################################################
# #################################################################
# ESCALONAMIENTO DE VELOCIDAD LINEAL
# #################################################################
VELOCIDADES_ESCALONADAS = {
    1: 20.0,   # Si la distancia está entre 0.5 m y 1 m
    2: 40.0,   # Entre 1 m y 2 m
    3: 60.0,   # Entre 2 m y 3 m
    4: 80.0,   # Entre 3 m y 4 m
    5: 100.0   # Entre 4 m y 5 m
}
DISTANCIA_MINIMA_PARADA = 1
VELOCIDAD_MAXIMA = 100.0  # A partir de 5 m

# #################################################################
# CONTROL DIFERENCIAL POR ÁNGULO
# #################################################################
SENSIBILIDAD_GIRO_DIFERENCIAL = 30.0   # Ángulo máximo considerado para curvatura
VELOCIDAD_DIFERENCIAL_MAXIMA = 255     # PWM máximo por rueda
