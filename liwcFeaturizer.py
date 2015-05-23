import pickle
import re

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

def readTriples(filename):
	speeches = []
	with open(filename, 'r') as f:
		while True:
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

if __name__ == "__main__":
	dictionary = getLIWCDictionary()
	speeches = readTriples('triples-0-small.txt')
	features = []
	for pair in speeches:
		speakers = pair[0]
		speech = pair[1]
		feature = liwcFeaturize(dictionary, speech)
		features.append((pair, feature))
	print len(features)
	print features[2]