import numpy as np

def calcular_angulo_entre_tag_y_robot(pos_tag, sensor_1, sensor_2):
    """
    Calcula el ángulo entre el vector medio de los sensores 1 y 2 y el vector al tag.
    El ángulo se da en grados, positivo si el tag está a la derecha, negativo si está a la izquierda.
    """
    centro_referencia = (np.array(sensor_1) + np.array(sensor_2)) / 2
    frente_robot = np.array(sensor_2) - np.array(sensor_1)
    frente_robot[2] = 0  # ignorar componente Z para ángulo en plano XY
    frente_robot_unitario = frente_robot / np.linalg.norm(frente_robot)

    direccion_tag = np.array(pos_tag) - centro_referencia
    direccion_tag[2] = 0  # ángulo relativo en plano XY
    direccion_tag_unitario = direccion_tag / np.linalg.norm(direccion_tag)

    producto_cruzado = np.cross(frente_robot_unitario, direccion_tag_unitario)
    producto_punto = np.dot(frente_robot_unitario, direccion_tag_unitario)

    angulo_rad = np.arctan2(producto_cruzado[2], producto_punto)
    angulo_grados = np.degrees(angulo_rad)
    return angulo_grados