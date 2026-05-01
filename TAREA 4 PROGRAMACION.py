from abc import ABC, abstractmethod
import logging

# ---------------- LOGS ----------------
logging.basicConfig(
    filename="sistema.log",
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# ---------------- EXCEPCIONES PERSONALIZADAS ----------------
class ErrorSistema(Exception):
    pass

class ClienteInvalidoError(ErrorSistema):
    pass

class ServicioNoDisponibleError(ErrorSistema):
    pass

class ReservaError(ErrorSistema):
    pass


# ---------------- CLASE ABSTRACTA BASE ----------------
class Entidad(ABC):
    @abstractmethod
    def mostrar_info(self):
        pass


# ---------------- CLIENTE ----------------
class Cliente(Entidad):
    def __init__(self, nombre, correo):
        self.__nombre = nombre
        self.__correo = correo
        self.validar()

    def validar(self):
        try:
            if not self.__nombre.strip():
                raise ClienteInvalidoError("Nombre vacío")
            if "@" not in self.__correo:
                raise ClienteInvalidoError("Correo inválido")
        except Exception as e:
            logging.error(e)
            raise

    def mostrar_info(self):
        return f"Cliente: {self.__nombre} - {self.__correo}"

    # Encapsulación
    @property
    def nombre(self):
        return self.__nombre


# ---------------- SERVICIO ABSTRACTO ----------------
class Servicio(ABC):
    def __init__(self, nombre):
        self.nombre = nombre

    @abstractmethod
    def calcular_costo(self, horas):
        pass

    @abstractmethod
    def descripcion(self):
        pass


# ---------------- SERVICIOS CONCRETOS ----------------
class Sala(Servicio):
    def calcular_costo(self, horas):
        return horas * 50000

    def descripcion(self):
        return "Reserva de sala"

class Equipo(Servicio):
    def calcular_costo(self, horas):
        return horas * 30000

    def descripcion(self):
        return "Alquiler de equipos"

class Asesoria(Servicio):
    def calcular_costo(self, horas):
        return horas * 80000

    def descripcion(self):
        return "Asesoría especializada"


# ---------------- RESERVA ----------------
class Reserva:
    def __init__(self, cliente, servicio, horas):
        self.cliente = cliente
        self.servicio = servicio
        self.horas = horas
        self.estado = "Pendiente"

    def confirmar(self):
        try:
            if self.horas <= 0:
                raise ReservaError("Horas inválidas")

            costo = self.servicio.calcular_costo(self.horas)
            self.estado = "Confirmada"

            return f"Reserva confirmada. Total: ${costo}"

        except Exception as e:
            logging.error(e)
            raise

    def cancelar(self):
        self.estado = "Cancelada"
        return "Reserva cancelada"


# ---------------- SISTEMA ----------------
class Sistema:
    def __init__(self):
        self.clientes = []
        self.reservas = []

    def agregar_cliente(self, cliente):
        try:
            self.clientes.append(cliente)
        except Exception as e:
            logging.error(e)

    def crear_reserva(self, cliente, servicio, horas):
        try:
            reserva = Reserva(cliente, servicio, horas)
            self.reservas.append(reserva)
            return reserva.confirmar()
        except Exception as e:
            logging.error(e)
            return "Error al crear reserva"


# ---------------- PRUEBAS ----------------
if __name__ == "__main__":
    sistema = Sistema()

    try:
        # Cliente válido
        c1 = Cliente("Emerson", "emerson@gmail.com")
        sistema.agregar_cliente(c1)

        # Cliente inválido
        c2 = Cliente("", "malcorreo")
        sistema.agregar_cliente(c2)

    except Exception as e:
        print("Error cliente:", e)

    try:
        servicio = Sala("Sala VIP")
        print(sistema.crear_reserva(c1, servicio, 2))

        # Error en reserva
        print(sistema.crear_reserva(c1, servicio, -1))

    except Exception as e:
        print("Error reserva:", e)
        #1#
        