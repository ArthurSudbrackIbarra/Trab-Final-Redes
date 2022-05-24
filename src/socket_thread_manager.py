import threading

# Essa classe vai gerenciar as duas threads (client e server).
# Atributos: instâncias de CustomUDPClientSocket e CustomUDPServerSocket.

class SocketThreadManager:
    def __init__(self, client, server):
        self.client = client;
        self.server = server

    def __clientThread(self, client):
        while True:
            client.send("Hello!")

    def __serverThread(self, server):
        while True:
            server.listen("Oh, hey!")

    def startThreads(self):
        threading.Thread(target=self.__clientThread, args=(self.client,)).start()
        threading.Thread(target=self.__serverThread, args=(self.server,)).start()