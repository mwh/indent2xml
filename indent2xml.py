#!/usr/bin/env python3
"""
indent2xml.py a python module to convert tab-indent structures to xml.
Copyright (C) 2010 Nathan Middleton

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
import re

class ParseError(Exception):
	"""
	ParseError: Raised during parsing when a line does not match
	any known patterns.
	"""
	WS_TABLE = {' ':'<spc>', '\t':'<tab>', '\n':'<nln>', '\r':'<rtn>', '\f':'<frm>', '\v':'<vtb>'}
	
	def __init__(self, lineno, str):
		self._lineno = lineno
		self._str = str
		
	def __str__(self):
		ws_match = re.match(r'^(\s+)', self._str)
		ws_str = ''.join([self.WS_TABLE[ws] for ws in ws_match.group()]) if ws_match else ''
		return "ParseError at line {} '{}{}'".format(self._lineno, ws_str, self._str.strip())

def parse(file=None, quiet=False, debug=False):
	if debug:
		from sys import stderr
		def out(*items):
			print(items, file=stderr)
		
	if file:
		try:
			fp = open(file, 'r')
			indent_lines = [line.rstrip() for line in fp.readlines()]
			indent_length = len(indent_lines)
			fp.close()
		except:
			raise IOError('There was an error reading the file {}.'.format(file))
		
		# regular expressions used for line matching
		re_comment = re.compile(r'^(\s*)#(\s*)(.*)')					# comments
		re_xml = re.compile(r'^<\?')									# <?xml ...?> lines
		re_node = re.compile(r'^(\t+)?([_a-zA-Z]+)\,?([^\t]+)?\t?(.*)')	# valid node declarations
		re_blank = re.compile(r'^\s*$')									# empty lines

		xml_lines = [] # parsed lines
		open_tags = [] # tags with children will be added to this stack.

		def current_indent():
			""" return the current indent level """
			return len(open_tags)

		def open_tag(match):
			""" return a opening tag string for parsed line """
			indent = match[0] if match[0] else ''
			name = match[1]
			options = (' ' + ' '.join(match[2].split(','))) if match[2] else ''
			content = match[3].strip()
			
			if content:
				tag = "{}<{}{}>{}</{}>".format(indent, name, options, content, name)
			else:
				tag = "{}<{}{}>".format(indent, name, options)
				open_tags.append((name, indent,))
				for i in range((ptr + 1), indent_length):
					node_match = re_node.match(indent_lines[i])
					if node_match:
						node_indent = len(node_match.groups()[0]) if node_match.groups()[0] else 0
						if node_indent <= len(indent):
							tag = "{}<{}{}/>".format(indent, name, options)
							open_tags.pop()
						break

			return (content, name, tag,)

		def close_tag():
			""" close the top tag on open_tags stack. """
			name, indent = open_tags.pop()
			xml_lines.append("{}</{}>".format(indent, name))
			return xml_lines[-1]

		for ptr in range(0, indent_length):
			# try each regular expression until a match is found, or none.
			# we should have filtered out empty lines already so significant
			# lines should be all that is left.
			#
			# unmatched lines will raise ParseError.
			try:
				match = re_blank.match(indent_lines[ptr])
				if match:
					# skip over blanks
					continue
					
				match = re_node.match(indent_lines[ptr])
				if match:
					# node matches will continue 4 fields:
					#	1. all tabs from start of line to first non-tab character.
					#	   len(match.groups()[0]) should give level of node entry.
					#	2. name of tag.
					#	3. tag options.
					#	   ' '.join(match.groups()[2].split(',')) should return a
					#	   string appropriate for putting in the first tag of a
					#	   node.
					#	4. any content the tag should contain between its opening
					#	   and closing tags.
					tag_indent = len(match.groups()[0]) if match.groups()[0] else 0
					if debug: out(match.groups(), current_indent(), open_tags)
					while tag_indent < current_indent(): close_tag()
					closed, name, tag = open_tag(match.groups())
					xml_lines.append(tag)
					continue
								
				match = re_comment.match(indent_lines[ptr])
				if match:
					# comment found. do nothing fancy, just append it as an
					# xml comment.
					indent, spacing, comment = match.groups()
					xml_lines.append("{}<!--{}{}{}-->".format(indent, spacing, comment, spacing))
					continue
					
				match = re_xml.match(indent_lines[ptr])
				if match:
					# xml line found (i.e. <?xml ...?>), prepend to lines
					xml_lines.reverse()
					xml_lines.append(indent_lines[ptr])
					xml_lines.reverse()
					continue
					
				# If no match is found, then a parse error has occurred.
				raise ParseError((ptr + 1), indent_lines[ptr])
			except ParseError as error:
				from sys import stderr,exit
				if not quiet:
					print(error, file=stderr)
					exit(1)
				
				
		# close any remaining open tags.
		while len(open_tags) > 0: close_tag()

		# return a stringified version of xml_lines stack.				
		return '\n'.join(xml_lines)
	else:
		raise ValueError('No filename provided to parse.')

if __name__ == '__main__':
	filename = 'data/testfile.struct'
	xml = parse(filename)
	print(xml)
