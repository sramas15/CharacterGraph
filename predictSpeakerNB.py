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
from sklearn.naive_bayes import MultinomialNB
from sklearn.grid_search import GridSearchCV
from sklearn.cross_validation import cross_val_score
from sklearn import metrics

from distributedwordreps import build, ShallowNeuralNetwork 
from SpeechAct import *
from liwcFeaturizer import *

# borrowed from the NLI codelab, but is our modification to accommodate multiclass classification
def train_NB(
		feats = None, labels = [],
		feature_selector=SelectFpr(chi2, alpha=0.05), # Use None to stop feature selection
		cv=5): # Number of folds used in cross-validation
	# Map the count dictionaries to a sparse feature matrix:
	vectorizer = DictVectorizer(sparse=False)
	feats = vectorizer.fit_transform(feats)
	##### FEATURE SELECTION 
	feat_matrix = feats
	feature_selector = RFE(estimator=LogisticRegression(), n_features_to_select=None, step=1, verbose=0)
	feat_matrix = feature_selector.fit_transform(feats, labels)

	##### HYPER-PARAMETER SEARCH
	# Define the basic model to use for parameter search:
	searchmod = MultinomialNB()
	# Parameters to grid-search over:
	parameters = {'alpha':np.arange(.1, 2.0, .5)}
	# Cross-validation grid search to find the best hyper-parameters:	
	clf = GridSearchCV(searchmod, parameters, cv=cv, n_jobs=-1)
	clf.fit(feat_matrix, labels)
	params = clf.best_params_

	# Establish the model we want using the parameters obtained from the search:
	mod = MultinomialNB(alpha=params['alpha'])
	##### ASSESSMENT
	scores = cross_val_score(mod, feat_matrix, labels, cv=cv, scoring="f1_macro")	  
	print 'Best model', mod
	print '%s features selected out of %s total' % (feat_matrix.shape[1], feats.shape[1])
	print 'F1 mean: %0.2f (+/- %0.2f)' % (scores.mean(), scores.std()*2)

	# TRAIN OUR MODEL:
	mod.fit(feat_matrix, labels)
	# Return the trained model along with the objects we need to
	# featurize test data in a way that aligns with our training
	# matrix:
	return (mod, vectorizer, feature_selector)

# borrowed from the NLI codelab and modified to suit our data format
def evaluate_trained_classifier(model=None):
	"""Evaluate model, the output of train_classifier, on the data in reader."""
	mod, vectorizer, feature_selector = model
	feat_matrix = vectorizer.transform(filteredFeatures)
	if feature_selector:
		feat_matrix = feature_selector.transform(feat_matrix)
	predictions = mod.predict(feat_matrix)
	print metrics.classification_report(filteredLabels, predictions)

# construct a dataset with lists of LIWC features and speakers (indexed)
def constructSpeakerLIWCDataset(filename):
	liwcDict = getLIWCDictionary()
	acts = readSpeechActs(filename)
	features = []
	speakers = []
	speakerInd = {}
	speakerCount = {}
	index = 0
	for act in acts:
		speaker = act.speaker
		feat, length = liwcFeaturize(liwcDict, act.text)
		if speaker not in speakerInd:
			speakerInd[speaker] = index
			index += 1
		if speakerInd[speaker] not in speakerCount:
			speakerCount[speakerInd[speaker]] = 1
		else:
			speakerCount[speakerInd[speaker]] += 1
		speakers.append(speakerInd[speaker])
		features.append(feat)
	return (features, speakers, speakerInd, speakerCount)

DELIMS = r'\n| |,|\.|\?|!|:|;|\]|\[|}|--'
DELIMS_PATTERN = re.compile(DELIMS)

