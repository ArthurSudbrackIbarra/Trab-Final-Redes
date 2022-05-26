# -*- coding: utf-8 -*-

import socket

class CustomUDPServerSocket:
    def __init__(self, localIP, localPort, bufferSize):
        self.localIP = localIP
        self.localPort = localPort
        self.bufferSize = bufferSize
        self.udpServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.udpServerSocket.bind((localIP, localPort))

    def listen(self, message):
        while(True):
            bytesToSend = str.encode(message)
            bytesAddressPair = self.udpServerSocket.recvfrom(self.bufferSize)
            receivedMessage = bytesAddressPair[0]
            print("Message from Client: {}".format(receivedMessage))
            address = bytesAddressPair[1]
            self.udpServerSocket.sendto(bytesToSend, address)
