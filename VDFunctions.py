import statistics
import re
import tkinter as tk
from tkinter import messagebox
import time

import coreClasses as coreC
import coreFunctions as coreF


def getRefinedVerts(gui, block):
	if float(gui.tempThreshAdvOnE.get()) != 0 or float(gui.tempThreshAdvOffE.get()) != 0:
		purgeByTemp(gui, block)
		purgeRedundantTypes(gui, block)
		moveToRegExtreme(gui, block)
		
	if float(gui.minSlopeOnE.get()) != 0 or float(gui.minSlopeOffE.get()) != 0:
		purgeBySlope(gui, block)
		purgeRedundantTypes(gui, block)
		# moveToRegExtreme(gui, block)
	
	return block.vertices
		
def migrateBySlope(gui, block, vertIndex):
	curVert = block.vertices[vertIndex]
	if curVert.vertType == "offStart":
		minSlope = float(gui.minSlopeOffE.get())
		slopeRange = int(gui.slopeRangeOffE.get())
	#Initialize values for on-bout
	else:
		minSlope = float(gui.minSlopeOnE.get())
		slopeRange = int(gui.slopeRangeOnE.get())
		
	#Set start of search to index of next vertex if it exists
	searchStart = curVert.index
	#If there is not another vertex, set stop to that vertex index minus range
	if vertIndex < (len(block.vertices) - 1):
		searchStop = (block.vertices[vertIndex + 1].index - slopeRange)
	else:
		searchStop = (block.stop - slopeRange)#(flag) may need to change to stop - 1
		
	#Parse datapoints
	for x in range(searchStart, searchStop):
		#If sufficient slope found, move vertex
		if coreF.checkSlopeSimple(gui, x, minSlope, slopeRange):
			newVertIndex =  coreF.findVertexI(gui, curVert.vertType, x, (x + slopeRange))
			block.vertices[vertIndex].index = newVertIndex
			block.vertices[vertIndex].temp = float(gui.masterList[newVertIndex][gui.tempsCol])		
			return True
			
	return False
		
		
def purgeBySlope(gui, block):
	popIndices = []
	
	if len(block.vertices) > 2:
		#Delete vertices if they do not meet minimum slope change
		for i in range (0, (len(block.vertices))):
			#Skip index, i, if already selected for deletion
			if i is 0 or (i - 1) not in popIndices:						
				curVert = block.vertices[i]
				slopeStart = curVert.index
				valid = True
			
				#Check off-bouts
				if curVert.vertType is "offStart":
					if float(gui.minSlopeOffE.get()) is 0:
						break
					minSlope = float(gui.minSlopeOffE.get())
					slopeRange = int(gui.slopeRangeOffE.get())
				elif curVert.vertType is "onStart":
					if float(gui.minSlopeOnE.get()) is 0:
						break
					minSlope = float(gui.minSlopeOnE.get())
					slopeRange = int(gui.slopeRangeOnE.get())
						
				
				#Special case if last vertex
				if i == (len(block.vertices) - 1):
					if (slopeStart + slopeRange) > block.stop:
						slopeStop = block.stop
						slopeRange = (slopeStop - slopeStart)
					else:
						slopeStop = (slopeStart + slopeRange)
				#Make sure range doesn't extend past next vertex
				else:
					if (slopeStart + slopeRange) > block.vertices[i + 1].index:
						slopeStop = block.vertices[i + 1].index
						slopeRange = (slopeStop - slopeStart)
					else:
						slopeStop = (slopeStart + slopeRange)
						
				#Calculate and check slope
				tempDif = (coreF.adjacentMean(gui, slopeStop) - coreF.adjacentMean(gui, slopeStart))		
		
				try:
					slope = (tempDif / slopeRange)
				except ZeroDivisionError:
					break				
				
				#Mark vertex for deletion if initial slope is not steep enough
				if curVert.vertType is "offStart":
					if slope > minSlope:
						valid = False
				elif curVert.vertType is "onStart":
					#Mark vertex for deletion if initial slope is not steep enough
					if slope < minSlope:
						valid = False

				#If slope did not meet requirement
				if not valid:
					if gui.vertMigrationBV.get():
						#Attempt migration
						migResult = migrateBySlope(gui, block, i)
						if migResult is False:
							popIndices.append(i)
					#Mark vertex for deletion if no migration location found
					else:
						popIndices.append(i)
				
		#Delete marked vertices
		popCount = 0
		block.boutsDropped += len(popIndices)
		# print("slope bouts dropped = ", block.boutsDropped)
		# print("vertices popped by slope =", len(popIndices))
		#Delete vertices identified in previous for loop
		for index in popIndices:
			block.vertices.pop(index - popCount)
			popCount += 1
	
