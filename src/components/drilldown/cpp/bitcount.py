def bitcount(result, past, future):
	if future == 0:
		result.append(str(past))
		return
	for i in [0, 1]:
		bitcount(result, past + i, future - 1)
		
def generate():	
	result = []
	bitcount(result, 0, 8)
	pp_result = []
	for i in range(16):
		pp_result.append(",".join(result[i * 16 : (i + 1) * 16]))
	print 'int bitcounts[] = {\n\t' + ",\n\t".join(pp_result) + '};'

if __name__ == "__main__":
	generate();