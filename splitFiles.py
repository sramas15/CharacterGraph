import sys

def split_file(inFNm="CompleteWorksCleaned.txt", end_token="THE END", file_format="out-%d.txt"):
	with open(inFNm, "r") as fIn:
		file_nm = 0
		fOut = open(file_format % file_nm, "w")
		for line in fIn:
			fOut.write(line)
			if line.strip() == end_token:
				fOut.close()
				file_nm += 1
				fOut = open(file_format % file_nm, "w")
		fOut.close()


if __name__ == "__main__":
	split_file()