def purgeByTemp(gui, block):
	popIndices = []
	
	if len(block.vertices) > 4:
		prevVert = block.vertices[3]
		
		#Delete vertices if they do not meet minimum temperature change
		for i in range (4, (len(block.vertices))):
			#Skip index, i, if i - 1 is already selected for deletion
			if (i - 1) not in popIndices:
				curVert = block.vertices[i]
				
				if curVert.vertType == "offStart":
					#Check temperature increase from last vertex to current
					if ((curVert.temp - prevVert.temp) > float(gui.tempThreshAdvOnE.get())):
						prevVert = curVert
					else:
						if (i + 1) < len(block.vertices):
							curVert = block.vertices[i + 1]
							
							if curVert.temp < prevVert.temp:
								prevVert = curVert
						#Mark vertex for later deletion if it did not meet temperature change requirement
						popIndices.append(i)
					
				else:
					#Check temperature decrease from last vertex to current
					if ((prevVert.temp - curVert.temp) > float(gui.tempThreshAdvOffE.get())):
							prevVert = curVert
					else:
						if (i + 1) < len(block.vertices):
							curVert = block.vertices[i + 1]
							
							if curVert.temp > prevVert.temp:
								prevVert = curVert
						#Mark vertex for later deletion if it did not meet temperature change requirement
						popIndices.append(i)
						
		popCount = 0
		block.boutsDropped += len(popIndices)
		# print("temp bouts dropped = ", block.boutsDropped)
		# print("vertices popped by temp =", len(popIndices))
		#Delete vertices identified in previous for loop
		for index in popIndices:
			block.vertices.pop(index - popCount)
			popCount += 1

def purgeRedundantTypes(gui, block):
	if len(block.vertices) > 2:
		changeMade = True
		prevVert = block.vertices[0]
		
		# Delete vertex if there are consecutive offStarts or consecutive onStarts (This arises due to deletion of vertices above)
		while changeMade:
			changeMade = False
			popCount = 0
			
			for i in range (1, len(block.vertices)):
				if i < (len(block.vertices) - popCount):
					curVert = block.vertices[i - popCount]
					# If both offStarts or both onStarts, delete vertex
					if prevVert.vertType == curVert.vertType:
						block.vertices.pop(i - popCount)
						changeMade = True
						popCount += 1
					else:
						prevVert = curVert
		

