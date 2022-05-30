# -*- coding: utf-8 -*-

from configurations import ConfigInterpreter
from thread_managers import SocketThreadManager

import sys


def main() -> None:
    filePath = "config/config-1.txt"
    serverSocketPort = 9000
    if len(sys.argv) > 1:
        filePath = sys.argv[1]
        serverSocketPort = int(sys.argv[2])

    # Interpretando o arquivo de configuração.
    configInterpreter = ConfigInterpreter(filePath)
    config = configInterpreter.config()
    print("\n[Arquivo de configuração]\n")
    print(f"IP da máquina à direita: {config.nextMachineIP}")
    print(f"Porta da máquina à direita: {config.nextMachinePort}")
    print(f"Apelido da máquina atual: {config.nickname}")
    print(f"Tempo do token: {config.tokenTime}")
    print(f"Deve gerar token: {config.isTokenTrue}")

    # Iniciando threads.
    threadManager = SocketThreadManager(
        config=config, serverSocketPort=serverSocketPort)
    threadManager.startThreads()


if __name__ == "__main__":
    main()
