class SpeechAct(object):

	def __init__(self, speaker, listeners, text):
		self.speaker = speaker
		self.listeners = listeners
		self.nListener = len(listeners)
		self.text = text
	def __str__(self):
		string = "Speaker: " + self.speaker + "\n"
		string += "Listners: " + str(self.listeners) + "\n"
		string += "Text: " + self.text
		return string


# This function parse the triple-*.txt files and convert the
# files into a list of tuples containing pairs of speakers 
# (following the convention speaker_listener) and the speech.
def readSpeechActs(filename):
	acts = []
	with open(filename, 'r') as f:
		while True:
			# process each speech block of the triple-*.txt file
			speaker = f.readline().strip()
			if speaker == "":
				break
			nSpeaker = int(float(f.readline()))
			listeners = []
			for i in xrange(nSpeaker):
				receiver = f.readline().strip()
				listeners.append(receiver)
			speech = ""
			while True:
				line = f.readline().strip()
				if line == "":
					break
				speech += " " + line
			acts.append(SpeechAct(speaker, listeners, speech))
	return acts

if __name__ == "__main__":
	acts = readSpeechActs('triples/triples-0.txt')
	print acts[0]