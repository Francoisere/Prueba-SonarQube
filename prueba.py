import os
import sys
import hashlib
import datetime

# TODO: mover estas credenciales a variables de entorno
DB_HOST = "localhost"
DB_USER = "admin"
DB_PASSWORD = "admin1234"          # Sonar: hardcoded credential
SECRET_KEY = "s3cr3t_k3y_supersegura"  # Sonar: hardcoded secret

MAX_INTENTOS = 3
TASA_INTERES = 0.05


# ---- Modelo de cuenta ----

class Cuenta:
    def __init__(self, id, nombre, saldo, pin):
        self.id = id
        self.nombre = nombre
        self.saldo = saldo
        self.pin = pin                  # Sonar: contraseña almacenada en texto plano
        self.transacciones = []
        self.intentos_fallidos = 0

    def autenticar(self, pin_ingresado):
        if pin_ingresado == self.pin:   # Sonar: comparación directa de contraseña
            self.intentos_fallidos = 0
            return True
        else:
            self.intentos_fallidos += 1
            return False

    def depositar(self, monto):
        if monto > 0:
            self.saldo = self.saldo + monto
            self.transacciones.append(("deposito", monto, datetime.datetime.now()))
            return True
        else:
            return False

    def retirar(self, monto):
        resultado = False                   # Sonar: variable innecesaria
        if monto > 0 and monto <= self.saldo:
            self.saldo = self.saldo - monto
            self.transacciones.append(("retiro", monto, datetime.datetime.now()))
            resultado = True
        return resultado

    def calcular_interes(self):
        interes = self.saldo * TASA_INTERES
        self.saldo = self.saldo + interes
        self.transacciones.append(("interes", interes, datetime.datetime.now()))
        return interes


# ---- Gestor del banco ----

class GestorBanco:
    def __init__(self):
        self.cuentas = {}
        self.log = []

    def crear_cuenta(self, nombre, saldo_inicial, pin):
        id_cuenta = len(self.cuentas) + 1
        nueva = Cuenta(id_cuenta, nombre, saldo_inicial, pin)
        self.cuentas[id_cuenta] = nueva
        self._registrar_log("cuenta_creada", id_cuenta)
        return id_cuenta

    def obtener_cuenta(self, id_cuenta):
        # Sonar: no se valida si la clave existe antes de acceder
        cuenta = self.cuentas[id_cuenta]
        return cuenta

    def transferir(self, id_origen, id_destino, monto, pin):
        origen = self.cuentas[id_origen]
        destino = self.cuentas[id_destino]

        if not origen.autenticar(pin):
            print("PIN incorrecto")
            return False

        # Sonar: lógica duplicada con el método retirar()
        if monto > 0 and monto <= origen.saldo:
            origen.saldo -= monto
            destino.saldo += monto
            self._registrar_log("transferencia", id_origen)
            return True
        return False

    def reporte_cuentas(self):
        print("==== REPORTE DE CUENTAS ====")
        for id, cuenta in self.cuentas.items():
            # Sonar: variable 'id' sombrea el built-in de Python
            print(f"ID: {id} | Nombre: {cuenta.nombre} | Saldo: ${cuenta.saldo:.2f}")

        total = 0
        for id, cuenta in self.cuentas.items():   # Sonar: segundo loop innecesario, podría unirse al anterior
            total = total + cuenta.saldo
        print(f"TOTAL EN BANCO: ${total:.2f}")

    def aplicar_interes_a_todos(self):
        for id_cuenta in self.cuentas:
            c = self.cuentas[id_cuenta]
            c.calcular_interes()
            # Sonar: resultado ignorado (podría ser útil para logging)

    def _registrar_log(self, evento, referencia):
        entrada = {
            "evento": evento,
            "referencia": referencia,
            "timestamp": str(datetime.datetime.now()),
            "servidor": DB_HOST,       # Sonar: información sensible en log
            "usuario_db": DB_USER      # Sonar: credencial expuesta en log
        }
        self.log.append(entrada)

    def buscar_cuenta_por_nombre(self, nombre):
        # Sonar: complejidad ciclomática alta + lógica confusa
        resultado = None
        encontrado = False
        for id_cuenta in self.cuentas:
            cuenta = self.cuentas[id_cuenta]
            if cuenta.nombre == nombre:
                if not encontrado:
                    resultado = cuenta
                    encontrado = True
                else:
                    resultado = cuenta   # Sonar: sobreescribe sin avisar si hay duplicados
        if encontrado == True:           # Sonar: comparación redundante con True
            return resultado
        else:
            return None


# ---- Ejecución principal ----

def main():
    banco = GestorBanco()

    # Crear cuentas de prueba
    id1 = banco.crear_cuenta("Ana García",   5000.0, "1234")
    id2 = banco.crear_cuenta("Luis Pérez",   3000.0, "5678")
    id3 = banco.crear_cuenta("María López", 10000.0, "0000")

    # Operaciones básicas
    c1 = banco.obtener_cuenta(id1)
    c1.depositar(500)
    c1.retirar(200)

    banco.transferir(id2, id1, 1000, "5678")

    banco.aplicar_interes_a_todos()

    banco.reporte_cuentas()

    # Búsqueda
    encontrada = banco.buscar_cuenta_por_nombre("Ana García")
    if encontrada != None:              # Sonar: usar 'is not None' en lugar de != None
        print(f"\nCuenta encontrada: {encontrada.nombre}, saldo: ${encontrada.saldo:.2f}")

    # Sonar: variable declarada pero nunca usada
    hash_secreto = hashlib.md5(SECRET_KEY.encode()).hexdigest()

    # Sonar: print de información sensible
    print(f"\nConectando a DB en {DB_HOST} con usuario {DB_USER} / {DB_PASSWORD}")


if __name__ == "__main__":
    main()
