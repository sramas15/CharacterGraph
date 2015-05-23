# Need to remove exit and 4 spaces from line before printing / before adding to currSpeech
# If char speaks who's not in char list, add them to char list?

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
	match = re.match(r'^  ([A-Z][A-Za-z]+(?: [A-Z][A-Za-z]+)*)\.', line)
	if match:
		currSpeaker = match.group(1)
		line = line.lstrip()
		line = line[len(currSpeaker)+2:]
		return (currSpeaker, line)
	return None

# Checks if a line contains characters entering the scene, 
# and if so returns the updated currCharList
# Will get wrong:
# Re-enter WHITMORE with SUFFOLK'S body
def checkEntryLine(line, currCharList):
	ind = line.lower().find('enter ')
	if ind != -1:
		match = re.findall(r'([A-Z][A-Za-z]+(?: [A-Z][A-Za-z]+)*)', line[ind+6:])
		for group in match:
			# print 'Enter:', group
			if group in charNames:
				currCharList.add(group)
			else:
				words = group.split()
				if len(words) > 1: # Deals with different forms of names
					for word in words:
						if word in charNames:
							currCharList.add(word)
				# else:
					# print group
				# 	for char in charNames: # Deals with abbreviated names
				# 		if char.find(group) != -1:
				# 			# print group, char
				# 			currCharList.add(char)
		return currCharList
	return None

# Checks if a line contains characters leaving the scene, 
# and if so returns (updated currCharList, line with exit removed)
# Will miss or get wrong
# [Edmund is borne off.]
# Exeunt all but the FIRST GENTLEMAN
def checkExit(line, currSpeaker, currCharList):
	# also catches "Exit running." and "[Exit.]"
	match = re.search(r'\[?(?:(?:Exit\.)|(?:Exit (?:[a-z ]*)\.?))\]?', line)
	if match:
		if currSpeaker in currCharList:
			# print 'Exit:', currSpeaker
			currCharList.remove(currSpeaker)
			line = line[:match.start()].rstrip()
			return (currCharList, line)
	ind = line.find('Exit ')
	if ind == -1:
		ind = line.find('Exeunt ')
		if ind != -1:
			ind += 7
	else:
		ind += 5
	if ind != -1:
		moreChars = re.findall(r'(?:[a-z ]*)([A-Z][A-Za-z]+(?: [A-Z][A-Za-z]+)*)', line[ind:])
		if moreChars:
			for group in moreChars:
				# print 'Exit:', group
				if group in currCharList:
					currCharList.remove(group)
			return (currCharList, line[:ind])
	return None

# Checks if a line is speech continuation
def checkSpeechContinuation(line):
	match = re.search(r'^    (?:[A-Za-z]+)', line)
	return match

# Writes triple: currSpeaker \n len(currCharList) \n currCharList \n currSpeech \n
def writeToFile(currSpeaker, currCharList, currSpeech, outFile):
	with open(outFile, 'a') as f:
		f.write(currSpeaker + '\n')
		f.write(str(len(currCharList)-1) + '\n')
		for char in currCharList:
			if char != currSpeaker:
				f.write(char + '\n')
		f.write(currSpeech+'\n')
	f.close()

for playNum in range(NUM_PLAYS):
	playFile = 'out-' + str(playNum) + '.txt'
	charFile = 'char-' + str(playNum) + '.txt'
	outFile = 'triples-' + str(playNum) + '.txt'

	# print '----------\n----------'
	charNames = set()
	with open(charFile, 'r') as f:
		i = 0
		for line in f:
			if i == 0: # First line is the play's title
				i = 1
			else:
				charNames.add(line.strip())
	f.close()
	# for c in charNames:
	# 	print c
	# print '----------'

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
				if tup:
					if needToWriteTriple:
						writeToFile(currSpeaker, currCharList, currSpeech, outFile)
					currSpeaker = tup[0]
					if currSpeaker not in currCharList:
						currCharList.add(currSpeaker)
					line = tup[1]
					needToWriteTriple = True
					exitOutput = checkExit(line, currSpeaker, currCharList)
					if exitOutput:
						line = exitOutput[1]
						writeToFile(currSpeaker, currCharList, currSpeech, outFile)
						currCharList = exitOutput[0]
						needToWriteTriple = False
					currSpeech = line
				else:
					if checkSpeechContinuation(line):
						exitOutput = checkExit(line, currSpeaker, currCharList)
						if exitOutput:
							line = exitOutput[1]
							writeToFile(currSpeaker, currCharList, currSpeech, outFile)
							needToWriteTriple = False
							currCharList = exitOutput[0]
						currSpeech += line
					else:
						newCharList = checkEntryLine(line, currCharList)
						if newCharList:
							currCharList = newCharList
	f.close()
