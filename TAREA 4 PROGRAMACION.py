from abc import ABC, abstractmethod
import logging
import tkinter as tk
from tkinter import ttk, messagebox

# ---------------- LOGS ----------------
logging.basicConfig(
    filename="sistema.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# ---------------- EXCEPCIONES ----------------
class ErrorSistema(Exception):
    pass

class ClienteError(ErrorSistema):
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
            logging.error(f"Error validando cliente: {e}")
            raise ClienteError("Error en validación de cliente") from e

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

    @abstractmethod
    def unidad(self):
        pass

    def calcular_costo(self, cantidad, descuento=0, impuesto=0):
        base = cantidad * self.tarifa
        return base - (base * descuento) + (base * impuesto)


class Sala(Servicio):
    def descripcion(self):
        return "Sala"

    def unidad(self):
        return "Horas"


class Equipo(Servicio):
    def descripcion(self):
        return "Equipo"

    def unidad(self):
        return "Cantidad"


class Asesoria(Servicio):
    def descripcion(self):
        return "Asesoría"

    def unidad(self):
        return "Sesiones"


# ---------------- RESERVA ----------------
class Reserva:
    def __init__(self, cliente, servicio, cantidad):
        self.cliente = cliente
        self.servicio = servicio
        self.cantidad = cantidad
        self.estado = "Pendiente"

    def confirmar(self):
        try:
            if self.cantidad <= 0:
                raise ReservaError("Cantidad inválida")

        except Exception as e:
            logging.error(f"Error en confirmación: {e}")
            raise ReservaError("Error al confirmar reserva") from e

        else:
            total = self.servicio.calcular_costo(self.cantidad, impuesto=0.19)
            self.estado = "Confirmada"
            logging.info(f"Reserva confirmada: {self.cliente.nombre} - {self.servicio.nombre}")
            return total

        finally:
            print("Intento de confirmación ejecutado")

    def cancelar(self):
        self.estado = "Cancelada"
        logging.warning(f"Reserva cancelada: {self.cliente.nombre}")

    def modificar(self, nueva_cantidad):
        try:
            if nueva_cantidad <= 0:
                raise ReservaError("Cantidad inválida")

            self.cantidad = nueva_cantidad
            logging.info(f"Reserva modificada: {self.cliente.nombre} -> {nueva_cantidad}")

        except Exception as e:
            logging.error(f"Error al modificar reserva: {e}")
            raise


# ---------------- SISTEMA ----------------
class Sistema:
    def __init__(self):
        self.clientes = []
        self.reservas = []

    def agregar_cliente(self, nombre, correo):
        try:
            cliente = Cliente(nombre, correo)
            self.clientes.append(cliente)
            logging.info(f"Cliente agregado: {nombre}")
            return cliente
        except Exception as e:
            logging.error(f"Error al agregar cliente: {e}")
            raise

    def crear_reserva(self, index_cliente, tipo_servicio, cantidad):
        try:
            cliente = self.clientes[index_cliente]

            if tipo_servicio == "Sala":
                servicio = Sala("Sala", 50000)
            elif tipo_servicio == "Equipo":
                servicio = Equipo("Equipo", 30000)
            else:
                servicio = Asesoria("Asesoría", 80000)

            reserva = Reserva(cliente, servicio, cantidad)
            total = reserva.confirmar()

            self.reservas.append(reserva)

            logging.info(f"Reserva creada: {cliente.nombre} - {tipo_servicio} - {cantidad}")

            return reserva, total

        except Exception as e:
            logging.error(f"Error al crear reserva: {e}")
            raise


# ---------------- INTERFAZ ----------------
class App:
    def __init__(self, root):
        self.sistema = Sistema()
        self.root = root
        self.root.title("Sistema Empresarial de Reservas")

        self.frame = ttk.Frame(root, padding=15)
        self.frame.grid()

        # CLIENTE
        ttk.Label(self.frame, text="Nombre").grid(row=0, column=0)
        self.nombre = ttk.Entry(self.frame)
        self.nombre.grid(row=0, column=1)

        ttk.Label(self.frame, text="Correo").grid(row=1, column=0)
        self.correo = ttk.Entry(self.frame)
        self.correo.grid(row=1, column=1)

        ttk.Button(self.frame, text="Agregar Cliente", command=self.agregar_cliente).grid(row=2, columnspan=2)

        # RESERVA
        ttk.Label(self.frame, text="Cliente").grid(row=3, column=0)
        self.combo_cliente = ttk.Combobox(self.frame, state="readonly")
        self.combo_cliente.grid(row=3, column=1)

        ttk.Label(self.frame, text="Servicio").grid(row=4, column=0)
        self.combo_servicio = ttk.Combobox(self.frame, values=["Sala", "Equipo", "Asesoria"])
        self.combo_servicio.grid(row=4, column=1)
        self.combo_servicio.bind("<<ComboboxSelected>>", self.actualizar_unidad)

        self.label_unidad = ttk.Label(self.frame, text="Cantidad")
        self.label_unidad.grid(row=5, column=0)

        self.cantidad = ttk.Entry(self.frame)
        self.cantidad.grid(row=5, column=1)

        ttk.Button(self.frame, text="Crear Reserva", command=self.crear_reserva).grid(row=6, columnspan=2)

        ttk.Button(self.frame, text="Modificar", command=self.modificar_reserva).grid(row=7, column=0)
        ttk.Button(self.frame, text="Cancelar", command=self.cancelar_reserva).grid(row=7, column=1)

        # TABLA
        self.tree = ttk.Treeview(self.frame, columns=("Cliente", "Servicio", "Cantidad", "Estado"), show="headings")
        for col in ("Cliente", "Servicio", "Cantidad", "Estado"):
            self.tree.heading(col, text=col)
        self.tree.grid(row=8, columnspan=2, pady=10)

    def actualizar_unidad(self, event):
        tipo = self.combo_servicio.get()

        if tipo == "Sala":
            texto = "Horas"
        elif tipo == "Equipo":
            texto = "Cantidad"
        else:
            texto = "Sesiones"

        self.label_unidad.config(text=texto)

    def agregar_cliente(self):
        try:
            cliente = self.sistema.agregar_cliente(self.nombre.get(), self.correo.get())
            self.combo_cliente["values"] = [c.nombre for c in self.sistema.clientes]
            messagebox.showinfo("OK", "Cliente agregado")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def crear_reserva(self):
        try:
            index = self.combo_cliente.current()
            tipo = self.combo_servicio.get()
            cantidad = int(self.cantidad.get())

            reserva, total = self.sistema.crear_reserva(index, tipo, cantidad)

            self.tree.insert("", "end", values=(
                reserva.cliente.nombre,
                reserva.servicio.descripcion(),
                f"{reserva.cantidad} {reserva.servicio.unidad()}",
                reserva.estado
            ))

            messagebox.showinfo("Total", f"${total}")

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def modificar_reserva(self):
        try:
            item = self.tree.selection()[0]
            nueva_cantidad = int(self.cantidad.get())

            index = self.tree.index(item)
            reserva = self.sistema.reservas[index]

            reserva.modificar(nueva_cantidad)

            self.tree.item(item, values=(
                reserva.cliente.nombre,
                reserva.servicio.descripcion(),
                f"{reserva.cantidad} {reserva.servicio.unidad()}",
                reserva.estado
            ))

            messagebox.showinfo("OK", "Reserva modificada")

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def cancelar_reserva(self):
        try:
            item = self.tree.selection()[0]
            index = self.tree.index(item)
            reserva = self.sistema.reservas[index]

            reserva.cancelar()

            self.tree.item(item, values=(
                reserva.cliente.nombre,
                reserva.servicio.descripcion(),
                f"{reserva.cantidad} {reserva.servicio.unidad()}",
                reserva.estado
            ))

            messagebox.showinfo("OK", "Reserva cancelada")

        except Exception as e:
            messagebox.showerror("Error", str(e))


# ---------------- MAIN ----------------
if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
    