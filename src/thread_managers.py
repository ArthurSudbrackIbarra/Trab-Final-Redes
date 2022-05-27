from file_interpreters import ConfigInterpreter
from custom_sockets import UDPClientSocket, UDPServerSocket
from packaging import ErrorControlTypes, TokenPacket, DataPacket, PacketIdentifier, CRC32
from queue import Queue
from threading import Thread, Semaphore


# Essa classe gerencia as threads de cliente e servidor.


class SocketThreadManager:
    def __init__(self,
                 config: ConfigInterpreter,
                 client: UDPClientSocket,
                 server: UDPServerSocket):
        self.config = config
        self.client = client
        self.server = server
        self.token = TokenPacket() if config["isTokenTrue"] else None
        self.messagesQueue = Queue()
        # self.semaphore = Semaphore(1)

    def __clientThread(self) -> None:
        while True:
            # Espera semáforo.
            # self.semaphore.acquire()
            message = input("\nMensagem a ser enviada: ")
            destinationNickname = input("Apelido do destino: ")
            dataPacket = DataPacket(
                ErrorControlTypes.MACHINE_DOES_NOT_EXIST,
                self.config["nickname"],
                destinationNickname,
                -1,
                message
            )
            # TODO: Colocar o CRC ^
            self.messagesQueue.put(dataPacket.toString())
            # Se estiver com o token, envia primeira mensagem da fila:
            if self.token is not None:
                if not self.messagesQueue.empty():
                    self.client.send(self.messagesQueue.get())
                else:
                    self.client.send(self.token.toString())
                    self.token = None
            # Libera semáforo.
            # self.semaphore.release()

    def __serverThread(self) -> None:
        while True:
            # Espera semáforo.
            # self.semaphore.acquire()
            packetString = self.server.listen()
            packetType = PacketIdentifier.identify(packetString)
            if packetType == PacketIdentifier.TOKEN:
                self.token = TokenPacket()
                if self.messagesQueue.empty():
                    self.messagesQueue.put(self.token.toString())
                    # self.client.send(self.token.toString())
            elif packetType == PacketIdentifier.DATA:
                dataPacket = DataPacket.fromString(packetString)
                if dataPacket.destinationNickname == self.config["nickname"]:
                    # TODO: Calcular o CRC
                    print(
                        f"\n[Pacote recebido]\n\nMensagem: {dataPacket.message}\nApelido da origem: {dataPacket.originNickname}\n")
                else:
                    # Verificar qual das duas linhas está certa.
                    self.messagesQueue.put(packetString)
                    # self.client.send(packetString)
            # Libera semáforo.
            # self.semaphore.release()

    def startThreads(self) -> None:
        Thread(target=self.__clientThread).start()
        Thread(target=self.__serverThread).start()
