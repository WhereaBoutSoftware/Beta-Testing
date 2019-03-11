import statistics
import re
import tkinter as tk
from tkinter import messagebox
import time

import coreClasses as coreC
import VDFunctions as coreVD

	
def scoreAlgo(gui, userVertIs, trainBlock, bestScore, coreVerts = False, refinedVerts = False):
	#Initialize core variables
	score = 0
	trainVertIs = []
	
	#Update variable values
	gui.setVars()
	
	#Run getVerts
	if refinedVerts:
		coreVD.getVerts(gui, trainBlock, coreVerts = False, refinedVerts = refinedVerts)
	else:
		coreVD.getVerts(gui, trainBlock, coreVerts = coreVerts)
	
	#If there are no vertices, return void
	if len(trainBlock.vertices) < 1:
		# print ("void")
		return "Void1"
	
	#Compile indices of predicted vertices
	for vertex in trainBlock.vertices:
		trainVertIs.append(gui.masterList[vertex.index][gui.dataPointCol])
		
	#Add penalty from having wrong number of bouts
	vertexNumDif = len(userVertIs) - len(trainVertIs)
	# print ("vertexNumDif = ", vertexNumDif)
	score += ((abs(vertexNumDif) * 10) ** 2)
	
	#Return void if score is already greater than current best score
	if score >= bestScore:
		#If parameters are too restrictive
		if vertexNumDif > 0:
			return "Void2"
		#If parameters are too lenient
		else:
			return "Void3"
	
	#Look at every user-provided vertex index
	for userIndex in userVertIs:
		minDif = -1
		#Look at index of every algorithm-aquired vertex
		for x in range(0, len(trainVertIs)):
			#Go until the userIndex is passed
			if int(trainVertIs[x]) > int(userIndex):
				try:
					#If vertex location is perfect, score penalty is 0
					if int(trainVertIs[x - 1]) == int(userIndex):
						minDif = 0
						break
					#Else minimum difference is smallest distance to either previous or next trainVert index
					else:
						minDif = min(abs(int(userIndex) - int(trainVertIs[x - 1])), abs(int(userIndex) - int(trainVertIs[x])))
						break
				
				#Accounts for first train index
				except:
					if x == 0:
						minDif = int(trainVertIs[x]) - int(userIndex)
						break
		
		#Accounts for last user index if further than last train index
		if minDif == -1:
			minDif = abs(int(userIndex) - int(trainVertIs[-1]))
		
		#Applies penalty for misplaced vertex
		minDif = (minDif * gui.interval)				
		score += (minDif ** 2)
		if score >= bestScore:
			# print ("void4Score =", score)
			return "Void4"
	
	print("New Best Score:", round(score))
	
	return score
	
#Save best parameter setup
def saveSettings(gui):
	
	#Adjacent mean radius section
	gui.bestAdjMeanRad = round(float(gui.adjMeanRadE.get()))
	
	#Vertex search (findVertexI) downstream limit section -- enacted as multiplier of duration threshold
	gui.bestVertSearchDownLim = round(float(gui.vertSearchDownLimE.get()))

	
	#Time threshold section
	gui.bestTimeThreshAdvOn = round(float(gui.timeThreshAdvOnE.get()), 3)
	gui.bestTimeThreshAdvOff = round(float(gui.timeThreshAdvOffE.get()), 3)

	#Temperature threshold section
	gui.bestTempThreshAdvOn = round(float(gui.tempThreshAdvOnE.get()), 3)
	gui.bestTempThreshAdvOff = round(float(gui.tempThreshAdvOffE.get()), 3)
	
	#Minimum initial slope section
	gui.bestMinSlopeOn = round(float(gui.minSlopeOnE.get()), 3)
	gui.bestMinSlopeOff = round(float(gui.minSlopeOffE.get()), 3)
	
	#Minimum initial slope range section
	gui.bestSlopeRangeOn = round(float(gui.slopeRangeOnE.get()))
	gui.bestSlopeRangeOff = round(float(gui.slopeRangeOffE.get()))
	
	#Vertex migration checkbox
	gui.bestVertMigrationBV = gui.vertMigrationBV.get()
	
