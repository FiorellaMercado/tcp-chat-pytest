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


@pytest.mark.parametrize("mensaje",[(b" "), 
                                    (b"\t"),
                                    (b"x" * 201)])
def test_servidor_invalida_mensajes(mensaje):
    emisor=SocketFalso()
    receptor=SocketFalso()

    server.clientes_conectados.append(receptor)
    emisor.por_recibir.append(mensaje)

    server.manejar_cliente(emisor,("127.0.0.1", 5000))

    assert len(receptor.enviados)==0

  


@pytest.mark.parametrize("mensaje",[(b" "), 
                                    (b"\t"),
                                    (b"x" * 201)])
                                    #(b"<script>const elemento=document.getElementById('miTexto');const mensaje='Texto cambiado con JavaScript!';const mensajeLargo='Este es un mensaje adicional para aumentar la cantidad de caracteres del script y comprobar correctamente el comportamiento del servidor cuando recibe contenido de mayor longitud.';elemento.textContent=mensaje+' '+mensajeLargo;</script>")])
#es mejor probar con b"x" * 201 ya que no asegura que falla por la longitud y no por simbolos, ademas no permite probrar el limite, el primer y ulitmo valido
def test_servidor_avisa_mensajes_invalidos(mensaje):
    emisor=SocketFalso()
    receptor=SocketFalso()

    server.clientes_conectados.append(receptor)
    emisor.por_recibir.append(mensaje)

    server.manejar_cliente(emisor,("127.0.0.1", 5000))

    recibido = b"".join(emisor.enviados).decode("utf-8")

    assert "inválido" in recibido

# test positivo
@pytest.mark.parametrize("mensaje",[(b"Hola" ), 
                                    (b"<b>hola</b>"),
                                    (b"x" * 200)])
def test_servidor_valida_mensajes(mensaje):
    emisor=SocketFalso()
    receptor=SocketFalso()

    server.clientes_conectados.append(receptor)
    emisor.por_recibir.append(mensaje)

    server.manejar_cliente(emisor,("127.0.0.1", 5000))

    assert receptor.enviados == [mensaje]
    assert emisor.enviados == [] #prever que al emisor no le llegue es mensaje de error