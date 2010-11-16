#!/usr/bin/env python3

from re import compile
from sys import argv

if __name__ == '__main__':
	def printout(level, name, data=None, opts=None):
		if opts:
			for opt in opts:
				name += " " + opt
		if data:
			print("%s<%s>%s</%s>" % ('\t' * level, name, data, name,))
		else:
			print("%s<%s>" % ('\t' * level, name,))
	
	try:
		fp = open(argv[1])
		lines = [line.rstrip() for line in fp.readlines()]
		fp.close()
	except:
		print("Please provide a valid file name.")
	
	NODES = []
	LEVEL = compile(r'^\t*')
	PARSE = False
	
	for line in lines:
		if not PARSE:
			if line.startswith('<?'):
				print(line)
				PARSE = True
		elif len(line.strip()) > 0:
			level = len(LEVEL.match(line).group())
			if level < len(NODES):
				while len(NODES) > level:
					oname = NODES.pop()
					printout(len(NODES), '/' + oname)

			if line.strip().startswith('#'):
				print(('\t' * level) + '<!--',line.strip(),'-->')
			else:
				name, data, opts = None, None, None
				parts = line.strip().split('\t')
				if len(parts) > 1:
					data = parts[1].strip()
				name = parts[0].strip()
				parts = name.split(',')
				if len(parts) > 1:
					name = parts[0].strip()
					opts = parts[1:]
				if not data:
					NODES.append(name)
					
				printout(level, name, data, opts)
			
	while len(NODES) > 0:
		oname = NODES.pop()
		printout(len(NODES), '/' + oname)
	