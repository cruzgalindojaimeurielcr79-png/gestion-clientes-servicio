import datetime
import logging
from abc import ABC, abstractmethod
from typing import List, Optional, Union

# =====================================================================
# CONFIGURACIÓN DEL SISTEMA DE LOGS (Archivo de registro de eventos)
# =====================================================================
logging.basicConfig(
    filename="software_fj_sistema.log",
    level=logging.INFO,
    format="%(asctime)s - [%(levelname)s] - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    encoding="utf-8"
)

# =====================================================================
# EXCEPCIONES PERSONALIZADAS (Jerarquía de Errores)
# =====================================================================
class SoftwareFJException(Exception):
    """Excepción base para el sistema Software FJ."""
    pass

class ValidationError(SoftwareFJException):
    """Se lanza cuando los datos de entrada no cumplen las validaciones."""
    pass

class ServiceUnavailableError(SoftwareFJException):
    """Se lanza cuando un servicio no está disponible o no tiene capacidad."""
    pass

class InvalidOperationError(SoftwareFJException):
    """Se lanza al intentar realizar acciones no permitidas en el estado actual."""
    pass

# =====================================================================
# ARQUITECTURA DE CLASES (POO, Abstracción y Encapsulación)
# =====================================================================

class EntidadSistema(ABC):
    """Clase abstracta que representa entidades generales con identificación única."""
    def __init__(self, id_entidad: str):
        if not id_entidad or not id_entidad.strip():
            raise ValidationError("El ID de la entidad no puede estar vacío.")
        self._id_entidad = id_entidad.strip()

    @property
    def id_entidad(self) -> str:
        return self._id_entidad

    @abstractmethod
    def obtener_detalles(self) -> str:
        """Sobreescrito por clases derivadas para mostrar su información."""
        pass


class Cliente(EntidadSistema):
    """Clase que encapsula los datos personales y validaciones del cliente."""
    def __init__(self, id_cliente: str, nombre: str, email: str, telefono: str):
        super().__init__(id_cliente)
        
        if not nombre or len(nombre.strip()) < 3:
            raise ValidationError("El nombre debe tener al menos 3 caracteres.")
        if "@" not in email or "." not in email:
            raise ValidationError(f"El correo electrónico '{email}' no es válido.")
        if not telefono.isdigit() or len(telefono) < 7:
            raise ValidationError("El teléfono debe contener solo números y mínimo 7 dígitos.")
            
        self.__nombre = nombre.strip()
        self.__email = email.strip()
        self.__telefono = telefono.strip()

    @property
    def nombre(self) -> str: return self.__nombre

    @property
    def email(self) -> str: return self.__email

    @property
    def telefono(self) -> str: return self.__telefono

    def obtener_detalles(self) -> str:
        return f"Cliente [{self.id_entidad}]: {self.__nombre} | Email: {self.__email} | Tel: {self.__telefono}"


class Servicio(EntidadSistema, ABC):
    """Clase abstracta base para los servicios de Software FJ."""
    def __init__(self, id_servicio: str, nombre_servicio: str, costo_base: float):
        super().__init__(id_servicio)
        if costo_base < 0:
            raise ValidationError("El costo base no puede ser un valor negativo.")
        self._nombre_servicio = nombre_servicio
        self._costo_base = costo_base

    @property
    def nombre_servicio(self) -> str: return self._nombre_servicio

    @property
    def costo_base(self) -> float: return self._costo_base

    @abstractmethod
    def calcular_costo(self, horas_o_dias: int) -> float:
        """Cálculo polimórfico del costo según el tipo de servicio."""
        pass

    def calcular_costo_avanzado(self, duracion: int, descuento: float = 0.0, impuesto: float = 0.19) -> float:
        """Calcula el costo aplicando opcionalmente descuentos e impuestos."""
        if descuento < 0 or descuento > 1:
            raise ValidationError("El descuento debe estar entre 0.0 y 1.0 (0% - 100%).")
        if impuesto < 0:
            raise ValidationError("El impuesto no puede ser negativo.")
        
        costo_neto = self.calcular_costo(duracion)
        costo_con_descuento = costo_neto * (1 - descuento)
        return round(costo_con_descuento * (1 + impuesto), 2)


# =====================================================================
# SERVICIOS ESPECIALIZADOS (Herencia y Polimorfismo)
# =====================================================================

