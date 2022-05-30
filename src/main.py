# -*- coding: utf-8 -*-

from file_interpreters import ConfigInterpreter
from custom_sockets import UDPClientSocket, UDPServerSocket
from thread_managers import SocketThreadManager
from packaging import ErrorControlTypes, TokenPacket, DataPacket, CRC32


def main() -> None:
    # Interpretando o arquivo de configuração.
    configInterpreter = ConfigInterpreter("config/config-2.txt")
    config = configInterpreter.config()
    print("\n[Arquivo de configuração]\n")
    print(f"IP da máquina à direita: {config['nextMachineIP']}")
    print(f"Porta da máquina à direita: {config['nextMachinePort']}")
    print(f"Apelido da máquina atual: {config['nickname']}")
    print(f"Tempo do token: {config['tokenTime']}")
    print(f"Deve gerar token: {config['isTokenTrue']}")

    # Instanciando sockets.
    client = UDPClientSocket("127.0.0.1", 9000, 1024)
    server = UDPServerSocket("127.0.0.1", 9000, 1024)

    # Testando criação de pacotes.
    dataPacket_1 = DataPacket(ErrorControlTypes.ACK,
                              "Maria", "Bob", 2636827734, "Hello!")
    dataPacket_2 = DataPacket.fromString("2222;NACK:Carlos:Gaspar:3000:Sushi!")
    tokenPacket = TokenPacket()
    print(f"\nPacote Token: {tokenPacket.toString()}")
    print(f"Pacote Dados 1: {dataPacket_1.toString()}")
    print(f"Pacote Dados 2: {dataPacket_2.toString()}")

    # Testando CRC32.
    crc_1 = CRC32.calculate(dataPacket_1.message)
    crc_2 = CRC32.calculate(dataPacket_2.message)
    check_1 = CRC32.check(dataPacket_1)
    check_2 = CRC32.check(dataPacket_2)
    print(f"\nCRC do pacote de dados 1: {crc_1}")
    print(f"CRC do pacote 1 bate? {check_1}")
    print(f"CRC do pacote de dados 2: {crc_2}")
    print(f"CRC do pacote 2 bate? {check_2}\n")

    # Testando threads.
    threadManager = SocketThreadManager(config, client, server)
    threadManager.startThreads()


if __name__ == "__main__":
    main()
