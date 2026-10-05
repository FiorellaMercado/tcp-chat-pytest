
import pytest
import server
import threading
import socket
import time

@pytest.fixture(autouse=True)
def limpiar_lista_conectados():
    server.clientes_conectados.clear()
    yield server.clientes_conectados
    server.clientes_conectados.clear()

#integracion
@pytest.fixture
def levantar_servidor():
    
    servidor=server.crear_servidor("localhost",0)
  
    puerto=servidor.getsockname()[1]
    print(f"trabajando en el puerto: {puerto}")
    hilo=threading.Thread(target=aceptar_clientes_test, args=(servidor,), daemon=True)
    hilo.start()
    yield puerto
    servidor.close()


def aceptar_clientes_test(servidor):
    try:
        server.aceptar_clientes(servidor)
    except OSError:
        pass

@pytest.fixture
def crear_socket(levantar_servidor):
    lista_sockets=[]

    def nuevo_cliente():
        socket_nuevo=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        socket_nuevo.connect(("localhost", levantar_servidor))
        lista_sockets.append(socket_nuevo)
        return socket_nuevo
    yield nuevo_cliente

    for item in lista_sockets: #cada item es uno de los sockets creado
        item.close()

def test_dos_clientes(crear_socket):
    a=crear_socket()
    b=crear_socket()
    
    espera(2,2)

    b.settimeout(2)
    mensaje="hola"
    a.send(mensaje.encode('utf-8'))
    recibido=b.recv(1024).decode('utf-8')
    #assert len(server.clientes_conectados) ==2
    assert recibido == mensaje
    a.settimeout(0.3)
    with pytest.raises(socket.timeout):
        a.recv(1024)


def espera(cant_clientes,tiempo):
    inicio = time.time()
    while len(server.clientes_conectados) != cant_clientes:
            if time.time()-inicio>=tiempo:
                pytest.fail(f"No se conectaron los {cant_clientes} clientes")
            time.sleep(0.01)

def test_tres_clientes(crear_socket):
    a=crear_socket()
    b=crear_socket()
    c=crear_socket()
    
    espera(3,2)

    b.settimeout(2)
    c.settimeout(2)

    mensaje="hola"
    a.send(mensaje.encode('utf-8'))

    recibido_b=b.recv(1024).decode('utf-8')
    recibido_c=c.recv(1024).decode('utf-8')
    
    assert recibido_b == mensaje 
    assert recibido_c == mensaje
    a.settimeout(0.3)
    with pytest.raises(socket.timeout):
        a.recv(1024)