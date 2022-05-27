import threading
from file_interpreters import ConfigInterpreter
from custom_sockets import UDPClientSocket, UDPServerSocket
from packaging import ErrorControlTypes, TokenPacket, DataPacket, CRC32
from queue import Queue


# Essa classe gerencia as threads de cliente e servidor.


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
            hasToken = True  # Mockado.
            if hasToken:
                # Enviando pacote de dados, mas pode ser de token!
                if not self.messagesQueue.empty():
                    self.client.send(self.messagesQueue.get())

    def __serverThread(self) -> None:
        while True:
            message = self.server.listen()
            # Assumindo que o pacote é de dados, mas pode ser de token!
            dataPacket = DataPacket.fromString(message)
            if dataPacket.destinationNickname == self.config["nickname"]:
                print(f"\nMensagem recebida: {message}")

    def startThreads(self) -> None:
        threading.Thread(target=self.__clientThread).start()
        threading.Thread(target=self.__serverThread).start()
