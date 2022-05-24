# -*- coding: utf-8 -*-

from config_interpreter import ConfigInterpreter

def main():
    configInterpreter = ConfigInterpreter("config/config-2.txt")
    nextMachineIP = configInterpreter.getNextMachineIP()
    nextMachinePort = configInterpreter.getNextMachinePort()
    print(nextMachineIP)
    print(nextMachinePort)

if __name__ == "__main__":
    main()