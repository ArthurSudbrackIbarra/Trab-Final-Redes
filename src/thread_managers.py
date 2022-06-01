import time
import os
from configurations import Configuration
from custom_sockets import UDPClientSocket, UDPServerSocket
from packaging import ErrorControlTypes, TokenPacket, DataPacket, PacketIdentifier, CRC32, PacketFaultInserter
from coloring import Colors
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
                print(
                    f"\nRecebi Token: {Colors.WARNING}{packetString}{Colors.ENDC}")
                self.token = TokenPacket()
                self.waiting = False
                time.sleep(self.config.tokenTime)
                continue
            # Recebi dados:
            elif packetType == PacketIdentifier.DATA:
                print("-" * 100)
                print(f"Recebi Dados: {packetString}")
                dataPacket = DataPacket.fromString(packetString)
                # Sou o destino:
                if dataPacket.destinationNickname == self.config.nickname:
                    isCRCCorrect = CRC32.check(dataPacket)
                    if isCRCCorrect:
                        print(
                            f"{Colors.OKGREEN}[ACK]{Colors.ENDC} - Origem: {dataPacket.originNickname}, Mensagem: {dataPacket.message}")
                        dataPacket.errorControlType = ErrorControlTypes.ACK
                    else:
                        print(
                            f"{Colors.FAIL}[NACK]{Colors.ENDC} - Origem: {dataPacket.originNickname}, o CRC não bate.")
                        dataPacket.errorControlType = ErrorControlTypes.NACK
                    print(
                        f"Enviando dados [{dataPacket.toString()}] para a máquina à direita com IP: {self.config.nextMachineIP}")
                    self.client.send(dataPacket.toString())
                # Sou a origem:
                elif dataPacket.originNickname == self.config.nickname:
                    self.waiting = False
                    if dataPacket.errorControlType is ErrorControlTypes.MACHINE_DOES_NOT_EXIST:
                        print(
                            f"{Colors.FAIL}[maquinanaoexiste]{Colors.ENDC} - A mensagem com conteúdo '{dataPacket.message}' não pôde ser enviada, pois a máquina destino '{dataPacket.destinationNickname}' não se encontra na rede.")
                    elif dataPacket.errorControlType is ErrorControlTypes.ACK:
                        print(
                            f"{Colors.OKGREEN}[ACK]{Colors.ENDC} recebido para a mensagem '{dataPacket.message}' - o recebimento do pacote foi confirmado.")
                    elif dataPacket.errorControlType is ErrorControlTypes.NACK:
                        print(
                            f"{Colors.FAIL}[NACK]{Colors.ENDC} recebido para a mensagem '{dataPacket.message}' - colocando o pacote no início da fila para tentar novamente.")
                        self.messagesQueue.appendleft(dataPacket.toString())
                    print(
                        f"Enviando token [{self.token.toString()}] para a máquina à direita com IP: {self.config.nextMachineIP}")
                    self.client.send(self.token.toString())
                    self.token = None
                # Não sou a origem nem o destino:
                else:
                    self.client.send(packetString)
                print("-" * 100)

    def __inputThread(self) -> None:
        # 20% dos pacotes serão enviados com erros propositais.
        faultInserter = PacketFaultInserter(20.0)
        # Caminho do arquivo inputs.txt
        absoluteFilePath = os.path.abspath("messages/inputs.txt")
        # Último input do usuário:
        lastUserInput = ""
        while True:
            userInput = ""
            with open(absoluteFilePath) as inputsFile:
                lines = inputsFile.readlines()
                if len(lines) > 0:
                    # Última linha:
                    userInput = lines[-1]
            # Se tem input e não é o mesmo de antes:
            if userInput != "" and userInput != lastUserInput:
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
                    print(
                        f"\nMensagem {Colors.OKCYAN}'{message}'{Colors.ENDC} para {Colors.OKCYAN}'{destinationNickname}'{Colors.ENDC} colocada na fila!\n")
                    lastUserInput = userInput

    def startThreads(self) -> None:
        Thread(target=self.__socketsThread, name="Sockets Thread").start()
        Thread(target=self.__inputThread, name="Input Thread").start()
