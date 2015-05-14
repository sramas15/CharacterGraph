# END_ACT
# <after char name> (Aside)

NUM_PLAYS = 34

# Checks if a line starts a new scene
def startsNewScene(line):
	# ACT <roman numeral>. SCENE <roman numeral>.

# Checks if a line starts a new character's speech, and if so updates currSpeaker
# and removes speaker's name from line
def newCharacterSpeaking(line, currSpeaker):
	# <two spaces><speaker name in all caps>.
	# set currSpeaker to new speaker
	# remove speaker's name and period from line

# Checks if a line contains characters entering the scene, and if so updates currCharList
def checkEntryLine(line, currCharList):
	# if line contains 'enter' and doesn't start with character name and has names in all caps
	# add characters to currCharList
	# return whether it's an entry line or not

# Checks if a line contains characters leaving the scene, and if so updates currCharList
def checkExit(line, currCharList):
	# if line has Exit with no character name following it, remove character that was speaking
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
			elif newCharacterSpeaking(line, currSpeaker):
				if needToWriteTriple:
					writeToFile(currSpeaker, currCharList, currSpeech, outFile)
				currSpeech = line
				needToWriteTriple = True
				if checkExit(line, currCharList):
					needToWriteTriple = True
			elif not checkEntryLine(line, currCharList):
				if checkSpeechContinuation(line):
					if needToWriteTriple:
						writeToFile(currSpeaker, currCharList, currSpeech, outFile)
					currSpeech += '\n' + line
				if checkExit(line, currCharList):
					needToWriteTriple = True

