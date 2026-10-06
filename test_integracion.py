
import pytest
import server
import threading
import socket
import time
import struct

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

def test_ordenados_duplicados(crear_socket):
    a=crear_socket()
    b=crear_socket()

    espera(2, 2)


    mensajes=["uno","dos","tres"]
    for mensaje in mensajes:
        a.send(mensaje.encode('utf-8'))
   

    bytes_acuculados=recibir_hasta(b,len("unodostres"),2)

    assert bytes_acuculados.decode('utf-8') == "unodostres"

    #duplicados
    b.settimeout(0.3)
    with pytest.raises(socket.timeout):
        b.recv(1024)

    a.settimeout(0.3)
    with pytest.raises(socket.timeout):
        a.recv(1024)
    
    




def recibir_hasta(sock, cantidad_bytes, tiempo_max):
    bytes_acumulados=b""
    inicio=time.time()
    while len(bytes_acumulados)<cantidad_bytes:

        tiempo_restante=tiempo_max-(time.time()-inicio)

        if tiempo_restante <= 0: 
            pytest.fail(f"Tiempo agotado. Bytes recibido {bytes_acumulados}")

        sock.settimeout(tiempo_restante)

        try:
            recibido = sock.recv(1024) # 4. recv dentro del try
        except socket.timeout:
            pytest.fail(f"Tiempo agotado. Bytes recibido {bytes_acumulados}")

        
        if not recibido:
            pytest.fail(f"el servidor cerró la conexión, bytes recibido hasta ahora {bytes_acumulados}")
        bytes_acumulados=bytes_acumulados+recibido
        
    
    return bytes_acumulados


    
def test_simultaneo(crear_socket):
    evento = threading.Event()

    a=crear_socket()
    b=crear_socket()
    c=crear_socket()

    #b receptor
    espera(3,2)

    #mensajes
    lista_a=["un","dos","tres"]
    lista_b=["a","b","C"]

    def enviar(lista, sock):
        for item in lista:
            evento.wait()
            sock.send(item.encode('utf-8'))

    hilo_a=threading.Thread(target=enviar,args=(lista_a,a))
    hilo_b=threading.Thread(target=enviar,args=(lista_b,b))

    
    hilo_a.start()
    hilo_b.start()
    evento.set()         
    hilo_a.join(timeout=2)
    hilo_b.join(timeout=2)



    bytes_a="".join(lista_a)
    bytes_b="".join(lista_b)
    letras_a = set(bytes_a)
    letras_b = set(bytes_b)

    total_bytes=len(bytes_a)+len(bytes_b)

    bytes_acumulados_c=recibir_hasta(c,total_bytes,2)

    bytes_acumulados_a=recibir_hasta(a,len(bytes_b),2)
    bytes_acumulados_b=recibir_hasta(b,len(bytes_a),2)

    
    texto_c = bytes_acumulados_c.decode('utf-8') 

    # los conjuntos no pueden compartir letras, si no el filtro se rompe
    assert letras_a.isdisjoint(letras_b)

    solo_a = ""
    solo_b = ""
    for caracter in texto_c:
        if caracter in letras_a:
            solo_a += caracter
        elif caracter in letras_b:
            solo_b += caracter

            

    assert solo_a == bytes_a
    assert solo_b == bytes_b

    assert bytes_acumulados_a.decode('utf-8') == bytes_b
    assert bytes_acumulados_b.decode('utf-8') == bytes_a

    #duplicados
    c.settimeout(0.3)
    with pytest.raises(socket.timeout):
        c.recv(1024)

    b.settimeout(0.3)
    with pytest.raises(socket.timeout):
        b.recv(1024)

    a.settimeout(0.3)
    with pytest.raises(socket.timeout):
        a.recv(1024)

def cerrar_abruptamente(sock):
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_LINGER, struct.pack('ii', 1, 0))
    sock.close()

#test servidor sigue funcionando si un cliente se cae abruptamente
def test_SO_LINGER(crear_socket):
    a=crear_socket()
    b=crear_socket()
    c=crear_socket()

    espera(3,2)

    cerrar_abruptamente(b)

    a.send("hola".encode('utf-8'))

    c.settimeout(2)
    mensaje=c.recv(1024).decode('utf-8')

    assert mensaje == "hola"

    espera(2, 2)

    d=crear_socket()

    espera(3, 2)

    a.send("hola de nuevo".encode('utf-8'))

    d.settimeout(2)
    mensaje2=d.recv(1024).decode('utf-8')

    assert mensaje2 == "hola de nuevo"

@pytest.mark.parametrize("caidos", [1, 2])
def test_SO_LINGER_varios_clientes(crear_socket, caidos):
    clientes=[]
    for i in range(4):
        clientes.append(crear_socket())

    

    emisor=clientes[0]
    receptores=clientes[1:]

    caen=receptores[0:caidos]
    vivos=receptores[caidos:]

    espera(4, 2)

    for sock in caen:
        cerrar_abruptamente(sock)

    emisor.send("hola".encode('utf-8'))

    for sock in vivos:
        sock.settimeout(2)
        mensaje=sock.recv(1024).decode('utf-8')
        assert mensaje == "hola"
    
    espera(4-caidos,2)


    d=crear_socket()

    espera(4 - caidos + 1, 2)

    emisor.send("hola de nuevo".encode('utf-8'))

    d.settimeout(2)
    mensaje2=d.recv(1024).decode('utf-8')

    assert mensaje2 == "hola de nuevo"

