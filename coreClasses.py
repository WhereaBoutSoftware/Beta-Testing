import re
import statistics
import tkinter as tk
from tkinter import ttk, filedialog, font, messagebox, Scale

	
#Stores information about a vertex representing a peak or valley in the data	
class vert:
	def __init__(self, index, temp, vertType):
		#Initialize members
		self.index = int(index)
		self.temp  = float(temp)
		self.vertType = vertType
		
		
		
#Stores information about a single on or off-bout
class bout:
	def __init__(self, gui, start, stop, boutType):
		#Initialize members
		self.start    = start
		self.stop     = stop
		self.boutType  = boutType
		self.dur      = (gui.interval * (self.stop - self.start))
		self.meanTemp = 0
		self.meanAirTemp = 0
		self.temps         = []
		airTemps = []
		
		#Get all temparture readings comprising the bout
		for x in range(self.start, (self.stop) + 1):
			self.temps.append(float(gui.masterList[x][gui.tempsCol]))
		
		self.meanTemp = round(statistics.mean(self.temps), 3)
			
		if gui.airValid is True:
			for x in range(self.start, (self.stop) + 1):
				airTemps.append(float(gui.masterList[x][gui.airTempCol]))
				
			self.meanAirTemp = round(statistics.mean(airTemps), 3)
		else:
			airTemps.append(0)
			

		
		
		#Set temperature change
		if self.boutType == "off":
			self.tempChange = ((float(gui.masterList[self.start][gui.tempsCol]) - float(gui.masterList[self.stop][gui.tempsCol])))
		elif self.boutType == "on":
			self.tempChange = ((float(gui.masterList[self.stop][gui.tempsCol]) - float(gui.masterList[self.start][gui.tempsCol])))
		
#Discrete section of time such as daytime, nightime, or day/night pair (24hr period)
class block:
	def __init__(self, gui, start, stop, partial):
		#Variable Key:
			#Dur => duration
			#Dec => temperature decrease
			#Temp => temperature
			#Inc => temperature increase
			#superCust => time above custom set temperature in minutes
			#partial => true if the block is not "complete" (i.e. is cut short)
		
		self.gui          = gui			
		self.start        = int(start)
		self.stop         = int(stop)
		self.partial      = partial
		self.date         = ""
		
		self.temps        = []
		self.airTemps     = []
		self.vertices     = []
		self.bouts        = []
		
		self.offCount     = 0
		self.offDurMean   = 0
		self.offDurStDev  = 0
		
		self.offDecMean   = 0
		self.offDecStDev  = 0
		
		self.meanOffTemp  = 0
		self.offTimeSum   = 0
		
		self.onCount      = 0
		self.onDurMean    = 0
		self.onDurStDev   = 0
	
		self.onIncMean    = 0
		self.onIncStDev   = 0
	
		self.meanOnTemp   = 0
		self.onTimeSum    = 0
		
		self.meanTemp     = 0
		self.tempStDev    = 0
		
		self.medianTemp   = 0
		self.minTemp      = 0
		self.maxTemp      = 0
		
		self.meanAirTemp  = 0
		self.minAir       = 0
		self.maxAir       = 0
		
		self.superCust    = 0
		self.subCust      = 0
		self.boutsDropped = 0
		
	def getStats(self, gui):
		offDurs  = []
		offDecs  = []
		offTemps = []
		onDurs   = []
		onIncs   = []
		onTemps  = []
		
		#Get date of block
		try:
			dateFind = re.search("(\d+/\d+/\d+)", gui.masterList[self.start][gui.dateTimesCol])
			self.date = dateFind.group(0)
		except AttributeError:
			messagebox.showerror(("Date Error"), 
			"Could not find a date in the valid format.  Use \"Check\" button to debug.")
			return False
		
		#Compile every temperature for this block
		for line in gui.masterList[self.start:self.stop + 1]:
			curTemp = float(line[gui.tempsCol])
			self.temps.append(curTemp)
			if gui.airValid is True:
				curAirTemp = float(line[gui.airTempCol])
				self.airTemps.append(curAirTemp)
		
			#Get time above custom temperature
			if curTemp > float(gui.superCustE.get()):
				self.superCust += gui.interval
			
			#Get time below custom temperature
			if curTemp < float(gui.subCustE.get()):
				self.subCust += gui.interval
		
		for bout in self.bouts:
			if bout.boutType == "off":
				#Compile off-bout data
				offDurs.append(bout.dur)
				offDecs.append(bout.tempChange)	
				offTemps.append(bout.meanTemp)
			else:
				#Compile on-bout data
				onDurs.append(bout.dur)
				onIncs.append(bout.tempChange)
				onTemps.append(bout.meanTemp)
		
		#Get means, standard deviations, and standard errors
		if self.offCount > 0:
			self.offDurMean  = round(statistics.mean(offDurs), 2)
			self.offDecMean  = round(statistics.mean(offDecs), 3)
			self.meanOffTemp = round(statistics.mean(offTemps), 3)
			self.offTimeSum  = round(sum(offDurs), 2)
			if self.offCount > 1:
				self.offDurStDev = round(statistics.stdev(offDurs), 2)
			
				self.offDecStDev = round(statistics.stdev(offDecs), 3)
			
		if self.onCount > 0:
			self.onDurMean  = round(statistics.mean(onDurs), 2)
			self.onIncMean  = round(statistics.mean(onIncs), 3)
			self.meanOnTemp = round(statistics.mean(onTemps), 3)
			self.onTimeSum  = round(sum(onDurs), 2)
			if self.onCount > 1:
				self.onDurStDev = round(statistics.stdev(onDurs), 2)
			
				self.onIncStDev = round(statistics.stdev(onIncs), 3)
			
		#Calculate temperature statistics for this block
		self.meanTemp   = round(statistics.mean(self.temps), 3)
		if len(self.temps) > 1:
			self.tempStDev = round(statistics.stdev(self.temps), 3)
		
		self.medianTemp = statistics.median(self.temps)
		self.minTemp    = min(self.temps)
		self.maxTemp    = max(self.temps)
		
		if gui.airValid is True:
			self.meanAirTemp = round(statistics.mean(self.airTemps), 3)
			self.minAir = min(self.airTemps)
			self.maxAir = max(self.airTemps)
			# print("mean =", round(statistics.mean(airTemps), 3))
			# print("minAir =", min(self.airTemps))
			# print("maxAir =", max(self.airTemps))
		
		return True
	
	#Flag - can possibly simplify by just using offDecs list etc
	def depositMultiIns(self, gui):
		#Initialize variables
		bulkOffDur   = []
		bulkOffDec   = []
		bulkOffTemps = []
		bulkOnDur    = []
		bulkOnInc    = []
		bulkOnTemps  = []
		
		#Compile various data for all block periods
		for bout in self.bouts:
			if bout.boutType == "off":
				bulkOffDur.append(bout.dur)
				bulkOffDec.append(bout.tempChange)
				for temp in bout.temps:
					bulkOffTemps.append(temp)
			else:
				bulkOnDur.append(bout.dur)
				bulkOnInc.append(bout.tempChange)
				for temp in bout.temps:
					bulkOnTemps.append(temp)
	
		#Compile lists used to calculate statistics across multiple input files
		gui.multiInOffDurs  += bulkOffDur
		gui.multiInOffDecs  += bulkOffDec
		gui.multiInOnDurs   += bulkOnDur
		gui.multiInOnIncs   += bulkOnInc
		
