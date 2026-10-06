import socket
import threading #IMPORTAMOS PARA MULTI CLIENTE

HOST = '127.0.0.1' #direccion 
PORT = 12345 #puerto
#lista de clientes
clientes_conectados = []
clientes_lock = threading.Lock()

def manejar_cliente(socket_cliente,direccion):
    print(f"Cliente conectado de {direccion}")

    with clientes_lock:
        clientes_conectados.append(socket_cliente)
        print(f"Clientes conectados ahora: {len(clientes_conectados)}")

    while True:
        try:

            mensaje = socket_cliente.recv(1024).decode('utf-8')
            if not mensaje:
                print(f"Cliente {direccion} desconectado")
                break

            mensaje_valido=validar_mensaje(mensaje)
            if mensaje_valido is None:
                socket_cliente.send("Mensaje inválido".encode('utf-8'))
                continue

            print(f"Recibido de {direccion}: {mensaje_valido}")
            broadcast(mensaje_valido, socket_cliente)

        except ConnectionResetError:
            print(f"cliente {direccion} se desconectó abruptamente")
            break

    with clientes_lock:
        if socket_cliente in clientes_conectados:
            clientes_conectados.remove(socket_cliente)
        print(f"Clientes conectados ahora: {len(clientes_conectados)}")
    
    socket_cliente.close()


def broadcast(mensaje, cliente_emisor):
    with clientes_lock:
        #agregado para manejar desconexiones abruptas
        sockets_muertos=[]
        for cliente in clientes_conectados:
            if cliente != cliente_emisor:
                try:
                    cliente.send(mensaje.encode('utf-8'))  #PERMITE ENVIAR ESTE MENSAJE A LOS DEMÁS CLIENTES 
                except ConnectionError:
                    sockets_muertos.append(cliente)
        for sock in sockets_muertos:
            clientes_conectados.remove(sock)

# conf del server
def crear_servidor(host=HOST, port=PORT):
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor.bind((host, port))  # RECIBO EN ESTA DIRECCION
    servidor.listen()  # MOD ESCUCHA
    print(f"Servidor escuchando en {host}:{port}")
    return servidor

#loop
def aceptar_clientes(servidor):
    while True:
        socket_cliente, direccion = servidor.accept()  # ATIENDE AL CLIENTE
        hilo = threading.Thread(target=manejar_cliente, args=(socket_cliente, direccion))
        hilo.start()

#validacion de mensaje
limite=200
def validar_mensaje(mensaje):
    mensaje=mensaje.strip()
    if mensaje=="" or len(mensaje)>limite:
        return None
    return mensaje


if __name__ == "__main__":
    servidor = crear_servidor()
    aceptar_clientes(servidor)