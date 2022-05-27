# -*- coding: utf-8 -*-
import os

# Interpreta o arquivo de configuração.


class ConfigInterpreter:
    def __init__(self,
                 filePath: str):
        self.filePath = filePath

    def config(self) -> dict[str, ]:
        absoluteFilePath = os.path.abspath(self.filePath)
        configFile = open(absoluteFilePath, 'r')
        lines = configFile.readlines()
        configFile.close()
        # Construindo dicionário:
        splitted = lines[0].strip().split(":")
        return {
            "nextMachineIP": splitted[0],
            "nextMachinePort": splitted[1],
            "nickname": lines[1].strip(),
            "tokenTime": int(lines[2].strip()),
            "isTokenTrue": True if lines[3].strip() == "true" else False
        }
