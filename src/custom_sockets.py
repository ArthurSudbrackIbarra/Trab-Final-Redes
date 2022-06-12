# -*- coding: utf-8 -*-

import enum
import socket


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
    OK = 1
    TIMEOUT_EXCEEDED = 2


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
        self.maxWaitingTime = 10000

    def receive(self) -> ClientResponse:
        self.udpServerSocket.settimeout(self.maxWaitingTime)
        clientResponse = None
        try:
            bytesAddressPair = self.udpServerSocket.recvfrom(self.bufferSize)
            message = bytesAddressPair[0].decode()
            clientResponse = ClientResponse(message, ResponseTimeTypes.OK)
        except socket.timeout:
            clientResponse = ClientResponse(
                "", ResponseTimeTypes.TIMEOUT_EXCEEDED)
        return clientResponse

    def setMaxWaitingTime(self, seconds: int) -> None:
        self.maxWaitingTime = seconds
