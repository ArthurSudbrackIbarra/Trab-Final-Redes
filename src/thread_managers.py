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
        self.waiting = False if self.token else True

    def __socketsThread(self) -> None:
        while True:
            # Tenho o token:
            if self.token is not None:
                if self.messagesQueue.empty() and not self.waiting:
                    self.client.send(self.token.toString())
                    self.token = None
                    self.waiting = True
                elif not self.waiting:
                    self.client.send(self.messagesQueue.get())
                    self.waiting = True
            # Não tenho o token:
            else:
                packetString = self.server.receive()
                packetType = PacketIdentifier.identify(packetString)
                # Recebi token:
                if packetType == PacketIdentifier.TOKEN:
                    self.token = TokenPacket()
                    self.waiting = False
                    continue
                # Recebi dados:
                elif packetType == PacketIdentifier.DATA:
                    dataPacket = DataPacket.fromString(packetString)
                    # Sou o destino:
                    if dataPacket.destinationNickname == self.config["nickname"]:
                        isCRCCorrect = CRC32.check(dataPacket)
                        if isCRCCorrect:
                            print(
                                f"\n[Pacote recebido]\n\nMensagem: {dataPacket.message}\nApelido da origem: {dataPacket.originNickname}\n")
                        else:
                            print(
                                f"Pacote recebido de {dataPacket.originNickname}, porém o CRC não bate. Descartando pacote...")
                    # Sou a origem:
                    elif dataPacket.originNickname == self.config["nickname"]:
                        self.waiting = False
                        # Verificar controle de erro...
                        pass
                    else:
                        self.client.send(packetString)

    def __inputThread(self) -> None:
        while True:
            # message = input("\nMensagem a ser enviada: ")
            # destinationNickname = input("Apelido do destino: ")
            message = "Hello!"
            destinationNickname = "Bob"
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
        socketsThread = Thread(
            target=self.__socketsThread, name="Sockets Thread")
        inputThread = Thread(
            target=self.__inputThread, name="Input Thread")
        socketsThread.start()
        inputThread.start()
