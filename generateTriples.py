import re

NUM_PLAYS = 34

# Returns whether a line starts a new scene
def startsNewScene(line):
	match = re.match(r'^(ACT [A-Z][A-Z]?. )?SCENE [A-Z][A-Z]?[A-Z]?.$', line)
	if match:
		return True

# Checks if a new character starts speaking, and if so
# returns (newSpeaker, line with speaker's name removed)
def newCharacterSpeaking(line):
	match = re.match(r'^  ([A-Z]+). ', line)
	if match:
		currSpeaker = match.group(0)
		line = line.lstrip().replace(currSpeaker, "", 1)[2:]
		return (currSpeaker, line)
	return None

# Checks if a line contains characters entering the scene, 
# and if so returns the updated currCharList
# Will get wrong:
# Re-enter WHITMORE with SUFFOLK'S body
def checkEntryLine(line, currCharList):
	ind = line.find('enter ')
	if ind != -1:
		match = re.search(r'(?:[a-z ]*)([A-Z][A-Za-z]+(?: [A-Z][A-Za-z]+)*)', line[ind+6:])
		if match:
			for group in match.groups():
				group = group.upper()
				# print 'Enter:', group
				if group in charNames:
					currCharList.add(group)
				else:
					words = group.split()
					if len(words) > 1: # Deals with different forms of names
						for word in words:
							if word in charNames:
								currCharList.add(word)
					else:
						for char in charNames: # Deals with abbreviated names
							if char.find(group) != -1:
								print group, char
								currCharList.add(char)

			return currCharList
	return None

# Checks if a line contains characters leaving the scene, 
# and if so returns updated currCharList
# Will miss or get wrong
# [Edmund is borne off.]
# Exeunt all but the FIRST GENTLEMAN
def checkExit(line, currSpeaker, currCharList):
	# also catches "Exit running." and "[Exit.]"
	match = re.search(r'\[?(?:(?:Exit\.)|(?:Exit (?:[a-z ]*)\.?))\]?', line)
	if match:
		if currSpeaker.upper() in currCharList:
			# print 'Exit:', currSpeaker
			currCharList.remove(currSpeaker.upper())
			return currCharList
	ind = line.find('Exit ')
	if ind == -1:
		ind = line.find('Exeunt ')
		if ind != -1:
			ind += 7
	else:
		ind += 5
	if ind != -1:
		line = line[ind:]
		moreChars = re.search(r'(?:[a-z ]*)([A-Z][A-Za-z]+(?: [A-Z][A-Za-z]+)*)', line)
		if moreChars:
			for group in moreChars.groups():
				# print 'Exit:', group
				if group.upper() in currCharList:
					currCharList.remove(group.upper())
			return currCharList
	return None

# Checks if a line is speech continuation
def checkSpeechContinuation(line):
	match = re.search(r'    (?:[A-Za-z]*)', line)
	if match:
		return True
	return False

# Writes triple: currSpeaker \n len(currCharList) \n currCharList \n currSpeech
def writeToFile(currSpeaker, currCharList, currSpeech, outFile):
	with open(outFile, 'a') as f:
		f.write(currSpeaker + '\n')
		f.write(str(len(currCharList)) + '\n')
		for char in currCharList:
			f.write(char + '\n')
		f.write(currSpeech) # BUT STRING HAS NEWLINES. FIND NUMLINES AND INSERT AS WELL?
	f.close()

for playNum in range(NUM_PLAYS):
	playFile = 'out-' + str(playNum) + '.txt'
	charFile = 'char-' + str(playNum) + '.txt'
	outFile = 'triples-' + str(playNum) + '.txt'

	print '----------\n----------'
	charNames = set()
	with open(charFile, 'r') as f:
		i = 0
		for line in f:
			line = line.upper()
			if i == 0: # First line is the play's title
				i = 1
			else:
				charNames.add(line.strip())
	f.close()
	for c in charNames:
		print c
	print '----------'

	with open(playFile, 'r') as f:
		currCharList = set()
		currSpeaker = ""
		needToWriteTriple = False
		currSpeech = ""
		for line in f:
			if startsNewScene(line):
				if needToWriteTriple:
					writeToFile(currSpeaker, currCharList, currSpeech, outFile)
					needToWriteTriple = False
				currCharList.clear()
				currSpeech = ""
			else:
				tup = newCharacterSpeaking(line) 
				if tup != None:
					if needToWriteTriple:
						writeToFile(currSpeaker, currCharList, currSpeech, outFile)
					currSpeaker = tup[0]
					line = tup[1]
					currSpeech = line
					needToWriteTriple = True
					if checkExit(line, currSpeaker, currCharList):
						writeToFile(currSpeaker, currCharList, currSpeech, outFile)
						needToWriteTriple = False
				else:
					newCharList = checkEntryLine(line, currCharList)
					if newCharList != None:
						currCharList = newCharList
						needToWriteTriple = True
					else:
						if checkSpeechContinuation(line):
							if needToWriteTriple:
								writeToFile(currSpeaker, currCharList, currSpeech, outFile)
								needToWriteTriple = False
							currSpeech += line
						if checkExit(line, currSpeaker, currCharList):
							needToWriteTriple = True
	f.close()
