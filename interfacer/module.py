import interfacer.utils as util
import subprocess
from lxml import etree
import re

class Module(object):
    def __init__(self, top, files, blackboxes=None, ipcores=None, part='xc7z020-clg400', vivado=None):
        self.log = util.log(self.__class__.__name__, enable=True, testing=True)
        self.version = "0.0.1"
        self.ports = None
        self.part = part
        self.name = top
        self.interface = None
        if ipcores:
            self.log.logger.info('Determining Vivado version used in IP cores...')
            self.vivado = {'version' : self.__read_vivado_version(ipcores)}
            if not vivado:
                self.vivado['cmd'] = '/opt/Xilinx/Vivado/{}/bin/vivado'.format(self.vivado['version'])
            else:
                self.vivado['cmd'] = vivado
            if not self.__check_vivado_version(self.vivado['version']):
                self.log.logger.error('Vivado version does not match IP core')
                raise ValueError
            self.ipcores = ipcores
            self.log.logger.info('Unpacking .xci files')            
            self.__unpack_ipcores(ipcores)
        if not blackboxes:
            self.blackboxes = top
            self.log.logger.info('Blackbox added: {}'.format(self.blackboxes))
        else:
            self.log.logger.info('Blackboxes added: {}'.format(', '.join(str(n) for n in blackboxes)))
            self.blackboxes = blackboxes
        if isinstance(files, list):
            self.files = files
        else:
            raise ValueError('Requires list of files')
        self.modes = {}

    def __read_vivado_version(self, ipcores):
        version = None
        for xci in ipcores:
            print(xci)
            doc = etree.parse(xci)
            xci_version = doc.find('spirit:configurableElementValue')
            if (version != None) and (version != xci_version):
                self.log.logger.error('Vivado IP Core version mismatch!')
                raise ValueError
            else:
                version = xci_version
        return version

    def __check_vivado_version(self, version):
        p = subprocess.Popen('{} -version | grep Vivado'.format(self.vivado), stdout=subprocess.PIPE, shell=True)
        version,_ = p.communicate()
        if re.search(r'(\d+\.)(\d)', version) == version:
            return True
        else:
            return False


    def __unpack_ipcores(self, ipcores):
        self.log.logger.debug('Verifying Vivado installation...')   
        pass

    def update(self, modules):
        self.ports = modules['ports']

    def add_mode(self, name, files, constraint, ipcores=None):
        if name in self.modes:
            raise ValueError('Mode already exists.')
        if ipcores:
            self.log.logger.info('Determining Vivado version used in IP cores...')
            self.vivado = {'version' : self.__read_vivado_version(ipcores)}
            # self.ipcores = ipcores
            self.log.logger.info('Unpacking .xci files')            
            self.__unpack_ipcores(ipcores)
        self.modes[name] = {'files':files, 'xdc':[constraint], 'ipcores':[ipcores]}

    def remove_mode(self, name, files, constraint):
        self.modes.pop(name, None)

    def list_modes(self):
        for mode in self.modes:
            self.log.logger.info('{}:{}'.format(mode,self.modes[mode]['files']))