def moveToRegExtreme(gui, block):
	if len(block.vertices) > 1:
		#Determine if first vertex is offStart or onStart
		vertType = block.vertices[1].vertType
		
			
	#Change offStarts to highest point between previous and next vertex, onStarts to lowest
	for i in range (1, (len(block.vertices) - 1)):	
		#Do not move static vertices
		# if not block.vertices[i].static:
		#If curVert is a offStart, look for higher point before and after
		if vertType == "offStart":
			maxIndex = block.vertices[i].index
			for x in range(block.vertices[i - 1].index, block.vertices[i + 1].index):
				#If higher point found, save index
				if float(gui.masterList[x][gui.tempsCol]) >= float(gui.masterList[maxIndex][gui.tempsCol]):
					maxIndex = x
			
			#Move vertex if higher point found
			if not maxIndex == block.vertices[i].index:
				block.vertices[i].index = maxIndex
				block.vertices[i].temp = float(gui.masterList[maxIndex][gui.tempsCol])
				
			vertType = "onStart"
		#If curVert is a onStart, look for lower point before and after
		else:
			minIndex = block.vertices[i].index
			for x in range(block.vertices[i - 1].index, block.vertices[i + 1].index):
				#If lower point found, save index
				if float(gui.masterList[x][gui.tempsCol]) <= float(gui.masterList[minIndex][gui.tempsCol]):
					minIndex = x
			
			#Move vertex if lower point found
			if not minIndex == block.vertices[i].index:		
				block.vertices[i].index = minIndex
				block.vertices[i].temp = float(gui.masterList[minIndex][gui.tempsCol])
				
			vertType = "offStart"
		
					
def getCoreVerts(gui, block):
		vertices = []
		boutType = "on"
		vertType = "onStart"
			
		#Check if data is initially decreasing
		if coreF.adjacentMean(gui, (block.start + 3)) < coreF.adjacentMean(gui, block.start):
			boutType = "off"
			vertType = "offStart"
		
		#Add initial vertex at start of block (will be deleted later because will cause partial bout)
		vertices.append(coreC.vert(block.start, gui.masterList[block.start][gui.tempsCol], vertType))
		prevVertI = block.start
		
			
		#Get all vertices imposing only a duration threshold
		for i in range(block.start, (block.stop)):
			#If currently in off-bout (going down)
			if boutType == "off":
				#Check for significant increase
				if coreF.sigChange(gui, boutType, i, block.stop):
					# (flag)print("sigchange datapoint =", gui.masterList[i][gui.dataPointCol])
					#Find local minimum (onStart)
					vertType = "onStart"
					curVertI = coreF.findVertexI(gui, vertType, prevVertI, (i + int(gui.vertSearchDownLimE.get())))
					vertices.append(coreC.vert(curVertI, gui.masterList[curVertI][gui.tempsCol], vertType))
					prevVertI = curVertI
					boutType = "on"
			#If currently in on-bout (going up)					
			else:
				#Check for significant decrease
				if coreF.sigChange(gui, boutType, i, block.stop):
					#Find local maximum (offStart)						
					vertType = "offStart"
					curVertI = coreF.findVertexI(gui, vertType, prevVertI, (i + int(gui.vertSearchDownLimE.get())))
					vertices.append(coreC.vert(curVertI, gui.masterList[curVertI][gui.tempsCol], vertType))
					prevVertI = curVertI
					boutType = "off"
		
		#Add final vertex at end of block (will be deleted later bacause will cause partial bout
		vertices.append(coreC.vert(block.stop, gui.masterList[block.stop][gui.tempsCol], vertType))
				
		return vertices
			
#Get vertices for a given day
def getVerts(gui, block, coreVerts = False, refinedVerts = False):

	#Get core vertices if not provided
	if not coreVerts:
		coreVerts = getCoreVerts(gui, block)	
		
	block.vertices = coreVerts
			
	#Refinded vertices if not proviede
	if not refinedVerts:
		getRefinedVerts(gui, block)
		
		
	#Delete first and last vertices to prevent partial bouts
	if len(block.vertices) > 1:
		#Delete first and last vertex because it is likely not a true offStart or true onStart
		del block.vertices[0]
		# del block.vertices[-1]
		
	# print("vert0 type =", block.vertices[0].vertType)
	# print("vert1 type =", block.vertices[1].vertType)
			
	# print ("Get core verts dur = ", afterCoreVerts - start)
	# print ("restrict dur", afterRestrict - afterCoreVerts)
	# print ("migrate dur =", stop - afterRestrict)
	# print ("total get verts dur =", stop - start, "\n")
	
	