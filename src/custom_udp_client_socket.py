# -*- coding: utf-8 -*-

import socket

class CustomUDPClientSocket:
    def __init__(self, serverAddress, serverPort, bufferSize):
        self.serverAddressPort = (serverAddress, serverPort)
        self.bufferSize = bufferSize
        self.udpClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

    def send(self, message):
        bytesToSend = str.encode(message)
        self.udpClientSocket.sendto(bytesToSend, self.serverAddressPort)

    def receive(self):
        msgFromServer = self.udpClientSocket.recvfrom(self.bufferSize)
        return msgFromServer[0]