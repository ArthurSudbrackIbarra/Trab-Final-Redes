from calendar import c
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
        self.token = TokenPacket() if config["isTokenTrue"] else None
        self.messagesQueue = Queue()

    def __socketsThread(self) -> None:
        while True:
            if self.token is not None:
                pass
            else:
                packetString = self.server.receive()
                packetType = PacketIdentifier.identify(packetString)
                if packetType == PacketIdentifier.TOKEN:
                    self.token = TokenPacket()
                    if self.messagesQueue.empty():
                        self.client.send(self.token.toString())
                    else:
                        self.client.send(self.messagesQueue.get())
                elif packetType == PacketIdentifier.DATA:
                    dataPacket = DataPacket.fromString(packetString)
                    if dataPacket.destinationNickname == self.config["nickname"]:
                        isCRCCorrect = CRC32.check(dataPacket)
                        if isCRCCorrect:
                            print(
                                f"\n[Pacote recebido]\n\nMensagem: {dataPacket.message}\nApelido da origem: {dataPacket.originNickname}\n")
                        else:
                            print(
                                f"Pacote recebido de {dataPacket.originNickname}, porém o CRC não bate. Descartando pacote...")
                    else:
                        self.client.send(packetString)

    def __inputThread(self) -> None:
        while True:
            message = input("\nMensagem a ser enviada: ")
            destinationNickname = input("Apelido do destino: ")
            crc = CRC32.calculate(message)
            dataPacket = DataPacket(
                ErrorControlTypes.MACHINE_DOES_NOT_EXIST,
                self.config["nickname"],
                destinationNickname,
                crc,
                message
            )
            self.messagesQueue.put(dataPacket.toString())

    def startThreads(self) -> None:
        Thread(target=self.__socketsThread).start()
        Thread(target=self.__inputThread).start()
