# src/utils/controladores/pwm_manager.py
import numpy as np

class PWMManager:
    def __init__(self, uart_controller):
        self.uart = uart_controller

    def enviar_pwm(self, canal_izq, canal_der):
        # Convertir PWM (0-255) a velocidad (-150 a 150) como en el definitivo
        vel_izq = int((canal_izq / 255.0) * 150)
        vel_der = int((canal_der / 255.0) * 150)
        
        # Si el uart tiene send_motor_command, usarlo (UARTMotorController)
        if hasattr(self.uart, 'send_motor_command'):
            self.uart.send_motor_command(vel_izq, vel_der)
        else:
            # Si es el UARTController genérico, usar send
            mensaje = f"PWM:{canal_izq},{canal_der}"
            self.uart.send(mensaje)

    def detener(self):
        self.enviar_pwm(0, 0)


def velocidad_a_pwm(v):
    return int(np.clip((v + 1) / 2 * 255, 0, 255))
