import statistics as statistics
import re as re
import datetime as datetime
import os as os


#Plotting libraries
import bokeh
import bokeh.plotting
import bokeh.models
from bokeh.plotting import figure, output_file, show, ColumnDataSource
from bokeh.models import HoverTool, PointDrawTool, Span
from bokeh.layouts import widgetbox, column
from bokeh.models.widgets import DataTable, DateFormatter, TableColumn
from bokeh.io import curdoc, reset_output
from screeninfo import get_monitors
import numpy as np

#GUI libraries
import tkinter as tk
from tkinter import ttk, filedialog, font, messagebox, Scale

#Local libraries
import coreClasses as coreC


#Return mean of temperatures in radius around given index
def adjacentMean(gui, index):
	radius = int(gui.adjMeanRadE.get())
	tempers = []

	#Append temperatures surrounding provided index, pass if index out of range
	for i in range(1, radius + 1):
		try:
			tempers.append(float(gui.masterList[index - i][gui.tempsCol]))
		except:
			pass
			
		try:
			tempers.append(float(gui.masterList[index + i][gui.tempsCol]))
		except:
			pass
			
	#Append temperature at index itself
	tempers.append(float(gui.masterList[index][gui.tempsCol]))
	#Get mean of temperatures discoverd within radius
	adjMean = statistics.mean(tempers)
	return adjMean
	
	
def getTime(gui, index):
	time = re.search("(\d+:\d+)", gui.masterList[index][gui.dateTimesCol])
	return time.group(1)
	
def getDate(gui, index):
	date = re.search("\d+\/\d+\/\d+", gui.masterList[index][gui.dateTimesCol])
	return date.group(0)
	
#Check for significant upward or downward trend
def sigChange(gui, boutType, curIndex, stop):
	indexThreshOn = int(round(float(gui.timeThreshAdvOnE.get())))
	indexThreshOff = int(round(float(gui.timeThreshAdvOffE.get())))
	
	
	
	#Looking for on bout
	if boutType == "off":
		#Check if at end of masterList
		if (curIndex + indexThreshOn) < stop:
			#Check if increasing
			if adjacentMean(gui, (curIndex + indexThreshOn)) > adjacentMean(gui, curIndex):
				#Check if increasing consistently over range
				threshold = indexThreshOn
				if checkInc(gui, curIndex, threshold):
					return True
	#Looking for off bout
	else:
		#Check if at end of masterList
		if (curIndex + indexThreshOff) < stop:
			#Check if decreasing
			if adjacentMean(gui, (curIndex + indexThreshOff)) < adjacentMean(gui, curIndex):
				#Check if decreasing consistently over range
				threshold = indexThreshOff
				if checkDec(gui, curIndex, threshold):
					return True
					
	#Return False if no significant trend detected				
	return False

	
#Check if temperature is decreasing over the defined time range
def checkDec(gui, index, threshold):
	# leniency = int(gui.leniencyOffE.get())
	leniency = 0
	offense = 0
	
	for i in range(0, threshold):
		#Check if end of gui.masterList
		if (index + i) < (len(gui.masterList) - 2):
			if adjacentMean(gui, (index + i)) < adjacentMean(gui, (index + i + 1)):
				offense += 1
				if offense > leniency:
					#Return false if increase detected
					return False
	
	return True
	
#Check if temperature is increasing over the defined time range
def checkInc(gui, index, threshold):
	# leniency = int(gui.leniencyOnE.get())
	leniency = 0
	offense = 0
	
	for i in range(0, threshold):
		#Check if end of gui.masterList
		if (index + i) < (len(gui.masterList) - 2):
			if adjacentMean(gui, (index + i)) > adjacentMean(gui, (index + i + 1)):
				offense += 1
				if offense > leniency:
					#Set inc to False if increase detected
					return False
			
	return True
	
#Find highest or lowest temperature in a given range of indices
def findVertexI(gui, vertType, leftLim, rightLim):	
	vertIndex = None
	if rightLim >= len(gui.masterList):
		rightLim = (len(gui.masterList) - 1)
	
	if vertType == "offStart":
		#Looking for maximum
		tempMax = gui.masterList[leftLim][gui.tempsCol]
						
		#Find highest temperature between left-side limit and right-side limit
		for subIndex in range(leftLim, (rightLim + 1)):
			if float(gui.masterList[subIndex][gui.tempsCol]) >= float(tempMax):
				tempMax = gui.masterList[subIndex][gui.tempsCol]
				vertIndex = subIndex
	elif vertType == "onStart":
		#Looking for minimum
		tempMin = gui.masterList[leftLim][gui.tempsCol]
				
		#Find lowest temperature between last vertex and right-side limit
		for subIndex in range(leftLim, (rightLim + 1)):
			try:
				if float(gui.masterList[subIndex][gui.tempsCol]) <= float(tempMin):
					tempMin = gui.masterList[subIndex][gui.tempsCol]
					vertIndex = subIndex
			except:
				pass
	
	#Return index of found vertex
	if vertIndex is None:
		vertIndex = rightLim
	return vertIndex

#Returns slope between given index and index + set slope range
def checkSlopeSimple(gui, index, minSlope, slopeRange):
	if minSlope == 0:
		return True
	
	temper1 = adjacentMean(gui, index)
	temper2 = adjacentMean(gui, (index + slopeRange))
	
	slope = ((temper2 - temper1) / slopeRange)

	#Off-bout slopes are less than 0
	if minSlope < 0:
		if slope <= minSlope:
			return True
	#On-bout slopes are greater than 0
	elif minSlope > 0:
		if slope >= minSlope:
			return True
			
	return False

#Check if time passed to function is within daytime range
def checkDaytime(dayStart, nightStart, time):
	daytime = True

	#Convert dayStart time to float
	day = re.search("(\d+)(:)(\d+)", dayStart)
	dayNum = float(day.group(1)) + (float(day.group(3)) / 60)
	
	#Convert nightStart time to float
	night = re.search("(\d+)(:)(\d+)", nightStart)
	nightNum = float(night.group(1)) + (float(night.group(3)) / 60)
	
	#Convert time passed to float
	curTime = re.search("(\d+)(:)(\d+)", time)
	timeNum = float(curTime.group(1)) + (float(curTime.group(3)) / 60)
	
	#Check if not in daytime range
	if (timeNum > nightNum) or (timeNum < dayNum):
		daytime = False
	
	#Return true if time passed is within daytime range
	return daytime
	