#Used to store stats for all days or all nights
class blockGroup:
	def __init__(self, gui, blockList):
		#Initialize members
		self.gui            = gui
		self.blockList      = blockList
		self.temps          = []
		self.airTemps       = []
		
		self.offCount       = 0
		self.offDurMean     = 0 
		self.offDurStDev    = 0
		
		self.offDecMean     = 0
		self.offDecStDev    = 0
		
		self.meanOffTemp    = 0
		self.offTimeSum     = 0
		
		self.onCount        = 0
		self.onDurMean      = 0
		self.onDurStDev     = 0
	
		self.onIncMean      = 0
		self.onIncStDev     = 0
	
		self.meanOnTemp     = 0
		self.onTimeSum      = 0
		
		self.meanTemp       = 0
		self.tempStDev      = 0
	
		self.medianTemp     = 0
		self.minTemp        = 0
		self.maxTemp        = 0
		
		self.meanAirTemp    = 0
		self.minAir         = 0
		self.maxAir         = 0
		
		
		self.superCust      = 0
		self.subCust        = 0
		self.boutsDropped   = 0
		self.fullDayCount   = 0
		
	def getStats(self, gui, append = True):
		#Initialize variables
		bulkOffDur   = []
		bulkOffDec   = []
		bulkOffTemps = []
		bulkOnDur    = []
		bulkOnInc    = []
		bulkOnTemps  = []
			
		for block in self.blockList:
			#Compile every temperature measurement for all blocks			
			self.temps += block.temps
			
			if gui.airValid is True:
				self.airTemps += block.airTemps
			
			#Sum offCounts
			self.offCount += block.offCount	
			self.onCount += block.onCount
						
			#Sum time exceeding critical tempertures
			self.superCust += block.superCust
			self.subCust += block.subCust
			
			self.boutsDropped += block.boutsDropped
						
			#Compile various data for all block periods
			for bout in block.bouts:
				if bout.boutType == "off":
					bulkOffDur.append(bout.dur)
					bulkOffDec.append(bout.tempChange)
					for temp in bout.temps:
						bulkOffTemps.append(temp)
				else:
					bulkOnDur.append(bout.dur)
					bulkOnInc.append(bout.tempChange)
					for temp in bout.temps:
						bulkOnTemps.append(temp)
		
		#Get means, standard deviations, and standard errors
		if self.offCount > 0:
			self.offDurMean    = round(statistics.mean(bulkOffDur), 2)
			self.offDecMean    = round(statistics.mean(bulkOffDec), 3)
			self.meanOffTemp   = round(statistics.mean(bulkOffTemps), 3)
			self.offTimeSum    = round(sum(bulkOffDur), 2)
			if self.offCount > 1:
				self.offDurStDev   = round(statistics.stdev(bulkOffDur), 2)
			
				self.offDecStDev   = round(statistics.stdev(bulkOffDec), 3)
			
				
		if self.onCount > 0:
			self.onDurMean     = round(statistics.mean(bulkOnDur), 2)
			self.onIncMean     = round(statistics.mean(bulkOnInc), 3)
			self.meanOnTemp    = round(statistics.mean(bulkOnTemps), 3)
			self.onTimeSum     = round(sum(bulkOnDur), 2)
			if self.onCount > 1:
				self.onDurStDev    = round(statistics.stdev(bulkOnDur), 2)
			
				self.onIncStDev    = round(statistics.stdev(bulkOnInc), 3)
			
			
		#Calculate temperature statistics for all blocks
		self.meanTemp      = round(statistics.mean(self.temps), 3)
		if len(self.temps) > 1:
			self.tempStDev = round(statistics.stdev(self.temps), 3)
		
		self.medianTemp = statistics.median(self.temps)
		self.minTemp    = min(self.temps)
		self.maxTemp    = max(self.temps)
		
		if gui.airValid is True:
			self.meanAirTemp = round(statistics.mean(self.airTemps), 3)
			self.minAir = min(self.airTemps)
			self.maxAir = max(self.airTemps)
		
