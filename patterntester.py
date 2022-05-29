def patterntester(String):
	inputString = String
	print("Pattern is: "+ inputString)	
	knownpatterns = []

	for line in open('knownpatterns.txt', "r"):
    		knownpatterns.append(line.rstrip('\n'))

	for line in knownpatterns:
    		if (line in inputString):
        		if (line != ''):
            		print("Line is: " +line)
            		print("Sql Injection Detected")
        