#Split data into day and night objects
def splitDays(gui, daysList, nightsList, modifier = 0):
	#Increment time by modifier value
	def modTime(oriTime):	
		if modifier is 0:
			newTime = (" " + oriTime.strip())
		else:
			#Convert csv time value to datetime format
			search = re.search("((\d+):(\d+))", oriTime)
			hour = int(search.group(2))
			minute = int(search.group(3))
			time = datetime.datetime(1, 1, 1, hour, minute, 0)
			
			#Add modifer and strip unnecessary info
			newTime = (time + datetime.timedelta(minutes = modifier))
			newTime = str(newTime)[11:-3]
			if newTime[0] is "0":
				newTime = newTime[1:]		
		
		#Return modified time
		return(" " + newTime.strip())


	#Set to False when end of list is encountered
	dayValid      = True
	dayStart = modTime(gui.dayStart)
	nightStart = modTime(gui.nightStart)
	dayDur        = getDayDur(dayStart, nightStart)
	nightDur      = (1440 - dayDur)
	dayInterval   = (1440 / gui.interval)
	# cur = current
	curDay        = -1
	curNight      = -1
	
	
	
	#Look for first day or night
	for i in range(0, len(gui.masterList)):
		#If dayStart found before nightStart
		if re.search(dayStart, gui.masterList[i][gui.dateTimesCol]):
			#Set start of first day to this index
			curDay = i
			#Set start of first night to day index + duration of daytime
			curNight = (i + (dayDur / gui.interval))
			#Check if this sets curNight past length of gui.masterList
			if curNight > (len(gui.masterList) - 1):
				dayValid = False
				curNight = (len(gui.masterList) - 1)
				daysList.append(coreC.block(gui, curDay, curNight - 1, True))
				
			break
		#If nightStart found before dayStart
		elif re.search(nightStart, gui.masterList[i][gui.dateTimesCol]):
			#Set start of first night to this index
			curNight = i
			#Set start of first day to night index + duration of nighttime
			curDay = (i + (nightDur / gui.interval))
			#Check if this sets curDay past length of gui.masterList
			if curDay > (len(gui.masterList) - 1):
				dayValid = False
				curDay = (len(gui.masterList) - 1)
				
			break
	
	#Check if data starts at night and process to achieve uniformity going into following while `
	#Catch partial day at start of gui.masterList
	if curNight < curDay:
		daysList.append(coreC.block(gui, 0, curNight - 1, True))
		nightsList.append(coreC.block(gui, curNight, curDay - 1, not dayValid))
		curNight += dayInterval
	#Catch partial night at start of gui.masterList
	elif curDay < curNight:
		nightsList.append(coreC.block(gui, 0, curDay - 1, True))
	#If neither dayStart or nightStart found, append partial day or night
	elif curDay == curNight:
		dayValid = False
		if checkDaytime(dayStart, nightStart, gui.masterList[0][gui.dateTimesCol]):
			daysList.append(coreC.block(gui, 0, (len(gui.masterList) - 1), True))
		else:
			nightsList.append(coreC.block(gui, 0, (len(gui.masterList) - 1), True))
			
	#Save each day and night as object
	while dayValid:
			daysList.append(coreC.block(gui, curDay, curNight - 1, False))
			curDay += dayInterval
			
			#Make final night stop at end of gui.masterList
			if curDay > len(gui.masterList):
				curDay = (len(gui.masterList) - 1)
				nightsList.append(coreC.block(gui, curNight, curDay - 1, True))
				dayValid = False
				break
			else:
				nightsList.append(coreC.block(gui, curNight, curDay - 1, False))
				curNight += dayInterval
			
			#Make final day stop at end of gui.masterList
			if curNight > len(gui.masterList):
				curNight = (len(gui.masterList) - 1)
				daysList.append(coreC.block(gui, curDay, curNight - 1, True))
				dayValid = False
	
	#Address problem of start time skipping
	if len(daysList) is 0 or len(nightsList) is 0:
		if (modifier + 1) < gui.interval:
			#Clear lists
			daysList.clear()
			nightsList.clear()
			#Recursively call splitDays with incremented modifier
			splitDays(gui, daysList, nightsList, (modifier + 1))
		#If no days or nights still found, provide text warning
		else:
			messagebox.showwarning("Warning", 
			("If daytime or nighttime periods are not being properly detected, make sure the Data Time Interval provided on the Main tab is correct."))

			

#Retrieve duration of daytime in minutes
def getDayDur(dayStart, nightStart):
	#Convert dayStart time to float
	day = re.search("(\d+)(:)(\d+)", dayStart)
	dayNum = float(day.group(1)) + (float(day.group(3)) / 60)
	
	#Convert nightStart time to float
	night = re.search("(\d+)(:)(\d+)", nightStart)
	nightNum = float(night.group(1)) + (float(night.group(3)) / 60)
	
	#Convert to minutes
	dayDur = ((nightNum - dayNum) * 60)	
	
	return dayDur
	

#Check if initial slope meets user defined minimum
def checkSlopeRegression(gui, index, offBout, raw = False):
	if offBout:
		minSlope = float(gui.minSlopeOffE.get())
		slopeRange = int(gui.slopeRangeOffE.get())
	else:
		minSlope = float(gui.minSlopeOnE.get())
		slopeRange = int(gui.slopeRangeOnE.get())

	if not raw:
		if minSlope == 0:
			return True
		
	xs = []
	ys = []
		
	for i in range(0, (slopeRange + 1)):
		#Check if end of gui.masterList
		if (index + i) < (len(gui.masterList) - 2):
			xs.append(gui.masterList[index + i][0])
			ys.append(gui.masterList[index + i][2])

	xArray = np.array(xs, dtype = np.float64)
	yArray = np.array(ys, dtype = np.float64)
	
	if len(xArray) == 0 or len(yArray) == 0:
		return False
	
	
	slope = (((statistics.mean(xArray) * statistics.mean(yArray)) - statistics.mean(xArray * yArray)) / ((statistics.mean(xArray) ** 2) - statistics.mean(xArray ** 2)))
	
	if raw:
		return slope

	
	if offBout:
		if slope >= minSlope:
			return True
	else:
		if slope <= minSlope:
			return True

	return False

	
def checkValidSlope(gui, block, i, boutType, minSlope, slopeRange):
	#Set start of search to index of next vertex if it exists			
	if (i + 1) < len(block.vertices):
		start = (block.vertices[i + 1].index - slopeRange)
	#If there is not another vertex, set start to end of block
	else:
		start = (block.stop - slopeRange)
		
	valid = False
	for x in range(start, block.vertices[i].index, -1):
		if checkSlopeSimple(gui, x, minSlope, slopeRange):
			valid = True
			break
			
	return valid

def resyncVertTypes(block):
	type = block.vertices[0].vertType
	
	for vertex in block.vertices:
		vertex.vertType = type
		if type == "offStart":
			type = "onStart"
		else:
			type = "offStart"
	
