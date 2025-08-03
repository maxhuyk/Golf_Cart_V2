# graficador_tag.py
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np

def determinar_color_error(error):
    if error < 50:
        return 'green'      # Excelente precisión
    elif error < 150:
        return 'orange'     # Aceptable
    else:
        return 'red'        # Incierto o mala precisión


class TagPlotter:
    def __init__(self):
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111, projection='3d')
        self.xs, self.ys, self.zs = [], [], []

        self.ax.set_xlabel("X (mm)")
        self.ax.set_ylabel("Y (mm)")
        self.ax.set_zlabel("Z (mm)")
        self.ax.set_title("Variación de posición del tag")
        self.ax.set_xlim(-500, 500)
        self.ax.set_ylim(-500, 500)
        self.ax.set_zlim(0, 1500)

        plt.ion()
        plt.show()

    def actualizar(self, x, y, z, radio_error=100):
        self.xs.append(x)
        self.ys.append(y)
        self.zs.append(z)

        self.ax.clear()
        self.ax.set_xlabel("X (mm)")
        self.ax.set_ylabel("Y (mm)")
        self.ax.set_zlabel("Z (mm)")
        self.ax.set_title("Variación de posición del tag")
        self.ax.set_xlim(x - 600, x + 600)
        self.ax.set_ylim(y - 600, y + 600)
        self.ax.set_zlim(max(0, z - 600), z + 600)


        # Trayectoria histórica
        self.ax.plot(self.xs, self.ys, self.zs, marker='o', color='blue')

        # Determinar color
        color_esfera = determinar_color_error(radio_error)

        # Esfera de error en último punto
        u, v = np.mgrid[0:2*np.pi:20j, 0:np.pi:10j]
        xs = x + radio_error * np.cos(u) * np.sin(v)
        ys = y + radio_error * np.sin(u) * np.sin(v)
        zs = z + radio_error * np.cos(v)
        self.ax.plot_surface(xs, ys, zs, color=color_esfera, alpha=0.6)

        # Mostrar el valor del error cerca del tag (opcional)
        self.ax.text(x, y, z + radio_error + 30,
                 f"±{radio_error:.1f} mm",
                 color=color_esfera, fontsize=9, weight='bold')



        plt.draw()
        plt.pause(0.01)