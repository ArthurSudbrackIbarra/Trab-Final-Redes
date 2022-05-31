import time
from configurations import Configuration
from custom_sockets import UDPClientSocket, UDPServerSocket
from packaging import ErrorControlTypes, TokenPacket, DataPacket, PacketIdentifier, CRC32, PacketFaultInserter
from collections import deque
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
        self.messagesQueue = deque()

    def __socketsThread(self) -> None:
        while True:
            # Se tenho o token:
            if self.token is not None:
                if len(self.messagesQueue) == 0 and not self.waiting:
                    self.client.send(self.token.toString())
                    self.token = None
                    self.waiting = True
                elif not self.waiting:
                    self.client.send(self.messagesQueue.popleft())
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
                            f"Pacote recebido de {dataPacket.originNickname}, porém o CRC não bate.")
                        dataPacket.errorControlType = ErrorControlTypes.NACK
                    if self.token is not None:
                        self.client.send(self.token.toString())
                        self.token = None
                    else:
                        self.client.send(packetString)
                # Sou a origem:
                elif dataPacket.originNickname == self.config.nickname:
                    self.waiting = False
                    if dataPacket.errorControlType is ErrorControlTypes.MACHINE_DOES_NOT_EXIST:
                        print(
                            f"\nA mensagem com conteúdo '{dataPacket.message}' não pôde ser enviada, pois a máquina destino {dataPacket.destinationNickname} não se encontra na rede.\n")
                    elif dataPacket.errorControlType is ErrorControlTypes.NACK:
                        self.messagesQueue.appendleft(dataPacket.toString())
                    self.client.send(self.token.toString())
                    self.token = None
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
                self.messagesQueue.append(dataPacket.toString())

    def startThreads(self) -> None:
        Thread(target=self.__socketsThread, name="Sockets Thread").start()
        Thread(target=self.__inputThread, name="Input Thread").start()
