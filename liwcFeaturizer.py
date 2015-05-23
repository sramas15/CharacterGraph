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
	length = len(words)
	features = {}
	for scale in dictionary:
		pattern = dictionary[scale].pattern
		count = 0.
		for word in words:
			match = re.match(pattern, word)
			if match:
				count += 1.
		features[scale] = count / length
	return features

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

# This fcuntion featurizes the speeches between characters
# obtained from the triple-*.txt files using the LIWC features.
def featurizeSpeeches(dictionary, speeches):
	features = []
	for pair in speeches:
		speakers = pair[0]
		speech = pair[1]
		feature = liwcFeaturize(dictionary, speech)
		features.append((speakers, feature))
	return features

# This function writes the LIWC features of character speeches
# into a CSV file that can be later parsed.
def writeLIWCFeatures(outFilename, features, dictionary):
	output = open(outFilename, 'wb')
	csvWriter = csv.writer(output, delimiter=',', quoting=csv.QUOTE_NONNUMERIC)
	# write the headers
	headers = ['speaker_listener']
	for scale in dictionary:
		headers.append(scale)
	csvWriter.writerow(headers)
	# write the features
	for featurePair in features:
		row = [featurePair[0]]
		features = featurePair[1]
		for scale in features:
			row.append(features[scale])
		csvWriter.writerow(row)

if __name__ == "__main__":
	dictionary = getLIWCDictionary()
	speeches = readTriples('triples-0.txt')
	features = featurizeSpeeches(dictionary, speeches)
	writeLIWCFeatures('triple-0.csv', features, dictionary)