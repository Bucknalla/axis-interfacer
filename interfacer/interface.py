import json
import pkgutil
import re
import interfacer.module as mod
import interfacer.utils as util

class Interface(object):
    def __init__(self, obj=None):
        self.log = util.log(self.__class__.__name__, enable=True, testing=True)
        self.protocols = json.loads(pkgutil.get_data(__name__, 'protocols/protocol.json'))
        self.protocol_classification = iter(self.__loadProtocols())
        self.protocol_match = []
        self.matched_interfaces = []
        if obj:
            self.verifyInterface(obj)


    def __requirePorts(self, protocol):
        require = set()
        for interface, interface_params in self.protocols['PROTOCOLS'][protocol['standard']][protocol['name']]['INFO']['INTERFACE'].items():
            if interface_params['REQUIRED']:
                require.add(interface)
        return require

    def __loadProtocols(self):
        classification = []
        for family in self.protocols['PROTOCOLS']:
            for name in self.protocols['PROTOCOLS'][family]:
                classification.append({'standard':family,'name':name})
        return classification

    def loadInterface(self, custom=None):
        if custom:
            self.protocols = json.loads(custom)
        else:
            self.protocols = json.loads(pkgutil.get_data(__name__, 'protocols/protocol.json'))
        self.protocol_classification = iter(self.__loadProtocols())

    def pragma(self, interface, options=None):
        classification = list(self.__loadProtocols())
        actual = [match[0] for match in self.matched_interfaces]
        official = [match[1] for match in self.matched_interfaces]
        try:
            official[actual.index(interface)]
        except ValueError as v:
            self.log.logger.warning('{} of ports.'.format(v))
            return None
        else:
            for each in classification:
                if official[actual.index(interface)] in self.protocols['PROTOCOLS'][each['standard']][each['name']]['INFO']['INTERFACE']:
                    if options:
                        return(self.protocols['PROTOCOLS'][each['standard']][each['name']]['PARAMETERS']['PRAGMA'].format(*options))
                    else:
                        # print("TC:",self.protocols['PROTOCOLS'][each['standard']][each['name']]['INFO']['PRAGMA'].format(interface,official[actual.index(interface)]))
                        return(self.protocols['PROTOCOLS'][each['standard']][each['name']]['INFO']['PRAGMA'].format(interface,official[actual.index(interface)]))
                # else:
                    # print("No match for {} in {}".format(interface,each))

    def verifyInterface(self, port_list, protocol=None):
        if not port_list:
            return True
        match_list = []
        if protocol == None:
            self.log.logger.info('Verifying port list.')
            protocol = next(self.protocol_classification)
        required = self.__requirePorts(protocol)
        for interface, interface_params in self.protocols['PROTOCOLS'][protocol['standard']][protocol['name']]['INFO']['INTERFACE'].items():
            self.__match([interface,interface_params], port_list, match_list)
        check_req = [match[1] for match in match_list]
        if self.__verify(required, check_req):
            self.log.logger.info('Verified a {} {} protocol'.format(protocol['standard'],protocol['name']))
            self.matched_interfaces += match_list
            self.protocol_match.append(protocol)
            port_list = list(set(port_list)-set([match[0] for match in self.matched_interfaces]))
        try:
            next_protocol = next(self.protocol_classification)
        except:
            self.log.logger.info('Verifying protocols complete.')
            self.protocol_classification = iter(self.__loadProtocols())
            return
        self.verifyInterface(port_list, next_protocol)


    def __verify(self, required, match_list):
        required, match_list = set(required), set(match_list)
        # print("VERIFY REQ:",required)
        # print("VERIFY MAT:", match_list)
        return (required.issubset(match_list) and (match_list))
        
    def __match(self, interface, compare, match_list):
        regex = [interface[0]]
        if 'ALTERNATIVES' in interface[1]:
            for alt in interface[1]['ALTERNATIVES']:
                regex.append(alt)
        for each in compare:
            for reg in regex:
                if re.search(reg, each, re.IGNORECASE):
                    self.log.logger.info("Matched {0} to {1}".format(each,regex[0]))
                    match_list.append([each, regex[0]])
                    break
        if not match_list: 
            return False
        else:
            return True
                

    def listInterfaces(self):
        return self.protocol_match

if __name__ == '__main__':
    obj = mod.Module(top="blinky_zybo_z7",files=["../examples/rtl/top.v","../examples/rtl/blink.v"], blackboxes=['blinky_zybo_z7'])

    obj.add_mode('mode_a',["../examples/rtl/top_0.v","../examples/rtl/blink.v"],"../examples/rtl/zybo.xdc")
    obj.add_mode('mode_b',["../examples/rtl/top_1.v","../examples/rtl/blink.v"],"../examples/rtl/zybo.xdc")

    obj.list_modes()

    i = Interface()
    i.verifyInterface(obj.ports)