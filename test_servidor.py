import pytest
import server

class SocketFalso:
    def __init__(self):
        self.enviados= [] #lo que el servidor envio a este cliente
        self.por_recibir = []  # lo que "escribe" este cliente
        self.cerrado=False

    def send(self,datos):
        self.enviados.append(datos)

    def recv(self,tam):
        if not self.por_recibir:
            return b""
        elemento=self.por_recibir.pop(0)
        return elemento

    def close(self):
        self.cerrado= True

# socket1=SocketFalso()
# socket1.send(b"hola")
# socket1.send(b"que tal")
# print(socket1.enviados)
# socket1.close()
# print(socket1.cerrado)



@pytest.fixture(autouse=True)
def limpiar_lista_conectados():
    server.clientes_conectados.clear()
    yield server.clientes_conectados
    server.clientes_conectados.clear()

def test_broadcast_no_envia_al_emisor():
    receptor=SocketFalso()
    receptor2=SocketFalso()
    emisor=SocketFalso()

    server.clientes_conectados.extend([receptor,receptor2,emisor])

    server.broadcast("hola",emisor)
    assert len(emisor.enviados) ==0
    assert receptor.enviados== [b"hola"]
    assert receptor2.enviados==[b"hola"]


def test_broadcast_borde():
    emisor=SocketFalso()
    server.clientes_conectados.append(emisor)
    server.broadcast("hola", emisor)
    assert len(emisor.enviados) == 0

def test_manejar_clientes():
    emisor=SocketFalso()
    receptor=SocketFalso()

    server.clientes_conectados.append(receptor)
    emisor.por_recibir.append(b"Hola")

    server.manejar_cliente(emisor,("127.0.0.1", 5000))

    assert receptor.enviados == [b"Hola"]
    assert emisor not in server.clientes_conectados
    assert emisor.cerrado



