import re
import sys
import csv
import copy
import numpy as np
import itertools
from collections import Counter

try:
	import sklearn
except ImportError:
	sys.stderr.write("scikit-learn version 0.16.* is required\n")
	sys.exit(2)
if sklearn.__version__[:4] != '0.16':
	sys.stderr.write("scikit-learn version 0.16.* is required. You're at %s.\n" % sklearn.__version__)
	sys.exit(2)

from sklearn.feature_extraction import DictVectorizer
from sklearn.feature_selection import SelectFpr, chi2, RFE
from sklearn.linear_model import LogisticRegression
from sklearn.grid_search import GridSearchCV
from sklearn.cross_validation import cross_val_score
from sklearn import metrics

from predictSpeakerLogReg import *
from SpeechAct import *
from liwcFeaturizer import *

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

# borrowed from the NLI codelab and modified to suit our data format
def evaluate_trained_classifier(model=None, features = None, labels = None):
	"""Evaluate model, the output of train_classifier, on the data in reader."""
	mod, vectorizer, feature_selector = model
	feat_matrix = vectorizer.transform(features)
	if feature_selector:
		feat_matrix = feature_selector.transform(feat_matrix)
	predictions = mod.predict(feat_matrix)
	print metrics.classification_report(labels, predictions)

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
	print "Cutting off listeners with fewer than 5 interactions with the speaker."
	for playNum in xrange(36):
		print "Play: " + str(playNum)
		print
		filename = 'triples/triples-'+str(playNum)+'.txt'
		acts = readSpeechActs(filename)
		speaker2listenerText = {}
		for act in acts:
			speaker2listenerText = SpeechAct2Dictionary(act, speaker2listenerText)
		speaker2listenerText = filterListeners(speaker2listenerText)
		speaker2FeatureLabels = dictionaryWordFeaturizer(speaker2listenerText)
		for speaker in speaker2FeatureLabels.keys():
			if not speaker2FeatureLabels[speaker]:
				continue
			features = speaker2FeatureLabels[speaker][0]
			labels = speaker2FeatureLabels[speaker][1]
			if len(labels) >= 20:
				print "========================================================================================================="
				print "Speaker: " + speaker
				print "Number of Total Listeners: " + str(len(labels))
				print
				# train model
				model = train_logistic_regression(feats = features, labels = labels, cv = 5)
				print
				# evaluate
				evaluate_trained_classifier(model, features = features, labels = labels)
				print "========================================================================================================="
				print
