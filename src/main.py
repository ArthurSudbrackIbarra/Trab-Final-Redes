# -*- coding: utf-8 -*-

from machine import Machine

def main():
    machine = Machine("Bob")
    name = machine.getName()
    print(name)

if __name__ == "__main__":
    main()