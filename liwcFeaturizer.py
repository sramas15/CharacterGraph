import pickle
import re
import csv 

# This function loads the LIWC dictionary and returns as a
# dict from strings of scales to regex patterns
def getLIWCDictionary():
	liwcFile = open('LIWC2007dictionary_regex.pickle', 'r')
	return pickle.load(liwcFile)

# This fcuntion parse the received text and perform counts
# of scales. Then normalize by the length of the text.
def liwcFeaturize(dictionary, text):
	words = re.split('[^A-Za-z0-9\']', text)
	features = {}
	for scale in dictionary:
		pattern = dictionary[scale].pattern
		count = 0.
		for word in words:
			match = re.match(pattern, word)
			if match:
				count += 1.
		features[scale] = count / len(words)
	return features, len(words)

# This function parse the triple-*.txt files and convert the
# files into a list of tuples containing pairs of speakers 
# (following the convention speaker_listener) and the speech.
def readTriples(filename):
	speeches = []
	with open(filename, 'r') as f:
		while True:
			# process each speech block of the triple-*.txt file
			speaker = f.readline().strip()
			if speaker == "":
				break
			nSpeaker = int(float(f.readline()))
			pairs = []
			for i in xrange(nSpeaker):
				receiver = f.readline().strip()
				pair = speaker + "_" + receiver
				pairs.append(pair)
			speech = ""
			while True:
				line = f.readline().strip()
				if line == "":
					break
				speech += line
			for pair in pairs:
				speeches.append((pair, speech))
	return speeches

# This function featurizes the speeches between characters
# obtained from the triple-*.txt files using the LIWC features.
def featurizeSpeeches(dictionary, speeches):
	features = []
	for pair in speeches:
		speakers = pair[0]
		speech = pair[1]
		feature, length = liwcFeaturize(dictionary, speech)
		features.append((speakers, length, feature))
	return features

# This function merges two entries with the same speaker and listener
# into one entry (in the form of triples)
def makeCSVRow(characters, length, features):
	row = [characters]
	for scale in features:
		row.append(features[scale])
	return row

# This function writes the LIWC features of character speeches
# into a CSV file that can be later parsed. It creates two files, one with
# each speech act as an entry, while another with each speaker_listener pair
# as an entry.
def writeLIWCFeatures(indFilename, mergedFilename, features, dictionary):
	outputInd = open(indFilename, 'wb')
	indWriter = csv.writer(outputInd, delimiter=',', quoting=csv.QUOTE_NONNUMERIC)
	outputMerged = open(mergedFilename, 'wb')
	mergedWriter = csv.writer(outputMerged, delimiter=',', quoting=csv.QUOTE_NONNUMERIC)
	# write the headers
	headers = ['speaker_listener']
	for scale in dictionary:
		headers.append(scale)
	indWriter.writerow(headers)
	mergedWriter.writerow(headers)
	# iterate through each speech act. write it to the individual csv file and merge it
	# into the featureMap for the merged csv file
	featureMap = {}
	for featurePair in features:
		characters = featurePair[0]
		length = featurePair[1]
		features = featurePair[2]
		# merge the entry into featureMap, or simply add it to the featureMap
		if characters in featureMap:
			mergedLength = featureMap[characters][0] + length
			mergedFeatures = {}
			for scale in features:
				mergedFeatures[scale] = features[scale] + featureMap[characters][1][scale]
			featureMap[characters] = (mergedLength, mergedFeatures)
		else:
			featureMap[characters] = (length, features)
		# write to the individual files
		indWriter.writerow(makeCSVRow(characters, length, features))
	# after processing each speech act, write the merged speech acts and features to the
	# merged file
	for characters in featureMap:
		featurePair = featureMap[characters]
		toWrite = False
		for scale in featurePair[1]:
			if featurePair[1][scale] != 0.0:
				toWrite = True
		if toWrite:
			mergedWriter.writerow(makeCSVRow(characters, featurePair[0], featurePair[1]))

if __name__ == "__main__":
	dictionary = getLIWCDictionary()
	for i in xrange(36):
		speeches = readTriples('triples/triples-' + str(i) + '.txt')
		features = featurizeSpeeches(dictionary, speeches)
		writeLIWCFeatures('Triples-LIWC/' + str(i) + '-individual-len.csv', 'Triples-LIWC/' + str(i) + '-merged-len.csv', features, dictionary)

	# combine files for each play into an aggregate
	indComb = open('Triples-LIWC/individual-combine-len.csv', 'wb')
	indWriter = csv.writer(indComb, delimiter=',', quoting=csv.QUOTE_NONNUMERIC)
	mergedComb = open('Triples-LIWC/merged-combinelen.csv', 'wb')
	mergedWriter = csv.writer(mergedComb, delimiter=',', quoting=csv.QUOTE_NONNUMERIC)

	# write the headers
	headers = ['speaker_listener']
	for scale in dictionary:
		headers.append(scale)
	indWriter.writerow(headers)
	mergedWriter.writerow(headers)

	for i in xrange(36):
		with open('Triples-LIWC/' + str(i) + '-individual-len.csv', 'r') as indFile:
			indFile.readline()
			lines = indFile.readlines()
			for line in lines:
				indComb.write(line)
		with open('Triples-LIWC/' + str(i) + '-merged-len.csv', 'r') as mergedFile:
			mergedFile.readline()
			lines = mergedFile.readlines()
			for line in lines:
				mergedComb.write(line)

				# ",0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0