class ReservaSala(Servicio):
    """Servicio de alquiler de salas de juntas o desarrollo."""
    def __init__(self, id_servicio: str, nombre_servicio: str, costo_base: float, capacidad_max: int):
        super().__init__(id_servicio, nombre_servicio, costo_base)
        if capacidad_max <= 0:
            raise ValidationError("La capacidad de la sala debe ser mayor a cero.")
        self.__capacidad_max = capacidad_max

    def calcular_costo(self, horas: int) -> float:
        if horas <= 0:
            raise ValidationError("Las horas de reserva deben ser mayores a cero.")
        return (self._costo_base * horas) + (15.0 * horas)

    def obtener_detalles(self) -> str:
        return f"Servicio Sala [{self.id_entidad}]: {self._nombre_servicio} | Capacidad: {self.__capacidad_max} pers. | Costo Base/Hora: ${self._costo_base}"


class AlquilerEquipo(Servicio):
    """Servicio de alquiler de laptops, servidores o infraestructura local."""
    def __init__(self, id_servicio: str, nombre_servicio: str, costo_base: float, stock_disponible: int):
        super().__init__(id_servicio, nombre_servicio, costo_base)
        if stock_disponible < 0:
            raise ValidationError("El stock inicial no puede ser negativo.")
        self.__stock = stock_disponible

    @property
    def stock(self) -> int: return self.__stock

    def restar_stock(self):
        if self.__stock <= 0:
            raise ServiceUnavailableError(f"No hay equipos disponibles para: {self._nombre_servicio}")
        self.__stock -= 1

    def aumentar_stock(self):
        self.__stock += 1

    def calcular_costo(self, dias: int) -> float:
        if dias <= 0:
            raise ValidationError("Los días de alquiler deben ser mayores a cero.")
        tarifa = self._costo_base * 0.9 if dias > 5 else self._costo_base
        return tarifa * dias

    def obtener_detalles(self) -> str:
        return f"Servicio Equipo [{self.id_entidad}]: {self._nombre_servicio} | Stock: {self.__stock} uds | Costo Base/Día: ${self._costo_base}"


class AsesoriaEspecializada(Servicio):
    """Servicio de consultoría en desarrollo de software y arquitectura cloud."""
    def __init__(self, id_servicio: str, nombre_servicio: str, costo_base: float, consultor: str):
        super().__init__(id_servicio, nombre_servicio, costo_base)
        if not consultor or len(consultor.strip()) < 3:
            raise ValidationError("El nombre del consultor asignado no es válido.")
        self.__consultor = consultor.strip()

    def calcular_costo(self, horas: int) -> float:
        if horas <= 0:
            raise ValidationError("Las horas de asesoría deben ser mayores a cero.")
        return (self._costo_base * horas) + 50.0

    def obtener_detalles(self) -> str:
        return f"Servicio Asesoría [{self.id_entidad}]: {self._nombre_servicio} | Especialista: {self.__consultor} | Tarifa/Hora: ${self._costo_base}"


# =====================================================================
# CLASE RESERVA (Gestión del ciclo de vida y Excepciones)
# =====================================================================

class Reserva(EntidadSistema):
    """Integra Clientes y Servicios controlando estados de reservas."""
    def __init__(self, id_reserva: str, cliente: Cliente, servicio: Servicio, duracion: int):
        super().__init__(id_reserva)
        if not isinstance(cliente, Cliente):
            raise ValidationError("El cliente asignado no es válido.")
        if not isinstance(servicio, Servicio):
            raise ValidationError("El servicio asignado no es válido.")
        
        self.__cliente = cliente
        self.__servicio = servicio
        self.__duracion = duracion
        self.__estado = "PENDIENTE"
        self.__costo_total = 0.0

    @property
    def estado(self) -> str: return self.__estado

    @property
    def costo_total(self) -> float: return self.__costo_total

    def confirmar_reserva(self, descuento: float = 0.0):
        """Confirma la reserva procesando inventarios y calculando costos."""
        try:
            if self.__estado != "PENDIENTE":
                raise InvalidOperationError(f"No se puede confirmar una reserva en estado {self.__estado}.")
            
            if isinstance(self.__servicio, AlquilerEquipo):
                self.__servicio.restar_stock()

            self.__costo_total = self.__servicio.calcular_costo_avanzado(self.__duracion, descuento=descuento)
            self.__estado = "CONFIRMADA"
            
        except SoftwareFJException as e:
            raise InvalidOperationError("Error crítico al procesar la confirmación") from e

    def cancelar_reserva(self):
        """Cancela la reserva y libera recursos si es necesario."""
        if self.__estado == "CANCELADA":
            raise InvalidOperationError("La reserva ya se encuentra cancelada.")
        
        if self.__estado == "CONFIRMADA" and isinstance(self.__servicio, AlquilerEquipo):
            self.__servicio.aumentar_stock()
            
        self.__estado = "CANCELADA"

    def obtener_detalles(self) -> str:
        return (f"Reserva [{self.id_entidad}] | Estado: {self.__estado} | "
                f"Cliente: {self.__cliente.nombre} | Servicio: {self.__servicio.nombre_servicio} | "
