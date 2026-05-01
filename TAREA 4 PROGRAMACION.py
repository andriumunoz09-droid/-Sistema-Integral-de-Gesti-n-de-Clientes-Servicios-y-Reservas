from abc import ABC, abstractmethod
import logging

# ---------------- LOGS ----------------
logging.basicConfig(
    filename="sistema.log",
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# ---------------- EXCEPCIONES ----------------
class ErrorSistema(Exception):
    pass

class ClienteInvalidoError(ErrorSistema):
    pass

class ServicioNoDisponibleError(ErrorSistema):
    pass

class ReservaError(ErrorSistema):
    pass


# ---------------- CLASE ABSTRACTA ----------------
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
            raise ClienteInvalidoError("Error en validación de cliente") from e

    def mostrar_info(self):
        return f"{self.__nombre} - {self.__correo}"

    @property
    def nombre(self):
        return self.__nombre


# ---------------- SERVICIO ABSTRACTO ----------------
class Servicio(ABC):
    def __init__(self, nombre, tarifa):
        self.nombre = nombre
        self.tarifa = tarifa

    @abstractmethod
    def descripcion(self):
        pass

    # 🔥 Sobrecarga simulada
    def calcular_costo(self, horas, descuento=0, impuesto=0):
        base = horas * self.tarifa
        total = base - (base * descuento) + (base * impuesto)
        return total


# ---------------- SERVICIOS ----------------
class Sala(Servicio):
    def descripcion(self):
        return "Reserva de sala"

class Equipo(Servicio):
    def descripcion(self):
        return "Alquiler de equipos"

class Asesoria(Servicio):
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
            if not isinstance(self.cliente, Cliente):
                raise ReservaError("Cliente inválido")

            if self.horas <= 0:
                raise ReservaError("Horas inválidas")

        except Exception as e:
            logging.error(e)
            raise ReservaError("Error al confirmar reserva") from e

        else:
            costo = self.servicio.calcular_costo(self.horas, impuesto=0.19)
            self.estado = "Confirmada"
            return f"Reserva confirmada - Total: ${costo}"

        finally:
            print("Proceso de confirmación ejecutado")

    def cancelar(self):
        self.estado = "Cancelada"
        return "Reserva cancelada"

    def modificar(self, nuevas_horas):
        try:
            if nuevas_horas <= 0:
                raise ReservaError("Horas inválidas en modificación")

            self.horas = nuevas_horas
            return "Reserva modificada correctamente"

        except Exception as e:
            logging.error(e)
            return "Error al modificar reserva"


# ---------------- SISTEMA ----------------
class Sistema:
    def __init__(self):
        self.clientes = []
        self.reservas = []

    def agregar_cliente(self, cliente):
        try:
            if not isinstance(cliente, Cliente):
                raise ClienteInvalidoError("Objeto no válido")

            self.clientes.append(cliente)

        except Exception as e:
            logging.error(e)

    def crear_reserva(self, cliente, servicio, horas):
        try:
            reserva = Reserva(cliente, servicio, horas)
            resultado = reserva.confirmar()
            self.reservas.append(reserva)
            return resultado

        except Exception as e:
            logging.error(e)
            return "Error en reserva"


# ---------------- SIMULACIÓN (10 OPERACIONES) ----------------
if __name__ == "__main__":
    sistema = Sistema()

    operaciones = [
        lambda: sistema.agregar_cliente(Cliente("Emerson", "correo@gmail.com")),
        lambda: sistema.agregar_cliente(Cliente("", "mal")),  # error
        lambda: sistema.crear_reserva(
            Cliente("Ana", "ana@gmail.com"),
            Sala("Sala VIP", 50000),
            2
        ),
        lambda: sistema.crear_reserva(
            Cliente("Luis", "luis@gmail.com"),
            Equipo("Laptop", 30000),
            -1  # error
        ),
        lambda: sistema.crear_reserva(
            Cliente("Carlos", "carlos@gmail.com"),
            Asesoria("Consultoría", 80000),
            3
        ),
    ]

    # Ejecutar mínimo 10 operaciones
    for i in range(10):
        try:
            resultado = operaciones[i % len(operaciones)]()
            print(f"Operación {i+1}: {resultado}")
        except Exception as e:
            print(f"Operación {i+1}: Error controlado -> {e}")
            