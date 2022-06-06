# -*- coding: utf-8 -*-

from __future__ import annotations
import enum
import zlib
import random


# Classe enum com os possíveis tipos de controle de erro.


class ErrorControlTypes(enum.Enum):
    MACHINE_DOES_NOT_EXIST = "maquinanaoexiste"
    ACK = "ACK"
    NAK = "NAK"


# Classe para representar um pacote de token.


class TokenPacket:
    CODE = "1111"

    def __init__(self):
        pass

    def toString(self) -> str:
        return f"{TokenPacket.CODE}"


# Classe para representar um pacote de dados.


class DataPacket:
    CODE = "2222"

    def __init__(self,
                 errorControlType: ErrorControlTypes,
                 originNickname: str,
                 destinationNickname: str,
                 crc: int,
                 message: str):
        self.errorControlType = errorControlType
        self.originNickname = originNickname
        self.destinationNickname = destinationNickname
        self.crc = crc
        self.message = message

    def toString(self) -> str:
        return f"{DataPacket.CODE};{self.errorControlType.value}:{self.originNickname}:{self.destinationNickname}:{self.crc}:{self.message}"

    @staticmethod
    def fromString(packet: str) -> DataPacket:
        if not packet.startswith(f"{DataPacket.CODE};") or len(packet) <= 5:
            return None
        relevantInfo = packet[5:len(packet)]
        splitted = relevantInfo.split(":")
        errorControlType = ErrorControlTypes(splitted[0])
        originNickname = splitted[1]
        destinationNickname = splitted[2]
        crc = int(splitted[3])
        message = splitted[4]
        return DataPacket(errorControlType, originNickname, destinationNickname, crc, message)


# Classe para identificar pacotes: token ou dados?


class PacketIdentifier:
    TOKEN = 1
    DATA = 2
    UNKNOWN = -1

    @staticmethod
    def identify(packet: str) -> int:
        if packet.startswith(TokenPacket.CODE):
            return PacketIdentifier.TOKEN
        elif packet.startswith(DataPacket.CODE):
            return PacketIdentifier.DATA
        return PacketIdentifier.UNKNOWN


# Classe para lidar com operações envolvendo CRC32.


class CRC32:
    @staticmethod
    def calculate(message: str) -> int:
        encodedBytes = str.encode(message)
        return zlib.crc32(encodedBytes)

    @staticmethod
    def check(packet: DataPacket) -> bool:
        return CRC32.calculate(packet.message) == packet.crc


# Classe para inserir falhas de propósito nos pacotes.


class PacketFaultInserter:
    def __init__(self,
                 percentage: float):
        self.percentage = percentage

    def tryInsert(self, packet: DataPacket) -> None:
        numberGenerated = random.random()
        if numberGenerated <= self.percentage / 100:
            packet.crc = -9999
