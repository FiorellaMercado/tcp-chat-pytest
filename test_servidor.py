import pytest
import server

class SocketFalso:
    def __init__(self):
        self.enviados= []
        self.por_recibir = []
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




