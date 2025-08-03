import numpy as np

def verificar_distancias(distances, uart_controller):
    if distances is None or len(distances) == 0 or np.any(distances <= 0.0):
        print("Distancias inválidas — Deteniendo motores")
        uart_controller.send("STOP")
        return False
    return True

# El umbral esta por defecto en grados no radianes    
def debe_corregir(angulo, umbral=1.0):
    """
    Evalúa si el ángulo es suficientemente grande para justificar una corrección.
    
    Parámetros:
    - angulo: float, en grados
    - umbral: float, umbral mínimo (ej. 1.0°)
    
    Retorna:
    - bool: True si se debe corregir, False si se ignora
    """
    return abs(angulo) > umbral