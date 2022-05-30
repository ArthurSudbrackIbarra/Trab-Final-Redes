# -*- coding: utf-8 -*-

import os


# Classes de configuração.

class Configuration:
    def __init__(self,
                 nextMachineIP: str,
                 nextMachinePort: int,
                 nickname: str,
                 tokenTime: int,
                 isTokenTrue: bool):
        self.nextMachineIP = nextMachineIP
        self.nextMachinePort = nextMachinePort
        self.nickname = nickname
        self.tokenTime = tokenTime
        self.isTokenTrue = isTokenTrue


class ConfigInterpreter:
    def __init__(self,
                 filePath: str):
        self.filePath = filePath

    def config(self) -> Configuration:
        absoluteFilePath = os.path.abspath(self.filePath)
        configFile = open(absoluteFilePath, 'r')
        lines = configFile.readlines()
        configFile.close()
        splitted = lines[0].strip().split(":")
        configuration = Configuration(
            nextMachineIP=splitted[0],
            nextMachinePort=int(splitted[1]),
            nickname=lines[1].strip(),
            tokenTime=int(lines[2].strip()),
            isTokenTrue=True if lines[3].strip() == "true" else False
        )
        return configuration
