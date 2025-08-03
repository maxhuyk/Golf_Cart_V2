import matplotlib.pyplot as plt

# Variables globales para mantener estado de la figura
fig = None
ax = None

def graficar_vel_izq_der(tiempos, vel_izq, vel_der):
    global fig, ax
    bar_width = 0.4

    if fig is None or ax is None:
        fig, ax = plt.subplots(figsize=(10, 5))

    ax.cla()  # Limpiar ejes

    ax.bar([t - bar_width/2 for t in tiempos], vel_izq, width=bar_width,
           label="Velocidad Izquierda", color="crimson")
    ax.bar([t + bar_width/2 for t in tiempos], vel_der, width=bar_width,
           label="Velocidad Derecha", color="seagreen")

    ax.set_xlabel("Tiempo (s)")
    ax.set_ylabel("Velocidad")
    ax.set_title("Comparación Velocidad por Rueda")
    ax.legend()
    ax.grid(True)

    fig.canvas.draw()
    fig.canvas.flush_events()
