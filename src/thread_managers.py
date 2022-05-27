from file_interpreters import ConfigInterpreter
from custom_sockets import UDPClientSocket, UDPServerSocket
from packaging import ErrorControlTypes, TokenPacket, DataPacket, PacketIdentifier, CRC32
from queue import Queue
from threading import Thread


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
                # Enviando pacote de dados, mas poderia ser de token (implementar)!
                if not self.messagesQueue.empty():
                    self.client.send(self.messagesQueue.get())

    def __serverThread(self) -> None:
        while True:
            packetString = self.server.listen()
            packetType = PacketIdentifier.identify(packetString)
            # Token = 1, Dados = 2
            if packetType == 1:
                pass
            elif packetType == 2:
                dataPacket = DataPacket.fromString(packetString)
                if dataPacket.destinationNickname == self.config["nickname"]:
                    print(f"\nPacote recebido: {packetString}")

    def startThreads(self) -> None:
        Thread(target=self.__clientThread).start()
        Thread(target=self.__serverThread).start()