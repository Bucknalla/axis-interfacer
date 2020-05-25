import sys
import os
import datetime
import json as j
import pyverilog.vparser.ast as vast
from pyverilog.ast_code_generator.codegen import ASTCodeGenerator
import interfacer.module as mod
import interfacer.interface as inter
import interfacer.utils as util
from jinja2 import Environment, PackageLoader, Template    

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class XilinxPragmaInput(vast.Value):
	attr_names = ('name', 'signed')

	def __init__(self, name, width=None, signed=False, dimensions=None, lineno=0):
		self.lineno = lineno
		self.name = name
		self.width = width
		self.signed = signed
		self.dimensions = dimensions

class XilinxPragmaOutput(vast.Value):
	attr_names = ('name', 'signed')

	def __init__(self, name, width=None, signed=False, dimensions=None, lineno=0):
		self.lineno = lineno
		self.name = name
		self.width = width
		self.signed = signed
		self.dimensions = dimensions

class Generate(object):
	def __init__(self, part='xc7z020-clg400'):
		self.log = util.log(self.__class__.__name__, enable=True, testing=True)
		self.module = {}
		self.wrapper_file = None
		self.blackbox_file = None
		self.part = part
		self.obj = None
		self.jinja_env = Environment(
			loader = PackageLoader(__package__,'templates'),
			trim_blocks = True,
			lstrip_blocks = True,
			keep_trailing_newline = True,
		)

	def __renderTemplate(self, template_file, target_file, template_vars = {}):
		template = self.jinja_env.get_template(template_file)
		with open(target_file, 'w') as f:
			f.write(template.render(template_vars))

	def load(self, obj):
		if isinstance(obj, mod.Module):
			self.obj = obj
			self.module['name'] = obj.name
			self.module['ports'] = obj.ports
		else:
			self.log.logger.error('Not a valid object')
			raise ValueError('Not a valid object')

	def write(self, output_file, tcl=True): 
		template_vars = {
			'module': self.module['name'],
			'file': None,
			'date': datetime.datetime.now().strftime("%H:%M %d/%m/%Y"),
			'content' : {},
		}  

		generated_files = []

		template_vars['file'] = output_file+"_blackbox.v"
		template_vars['content'] = self.blackbox_file
		if self.blackbox_file != None:
			self.log.logger.info('Generating {}'.format(output_file+"_blackbox.v"))
			self.__renderTemplate("base.j2",output_file+"_blackbox.v",template_vars)
			generated_files.append(output_file+"_blackbox.v")
		else:
			self.log.logger.error('Missing module blackbox')
			raise ValueError('Missing module blackbox')  

		template_vars['file'] = output_file+"_wrapper.v"
		template_vars['content'] = self.wrapper_file
		if self.wrapper_file != None:
			self.log.logger.info('Generating {}'.format(output_file+"_wrapper.v"))
			self.__renderTemplate("base.j2",output_file+"_wrapper.v",template_vars)
			generated_files.append(output_file+"_wrapper.v")

		if self.part != None:
			template_vars['file'] = output_file+"_generate.tcl"
			template_vars['content'] = {
				'part' : self.part,
				'file' : self.obj.files,
				'top'  : self.module['name'],
				'modes': self.obj.modes
			}
			self.log.logger.info('Generating {}'.format(output_file+"_generate.tcl"))
			self.__renderTemplate("generate.tcl.j2",output_file+"_generate.tcl",template_vars)
			generated_files.append(output_file+"_generate.tcl")
		
		return generated_files
	
	def tclScript(self):
		pass

	def blackbox(self):
		port_list = []
		for each in self.module['ports']:
			width = vast.Width( vast.IntConst(self.module['ports'][each]['msb']), vast.IntConst(self.module['ports'][each]['lsb']) )
			if self.module['ports'][each]['direction'] == 'input':
				port = vast.Input(each, width=width)
			else:
				port = vast.Output(each, width=width)
			port_list.append(vast.Ioport(port))
		params = vast.Paramlist([])
		ports = vast.Portlist(port_list)

		ast = vast.ModuleDef(self.module['name'], params, ports, [])
		
		codegen = ASTCodeGenerator()
		self.blackbox_file = codegen.visit(ast)

	def __replacePragma(self, replace_file, pragma_list):
		new_gen = ''
		index = 0
		for line in replace_file.splitlines():
			new_gen += (Template(line).render(xilinx_pragma=pragma_list[index]) + '\n')
			if ('{{ xilinx_pragma }}' in line ) and (index < (len(pragma_list) - 1)):
				index = index + 1
		return new_gen

	def wrapper(self,xilinx_pragmas=None):
		self.log.logger.info('Generating wrapper (Xilinx Pragmas: {})'.format(xilinx_pragmas))
		port_list = []
		black_list = []
		wire_list = []
		pragma_list = []
		i = inter.Interface(self.module['ports'])
		for each in self.module['ports']:
			self.log.logger.info('Port: {}'.format(each))
			port = None
			if (self.module['ports'][each]['msb'] - self.module['ports'][each]['lsb'] != 0):
				width = vast.Width( vast.IntConst(self.module['ports'][each]['msb']), vast.IntConst(self.module['ports'][each]['lsb']) )
			else:
				width = None
			arg = vast.PortArg(each,vast.Identifier(each))
			wire = vast.Wire(each+"_wire", width=width)
			wire_list.append(wire)
			valid = i.pragma(each)
			if valid:
				pragma_list.append(valid)
			if self.module['ports'][each]['direction'] == 'input':
				if (xilinx_pragmas and (valid)):
					port = XilinxPragmaInput(each, width=width)
					port.__class__.__name__ = ('{{ xilinx_pragma }}\ninput')
				else:
					port = vast.Input(each, width=width)
			else:
				if (xilinx_pragmas and (valid)):
					port = XilinxPragmaOutput(each, width=width)
					port.__class__.__name__ = ('{{ xilinx_pragma }}\noutput')
				else:
					port = vast.Output(each, width=width)

			port_list.append(vast.Ioport(port,vast.Wire(each)))
			black_list.append(arg)
			valid = None

		params = vast.Paramlist([])
		ports = vast.Portlist( port_list )

		blackbox = vast.Instance(self.module['name'], 'blackbox', black_list, params,array=None)
		blackbox_list = vast.InstanceList(self.module['name'],[],[blackbox] )

		items = []
		# items.append(pragma_list)
		items.append(blackbox_list)

		ast = vast.ModuleDef(self.module['name']+"_wrapper", params, ports, items)
		
		codegen = ASTCodeGenerator()
		if xilinx_pragmas and (len(pragma_list) > 0):
			self.log.logger.info('Inserting {} Xilinx Pragmas'.format(len(pragma_list)))
			self.wrapper_file = self.__replacePragma(codegen.visit(ast), pragma_list)
		else:
			self.wrapper_file = codegen.visit(ast)
		
		
if __name__ == '__main__':
	gen = Generate()
	gen.load("examples/test.json")
	gen.wrapper()
	gen.blackbox()
	gen.write("examples/output_thingy")