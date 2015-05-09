import re

UPPERCASE_CNM = re.compile(r"  [A-Z]*\.")
LOWERCASE_CNM = re.compile(r"  [A-Z][a-z]*\.")

def printCharSet(outF, characters):
	for char in characters:
		outF.write("%s\n" % char)

def GetCharacters(num_files=35, inPtrn="out-%d.txt", outPtrn="char-%d.txt"):
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
				if match and match.start() == 0:
					char = match.group().strip(" .")
					characters.add(char)
				match = LOWERCASE_CNM.search(line)
				if match and match.start() == 0:
					char = match.group().strip(" .")
					characters.add(char)
		with open(outFNm, "w") as fOut:
			fOut.write("%s\n" % title)
			printCharSet(fOut, characters)

if __name__ == "__main__":
	GetCharacters()
