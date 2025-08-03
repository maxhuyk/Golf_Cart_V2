import numpy as np
from scipy.optimize import minimize
from src.utils.auxiliares.error_metricas import calcular_error_promedio
from src.utils.auxiliares.filtro_media_movil import FiltroMediaMovil
"""
def obtener_posicion_tag_3d(distancias, posiciones_anchors):
    def funcion_objetivo(pos):
        return sum((np.linalg.norm(pos - anchor) - d)**2 for d, anchor in zip(distancias, posiciones_anchors))

    resultado = minimize(funcion_objetivo, x0=np.array([0, 0, 0]), method='L-BFGS-B')
    posicion_estimada = resultado.x
    margen_error = calcular_error_promedio(posicion_estimada, distancias, posiciones_anchors)
    return posicion_estimada, margen_error
"""
filtro_medidas = FiltroMediaMovil(tamaño_ventana=5)

def obtener_posicion_tag_3d(distancias_crudas, posiciones_anchors, id_tag='default'):
    # Filtrar distancias
    distancias_filtradas = [
        filtro_medidas.filtrar(f"{id_tag}_{i}", d)
        for i, d in enumerate(distancias_crudas)
    ]

    def funcion_objetivo(pos):
        return sum(
            (np.linalg.norm(pos - anchor) - d_filt)**2
            for d_filt, anchor in zip(distancias_filtradas, posiciones_anchors)
        )

    resultado = minimize(funcion_objetivo, x0=np.array([0, 0, 0]), method='L-BFGS-B')
    posicion_estimada = resultado.x
    margen_error = calcular_error_promedio(posicion_estimada, distancias_filtradas, posiciones_anchors)
    return posicion_estimada, margen_error