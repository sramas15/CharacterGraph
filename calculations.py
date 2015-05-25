from distributedwordreps import *

NUM_PLAYS = 36

for playNum in range(NUM_PLAYS):
	csvFile = 'matrices/matrix-'+str(playNum)+'.csv'
	mat, rownames, colnames = distributedwordreps.build(csvFile)
	print '***** INTERESTING THINGS FOR PLAY ', playNum, ' *****'

	mat_tfidf, rownames = distributedwordreps.tfidf(mat, rownames)
	topK = 5
	for index, pair in enumerate(rownames):
		print 'TOP ', topK, ' NEIGHBORS FOR PAIR ', pair
		print distributedwordreps.neighbors(pair, mat, rownames)[:topK], '\n'
		print 'HIGHEST TF-IDF WORD FOR PAIR ', pair
		row = mat_tfidf[index]
		maxTFIDF = max(row)
		maxWord = colnames[row.index(maxTFIDF)]
		print maxWord, '\t', maxTFIDF