def testVertMigration(gui, userVertIs, refinedVerts, bestScore):
	#Get score without vertex migration
	trainBlock = coreC.block(gui, 0, (len(gui.masterList) - 1), False)
	noMigScore = scoreAlgo(gui, userVertIs, trainBlock, bestScore, False, refinedVerts)
	
	#Bypasses vertex migration testing if difference from number of vertices is already greater than best score
	if noMigScore is "Void2" or noMigScore is "Void3":
		
		return bestScore

	#Turn on migration
	gui.vertMigrationCK.select()
	
	del trainBlock
	trainBlock = coreC.block(gui, 0, (len(gui.masterList) - 1), False)
	
	#Get score with vertex migration
	migScore = scoreAlgo(gui, userVertIs, trainBlock, bestScore, False, refinedVerts)
	
	
	# print("\nbestScore =", bestScore)
	# print("noMig =", noMigScore)
	# print("migScore =", migScore)
	
	#If both have valid score, take the best
	if isinstance(noMigScore, float) and isinstance(migScore, float):
		if noMigScore <= migScore:
			localBest = noMigScore
			gui.vertMigrationCK.deselect()
		else:
			localBest = migScore
	#If only noMig is valid score, take it
	elif isinstance(noMigScore, float):
		localBest = noMigScore
		gui.vertMigrationCK.deselect()
	#If only mig is valid score, take it
	elif isinstance(migScore, float):
		localBest = migScore
	#If neither are valid, return provided bestScore
	else:
		gui.vertMigrationCK.deselect()
		# print("neither valid")
		return bestScore
	
	# print("localBest =", localBest)
	
	#Update bestScore and save settings if better score encountered
	if localBest < bestScore:
		bestScore = localBest
		saveSettings(gui)

	gui.vertMigrationCK.deselect()
	return bestScore	
	
	
def trainOffSlope(gui, paramDict, userVertIs, coreVerts, bestScore):
	slopeStart, slopeStop, slopeStep = paramDict["offSlopeStart"], paramDict["offSlopeStop"], paramDict["offSlopeStep"]  #minSlopeOff
	rangeStart, rangeStop, rangeStep = paramDict["offRangeStart"], paramDict["offRangeStop"], paramDict["offRangeStep"]  #slopeRangeOff
	

	#Tier5 = minimum off-bout slope
	for i1 in range(slopeStart, slopeStop, slopeStep):
		gui.minSlopeOffE.delete(0, "end")
		gui.minSlopeOffE.insert(0, ((i1 * 0.01) * -1))

		#Tier7 = off-bout slope range
		for i2 in range(rangeStart, rangeStop, rangeStep):
			gui.slopeRangeOffE.delete(0, "end")
			gui.slopeRangeOffE.insert(0, i2)
		
				
			#Initialize vertex migration to off
			gui.vertMigrationCK.deselect()
			
			#Get refined vertices to expidite migration testing
			trainBlock = coreC.block(gui, 0, (len(gui.masterList) - 1), False)
			refinedVerts = coreVD.getRefinedVerts(gui, trainBlock)

			#Test vertex migration
			del trainBlock
			trainBlock = coreC.block(gui, 0, (len(gui.masterList) - 1), False)
			bestScore = testVertMigration(gui, userVertIs, refinedVerts, bestScore)
			
	return bestScore

def trainOnSlope(gui, paramDict, userVertIs, coreVerts, bestScore):
	slopeStart, slopeStop, slopeStep = paramDict["onSlopeStart"], paramDict["onSlopeStop"], paramDict["onSlopeStep"]  #minSlopeOn
	rangeStart, rangeStop, rangeStep = paramDict["onRangeStart"], paramDict["onRangeStop"], paramDict["onRangeStep"]  #slopeRangeOn
	

	#Tier5 = minimum on-bout slope
	for i1 in range(slopeStart, slopeStop, slopeStep):
		gui.minSlopeOnE.delete(0, "end")
		gui.minSlopeOnE.insert(0, (i1 * 0.01))

		#Tier7 = on-bout slope range
		for i2 in range(rangeStart, rangeStop, rangeStep):
			gui.slopeRangeOnE.delete(0, "end")
			gui.slopeRangeOnE.insert(0, i2)
		
				
			#Initialize vertex migration to off
			gui.vertMigrationCK.deselect()
			
			bestScore = trainOffSlope(gui, paramDict, userVertIs, coreVerts, bestScore)
			
	return bestScore
		
	
	
