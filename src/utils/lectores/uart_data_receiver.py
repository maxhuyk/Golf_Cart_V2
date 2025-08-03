#!/usr/bin/env python3
"""
UART Data Receiver Module
Modulo para recibir datos del ESP32 via UART y retornarlos como arrays numpy
Formato de datos: [D1,D2,D3,Vbat,Currmot1,Currmot2]

Author: Sistema UWB Carrito de Golf
Date: July 2025
"""

import serial
import time
import numpy as np
from typing import Optional
from threading import Lock

class UARTDataReceiver:
    """
    Receptor de datos UART que convierte los datos recibidos en arrays numpy
    Parsea formato: [D1,D2,D3,Vbat,Currmot1,Currmot2]
    """
    
    def __init__(self, port: str = '/dev/ttyAMA0', baudrate: int = 2000000, timeout: float = 1.0):
        """
        Inicializar el receptor UART
        
        Args:
            port: Puerto serie (ej: '/dev/ttyAMA0', 'COM3')
            baudrate: Velocidad de comunicación
            timeout: Timeout para lectura de datos
        """
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.serial_conn = None
        self.is_connected = False
        self.lock = Lock()
        
        # Buffer para datos recibidos
        self.buffer = b''
        
        # Último array de datos válido [D1,D2,D3,Vbat,Currmot1,Currmot2]
        self.last_data_array = np.zeros(6, dtype=np.float64)
        self.data_valid = False
        
    def connect(self) -> bool:
        """
        Conectar al puerto serie
        
        Returns:
            bool: True si la conexión fue exitosa
        """
        try:
            self.serial_conn = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=self.timeout,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                bytesize=serial.EIGHTBITS
            )
            
            if self.serial_conn.is_open:
                self.is_connected = True
                print(f"UART conectado a {self.port} @ {self.baudrate} bps")
                return True
            else:
                print(f"Error: No se pudo abrir el puerto {self.port}")
                return False
                
        except Exception as e:
            print(f"Error conectando UART: {e}")
            self.serial_conn = None
            self.is_connected = False
            return False
    
    def disconnect(self):
        """Desconectar del puerto serie"""
        with self.lock:
            if self.serial_conn and self.serial_conn.is_open:
                self.serial_conn.close()
                print("UART desconectado")
            
            self.serial_conn = None
            self.is_connected = False
    
    def read_data(self) -> Optional[np.ndarray]:
        """
        Leer datos desde UART y retornar como array numpy
        
        Returns:
            numpy array con [D1,D2,D3,Vbat,Currmot1,Currmot2] o None si no hay datos válidos
        """
        if not self.is_connected or not self.serial_conn:
            return None
            
        try:
            with self.lock:
                # Leer datos disponibles
                if self.serial_conn.in_waiting > 0:
                    data = self.serial_conn.read(self.serial_conn.in_waiting)
                    self.buffer += data
                    
                    # Procesar buffer para encontrar mensajes completos
                    data_array = self._parse_buffer()
                    if data_array is not None:
                        self.last_data_array = data_array
                        self.data_valid = True
                        return data_array
                        
                # Retornar último dato válido si no hay nuevos datos
                if self.data_valid:
                    return self.last_data_array.copy()
                else:
                    return None
                
        except Exception as e:
            print(f"Error leyendo datos UART: {e}")
            return None
    
    def _parse_buffer(self) -> Optional[np.ndarray]:
        """
        Parsear el buffer para extraer array [D1,D2,D3,Vbat,Currmot1,Currmot2]
        
        Returns:
            numpy array con los 6 valores o None si no hay mensaje completo válido
        """
        try:
            # Buscar inicio y fin de array
            start_marker = b'['
            end_marker = b']'
            
            start_idx = self.buffer.find(start_marker)
            if start_idx == -1:
                return None
                
            end_idx = self.buffer.find(end_marker, start_idx)
            if end_idx == -1:
                return None  # Mensaje incompleto
                
            # Extraer mensaje
            array_data = self.buffer[start_idx:end_idx+1]
            self.buffer = self.buffer[end_idx+1:]  # Remover mensaje procesado
            
            # Parsear array
            array_str = array_data.decode('utf-8')
            # Remover corchetes y dividir por comas
            values_str = array_str.strip('[]').split(',')
            
            if len(values_str) != 6:
                print(f"Error: Se esperaban 6 valores, se recibieron {len(values_str)}")
                return None
            
            # Convertir a float y crear array numpy
            values = [float(v.strip()) for v in values_str]
            return np.array(values, dtype=np.float64)
            
        except Exception as e:
            print(f"Error parseando buffer: {e}")
            # Limpiar buffer en caso de error
            self.buffer = b''
            return None
    
    def get_distances_array(self) -> np.ndarray:
        """
        Obtener distancias UWB como array numpy
        
        Returns:
            numpy array con [D1, D2, D3] en milímetros (convierte automáticamente desde cm)
        """
        if self.data_valid:
            # Convertir de centímetros a milímetros multiplicando por 10
            distances_cm = self.last_data_array[:3].copy()
            distances_mm = distances_cm * 10.0
            return distances_mm
        else:
            return np.zeros(3, dtype=np.float64)
    
    def get_power_data_array(self) -> np.ndarray:
        """
        Obtener datos de alimentación como array numpy
        
        Returns:
            numpy array con [Vbat, Currmot1, Currmot2]
        """
        if self.data_valid:
            return self.last_data_array[3:].copy()
        else:
            return np.zeros(3, dtype=np.float64)
    
    def get_full_data_array(self) -> np.ndarray:
        """
        Obtener todos los datos como array numpy
        
        Returns:
            numpy array con [D1,D2,D3,Vbat,Currmot1,Currmot2]
        """
        if self.data_valid:
            return self.last_data_array.copy()
        else:
            return np.zeros(6, dtype=np.float64)
    
    def get_battery_voltage(self) -> float:
        """
        Obtener voltaje de batería
        
        Returns:
            float: Voltaje de batería en V
        """
        if self.data_valid:
            return float(self.last_data_array[3])
        else:
            return 0.0
    
    def get_motor_currents(self) -> np.ndarray:
        """
        Obtener corrientes de motores
        
        Returns:
            numpy array con [Currmot1, Currmot2]
        """
        if self.data_valid:
            return self.last_data_array[4:6].copy()
        else:
            return np.zeros(2, dtype=np.float64)
    
    def is_data_valid(self) -> bool:
        """
        Verificar si los últimos datos recibidos son válidos
        
        Returns:
            bool: True si los datos son válidos
        """
        return self.data_valid and self.is_connected
    
    def get_connection_status(self) -> dict:
        """
        Obtener estado de la conexión
        
        Returns:
            Dict con información de estado
        """
        return {
            'connected': self.is_connected,
            'port': self.port,
            'baudrate': self.baudrate,
            'data_valid': self.data_valid,
            'last_data': self.last_data_array.tolist() if self.data_valid else None
        }
