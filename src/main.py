# -*- coding: utf-8 -*-

from config_interpreter import ConfigInterpreter

def main():
    confInt = ConfigInterpreter("config/config-2.txt")
    print(confInt.nextMachineIP)
    print(confInt.nextMachinePort)
    print(confInt.nickname)
    print(confInt.tokenTime)
    print(confInt.isTokenTrue)

if __name__ == "__main__":
    main()