def checkAlternatingTemps(block):
	changeMade = True
	while changeMade:
		changeMade = False
		resyncVertTypes(block)
		for i in range(1, len(block.vertices)):
		#(flag)
			# print("type =", block.vertices[i].vertType)
			# print("temp i - 1 =", block.vertices[i - 1].temp)
			# print("temp i =", block.vertices[i].temp)
			if block.vertices[i].vertType == "offStart":
				if block.vertices[i - 1].temp > block.vertices[i].temp:
					block.vertices.pop(i - 1)
					changeMade = True
					break
			else:
				if block.vertices[i - 1].temp < block.vertices[i].temp:
					block.vertices.pop(i - 1)
					changeMade = True
					break

	
def sequentialDPWarn(gui, masterList):
	#Check if data points are sequential and continuous
	prevIndex = masterList[0][gui.dataPointCol]
	first = True
	lineNum = 1
	for line in masterList:
		if not first:
			try:
				if not int(line[gui.dataPointCol]) == (int(prevIndex) + 1):
					messagebox.showwarning("Data Point Warning", 
					("Warning on line " + str(lineNum) + ". Data point number is not sequential with regrad to previous index.  This could result in incorrect statistical output."))
					return False	
			#If int conversion fails, just pass: will be detected with checkInFile
			except ValueError:
				pass
		else:
			first = False
			
		lineNum += 1	
		prevIndex = line[gui.dataPointCol]
	
#Create masterList from input csv file and format appropriately
def prepareList(gui, sourceFile):
	popCount   = 0
	popindices = []
	masterList = []
	
	#Open, read, and split csv file into masterList 
	csv = open(sourceFile, 'r')
	lines = csv.readlines()
	csv.close()
	
	for line in lines:
		masterList.append(line.split(","))
		
	for i in range(0, (len(masterList) - 1)):
		#Record indices of lines not conforming to expected format (This line deletes headers)
		if not re.search("\d", masterList[i][gui.dataPointCol]):
			popindices.append(i)
		#If incubation temperature is absent, set equal to previous temperature
		elif not re.search("(\d)+(\.)?((\d)?)+", masterList[i][gui.tempsCol]):
			try:
				masterList[i][gui.tempsCol] = float(masterList[i - 1][gui.tempsCol])
			except:
				masterList[i][gui.tempsCol] = 0
			
	#Delete extra line created as a result of the above for loop		
	del masterList[-1]
	
	#Remove lines not conforming to format
	for index in popindices:
		masterList.pop(index - popCount)
		popCount += 1
	
	#Clear formatting characters sometimes present on first position
	search = re.search("\d+", masterList[0][gui.dataPointCol])
	masterList[0][gui.dataPointCol] = search.group(0)
	
	sequentialDPWarn(gui, masterList)
	
	return masterList
	
def detectVertType(gui, userVertIs):
	pass
	

#Extract datapoints corresponding to vertices placed by user
def extractDPsFromHTML(gui, file):
		DPList = []
		
		#Get lines of HTML file
		with open(file, "r") as htmlFile:
			htmlLines = htmlFile.readlines()
			
		#Remove superfluous lines of table data if present
		found = False
		with open(file, "w") as htmlFile:
			for line in htmlLines:
				#Search for vertex data containing line
				if not line.find("<div class") == -1:
					#Retain the first
					if not found:
						found = True
						htmlFile.write(line)
					#Discard all others
					else:
						pass
				#Retain all non-table data containing lines
				else:
					htmlFile.write(line)				
		
		#Now proceed with file purged of curropting data lines
		with open(file, "r") as htmlFileClean:
			htmlCont = htmlFileClean.read()
			
		#Gets all data points and temperatures from table
		tokens = re.finditer("((\d+\.)?\d+)</span>", htmlCont)
		
		type = "DP"
		for match in tokens:
			if type == "DP":
				#Add data point to list if not a duplicate
				dataPoint = round(float(match.group(1)))
				if dataPoint not in DPList:
					DPList.append(dataPoint)
	
				type = "temp"
			#Ignore temperatures
			else:
				type = "DP"
	
		#Return sorted list of datapoints
		return sorted(DPList)
	
#Extract vertices corresponding to certain window of the input file
def extractVertsInRange(gui, totalVerts, startIndex, stopIndex):
	subVerts = []
	leftLim = 0
	rightLim = 0
	#Check if any vertices are present
	if len(totalVerts) < 1:
		return subVerts
	#Check if stop index is lower than lowest present in vertex list, return empty list
	if stopIndex < totalVerts[0].index:
		return subVerts
	#Check if start index is greater than greatest present in vertex list, return empty list
	if startIndex > totalVerts[-1].index:
		return subVerts
	
	#Find first vertex over start index and set as left limit
	for i in range(len(totalVerts)):
		if totalVerts[i].index >= startIndex:
			leftLim = i
			break
		
	#Find first vertex under stop index and set as right limit
	for i in range((len(totalVerts)- 1), -1, -1):
		if totalVerts[i].index <= stopIndex:
			rightLim = i
			break
			
	#Return vertices in desired rane
	subVerts = totalVerts[leftLim:(rightLim + 1)]
	return subVerts	
	
#Create vertices based on provied datapoints
def extractVertsFromDPs(gui):
	vertices = []
	userVertDPs = extractDPsFromHTML(gui, gui.vertexFileE.get())
	for i in range(len(gui.masterList)):
		#Search for gap between index value and corresponding datapoint
		if int(gui.masterList[i][gui.dataPointCol]) == int(userVertDPs[0]):
			#Delta is discrepency between index and data point number
			delta = (userVertDPs[0] - i)
			break
			
	firstVertTemp = gui.masterList[userVertDPs[0] - delta][gui.tempsCol]
	secondVertTemp = gui.masterList[userVertDPs[1] - delta][gui.tempsCol]
	
	#Determine if first vertex is an offStart or onStart
	if firstVertTemp > secondVertTemp:
		vertType = "offStart"
	else:
		vertType = "onStart"
	
	#(flag) this could lead to some issues due to invalid assumption
	for dataPoint in userVertDPs:
		index = (dataPoint - delta)
		vertices.append(coreC.vert(index, gui.masterList[index][gui.tempsCol], vertType))
		if vertType == "offStart":
			vertType = "onStart"
		elif vertType == "onStart":
			vertType = "offStart"
		
	return vertices
		
