def calcular_velocidad_escalonada(distancia, distancia_minima, velocidades_por_metro, velocidad_maxima):
    """
    Devuelve la velocidad basada en niveles de distancia.
    Si está debajo de la distancia mínima → velocidad 0
    Si supera el último escalón → velocidad máxima
    """
    if distancia <= distancia_minima:
        return 0.0

    nivel = int(distancia)  # redondea hacia abajo
    if nivel in velocidades_por_metro:
        return velocidades_por_metro[nivel]
    else:
        return velocidad_maxima