#!/usr/bin/env python3

from distutils.core import setup
setup(name='indent2xml',
	  version='0.5',
	  description='Convert tab-delimited file into a parent-child xml file.',
	  author='Nathan Middleton',
	  author_email='nathan.middleton@gmail.com',
	  py_modules=['indent2xml'],
	  data_files=[('bin','indent2xml')]
	 )