#Extract only section of masterList corresponding to user selected vertices
def sliceMasterList(gui, userVertDPs):
	start = None
	stop = None
	firstVertI = None
	
	#If no user vertices provided, return whole list
	if len(userVertDPs) < 1:
		return gui.masterList

	#Get average distance between vertices
	deltas = []
	for x in range(len(userVertDPs) - 2):
		deltas.append(userVertDPs[x + 1] - userVertDPs[x])
		
	averageDelta = statistics.mean(deltas)
	
	#Buffer is number of data points  before the start and after the stop to be collected
	buffer = round((averageDelta / 2))
	
	found = False
	for x in range(len(gui.masterList)):
		#Find index number corrisponding to vertex data point
		if int(gui.masterList[x][gui.dataPointCol]) == userVertDPs[0]:
			firstVertI = x
			#Start at vertex index minus buffer and move right until valid index encountered
			for i in range((round(firstVertI - buffer)), firstVertI):
				if not i < 0:
					start = i
					found = True
					break
		#Break once valid vertex found
		if found:
			break
	
	if firstVertI is None:
		return False
	
	#Determine last possible index value
	lastVertI = (firstVertI + (userVertDPs[-1] - userVertDPs[0]))
	found = False
	
	#Start at last vertex plus buffer and move left until valid index encountered
	for i in range ((lastVertI + buffer), lastVertI, -1):
		if not i >= len(gui.masterList):
			stop = i
			break
		#Break once valid vertex found
		if found:
			break
	
	#If no valid vertex found for start or stop
	if start is None:
		start = 0
	if stop is None:
		stop = (len(gui.masterList) - 1)
			
	#Return reduced master list
	splitList = gui.masterList[start:(stop + 1)]
	return splitList
			
#Identify bouts and save as bout object
def getBouts(gui, block):
	verts = block.vertices
	#Return if no vertices provided
	if verts == None or len(verts) < 2:
		return
		
	for i in range(0, (len(verts) - 1)):
		#Append off-bout
		if verts[i].vertType == "offStart":
			block.bouts.append(coreC.bout(gui, verts[i].index, verts[i + 1].index, "off"))
			block.offCount += 1
		#Append on-bout
		elif verts[i].vertType == "onStart":
			block.bouts.append(coreC.bout(gui, verts[i].index, verts[i + 1].index, "on"))
			block.onCount += 1

#Create DN (day/night) pair objects
def getPairs(gui, daysList, nightsList, pairsList):
	#Set modifier based on if day or night comes first
	if daysList[0].start > nightsList[0].start:
		modifier = 1
	else:
		modifier = 0
			
	for i in range(len(daysList)):
		#If there is a night corrisponding with the day at index i
		if (i + modifier) < (len(nightsList)):
			#Create pair if both daytime and nightime are complete
			if not daysList[i].partial and not nightsList[i + modifier].partial:
				pairsList.append(coreC.block(gui, daysList[i].start, nightsList[i + modifier].stop, False))

#Warns user not to drag existing vertices while in edit mode				
def dragWarn(gui):
	if gui.dragWarnConfig.lower() == "yes":
		if not messagebox.askyesno("WARNING", ("Do NOT drag existing vertices.  To \"move\" a vertex, you must select it (left click), delete it (backspace), and place a new vertex (left click) where you wish.  However, newly placed vertices CAN be dragged with no issues.\n\n Continue to show this warning in the future?")):
			with open(os.path.join(gui.coreDir, "config_files", "defaultConfig.ini"), "w") as configFile:
			# with open("./../config.ini", "w") as configFile:		
				gui.config.set("Main Settings", "drag_warn", "no")
				gui.config.write(configFile)
			gui.dragWarnConfig = "no"

#Warns user if a valid air temperature column is not detected
def airTempWarn(gui, dataPoint, type):
	response = False
	if gui.airWarnConfig.lower() == "yes":
		if type == "missing":
			if messagebox.askyesno("Air Temperature Warning", ("No air temperature detected for data point " + dataPoint + ". Air temperatures will not be plotted or included in statistical output.\n\n Continue to show this warning in the future?")):
				response = True
		elif type == "invalid":
			if messagebox.askyesno("Air Temperature Warning", ("Invalid air temperature detected for data point " + dataPoint + ". Air temperatures will not be plotted or included in statistical output.\n\n Continue to show this warning in the future??")):
				response = True
			
		#Rewrite config file to disable air temperature warning
		if response is False:
			with open(os.path.join(gui.coreDir, "config_files", "defaultConfig.ini"), "w") as configFile:
			# with open("./../config.ini", "w") as configFile:		
				gui.config.set("Main Settings", "air_temp_warn", "no")
				gui.config.write(configFile)
			gui.airWarnConfig = "no"
			
			
			
	
			
