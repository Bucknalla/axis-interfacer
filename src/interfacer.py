from __future__ import absolute_import
from __future__ import print_function
import sys
import os
from optparse import OptionParser
import json

# the next line can be removed after installation
# sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pyverilog.dataflow.dataflow_analyzer import VerilogDataflowAnalyzer
import pyverilog.utils.op2mark as op2mark

def inSet(direction):
    if 'Input' in direction:
        return 'input'
    if 'Output' in direction:
        return 'output'

def convert(s): 
    new = "(" 
    for x in s: 
        new += str(x)  
    new += ")"
    return new 

def dive(node, path, params):
    if hasattr(node,'nextnodes'):
        temp = []
        for i,each in enumerate(node.nextnodes):
            if hasattr(node,'operator') & i == 1:
                temp.append(op2mark.op2mark(node.operator))
            dive(each,temp,params)
        path.append(convert(temp))
    else:
        if hasattr(node,'name'):
            # print(node.name)
            if node.name in params:
                path.append(params[node.name])
        if hasattr(node,'value'):
            path.append(int(node.value))

def evaluate(value,params):
    try:
        return int(eval(value))
    except:
        try:
            return int(value.value)
        except:
            try:
                return int(value)
            except:
                print("ERROR")

def main():
    INFO = "Verilog module signal/module dataflow analyzer"
    USAGE = "Usage: python example_dataflow_analyzer.py -t TOPMODULE file ..."

    def showVersion():
        print(INFO)
        print(USAGE)
        sys.exit()
    
    optparser = OptionParser()
    optparser.add_option("-v","--version",action="store_true",dest="showversion",
                         default=False,help="Show the version")
    optparser.add_option("-I","--include",dest="include",action="append",
                         default=[],help="Include path")
    optparser.add_option("-D",dest="define",action="append",
                         default=[],help="Macro Definition")
    optparser.add_option("-t","--top",dest="topmodule",
                         default="TOP",help="Top module, Default=TOP")
    optparser.add_option("--nobind",action="store_true",dest="nobind",
                         default=False,help="No binding traversal, Default=False")
    optparser.add_option("-o","--output",dest="output",
                         default=".",help="Output Directory")
    (options, args) = optparser.parse_args()

    filelist = args
    print(filelist)
    if options.showversion:
        showVersion()

    for f in filelist:
        if not os.path.exists(f): raise IOError("file not found: " + f)

    analyzer = VerilogDataflowAnalyzer(filelist, options.topmodule,
                                       noreorder=False,
                                       nobind=options.nobind,
                                       preprocess_include=options.include,
                                       preprocess_define=options.define)
    analyzer.generate()

    module_dict = {}
    module_dict['name'] = options.topmodule
    module_dict['ports'] = {}

    instances = analyzer.getInstances()
    print('Instance:')
    terms = analyzer.getTerms()
    params = {}
    for tk,tv in terms.items():
        scope = tv.getScope(tv.name)
        # Reject non-topmodule params
        if ('Parameter' in tv.termtype) & tv.isTopmodule(scope):
            params[tv.name] = None
    binddict = analyzer.getBinddict()
    for bk, bv in binddict.items():
        for bvi in bv:
            if bvi.dest in params:
                params[bvi.dest] = bvi.tree
    print("PARAMS:",params)
    for tk, tv in terms.items():
        scope = tv.getScope(tv.name)
        if ('Input' in tv.termtype or 'Output' in tv.termtype) & tv.isTopmodule(scope):
            path = []
            dive(tv.msb,path,params)
            msb = evaluate(path[0],params)
            path = []
            dive(tv.lsb,path,params)
            lsb = evaluate(path[0],params)
            name = str(tv.name).split('.')[-1]
            direction = inSet(tv.termtype)
            port = {
                'msb'  : msb,
                'lsb'  : lsb,
                'direction' : direction
                }
            module_dict['ports'][name] = port
    print(json.dumps(module_dict))
    # json.dumps(module_dict, sort_keys=True, indent=4)

if __name__ == '__main__':
    main()
