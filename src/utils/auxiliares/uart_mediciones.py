import numpy as np

def obtener_distancias_uart(data_receiver, n_sensores):
    data_array = data_receiver.read_data()
    print(">>>>>>>>: ", data_array)
    if data_array is not None:
        distances = data_receiver.get_distances()
        return distances[:n_sensores]
    return np.zeros(n_sensores, dtype=np.float64)