#Generate plot
def graph(gui, daysList, nightsList, masterBlock, plotVertices = True, showDragWarn = False):
	bulkvertices = []
	vertX        = []
	vertY        = []
	masterX      = []
	masterY      = []
	airX         = []
	airY         = []
	monResList   = []
	
	#Clears previous graphs from memory
	reset_output()
	
	if plotVertices:
		#Add daytime period delimiting lines if appropriate
		if gui.restrictSearchBV.get() is True:
			for day in daysList:
				if len(day.vertices) > 0:
					#Add vertex at 0 to mark begining of day
					bulkvertices.append(coreC.vert(day.vertices[0].index, np.nan, day.vertices[0].vertType))
					#Get all vertices from bouts
					bulkvertices += day.vertices
					#Add vertex at 0 to mark end of day
					bulkvertices.append(coreC.vert(day.vertices[-1].index, np.nan, day.vertices[-1].vertType))
		#Else compile vertices for entire input file
		else:
			bulkvertices = masterBlock.vertices
			
		#Compile index number and temperature of all vertices
		for vertex in bulkvertices:
			vertX.append(gui.masterList[vertex.index][gui.dataPointCol])
			vertY.append(vertex.temp)
			
		#Output to HTML file
		output_file(gui.graphName)
	else:
		output_file(os.path.join(gui.coreDir, "misc_files", "tempGraph.html"))
	
	#Create column data source for vertex data so it can be manipulated in the interactive plot
	boutsSourceData = ColumnDataSource(data = dict(x = vertX, y = vertY))
	
	#Compile index number and temperature for every line in input file
	for line in gui.masterList:
		masterX.append(int(line[gui.dataPointCol]))
		masterY.append(float(line[gui.tempsCol]))
		
		#Compile air temperature if a valid column is present
		if gui.airValid is True:
			airX.append(int(line[gui.dataPointCol]))
			airY.append(float(line[gui.airTempCol]))
		
	
	#Set plot dimensions
	if gui.plotDimVar.get() is 1:
		#Get monitor resolution if "auto" selected
		for monitor in get_monitors():
			monResList.append(str(monitor))	
		
		#Extract monitor width and height
		resRE = re.search("(\d+)x(\d+)", monResList[0])
		monX = int(resRE.group(1))
		monY = int(resRE.group(2))
		plotX = (monX - 200)
		plotY = (monY - 200)
	#Get user dimension values if "manual" selected
	else:
		plotX = int(gui.plotDimXE.get())
		plotY = int(gui.plotDimYE.get())
	
	#Initialize hover tool (provides information about individual datapoints)
	hover = HoverTool(tooltips=[("Data Point", "$x{int}"), ("Temperature", "$y")])

	#(flag) may not be neccessary
	# for y in masterY:
		# float(y)
	
	#Get name of plot
	if plotVertices:
		plotName = gui.graphName[:-5]
	else:
		#Get input file root name
		tempRE = re.search((".*\."), os.path.basename(os.path.normpath(gui.inputFileAdvE.get())))
		#Assign default plot name
		if tempRE:
			plotName = tempRE.group(0)[:-1]
		else:
			plotName = os.path.basename(os.path.normpath(gui.inputFileAdvE.get()))

	#Detect best y axis range
	if gui.airValid is True:
		yMin = (float(min(min(masterY), min(airY))) - 2)
		yMax = (float(max(max(masterY), max(airY))) + 2)
	else:
		yMin = (float(min(masterY)) - 2)
		yMax = (float(max(masterY)) + 2)
		
	#Create core plot
	plot  = figure(tools = [hover, "box_zoom, wheel_zoom, pan, reset, save"],
				   x_range = [int(masterX[0]), int(masterX[len(masterX) - 1])],
				   y_range = [yMin, yMax],
				   # y_range = [float(min((float(min(airY)), float(min(masterY)))) - 2), (max(max(airY), max(masterY)) + 2)], 
				   title = plotName,
				   x_axis_label= "Data Point", y_axis_label = "Temperature (C)", plot_width = plotX, plot_height = plotY)
				   
	
	#Add vertical lines delimiting days
	if gui.showDayDelimsBV.get() is True:
		for day in daysList:
			vline = Span(location = int(gui.masterList[day.start][gui.dataPointCol]), dimension = "height",
				    line_color = gui.dayMarkerColorVar.get(), line_width = float(gui.dayMarkerSize_E.get()), line_alpha = 0.6)
			plot.renderers.extend([vline])
	
	#Get size settings from GUI
	plot.title.text_font_size = (gui.titleFontSizeE.get() + "pt")
	plot.axis.axis_label_text_font_size  = (gui.axisTitleFontSizeE.get() + "pt")
	plot.axis.major_label_text_font_size  = (gui.axisLabelFontSizeE.get() + "pt")	
	plot.axis.major_tick_line_width = int(gui.axisTickSizeE.get())
	plot.axis.minor_tick_line_width = int(gui.axisTickSizeE.get())
	plot.axis.major_tick_out = int(gui.axisTickSizeE.get())
	plot.axis.minor_tick_out = int(gui.axisTickSizeE.get())

	#Append vertex x and y values to data dictionary
	data = {"x": [], "y": []}
	for x in vertX: data["x"].append(x)
	for y in vertY: data["y"].append(y)
	
	#Generate table with vertex information
	src = ColumnDataSource(data)
	columns = [
				TableColumn(field = "x", title = "Data Point"),
				TableColumn(field = "y", title = "Temperature")
			  ]
	data_table = DataTable(source = src, columns = columns, width = 500, height = 20000)
	
	if gui.editModeBV.get():
		#Show drag warning if applicable
		if showDragWarn:
			dragWarn(gui)
			
		#Plot air temperatures
		if gui.showAirTempBV.get() is True and gui.airValid:
			# plot.circle(airX, airY, size = 5, color = "black", alpha = 1, legend = "Air Temeprature")
			plot.line(airX, airY, line_width = float(gui.airTempSize_E.get()), color = gui.airTempColorVar.get(), line_alpha = 1, legend = "Air Temeprature")
		
		#Plot egg temperatures
		plot.circle(masterX, masterY, size = float(gui.eggTempPointSize_E.get()), color = gui.eggTempPointColorVar.get(), legend = "Egg Temperature")
		plot.line(masterX, masterY, line_width = float(gui.eggTempLineSize_E.get()), color = gui.eggTempLineColorVar.get())

		#Plot verticies as large circles if edit mode selected
		renderer = plot.circle  (
									"x",
									"y",
									size = (float(gui.boutSize_E.get()) * 3),
									color = "black",
									fill_color = gui.boutColorVar.get(),
									fill_alpha = 0.8,
									legend = "Prediced Incubation Shift",
									source = src
								)
		
		draw_tool = PointDrawTool(renderers = [renderer], empty_value = 1)
		plot.add_tools(draw_tool)
		plot.toolbar.active_drag = draw_tool
		
		
			
	#Else plot verticies as lines
	else:		
		#Plot air temperatures
		if gui.showAirTempBV.get() is True and gui.airValid:
			# plot.circle(airX, airY, size = 5, color = "black", alpha = 1, legend = "Air Temeprature")
			plot.line(airX, airY, line_width = float(gui.airTempSize_E.get()), color = gui.airTempColorVar.get(), line_alpha = 1, legend = "Air Temeprature")
			
		#Plot egg temperatures
		plot.circle(masterX, masterY, size = float(gui.eggTempPointSize_E.get()), color = gui.eggTempPointColorVar.get(), legend = "Egg Temperature")	
		plot.line(masterX, masterY, line_width = float(gui.eggTempLineSize_E.get()), color = gui.eggTempLineColorVar.get())
			
		#Add vertices
		plot.line("x", "y", line_width = float(gui.boutSize_E.get()), legend = "Detected Bout", line_color = gui.boutColorVar.get(), source = boutsSourceData)
	
	if gui.showGridBV.get() is False:
		plot.grid.visible = False
	
	plot.legend.label_text_font_size = (gui.legendFontSizeE.get() + "pt")
	plot.background_fill_color = None
	plot.border_fill_color = None
	# plot.outline_color = None
			
	#Generate plot
	show(column(plot, widgetbox(data_table)))
			
