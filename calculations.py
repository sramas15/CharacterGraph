from distributedwordreps import *
import numpy as np

NUM_PLAYS = 1

for playNum in range(NUM_PLAYS):
	csvFile = 'matrices/matrix-'+str(playNum)+'.csv'
	mat, rownames, colnames = build(csvFile)
	print '***** INTERESTING THINGS FOR PLAY ', playNum, ' *****'

	mat_tfidf, rownames = tfidf(mat, rownames)

	topK = 5
	for index, pair in enumerate(rownames):
		# print 'TOP ', topK, ' NEIGHBORS FOR PAIR', pair
		# print neighbors(pair, mat, rownames)[:topK], '\n'
		print 'HIGHEST TF-IDF WORD FOR PAIR', pair
		row = mat_tfidf[index]
		# print row, np.amax(row)
		maxTFIDF = np.amax(row)
		maxWord = colnames[row.index(maxTFIDF)]
		print maxWord, '\t', maxTFIDF