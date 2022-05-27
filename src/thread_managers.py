import threading
from file_interpreters import ConfigInterpreter
from custom_sockets import UDPClientSocket, UDPServerSocket
from packaging import ErrorControlTypes, TokenPacket, DataPacket, CRC32
from queue import Queue


# Essa classe vai gerenciar as duas threads (client e server).
# Atributos: instâncias de CustomUDPClientSocket e CustomUDPServerSocket.


class SocketThreadManager:
    def __init__(self,
                 config: ConfigInterpreter,
                 client: UDPClientSocket,
                 server: UDPServerSocket):
        self.config = config
        self.client = client
        self.server = server
        self.messagesQueue = Queue()

    def __clientThread(self) -> None:
        while True:
            message = input("\nMensagem a ser enviada: ")
            destinationNickname = input("Apelido do destino: ")
            dataPacket = DataPacket(
                ErrorControlTypes.MACHINE_DOES_NOT_EXIST,
                self.config["nickname"],
                destinationNickname,
                -1,
                message
            )
            # ! Falta colocar o CRC !
            self.messagesQueue.put(dataPacket.toString())
            # Se estiver com o token, envia primeira mensagem da fila:
            if True:
                self.client.send(self.messagesQueue.get())

    def __serverThread(self) -> None:
        while True:
            message = self.server.listen()
            print(f"\nMensagem recebida: {message}")

    def startThreads(self) -> None:
        threading.Thread(target=self.__clientThread).start()
        threading.Thread(target=self.__serverThread).start()
