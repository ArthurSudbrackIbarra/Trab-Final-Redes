# -*- coding: utf-8 -*-

class Machine: # Ou só uma queue?
    def __init__(self, name):
        self.name = name,
        self.queue = []

    def getName(self):
        return self.name