def trainSlopesSynced(gui, paramDict, userVertIs, coreVerts, bestScore):
	slopeStart, slopeStop, slopeStep = paramDict["slopeSyncedStart"], paramDict["slopeSyncedStop"], paramDict["slopeSyncedStep"]  #minSlopeOn
	rangeStart, rangeStop, rangeStep = paramDict["rangeSyncedStart"], paramDict["rangeSyncedStop"], paramDict["rangeSyncedStep"]  #slopeRangeOn

	#Tier5 = minimum on-bout slope
	for i1 in range(slopeStart, slopeStop, slopeStep):
		gui.minSlopeOnE.delete(0, "end")
		gui.minSlopeOffE.delete(0, "end")
		gui.minSlopeOnE.insert(0, (i1 * 0.01))
		gui.minSlopeOffE.insert(0, ((i1 * 0.01) * -1))
	
			
		#Tier7 = on-bout slope range
		for i2 in range(rangeStart, rangeStop, rangeStep):
			gui.slopeRangeOnE.delete(0, "end")
			gui.slopeRangeOffE.delete(0, "end")
			gui.slopeRangeOnE.insert(0, paramDict["rangeSyncedStart"])
			gui.slopeRangeOffE.insert(0, paramDict["rangeSyncedStart"])
		
			#Initialize vertex migration to off
			gui.vertMigrationCK.deselect()
			
			#Get refined vertices to expidite migration testing
			trainBlock = coreC.block(gui, 0, (len(gui.masterList) - 1), False)
			refinedVerts = coreVD.getRefinedVerts(gui, trainBlock)

			#Test vertex migration
			del trainBlock
			trainBlock = coreC.block(gui, 0, (len(gui.masterList) - 1), False)
			bestScore = testVertMigration(gui, userVertIs, refinedVerts, bestScore)
					
	return bestScore

def trainOffTemp(gui, paramDict, userVertIs, coreVerts, bestScore):
	start, stop, step = paramDict["offTempStart"], paramDict["offTempStop"], paramDict["offTempStep"]  #temperThreshOn	
	
	trainBlock = coreC.block(gui, 0, (len(gui.masterList) - 1), False)
	
	#Tier3 = on-bout temperature threshold
	for i in range(start, stop, step):
		#Populate entry boxes
		gui.tempThreshAdvOffE.delete(0, "end")
		gui.tempThreshAdvOffE.insert(0, (i * 0.1))
		
		
		gui.minSlopeOnE.delete(0, "end")
		gui.minSlopeOffE.delete(0, "end")
		gui.slopeRangeOnE.delete(0, "end")
		gui.slopeRangeOffE.delete(0, "end")
		gui.minSlopeOnE.insert(0, 0)
		gui.minSlopeOffE.insert(0, 0)
		gui.slopeRangeOnE.insert(0, paramDict["rangeSyncedStart"])
		gui.slopeRangeOffE.insert(0, paramDict["rangeSyncedStart"])
		
		#Initialize vertex migration to off
		gui.vertMigrationCK.deselect()
		
		
		if scoreAlgo(gui, userVertIs, trainBlock, bestScore, coreVerts) is not "Void2":
			if gui.trainSlopeBV.get():
				if gui.decoupleSlopeBV.get():
					bestScore = trainOnSlope(gui, paramDict, userVertIs, coreVerts, bestScore)
				else:
					bestScore = trainSlopesSynced(gui, paramDict, userVertIs, coreVerts, bestScore)
			else:
				#Get refined vertices to expidite migration testing
				del trainBlock
				trainBlock = coreC.block(gui, 0, (len(gui.masterList) - 1), False)
				refinedVerts = coreVD.getRefinedVerts(gui, trainBlock)

				#Test vertex migration
				del trainBlock
				trainBlock = coreC.block(gui, 0, (len(gui.masterList) - 1), False)
				bestScore = testVertMigration(gui, userVertIs, refinedVerts, bestScore)
		else:
			# print("break at offTemp")
			break
				
	return bestScore	
	
	
		
