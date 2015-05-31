import re

LISTENERS = re.compile(r"[A-Z ]*")

def isListener(line):
	x = re.match(LISTENERS, line)
	return x != None and len(x.group()) == len(line)

def getTriples(inFNm):
	triples = []
	speaker = None
	listeners = set()
	text = []
	num_listeners = 0
	with open(inFNm, 'r') as inF:
		newTriple = True
		getCount = False
		for line in inF:
			line = line.strip()
			if line == '': # reached the end of a triple
				if speaker != None:
					triples.append([speaker, listeners, text])
				newTriple = True
				speaker = None
				listeners = set()
				text = []
				num_listeners = 0
				continue
			if newTriple: # read character name
				newTriple = False
				getCount = True
				speaker = line
				continue
			if getCount: # read number of listeners
				getCount = False
				num_listeners = int(line)
				continue
			if isListener(line):
				listeners.add(line)
				continue
			assert num_listeners == len(listeners)
			text.append(line)
		if speaker != None:
			triples.append([speaker, listeners, text])
	return triples

def writeLine(outF, triple):
	outF.write("%s\n" % triple[0]) # write speaker
	outF.write("%d\n" % len(triple[1])) # write speaker
	for listener in triple[1]:
		outF.write("%s\n" % listener)
	for text in triple[2]:
		outF.write("%s\n" % text)
	outF.write("\n")

def filterListenersByNeighbors(inFNm, outFNm, numNbrs=2):
	triples = getTriples(inFNm)
	with open(outFNm, "w") as outF:
		for i in range(len(triples)):
			speaker = triples[i][0]
			index = i-1
			prev = []
			while index >= 0 and len(prev) < numNbrs:
				nbr = triples[index][0]
				if nbr != speaker:
					prev.append(nbr)
				index -= 1
			index = i+1
			next = []
			while index < len(triples) and len(next) < numNbrs:
				nbr = triples[index][0]
				if nbr != speaker:
					next.append(nbr)
				index += 1
			nbrs = set(prev + next)
			triples[i][1].intersection_update(nbrs)
			writeLine(outF, triples[i])

if __name__ == "__main__":
	for i in range(36):
		filterListenersByNeighbors("triples/triples-%d.txt" % i, "triples2/triples-%d.txt" % i)