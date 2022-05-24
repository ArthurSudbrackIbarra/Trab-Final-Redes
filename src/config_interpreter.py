# -*- coding: utf-8 -*-
import os

# Interpreta o arquivo de configuração.
class ConfigInterpreter:
    def __init__(self, filePath):
        absoluteFilePath = os.path.abspath(filePath)
        configFile = open(absoluteFilePath, 'r')
        lines = configFile.readlines()
        count = 0
        for line in lines:
            content = line.strip()
            if count == 0:
                splitted = content.split(":")
                self.nextMachineIP = splitted[0]
                self.nextMachinePort = splitted[1]
            elif count == 1:
                self.nickname = content
            elif count == 2:
                self.tokenTime = int(content)
            elif count == 3:
                if content == "true":
                    self.isTokenTrue = True
                else:
                    self.isTokenTrue = False
            count += 1

    def getNextMachineIP(self):
        return self.nextMachineIP

    def getNextMachinePort(self):
        return self.nextMachinePort

    def getNickname(self):
        return self.nickname

    def getTokenTime(self):
        return self.tokenTime

    def getIsTokenTrue(self):
        return self.isTokenTrue