# END_ACT
# <after char name> (Aside)
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
		line = replace(lstrip(line), currSpeaker, "")[2:]
		return (currSpeaker, line)
	return None

# Checks if a line contains characters entering the scene, and if so 
# returns the updated currCharList

# Lines still to deal with:
# Enter [Oswald the] Steward.

# Will get wrong:
# Re-enter WHITMORE with SUFFOLK'S body

def checkEntryLine(line, currCharList):
	match = re.search(r'[Ee]nter ([A-Z][A-Za-z]+(?: [A-Z][A-Za-z]+)*)[., ]', line)
	if match:
		char = match.group(0)
		currCharList.add(char)
		moreChars = re.search(r'(?:[a-z ]*)([A-Z][A-Za-z]+(?: [A-Z][A-Za-z]+)*)[., ]', line)
		if moreChars:
			for group in moreChars.groups() where group != char:
				currCharList.add(group)
		return currCharList
	return None

# Checks if a line contains characters leaving the scene, and if so
# returns updated currCharList

# Lines still to deal with:
# Exeunt Goneril, [Edmund, and Oswald].
# Exit [one] with Gloucester.
# Exit [Cornwall, led by Regan].
# Exit running.
# [Exit.]
# Exit servant with PETER
# Exit WALTER with SUFFOLK
# Exeunt all but the FIRST GENTLEMAN

# Will definitely miss
# [Edmund is borne off.]

def checkExit(line, currSpeaker, currCharList):
	match = re.search(r'Exit\.', line)
	if match:
		currCharList.remove(currSpeaker)
		return currCharList
	moreChars = re.search(r'Exit ', line)
	if moreChars:
		for group in moreChars.groups():
			currCharList.remove(group)
		return currCharList
	return None

	# if line has Exit with a character name following it, remove that character
	# if line has exeunt, figure out who to remove

# Checks if a line is speech continuation
def checkSpeechContinuation(line):
	# speech has 4 spaces before it. -> look for 4 spaces then alphanumeric character

# Writes all possible triples for a given speech to file
def writeToFile(currSpeaker, currCharList, currSpeech, outFile):
	for listener in currCharList where listener is not currSpeaker:
		# write speaker to outFile
		# write listener to outFile
		# write currSpeech to outFile

def resetAll(currSpeaker, currSpeech, currCharList)

for playNum in range(NUM_PLAYS):
	playFile = 'out-' + playNum + '.txt'
	outFile = 'triples-' + playNum + '.txt'
	with open(playFile, 'r') as f:
		currCharList = set()
		currSpeaker = ""
		needToWriteTriple = False
		currSpeech = ""
		for line in f:
			if startsNewScene(line):
				if needToWriteTriple:
					writeToFile(currSpeaker, currCharList, currSpeech, outFile)
				resetAll(currSpeaker, currSpeech, currCharList)
			else:
				tup = newCharacterSpeaking(line, currSpeaker) 
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
						if checkSpeechContinuation(line):
							if needToWriteTriple:
								writeToFile(currSpeaker, currCharList, currSpeech, outFile)
							currSpeech += line
						if checkExit(line, currSpeaker, currCharList):
							needToWriteTriple = True

