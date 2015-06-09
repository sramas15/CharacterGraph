import re
import sys
import csv
import copy
import numpy as np
import itertools
from collections import Counter
from random import sample
from sklearn import metrics

from SpeechAct import *

DELIMS = r'\n| |,|\.|\?|!|:|;|\]|\[|}|--'
DELIMS_PATTERN = re.compile(DELIMS)

def dictionaryWordFeaturizer(speaker2listenerText):
	speaker2FeatureLabels = {}
	for speaker in speaker2listenerText:
		features = []
		labels = []
		for pair in speaker2listenerText[speaker]:
			labels.append(pair[0])
			features.append(Counter(re.split(DELIMS_PATTERN, pair[1])))
		speaker2FeatureLabels[speaker] = (features, labels)
	return speaker2FeatureLabels

def SpeechAct2Dictionary(act, speaker2listenerText):
	speaker = act.speaker
	listeners = act.listeners
	text = act.text
	if speaker not in speaker2listenerText:
		speaker2listenerText[speaker] = []
	for listener in listeners:
		speaker2listenerText[speaker].append((listener, text))
	return speaker2listenerText

# filter the listeners with too few instances
def filterListeners(speaker2listenerText):
	listenerCounts = {}
	for speaker in speaker2listenerText.keys():
		listenerCounts[speaker] = {}
		for listenerText in speaker2listenerText[speaker]:
			listener = listenerText[0]
			text = listenerText[1]
			if listener not in listenerCounts[speaker]:
				listenerCounts[speaker][listener] = 1
			else:
				listenerCounts[speaker][listener] += 1
	filteredListeners = {}
	for speaker in speaker2listenerText.keys():
		filteredListeners[speaker] = []
		for listenerText in speaker2listenerText[speaker]:
			if listenerCounts[speaker][listenerText[0]] >= 5:
				filteredListeners[speaker].append(listenerText)
	return filteredListeners

if __name__ == "__main__":
	outFile = 'listener_predictions/listener-baseline.out'
	print "Cutting off listeners with fewer than 5 interactions with the speaker."
	for playNum in xrange(36):
		filename = 'triples/triples-'+str(playNum)+'.txt'
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
		f.close()
		with open(outFile, 'a') as f:
			f.write("Play: "+str(playNum)+', '+playTitle)
		f.close()

		acts = readSpeechActs(filename)
		speaker2listenerText = {}
		for act in acts:
			speaker2listenerText = SpeechAct2Dictionary(act, speaker2listenerText)
		speaker2listenerText = filterListeners(speaker2listenerText)
		speaker2FeatureLabels = dictionaryWordFeaturizer(speaker2listenerText)
		for speaker in speaker2FeatureLabels.keys():
			if not speaker2FeatureLabels[speaker]:
				continue
			labels = speaker2FeatureLabels[speaker][1]
			randomPredictions = []
			for i in range(len(labels)):
				randomPredictions.append(sample(characters, 1)[0])
			if len(labels) >= 20:
				with open(outFile, 'a') as f:
					f.write("\n====================================================\n")
					f.write("Speaker: "+speaker)
					f.write("\nNumber of Total Listeners: "+str(len(labels))+'\n')
					f.write(metrics.classification_report(labels, randomPredictions))
					f.write("\n===================================================\n")
				f.close()