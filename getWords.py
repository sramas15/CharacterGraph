import re

LISTENERS = re.compile(r"[A-Z ]*")
DELIMS = r'\n| |,|\.|\?|!|:'
DELIMS_PATTERN = re.compile(DELIMS)
COUNT = 0
print COUNT

def isListener(line):
	x = re.match(LISTENERS, line)
	return x != None and len(x.group()) == len(line)

def getWordsFromLine(line, words):
	cand_words = re.split(DELIMS_PATTERN, line)
	cnt = 0
	for word in cand_words:
		word = word.strip("'") # if it is in quotes, strip quotes
		word = word.strip("-") # if it is in quotes, strip quotes
		if word == "":
			continue
		cnt += 1
		words.add(word.lower())
	return cnt

def getWords(inFNm):
	words = set()
	cnt = 0
	with open(inFNm, 'r') as inF:
		newTriple = True
		getCount = False
		for line in inF:
			line = line.strip()
			if line == '': # reached the end of a triple
				newTriple = True
				continue
			if newTriple: # read character name
				newTriple = False
				getCount = True
				continue
			if getCount: # read number of listeners
				getCount = False
				continue
			if isListener(line):
				continue
			cnt += getWordsFromLine(line, words)
	return words, cnt

def getAllWords(inPtrn="triples/triples-%d.txt", num_files=36):
	allWords = set()
	total = 0
	for i in range(num_files):
		inFNm = inPtrn % i
		words, cnt = getWords(inFNm)
		allWords.update(words)
		total += cnt
	print "%d / %d" % (len(allWords), total)
	print float(total) / len(allWords)


if __name__ == "__main__":
	getAllWords()



