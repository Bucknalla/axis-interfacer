class InterfaceObj(object):
    def __init__(self, module):
        self.version = "0.0.1"
        self.ports = module['ports']
        self.name = module['name']