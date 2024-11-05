import random
import socket
import threading
import time

# Dirección IP y puertos para la simulación
COMPUTER_ADDRESSES = {
    "master": ("127.0.0.1", 5000),
    "slave1": ("127.0.0.1", 5001),
    "slave2": ("127.0.0.1", 5002)
}

# Función que simula obtener la hora actual de cada computadora
def get_current_time():
    return time.time()

# Función para cada computadora esclava
def slave_node(name, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as slave_socket:
        slave_socket.bind(("127.0.0.1", port))
        slave_socket.listen()
        print(f"{name} está escuchando en el puerto {port}...")
        while True:
            conn, addr = slave_socket.accept()
            with conn:
                data = conn.recv(1024).decode()
                if data == "GET_TIME":
                    current_time = get_current_time()
                    conn.sendall(str(current_time).encode())
                elif data.startswith("ADJUST_TIME"):
                    adjustment = float(data.split(" ")[1])
                    adjusted_time = get_current_time() + adjustment
                    print(f"{name} ha ajustado el tiempo a {adjusted_time:.2f}")

# Función de la computadora maestra que sincroniza las horas
def master_node():
    time_diffs = []
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as master_socket:
        # Conectar a cada esclavo y obtener el tiempo
        for name, address in COMPUTER_ADDRESSES.items():
            if name != "master":
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as slave_socket:
                    slave_socket.connect(address)
                    slave_socket.sendall("GET_TIME".encode())
                    slave_time = float(slave_socket.recv(1024).decode())
                    time.sleep(random.uniform(0.5, 1.5)) # retraso para que el resultado sea más realista
                    time_diff = slave_time - get_current_time()
                    time_diffs.append(time_diff)
                    print(f"Tiempo recibido de {name}: {slave_time}, Diferencia: {time_diff:.2f}")
        
        # Calcular el ajuste promedio
        avg_adjustment = sum(time_diffs) / len(time_diffs)
        print(f"Ajuste promedio calculado: {avg_adjustment:.2f}")

        # Enviar ajuste a cada esclavo
        for name, address in COMPUTER_ADDRESSES.items():
            if name != "master":
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as slave_socket:
                    slave_socket.connect(address)
                    slave_socket.sendall(f"ADJUST_TIME {avg_adjustment}".encode())
                    print(f"Ajuste enviado a {name}: {avg_adjustment:.2f}")

# Configuración de los hilos para ejecutar el código en paralelo
threads = []
# Crear los esclavos en hilos separados
for name, (_, port) in COMPUTER_ADDRESSES.items():
    if name != "master":
        thread = threading.Thread(target=slave_node, args=(name, port))
        threads.append(thread)
        thread.start()

# Ejecutar la computadora maestra
time.sleep(1)  # Espera para que los esclavos estén listos
master_node()

# Esperar a que los hilos terminen (para fines de simulación)
for thread in threads:
    thread.join()
