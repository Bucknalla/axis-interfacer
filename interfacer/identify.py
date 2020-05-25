import sys
import os
from optparse import OptionParser
import json
from pyverilog.dataflow.dataflow_analyzer import VerilogDataflowAnalyzer
import pyverilog.utils.op2mark as op2mark
import interfacer.module as mod
import interfacer.generate as gen
import interfacer.utils as util

class Identify(object):
	def __init__(self):
		self.log = util.log(self.__class__.__name__, enable=True, testing=True)
		self.version = "0.0.1"
		self.top = None
		self.filelist = []

	def __inSet(self, direction):
		if 'Input' in direction:
			return('input')
		if 'Output' in direction:
			return('output')

	def __convert(self,s): 
		new = "(" 
		for x in s: 
			new += str(x)  
		new += ")"
		return new 

	def __dive(self, node, path, params):
		if hasattr(node,'nextnodes'):
			temp = []
			for i,each in enumerate(node.nextnodes):
					if hasattr(node,'operator') & i == 1:
						temp.append(op2mark.op2mark(node.operator))
					self.__dive(each,temp,params)
			path.append(self.__convert(temp))
		else:
			if hasattr(node,'name'):
					# print(node.name)
					if node.name in params:
						path.append(params[node.name])
			if hasattr(node,'value'):
					path.append(int(node.value))

	def __evaluate(self, value, params):
		try:
			return int(eval(value))
		except:
			try:
					return int(value.value)
			except:
					try:
						return int(value)
					except:
						self.log.logger.error('Invalid value.')

	def load(self,obj):
		if isinstance(obj, mod.Module):
			self.top = obj.name
			self.filelist = obj.files
			self.blackboxes = obj.blackboxes
		else:
			raise ValueError('Not a valid object')

		for f in self.filelist:
			if not os.path.exists(f): raise IOError("file not found: " + f)

		analyzer = VerilogDataflowAnalyzer(self.filelist, self.top,
													noreorder=False,
													nobind=False,
													preprocess_include=[],
													preprocess_define=[])
		analyzer.generate()
		module_dict = {}
		module_dict['name'] = self.top
		module_dict['ports'] = {}

		instances = analyzer.getInstances()
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
		for tk, tv in terms.items():
			scope = tv.getScope(tv.name)
			if ('Input' in tv.termtype or 'Output' in tv.termtype) & (str(scope) in self.blackboxes):
				path = []
				self.__dive(tv.msb,path,params)
				msb = self.__evaluate(path[0],params)
				path = []
				self.__dive(tv.lsb,path,params)
				lsb = self.__evaluate(path[0],params)
				name = str(tv.name).split('.')[-1]
				direction = self.__inSet(tv.termtype)
				port = {
					'msb'  : msb,
					'lsb'  : lsb,
					'direction' : direction
					}
				module_dict['ports'][name] = port
		obj.update(module_dict)

if __name__ == '__main__':
	obj = mod.Module(top="blinky_zybo_z7",files=["../examples/rtl/top.v","../examples/rtl/blink.v"], blackboxes=['blinky_zybo_z7'])

	obj.add_mode('mode_a',["../examples/rtl/top_0.v","../examples/rtl/blink.v"],"../examples/rtl/zybo.xdc")
	obj.add_mode('mode_b',["../examples/rtl/top_1.v","../examples/rtl/blink.v"],"../examples/rtl/zybo.xdc")

	obj.list_modes()

	# print(dir(obj))

	iden = Identify()
	iden.load(obj)

	gen = gen.Generate()
	gen.load(obj)
	# gen.wrapper(xilinx_pragmas=False)
	gen.blackbox()
	gen.write("../examples/out")