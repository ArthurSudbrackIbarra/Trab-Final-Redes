import time
import os
from socket import socket
from configurations import Configuration
from custom_sockets import UDPClientSocket, ResponseTimeTypes, UDPServerSocket
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
        # Tempo mínimo e máximo de espera:
        self.server.setTimes(minSecs=-1, maxSecs=10)
        self.token = TokenPacket() if config.isTokenTrue else None
        self.messagesQueue = deque()
        self.receivedNACK = False

    def __socketsThread(self) -> None:
        while True:
            # Se tenho o token:
            if self.token is not None:
                if len(self.messagesQueue) == 0:
                    self.client.send(self.token.toString())
                    self.token = None
                else:
                    nextMessage = self.messagesQueue.popleft()
                    print(
                        f"\nEnviando próxima mensagem da fila: '{nextMessage}'")
                    self.client.send(nextMessage)
            # Tentando receber um pacote por x segundos.
            clientResponse = self.server.receive()
            # Tempo de espera menor que o mínimo.
            if clientResponse.responseTime is ResponseTimeTypes.LESS_THAN_EXPECTED:
                print(
                    "Um pacote foi recebido em um tempo menor que o esperado. Um token deve ser removido da rede.")
            # Tempo de espera maior que o máximo.
            elif clientResponse.responseTime is ResponseTimeTypes.TIMEOUT_EXCEEDED:
                print(
                    f"\n{Colors.FAIL}[Timeout]{Colors.ENDC} de 10 segundos atingido, um novo token será gerado.")
                self.token = TokenPacket()
                continue
            # Tempo de espera OK.
            packetString = clientResponse.message
            packetType = PacketIdentifier.identify(packetString)
            # Recebi token:
            if packetType == PacketIdentifier.TOKEN:
                print(
                    f"\nRecebi Token: {Colors.WARNING}{packetString}{Colors.ENDC}")
                self.token = TokenPacket()
                time.sleep(self.config.tokenTime)
                continue
            # Recebi dados:
            elif packetType == PacketIdentifier.DATA:
                print("\n" + ("-" * 100))
                print(f"Recebi Dados: {packetString}")
                dataPacket = DataPacket.fromString(packetString)
                # Sou o destino:
                if dataPacket.destinationNickname == self.config.nickname or (dataPacket.destinationNickname == "TODOS" and dataPacket.originNickname != self.config.nickname):
                    isCRCCorrect = CRC32.check(dataPacket)
                    if isCRCCorrect:
                        print(
                            f"Retornando {Colors.OKGREEN}[ACK]{Colors.ENDC} - Origem: {dataPacket.originNickname}, Mensagem: {dataPacket.message}")
                        dataPacket.errorControlType = ErrorControlTypes.ACK
                    else:
                        print(
                            f"Retornando {Colors.FAIL}[NACK]{Colors.ENDC} - Origem: {dataPacket.originNickname}, o CRC não bate.")
                        dataPacket.errorControlType = ErrorControlTypes.NACK
                    self.client.send(dataPacket.toString())
                # Sou a origem:
                elif dataPacket.originNickname == self.config.nickname:
                    if dataPacket.errorControlType is ErrorControlTypes.MACHINE_DOES_NOT_EXIST:
                        print(
                            f"Recebi {Colors.FAIL}[maquinanaoexiste]{Colors.ENDC} - A mensagem com conteúdo '{dataPacket.message}' não pôde ser enviada, pois a máquina destino '{dataPacket.destinationNickname}' não se encontra na rede.")
                    elif dataPacket.errorControlType is ErrorControlTypes.ACK:
                        print(
                            f"Recebi {Colors.OKGREEN}[ACK]{Colors.ENDC} para a mensagem '{dataPacket.message}' - o recebimento do pacote foi confirmado.")
                    elif dataPacket.errorControlType is ErrorControlTypes.NACK:
                        if not self.receivedNACK:
                            print(
                                f"Recebi {Colors.FAIL}[NACK]{Colors.ENDC} para a mensagem '{dataPacket.message}' - colocando o pacote no início da fila para tentar novamente.")
                            self.receivedNACK = True
                            self.messagesQueue.appendleft(
                                dataPacket.toString())
                        else:
                            print(
                                f"Mesmo após o reenvio do pacote, um {Colors.FAIL}[NACK]{Colors.ENDC} foi recebido novamente. O pacote não será adicionado na fila novamente.")
                            self.receivedNACK = False
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
                        f"\nMensagem {Colors.OKCYAN}'{message}'{Colors.ENDC} para {Colors.OKCYAN}'{destinationNickname}'{Colors.ENDC} colocada na fila!")
                    lastUserInput = userInput

    def startThreads(self) -> None:
        Thread(target=self.__socketsThread, name="Sockets Thread").start()
        Thread(target=self.__inputThread, name="Input Thread").start()
