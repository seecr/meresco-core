from sys import argv, stdout

if len(argv) < 2:
    print 'Usage:', argv[0], '<path to index>'
    exit(0)

indexPath = argv[1]

from PyLucene import IndexReader

reader = IndexReader.open(indexPath)
numDocs = reader.numDocs()
print 'Opened', indexPath, 'with', numDocs, 'documents'
termDocs = reader.termDocs()
termEnum = reader.terms()
dfFreq = {}
stopwords = []
l, t, f = 0, 0, 0
while termEnum.next():
	term = termEnum.term()
	l += len(term.text())
	t += 1
	ft = termEnum.docFreq()
	dff = 100*ft/numDocs/10 * 10
	if dff not in dfFreq:
		dfFreq[dff] = 1
	else:
		dfFreq[dff] += 1
	if ft > numDocs*0.9:
		stopwords.append((term.text(), ft))
	f += ft
	if t % 10000 == 0: print 'Analyzing terms:', t, '\r',
	stdout.flush()
atl = float(l)/t
adf = float(f)/t
print 'Terms:', t, 'Average term lenght:', atl, 'Average doc freq:', adf
termDictSize = t * atl*16
matrixSize = t * adf*64
x64 = (termDictSize + matrixSize) /8 /1024 /1024 /1024
print 'With postings of 64 bits, an index would require', x64, 'GB.'
print 'TermDict:', termDictSize/8/1024/1024/1024, 'Matrix:', matrixSize/8/1024/1024/1024
print 'TF distributie'
for r in sorted(dfFreq.keys()):
	print 'from', r,'% :',dfFreq[r]
print 'Stopwords:', len(stopwords), 'save', sum(f for sw, f in stopwords)*64/8/1024/1024, 'MB'
for s, f in stopwords:
	print s, 100*f/numDocs, '%'