def trainOnTemp(gui, paramDict, userVertIs, coreVerts, bestScore):
	start, stop, step = paramDict["onTempStart"], paramDict["onTempStop"], paramDict["onTempStep"]  #temperThreshOn	
	
	trainBlock = coreC.block(gui, 0, (len(gui.masterList) - 1), False)
	
	#Tier3 = on-bout temperature threshold
	for i in range(start, stop, step):
		#Populate entry boxes
		gui.tempThreshAdvOnE.delete(0, "end")
		gui.tempThreshAdvOnE.insert(0, (i * 0.1))
		
		gui.tempThreshAdvOffE.delete(0, "end")
		gui.minSlopeOnE.delete(0, "end")
		gui.minSlopeOffE.delete(0, "end")
		gui.slopeRangeOnE.delete(0, "end")
		gui.slopeRangeOffE.delete(0, "end")
		gui.tempThreshAdvOffE.insert(0, 0)
		gui.minSlopeOnE.insert(0, 0)
		gui.minSlopeOffE.insert(0, 0)
		gui.slopeRangeOnE.insert(0, paramDict["rangeSyncedStart"])
		gui.slopeRangeOffE.insert(0, paramDict["rangeSyncedStart"])
		
		#Initialize vertex migration to off
		gui.vertMigrationCK.deselect()
		
		
		if scoreAlgo(gui, userVertIs, trainBlock, bestScore, coreVerts) is not "Void2":
			#Test downstream parameters with these upstream parameters
			bestScore = trainOffTemp(gui, paramDict, userVertIs, coreVerts, bestScore)
		else:
			# print("break at onTemp")
			break
				
	return bestScore
	
def trainTempsSynced(gui, paramDict, userVertIs, coreVerts, bestScore):
	start, stop, step = paramDict["tempSyncedStart"], paramDict["tempSyncedStop"], paramDict["tempSyncedStep"]  #tempThreshOn	
	
	trainBlock = coreC.block(gui, 0, (len(gui.masterList) - 1), False)
	
	#On/off-bout temperature threshold
	for i in range(start, stop, step):
		#Populate entry boxes
		gui.tempThreshAdvOnE.delete(0, "end")
		gui.tempThreshAdvOffE.delete(0, "end")
		gui.tempThreshAdvOnE.insert(0, (i * 0.1))
		gui.tempThreshAdvOffE.insert(0, (i * 0.1))
		
		#Initialize downstream parameters to 0
		gui.minSlopeOnE.delete(0, "end")
		gui.minSlopeOffE.delete(0, "end")
		gui.slopeRangeOnE.delete(0, "end")
		gui.slopeRangeOffE.delete(0, "end")
		gui.minSlopeOnE.insert(0, 0)
		gui.minSlopeOffE.insert(0, 0)
		gui.slopeRangeOnE.insert(0, paramDict["rangeSyncedStart"])
		gui.slopeRangeOffE.insert(0, paramDict["rangeSyncedStart"])
		
		#Initialize vertex migration to off
		gui.vertMigrationCK.deselect()
		
		
		if scoreAlgo(gui, userVertIs, trainBlock, bestScore, coreVerts) is not "Void2":
			if gui.trainSlopeBV.get():
				if gui.decoupleSlopeBV.get():
					bestScore = trainOnSlope(gui, paramDict, userVertIs, coreVerts, bestScore)
				else:
					bestScore = trainSlopesSynced(gui, paramDict, userVertIs, coreVerts, bestScore)
			else:
				#Get refined vertices to expidite migration testing
				del trainBlock
				trainBlock = coreC.block(gui, 0, (len(gui.masterList) - 1), False)
				refinedVerts = coreVD.getRefinedVerts(gui, trainBlock)

				#Test vertex migration
				del trainBlock
				trainBlock = coreC.block(gui, 0, (len(gui.masterList) - 1), False)
				bestScore = testVertMigration(gui, userVertIs, refinedVerts, bestScore)
		else:
			# print("break at onTemp")
			break
				
	return bestScore
			
		
