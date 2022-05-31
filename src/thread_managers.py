import time
from configurations import Configuration
from custom_sockets import UDPClientSocket, UDPServerSocket
from packaging import ErrorControlTypes, TokenPacket, DataPacket, PacketIdentifier, CRC32, PacketFaultInserter
from queue import Queue
from threading import Thread


# Essa classe gerencia duas threads: a de sockets e a de recebimento de input.


class SocketThreadManager:
    def __init__(self,
                 config: Configuration,
                 serverSocketPort: int = 9000):
        self.config = config
        self.client = UDPClientSocket(
            serverAddress=config.nextMachineIP,
            serverPort=config.nextMachinePort,
            bufferSize=1024
        )
        self.server = UDPServerSocket(
            port=serverSocketPort,
            bufferSize=1024
        )
        self.token = TokenPacket() if config.isTokenTrue else None
        self.waiting = False if self.token is not None else True
        self.messagesQueue = Queue()

    def __socketsThread(self) -> None:
        while True:
            # Se tenho o token:
            if self.token is not None:
                if self.messagesQueue.empty() and not self.waiting:
                    self.client.send(self.token.toString())
                    self.token = None
                    self.waiting = True
                elif not self.waiting:
                    self.client.send(self.messagesQueue.get())
                    self.waiting = True
            packetString = self.server.receive()
            packetType = PacketIdentifier.identify(packetString)
            # Recebi token:
            if packetType == PacketIdentifier.TOKEN:
                print(f"\nRecebi Token: {packetString}\n")
                self.token = TokenPacket()
                self.waiting = False
                time.sleep(self.config.tokenTime)
                continue
            # Recebi dados:
            elif packetType == PacketIdentifier.DATA:
                print(f"\nRecebi Dados: {packetString}\n")
                dataPacket = DataPacket.fromString(packetString)
                # Sou o destino:
                if dataPacket.destinationNickname == self.config.nickname:
                    isCRCCorrect = CRC32.check(dataPacket)
                    if isCRCCorrect:
                        print(
                            f"\n[Pacote recebido]\n\nMensagem: {dataPacket.message}\nApelido da origem: {dataPacket.originNickname}\n")
                        dataPacket.errorControlType = ErrorControlTypes.ACK
                    else:
                        print(
                            f"Pacote recebido de {dataPacket.originNickname}, porém o CRC não bate. Descartando pacote...")
                        dataPacket.errorControlType = ErrorControlTypes.NACK
                    if self.token is not None:
                        self.client.send(self.token.toString())
                        self.token = None
                    else:
                        self.client.send(packetString)
                # Sou a origem:
                elif dataPacket.originNickname == self.config.nickname:
                    self.waiting = False
                    # Verificar controle de erro...
                    if dataPacket.errorControlType == ErrorControlTypes.MACHINE_DOES_NOT_EXIST:
                        pass
                    elif dataPacket.errorControlType == ErrorControlTypes.ACK:
                        pass
                    elif dataPacket.errorControlType == ErrorControlTypes.NACK:
                        pass
                    # Ver o que fazer aqui...
                    self.client.send(self.token.toString())
                    self.token = None
                    pass
                # Não sou a origem nem o destino:
                else:
                    self.client.send(packetString)

    def __inputThread(self) -> None:
        # 20% dos pacotes serão enviados com erros propositais.
        faultInserter = PacketFaultInserter(20.0)
        while True:
            userInput = input("\nMensagem a ser enviada: ")
            splitted = userInput.split(" -> ")
            if len(splitted) >= 2:
                message = splitted[0]
                destinationNickname = splitted[1]
                crc = CRC32.calculate(message)
                dataPacket = DataPacket(
                    ErrorControlTypes.MACHINE_DOES_NOT_EXIST,
                    self.config.nickname,
                    destinationNickname,
                    crc,
                    message
                )
                faultInserter.tryInsert(dataPacket)
                self.messagesQueue.put(dataPacket.toString())

    def startThreads(self) -> None:
        Thread(target=self.__socketsThread, name="Sockets Thread").start()
        Thread(target=self.__inputThread, name="Input Thread").start()
