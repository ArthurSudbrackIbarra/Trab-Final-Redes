# -*- coding: utf-8 -*-

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


# Classe do socket servidor UDP.


class UDPServerSocket:
    def __init__(self,
                 localIP: str,
                 localPort: int,
                 bufferSize: int):
        self.localIP = localIP
        self.localPort = localPort
        self.bufferSize = bufferSize
        self.udpServerSocket = socket.socket(
            family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.udpServerSocket.bind((localIP, localPort))

    def receive(self) -> str:
        while(True):
            bytesAddressPair = self.udpServerSocket.recvfrom(self.bufferSize)
            return bytesAddressPair[0].decode()