def trainOffDur(gui, paramDict, userVertIs, bestScore):
	trainBlock = coreC.block(gui, 0, (len(gui.masterList) - 1), False)
	
	#Initialize range of values to be tested			
	start, stop, step = paramDict["offDurStart"], paramDict["offDurStop"], paramDict["offDurStep"] 	#off-bout duration threshold

	#Tier1 = on-bout time threshold
	for i in range(start, stop, step):
		#Populate entry boxes
		gui.timeThreshAdvOffE.delete(0, "end")
		gui.timeThreshAdvOffE.insert(0, i)
		
		#Initialize downstream parameters to 0
		gui.tempThreshAdvOnE.delete(0, "end")
		gui.tempThreshAdvOffE.delete(0, "end")
		gui.minSlopeOnE.delete(0, "end")
		gui.minSlopeOffE.delete(0, "end")
		gui.slopeRangeOnE.delete(0, "end")
		gui.slopeRangeOffE.delete(0, "end")
		gui.tempThreshAdvOnE.insert(0, 0)
		gui.tempThreshAdvOffE.insert(0, 0)
		gui.minSlopeOnE.insert(0, 0)
		gui.minSlopeOffE.insert(0, 0)
		gui.slopeRangeOnE.insert(0, paramDict["rangeSyncedStart"])
		gui.slopeRangeOffE.insert(0, paramDict["rangeSyncedStart"])
		
		#Initialize vertex migration to off
		gui.vertMigrationCK.deselect()
	
		coreVerts = coreVD.getCoreVerts(gui, trainBlock)
	
		#Bypasses further testing if penalty from too few vertices (too restrictive of settings) is already greater than best score
		if scoreAlgo(gui, userVertIs, trainBlock, bestScore, coreVerts) is not "Void2":
			if gui.decoupleTempsBV.get():
				#Test downstream parameters with this combination of duration thresholds
				bestScore = trainOnTemp(gui, paramDict, userVertIs, coreVerts, bestScore)
			else:
				bestScore = trainTempsSynced(gui, paramDict, userVertIs, coreVerts, bestScore)
		else:
			# print("break at off dur")
			break
				
	return bestScore
	

def trainOnDur(gui, paramDict, userVertIs, bestScore):
	trainBlock = coreC.block(gui, 0, (len(gui.masterList) - 1), False)
	
	#Initialize range of values to be tested			
	start, stop, step = paramDict["onDurStart"], paramDict["onDurStop"], paramDict["onDurStep"]   #on-bout duration threshold

	#Tier1 = on-bout time threshold
	for i in range(start, stop, step):
		#Populate entry boxes
		gui.timeThreshAdvOnE.delete(0, "end")
		gui.timeThreshAdvOnE.insert(0, i)
		
		#Initialize downstream parameters to 0
		gui.timeThreshAdvOffE.delete(0, "end")
		gui.tempThreshAdvOnE.delete(0, "end")
		gui.tempThreshAdvOffE.delete(0, "end")
		gui.minSlopeOnE.delete(0, "end")
		gui.minSlopeOffE.delete(0, "end")
		gui.slopeRangeOnE.delete(0, "end")
		gui.slopeRangeOffE.delete(0, "end")
		gui.timeThreshAdvOffE.insert(0, 0)
		gui.tempThreshAdvOnE.insert(0, 0)
		gui.tempThreshAdvOffE.insert(0, 0)
		gui.minSlopeOnE.insert(0, 0)
		gui.minSlopeOffE.insert(0, 0)
		gui.slopeRangeOnE.insert(0, paramDict["rangeSyncedStart"])
		gui.slopeRangeOffE.insert(0, paramDict["rangeSyncedStart"])
		
		#Initialize vertex migration to off
		gui.vertMigrationCK.deselect()
		
	
		#Bypasses further testing if penalty from too few vertices (too restrictive of settings) is already greater than best score
		if scoreAlgo(gui, userVertIs, trainBlock, bestScore) is not "Void2":
			#Test downstream parameters with this combination of duration thresholds
			bestScore = trainOffDur(gui, paramDict, userVertIs, bestScore)
		else:
			# print("break at on dur")
			break
				
	return bestScore
	