# construct a dataset with lists of Word Count features and speakers (indexed)
def constructSpeakerWordCountDataset(filename):
	acts = readSpeechActs(filename)
	features = []
	speakers = []
	speakerInd = {}
	speakerCount = {}
	index = 0
	for act in acts:
		speaker = act.speaker
		if speaker not in speakerInd:
			speakerInd[speaker] = index
			index += 1
		if speakerInd[speaker] not in speakerCount:
			speakerCount[speakerInd[speaker]] = 1
		else:
			speakerCount[speakerInd[speaker]] += 1
		speakers.append(speakerInd[speaker])
		feat = Counter(re.split(DELIMS_PATTERN, act.text))
		features.append(feat)
	return (features, speakers, speakerInd, speakerCount)
	# mat, rownames, headers = build(filename)
	# features = []
	# speakers = []
	# speakerInd = {}
	# speakerCount = {}
	# index = 0
	# for i in xrange(len(rownames)):
	# 	chars = rownames[i].split('_')
	# 	speaker = chars[0]
	# 	listener = chars[0]
	# 	if speaker not in speakerInd:
	# 		speakerInd[speaker] = index
	# 		index += 1
	# 	if speakerInd[speaker] not in speakerCount:
	# 		speakerCount[speakerInd[speaker]] = 1
	# 	else:
	# 		speakerCount[speakerInd[speaker]] += 1
	# 	speakers.append(speakerInd[speaker])
	# 	feat = {}
	# 	for j in xrange(1, len(headers)):
	# 		feat[headers[j]] = mat[i][j]
	# 	features.append(feat)
	# return (features, speakers, speakerInd, speakerCount)

# constant for the speech act number cutoff proportion - speaker with acts fewer than
# this fraction of the total acts will be eliminated
CUTOFF_FRACTION = 20

# filter the dataset to eliminate speakers with too few speech acts
def filterSpeakerLIWCDataset(features, labels, speakerCount, MIN_ACTS = -1):
	if MIN_ACTS == -1:
		MIN_ACTS = len(features) / CUTOFF_FRACTION
	# filter the speakers with too few number of speech acts
	filteredFeatures = []
	filteredLabels = []
	for feat, label in itertools.izip(features, labels):
		if speakerCount[label] >= MIN_ACTS:
			filteredFeatures.append(feat)
			filteredLabels.append(label)
	return (filteredFeatures, filteredLabels, MIN_ACTS)

def getImportantWeights(model, features):
	print 
	print "Highest and lowest weights in the model"
	print 
	coefficients = model.coef_
	# there is a set of feature weights for each speaker
	for i in xrange(coefficients.shape[0]):
		weights= coefficients[i]
		argmax = np.argmax(weights)
		argmin = np.argmin(weights)
		Wmax = np.max(weights)
		Wmin = np.min(weights)
		index = 0
		featMax = 'None'
		featMin = 'None'
		for feat in features.keys():
			if index == argmax:
				featMax = feat
			if index == argmin:
				featMin = feat
			index += 1
		print "Max: " + featMax + ", " + str(Wmax)
		print "Min: " + featMin + ", " + str(Wmin)
		print

if __name__ == "__main__":
	print "Proportion of cutoff: 20"
	for i in xrange(36):
		print "========================================================================================================="
		print "Play Number: " + str(i) 
		# construct the multiclass dataset
		features, labels, speakerMap, speakerCount = constructSpeakerLIWCDataset('triples/triples-'+str(i)+'.txt')
		# features, labels, speakerMap, speakerCount = constructSpeakerWordCountDataset('triples2/triples-'+str(i)+'.txt')
		# filter dataset
		filteredFeatures, filteredLabels, MIN_ACTS = filterSpeakerLIWCDataset(features, labels, speakerCount)
		print
		print "Speech Act Number Cutoff: " + str(MIN_ACTS)
		print "Number of Total Speakers: " + str(len(speakerCount))
		print
		# train model
		model = train_NB(feats = filteredFeatures, labels = filteredLabels, cv = MIN_ACTS / 10)
		# print out several LIWC weights (cannot be done for word features though)
		getImportantWeights(model[0], getLIWCDictionary())
		# evaluate
		evaluate_trained_classifier(model)
		print speakerMap
		print
		print speakerCount
		print "========================================================================================================="
		print