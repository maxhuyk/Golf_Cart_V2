import numpy as np

def calcular_error_promedio(posicion_estimada, distancias, anchors):
    errores = [
        abs(np.linalg.norm(posicion_estimada - anchor) - d)
        for d, anchor in zip(distancias, anchors)
    ]
    promedio = np.mean(errores)
    #print(f" Error promedio real: {promedio:.5f} mm\n")
    return promedio