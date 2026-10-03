import socket
import threading

HOST = '127.0.0.1'
PORT = 12345

def recibir_mensajes(socket_cliente):
    while True:
        try:
            mensaje = socket_cliente.recv(1024).decode('utf-8')
            if not mensaje:
                print("conexion cerrada por el servidor")
                break
            print(f"{mensaje}")
        except:
            print("error al recibir mensaje")
            break

#crear cliente y conectar
cliente = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
cliente.connect((HOST,PORT)) #ES COMO SI TOCARA LA PUERTA
print(f"Conectado al servidor {HOST}:{PORT}")

#hilo
hilo_recepcion = threading.Thread(target=recibir_mensajes,args=(cliente,))
hilo_recepcion.daemon = True
hilo_recepcion.start()

#enviar mensajes

while True:
    try:
        texto=input("Escribe un mensaje (o 'salir'): ")
        if texto.lower()=="salir":
            break

        #logica de reintento
        enviado = False #bandera
        for intento in range(3):          # hasta 3 reintentos
            try:
                cliente.send(texto.encode('utf-8'))#MANDA BITES 
                enviado = True
                break
            except:
                print(f"Reintentando... ")
                try:
                    cliente.close()
                    cliente = socket.socket(socket.AF_INET,socket.SOCK_STREAM)  # ← socket nuevo
                    cliente.connect((HOST,PORT))
                except:
                    print(f"No se pudo reconectar (intento {intento + 1} de 3)")
        if not enviado:
            print("No se pudo enviar. Vuelva a intentarlo.")
        

    except:
        print("Error al enviar mensaje")


cliente.close()