def trainDursSynced(gui, paramDict, userVertIs, bestScore):
	trainBlock = coreC.block(gui, 0, (len(gui.masterList) - 1), False)
	
	#Initialize range of values to be tested			
	start, stop, step = paramDict["durSyncedStart"], paramDict["durSyncedStop"], paramDict["durSyncedStep"]  #on/off-bout duration threshold
	
	#Tier1 = on/off-bout time threshold
	for i in range(start, stop, step):
		#Populate entry boxes
		gui.timeThreshAdvOnE.delete(0, "end")
		gui.timeThreshAdvOffE.delete(0, "end")
		gui.timeThreshAdvOnE.insert(0, i)
		gui.timeThreshAdvOffE.insert(0, i)

		
		#Initialize downstream parameters to 0
		gui.tempThreshAdvOnE.delete(0, "end")
		gui.tempThreshAdvOffE.delete(0, "end")
		gui.minSlopeOnE.delete(0, "end")
		gui.minSlopeOffE.delete(0, "end")
		gui.slopeRangeOnE.delete(0, "end")
		gui.slopeRangeOffE.delete(0, "end")
		gui.tempThreshAdvOnE.insert(0, 0)
		gui.tempThreshAdvOffE.insert(0, 0)
		gui.minSlopeOnE.insert(0, 0)
		gui.minSlopeOffE.insert(0, 0)
		gui.slopeRangeOnE.insert(0, paramDict["rangeSyncedStart"])
		gui.slopeRangeOffE.insert(0, paramDict["rangeSyncedStart"])
		
		#Initialize vertex migration to off
		gui.vertMigrationCK.deselect()
		
		coreVerts = coreVD.getCoreVerts(gui, trainBlock)
		
		
		#Bypasses further testing if penalty from too few vertices (too restrictive of settings) is already greater than best score
		if scoreAlgo(gui, userVertIs, trainBlock, bestScore) is not "Void2":
			if gui.decoupleTempsBV.get():
				#Test downstream parameters with this combination of duration thresholds
				bestScore = trainOnTemp(gui, paramDict, userVertIs, coreVerts, bestScore)
			else:
				del trainBlock
				trainBlock = coreC.block(gui, 0, (len(gui.masterList) - 1), False)
				
				trainTempsSynced(gui, paramDict, userVertIs, coreVerts, bestScore)
		else:
			# print("break at sync dur")
			break
				
	return bestScore

