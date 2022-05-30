# -*- coding: utf-8 -*-

from file_interpreters import ConfigInterpreter
from thread_managers import SocketThreadManager


def main() -> None:
    # Interpretando o arquivo de configuração.
    configInterpreter = ConfigInterpreter("src/config/config-2.txt")
    config = configInterpreter.config()
    print("\n[Arquivo de configuração]\n")
    print(f"IP da máquina à direita: {config['nextMachineIP']}")
    print(f"Porta da máquina à direita: {config['nextMachinePort']}")
    print(f"Apelido da máquina atual: {config['nickname']}")
    print(f"Tempo do token: {config['tokenTime']}")
    print(f"Deve gerar token: {config['isTokenTrue']}")

    # Iniciando threads.
    threadManager = SocketThreadManager(config)
    threadManager.startThreads()


if __name__ == "__main__":
    main()
