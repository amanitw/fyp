import csv
import fileinput
import linecache
import os
import collections
import sys
import csv
import numbers
import operator

#This is used to insert buggy program in input.csv file
'''
with open('inputs.csv', 'w', newline='\n') as file:
	writer = csv.writer(file)
	writer.writerow(["BuggyProgram","TestSuite"])
	writer.writerow(["middle.py","testSuiteMid.txt"])
	writer.writerow(["maximum.py","testSuiteMaximum.txt"])
	writer.writerow(["is_prime.py","testSuitePrime.txt"])
	
	
'''
class Line:
	def __init__(self,suspiciousScore=0.0, rank=0, text= "", lineNo=0):
		self.suspiciousScore = suspiciousScore
		self.rank = rank
		self.text = text
		self.lineNo = lineNo

	def setSuspiciousScore(self,suspiciousScore):
		self.suspiciousScore =suspiciousScore

	def setRank(self, rank):
		self.rank = rank 

	def setText(self, text):
		self.text = text

	def setLineNo(self,lineNo):
		self.lineNo = lineNo
	def __repr__(self):
		return str(self.lineNo)+" "+str(self.suspiciousScore)+" "+str(self.rank)+" "+self.text;
	def __gt__(self, line2):
		return self.rank > line2.rank


def trace(frame, event, arg):
	code=frame.f_code
	functionName=code.co_name
	if event == "line":
		lineNo = frame.f_lineno
		if lineNo<=fileLen:
			testToLines[testCase].append(lineNo)
			if lineNo  in lineToTests.keys():
				lineToTests[lineNo].append(i)
			else:
				lineToTests[lineNo]=[i]
	return trace

def fileLength(fileName,lines):
	with open(fileName) as f:	
		for i, l in enumerate(f):
			line=Line(0.0,0,l,i+1)
			lines.append(line)
	return i+1
	
def importFileNames(csvFile):
	with open(csvFile, 'r') as file:
		reader = csv.reader(file)
		i=0
		for row in reader:
			if i==0:
				i+=1
			else:
				testFileNames.append(row[0])
				testSuiteFileNames.append(row[1])
				
def fillTestCases(testSuiteFileName):
	testCases=[]
	with open(testSuiteFileName,"r") as file:
		while True:
			line1=file.readline().strip()
			try:
				test=tuple([int(x) for x in line1.split(' ')])
				line2=file.readline().strip()
				actualOutput=int(line2)
			except ValueError:
				break
			testCases.append((test,actualOutput))
	return testCases		
 
def getPassPercentage(lineNo,TestCases,totalPassedTestCase,resultOfTestCase):
	passed=0
	for tcNo in TestCases:
		if resultOfTestCase[tcNo]=="passed":
			passed+=1
	return (passed*100)/totalPassedTestCase
def getFailPercentage(lineNo,TestCases,totalFailedTestCase,resultOfTestCase):
	failed=0
	for tcNo in TestCases:
		if resultOfTestCase[tcNo]=="failed":
			failed+=1
	return (failed*100)/totalFailedTestCase
def assignSuspiciousScore(suspiciousScore,k,passPercentage,failPercentage):
	ss=failPercentage/(failPercentage+passPercentage)
	suspiciousScore[k]=ss
		
def findRanks(ranks,suspiciousScore):
	prev=-1
	rank=0
	for k in suspiciousScore:
		if suspiciousScore[k]!=prev:
			rank+=1
		prev=suspiciousScore[k]
		ranks[k]=rank
		
def makeListOfLineObject(lines,suspiciousScore,ranks):
	for itr in range(len(lines)):
		lines[itr].setSuspiciousScore(suspiciousScore[itr+1])
		lines[itr].setRank(ranks[itr+1])
		
def writeToOutputFile(fileWriter,suspiciousScore,lines):
	fileWriter.write("LineNo\tSuspicious_Score\tRank\t\tLine of code\n")
	for k in suspiciousScore:
		k-=1
		fileWriter.write(str(lines[k].lineNo)+"\t\t"+str(lines[k].suspiciousScore)+"\t\t"+str(lines[k].rank)+"\t\t"+lines[k].text+"\n")
	
	
	
	
#FILES_IMPORT
csvFile=sys.argv[1]
testFileNames=[]
testSuiteFileNames=[]
#import TestFileName and TestSuiteFileName
importFileNames(csvFile) 

#Trace each buggy program
for p in range(len(testFileNames)):
	#these are file names
	testFileName=testFileNames[p]
	testSuiteFileName=testSuiteFileNames[p]
	funName=os.path.splitext(testFileName)[0]
	outputFile="output"+str(p+1)+".txt"
	lines=[]
	fileLen=fileLength(testFileName,lines)#get file len and append all line object to lines list
	testCases=fillTestCases(testSuiteFileName)
	exec(open(testFileName).read())
	
	suspiciousScore={} #key:lineNo val:suspiciousScore
	ranks={} #key:lineNo val:rank
	testToLines = {} ## current testcase executes which set of lines
	lineToTests={} ## current line is executed by which testcases.
	resultOfTestCase={} ## key:testCaseNo val:result
	totalPassedTestCase=0
	totalFailedTestCase=0
	
	fileWriter=open(outputFile,'w')
	i=0
	for tup in testCases:
		i+=1
		testCase=tup[0]
		actualOutput=tup[1]
		testToLines[testCase]=[]
		sys.settrace(trace)
		exec('observedOutput=%s(*(testCase))' %funName)
		result=""
		if actualOutput==observedOutput:
			result="passed"
			totalPassedTestCase+=1
		else:
			result="failed"
			totalFailedTestCase+=1
		resultOfTestCase[i]=result;
		fileWriter.write("TestCase"+str(i)+": "+str(testCase)+"     Actual Output : "+str(actualOutput)+"\n")
		fileWriter.write("Observed Output : "+str(observedOutput)+"   TestResult : "+str(result)+"\n")
		fileWriter.write("Lines Covered: "+str(list(dict.fromkeys(testToLines[testCase])))+"\n")
		fileWriter.write("---------------------------------------------------------\n")
	
	
	##finding suspicious score of each line
	for l in range(len(lines)):
		suspiciousScore[l+1]=0.0
	for k in lineToTests:
		passPercentage=getPassPercentage(k,lineToTests[k],totalPassedTestCase,resultOfTestCase)
		failPercentage=getFailPercentage(k,lineToTests[k],totalFailedTestCase,resultOfTestCase)
		assignSuspiciousScore(suspiciousScore,k,passPercentage,failPercentage)
		
	##sort suspiciousScore dict based on values(i.e. score from high to low)	
	sortedList=sorted(suspiciousScore.items(), key=operator.itemgetter(1),reverse=True)	
	##converted list to dict.
	suspiciousScore=collections.OrderedDict(sortedList)
	##fill rank
	findRanks(ranks,suspiciousScore)
	
	##fill all the details of a line in line object,lines is list contain all line object
	makeListOfLineObject(lines,suspiciousScore,ranks)
	
	##maked output file output1/2/3.txt
	writeToOutputFile(fileWriter,suspiciousScore,lines);
	fileWriter.close();
	
	
	
	
	

