import time
import os
import random
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
                 serverSocketPort: int = 9000,
                 minWaitingTime: int = -1,
                 maxWaitingTime: int = 10,
                 tokenFailure: bool = False):
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
        self.server.setMaxWaitingTime(maxWaitingTime)
        self.minWaitingTime = minWaitingTime
        self.tokenFailure = tokenFailure
        self.token = TokenPacket() if config.isTokenTrue else None
        self.messagesQueue = deque()
        self.receivedNAK = False
        self.lastTokenTime = -1

    def __socketsThread(self) -> None:
        while True:
            # Se tenho o token:
            if self.token is not None:
                if len(self.messagesQueue) == 0:
                    numberGenerated = random.random()
                    # 5% dos casos não enviará o token se tokenFailure = True.
                    if not self.tokenFailure or numberGenerated < 0.95:
                        print("\nEnviando token para a máquina à direita.")
                        self.client.send(self.token.toString())
                    else:
                        print(
                            f"{Colors.OKBLUE}\nRemovendo{Colors.ENDC} token da rede...")
                    self.token = None
                else:
                    nextMessage = self.messagesQueue.popleft()
                    print(
                        f"\nEnviando próxima mensagem da fila: '{nextMessage}'")
                    self.client.send(nextMessage)
            # Tentando receber um pacote por x segundos.
            clientResponse = self.server.receive()
            packetString = clientResponse.message
            packetType = PacketIdentifier.identify(packetString)
            # Não recebi nada:
            if packetType == PacketIdentifier.UNKNOWN and self.config.isTokenTrue:
                print(
                    f"\n{Colors.FAIL}[Timeout]{Colors.ENDC} atingido, um novo token será gerado.")
                self.token = TokenPacket()
            # Recebi token:
            elif packetType == PacketIdentifier.TOKEN:
                print(
                    f"\nRecebi Token: {Colors.WARNING}{packetString}{Colors.ENDC}")
                # Tempo de espera menor que o mínimo.
                if (time.time() - self.lastTokenTime < self.minWaitingTime) and self.config.isTokenTrue:
                    print(
                        f"\n{Colors.OKBLUE}Descartando{Colors.ENDC} o token, pois este foi recebido em um tempo menor que o esperado.")
                else:
                    self.token = TokenPacket()
                    self.lastTokenTime = time.time()
                    time.sleep(self.config.tokenTime)
            # Recebi dados:
            elif packetType == PacketIdentifier.DATA:
                print("\n" + ("-" * 100))
                print(f"Recebi Dados: {packetString}")
                dataPacket = DataPacket.fromString(packetString)
                # Broadcast:
                if dataPacket.destinationNickname == "TODOS" and dataPacket.originNickname != self.config.nickname:
                    print(
                        f"Retornando {Colors.OKCYAN}[maquinanaoexiste]{Colors.ENDC}, a mensagem recebida foi enviada em broadcast.")
                    dataPacket.errorControlType = ErrorControlTypes.MACHINE_DOES_NOT_EXIST
                    self.client.send(dataPacket.toString())
                # Sou o destino:
                elif dataPacket.destinationNickname == self.config.nickname:
                    isCRCCorrect = CRC32.check(dataPacket)
                    if isCRCCorrect:
                        print(
                            f"Retornando {Colors.OKGREEN}[ACK]{Colors.ENDC} - Origem: {dataPacket.originNickname}, Mensagem: {dataPacket.message}")
                        dataPacket.errorControlType = ErrorControlTypes.ACK
                    else:
                        print(
                            f"Retornando {Colors.FAIL}[NAK]{Colors.ENDC} - Origem: {dataPacket.originNickname}, o CRC não bate.")
                        dataPacket.errorControlType = ErrorControlTypes.NAK
                    self.client.send(dataPacket.toString())
                # Sou a origem:
                elif dataPacket.originNickname == self.config.nickname:
                    if dataPacket.destinationNickname == "TODOS" and dataPacket.errorControlType is ErrorControlTypes.MACHINE_DOES_NOT_EXIST:
                        print(
                            f"Recebi {Colors.OKCYAN}[maquinanaoexiste]{Colors.ENDC} para a mensagem '{dataPacket.message}' - retorno de meu BROADCAST.")
                    elif dataPacket.errorControlType is ErrorControlTypes.MACHINE_DOES_NOT_EXIST:
                        print(
                            f"Recebi {Colors.FAIL}[maquinanaoexiste]{Colors.ENDC} - A mensagem com conteúdo '{dataPacket.message}' não pôde ser enviada, pois a máquina destino '{dataPacket.destinationNickname}' não se encontra na rede.")
                    elif dataPacket.errorControlType is ErrorControlTypes.ACK:
                        print(
                            f"Recebi {Colors.OKGREEN}[ACK]{Colors.ENDC} para a mensagem '{dataPacket.message}' - o recebimento do pacote foi confirmado.")
                    elif dataPacket.errorControlType is ErrorControlTypes.NAK:
                        if not self.receivedNAK:
                            print(
                                f"Recebi {Colors.FAIL}[NAK]{Colors.ENDC} para a mensagem '{dataPacket.message}' - colocando o pacote no início da fila para tentar novamente.")
                            self.receivedNAK = True
                            self.messagesQueue.appendleft(
                                dataPacket.toString())
                        else:
                            print(
                                f"Mesmo após o reenvio do pacote, um {Colors.FAIL}[NAK]{Colors.ENDC} foi recebido novamente. O pacote não será adicionado na fila novamente.")
                            self.receivedNAK = False
                    numberGenerated = random.random()
                    # 5% dos casos não enviará o token se tokenFailure = True.
                    if not self.tokenFailure or numberGenerated < 0.95:
                        if self.token is not None:
                            print(
                                f"Enviando token [{Colors.WARNING}{self.token.toString()}{Colors.ENDC}] para a máquina à direita com IP: {self.config.nextMachineIP}")
                            self.client.send(self.token.toString())
                    else:
                        print(
                            f"{Colors.OKBLUE}\nRemovendo{Colors.ENDC} token da rede...")
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
        oldUserInputs = []
        while True:
            newUserInputs = []
            with open(absoluteFilePath, "r") as inputsFile:
                lines = inputsFile.readlines()
                if len(lines) > 0:
                    newUserInputs = lines[:10]
            if len(newUserInputs) > 0 and newUserInputs != oldUserInputs:
                for userInput in newUserInputs:
                    splitted = userInput.strip().split(" -> ")
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
                        oldUserInputs = newUserInputs

    def startThreads(self) -> None:
        Thread(target=self.__socketsThread, name="Sockets Thread").start()
        Thread(target=self.__inputThread, name="Input Thread").start()
