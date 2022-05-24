# -*- coding: utf-8 -*-

from config_interpreter import ConfigInterpreter

def main():
    configInterpreter = ConfigInterpreter("config/config-2.txt")
    nextMachineIP = configInterpreter.getNextMachineIP()
    nextMachinePort = configInterpreter.getNextMachinePort()
    nickname = configInterpreter.getNickname()
    tokenTime = configInterpreter.getTokenTime()
    isTokenTrue = configInterpreter.getIsTokenTrue()
    print(nextMachineIP)
    print(nextMachinePort)
    print(nickname)
    print(tokenTime)
    print(isTokenTrue)

if __name__ == "__main__":
    main()