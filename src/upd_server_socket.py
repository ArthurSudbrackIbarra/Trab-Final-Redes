# -*- coding: utf-8 -*-

import socket

class CustomUDPServerSocket:
    def __init__(self, localIP, localPort, bufferSize):
        self.localIP = localIP
        self.localPort = localPort
        self.bufferSize = bufferSize

        self.UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.UDPServerSocket.bind((localIP, localPort))

    def listen(self, message):
        while(True):
            bytesToSend = str.encode(message)
            bytesAddressPair = self.UDPServerSocket.recvfrom(self.bufferSize)
            receivedMessage = bytesAddressPair[0]
            print("Mensagem recebida: " + receivedMessage)
            address = bytesAddressPair[1]
            self.UDPServerSocket.sendto(bytesToSend, address)
