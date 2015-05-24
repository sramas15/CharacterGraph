# Need to deal with [To NAME] in speech
# Need to deal with [Within] in speech

import re

NUM_PLAYS = 36

# Returns whether a line starts a new scene
def startsNewScene(line):
	match = re.match(r'^(ACT [A-Z][A-Z]?. )?S(CENE|cene) ([A-Z][A-Z]?[A-Z]?|[0-9][0-9]?).$', line)
	return match

# Checks if a new character starts speaking, and if so
# returns (newSpeaker, line with speaker's name removed)
def newCharacterSpeaking(line):
	match = re.match(r'^  ([A-Z][A-Z]+(?: [A-Z][A-Z]+)*)\.', line)
	if match:
		currSpeaker = match.group(1)
		line = line.lstrip()
		line = line[len(currSpeaker)+2:]
		return (currSpeaker, line)
	return None

# Checks if a line contains characters entering the scene, 
# and if so updates currCharList and returns list of entering characters
# Will get wrong:
# Re-enter WHITMORE with SUFFOLK'S body
def checkEntryLine(line, currCharList):
	enteringChars = []
	ind = line.lower().find('enter ')
	if ind != -1:
		match = re.findall(r'([A-Z][A-Z]+(?: [A-Z][A-Z]+)*)', line[ind+6:])
		for group in match:
			if group in charNames:
				currCharList.add(group)
				enteringChars.append(group)
			# else:
			# 	words = group.split()
			# 	if len(words) > 1: # Deals with different forms of names
			# 		for word in words:
			# 			if word in charNames:
			# 				currCharList.add(word)
			# 				enteringChars.append(word)
	return enteringChars

# Checks if a line contains characters leaving the scene, 
# and if so updates currCharList, and returns 
# line with exit removed, list of exiting characters
# Will miss or get wrong
# [Edmund is borne off.]
def checkExit(line, currSpeaker, currCharList):
	# also catches "Exit running." and "[Exit.]"
	match = re.search(r'\[?(?:(?:Exit\.?)|(?:Exit (?:[a-z ]*)\.?))\]?$', line)
	if match:
		if currSpeaker in currCharList:
			currCharList.remove(currSpeaker)
			line = line[:match.start()].rstrip()+'\n'
			return line, set([currSpeaker])
	match = re.search(r'\[?(?:(?:Exeunt\.?)|(?:Exeunt (?:[a-z ]*)\.?))\]?$', line)
	if match:
		oldCharList = currCharList
		currCharList.clear()
		line = line[:match.start()].rstrip()+'\n'
		return line, oldCharList
	ind = line.find('Exit ')
	if ind == -1:
		ind = line.find('Exeunt ')
		if ind != -1:
			charInd = ind + 7
	else:
		charInd = ind + 5
	if ind != -1:
		moreChars = re.findall(r'(?:[a-z ]*)([A-Z][A-Z]+(?: [A-Z][A-Z]+)*)', line[charInd:])
		all_but = re.match(r'all but ', line[charInd:])
		if moreChars:
			to_remove = set()
			for group in moreChars:
				if group in currCharList:
					to_remove.add(group)
			if all_but:
				removed = currCharList.difference(to_remove)
				currCharList.intersection_update(to_remove)
				return line[:ind].rstrip()+'\n', removed
			else:
				currCharList.difference_update(to_remove)
				return line[:ind].rstrip()+'\n', to_remove
			# return line[:ind].rstrip()+'\n'
	return None, None

# Checks if a line is speech continuation
def checkSpeechContinuation(line):
	match = re.search(r'^    [\S]', line)
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
	playFile = 'full_text/out-' + str(playNum) + '.txt'
	charFile = 'char_list/char-' + str(playNum) + '.txt'
	outFile = 'triples/triples-' + str(playNum) + '.txt'

	# print '----------\n----------'
	charNames = set()
	with open(charFile, 'r') as f:
		playTitle = True
		for line in f:
			if playTitle: # First line is the play's title
				playTitle = False
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
					currSpeech = line
					exitLine, removedChars = checkExit(line, currSpeaker, currCharList)
					if exitLine:
						line = exitLine
						currSpeech = line
						exitCharList = removedChars.union(currCharList)
						writeToFile(currSpeaker, exitCharList, currSpeech, outFile)
						needToWriteTriple = False
				else:
					if checkSpeechContinuation(line):
						exitLine, removedChars = checkExit(line, currSpeaker, currCharList)
						if exitLine:	
							line = exitLine
							currSpeech += line.lstrip() # Remove leading 4 spaces
							exitCharList = removedChars.union(currCharList)
							writeToFile(currSpeaker, exitCharList, currSpeech, outFile)
							needToWriteTriple = False
						else:
							currSpeech += line.lstrip() # Remove leading 4 spaces
					else:
						enteringChars = checkEntryLine(line, currCharList)
						if enteringChars:
							if needToWriteTriple:
								beforeChars = currCharList.difference(enteringChars)
								writeToFile(currSpeaker, beforeChars, currSpeech, outFile)
								needToWriteTriple = False
	f.close()