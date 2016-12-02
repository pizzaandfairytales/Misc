import sys
if len(sys.argv) is not 3:
	print "Please pass exactly 2 arguments (input file, output file)"
else:
	file = open(sys.argv[1], 'r')
	goodlines = []
	for line in file:
		if "\\n" in line:
			str = line[33:]
			str = str[:-43]
			goodlines.append(str)
	file.close()
	file = open(sys.argv[2], 'w')
	for x in goodlines:
		x += "\n"
		file.write(x)
	file.close
