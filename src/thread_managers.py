import threading

from custom_sockets import UDPClientSocket, UDPServerSocket

# Essa classe vai gerenciar as duas threads (client e server).
# Atributos: instâncias de CustomUDPClientSocket e CustomUDPServerSocket.


class SocketThreadManager:
    def __init__(self,
                 client: UDPClientSocket,
                 server: UDPServerSocket):
        self.client = client
        self.server = server

    def __clientThread(self, client: UDPClientSocket) -> None:
        while True:
            client.send("Hello!")

    def __serverThread(self, server: UDPServerSocket) -> None:
        while True:
            server.listen("Oh, hey!")

    def startThreads(self) -> None:
        threading.Thread(target=self.__clientThread,
                         args=(self.client,)).start()
        threading.Thread(target=self.__serverThread,
                         args=(self.server,)).start()