#Set start, stop, and step for every ML parameter based on depth slider value
def getMLDict(gui):
	depthVar = int(gui.MLDepthVar.get())
	
	if depthVar == 1:
		dict = {
				"durSyncedStart" : 3, 	"durSyncedStop" : 10,	"durSyncedStep" : 6,
				"onDurStart" : 3, 		"onDurStop" : 10, 		"onDurStep" : 6,
				"offDurStart" : 3, 		"offDurStop" : 10, 		"offDurStep" : 6,
				"tempSyncedStart" : 0,	"tempSyncedStop" : 13, 	"tempSyncedStep" : 6,
				"onTempStart" : 0,		"onTempStop" : 13, 		"onTempStep" : 6,
				"offTempStart" : 0,		"offTempStop" : 13, 	"offTempStep" : 6,
				"slopeSyncedStart" : 0,	"slopeSyncedStop" : 4, 	"slopeSyncedStep" : 3,
				"onSlopeStart" : 0, 	"onSlopeStop" : 4, 		"onSlopeStep" : 3,
				"offSlopeStart" : 0, 	"offSlopeStop" : 4, 	"offSlopeStep" : 3,
				"rangeSyncedStart" : 5, "rangeSyncedStop" : 6, "rangeSyncedStep" : 2,
				"onRangeStart" : 5, 	"onRangeStop" : 6, 		"onRangeStep" : 2,
				"offRangeStart" : 5, 	"offRangeStop" : 6, 	"offRangeStep" : 2
			   }
			
	elif depthVar == 2:
		dict = {
				"durSyncedStart" : 3, 	"durSyncedStop" : 12,	"durSyncedStep" : 4,
				"onDurStart" : 3, 		"onDurStop" : 12, 		"onDurStep" : 4,
				"offDurStart" : 3, 		"offDurStop" : 12, 		"offDurStep" : 4,
				"tempSyncedStart" : 0,	"tempSyncedStop" : 13, 	"tempSyncedStep" : 4,
				"onTempStart" : 0,		"onTempStop" : 13, 		"onTempStep" : 4,
				"offTempStart" : 0,		"offTempStop" : 13, 	"offTempStep" : 4,
				"slopeSyncedStart" : 0,	"slopeSyncedStop" : 4, 	"slopeSyncedStep" : 3,
				"onSlopeStart" : 0, 	"onSlopeStop" : 4, 		"onSlopeStep" : 3,
				"offSlopeStart" : 0, 	"offSlopeStop" : 4, 	"offSlopeStep" : 3,
				"rangeSyncedStart" : 5, "rangeSyncedStop" : 11, "rangeSyncedStep" : 5,
				"onRangeStart" : 5, 	"onRangeStop" : 11, 		"onRangeStep" : 5,
				"offRangeStart" : 5, 	"offRangeStop" : 11, 	"offRangeStep" : 5
			   }
	
	elif depthVar == 3:
		dict = {
				"durSyncedStart" : 3, 	"durSyncedStop" : 19,	"durSyncedStep" : 3,
				"onDurStart" : 3, 		"onDurStop" : 19, 		"onDurStep" : 3,
				"offDurStart" : 3, 		"offDurStop" : 19, 		"offDurStep" : 3,
				"tempSyncedStart" : 0,	"tempSyncedStop" : 13, 	"tempSyncedStep" : 4,
				"onTempStart" : 0,		"onTempStop" : 13, 		"onTempStep" : 4,
				"offTempStart" : 0,		"offTempStop" : 13, 	"offTempStep" : 4,
				"slopeSyncedStart" : 0,	"slopeSyncedStop" : 5, 	"slopeSyncedStep" : 2,
				"onSlopeStart" : 0, 	"onSlopeStop" : 5, 		"onSlopeStep" : 2,
				"offSlopeStart" : 0, 	"offSlopeStop" : 5, 	"offSlopeStep" : 2,
				"rangeSyncedStart" : 5, "rangeSyncedStop" : 11, "rangeSyncedStep" : 5,
				"onRangeStart" : 5, 	"onRangeStop" : 11, 		"onRangeStep" : 5,
				"offRangeStart" : 5, 	"offRangeStop" : 11, 	"offRangeStep" : 5
			   }
		
	elif depthVar == 4:
		dict = {
				"durSyncedStart" : 3, 	"durSyncedStop" : 21,	"durSyncedStep" : 2,
				"onDurStart" : 3, 		"onDurStop" : 21, 		"onDurStep" : 2,
				"offDurStart" : 3, 		"offDurStop" : 21, 		"offDurStep" : 2,
				"tempSyncedStart" : 0,	"tempSyncedStop" : 13, 	"tempSyncedStep" : 1,
				"onTempStart" : 0,		"onTempStop" : 13, 		"onTempStep" : 1,
				"offTempStart" : 0,		"offTempStop" : 13, 	"offTempStep" : 1,
				"slopeSyncedStart" : 0,	"slopeSyncedStop" : 5, 	"slopeSyncedStep" : 1,
				"onSlopeStart" : 0, 	"onSlopeStop" : 5, 		"onSlopeStep" : 1,
				"offSlopeStart" : 0, 	"offSlopeStop" : 5, 	"offSlopeStep" : 1,
				"rangeSyncedStart" : 5, "rangeSyncedStop" : 12, "rangeSyncedStep" : 3,
				"onRangeStart" : 5, 	"onRangeStop" : 12, 		"onRangeStep" : 3,
				"offRangeStart" : 5, 	"offRangeStop" : 12, 	"offRangeStep" : 3
			   }
	
	elif depthVar == 5:
		dict = {
				"durSyncedStart" : 3, 	"durSyncedStop" : 30,	"durSyncedStep" : 1,
				"onDurStart" : 3, 		"onDurStop" : 30, 		"onDurStep" : 1,
				"offDurStart" : 3, 		"offDurStop" : 30, 		"offDurStep" : 1,
				"tempSyncedStart" : 0,	"tempSyncedStop" : 21, 	"tempSyncedStep" : 1,
				"onTempStart" : 0,		"onTempStop" : 21, 		"onTempStep" : 1,
				"offTempStart" : 0,		"offTempStop" : 21, 	"offTempStep" : 1,
				"slopeSyncedStart" : 0,	"slopeSyncedStop" : 8, 	"slopeSyncedStep" : 1,
				"onSlopeStart" : 0, 	"onSlopeStop" : 8, 		"onSlopeStep" : 1,
				"offSlopeStart" : 0, 	"offSlopeStop" : 8, 	"offSlopeStep" : 1,
				"rangeSyncedStart" : 4, "rangeSyncedStop" : 20, "rangeSyncedStep" : 3,
				"onRangeStart" : 4, 	"onRangeStop" : 20, 		"onRangeStep" : 3,
				"offRangeStart" : 4, 	"offRangeStop" : 20, 	"offRangeStep" : 3
			   }
			   
	return dict
	
def runTraining(gui, userVertIs):
	paramDict = getMLDict(gui)
		
	saveSettings(gui)
	bestScore = 9999999999999999
	
	if gui.decoupleDursBV.get():
		bestScore = trainOnDur(gui, paramDict, userVertIs, bestScore)
	else:
		bestScore = trainDursSynced(gui, paramDict, userVertIs, bestScore)
		
	return bestScore
	
	
	
	
	
	
		