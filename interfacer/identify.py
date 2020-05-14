import sys
import os
from optparse import OptionParser
import json
from pyverilog.dataflow.dataflow_analyzer import VerilogDataflowAnalyzer
import pyverilog.utils.op2mark as op2mark
import util

class Identify(object):
	def __init__(self):
		self.version = "0.0.1"
		self.top = None
		self.filelist = []

	def __inSet__(self, direction):
		if 'Input' in direction:
			return('input')
		if 'Output' in direction:
			return('output')

	def __convert__(self,s): 
		new = "(" 
		for x in s: 
			new += str(x)  
		new += ")"
		return new 

	def __dive__(self, node, path, params):
		if hasattr(node,'nextnodes'):
			temp = []
			for i,each in enumerate(node.nextnodes):
					if hasattr(node,'operator') & i == 1:
						temp.append(op2mark.op2mark(node.operator))
					self.__dive__(each,temp,params)
			path.append(self.__convert__(temp))
		else:
			if hasattr(node,'name'):
					# print(node.name)
					if node.name in params:
						path.append(params[node.name])
			if hasattr(node,'value'):
					path.append(int(node.value))

	def __evaluate__(self, value, params):
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

	def load(self,top,files):

		self.top = top
		self.filelist = files

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
			if ('Input' in tv.termtype or 'Output' in tv.termtype) & tv.isTopmodule(scope):
				path = []
				self.__dive__(tv.msb,path,params)
				msb = self.__evaluate__(path[0],params)
				path = []
				self.__dive__(tv.lsb,path,params)
				lsb = self.__evaluate__(path[0],params)
				name = str(tv.name).split('.')[-1]
				direction = self.__inSet__(tv.termtype)
				port = {
					'msb'  : msb,
					'lsb'  : lsb,
					'direction' : direction
					}
				module_dict['ports'][name] = port
		print(json.dumps(module_dict,sort_keys=True, indent=4))

if __name__ == '__main__':
	 iden = Identify()
	 iden.load("blinky_zybo_z7",["examples/test.v","examples/mod.v"])
