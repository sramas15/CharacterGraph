import re

UPPERCASE_CNM = re.compile(r"  [A-Z ]*\.")
UPPERCASE_CNM2 = re.compile(r"[A-Z ]*\.")
LOWERCASE_CNM = re.compile(r"  ([A-Z][a-z ]*)+\.")

def printCharSet(outF, characters):
	for char in characters:
		outF.write("%s\n" % char)

def GetCharacters(num_files=36, inPtrn="full_text/out-%d.txt", outPtrn="char_list/char-%d.txt"):
	match = UPPERCASE_CNM.search("                          SCENE XIII.")
	print match.group()[2] != " "
	for i in range(num_files):
		inFNm = inPtrn % i
		outFNm = outPtrn % i
		title = None
		characters = set()
		with open(inFNm, "r") as fIn:
			for line in fIn:
				if not title:
					title = line.strip()
					continue
				match = UPPERCASE_CNM.search(line)
				if match and match.start() == 0 and match.group()[2] != " ":
					char = match.group().strip(" .")
					characters.add(char)
				#match = LOWERCASE_CNM.search(line)
				#if match and match.start() == 0 and match.group()[2] != " ":
			#		char = match.group().strip(" .")
			#		characters.add(char)
		with open(outFNm, "w") as fOut:
			fOut.write("%s\n" % title)
			printCharSet(fOut, characters)

def GetCharactersSingleFile(inFNm="full_text/out-3.txt", outFNm = "char_list/char-3.txt"):
	title = None
	characters = set()
	with open(inFNm, "r") as fIn:
		for line in fIn:
			if not title:
				title = line.strip()
				continue
			match = UPPERCASE_CNM2.search(line)
			if match and match.start() == 0:
				char = match.group().strip(" .")
				characters.add(char)
	with open(outFNm, "w") as fOut:
		fOut.write("%s\n" % title)
		printCharSet(fOut, characters)


if __name__ == "__main__":
	GetCharacters()
