import threading

def clientThread(client):
    while True:
        client.send("Hello!")

def serverThread(server):
    while True:
        server.listen("Oh, hey!")

# Essa classe vai gerenciar as duas threads (client e server).
# Atributos: instâncias de CustomUDPClientSocket e CustomUDPServerSocket.

class SocketThreadManager:
    def __init__(self, client, server):
        self.client = client;
        self.server = server

    def startThreads(self):
        threading.Thread(target=clientThread, args=(self.client,)).start()
        threading.Thread(target=serverThread, args=(self.server,)).start()