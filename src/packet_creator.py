# -*- coding: utf-8 -*-

import enum

class ErrorControlTypes(enum.Enum):
    MACHINE_DOES_NOT_EXIST = "maquinanaoexiste"
    ACK = "ACK"
    NACK = "NACK"

class PacketCreator:
    def __init__(self) -> None:
        pass

    def createTokenPacket(self):
        return "1111"

    def createDataPacket(self, errorControlType, originNickname, destinationNickname, crc, message):
        return f"2222;{errorControlType.value}:{originNickname}:{destinationNickname}:{crc}:{message}"