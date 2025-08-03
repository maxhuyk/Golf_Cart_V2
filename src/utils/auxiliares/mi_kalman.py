class KalmanFilter:
    def __init__(self, q, r, initial_estimate=0.0):
        self.q = q  # Varianza del proceso
        self.r = r  # Varianza del sensor
        self.x_hat = initial_estimate  # Estimación inicial
        self.p = 1.0  # Error de estimación inicial

    def update(self, measurement):
        self.p += self.q  # Predicción
        k = self.p / (self.p + self.r)  # Ganancia Kalman
        self.x_hat += k * (measurement - self.x_hat)  # Corrección
        self.p *= (1 - k)
        return self.x_hat