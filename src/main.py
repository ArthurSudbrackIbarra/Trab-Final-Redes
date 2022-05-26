# -*- coding: utf-8 -*-

from config_interpreter import ConfigInterpreter
from custom_udp_client_socket import CustomUDPClientSocket
from custom_udp_server_socket import CustomUDPServerSocket
from socket_thread_manager import SocketThreadManager

def main():
    # Interpretando o arquivo de configuração.
    configInterpreter = ConfigInterpreter("config/config-2.txt")
    config = configInterpreter.config()
    print(config["nextMachineIP"])
    print(config["nextMachinePort"])
    print(config["nickname"])
    print(config["tokenTime"])
    print(config["isTokenTrue"])

    # Instanciando sockets.
    client = CustomUDPClientSocket("127.0.0.1", 9000, 1024)
    server = CustomUDPServerSocket("127.0.0.1", 9000, 1024)

    # Testando threads.
    # threadManager = SocketThreadManager(client, server)
    # threadManager.startThreads()


if __name__ == "__main__":
    main()