#Create file containing information about individual bouts as well as by whole-day and comprehensive file summaries at the bottom	
def outStats(gui, days, nights, pairsBlockGroup, masterBlock):
	allTemps = []
	allAirTemps =  []

	masterSuperCust = 0
	masterSubCust = 0
	
	if gui.makeOutputBool or gui.compileStatsBool:
		#Acquire list of ALL temperatures for reporting statistics accross entire data set
		for i in range(len(gui.masterList)):
			allTemps.append(float(gui.masterList[i][gui.tempsCol]))
			if gui.airValid is True:
				allAirTemps.append(float(gui.masterList[i][gui.airTempCol]))
			else:
				allAirTemps.append(0)
		
		#Get time exceeding critical temperatures
		for temp in allTemps:
			if temp > float(gui.superCustE.get()):
				masterSuperCust += gui.interval
				
			if temp < float(gui.subCustE.get()):
				masterSubCust += gui.interval
				
	
	#Output summary statistics
	if gui.makeOutputBool:
		file = gui.outName
	#If "Ouptut statistics" is not selected but "Compile statistics" is, send the summary to compile statistics file
	elif gui.compileStatsBool:
		file = gui.compileName
	
	#If either of these options is selected, generate the file stats summary
	if gui.makeOutputBool or gui.compileStatsBool:
		with open(file, "a") as summaryFile:
			#Used to indictate scope of certain statistics
			if gui.restrictSearchBV.get() is True:
				qualifier = " (D),"
			else:
				qualifier = " (DN),"
		
			#Print input file name first (remove path)
			if file == gui.compileName:
				print (os.path.basename(os.path.normpath(gui.inFile)), file = summaryFile)
			else:
				print ("Day and Cumulative Stats", file = summaryFile)
		
			#Output headers
			if gui.dayNumVar.get()      :  print ("Day Number,", end = "", file = summaryFile)
			if gui.dateVar.get()        :  print ("Date,", end = "", file = summaryFile)
			
			if gui.offCountVar.get()    :  print ("Off-bout Count" + qualifier, end = "", file = summaryFile)
			if gui.offDurVar.get()      :  print ("Mean Off Duration (min)" + qualifier, end = "", file = summaryFile)
			if gui.offDurSDVar.get()    :  print ("Off Dur StDev" + qualifier, end = "", file = summaryFile)
			if gui.offDecVar.get()      :  print ("Mean Off Temp Drop" + qualifier, end = "", file = summaryFile)
			if gui.offDecSDVar.get()    :  print ("Off Drop StDev" + qualifier, end = "", file = summaryFile)
			if gui.meanOffTempVar.get()	:  print ("Mean Off-Bout Temp" + qualifier, end = "", file = summaryFile)
			if gui.offTimeSumVar.get()     :  print ("Off-Bout Time Sum" + qualifier, end = "", file = summaryFile)
			
			if gui.onCountVar.get()     :  print ("On-bout Count" + qualifier, end = "", file = summaryFile)
			if gui.onDurVar .get()      :  print ("Mean On Duration (min)" + qualifier, end = "", file = summaryFile)
			if gui.onDurSDVar.get()     :  print ("On Dur StDev" + qualifier, end = "", file = summaryFile)
			if gui.onIncVar.get()       :  print ("Mean On Temp Rise" + qualifier, end = "", file = summaryFile)
			if gui.onIncSDVar.get()     :  print ("On Rise StDev" + qualifier, end = "", file = summaryFile)
			if gui.meanOnTempVar.get()  :  print ("Mean On-Bout Temp" + qualifier, end = "", file = summaryFile)
			if gui.onTimeSumVar.get()      :  print ("On-Bout Time Sum" + qualifier, end = "", file = summaryFile)
			
			if gui.superCustVar.get()   :  print ("Time above (minutes)", gui.superCustE.get(), "(DN),", end = "", file = summaryFile)
			if gui.subCustVar.get()     :  print ("Time below (minutes)", gui.subCustE.get(), "(DN),", end = "", file = summaryFile)
			if gui.boutsDroppedVar.get():  print ("Vertices Dropped" + qualifier, end = "", file = summaryFile)
			
			if gui.meanTempDVar.get()   :  print ("Mean Daytime Egg Temp,", end = "", file = summaryFile)
			if gui.meanTempDSDVar.get() :  print ("Day Egg Temp StDev,", end = "", file = summaryFile)
			if gui.medianTempDVar.get() :  print ("Median Daytime Egg Temp,", end = "", file = summaryFile)
			if gui.minTempDVar.get()    :  print ("Min Daytime Egg Temp,", end = "", file = summaryFile)
			if gui.maxTempDVar.get()    :  print ("Max Daytime Egg Temp,", end = "", file = summaryFile)
			
			if gui.meanTempNVar.get()   :  print ("Mean Nighttime Egg Temp,", end = "", file = summaryFile)
			if gui.meanTempNSDVar.get() :  print ("Night Egg Temp StDev,", end = "", file = summaryFile)
			if gui.medianTempNVar.get() :  print ("Median Nighttime Egg Temp,", end = "", file = summaryFile)
			if gui.minTempNVar.get()    :  print ("Min Nighttime Egg Temp,", end = "", file = summaryFile)
			if gui.maxTempNVar.get()    :  print ("Max Nighttime Egg Temp,", end = "", file = summaryFile)
			
			if gui.meanTempDNVar.get()  :  print ("Mean Egg Temp (DN),", end = "", file = summaryFile)
			if gui.meanTempDNSDVar.get():  print ("Egg Temp StDev (DN),", end = "", file = summaryFile)
			if gui.medianTempDNVar.get():  print ("Median Egg Temp (DN),", end = "", file = summaryFile)
			if gui.minTempDNVar.get()   :  print ("Min Egg Temp (DN),", end = "", file = summaryFile)
			if gui.maxTempDNVar.get()   :  print ("Max Egg Temp (DN),", end = "", file = summaryFile)
			
			if gui.airValid is True:
				if gui.meanAirVar.get()   :  print ("Mean Air Temp (DN),", end = "", file = summaryFile)
				if gui.minAirVar.get()   :  print ("Min Air Temp (DN),", end = "", file = summaryFile)
				if gui.maxAirVar.get()   :  print ("Max Air Temp (DN),", end = "", file = summaryFile)
				
			
			print ("", file = summaryFile)
			
			if len(days.blockList) > 0 and len(nights.blockList) > 0:
				#If night comes first
				if days.blockList[0].start > nights.blockList[0].start:
					modifier = 1
				else:
					modifier = 0
							
				x = 0
				#Print individual day stats
				for i in range(len(days.blockList)):	
					if (i + modifier) < (len(nights.blockList)):
						if not days.blockList[i].partial and not nights.blockList[i + modifier].partial:
							if gui.restrictSearchBV.get() is True:
								statCore = days.blockList[i]
							else:
								statCore = pairsBlockGroup.blockList[x]
						
							#Output statistics
							if gui.dayNumVar.get()      :  print (str(x + 1) + ",", end = "", file = summaryFile)
							if gui.dateVar.get()        :  print (str(statCore.date) + ",", end = "", file = summaryFile)
							
							if gui.offCountVar.get()    :  print (str(statCore.offCount) + ",", end = "", file = summaryFile)
							if gui.offDurVar.get()      :  print (str(statCore.offDurMean) + ",", end = "", file = summaryFile)
							if gui.offDurSDVar.get()    :  print (str(statCore.offDurStDev) + ",", end = "", file = summaryFile)
							if gui.offDecVar.get()      :  print (str(statCore.offDecMean) + ",", end = "", file = summaryFile)
							if gui.offDecSDVar.get()    :  print (str(statCore.offDecStDev) + ",", end = "", file = summaryFile)
							if gui.meanOffTempVar.get()	:  print (str(statCore.meanOffTemp) + ",", end = "", file = summaryFile)
							if gui.offTimeSumVar.get()  :  print (str(statCore.offTimeSum) + ",", end = "", file = summaryFile)
							
							if gui.onCountVar.get()     :  print (str(statCore.onCount) + ",", end = "", file = summaryFile)
							if gui.onDurVar .get()      :  print (str(statCore.onDurMean) + ",", end = "", file = summaryFile)
							if gui.onDurSDVar.get()     :  print (str(statCore.onDurStDev) + ",", end = "", file = summaryFile)
							if gui.onIncVar.get()       :  print (str(statCore.onIncMean) + ",", end = "", file = summaryFile)
							if gui.onIncSDVar.get()     :  print (str(statCore.onIncStDev) + ",", end = "", file = summaryFile)
							if gui.meanOnTempVar.get()	:  print (str(statCore.meanOnTemp) + ",", end = "", file = summaryFile)
							if gui.onTimeSumVar.get()   :  print (str(statCore.onTimeSum) + ",", end = "", file = summaryFile)
							
							if gui.superCustVar.get()   :  print (str(pairsBlockGroup.blockList[x].superCust) + ",",  end = "", file = summaryFile)
							if gui.subCustVar.get()     :  print (str(pairsBlockGroup.blockList[x].subCust) + ",",  end = "", file = summaryFile)
							if gui.boutsDroppedVar.get():  print ("--,",  end = "", file = summaryFile)
							
							if gui.meanTempDVar.get()   :  print (str(days.blockList[i].meanTemp) + ",", end = "", file = summaryFile)
							if gui.meanTempDSDVar.get() :  print (str(days.blockList[i].tempStDev) + ",", end = "", file = summaryFile)
							if gui.medianTempDVar.get() :  print (str(days.blockList[i].medianTemp) + ",", end = "", file = summaryFile)
							if gui.minTempDVar.get()    :  print (str(days.blockList[i].minTemp) + ",", end = "", file = summaryFile)
							if gui.maxTempDVar.get()    :  print (str(days.blockList[i].maxTemp) + ",", end = "", file = summaryFile)
							
							if gui.meanTempNVar.get()   :  print (str(nights.blockList[i + modifier].meanTemp) + ",", end = "", file = summaryFile)
							if gui.meanTempNSDVar.get() :  print (str(nights.blockList[i + modifier].tempStDev) + ",", end = "", file = summaryFile)
							if gui.medianTempNVar.get() :  print (str(nights.blockList[i + modifier].medianTemp) + ",", end = "", file = summaryFile)
							if gui.minTempNVar.get()    :  print (str(nights.blockList[i + modifier].minTemp) + ",", end = "", file = summaryFile)
							if gui.maxTempNVar.get()    :  print (str(nights.blockList[i + modifier].maxTemp) + ",", end = "", file = summaryFile)
							
							if gui.meanTempDNVar.get()  :  print (str(pairsBlockGroup.blockList[x].meanTemp) + ",", end = "", file = summaryFile)
							if gui.meanTempDNSDVar.get():  print (str(pairsBlockGroup.blockList[x].tempStDev) + ",", end = "", file = summaryFile)
							if gui.medianTempDNVar.get():  print (str(pairsBlockGroup.blockList[x].medianTemp) + ",", end = "", file = summaryFile)
							if gui.minTempDNVar.get()   :  print (str(pairsBlockGroup.blockList[x].minTemp) + ",", end = "", file = summaryFile)
							if gui.maxTempDNVar.get()   :  print (str(pairsBlockGroup.blockList[x].maxTemp) + ",", end = "", file = summaryFile)
							
							if gui.airValid is True:
								if gui.meanAirVar.get()  :  print (str(pairsBlockGroup.blockList[x].meanAirTemp) + ",", end = "", file = summaryFile)
								if gui.minAirVar.get()   :  print (str(pairsBlockGroup.blockList[x].minAir) + ",", end = "", file = summaryFile)
								if gui.maxAirVar.get()   :  print (str(pairsBlockGroup.blockList[x].maxAir) + ",", end = "", file = summaryFile)
								
							x += 1
							
							print ("", file = summaryFile)
				
				#Add number of full days for this input file to the counter for multiple input files
				gui.multiInFullDayCount += x
			
			#Stat core changes based on restriction settings
			if gui.restrictSearchBV.get() is True:
				sumStatCore = days
			else:
				sumStatCore = masterBlock
			
			#Output stats summary for entire input file
			if gui.dayNumVar.get()      :  print ("--,",  end = "", file = summaryFile)
			if gui.dateVar.get()        :  print ("ALL DATA,",  end = "", file = summaryFile)
			
			if gui.offCountVar.get()    :  print (str(sumStatCore.offCount) + ",",  end = "", file = summaryFile)
			if gui.offDurVar.get()      :  print (str(sumStatCore.offDurMean) + ",",  end = "", file = summaryFile)
			if gui.offDurSDVar.get()    :  print (str(sumStatCore.offDurStDev) + ",",  end = "", file = summaryFile)
			if gui.offDecVar.get()      :  print (str(sumStatCore.offDecMean) + ",",  end = "", file = summaryFile)
			if gui.offDecSDVar.get()    :  print (str(sumStatCore.offDecStDev) + ",",  end = "", file = summaryFile)
			if gui.meanOffTempVar.get() :  print (str(sumStatCore.meanOffTemp) + ",",  end = "", file = summaryFile)
			if gui.offTimeSumVar.get()  :  print (str(sumStatCore.offTimeSum) + ",", end = "", file = summaryFile)
			
			if gui.onCountVar.get()     :  print (str(sumStatCore.onCount) + ",",  end = "", file = summaryFile)
			if gui.onDurVar .get()      :  print (str(sumStatCore.onDurMean) + ",",  end = "", file = summaryFile)
			if gui.onDurSDVar.get()     :  print (str(sumStatCore.onDurStDev) + ",",  end = "", file = summaryFile)
			if gui.onIncVar.get()       :  print (str(sumStatCore.onIncMean) + ",",  end = "", file = summaryFile)
			if gui.onIncSDVar.get()     :  print (str(sumStatCore.onIncStDev) + ",",  end = "", file = summaryFile)
			if gui.meanOnTempVar.get()	:  print (str(sumStatCore.meanOnTemp) + ",",  end = "", file = summaryFile)
			if gui.onTimeSumVar.get()   :  print (str(sumStatCore.onTimeSum) + ",", end = "", file = summaryFile)
			
			if gui.superCustVar.get()   :  print (str(masterSuperCust) + ",",  end = "", file = summaryFile)
			if gui.subCustVar.get()     :  print (str(masterSubCust) + ",",  end = "", file = summaryFile)
			if gui.boutsDroppedVar.get():  print (str(sumStatCore.boutsDropped) + ",",  end = "", file = summaryFile)
			
			if gui.meanTempDVar.get()   :  print (str(days.meanTemp) + ",",  end = "", file = summaryFile)
			if gui.meanTempDSDVar.get() :  print (str(sumStatCore.tempStDev) + ",",  end = "", file = summaryFile)
			if gui.medianTempDVar.get() :  print (str(sumStatCore.medianTemp) + ",",  end = "", file = summaryFile)
			if gui.minTempDVar.get()    :  print (str(sumStatCore.minTemp) + ",",  end = "", file = summaryFile)
			if gui.maxTempDVar.get()    :  print (str(sumStatCore.maxTemp) + ",",  end = "", file = summaryFile)

			if gui.meanTempNVar.get()   :  print (str(nights.meanTemp) + ",",  end = "", file = summaryFile)
			if gui.meanTempNSDVar.get() :  print (str(nights.tempStDev) + ",",  end = "", file = summaryFile)
			if gui.medianTempNVar.get() :  print (str(nights.medianTemp) + ",",  end = "", file = summaryFile)
			if gui.minTempNVar.get()    :  print (str(nights.minTemp) + ",",  end = "", file = summaryFile)
			if gui.maxTempNVar.get()    :  print (str(nights.maxTemp) + ",",  end = "", file = summaryFile)
			
			if gui.meanTempDNVar.get()  :  print (str(round(statistics.mean(allTemps), 3)) + ",",  end = "", file = summaryFile)
			if gui.meanTempDNSDVar.get():  print (str(round(statistics.stdev(allTemps), 3)) + ",",  end = "", file = summaryFile)
			if gui.medianTempDNVar.get():  print (str(statistics.median(allTemps)) + ",",  end = "", file = summaryFile)
			if gui.minTempDNVar.get()   :  print (str(min(allTemps)) + ",",  end = "", file = summaryFile)
			if gui.maxTempDNVar.get()   :  print (str(max(allTemps)) + ",",  end = "", file = summaryFile)
			
			if gui.airValid is True:
				if gui.meanAirVar.get()   :  print (str(round(statistics.mean(allAirTemps), 3)) + ",",  end = "", file = summaryFile)
				if gui.minAirVar.get()   :  print (str(min(allAirTemps)) + ",",  end = "", file = summaryFile)
				if gui.maxAirVar.get()   :  print (str(max(allAirTemps)) + ",",  end = "", file = summaryFile)
			
			if file == gui.compileName:
				print ("\n\n", file = summaryFile)
	
	#If both options are selected, simply copy the summary from the "Stats Options statistics" file to the "Compile statistics" file
	if gui.makeOutputBool and gui.compileStatsBool:
		lenAppend = x + 2
		
		with open(gui.outName, "r") as outFile:
			with open(gui.compileName, "a") as compileFile:
				print(os.path.basename(os.path.normpath(gui.inFile)), file = compileFile)
				outLines = outFile.readlines()
				for line in outLines[(len(outLines) - lenAppend):len(outLines)]:
					compileFile.write(line)
					
				print ("\n\n", file = compileFile)

				
				
	
	#Generate statistics file if requested
	if gui.makeOutputBool:
		#Open output file
		with open(gui.outName, "a") as outFile:
			#Spacer
			print("\n\n", "Individual Bout Stats", file = outFile)
			#Print header
			print ("Date,Bout Type,Start Time,End Time,Start Data Point,End Data Point,Duration (min),Egg Temp Change, Start Egg Temp, End Egg Temp, Mean Egg Temp,", end = "", file = outFile)
			if gui.airValid is True:
				print("Start Air Temp, End Air Temp, Mean Air Temp", end = "", file = outFile)
			
			print("", file = outFile)
				
			#If daytime bouts only is selected:
			if gui.restrictSearchBV.get() is True:
				for day in days.blockList:
					firstBout = True
					#Print date of day
					print (day.date + ",", end = "", file = outFile)
					#Print stats for individual bouts
					for bout in day.bouts:
						#First bout in day must be printed differently due to presence of date
						if not firstBout:
							print (",", end = "", file = outFile)
						else:
							firstBout = False
							
						if bout.boutType == "off":
							print ("Off" + ",", end = "", file = outFile)
						else:
							print ("On" + ",", end = "", file = outFile)
							
						print (getTime(gui, bout.start) + "," + getTime(gui, bout.stop) + ",", end = "", file = outFile)
						print (gui.masterList[bout.start][gui.dataPointCol] + "," + gui.masterList[bout.stop][gui.dataPointCol] + ",", end = "", file = outFile)
						print (str(bout.dur) + "," + str(bout.tempChange) + ",", end = "", file = outFile)
						print (gui.masterList[bout.start][gui.tempsCol].strip() + "," + gui.masterList[bout.stop][gui.tempsCol].strip() + "," + str(bout.meanTemp) + ",", end = "", file = outFile)
						
						if gui.airValid is True:
							print (gui.masterList[bout.start][gui.airTempCol].strip() + "," + gui.masterList[bout.stop][gui.airTempCol].strip() + "," + str(bout.meanAirTemp) + ",", end = "", file = outFile)
						
						print("", file = outFile)
				
				print ("\n\n", file = outFile)
			#If day and night bouts are being gathered
			else:
				if len(masterBlock.bouts) > 0:
					curDate = ""
					for bout in masterBlock.bouts:
						#First bout in day must be printed differently due to presence of date
						if getDate(gui, bout.start) == curDate:
							print (",", end = "", file = outFile)
						else:
							curDate = getDate(gui, bout.start)
							print (curDate + ",", end = "", file = outFile)
							
						if bout.boutType == "off":
							print ("Off" + ",", end = "", file = outFile)
						else:
							print ("On" + ",", end = "", file = outFile)
							
						print (getTime(gui, bout.start) + "," + getTime(gui, bout.stop) + ",", end = "", file = outFile)
						print (gui.masterList[bout.start][gui.dataPointCol] + "," + gui.masterList[bout.stop][gui.dataPointCol] + ",", end = "", file = outFile)
						print (str(bout.dur) + "," + str(bout.tempChange) + ",", end = "", file = outFile)
						print (gui.masterList[bout.start][gui.tempsCol].strip() + "," + gui.masterList[bout.stop][gui.tempsCol].strip() + "," + str(bout.meanTemp) + ",", end = "", file = outFile)
						
						if gui.airValid is True:
							print (gui.masterList[bout.start][gui.airTempCol].strip() + "," + gui.masterList[bout.stop][gui.airTempCol].strip() + "," + str(bout.meanAirTemp) + ",", end = "", file = outFile)
											
						print("", file = outFile)
											
					print ("\n\n", file = outFile)
		
		