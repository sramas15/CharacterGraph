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

from distributedwordreps import build, ShallowNeuralNetwork 
from SpeechAct import *
from liwcFeaturizer import *

# borrowed from the NLI codelab, but is our modification to accommodate multiclass classification
def train_logistic_regression(
		feats = None, labels = [],
		feature_selector=SelectFpr(chi2, alpha=0.05), # Use None to stop feature selection
		cv=5, # Number of folds used in cross-validation
		priorlims=np.arange(.1, 3.1, .1), feature_elim = True): # regularization priors to explore (we expect something around 1)
	# Map the count dictionaries to a sparse feature matrix:
	vectorizer = DictVectorizer(sparse=False)
	feats = vectorizer.fit_transform(feats)
	##### FEATURE SELECTION 
	feat_matrix = feats
	feature_selector = None
	if feature_elim == True:
		feature_selector = RFE(estimator=LogisticRegression(), n_features_to_select=None, step=1, verbose=0)
		feat_matrix = feature_selector.fit_transform(feats, labels)

	##### HYPER-PARAMETER SEARCH
	# Define the basic model to use for parameter search:
	searchmod = LogisticRegression(fit_intercept=True, intercept_scaling=1, verbose=1, solver='lbfgs', max_iter=2000)
	# Parameters to grid-search over:
	parameters = {'C':priorlims, 'penalty':['l1', 'l2'], 'multi_class':['multinomial', 'ovr']}  
	# Cross-validation grid search to find the best hyper-parameters:	
	clf = GridSearchCV(searchmod, parameters, cv=cv)
	clf.fit(feat_matrix, labels)
	params = clf.best_params_

	# Establish the model we want using the parameters obtained from the search:
	mod = LogisticRegression(fit_intercept=True, intercept_scaling=1, C=params['C'], penalty=params['penalty'], multi_class=params['multi_class'], solver='lbfgs', verbose=1, max_iter=200)
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
def evaluate_trained_classifier(model=None, filteredFeatures = None, filteredLabels = None):
	"""Evaluate model, the output of train_classifier, on the data in reader."""
	mod, vectorizer, feature_selector = model
	feat_matrix = vectorizer.transform(filteredFeatures)
	if feature_selector:
		feat_matrix = feature_selector.transform(feat_matrix)
	predictions = mod.predict(feat_matrix)
	print metrics.classification_report(filteredLabels, predictions)


def readHandLabels(inFNm):
	labels = {}
	with open(inFNm, "r") as inF:
		for line in inF:
			vals = line.strip().split("\t")
			if len(vals) < 2:
				continue
			labels[vals[0]] = vals[1]
	return labels


def readFeatureNames(line):
	return line.strip().split(",")[2:]

def getFeaturesFromLine(line, featNames):
	vals = line.strip().split(",")
	pair = vals[0]
	length = float(vals[1])
	features = [float(x)/length for x in vals[2:]]
	featDict = {}
	for i in range(len(featNames)):
		featDict[featNames[i]] = features[i]
	return pair, featDict, length

NEUTRAL_LABEL = "0"

def getFeaturesAndLabels(inFNm, hand_labeled):
	features = []
	labels = []
	characters = []
	with open(inFNm, "r") as inF:
		featNames = None
		for line in inF:
			if featNames is None:
				featNames = readFeatureNames(line)
				continue
			pair, feats, length = getFeaturesFromLine(line, featNames)
			if length < 100:
				continue
			if pair in hand_labeled:
				labels.append(hand_labeled[pair])
			else:
				labels.append(NEUTRAL_LABEL)
			features.append(feats)
			characters.append(pair)
	return features, labels, characters



if __name__ == "__main__":
	print "Proportion of cutoff: 20"
	for i in [15]:
		print "========================================================================================================="
		print "Play Number: " + str(i) 

		goldInFNm = "sentiment_labels/labels-%d.txt" % i
		hand_labeled = readHandLabels(goldInFNm)

		inFNm = "Triples-LIWC/%d-merged.csv" % i
		filteredFeatures, filteredLabels, char_names = getFeaturesAndLabels(inFNm, hand_labeled)
		

		# train model
		model = train_logistic_regression(feats = filteredFeatures, labels = filteredLabels, cv = 10)
		evaluate_trained_classifier(model, filteredFeatures = filteredFeatures, filteredLabels = filteredLabels)
		print "========================================================================================================="
		print