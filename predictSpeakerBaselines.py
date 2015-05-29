from SpeechAct import *
from random import sample
from sklearn import metrics

NUM_PLAYS = 36
PRUNING_LIMIT = 40
for playNum in range(NUM_PLAYS):
	playFile = 'triples/triples-'+str(playNum)+'.txt'
	charFile = 'char_list/char-'+str(playNum)+'.txt'

	characters = set()
	playTitle = ''
	with open(charFile, 'r') as f:
		titleLine = True
		for line in f:
			if titleLine:
				playTitle = line.strip()
				titleLine = False
			else:
				characters.add(line.strip())

	acts = readSpeechActs(playFile)
	speechActCounts = {} # speaker -> number of speech acts
	goldLabels = []
	randomPredictions = []

	for act in acts:
		trueSpeaker = act.speaker
		goldLabels.append(trueSpeaker)
		if trueSpeaker in speechActCounts:
			speechActCounts[trueSpeaker] += 1
		else:
			speechActCounts[trueSpeaker] = 1
		randomSpeaker = sample(characters, 1)[0]
		randomPredictions.append(randomSpeaker)

	prunedCharacters = set()
	for key in speechActCounts:
		if speechActCounts[key] > PRUNING_LIMIT:
			prunedCharacters.add(key)

	mostCommonSpeaker = max((value, key) for key, value in speechActCounts.items())[1]
	mostCommonPredictions = [mostCommonSpeaker for x in range(len(goldLabels))]

	goldPrunedLabels = []
	randomPrunedPredictions = []
	mostCommonPrunedPredictions = []
	for act in acts:
		trueSpeaker = act.speaker
		if speechActCounts[trueSpeaker] > 40:
			goldPrunedLabels.append(trueSpeaker)
			randomPrunedPredictions.append(sample(prunedCharacters, 1)[0])
	mostCommonPrunedPredictions = [mostCommonSpeaker for x in range(len(goldPrunedLabels))]

	print "\nBaselines for play", playNum, playTitle
	print "Random speaker baseline performance:"
	print metrics.classification_report(goldLabels, randomPredictions)
	print "Most common speaker baseline performance:"
	print metrics.classification_report(goldLabels, mostCommonPredictions)
	print "Pruned random speaker baseline performance:"
	print metrics.classification_report(goldPrunedLabels, randomPrunedPredictions)
	print "Pruned most common speaker baseline performance:"
	print metrics.classification_report(goldPrunedLabels, mostCommonPrunedPredictions)
