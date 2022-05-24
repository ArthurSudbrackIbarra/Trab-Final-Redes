# -*- coding: utf-8 -*-

import socket

class CustomUDPClientSocket:
    def __init__(self, serverAddress, serverPort, bufferSize):
        self.serverAddressPort = (serverAddress, serverPort)
        self.bufferSize = bufferSize

        self.UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

    def send(self, message):
        bytesToSend = str.encode(message)
        self.UDPClientSocket.sendto(bytesToSend, self.serverAddressPort)

    def receive(self):
        msgFromServer = self.UDPClientSocket.recvfrom(self.bufferSize)
        return msgFromServer[0]