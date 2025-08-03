import numpy as np
import matplotlib.pyplot as plt

# Valores
errores = np.linspace(-10, 10, 100)
umbral = 1.0
Kp = 9.0  # solo proporcional para simplificar
pid_salida = Kp * errores

# Aplicamos umbral
corregir = np.abs(errores) > umbral
pid_salida_filtrada = np.where(corregir, pid_salida, 0)

# Aplicamos límite del PID
pid_clipped = np.clip(pid_salida_filtrada, -30, 30)

# Gráfico
plt.figure(figsize=(10, 6))
plt.plot(errores, pid_salida, label="Salida PID cruda", linestyle="--", color="gray")
plt.plot(errores, pid_salida_filtrada, label="Después de umbral", color="blue")
plt.plot(errores, pid_clipped, label="Después de clip (-30, 30)", color="green")

# Visualizamos el umbral
plt.axvline(-umbral, color="red", linestyle=":", label="Umbral de corrección")
plt.axvline(+umbral, color="red", linestyle=":")

plt.title("Efecto de umbral y límite de PID sobre el ángulo de corrección")
plt.xlabel("Error en grados (ángulo)")
plt.ylabel("Salida del PID")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()