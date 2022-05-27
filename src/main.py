# -*- coding: utf-8 -*-

from file_interpreters import ConfigInterpreter
from custom_sockets import UDPClientSocket, UDPServerSocket
from thread_managers import SocketThreadManager
from packaging import ErrorControlTypes, DataPacket, TokenPacket


def main() -> None:
    # Interpretando o arquivo de configuração.
    configInterpreter = ConfigInterpreter("config/config-2.txt")
    config = configInterpreter.config()
    print(config["nextMachineIP"])
    print(config["nextMachinePort"])
    print(config["nickname"])
    print(config["tokenTime"])
    print(config["isTokenTrue"])

    # Instanciando sockets.
    client = UDPClientSocket("127.0.0.1", 9000, 1024)
    server = UDPServerSocket("127.0.0.1", 9000, 1024)

    # Testando threads.
    # threadManager = SocketThreadManager(client, server)
    # threadManager.startThreads()

    # Testando criação de pacotes.
    dataPacket_1 = DataPacket(ErrorControlTypes.ACK,
                              "Maria", "Bob", 1000, "Hello!")
    dataPacket_2 = DataPacket.fromString("2222;NACK:Carlos:Gaspar:3000:Sushi!")
    tokenPacket = TokenPacket()
    print(f"Pacote Token: {tokenPacket.toString()}")
    print(f"Pacote Dados 1: {dataPacket_1.toString()}")
    print(f"Pacote Dados 2: {dataPacket_2.toString()}")


if __name__ == "__main__":
    main()
