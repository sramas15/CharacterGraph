import getWords
import liwcFeaturizer
from collections import defaultdict
import csv 
import pickle

def flipLexicon(lexicon):
	numToWord = {}
	for word in lexicon:
		numToWord[lexicon[word]] = word
	return numToWord


def writeToFile(matrix, outFNm, lexicon=None):
	if not lexicon:
		lexFile = open('lexicon.p', 'r')
		lexicon =  pickle.load(lexFile)
	indF = open(outFNm, 'wb')
	indWriter = csv.writer(indF, delimiter=',', quoting=csv.QUOTE_MINIMAL)
	headers = ['speaker_listener']
	flippedLex = flipLexicon(lexicon)
	num_words = len(flippedLex)
	for i in range(num_words):
		headers.append(flippedLex[i])
	indWriter.writerow(headers)
	for pair in matrix:
		line = [pair]
		for i in range(num_words):
			line.append(matrix[pair][i])
		indWriter.writerow(line)


# call readTriples
# list of tuples (character pair, speech)
def getMatrix(inFNm, lexicon=None):
	if not lexicon:
		lexFile = open('lexicon.p', 'r')
		lexicon =  pickle.load(lexFile)
	pairToWord = {}
	triples = liwcFeaturizer.readTriples(inFNm)
	for pair, text in triples:
		words = list()
		getWords.getWordsFromLine(text, words)
		if pair not in pairToWord:
			pairToWord[pair] = defaultdict(int)
		for word in words:
			if word not in lexicon:
				print "ERROR", text
			index = lexicon[word]
			pairToWord[pair][index] += 1
	return pairToWord


def writeAllCSVs(inFmt="triples/triples-%d.txt", outFmt="matrices/matrix-%d.csv", lexFNm="lexicon.p", num_files=36):
	lexicon = pickle.load(open(lexFNm, 'r'))
	for i in range(num_files):
		inFNm = inFmt % i
		outFNm = outFmt % i
		matrix = getMatrix(inFNm, lexicon)
		writeToFile(matrix, outFNm, lexicon)

if __name__ == "__main__":
	writeAllCSVs()



