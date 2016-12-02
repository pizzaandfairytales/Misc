import random
import sys
import urllib2
import html5lib
random.seed()
if len(sys.argv) is not 2:
	print "Please pass exactly 1 argument (input file)"
else:
	file = open(sys.argv[1], 'r')
	names = []
	count = 0
	for line in file:
		count += 1
		names.append(line.rstrip())
	file.close()
	elements_gauss = []
	for x in range(count):
		elements_gauss.append(random.gauss(50, 12.5))
	elements_uniform = []
	for x in range(count):
		elements_uniform.append(random.random() * 100)
	elements_gauss.sort()
	elements_gauss.reverse()
	elements_uniform.sort()
	elements_uniform.reverse()
	outfile = sys.argv[1] + "_uniform"
	file = open(outfile, 'w')
	for x in range(count):
		file.write(names[x] + " | " + str(int(elements_uniform[x])) + "\n")
	file.close()
	outfile2 = sys.argv[1] + "_gauss"
	file = open(outfile2, 'w')
	for x in range(count):
		file.write(names[x] + " | " + str(int(elements_gauss[x])) + "\n")
	file.close()
