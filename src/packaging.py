# -*- coding: utf-8 -*-

from __future__ import annotations
import enum


class ErrorControlTypes(enum.Enum):
    MACHINE_DOES_NOT_EXIST = "maquinanaoexiste"
    ACK = "ACK"
    NACK = "NACK"


class TokenPacket:
    CODE = "1111"

    def __init__(self):
        pass

    def toString(self) -> str:
        return f"{TokenPacket.CODE}"


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
    def fromString(package: str) -> DataPacket:
        if not package.startswith(f"{DataPacket.CODE};") or len(package) <= 5:
            return None
        relevantInfo = package[5:len(package)]
        splitted = relevantInfo.split(":")
        errorControlType = ErrorControlTypes(splitted[0])
        originNickname = splitted[1]
        destinationNickname = splitted[2]
        crc = int(splitted[3])
        message = splitted[4]
        return DataPacket(errorControlType, originNickname, destinationNickname, crc, message)
