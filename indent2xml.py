#!/usr/bin/env python3

from re import compile


re_comment = compile(r'^(\s+)?#')
re_xml = compile(r'^<\?')
re_node = compile(r'^(\t+)?([_a-zA-Z]+)\,?([^\t]+)?\t?(.*)')

xml_lines = [] # parsed lines

def parse(file=None, debug=False):
	if debug:
		from sys import stderr
		def out(*items):
			print(items, file=stderr)
		
	if file:
		try:
			fp = open(file, 'r')
			indent_lines = [line.rstrip() for line in fp.readlines() if len(line.strip()) > 0]
			fp.close()
		except:
			raise Exception('Unable to read file.')
		
		open_tags = [] # tags with children will be added to this stack.
		
		#
		def current_indent():
			return len(open_tags)

		# create text from parsed line
		def open_tag(match):
			tag = []
			indent, name, options, content = match[0], match[1], match[2], match[3].strip()
			if indent:
				tag.append(indent)
			tag.append('<')
			tag.append(name)
			if options:
				tag.append(' ')
				tag.append(' '.join(options.split(',')))
			tag.append('>')
			if len(content) > 0:
				tag.append(content)
				tag.append("</%s>" % (name,))
			else:
				open_tags.append(name)
			return (content, name, ''.join(tag),)

		# remove top tag from open_tags stack and return a text version
		def close_tag(indent):
			name = open_tags.pop()
			xml_lines.append("%s</%s>" % ('\t' * indent, name,))
			return xml_lines[-1]

		for line in indent_lines:
			# try each regular expression until a match is found, or none.
			# we should have filtered out empty lines already so significant
			# lines should be all that is left.
			match = re_node.match(line)
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
				tag_indent = match.groups()[0] and len(match.groups()[0]) or 0
				if debug: out(match.groups(), current_indent(), open_tags)
				while tag_indent < current_indent():
					close_tag(current_indent()-1)
				closed, name, tag = open_tag(match.groups())
				xml_lines.append(tag)
				continue
							
			match = re_comment.match(line)
			if match:
				# comment found. do nothing fancy, just append it as an
				# xml comment.
				xml_lines.append("<!-- %s -->" % (line,))
				continue
				
			match = re_xml.match(line)
			if match:
				# xml line found (i.e. <?xml ...?>), prepend to lines
				xml_lines.reverse()
				xml_lines.append(line)
				xml_lines.reverse()
				
		# close any remaining open tags.
		while len(open_tags) > 0: close_tag(current_indent()-1)

		# return a stringified version of xml_lines stack.				
		return '\n'.join(xml_lines)
	else:
		raise Exception('No file provided.')

if __name__ == '__main__':
	filename = 'data/testfile.struct'
	xml = parse(filename, True)
	print(xml)
	
