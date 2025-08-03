import matplotlib.pyplot as plt
import numpy as np

plt.ion()  #  Activar modo interactivo

def graficar_direccion_robot_y_tag(pos_tag, sensor_1, sensor_2):
    """
    Muestra el plano XY con la orientación entre sensores y tag.
    Actualiza la misma figura en cada llamada.
    """
    centro = (np.array(sensor_1) + np.array(sensor_2)) / 2
    frente = np.array(sensor_2) - np.array(sensor_1)
    frente[2] = 0
    frente_unitario = frente / np.linalg.norm(frente)

    direccion = np.array(pos_tag) - centro
    direccion[2] = 0
    direccion_unitario = direccion / np.linalg.norm(direccion)

    plt.clf()  # Limpiar figura anterior
    plt.quiver(*centro[:2], *frente_unitario[:2], color='blue', scale=5, label='Frente robot')
    plt.quiver(*centro[:2], *direccion_unitario[:2], color='red', scale=5, label='Dirección al tag')

    plt.scatter(*sensor_1[:2], color='green', label='Sensor 1')
    plt.scatter(*sensor_2[:2], color='green', label='Sensor 2')
    plt.scatter(*pos_tag[:2], color='orange', label='Tag')

    plt.xlim(-5000, 5000)
    plt.ylim(-5000, 5000)
    plt.grid(True)
    plt.legend()
    plt.title("Ángulo entre robot y dirección al tag")
    plt.xlabel("X [mm]")
    plt.ylabel("Y [mm]")
    plt.tight_layout()
    plt.pause(0.001)  #  No bloquea el flujo, espera brevemente