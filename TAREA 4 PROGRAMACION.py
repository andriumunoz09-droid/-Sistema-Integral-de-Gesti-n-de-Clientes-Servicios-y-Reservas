from abc import ABC, abstractmethod
import logging
import tkinter as tk
from tkinter import ttk, messagebox

# ---------------- LOGS ----------------
logging.basicConfig(
    filename="sistema.log",
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# ---------------- EXCEPCIONES ----------------
class ErrorSistema(Exception):
    pass

class ClienteError(ErrorSistema):
    pass

class ServicioError(ErrorSistema):
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
                raise ClienteError("Nombre vacío")
            if "@" not in self.__correo:
                raise ClienteError("Correo inválido")
        except Exception as e:
            logging.error(e)
            raise ClienteError("Error validando cliente") from e

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

    # 🔥 Sobrecarga
    def calcular_costo(self, horas, descuento=0, impuesto=0):
        base = horas * self.tarifa
        return base - (base * descuento) + (base * impuesto)


class Sala(Servicio):
    def descripcion(self):
        return "Sala"


class Equipo(Servicio):
    def descripcion(self):
        return "Equipo"


class Asesoria(Servicio):
    def descripcion(self):
        return "Asesoría"


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

        except Exception as e:
            logging.error(e)
            raise ReservaError("Error al confirmar") from e

        else:
            total = self.servicio.calcular_costo(self.horas, impuesto=0.19)
            self.estado = "Confirmada"
            return total

        finally:
            print("Intento de confirmación ejecutado")

    def cancelar(self):
        self.estado = "Cancelada"

    def modificar(self, nuevas_horas):
        if nuevas_horas <= 0:
            raise ReservaError("Horas inválidas")
        self.horas = nuevas_horas


# ---------------- SISTEMA ----------------
class Sistema:
    def __init__(self):
        self.clientes = []
        self.reservas = []

    def agregar_cliente(self, nombre, correo):
        cliente = Cliente(nombre, correo)
        self.clientes.append(cliente)
        return cliente

    def crear_reserva(self, index_cliente, tipo_servicio, horas):
        cliente = self.clientes[index_cliente]

        if tipo_servicio == "Sala":
            servicio = Sala("Sala", 50000)
        elif tipo_servicio == "Equipo":
            servicio = Equipo("Equipo", 30000)
        else:
            servicio = Asesoria("Asesoría", 80000)

        reserva = Reserva(cliente, servicio, horas)
        total = reserva.confirmar()
        self.reservas.append(reserva)

        return reserva, total


# ---------------- INTERFAZ TTK ----------------
class App:
    def __init__(self, root):
        self.sistema = Sistema()
        self.root = root
        self.root.title("Sistema Empresarial")

        self.frame = ttk.Frame(root, padding=15)
        self.frame.grid()

        # -------- CLIENTES --------
        ttk.Label(self.frame, text="Nombre").grid(row=0, column=0)
        self.nombre = ttk.Entry(self.frame)
        self.nombre.grid(row=0, column=1)

        ttk.Label(self.frame, text="Correo").grid(row=1, column=0)
        self.correo = ttk.Entry(self.frame)
        self.correo.grid(row=1, column=1)

        ttk.Button(self.frame, text="Agregar Cliente", command=self.agregar_cliente).grid(row=2, columnspan=2)

        # -------- RESERVAS --------
        ttk.Label(self.frame, text="Cliente").grid(row=3, column=0)
        self.combo_cliente = ttk.Combobox(self.frame, state="readonly")
        self.combo_cliente.grid(row=3, column=1)

        ttk.Label(self.frame, text="Servicio").grid(row=4, column=0)
        self.combo_servicio = ttk.Combobox(self.frame, values=["Sala", "Equipo", "Asesoria"])
        self.combo_servicio.grid(row=4, column=1)

        ttk.Label(self.frame, text="Horas").grid(row=5, column=0)
        self.horas = ttk.Entry(self.frame)
        self.horas.grid(row=5, column=1)

        ttk.Button(self.frame, text="Crear Reserva", command=self.crear_reserva).grid(row=6, columnspan=2)

        # -------- TABLA --------
        self.tree = ttk.Treeview(self.frame, columns=("Cliente", "Servicio", "Horas", "Estado"), show="headings")
        self.tree.heading("Cliente", text="Cliente")
        self.tree.heading("Servicio", text="Servicio")
        self.tree.heading("Horas", text="Horas")
        self.tree.heading("Estado", text="Estado")
        self.tree.grid(row=7, columnspan=2, pady=10)

    def agregar_cliente(self):
        try:
            cliente = self.sistema.agregar_cliente(self.nombre.get(), self.correo.get())
            messagebox.showinfo("OK", "Cliente agregado")

            self.combo_cliente["values"] = [c.nombre for c in self.sistema.clientes]

        except Exception as e:
            logging.error(e)
            messagebox.showerror("Error", str(e))

    def crear_reserva(self):
        try:
            index = self.combo_cliente.current()
            tipo = self.combo_servicio.get()
            horas = int(self.horas.get())

            reserva, total = self.sistema.crear_reserva(index, tipo, horas)

            self.tree.insert("", "end", values=(
                reserva.cliente.nombre,
                reserva.servicio.descripcion(),
                reserva.horas,
                reserva.estado
            ))

            messagebox.showinfo("Total", f"${total}")

        except Exception as e:
            logging.error(e)
            messagebox.showerror("Error", str(e))


# ---------------- MAIN ----------------
if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
    