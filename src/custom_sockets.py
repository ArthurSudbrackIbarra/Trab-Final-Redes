# -*- coding: utf-8 -*-

import enum
import socket
import time
from math import floor


# Classe do socket cliente UDP.


class UDPClientSocket:
    def __init__(self,
                 serverAddress: str,
                 serverPort: int,
                 bufferSize: int):
        self.serverAddressPort = (serverAddress, serverPort)
        self.bufferSize = bufferSize
        self.udpClientSocket = socket.socket(
            family=socket.AF_INET, type=socket.SOCK_DGRAM)

    def send(self, message: str) -> None:
        bytesToSend = str.encode(message)
        self.udpClientSocket.sendto(bytesToSend, self.serverAddressPort)


# Enum com os tipos de tempo de resposta.


class ResponseTimeTypes(enum.Enum):
    LESS_THAN_EXPECTED = 1
    OK = 2
    TIMEOUT_EXCEEDED = 3


# Classe que representa um pacote que o servidor recebeu de um cliente.


class ClientResponse:
    def __init__(self,
                 message: str,
                 responseTime: ResponseTimeTypes):
        self.message = message
        self.responseTime = responseTime


# Classe do socket servidor UDP.


class UDPServerSocket:
    def __init__(self,
                 port: int,
                 bufferSize: int):
        self.port = port
        self.bufferSize = bufferSize
        self.udpServerSocket = socket.socket(
            family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.udpServerSocket.bind(("", port))
        self.minSecs = -1
        self.maxSecs = 10000

    def receive(self) -> ClientResponse:
        self.udpServerSocket.settimeout(self.maxSecs)
        secondsBefore = floor(time.time())
        clientResponse = None
        bytesAddressPair = ()
        try:
            bytesAddressPair = self.udpServerSocket.recvfrom(self.bufferSize)
            secondsAfter = floor(time.time())
            message = bytesAddressPair[0].decode()
            print(f"\nDiferença de segundos: {secondsAfter - secondsBefore}")
            if secondsAfter - secondsBefore <= self.minSecs:
                clientResponse = ClientResponse(
                    message, ResponseTimeTypes.LESS_THAN_EXPECTED)
            else:
                clientResponse = ClientResponse(message, ResponseTimeTypes.OK)
        except socket.timeout:
            clientResponse = ClientResponse(
                "", ResponseTimeTypes.TIMEOUT_EXCEEDED)
        return clientResponse

    def setTimes(self, minSecs: int, maxSecs: int) -> None:
        self.minSecs = minSecs
        self.maxSecs = maxSecs
