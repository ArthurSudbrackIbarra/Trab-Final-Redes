# -*- coding: utf-8 -*-
import os

# Interpreta o arquivo de configuração.
class ConfigInterpreter:
    def __init__(self, filePath):
        absoluteFilePath = os.path.abspath(filePath)
        configFile = open(absoluteFilePath, 'r')
        lines = configFile.readlines()
        # Machine IP
        splitted = lines[0].strip().split(":")
        self.nextMachineIP = splitted[0]
        self.nextMachinePort = splitted[1]
        # Nickname
        self.nickname = lines[1].strip();
        # Token Time
        self.tokenTime = int(lines[2].strip())
        # Is Token True
        self.isTokenTrue = True if lines[3].strip() == "true" else False