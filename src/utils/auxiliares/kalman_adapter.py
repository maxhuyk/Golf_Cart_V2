from src.config.variables import kalman_sensores

def filtrar_mediciones_kalman(distancias):
    return [kf.update(d) for kf, d in zip(kalman_sensores, distancias)]