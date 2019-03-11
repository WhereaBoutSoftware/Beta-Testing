#Import core libraries
import re as re
import math as math
import statistics as statistics
import time as time
from time import sleep
import os as os
import traceback as traceback

import configparser
import sys

#GUI libraries
import tkinter as tk
from tkinter import ttk, filedialog, font, messagebox, Scale

import PIL
from PIL import ImageTk, Image
import subprocess
from shutil import copyfile



#Local libraries
import coreFunctions as coreF
import coreClasses as coreC
import MLFunctions as coreML
import VDFunctions as coreVD

#Initialize root for GUI
root = tk.Tk()

#Initialize fonts
STANDARD_FONT = font.Font(size = 10)
HELP_FONT = font.Font(size = 8)
HEADER_FONT = font.Font(size = 12, weight = "bold")
SUBHEADER_FONT = "Helvetica 10 bold"




#Class storing all information for GUI
class guiClass():
	def __init__(self):
		#Gets core directory for later file pathing
		self.coreDir = os.path.normpath(os.getcwd() + os.sep + os.pardir)
	
		#Initialize configuration file
		self.initConfig()
			
		#Initialize column identities
		self.dataPointCol = 0
		self.dateTimesCol = 1
		self.tempsCol = 2
		self.airTempCol = 3
			
		#Variables used for storing information accross multiple input files
		self.multiInOffDurs    = []
		self.multiInOffDecs    = []
		self.multiInOnDurs     = []
		self.multiInOnIncs     = []
		self.multiInDayTemps   = []
		self.multiInNightTemps = []
		self.multiInAirTemps = []
		self.multiInFullDayCount = 0
		self.inPathName = ()
		self.inputRoot = None
		self.verticesProvided = False
		self.airValid = True
		self.dragWarnConfig = self.config.get("Main Settings", "drag_warn")
		self.airWarnConfig = self.config.get("Main Settings", "air_temp_warn")
				
		#Configure root
		root.wm_title("NestIQ")
		root.geometry("370x720")
		root.configure(background = "white")
		
		#Create 1 x 30 grid in GUI
		rows = 0
		while rows < 30:
			root.rowconfigure(rows, weight = 1)
			rows += 1
			
		root.columnconfigure(0, weight = 1)
		
		#Initialize notebook (allows for tabs)
		nb = ttk.Notebook(root)
		nb.grid(row = 1, rowspan = 28, columnspan = 1, sticky = "NESW")

		#Add tabs
		tab1 = ttk.Frame(nb)
		tab2 = ttk.Frame(nb)
		tab3 = ttk.Frame(nb)
		tab4 = ttk.Frame(nb)
		nb.add(tab1, text = "Main")
		nb.add(tab2, text = "Plot Options")
		nb.add(tab3, text = "Stats Options")
		nb.add(tab4, text = "Advanced")
		
		#---------------------------------------------------------Tab 1-------------------------------------------------		
		#Add title background
		titleBG = tk.Label(tab1, text = "", bg = "red4")
		titleBG.grid(row = 0, sticky = "NSEW")
		
		#Program title at top of Main tab
		progTitle = tk.Label(tab1, text = "NestIQ", fg = "white", bg = "red4", font = ("Helvetica", 18))
		progTitle.grid(row = 0, sticky = "NSW", padx = 10, pady = 5)
				
		#Main tab help button
		helpB = tk.Button(tab1, text = "Help", command = self.help)
		helpB.grid(row = 0, sticky = "NW", padx = 335)
		helpB.configure(width = 4, height = 0)
		helpB["font"] = HELP_FONT

		#Data nput file
		self.inputLabel = tk.Label(tab1, text = "Input file:", font = STANDARD_FONT)
		self.inputLabel.grid(row = 1, sticky = "W", padx = 10, pady = (5, 0))
		self.inputFileE = tk.Entry(tab1, width = 26)
		self.inputFileE.grid(row = 1, sticky = "W", padx = 70, pady = (10, 0))
		self.inputB = tk.Button(tab1, text = "Browse File", command = (lambda: self.getInFileName(self.inputFileE)))
		self.inputB.grid(row = 1, sticky = "W", padx = 236, pady = (10, 0))
		self.inputB.configure(background = "white")
		
		#Check input file button
		checkDataB = tk.Button(tab1, text = "Check", command = (lambda: self.checkInFile(self.inputFileE, root)))
		checkDataB.grid(row = 1, sticky = "W", padx = 310, pady = (10, 0))
		checkDataB.configure(background = "white")
		
		#Edit mode checkbutton
		self.editModeBV = tk.BooleanVar()
		self.editCK = tk.Checkbutton(tab1, text = "Edit mode", variable = self.editModeBV, font = STANDARD_FONT)
		self.editCK.grid(row = 2, sticky = "NW", padx = 25)
		
		#Use provided vertices checkbutton
		self.useProvidedBV = tk.BooleanVar()
		self.useProvidedCK = tk.Checkbutton(tab1, text = "Use provided vertices", variable = self.useProvidedBV, font = STANDARD_FONT)
		self.useProvidedCK.grid(row = 3, sticky = "NW", padx = 25)
		
		#HTML vertex selection file
		self.vertexFileLabel = tk.Label(tab1, text = "Vertex file:", font = STANDARD_FONT)
		self.vertexFileE = tk.Entry(tab1, width = 18)
		self.vertexFileB = tk.Button(tab1, text = "Browse File", command = (lambda: self.getFileName(self.vertexFileE)))
		self.vertexFileB.configure(background = "white")
		
		#HTML vertex selection check button
		self.checkVertsB = tk.Button(tab1, text = "Check", command = (lambda: self.checkVertSourceFile(self.vertexFileE.get(), "Main", True)))
		self.checkVertsB.configure(background = "white")

		#Indexes column label and entry box
		# indexColLabel = tk.Label(tab1, text = "Indexes column number:", font = STANDARD_FONT)
		# indexColLabel.grid(row = 3, sticky = "W", padx = 10)
		# self.indicesColE = tk.Entry(tab1, width = 5)
		# self.indicesColE.insert(0, self.config.get("Main Settings", "indicesColumnNumber"))
		# self.indicesColE.grid(row = 3, sticky = "W", padx = 220, pady = (5, 0))
		
		#Dates and times column label and entry box
		# dateTimeColumnLabel = tk.Label(tab1, text = "Dates and times column number:", font = STANDARD_FONT)
		# dateTimeColumnLabel.grid(row = 4, sticky = "W", padx = 10, pady = 10)
		# self.dateTimesColE = tk.Entry(tab1, width = 5)
		# self.dateTimesColE.insert(0, self.config.get("Main Settings", "datesTimesColumnNumber"))
		# self.dateTimesColE.grid(row = 4, sticky = "W", padx = 220, pady = (5, 0))
		
		#Temperatures column label and entry box
		# tempColLabel = tk.Label(tab1, text = "Temperatures column number:", font = STANDARD_FONT)
		# tempColLabel.grid(row = 5, sticky = "W", padx = 10, pady = (0, 15))
		# self.tempsColE = tk.Entry(tab1, width = 5)
		# self.tempsColE.insert(0, self.config.get("Main Settings", "temperaturesColumnNumber"))
		# self.tempsColE.grid(row = 5, sticky = "W", padx = 220, pady = (0, 10))		
		
		#Graph label, checkbox, and browse button
		self.makeGraphBV = tk.BooleanVar()
		self.graphCK = tk.Checkbutton(tab1, text = "Generate Graph", variable = self.makeGraphBV, font = STANDARD_FONT)
		self.graphCK.grid(row = 8, sticky = "W", padx = 10)
		self.gFileTitle = tk.Label(tab1, text = "File name:", font = STANDARD_FONT)
		self.graphE = tk.Entry(tab1, width = 24)
		self.graphE.insert(0, "graph.html")
		self.graphB = tk.Button(tab1, text = "Browse Directory", command = (lambda: self.getDirName(self.graphE)))
		
		#Adds "(x)" to end of default file name if the file already exists
		i = 1
		while os.path.exists(self.graphE.get()):
			self.graphE.delete(0, "end")
			self.graphE.insert(0, ("graph(" + str(i) + ").html"))
			i += 1	
			
		#Initialize Generate Graph to selected
		self.graphCK.select()
		self.gFileTitle.grid(row = 9, sticky = "W", padx = 32)
		self.graphE.grid(row = 9, sticky = "W", padx = 102)
		self.graphB.grid(row = 9, sticky = "W", padx = 255)
		self.graphB.configure(background = "white")

		#Generate stats label, checkbox, and browse button
		self.makeOutputBV = tk.BooleanVar()
		self.outCK = tk.Checkbutton(tab1, text = "Output Statistics", variable = self.makeOutputBV, font = STANDARD_FONT)
		self.outCK.grid(row = 10, sticky = "NW", padx = 10, pady = (10, 0))
		self.oFileTitle = tk.Label(tab1, text = "File name:", font = STANDARD_FONT)
		self.outE = tk.Entry(tab1, width = 24)
		self.outE.insert(0, "stats.csv")
		self.outB = tk.Button(tab1, text = "Browse Directory", command = (lambda: self.getDirName(self.outE)))
		
		#Adds "(x)" to end of default file name if the file already exists
		i = 1
		while os.path.exists(self.outE.get()):
			self.outE.delete(0, "end")
			self.outE.insert(0, ("stats(" + str(i) + ").csv"))
			i += 1	
		
		#Initialize generate stats to selected
		self.outCK.select()
		self.oFileTitle.grid(row = 11, sticky = "W", padx = 32)
		self.outE.grid(row = 11, sticky = "W", padx = 102)
		self.outB.grid(row = 11, sticky = "W", padx = 255)
		self.outB.configure(background = "white")

		#Compile Stats label, checkbox, and browse button
		self.complileStatsBV = tk.BooleanVar()
		self.compileCK = tk.Checkbutton(tab1, text = "Compile Statistics", variable = self.complileStatsBV, font = STANDARD_FONT)
		self.compileCK.grid(row = 12, sticky = "W", padx = 10, pady = (10, 0))
		self.aFileTitle = tk.Label(tab1, text = "File name:", font = STANDARD_FONT)
		self.compileE = tk.Entry(tab1, width = 24)
		self.compileE.insert(0, "compileStats.csv")
		self.compileB = tk.Button(tab1, text = "Browse Directory", command = (lambda: self.getDirName(self.compileE)))

		#Add separator
		separator = ttk.Separator(tab1, orient = "horizontal")
		separator.grid(row = 14, sticky = "NSEW", pady = 10)
		
		#Data time interval label and entry box
		intervalTitle = tk.Label(tab1, text = "Data time interval (minutes):", font = SUBHEADER_FONT)
		intervalTitle.grid(row = 17, sticky = "W", padx = 10)
		self.intervalE = tk.Entry(tab1, width = 5)
		self.intervalE.insert(0, self.config.get("Main Settings", "data_Time_Interval"))
		self.intervalE.grid(row = 17, sticky = "W", padx = 220)
		
		#Duration threshold label and entry box
		timeThreshTitle = tk.Label(tab1, text = "Duration threshold (data points):", font = STANDARD_FONT)
		timeThreshTitle.grid(row = 18, sticky = "W", padx = 10, pady = 10)
		self.timeThreshE = tk.Entry(tab1, width = 5)
		self.timeThreshE.insert(0, self.config.get("Main Settings", "duration_Threshold"))
		self.timeThreshE.grid(row = 18, sticky = "W", padx = 220)

		#Temperature threshold label and entry box
		tempThreshTitle = tk.Label(tab1, text = "Temperature threshold:", font = STANDARD_FONT)
		tempThreshTitle.grid(row = 19, sticky = "W", padx = 10)
		self.tempThreshE = tk.Entry(tab1, width = 5)
		self.tempThreshE.insert(0, self.config.get("Main Settings", "temperature_Threshold"))
		self.tempThreshE.grid(row = 19, sticky = "W", padx = 220)
		
		spacer1 = tk.Label(tab1, text = " ")
		spacer1.grid(row = 20)
		
		#Initialize daytime and nightime entry boxes
		dayStartLabel = tk.Label(tab1, text = "Day start time:", font = STANDARD_FONT)
		nightStartLabel = tk.Label(tab1, text = "Night start time:", font = STANDARD_FONT)
		self.dayStartE = tk.Entry(tab1, width = 7)
		self.dayStartE.insert(0, self.config.get("Main Settings", "day_Start_Time"))
		self.nightStartE = tk.Entry(tab1, width = 7)
		self.nightStartE.insert(0, self.config.get("Main Settings", "night_Start_Time"))
		
		#Display daytime and nightime entry boxes
		dayStartLabel.grid(row = 22, sticky = "W", padx = 10)
		nightStartLabel.grid(row = 23, sticky = "NW", padx = 10, pady = 10)
		self.dayStartE.grid(row = 22, sticky = "W", padx = 120)
		self.nightStartE.grid(row = 23, sticky = "W", padx = 120)
		
		#Restrict search checkbutton
		self.restrictSearchBV = tk.BooleanVar()
		self.restrictSearchCK = tk.Checkbutton(tab1, text = "Restrict search to daytime", variable = self.restrictSearchBV, font = STANDARD_FONT)
		self.restrictSearchCK.grid(row = 25, sticky = "NW", padx = 10, pady = (10, 0))
		
		#Initialize based on config file
		if self.config.get("Main Settings", "restrict_bout_search").lower() == "yes":
			self.restrictSearchCK.select()
		else:
			self.restrictSearchCK.deselect()
			
			
				
		def mainTab_callback(*args):
			if self.useProvidedBV.get():
				self.vertexFileLabel.grid(row = 4, sticky = "W", padx = 48)
				self.vertexFileE.grid(row = 4, sticky = "W", padx = 117)
				self.vertexFileB.grid(row = 4, sticky = "W", padx = 236)
				self.checkVertsB.grid(row = 4, sticky = "W", padx = 310)
				self.vertexFileB.configure(background = "white")
			else:
				self.vertexFileLabel.grid_forget()
				self.vertexFileE.grid_forget()
				self.vertexFileB.grid_forget()
				self.checkVertsB.grid_forget()
				
			if self.makeGraphBV.get():
				self.gFileTitle.grid(row = 9, sticky = "W", padx = 30)
				self.graphE.grid(row = 9, sticky = "W", padx = 102)
				self.graphB.grid(row = 9, sticky = "W", padx = 255)
				self.graphB.configure(background = "white")
			else:
				self.gFileTitle.grid_forget()
				self.graphE.grid_forget()
				self.graphB.grid_forget()
			
			if self.makeOutputBV.get():
				self.oFileTitle.grid(row = 11, sticky = "W", padx = 32)
				self.outE.grid(row = 11, sticky = "W", padx = 102)
				self.outB.grid(row = 11, sticky = "W", padx = 255)
				self.outB.configure(background = "white")
			else:
				self.oFileTitle.grid_forget()
				self.outE.grid_forget()
				self.outB.grid_forget()
				
			if self.complileStatsBV.get():
				self.aFileTitle.grid(row = 13, sticky = "W", padx = 32)
				self.compileE.grid(row = 13, sticky = "W", padx = 102)
				self.compileB.grid(row = 13, sticky = "W", padx = 255)
				self.compileB.configure(background = "white")
			else:
				self.compileE.grid_forget()
				self.aFileTitle.grid_forget()
				self.compileB.grid_forget()
				
				
		mainTab_callback()
				
		# Establish tracing
		self.useProvidedBV.trace("w", mainTab_callback)
		self.makeGraphBV.trace("w", mainTab_callback)
		self.makeOutputBV.trace("w", mainTab_callback)
		self.complileStatsBV.trace("w", mainTab_callback)
		
		

			
		#---------------------------------------------------------tab 2-------------------------------------------
		#Add header background
		tab2BG = tk.Label(tab2, text = "", bg = "red4")
		tab2BG.grid(row = 0, sticky = "NSEW")
		
		#Hello?
		hello = tk.Label(tab2, text = "NestIQ", fg = "white", bg = "red4", font = ("Helvetica", 18))
		hello.grid(row = 0, sticky = "NSW", padx = 10, pady = 5)
		
		#Create label for radio buttons
		plotDimLabel = tk.Label(tab2, text = "Plot dimensions", font = STANDARD_FONT)
		plotDimLabel.grid(row = 4, sticky = "W", padx = 10, pady = (5, 0))
		
		#Create plot dimensions radio buttons
		self.plotDimVar = tk.IntVar()
		autoDimRB = tk.Radiobutton(tab2, text = "Auto", variable = self.plotDimVar, value = 1)
		autoDimRB.grid(row = 5, sticky = "W", padx = 25)
		manDimRB = tk.Radiobutton(tab2, text="Manual", variable = self.plotDimVar, value = 2)
		manDimRB.grid(row = 6, sticky = "W", padx = 25, pady = (0, 0))
		
		
		#X and Y value entry boxes
		plotDimX_L = tk.Label(tab2, text = "x:", font = STANDARD_FONT)
		plotDimY_L = tk.Label(tab2, text = "y:", font = STANDARD_FONT)
		plotDimX_L.grid(row = 6, sticky = "W", padx = 95)
		plotDimY_L.grid(row = 6, sticky = "W", padx = 150)
		self.plotDimXE = tk.Entry(tab2, width = 5)
		self.plotDimYE = tk.Entry(tab2, width = 5)
		self.plotDimXE.grid(row = 6, sticky = "W", padx = 110)
		self.plotDimYE.grid(row = 6, sticky = "W", padx = 165)
		
		#Title font size
		titleFontSize_L = tk.Label(tab2, text = "Plot title font size:", font = STANDARD_FONT)
		titleFontSize_L.grid(row = 8, sticky = "W", padx = 10, pady = (15, 5))
		self.titleFontSizeE = tk.Entry(tab2, width = 5)
		self.titleFontSizeE.grid(row = 8, sticky = "W", padx = 140, pady = (15, 5))
		
		#Axis title font size
		axisTitleFontSize_L = tk.Label(tab2, text = "Axis title font size:", font = STANDARD_FONT)
		axisTitleFontSize_L.grid(row = 9, sticky = "W", padx = 10, pady = 5)
		self.axisTitleFontSizeE = tk.Entry(tab2, width = 5)
		self.axisTitleFontSizeE.grid(row = 9, sticky = "W", padx = 140, pady = 5)
		
		#Axis label font size
		axisLabelFontSize_L = tk.Label(tab2, text = "Axis label font size:", font = STANDARD_FONT)
		axisLabelFontSize_L.grid(row = 10, sticky = "W", padx = 10, pady = 5)
		self.axisLabelFontSizeE = tk.Entry(tab2, width = 5)
		self.axisLabelFontSizeE.grid(row = 10, sticky = "W", padx = 140, pady = 5)
		
		#Axis tick size
		axisTickSize_L = tk.Label(tab2, text = "Axis tick size:", font = STANDARD_FONT)
		axisTickSize_L.grid(row = 11, sticky = "W", padx = 10, pady = 5)
		self.axisTickSizeE = tk.Entry(tab2, width = 5)
		self.axisTickSizeE.grid(row = 11, sticky = "W", padx = 140, pady = 5)

		# Legend font size
		tk.Label(tab2, text = "Legend font size:", font = STANDARD_FONT).grid(row = 12, sticky = "W", padx = 10, pady = 5)
		self.legendFontSizeE = tk.Entry(tab2, width = 5)
		self.legendFontSizeE.grid(row = 12, sticky = "W", padx = 140, pady = 5)

		#Add separator
		separator = ttk.Separator(tab2, orient = "horizontal")
		separator.grid(row = 14, sticky = "NSEW", pady = 10)
		
		#Column labels
		tk.Label(tab2, text = "Color", font = SUBHEADER_FONT).grid(row = 15, sticky = "NW", padx = (160, 0))
		tk.Label(tab2, text = "Size/Width", font = SUBHEADER_FONT).grid(row = 15, sticky = "NW", padx = (272, 0))
		
		#List color options
		_colorChoices = ["pink", "salmon", "red", "darkred", "orangered", "orange", "gold",  "darkkhaki", "beige", "saddlebrown", 
						 "yellow", "lime", "greenyellow", "yellowgreen", "olive", "green", "cyan", "aquamarine", "lightskyblue", 
						 "blue", "darkblue", "indigo", "darkviolet", "black", "gray", "slategray", "lightgray", "white"]
		# _colorChoices = {"pink", "red", "darkred", "orange", "darkorange", "gold", "yellow", "green", "darkgreen", "cyan", "blue", "darkblue", "black", "gray", "darkgray"}

		#Declare color variables
		self.eggTempPointColorVar = tk.StringVar()		
		self.eggTempLineColorVar = tk.StringVar()		
		self.boutColorVar = tk.StringVar()
		self.dayMarkerColorVar = tk.StringVar()
		self.airTempColorVar = tk.StringVar()
		
		# self.eggTempPointColorVar = ""
		# self.boutColorVar = ""
		# self.dayMarkerColorVar = ""
		# self.airTempColorVar = ""
		
		#Plot element labels
		tk.Label(tab2, text = "Egg temperature (point):").grid(row = 16, sticky = "NW", padx = (10, 0))
		tk.Label(tab2, text = "Egg temperature (line):").grid(row = 17, sticky = "NW", padx = (10, 0))
		tk.Label(tab2, text = "Bout predictions: ").grid(row = 18, sticky = "NW", padx = (10, 0))
		
		#Create color menus
		self.eggTempPointColor_PM = tk.OptionMenu(tab2, self.eggTempPointColorVar, *_colorChoices)
		self.eggTempPointColor_PM.grid(row = 16, sticky = "NW", padx = 150)
		self.eggTempLineColor_PM = tk.OptionMenu(tab2, self.eggTempLineColorVar, *_colorChoices)
		self.eggTempLineColor_PM.grid(row = 17, sticky = "NW", padx = 150)
		self.boutColor_PM = tk.OptionMenu(tab2, self.boutColorVar, *_colorChoices)
		self.boutColor_PM.grid(row = 18, sticky = "NW", padx = 150)
		self.dayMarkerColor_PM = tk.OptionMenu(tab2, self.dayMarkerColorVar, *_colorChoices)
		self.dayMarkerColor_PM.grid(row = 19, sticky = "NW", padx = 150)
		self.airTempColor_PM = tk.OptionMenu(tab2, self.airTempColorVar, *_colorChoices)
		self.airTempColor_PM.grid(row = 20, sticky = "NW", padx = 150)
		
		#Create size entry boxes
		self.eggTempPointSize_E = tk.Entry(tab2, width = 5)
		self.eggTempPointSize_E.grid(row = 16, sticky = "W", padx = 286)
		self.eggTempLineSize_E = tk.Entry(tab2, width = 5)
		self.eggTempLineSize_E.grid(row = 17, sticky = "W", padx = 286)
		self.boutSize_E = tk.Entry(tab2, width = 5)
		self.boutSize_E.grid(row = 18, sticky = "W", padx = 286)
		self.dayMarkerSize_E = tk.Entry(tab2, width = 5)
		self.dayMarkerSize_E.grid(row = 19, sticky = "W", padx = 286)
		self.airTempSize_E = tk.Entry(tab2, width = 5)
		self.airTempSize_E.grid(row = 20, sticky = "W", padx = 286)
		
		#Create checkbox for printing day makers
		self.showDayDelimsBV = tk.BooleanVar()
		self.showDayDelimsCK = tk.Checkbutton(tab2, text = "Day markers:", variable = self.showDayDelimsBV, font = STANDARD_FONT)
		self.showDayDelimsCK.grid(row = 19, sticky = "W", padx = (10, 0), pady = (5, 0))
		
		#Create checkbox for plotting air temperature
		self.showAirTempBV = tk.BooleanVar()
		self.showAirTempCK = tk.Checkbutton(tab2, text = "Air temperature:", variable = self.showAirTempBV, font = STANDARD_FONT)
		self.showAirTempCK.grid(row = 20, sticky = "W", padx = (10, 0))
		
		#Plot grid checkbox
		self.showGridBV = tk.BooleanVar()
		self.showGridCK = tk.Checkbutton(tab2, text = "Show grid", variable = self.showGridBV, font = STANDARD_FONT)
		self.showGridCK.grid(row = 21, sticky = "W", padx = (10, 0))	
	
		if self.config.get("Plot Options", "plot_dim_mode").lower() == "auto":
			self.plotDimVar.set(1)
		else:
			self.plotDimVar.set(2)
	
		self.plotDimXE.insert(0, self.config.get("Plot Options", "plot_x_dim"))
		self.plotDimYE.insert(0, self.config.get("Plot Options", "plot_y_dim"))
		
		self.titleFontSizeE.insert(0, self.config.get("Plot Options", "title_font_size"))
		self.axisTitleFontSizeE.insert(0, self.config.get("Plot Options", "axis_title_font_size"))
		self.axisLabelFontSizeE.insert(0, self.config.get("Plot Options", "axis_label_font_size"))
		self.axisTickSizeE.insert(0, self.config.get("Plot Options", "axis_tick_size"))
		self.legendFontSizeE.insert(0, self.config.get("Plot Options", "legend_font_size"))
	
	
		#Initialize values from config
		self.eggTempPointColorVar.set(self.config.get("Plot Options", "egg_temp_point_color"))
		self.eggTempLineColorVar.set(self.config.get("Plot Options", "egg_temp_line_color"))
		self.boutColorVar.set(self.config.get("Plot Options", "bout_prediction_color"))
		self.dayMarkerColorVar.set(self.config.get("Plot Options", "day_marker_color"))
		self.airTempColorVar.set(self.config.get("Plot Options", "air_temp_color"))
		
		
		self.eggTempPointSize_E.insert(0, self.config.get("Plot Options", "egg_temp_point_size"))
		self.eggTempLineSize_E.insert(0, self.config.get("Plot Options", "egg_temp_line_size"))
		self.boutSize_E.insert(0, self.config.get("Plot Options", "bout_prediction_size"))
		self.dayMarkerSize_E.insert(0, self.config.get("Plot Options", "day_marker_size"))
		self.airTempSize_E.insert(0, self.config.get("Plot Options", "air_temp_size"))
		
		

		if self.config.get("Plot Options", "show_day_marker").lower() == "yes":
			self.showDayDelimsCK.select()
		else:
			self.showDayDelimsCK.deselect()
			
		if self.config.get("Plot Options", "show_air_temp").lower() == "yes":
			self.showAirTempCK.select()
		else:
			self.showAirTempCK.deselect()
			
		if self.config.get("Plot Options", "show_grid").lower() == "yes":
			self.showGridCK.select()
		else:
			self.showGridCK.deselect()
		
		
		def colorMenus_callback(*args):
			self.eggTempPointColor_PM.config(bg = self.eggTempPointColorVar.get())
			self.eggTempLineColor_PM.config(bg = self.eggTempLineColorVar.get())
			self.boutColor_PM.config(bg = self.boutColorVar.get())
			self.dayMarkerColor_PM.config(bg = self.dayMarkerColorVar.get())
			self.airTempColor_PM.config(bg = self.airTempColorVar.get())
		
		colorMenus_callback()
		
		def plotSettingCKs_callback(*args):
			if self.showDayDelimsBV.get() is True:
				self.dayMarkerColor_PM.grid(row = 19, sticky = "NW", padx = 150)
				self.dayMarkerSize_E.grid(row = 19, sticky = "W", padx = 286)
			else:
				self.dayMarkerColor_PM.grid_forget()
				self.dayMarkerSize_E.grid_forget()
				
				
			if self.showAirTempBV.get() is True:
				self.airTempColor_PM.grid(row = 20, sticky = "NW", padx = 150)
				self.airTempSize_E.grid(row = 20, sticky = "W", padx = 286)
			else:
				self.airTempColor_PM.grid_forget()
				self.airTempSize_E.grid_forget()
		
		# Establish tracing
		self.eggTempPointColorVar.trace("w", colorMenus_callback)
		self.eggTempLineColorVar.trace("w", colorMenus_callback)
		self.boutColorVar.trace("w", colorMenus_callback)
		self.dayMarkerColorVar.trace("w", colorMenus_callback)
		self.airTempColorVar.trace("w", colorMenus_callback)
		
		self.showDayDelimsBV.trace("w", plotSettingCKs_callback)
		self.showAirTempBV.trace("w", plotSettingCKs_callback)
		
		
		#---------------------------------------------------------tab 3-------------------------------------------
			
		#Add select/deselect background
		tab3BG = tk.Label(tab3, text = "", bg = "red4")
		tab3BG.grid(row = 2, sticky = "NSEW")

		#Create buttons for selecting and deselecting column 1
		addCol1B = tk.Button(tab3, text = "Select Column", command = (lambda: self.toggleCol(col1, "select")))
		addCol1B.grid(row = 2, sticky = "W", padx = 10, pady = (10, 10))
		addCol1B.configure(background = "white")
		dropCol1B = tk.Button(tab3, text = "Deselect", command = (lambda: self.toggleCol(col1, "deselect")))
		dropCol1B.grid(row = 2, sticky = "W", padx = 100, pady = (10, 10))
		dropCol1B.configure(background = "white")

		#Create buttons for selecting and deselecting column 2
		addCol2B = tk.Button(tab3, text = "Select Column", command = (lambda: self.toggleCol(col2, "select")))
		addCol2B.grid(row = 2, sticky = "W", padx = 200, pady = (10, 10))
		addCol2B.configure(background = "white")
		dropCol2B = tk.Button(tab3, text = "Deselect", command = (lambda: self.toggleCol(col2, "deselect")))
		dropCol2B.grid(row = 2, sticky = "W", padx = 290, pady = (10, 10))
		dropCol2B.configure(background = "white")	
		
		#Initialize stats option booleans for cluster 1
		self.dayNumVar       = tk.BooleanVar()
		self.dateVar         = tk.BooleanVar()

		#Initialize stats option booleans for cluster 2
		self.offCountVar     = tk.BooleanVar()
		self.offDurVar       = tk.BooleanVar()
		self.offDurSDVar     = tk.BooleanVar()
		self.offDecVar       = tk.BooleanVar()
		self.offDecSDVar     = tk.BooleanVar()
		self.meanOffTempVar  = tk.BooleanVar()
		self.offTimeSumVar   = tk.BooleanVar()

		#Initialize stats option booleans for cluster 3
		self.onCountVar      = tk.BooleanVar()
		self.onDurVar        = tk.BooleanVar()
		self.onDurSDVar      = tk.BooleanVar()
		self.onIncVar        = tk.BooleanVar()
		self.onIncSDVar      = tk.BooleanVar()
		self.meanOnTempVar   = tk.BooleanVar()
		self.onTimeSumVar    = tk.BooleanVar()
		
		#Initialize stats option booleans for cluster 4
		self.boutsDroppedVar = tk.BooleanVar()
		self.superCustVar    = tk.BooleanVar()
		self.subCustVar      = tk.BooleanVar()
		
		#Initialize stats option booleans for cluster 5
		self.meanTempDVar    = tk.BooleanVar()
		self.meanTempDSDVar  = tk.BooleanVar()
		self.medianTempDVar  = tk.BooleanVar()
		self.minTempDVar     = tk.BooleanVar()
		self.maxTempDVar     = tk.BooleanVar()

		#Initialize stats option booleans for cluster 6
		self.meanTempNVar    = tk.BooleanVar()
		self.meanTempNSDVar  = tk.BooleanVar()
		self.medianTempNVar  = tk.BooleanVar()
		self.minTempNVar     = tk.BooleanVar()
		self.maxTempNVar     = tk.BooleanVar()

		#Initialize stats option booleans for cluster 7
		self.meanTempDNVar   = tk.BooleanVar()
		self.meanTempDNSDVar = tk.BooleanVar()
		self.medianTempDNVar = tk.BooleanVar()
		self.minTempDNVar    = tk.BooleanVar()
		self.maxTempDNVar    = tk.BooleanVar()
		
		self.meanAirVar   = tk.BooleanVar()
		self.minAirVar    = tk.BooleanVar()
		self.maxAirVar    = tk.BooleanVar()

		#Initialize checkboxes for options cluster 1
		self.dayNumOp       = tk.Checkbutton(tab3, text = "Day Number", variable = self.dayNumVar)
		self.dateOp         = tk.Checkbutton(tab3, text = "Date", variable = self.dateVar)

		#Initialize checkboxes for options cluster 2
		self.offCountOp     = tk.Checkbutton(tab3, text = "Off-Bout Count", variable = self.offCountVar)
		self.offDurOp       = tk.Checkbutton(tab3, text = "Mean Off-Bout Duration", variable = self.offDurVar)
		self.offDurSDOp     = tk.Checkbutton(tab3, text = "Off-Bout Duration StDev", variable = self.offDurSDVar)
		self.offDecOp       = tk.Checkbutton(tab3, text = "Mean Off-Bout Temp Drop", variable = self.offDecVar)
		self.offDecSDOp     = tk.Checkbutton(tab3, text = "Off-Bout Temp Drop StDev", variable = self.offDecSDVar)
		self.meanOffTempOp  = tk.Checkbutton(tab3, text = "Mean Off-Bout Temp", variable  = self.meanOffTempVar)
		self.offTimeSumOp   = tk.Checkbutton(tab3, text = "Off-Bout Time Sum", variable = self.offTimeSumVar)

		#Initialize checkboxes for options cluster 3
		self.onCountOp      = tk.Checkbutton(tab3, text = "On-Bout Count", variable = self.onCountVar)
		self.onDurOp        = tk.Checkbutton(tab3, text = "Mean On-Bout Duration", variable = self.onDurVar)
		self.onDurSDOp      = tk.Checkbutton(tab3, text = "On-Bout Duration StDev", variable = self.onDurSDVar)
		self.onIncOp        = tk.Checkbutton(tab3, text = "Mean On-Bout Temp Rise", variable = self.onIncVar)
		self.onIncSDOp      = tk.Checkbutton(tab3, text = "On-Bout Temp Rise StDev", variable = self.onIncSDVar)
		self.meanOnTempOp   = tk.Checkbutton(tab3, text = "Mean On-Bout Temp", variable = self.meanOnTempVar)
		self.onTimeSumOp    = tk.Checkbutton(tab3, text = "On-Bout Time Sum", variable = self.onTimeSumVar)
		
		#Initialize checkboxes for options cluster 4
		self.boutsDroppedOp = tk.Checkbutton(tab3, text = "Vertices Dropped", variable = self.boutsDroppedVar)
		self.superCustOp    = tk.Checkbutton(tab3, text = "Time above             degrees", variable = self.superCustVar)
		self.subCustOp      = tk.Checkbutton(tab3, text = "Time under             degrees", variable = self.subCustVar)

		#Initialize checkboxes for options cluster 5
		self.meanTempDOp    = tk.Checkbutton(tab3, text = "Mean Temperature (D)", variable = self.meanTempDVar)
		self.meanTempDSDOp  = tk.Checkbutton(tab3, text = "Mean Temp StDev (D)", variable = self.meanTempDSDVar)
		self.medianTempDOp  = tk.Checkbutton(tab3, text = "Median Temp (D)", variable = self.medianTempDVar)
		self.minTempDOp     = tk.Checkbutton(tab3, text = "Minimum Temp (D)", variable = self.minTempDVar)
		self.maxTempDOp     = tk.Checkbutton(tab3, text = "Maximum Temp (D)", variable = self.maxTempDVar)

		#Initialize checkboxes for options cluster 6
		self.meanTempNOp    = tk.Checkbutton(tab3, text = "Mean Temperature (N)", variable = self.meanTempNVar)
		self.meanTempNSDOp  = tk.Checkbutton(tab3, text = "Mean Temp StDev (N)", variable = self.meanTempNSDVar)
		self.medianTempNOp  = tk.Checkbutton(tab3, text = "Median Temp (N)", variable = self.medianTempNVar)
		self.minTempNOp     = tk.Checkbutton(tab3, text = "Minimum Temp (N)", variable = self.minTempNVar)
		self.maxTempNOp     = tk.Checkbutton(tab3, text = "Maximum Temp (N)", variable = self.maxTempNVar)

		#Initialize checkboxes for options cluster 7
		self.meanTempDNOp   = tk.Checkbutton(tab3, text = "Mean Temperature (DN)", variable = self.meanTempDNVar)
		self.meanTempDNSDOp = tk.Checkbutton(tab3, text = "Mean Temp StDev (DN)", variable = self.meanTempDNSDVar)
		self.medianTempDNOp = tk.Checkbutton(tab3, text = "Median Temp (DN)", variable = self.medianTempDNVar)
		self.minTempDNOp    = tk.Checkbutton(tab3, text = "Minimum Temp (DN)", variable = self.minTempDNVar)
		self.maxTempDNOp    = tk.Checkbutton(tab3, text = "Maximum Temp (DN)", variable = self.maxTempDNVar)
		
		self.meanAirOp    = tk.Checkbutton(tab3, text = "Mean Air Temp (DN)", variable = self.meanAirVar)
		self.minAirOp    = tk.Checkbutton(tab3, text = "Min Air Temp (DN)", variable = self.minAirVar)
		self.maxAirOp    = tk.Checkbutton(tab3, text = "Max Air Temp (DN)", variable = self.maxAirVar)
		
		#Create list of options in each column for mass selection and deselection
		col1 = [self.dayNumOp, self.dateOp, self.offCountOp, self.offDurOp, self.offDurSDOp, self.offDecOp, self.offDecSDOp, self.meanOffTempOp, self.offTimeSumOp, self.onCountOp,
				self.onDurOp, self.onDurSDOp, self.onIncOp, self.onIncSDOp, self.meanOnTempOp, self.onTimeSumOp, self.superCustOp, self.subCustOp, self.boutsDroppedOp]

		col2 = [self.meanTempDOp, self.meanTempDSDOp, self.medianTempDOp, self.minTempDOp, self.maxTempDOp, self.meanTempNOp, self.meanTempNSDOp, self.medianTempNOp, self.minTempNOp,
				self.maxTempNOp, self.meanTempDNOp, self.meanTempDNSDOp, self.medianTempDNOp,  self.minTempDNOp, self.maxTempDNOp, self.meanAirOp, self.minAirOp, self.maxAirOp]

		#Start with all selected
		self.toggleCol(col1, "select")
		self.toggleCol(col2, "select")

		#Deselect options by default if specified in config file
		if self.config.get("Stats Options", "day_Number").lower() == "no": self.dayNumOp.deselect()
		if self.config.get("Stats Options", "date").lower() == "no": self.dateOp.deselect()		
			
		if self.config.get("Stats Options", "off_Bout_Count").lower() == "no": self.offCountOp.deselect()	
		if self.config.get("Stats Options", "mean_Off_Bout_Duration").lower() == "no": self.offDurOp.deselect()
		if self.config.get("Stats Options", "off_Bout_Duration_StDev").lower() == "no": self.offDurSDOp.deselect()
		if self.config.get("Stats Options", "mean_Off_Bout_Temp_Drop").lower() == "no": self.offDecOp.deselect()			
		if self.config.get("Stats Options", "off_Bout_Temp_Drop_StDev").lower() == "no": self.offDecSDOp.deselect()
		if self.config.get("Stats Options", "mean_Off_Bout_Temp").lower() == "no": self.meanOffTempOp.deselect()
		if self.config.get("Stats Options", "on_bout_time_sum").lower() == "no": self.offTimeSumOp.deselect()
			
		if self.config.get("Stats Options", "on_Bout_Count").lower() == "no": self.onCountOp.deselect()					
		if self.config.get("Stats Options", "mean_On_Bout_Duration").lower() == "no": self.onDurOp.deselect()					
		if self.config.get("Stats Options", "on_Bout_Duration_StDev").lower() == "no": self.onDurSDOp.deselect()					
		if self.config.get("Stats Options", "mean_On_Bout_Temp_Rise").lower() == "no": self.onIncOp.deselect()						
		if self.config.get("Stats Options", "on_Bout_Temp_Rise_StDev").lower() == "no": self.onIncSDOp.deselect()				
		if self.config.get("Stats Options", "mean_On_Bout_Temp").lower() == "no": self.meanOnTempOp.deselect()
		if self.config.get("Stats Options", "on_bout_time_sum").lower() == "no": self.onTimeSumOp.deselect()
			
		if self.config.get("Stats Options", "bouts_Dropped").lower() == "no": self.boutsDroppedOp.deselect()
		if self.config.get("Stats Options", "time_Under_30").lower() == "no": self.superCustOp.deselect()		
		if self.config.get("Stats Options", "time_Under_26").lower() == "no": self.subCustOp.deselect()					
			
		if self.config.get("Stats Options", "mean_Daytime_Temperature").lower() == "no": self.meanTempDOp.deselect()		
		if self.config.get("Stats Options", "daytime_Temp_StDev").lower() == "no": self.meanTempDSDOp.deselect()	
		if self.config.get("Stats Options", "median_Daytime_Temp").lower() == "no": self.medianTempDOp.deselect()		
		if self.config.get("Stats Options", "min_Daytime_Temp").lower() == "no": self.minTempDOp.deselect()		
		if self.config.get("Stats Options", "max_Daytime_Temp").lower() == "no": self.maxTempDOp.deselect()		
			
		if self.config.get("Stats Options", "mean_Nighttime_Temp").lower() == "no": self.meanTempNOp.deselect()		
		if self.config.get("Stats Options", "nighttime_Temp_StDev").lower() == "no": self.meanTempNSDOp.deselect()		
		if self.config.get("Stats Options", "median_Nighttime_Temp").lower() == "no": self.medianTempNOp.deselect()	
		if self.config.get("Stats Options", "min_Nighttime_Temp").lower() == "no": self.minTempNOp.deselect()		
		if self.config.get("Stats Options", "max_Nighttime_Temp").lower() == "no": self.maxTempNOp.deselect()			
			
		if self.config.get("Stats Options", "mean_DayNight_Temp").lower() == "no": self.meanTempDNOp.deselect()		
		if self.config.get("Stats Options", "dayNight_Temp_StDev").lower() == "no": self.meanTempDNSDOp.deselect()			
		if self.config.get("Stats Options", "median_DayNight_Temp").lower() == "no": self.medianTempDNOp.deselect()		
		if self.config.get("Stats Options", "min_DayNight_Temp").lower() == "no": self.minTempDNOp.deselect()		
		if self.config.get("Stats Options", "max_DayNight_Temp").lower() == "no": self.maxTempDNOp.deselect()	
		
		if self.config.get("Stats Options", "mean_air_temp").lower() == "no": self.meanAirOp.deselect()	
		if self.config.get("Stats Options", "min_air_temp").lower() == "no": self.minAirOp.deselect()	
		if self.config.get("Stats Options", "max_air_temp").lower() == "no": self.maxAirOp.deselect()	
		
		#Print checkboxes to screen
		self.dayNumOp.grid        (row = 3, sticky = "W", padx = 10, pady = (10, 0))
		self.dateOp.grid          (row = 4, sticky = "W", padx = 10)
		
		self.offCountOp.grid      (row = 7, sticky = "W", padx = 10)
		self.offDurOp.grid        (row = 8, sticky = "W", padx = 10)
		self.offDurSDOp.grid      (row = 9, sticky = "W", padx = 10)
		self.offDecOp.grid        (row = 10, sticky = "W", padx = 10)
		self.offDecSDOp.grid      (row = 11, sticky = "W", padx = 10)
		self.meanOffTempOp.grid   (row = 12, sticky = "W", padx = 10)
		self.offTimeSumOp.grid    (row = 13, sticky = "W", padx = 10)
		
		self.onCountOp.grid       (row = 15, sticky = "W", padx = 10)
		self.onDurOp.grid         (row = 16, sticky = "W", padx = 10)
		self.onDurSDOp.grid       (row = 17, sticky = "W", padx = 10)
		self.onIncOp.grid         (row = 18, sticky = "W", padx = 10)
		self.onIncSDOp.grid       (row = 19, sticky = "W", padx = 10)
		self.meanOnTempOp.grid    (row = 20, sticky = "W", padx = 10)
		self.onTimeSumOp.grid     (row = 21, sticky = "W", padx = 10)
				
		self.boutsDroppedOp.grid  (row = 23, sticky = "W", padx = 10)	
		self.superCustOp.grid     (row = 24, sticky = "W", padx = 10)
		self.subCustOp.grid       (row = 25, sticky = "W", padx = 10)	

		self.meanTempDOp.grid     (row = 3, sticky = "W", padx = 200, pady = (10, 0))
		self.meanTempDSDOp.grid   (row = 4, sticky = "W", padx = 200)
		self.medianTempDOp.grid   (row = 6, sticky = "W", padx = 200)
		self.minTempDOp.grid      (row = 7, sticky = "W", padx = 200)
		self.maxTempDOp.grid      (row = 8, sticky = "W", padx = 200)

		self.meanTempNOp.grid     (row = 10, sticky = "W", padx = 200)
		self.meanTempNSDOp.grid   (row = 11, sticky = "W", padx = 200)
		self.medianTempNOp.grid   (row = 12, sticky = "W", padx = 200)
		self.minTempNOp.grid      (row = 13, sticky = "W", padx = 200)
		self.maxTempNOp.grid      (row = 14, sticky = "W", padx = 200)

		self.meanTempDNOp.grid    (row = 16, sticky = "W", padx = 200)
		self.meanTempDNSDOp.grid  (row = 17, sticky = "W", padx = 200)
		self.medianTempDNOp.grid  (row = 18, sticky = "W", padx = 200)
		self.minTempDNOp.grid     (row = 19, sticky = "W", padx = 200)
		self.maxTempDNOp.grid     (row = 20, sticky = "W", padx = 200)
		
		self.meanAirOp.grid       (row = 22, sticky = "W", padx = 200)
		self.minAirOp.grid 		 (row = 23, sticky = "W", padx = 200)
		self.maxAirOp.grid        (row = 24, sticky = "W", padx = 200)
		
		#Adds entry box in which the user can specify a temperature for which the gross time over will be reported
		self.superCustE = tk.Entry(tab3, width = 5)
		self.superCustE.insert(0, self.config.get("Stats Options", "custom_time_over_temperature"))
		self.superCustE.grid(row = 24, sticky = "W", padx = 97)
		
		#Adds entry box in which the user can specify a temperature for which the gross time under will be reported
		self.subCustE = tk.Entry(tab3, width = 5)
		self.subCustE.insert(0, self.config.get("Stats Options", "custom_time_under_temperature"))
		self.subCustE.grid(row = 25, sticky = "W", padx = 97)
		

		#---------------------------------------------------------Tab 4-------------------------------------------
		#Add header background
		tab3BG = tk.Label(tab4, text = "", bg = "red4")
		tab3BG.grid(row = 2, sticky = "NSEW")
		
		#Create trian algorithm button
		trainAlgoB = tk.Button(tab4, text = "Train Algorithm", command = (lambda: self.trainAlgo()))
		trainAlgoB.grid(row = 2, sticky = "W", padx = 10, pady = (10, 10))
		trainAlgoB.configure(background = "white")
		
		#Create button for saving settings to configuration file
		saveConfigB = tk.Button(tab4, text = "Save Config", command = (lambda: self.saveConfig()))
		saveConfigB.grid(row = 2, sticky = "W", padx = 111, pady = (10, 10))
		saveConfigB.configure(background = "white")
		
		#Create button for saving settings to configuration file
		loadConfigB = tk.Button(tab4, text = "Load Config", command = (lambda: self.loadConfig()))
		loadConfigB.grid(row = 2, sticky = "W", padx = 191, pady = (10, 10))
		loadConfigB.configure(background = "white")
		
		#Create button for restoring original default settings
		setDefaultsB = tk.Button(tab4, text = "Set as Default", command = (lambda: self.setDefaults()))
		setDefaultsB.grid(row = 2, sticky = "W", padx = 273, pady = (10, 10))
		setDefaultsB.configure(background = "white")		
		
		#Input file
		inputAdvLabel = tk.Label(tab4, text = "Input File:", font = STANDARD_FONT)
		inputAdvLabel.grid(row = 5, sticky = "W", padx = 10, pady = (5, 0))
		self.inputFileAdvE = tk.Entry(tab4, width = 18)
		self.inputFileAdvE.grid(row = 5, sticky = "W", padx = 85, pady = (10, 0))
		inputAdvB = tk.Button(tab4, text = "Browse File", command = (lambda: self.getFileName(self.inputFileAdvE)))
		inputAdvB.grid(row = 5, sticky = "W", padx = 201, pady = (10, 0))
		inputAdvB.configure(background = "white")
		
		#Select vertices button
		selectVerticesB = tk.Button(tab4, text = "Select Vertices", command = (lambda: self.selectVertices()))
		selectVerticesB.grid(row = 5, sticky = "W", padx = 275, pady = (10, 0))
		selectVerticesB.configure(background = "white")
		
		
		#Vertex list file
		vertexFileAdvLabel = tk.Label(tab4, text = "Vertex File:", font = STANDARD_FONT)
		vertexFileAdvLabel.grid(row = 6, sticky = "W", padx = 10, pady = (10, 0))
		self.vertexFileAdvE = tk.Entry(tab4, width = 18)
		self.vertexFileAdvE.grid(row = 6, sticky = "W", padx = 85, pady = (10, 0))
		vertexFileAdvB = tk.Button(tab4, text = "Browse File", command = (lambda: self.getFileName(self.vertexFileAdvE)))
		vertexFileAdvB.grid(row = 6, sticky = "W", padx = 201, pady = (10, 0))
		vertexFileAdvB.configure(background = "white")
		
		#Check input file button
		checkAdvB = tk.Button(tab4, text = "Check", command = (lambda: self.checkVertSourceFile(self.vertexFileAdvE.get(), "Advanced", True)))
		checkAdvB.grid(row = 6, sticky = "W", padx = 275, pady = (10, 0))
		checkAdvB.configure(background = "white")
		
		#Add separator
		separator = ttk.Separator(tab4, orient = "horizontal")
		separator.grid(row = 7, sticky = "NSEW", pady = 10)
				
		#Machine learning depth scale bar
		self.MLDepthVar = tk.IntVar()
		MLDepthScale = Scale(tab4, from_ = 1, to = 5, length = 330, orient = "horizontal", font = STANDARD_FONT, label = "Algorithm Training Depth", variable = self.MLDepthVar)
		MLDepthScale.grid(row = 8, sticky = "W", padx = (5, 0))
		depthScaleLeftLabel = tk.Label(tab4, text = "Shallow (fast)", font = STANDARD_FONT)
		depthScaleRightLabel = tk.Label(tab4, text = "Deep (slow)", font = STANDARD_FONT)
		depthScaleLeftLabel.grid(row = 9, sticky = "W", padx = 5)
		depthScaleRightLabel.grid(row = 9, sticky = "W", padx = 280)
		
		#Declare boolean varibales
		self.decoupleDursBV = tk.BooleanVar()
		self.decoupleTempsBV = tk.BooleanVar()
		self.trainSlopeBV = tk.BooleanVar()
		self.decoupleSlopeBV = tk.BooleanVar()
		
		#Initialize checkboxes
		self.decoupleDursCK = tk.Checkbutton(tab4, text = "Decouple duration thresholds", variable = self.decoupleDursBV, font = STANDARD_FONT)
		self.decoupleTempsCK = tk.Checkbutton(tab4, text = "Decouple temperature thresholds", variable = self.decoupleTempsBV, font = STANDARD_FONT)
		self.trainSlopesCK = tk.Checkbutton(tab4, text = "Train slope thresholds", variable = self.trainSlopeBV, font = STANDARD_FONT)
		self.decoupleSlopesCK = tk.Checkbutton(tab4, text = "Decouple slope thresholds", variable = self.decoupleSlopeBV, font = STANDARD_FONT)
		
		#Print checkboxes
		self.decoupleDursCK.grid(row = 12, sticky = "W", padx = 10, pady = (5, 0))
		self.decoupleTempsCK.grid(row = 13, sticky = "W", padx = 10)
		self.trainSlopesCK.grid(row = 14, sticky = "W", padx = 10)
		self.decoupleSlopesCK.grid(row = 15, sticky = "W", padx = 30)
		
		#Initialize checkboxes to selected
		self.decoupleDursCK.select()
		self.decoupleTempsCK.select()
		self.trainSlopesCK.select()
		self.decoupleSlopesCK.select()
		
		#Add separator
		separator = ttk.Separator(tab4, orient = "horizontal")
		separator.grid(row = 16, sticky = "NSEW", pady = (10, 5))
		
		#Running mean radius
		adjMeanRadLabel = tk.Label(tab4, text = "Running Mean Radius:", font = STANDARD_FONT)
		adjMeanRadLabel.grid(row = 17, sticky = "W", padx = 10, pady = (5, 10))
		self.adjMeanRadE = tk.Entry(tab4, width = 7)
		self.adjMeanRadE.insert(0, self.config.get("Advanced Settings", "adjacent_Mean_Radius"))
		self.adjMeanRadE.grid(row = 17, sticky = "W", padx = 160)		
		
		#Vertex search (findVertexI) downstream limit section -- enacted as multiplier of duration threshold
		vertSearchDownLimLabel = tk.Label(tab4, text = "Vertex Search Downstream Limit:", font = STANDARD_FONT)
		vertSearchDownLimLabel.grid(row = 19, sticky = "W", padx = 10)
		self.vertSearchDownLimE = tk.Entry(tab4, width = 7)
		self.vertSearchDownLimE.insert(0, self.config.get("Advanced Settings", "vertex_Search_Downstream_Limit"))
		self.vertSearchDownLimE.grid(row = 19, sticky = "W", padx = 220)	
		
		#On and off bout column labels
		AdvOnLabel = tk.Label(tab4, text = "On-bouts", font = SUBHEADER_FONT)
		AdvOffLabel = tk.Label(tab4, text = "Off-bouts", font = SUBHEADER_FONT)
		AdvOnLabel.grid(row = 20, sticky = "W", padx = 215, pady = (25, 5))
		AdvOffLabel.grid(row = 20, sticky = "NW", padx = 285, pady = (25, 5))
		
		#Time threshold
		timeThreshAdvLabel = tk.Label(tab4, text = "Duration Threshold (data points):", font = STANDARD_FONT)
		timeThreshAdvLabel.grid(row = 22, sticky = "W", padx = 10)
		self.timeThreshAdvOnE = tk.Entry(tab4, width = 7)
		self.timeThreshAdvOffE = tk.Entry(tab4, width = 7)
		self.timeThreshAdvOnE.insert(0, self.config.get("Advanced Settings", "duration_Threshold(On)"))
		self.timeThreshAdvOffE.insert(0, self.config.get("Advanced Settings", "duration_Threshold(Off)"))
		self.timeThreshAdvOnE.grid(row = 22, sticky = "W", padx = 220)
		self.timeThreshAdvOffE.grid(row = 22, sticky = "W", padx = 290)
	
		#Temperature threshold
		tempThreshAdvLabel = tk.Label(tab4, text = "Temperature Threshold:", font = STANDARD_FONT)
		tempThreshAdvLabel.grid(row = 23, sticky = "W", padx = 10, pady = (10, 0))
		self.tempThreshAdvOnE = tk.Entry(tab4, width = 7)
		self.tempThreshAdvOffE = tk.Entry(tab4, width = 7)
		self.tempThreshAdvOnE.insert(0, self.config.get("Advanced Settings", "temperature_Threshold(On)"))
		self.tempThreshAdvOffE.insert(0, self.config.get("Advanced Settings", "temperature_Threshold(Off)"))
		self.tempThreshAdvOnE.grid(row = 23, sticky = "W", padx = 220, pady = (10, 0))
		self.tempThreshAdvOffE.grid(row = 23, sticky = "W", padx = 290, pady = (10, 0))
		
		#Minimum initial slope
		minSlopeLabel = tk.Label(tab4, text = "Minimum Slope (C/data point):", font = STANDARD_FONT)
		minSlopeLabel.grid(row = 24, sticky = "W", padx = 10, pady = (10, 0))
		self.minSlopeOnE = tk.Entry(tab4, width = 7)
		self.minSlopeOffE = tk.Entry(tab4, width = 7)
		self.minSlopeOnE.insert(0, self.config.get("Advanced Settings", "minimum_Initial_Slope(On)"))
		self.minSlopeOffE.insert(0, self.config.get("Advanced Settings", "minimum_Initial_Slope(Off)"))
		self.minSlopeOnE.grid(row = 24, sticky = "W", padx = 220, pady = (10, 0))
		self.minSlopeOffE.grid(row = 24, sticky = "W", padx = 290, pady = (10, 0))
		
		#Minimum initial slope range
		slopeRangeLabel = tk.Label(tab4, text = "Slope Range (data points):", font = STANDARD_FONT)
		slopeRangeLabel.grid(row = 25, sticky = "W", padx = 10, pady = (10, 0))
		self.slopeRangeOnE = tk.Entry(tab4, width = 7)
		self.slopeRangeOffE = tk.Entry(tab4, width = 7)
		self.slopeRangeOnE.insert(0, self.config.get("Advanced Settings", "initial_Slope_Range(On)"))
		self.slopeRangeOffE.insert(0, self.config.get("Advanced Settings", "initial_Slope_Range(Off)"))
		self.slopeRangeOnE.grid(row = 25, sticky = "W", padx = 220, pady = (10, 0))
		self.slopeRangeOffE.grid(row = 25, sticky = "W", padx = 290, pady = (10, 0))
		
		#Vertex migration checkbox
		self.vertMigrationBV = tk.BooleanVar()
		self.vertMigrationCK = tk.Checkbutton(tab4, text = "Vertex Migration", variable = self.vertMigrationBV, font = STANDARD_FONT)
		self.vertMigrationCK.grid(row = 27, sticky = "W", padx = 10, pady = (10, 0))
		
		#Initialize to selected if requested in config file
		if self.config.get("Advanced Settings", "vertex_Migration").lower() != "no":
			self.vertMigrationCK.select()
		else:
			self.vertMigrationCK.deselect()
			
		def advTab_callback(*args):
			if self.trainSlopeBV.get():
				self.decoupleSlopesCK.grid(row = 15, sticky = "W", padx = 20)
			else:
				self.decoupleSlopesCK.grid_forget()
	
		advTab_callback()
		
		
		self.trainSlopeBV.trace("w", advTab_callback)

	
		#------------------------------------------------------------------------------------------------------------
		
		#Print U of A logo
		path1 = "NIQ_Sups/uark.png"
		path2 = "NIQ_Sups/durant.png"
		uarkLogoLoad = PIL.ImageTk.PhotoImage(PIL.Image.open(path1))
		durantLogoLoad = PIL.ImageTk.PhotoImage(PIL.Image.open(path2))
		uarkLogo = tk.Label(root, background = "white", image = uarkLogoLoad)
		uarkLogo.grid(row = 29, sticky = "W", padx = 20)
		durantLogo = tk.Label(root, background = "white", image = durantLogoLoad)
		durantLogo.grid(row = 29, sticky = "W", padx = 80)

		#Create run button
		self.run = False
		self.runB = tk.Button(root, text = "Run", command = (lambda:self.toggleRun(root)))
		self.runB.grid(row = 29, sticky = "E", padx = 10)
		self.runB.configure(bg = "red4", fg = "white", width = 10, height = 1)
		self.runB["font"] = HEADER_FONT
		
	
		self.prevTimeThresh = self.timeThreshE.get()
		self.prevTempThresh = self.tempThreshE.get()
		self.prevTimeThreshAdvOn = self.timeThreshAdvOnE.get()
		self.prevTimeThreshAdvOff = self.timeThreshAdvOffE.get()
		self.prevTempThreshAdvOn = self.tempThreshAdvOnE.get()
		self.prevTempThreshAdvOff = self.tempThreshAdvOffE.get()
		
		
		#Call function to handle user closing GUI window
		root.protocol("WM_DELETE_WINDOW", lambda:self.onClosing(root))
		
		#Bind run button to return key
		temp = None
		root.bind("<Return>", lambda temp = temp:self.toggleRun(root))
		root.bind("<`>", lambda temp = temp:self.testRun(root))
		
		#Get and change to output file directory
		outPath = self.config.get("Main Settings", "output_dir")
		os.chdir(outPath)
		
		#Used to detect program closing
		self.valid = True
		
		#Loop to detect user input
		while self.valid and not self.run:
			self.runLoop(root)
	
	#Loop running while program is open. Detects and responds to input
	def runLoop(self, root):		
		#Detect changes on main tab, update advanced variables to match
		if self.timeThreshE.get() != self.prevTimeThresh:
			if self.timeThreshE.get() != "Adv.":
				self.timeThreshAdvOnE.delete(0, "end")
				self.timeThreshAdvOnE.insert(0, self.timeThreshE.get())
				self.timeThreshAdvOffE.delete(0, "end")
				self.timeThreshAdvOffE.insert(0, self.timeThreshE.get())
				self.prevTimeThresh = self.timeThreshE.get()
				self.prevTimeThreshAdvOn = self.timeThreshE.get()
				self.prevTimeThreshAdvOff = self.timeThreshE.get()
		
		if self.tempThreshE.get() != self.prevTempThresh:
			if self.tempThreshE.get() != "Adv.":
				self.tempThreshAdvOnE.delete(0, "end")
				self.tempThreshAdvOnE.insert(0, self.tempThreshE.get())
				self.tempThreshAdvOffE.delete(0, "end")
				self.tempThreshAdvOffE.insert(0, self.tempThreshE.get())
				self.prevTempThresh = self.tempThreshE.get()
				self.prevTempThreshAdvOn = self.tempThreshE.get()
				self.prevTempThreshAdvOff = self.tempThreshE.get()

		# Detect changes on advanced tab, populate main tab boxes with "Adv."
		if self.timeThreshE.get() != "Adv.":
			if self.timeThreshAdvOnE.get() != self.prevTimeThreshAdvOn or self.timeThreshAdvOffE.get() != self.prevTimeThreshAdvOff:
				self.timeThreshE.delete(0, "end")
				self.timeThreshE.insert(0, "Adv.")
				self.prevTimeThresh = self.timeThreshE.get()
				self.prevTimeThreshAdvOn = self.timeThreshAdvOnE.get()
				self.prevTimeThreshAdvOff = self.timeThreshAdvOffE.get()
		
		if self.tempThreshE.get() != "Adv.":
			if self.tempThreshAdvOnE.get() != self.prevTempThreshAdvOn or self.tempThreshAdvOffE.get() != self.prevTempThreshAdvOff:
				self.tempThreshE.delete(0, "end")
				self.tempThreshE.insert(0, "Adv.")			
				self.prevTempThresh = self.tempThreshE.get()				
				self.prevTempThreshAdvOn = self.tempThreshAdvOnE.get()
				self.prevTempThreshAdvOff = self.tempThreshAdvOffE.get()
			
		#Update GUI and set program clock
		root.update_idletasks()
		root.update()
		time.sleep(0.01)
		
	def saveConfig(self):
		#Get path and name of file to be saved
		saveFile = filedialog.asksaveasfilename()
		
		#Add ".ini" extention if not provided by user
		if not re.search("\.ini", saveFile):
			saveFile = (saveFile + ".ini")
		
		#Copy over configStatic as template
		copyfile(os.path.join(self.coreDir, "misc_files", "configStatic.ini"), saveFile)
		# copyfile("./../misc_files/configStatic.ini", saveFile)
		
		#Update parameters
		self.updateConfig(saveFile)

	def loadConfig(self):
		configFile = filedialog.askopenfilename()
	
		if configFile is "":
			return False
	
		if not os.path.exists(configFile):
			messagebox.showerror(("Config File Loading Error"), 
			"Configuration file could not be found.")
			return False
		
		# try:
		self.config.read(configFile)
		# except:
		# messagebox.showerror(("Config File Loading Error"), 
		# "Configuration file appears invalid.  Please try a differnt file.")
		
		try:
			#Display warning if there is a discrepency in main tab and advance tab parameters
			if self.config.get("Main Settings", "duration_threshold").lower() != "adv.":
				if(
					self.config.get("Main Settings", "duration_threshold") != self.config.get("Advanced Settings", "duration_threshold(on)") or
					self.config.get("Main Settings", "duration_threshold") != self.config.get("Advanced Settings", "duration_threshold(off)")				
				  ):
					messagebox.showwarning("Duration Threshold Conflict", 
					("Config file duration threshold settings from the main and advanced tab are not in agreement.  NestIQ will be using the settings from the advanced tab."))

			if self.config.get("Main Settings", "temperature_threshold").lower() != "adv.":
				if(
					self.config.get("Main Settings", "temperature_threshold") != self.config.get("Advanced Settings", "temperature_threshold(on)") or
					self.config.get("Main Settings", "temperature_threshold") != self.config.get("Advanced Settings", "temperature_threshold(off)")				
				  ):
					messagebox.showwarning("Temperature Threshold Conflict", 
					("Config file temperature threshold settings from the main and advanced tab are not in agreement.  NestIQ will be using the settings from the advanced tab."))
		except Exception:
			messagebox.showerror(("Config File Loading Error"), 
			configFile + " could not be read.")	
			traceback.print_exc()
			return False

		
		try:
			#Clear main tab parameters
			self.intervalE.delete(0, "end")
			self.timeThreshE.delete(0, "end")
			self.tempThreshE.delete(0, "end")
			self.dayStartE.delete(0, "end")
			self.nightStartE.delete(0, "end")
		
			#Refill main tab with config file parameters
			self.dragWarnConfig = self.config.get("Main Settings", "drag_warn")
			self.airWarnConfig = self.config.get("Main Settings", "air_temp_warn")
			self.intervalE.insert(0, self.config.get("Main Settings", "data_Time_Interval"))
			self.timeThreshE.insert(0, self.config.get("Main Settings", "duration_Threshold"))
			self.tempThreshE.insert(0, self.config.get("Main Settings", "temperature_Threshold"))
			self.dayStartE.insert(0, self.config.get("Main Settings", "day_Start_Time"))
			self.nightStartE.insert(0, self.config.get("Main Settings", "night_Start_Time"))
			
			#Initialie restrict bout search checkbox
			if self.config.get("Main Settings", "restrict_bout_search").lower() == "yes":
				self.restrictSearchCK.select()
			else:
				self.restrictSearchCK.deselect()
				
			#Clear plot options tab parameters
			self.plotDimXE.delete(0, "end")
			self.plotDimYE.delete(0, "end")
			self.titleFontSizeE.delete(0, "end")
			self.axisTitleFontSizeE.delete(0, "end")
			self.axisLabelFontSizeE.delete(0, "end")
			self.axisTickSizeE.delete(0, "end")
			self.legendFontSizeE.delete(0, "end")
			self.eggTempPointSize_E.delete(0, "end")
			self.eggTempLineSize_E.delete(0, "end")
			self.boutSize_E.delete(0, "end")
			self.dayMarkerSize_E.delete(0, "end")
			self.airTempSize_E.delete(0, "end")
			
			#Refill plot options tab from config
			if self.config.get("Plot Options", "plot_dim_mode").lower() == "auto":
				self.plotDimVar.set(1)
			else:
				self.plotDimVar.set(2)
		
			self.plotDimXE.insert(0, self.config.get("Plot Options", "plot_x_dim"))
			self.plotDimYE.insert(0, self.config.get("Plot Options", "plot_y_dim"))
			
			self.titleFontSizeE.insert(0, self.config.get("Plot Options", "title_font_size"))
			self.axisTitleFontSizeE.insert(0, self.config.get("Plot Options", "axis_title_font_size"))
			self.axisLabelFontSizeE.insert(0, self.config.get("Plot Options", "axis_label_font_size"))
			self.axisTickSizeE.insert(0, self.config.get("Plot Options", "axis_tick_size"))
			self.legendFontSizeE.insert(0, self.config.get("Plot Options", "legend_font_size"))
		
		
			#Initialize values from config
			self.eggTempPointColorVar.set(self.config.get("Plot Options", "egg_temp_point_color"))
			self.eggTempLineColorVar.set(self.config.get("Plot Options", "egg_temp_line_color"))
			self.boutColorVar.set(self.config.get("Plot Options", "bout_prediction_color"))
			self.dayMarkerColorVar.set(self.config.get("Plot Options", "day_marker_color"))
			self.airTempColorVar.set(self.config.get("Plot Options", "air_temp_color"))
			
			
			self.eggTempPointSize_E.insert(0, self.config.get("Plot Options", "egg_temp_point_size"))
			self.eggTempLineSize_E.insert(0, self.config.get("Plot Options", "egg_temp_line_size"))
			self.boutSize_E.insert(0, self.config.get("Plot Options", "bout_prediction_size"))
			self.dayMarkerSize_E.insert(0, self.config.get("Plot Options", "day_marker_size"))
			self.airTempSize_E.insert(0, self.config.get("Plot Options", "air_temp_size"))
			
			if self.config.get("Plot Options", "show_day_marker").lower() == "yes":
				self.showDayDelimsCK.select()
			else:
				self.showDayDelimsCK.deselect()
				
			if self.config.get("Plot Options", "show_air_temp").lower() == "yes":
				self.showAirTempCK.select()
			else:
				self.showAirTempCK.deselect()
				
			if self.config.get("Plot Options", "show_grid").lower() == "yes":
				self.showGridCK.select()
			else:
				self.showGridCK.deselect()
			
			#Deselect options if specified in config file
			if self.config.get("Stats Options", "day_Number").lower() == "no": self.dayNumOp.deselect()
			if self.config.get("Stats Options", "date").lower() == "no": self.dateOp.deselect()		
				
			if self.config.get("Stats Options", "off_Bout_Count").lower() == "no": self.offCountOp.deselect()	
			if self.config.get("Stats Options", "mean_Off_Bout_Duration").lower() == "no":  self.offDurOp.deselect()
			if self.config.get("Stats Options", "off_Bout_Duration_StDev").lower() == "no": self.offDurSDOp.deselect()
			if self.config.get("Stats Options", "mean_Off_Bout_Temp_Drop").lower() == "no": self.offDecOp.deselect()			
			if self.config.get("Stats Options", "off_Bout_Temp_Drop_StDev").lower() == "no": self.offDecSDOp.deselect()
			if self.config.get("Stats Options", "mean_Off_Bout_Temp").lower() == "no": self.meanOffTempOp.deselect()
			if self.config.get("Stats Options", "off_bout_time_sum").lower() == "no": self.offTimeSumOp.deselect()
					
			if self.config.get("Stats Options", "on_Bout_Count").lower() == "no":	self.onCountOp.deselect()					
			if self.config.get("Stats Options", "mean_On_Bout_Duration").lower() == "no":	self.onDurOp.deselect()					
			if self.config.get("Stats Options", "on_Bout_Duration_StDev").lower() == "no": self.onDurSDOp.deselect()					
			if self.config.get("Stats Options", "mean_On_Bout_Temp_Rise").lower() == "no": self.onIncOp.deselect()						
			if self.config.get("Stats Options", "on_Bout_Temp_Rise_StDev").lower() == "no": self.onIncSDOp.deselect()				
			if self.config.get("Stats Options", "mean_On_Bout_Temp").lower() == "no": self.meanOnTempOp.deselect()
			if self.config.get("Stats Options", "on_bout_time_sum").lower() == "no": self.onTimeSumOp.deselect()
				
			if self.config.get("Stats Options", "time_Under_30").lower() == "no":	self.superCustOp.deselect()		
			if self.config.get("Stats Options", "time_Under_26").lower() == "no":	self.subCustOp.deselect()		
			if self.config.get("Stats Options", "bouts_Dropped").lower() == "no":	self.boutsDroppedOp.deselect()		
				
			if self.config.get("Stats Options", "mean_Daytime_Temperature").lower() == "no": self.meanTempDOp.deselect()		
			if self.config.get("Stats Options", "daytime_Temp_StDev").lower() == "no": self.meanTempDSDOp.deselect()	
			if self.config.get("Stats Options", "median_Daytime_Temp").lower() == "no": self.medianTempDOp.deselect()		
			if self.config.get("Stats Options", "min_Daytime_Temp").lower() == "no": self.minTempDOp.deselect()		
			if self.config.get("Stats Options", "max_Daytime_Temp").lower() == "no": self.maxTempDOp.deselect()		
				
			if self.config.get("Stats Options", "mean_Nighttime_Temp").lower() == "no": self.meanTempNOp.deselect()		
			if self.config.get("Stats Options", "nighttime_Temp_StDev").lower() == "no": self.meanTempNSDOp.deselect()		
			if self.config.get("Stats Options", "median_Nighttime_Temp").lower() == "no": self.medianTempNOp.deselect()	
			if self.config.get("Stats Options", "min_Nighttime_Temp").lower() == "no": self.minTempNOp.deselect()		
			if self.config.get("Stats Options", "max_Nighttime_Temp").lower() == "no": self.maxTempNOp.deselect()			
				
			if self.config.get("Stats Options", "mean_DayNight_Temp").lower() == "no": self.meanTempDNOp.deselect()		
			if self.config.get("Stats Options", "dayNight_Temp_StDev").lower() == "no": self.meanTempDNSDOp.deselect()			
			if self.config.get("Stats Options", "median_DayNight_Temp").lower() == "no": self.medianTempDNOp.deselect()		
			if self.config.get("Stats Options", "min_DayNight_Temp").lower() == "no": self.minTempDNOp.deselect()		
			if self.config.get("Stats Options", "max_DayNight_Temp").lower() == "no": self.maxTempDNOp.deselect()	
			
			if self.config.get("Stats Options", "mean_air_temp").lower() == "no": self.meanAirOp.deselect()	
			if self.config.get("Stats Options", "min_air_temp").lower() == "no": self.minAirOp.deselect()	
			if self.config.get("Stats Options", "max_air_temp").lower() == "no": self.maxAirOp.deselect()	

			#Clear stats options tab parameters
			self.superCustE.delete(0, "end")
			self.subCustE.delete(0, "end")
			
			#Refill stats options tab from config
			self.superCustE.insert(0, self.config.get("Stats Options", "custom_time_over_temperature"))
			self.subCustE.insert(0, self.config.get("Stats Options", "custom_time_under_temperature"))
			
			
			
			#Clear advanced tab parameters
			self.adjMeanRadE.delete(0, "end")
			self.vertSearchDownLimE.delete(0, "end")
			self.timeThreshAdvOnE.delete(0, "end")
			self.timeThreshAdvOffE.delete(0, "end")
			self.tempThreshAdvOnE.delete(0, "end")
			self.tempThreshAdvOffE.delete(0, "end")
			self.minSlopeOnE.delete(0, "end")
			self.minSlopeOffE.delete(0, "end")
			self.slopeRangeOnE.delete(0, "end")
			self.slopeRangeOffE.delete(0, "end")
			
			#Refill advanced tab from config	
			self.adjMeanRadE.insert(0, self.config.get("Advanced Settings", "adjacent_Mean_Radius"))
			self.vertSearchDownLimE.insert(0, self.config.get("Advanced Settings", "vertex_Search_Downstream_Limit"))
			self.timeThreshAdvOnE.insert(0, self.config.get("Advanced Settings", "duration_Threshold(On)"))
			self.timeThreshAdvOffE.insert(0, self.config.get("Advanced Settings", "duration_Threshold(Off)"))
			self.tempThreshAdvOnE.insert(0, self.config.get("Advanced Settings", "temperature_Threshold(On)"))
			self.tempThreshAdvOffE.insert(0, self.config.get("Advanced Settings", "temperature_Threshold(Off)"))
			self.minSlopeOnE.insert(0, self.config.get("Advanced Settings", "minimum_Initial_Slope(On)"))
			self.minSlopeOffE.insert(0, self.config.get("Advanced Settings", "minimum_Initial_Slope(Off)"))
			self.slopeRangeOnE.insert(0, self.config.get("Advanced Settings", "initial_Slope_Range(On)"))
			self.slopeRangeOffE.insert(0, self.config.get("Advanced Settings", "initial_Slope_Range(Off)"))
			outPath = self.config.get("Main Settings", "output_dir")
			os.chdir(outPath)
			
			if self.config.get("Advanced Settings", "vertex_Migration").lower() != "no":
				self.vertMigrationCK.select()
			else:
				self.vertMigrationCK.deselect()
				
				
		#Show error if problem encountered with loading
		except Exception:
			messagebox.showerror(("Config File Loading Error"), 
			configFile + " could not be read.")	
			traceback.print_exc()
	
	#Save current parameters as default (update defaultConfig.ini)
	def setDefaults(self):
		# try:
		self.updateConfig()
		messagebox.showinfo("Default Parameters Saved", 
		"defaultParameters.ini has been updated.")	
		# except:
			# messagebox.showerror(("Default Settings Error"), 
			# "An error was encountered while updating default parameters.  Check if provided parameters are valid.")
	
	#Checks for common problems with HTML vertex source files
	def checkVertSourceFile(self, file, tab, button = False):
		#Stores datapoints extracted from HTML file
		DPList = []
		
		try:
			#Get lines of original file
			with open(file, "r") as htmlFile:
				htmlLines = htmlFile.readlines()
		except FileNotFoundError:
			messagebox.showerror(("Vertex File Error (Advanced tab)"), 
			"Vertex file could not be found with the given path.")	
			return False
		
		#Remove superfluous lines of table data if present
		found = False
		with open("tempFile", "w") as htmlFile:
			for line in htmlLines:
				#Search for table data containing line
				if not line.find("<div class") == -1:
					#The first is retained
					if not found:
						found = True
						htmlFile.write(line)
					#All others are discarded
					else:
						pass
				#Retain all non-table data containing lines
				else:
					htmlFile.write(line)				
		
		#Now proceed with file purged of curropting data lines
		with open("tempFile", "r") as htmlFileClean:
			htmlCont = htmlFileClean.read()
			
		#Delete temporary file
		os.remove("tempFile")
		
		#Obtains raw putative datapoints
		tokens = re.finditer(">([\d\.-]+)</span>", htmlCont)
		
		#Obains maximal allowed datapoint value
		DPLimRE = re.search("(\d+)\],\"y\":\[", htmlCont)
		
		#Maximal value should be integer. If isn't, return error
		try:
			DPLim = int(DPLimRE.group(1))
		except:
			messagebox.showerror(("Invalid vertex list file (" + tab + " tab)"), 
			"Provided vertex list file appears invalid.  Please select a new one.")
			return False
		
		
		type = "DP"
		try:
			for match in tokens:
				#Retain datapoints in list
				if type == "DP":
					dataPoint = round(float(match.group(1)))
					DPList.append(dataPoint)
					type = "temp"
				#Skip temperature values
				else:
					type = "DP"
		except:
			messagebox.showerror(("Vertex Source File Error (" + tab + " tab)"), 
			"Data unreadable, possibly due to dragging vertices.  Be sure to avoid dragging existing vertices while in edit mode.")
			return False

		
		#Check if no datapoints found
		if len(DPList) < 1:
			messagebox.showerror(("Vertex Source File Error (" + tab + " tab)"), 
			"No vertices detected in vertex source file.")
			return False
		
		#Check for common errors of hyphenated and double decimal values
		for i in range(len(DPList)):
			corrupt = re.search("(\d*-\d*)|(\d+\.\d+\.)", str(DPList[i]))
			if corrupt:
				messagebox.showerror(("Vertex Source File Error (" + tab + " tab)"), 
				"Data unreadable, possibly due to dragging vertices.  Be sure to avoid dragging existing vertices while in edit mode.")
				return False
				
		#Check for commen error of datapoint outside of input data range
		for dp in DPList:
			if dp > DPLim:
				messagebox.showerror(("Vertex Source File Error (" + tab + " tab)"), 
				"Data unreadable, possibly due to dragging vertices.  Be sure to avoid dragging existing vertices while in edit mode.")
				return False
		
		#If this check was requested via the check button, provide "Check complete" message
		if button is True:
			messagebox.showinfo("Check complete", 
			"Check of vertex selection file was successful.  File is valid.")
		
		#True will be returned if every check was successful
		return True
		
	#(flag1)  Auto-populate input boxes for easy testing.  Comment or delete prior to release
	def testRun(self, root):
		# self.inputFileE.delete(0, "end")
		# self.inputFileE.insert(0, "C:\\Users\\wxhaw\\Desktop\\github\\whereabout\\inputFiles\\Static\\testInFile.csv")
		self.inputFileE.delete(0, "end")
		self.inputFileE.insert(0, "C:/Users/wxhaw/OneDrive/Desktop/oldNIQ/inputFiles/testRun/quailTest.csv")
		self.inputFileAdvE.delete(0, "end")
		self.inputFileAdvE.insert(0, "C:/Users/wxhaw/OneDrive/Desktop/oldNIQ/inputFiles/testRun/trainIn.csv")
		self.vertexFileAdvE.delete(0, "end")
		self.vertexFileAdvE.insert(0, "C:/Users/wxhaw/OneDrive/Desktop/oldNIQ/inputFiles/testRun/trainVerts.html")

		
		
	#Launch user manual pdf if help button clicked			
	def help(self):
		subprocess.Popen(os.path.join(self.coreDir, "NIQ_Manual.pdf"), shell = True)
		
	#Select or deselect entire column of stats options	
	def toggleCol(self, column, command):
		for option in column:
			if command == "select":
				option.select()
			elif command == "deselect":
				option.deselect()
	
	#Automatically sets up file names if multiple input files are selected
	def multiInSetup(self, inFile):
		#Update input file entry box
		self.inputFileE.delete(0, "end")
		self.inputFileE.insert(0, inFile)
		
		#Get input file root name
		tempRE = re.search((".*\."), os.path.basename(os.path.normpath(inFile)))
		if tempRE:
			self.inputRoot = tempRE.group(0)[:-1]
		else:
			self.inputRoot = os.path.basename(os.path.normpath(inFile))
				
		#Update default name for graph file
		self.graphE.delete(0, "end")
		self.graphE.insert(0, (self.inputRoot + "Graph.html"))
		
		#Continue to add "(x)" until a non-existent file name is found
		i = 1
		while os.path.exists(self.graphE.get()):
			self.graphE.delete(0, "end")
			self.graphE.insert(0, (self.inputRoot + "Graph(" + str(i) + ").html"))
			i += 1
		
		#Update default name for stats file			
		self.outE.delete(0, "end")
		self.outE.insert(0, (self.inputRoot + "Stats.csv"))
	
		#Continue to add "(x)" until a non-existent file name is found
		i = 1
		while os.path.exists(self.outE.get()):
			self.outE.delete(0, "end")
			self.outE.insert(0, (self.inputRoot + "Stats(" + str(i) + ").csv"))
			i += 1
		
	#Set varibales based on user inputs and settings
	def setVars(self):
		#Set input file
		self.inFile = self.inputFileE.get()
		
		#Set vertex selection file
		self.vertFile = self.vertexFileE.get()
		
		#Establish column identities
		# self.dataPointCol = (int(self.indicesColE.get()) - 1)
		# self.dateTimesCol = (int(self.dateTimesColE.get()) - 1)
		# self.tempsCol = (int(self.tempsColE.get()) - 1)
		
		#Set graph file name (add .html extension if needed)
		if re.search("(.html$)", self.graphE.get()):
			self.graphName = self.graphE.get()
		else:
			self.graphName = (self.graphE.get() + ".html")
		
		#Set statistics file name (add .csv extension if needed)
		if re.search("(.csv$)", self.outE.get()):
			self.outName = self.outE.get()
		else:
			self.outName = (self.outE.get() + ".csv")
			
		#Set compile stats file name (add .csv extension if needed)
		if re.search("(.csv$)", self.compileE.get()) or os.path.exists(self.compileE.get()):
			self.compileName = self.compileE.get()
		else:
			self.compileName = (self.compileE.get() + ".csv")
		
		#Set stats option booleans
		self.makeGraphBool = self.makeGraphBV.get()
		self.makeOutputBool = self.makeOutputBV.get()
		self.compileStatsBool = self.complileStatsBV.get()
		
		#Set data interval
		self.interval = float(self.intervalE.get())
		
		#Store bout restriction selection and save start times
		self.dayStart = str(self.dayStartE.get())
		self.nightStart = str(self.nightStartE.get())
	
	#Update default output file names			
	def updateDefaultOuts(self):
		#Regular expression used to search for "graph(x).html" default file name
		graphRE = ("graph(\((\d)\))?\.html")
		#Regular expression used to search for "stats(x).csv" default file name
		outRE = ("stats(\((\d)\))?\.csv")
		
		if self.inputRoot:
			#Regular expression used to search for "(inputRoot)Graph(x).html" default file name
			graphInputRE = (self.inputRoot + "Graph(\((\d)\))?\.html")
			#Regular expression used to search for "(inputRoot)Stats(x).csv" default file name
			outInputRE = (self.inputRoot + "Stats(\((\d)\))?\.csv")
	
		#If a file with the current output file name already exists, add "(x)", incrimenting x until a novel file name is found
		if os.path.exists(self.graphE.get()):
			if re.search(graphRE, self.graphE.get()):
				i = 1
				while os.path.exists(self.graphE.get()):
					self.graphE.delete(0, "end")
					self.graphE.insert(0, ("graph(" + str(i) + ").html"))
					i += 1
			elif self.inputRoot:		
				if re.search(graphInputRE, self.graphE.get()):
					i = 1
					while os.path.exists(self.graphE.get()):
						self.graphE.delete(0, "end")
						self.graphE.insert(0, (self.inputRoot + "Graph(" + str(i) + ").html"))
						i += 1
		
		#If a file with the current output file name already exists, add "(x)", incrimenting x until a novel file name is found
		if os.path.exists(self.outE.get()):
			if re.search(outRE, self.outE.get()):
				i = 1
				while os.path.exists(self.outE.get()):
					self.outE.delete(0, "end")
					self.outE.insert(0, ("stats(" + str(i) + ").csv"))
					i += 1
					
			elif self.inputRoot:		
				if re.search(outInputRE, self.outE.get()):
					i = 1
					while os.path.exists(self.outE.get()):
						self.outE.delete(0, "end")
						self.outE.insert(0, (self.inputRoot + "Stats(" + str(i) + ").csv"))
						i += 1
						
	#Checks if output file name provided is valid
	def checkOutFile(self, entry, title):
		#Check if empty
		if entry.get().strip() == "":
			messagebox.showerror((title + " error"), "File name is empty.") 
			return False
		
		#Check if directory but no file name provided
		if entry.get()[-1] == "/" or entry.get()[-1] == "\\":
			messagebox.showerror((title + " error"), "Directory provided but no file name.")
			return False
					
		#Check if graph file already exists and if so, ask to continue (appends new graph below old)
		if entry == self.graphE:
			if os.path.exists(entry.get()) or os.path.exists(entry.get() + ".html"):
				if messagebox.askyesno("Override?", ("The file \"" + entry.get() + "\" already exists.  Do you want to continue?")):
					try:
						os.remove(entry.get())
					except:
						os.remove(entry.get() + ".html")
				else:	
					return False
					
		#Check if output or compile statistics file already exists and if so, ask to override
		if entry == self.outE or entry == self.compileE:
			if os.path.exists(entry.get()) or os.path.exists(entry.get() + ".csv"):
				if messagebox.askyesno("Override?", ("The file \"" + entry.get() + "\" already exists.  Do you want to override?")):
					try:
						os.remove(entry.get())
					except:
						try:
							os.remove(entry.get() + ".csv")
						except:
							messagebox.showerror(("Override error"), ("Could not override file.  Please close \"" + entry.get() + "\" if open."))
							return False
				else:	
					return False
		
		if not os.path.exists(entry.get()):
			#Check if provided name is valid
			try:
				with open(entry.get(), "a+") as testFile:
					pass
			except:
				messagebox.showerror((title + " Error"), "Invalid directory/file name.")
				return False
				
			os.remove(entry.get())
		
		#Return true if provided name is valid
		return True
	
	#Check if times provided for day start and night start are valid
	def checkTime(self, time, DN):
		#Regular expression used to check for proper time format
		timeRE = re.search("(\d+)(:)(\d+)", time)
		
		#If time found, store hour and minute values
		if timeRE:
			hour = int(timeRE.group(1))
			minute = int(timeRE.group(3))
		#Else return error
		else:
			messagebox.showerror("Start time error", ("Invalid " + DN + " start time."))
			return False
		
		#Detects non-numerical characters (possibly due to use of 12hr, am/pm format)
		if re.search("([^0-9:])", time):
			messagebox.showerror("Start time error", (DN + " start time must be entered in 24hr format."))
			return False
		#Checks for proper hour value
		elif hour < 0 or hour > 23:
			messagebox.showerror("Start time error", ("Invalid " + DN + " start time."))
			return False
		#Checks for proper minute value
		elif minute < 0 or minute > 59:
			messagebox.showerror("Start time error", ("Invalid " + DN + " start time."))
			return False
	
		#Return true time is valid
		return True
		
	#Check if everything in main tab is in order before executing the body of the script	
	def checkValidMain(self, firstIn = True, training = False):
		#If this check is not part of algorithm training
		if not training:
			#Check for empty input file box
			if self.inputFileE.get() == "":
				messagebox.showerror("Input error (Main tab)", "No input file provided.")
				return False
		
			#Check for valid input file
			inputFile = self.inputFileE.get()
			if not os.path.exists(inputFile):	
				#Check for curly brace addition (done for paths with spaces)
				if inputFile[0] is "{":
					#Check if true path exists
					if os.path.exists(inputFile[1:(len(inputFile) - 1)]):
						#Remove curly braces
						self.inputFileE.delete(0, "end")
						self.inputFileE.insert(0, (inputFile[1:(len(inputFile) - 1)]))
						inputFile = self.inputFileE.get()
					else:
						#Check for special error caused by "Use provided vertices" with mulitple input files
						if self.useProvidedBV.get() is True:
							messagebox.showerror("Input File Error (Main tab)", "Input file not found.  If processing multiple files, ensure \"Use provided vertices\" is not selected.")
						else:
							messagebox.showerror("Input File Error (Main tab)", "Provided input file not found.")
						return False	
				else:
					#Check for special error caused by "Use provided vertices" with mulitple input files
					if self.useProvidedBV.get() is True:
						messagebox.showerror("Input File Error (Main tab)", "Input file not found.  If processing multiple files, ensure \"Use provided vertices\" is not selected.")
					else:
						messagebox.showerror("Input File Error (Main tab)", "Provided input file not found.")
					return False
				
			#Check for correct file format (CSV)
			if self.inputFileE.get()[-4:] != ".csv":
				messagebox.showerror("Input error (Main tab)", "Input file must end in \".csv\" (comma separated value file format).")
				return False
				
			#Check vertex selection file
			vertexFile = self.vertexFileE.get()
			if self.useProvidedBV.get() and vertexFile != "":
				if not os.path.exists(vertexFile):
					#Check for curly brace addition (done for paths with spaces)
					if vertexFile[0] is "{":
						#Check if true path exists
						if os.path.exists(vertexFile[1:(len(vertexFile) - 1)]):
							#Remove curly braces
							self.vertexFileE.delete(0, "end")
							self.vertexFileE.insert(0, (vertexFile[1:(len(vertexFile) - 1)]))
							vertexFile = self.vertexFileE.get()
						else:
							messagebox.showerror("Vertex Selection Error (Main tab)", "Provided vertex selection file not found.")
							return False
					else:
						messagebox.showerror("Vertex Selection Error (Main tab)", "Provided vertex selection file not found.")
						return False
				if vertexFile[-5:] != ".html":
					messagebox.showerror("Vertex Selection Error (Main tab)", "Vertex selection file must end in \".html\".")
					return False
				if not self.checkVertSourceFile(vertexFile, "Main"):
					return False
				
				self.verticesProvided = True
			else:
				self.verticesProvided = False
				
			#Check for valid column numbers
			# try:
				# float(self.indicesColE.get())
				# float(self.dateTimesColE.get())
				# float(self.tempsColE.get())
			# except:
				# messagebox.showerror("Column number error", "Invalid column number.")
				# return False
			
			#Checks for valid output file names
			if self.makeGraphBV.get():
				if not self.checkOutFile(self.graphE, "Graph file"):
					return False

			if self.makeOutputBV.get():
				if not self.checkOutFile(self.outE, "Stats Options file"):
					return False
					
			if self.complileStatsBV.get():
				#Only check once if multiple input files provided
				if firstIn:
					if not self.checkOutFile(self.compileE, "Compile summary"):
						return False
					
		#Time interval error check
		try:
			if float(self.intervalE.get()) < 0:
				messagebox.showerror("Data interval error (Main tab)", "Interval must be greater than 0.")
				return False
		except:
			messagebox.showerror("Data interval error (Main tab)", "Invalid interval.")
			return False
			

		#Error check day and night start times (checkTime function triggers appropriate error message)
		if not self.checkTime(self.dayStartE.get(), "day") or not self.checkTime(self.nightStartE.get(), "night"):
			return False
						
		return True
	
	#Check if all plot options settings are valid
	def checkValidPlotOps(self):
		#Check if user plot dimensions are valid
		if self.plotDimVar.get() is 2:
			valid = True
			#Make sure values are positive integers
			try:
				if int(self.plotDimXE.get()) < 1 or int(self.plotDimYE.get()) < 1:
					valid = False
			except:
				valid = False
		
			#Set plot dimensions to auto if manual values invalid
			if valid is False:
				messagebox.showwarning("Plot Dimensions Warning", 
									("Provided plot dimensions are not valid; please provide positive integers. Automatic resolution detection will be used."))
				self.plotDimVar.set(1)
		
		#Check graph backbone settings (top half of tab)
		try:
			if float(self.titleFontSizeE.get()) < 0:
				raise ValueError("Provided plot title font size is less than 0")
		except ValueError:
			messagebox.showerror("Plot title Font Size Error (Plot Options tab)", "Invalid plot title font size was provided.")
			return False
			
		try:
			if float(self.axisTitleFontSizeE.get()) < 0:
				raise ValueError("Provided axis title font size is less than 0")
		except ValueError:
			messagebox.showerror("Axis Title Font Size Error (Plot Options tab)", "Invalid axis title font size was provided.")
			return False
			
		try:
			if float(self.axisLabelFontSizeE.get()) < 0:
				raise ValueError("Provided axis label font size is less than 0")
		except ValueError:
			messagebox.showerror("Axis Label Font Size Error (Plot Options tab)", "Invalid axis label font size was provided.")
			return False
			
		try:
			if int(self.axisTickSizeE.get()) < 0:
				raise ValueError("Provided axis tick size is less than 0")
		except ValueError:
			messagebox.showerror("Axis Tick Size Error (Plot Options tab)", "Invalid axis tick size was provided.")
			return False

		try:
			if float(self.legendFontSizeE.get()) < 0:
				raise ValueError("Provided legend font size is less than 0")
		except ValueError:
			messagebox.showerror("Legend Font Size Error (Plot Options tab)", "Invalid legend font size was provided.")
			return False

		
		#Check plot element sizes/widths
		try:
			if float(self.eggTempPointSize_E.get()) < 0:
				raise ValueError("Provided egg temperature point size is less than 0")
		except ValueError:
			messagebox.showerror("Egg Temperature Point Size Error (Plot Options tab)", "Invalid egg temperature point size was provided.")
			return False
			
		try:
			if float(self.eggTempLineSize_E.get()) < 0:
				raise ValueError("Provided egg temperature line size is less than 0")
		except ValueError:
			messagebox.showerror("Egg Temperature Line Size Error (Plot Options tab)", "Invalid egg temperature line size was provided.")
			return False

		try:
			if float(self.boutSize_E.get()) < 0:
				raise ValueError("Provided bout prediction size is less than 0")
		except ValueError:
			messagebox.showerror("Bout Prediction Size Error (Plot Options tab)", "Invalid bout prediction size was provided.")
			return False

			
		if self.showDayDelimsBV.get():
			try:
				if float(self.dayMarkerSize_E.get()) < 0:
					raise ValueError("Provided day marker size is less than 0")
			except ValueError:
				messagebox.showerror("Day Marker Size Error (Plot Options tab)", "Invalid day marker size was provided.")
				return False

		if self.showAirTempBV.get():
			try:
				if float(self.airTempSize_E.get()) < 0:
					raise ValueError("Provided air temperature size is less than 0")
			except ValueError:
				messagebox.showerror("Air Temperature Size Error (Plot Options tab)", "Invalid air temperature size was provided.")
				return False
				
		return True
		

	#Check if all stats options settings are valid
	def checkValidStatsOps(self):
		#Check for valid "Time above" temperature
		try:
			float(self.superCustE.get())
		except:
			messagebox.showerror("Custom temperature error (Main tab)", "Invalid \"Time above\" temperature.")
			return False
		
		#Check for valid "Time below" temperature
		try:
			float(self.subCustE.get())
		except:
			messagebox.showerror("Custom temperature error (Main tab)", "Invalid \"Time below\" temperature.")
			return False
			
		return True
	
	#Check if all advanced settings are valid
	def checkValidAdv(self, _checkInput = False, _checkVerts = True):	
		checkInput = _checkInput
		checkVerts = _checkVerts
	
	
		#Check input file if preparing for training
		inputFile = self.inputFileAdvE.get()
		if checkInput is True:
			#Check for empty input file box
			if inputFile == "":
				messagebox.showerror("Input File Error (Advanced tab)", "No input file provided.")
				return False
		
			#Check for valid input file
			if not os.path.exists(inputFile):
				#Check for curly brace addition (done for paths with spaces)
				if inputFile[0] is "{":
					#Check if true path exists
					if os.path.exists(inputFile[1:(len(inputFile) - 1)]):
						#Remove curly braces
						self.inputFileAdvE.delete(0, "end")
						self.inputFileAdvE.insert(0, (inputFile[1:(len(inputFile) - 1)]))
						inputFile = self.inputFileAdvE.get()
					else:
						messagebox.showerror("Input File Error (Advanced tab)", "Provided input file not found.")
						return False		
				else:
					messagebox.showerror("Input File Error (Advanced tab)", "Provided input file not found.")
					return False
				
			#Check for corrct file format (CSV)
			if inputFile[-4:] != ".csv":
				messagebox.showerror("Input File Error (Advanced tab)", "Input file must end in \".csv\" (comma separated value file format).")
				return False
				
			#Check vertex selection file
			vertexFile = self.vertexFileAdvE.get()
			if checkVerts is True:
				if vertexFile != "":
					if not os.path.exists(vertexFile):
						#Check for curly brace addition (done for paths with spaces)
						if vertexFile[0] is "{":
							#Check if true path exists
							if os.path.exists(vertexFile[1:(len(vertexFile) - 1)]):
								#Remove curly braces
								self.vertexFileAdvE.delete(0, "end")
								self.vertexFileAdvE.insert(0, (vertexFile[1:(len(vertexFile) - 1)]))
								vertexFile = self.vertexFileAdvE.get()
							else:
								messagebox.showerror("Vertex Selection Error (Advanced tab)", "Provided vertex selection file not found.")
								return False
						else:
							messagebox.showerror("Vertex Selection Error (Advanced tab)", "Provided vertex selection file not found.")
							return False
					if vertexFile[-5:] != ".html":
						messagebox.showerror("Vertex Selection Error (Advanced tab)", "Vertex selection file must end in \".html\".")
						return False
					if not self.checkVertSourceFile(vertexFile, "Advanced"):
						return False
			
		#Check Running mean radius
		if not float(self.adjMeanRadE.get()).is_integer():
			messagebox.showerror("Running Mean Radius Error (Advanced tab)", "Running mean radius must be an ineger.")
			return False
			
		if not int(self.adjMeanRadE.get()) >= 0:
			messagebox.showerror("Running Mean Radius Error (Advanced tab)", "Running mean radius must be greater than or equal to zero.")
			return False
		
		#Check time threshold
		for timeThresh in (float(self.timeThreshAdvOnE.get()), float(self.timeThreshAdvOffE.get())):
			try:
				if timeThresh < 3:
					messagebox.showerror("Time Threshold Error (Advanced tab)", "Duration threshold cannot be less than three data points.")
					return False
			except ValueError:
				messagebox.showerror("Time Threshold Error (Advanced tab)", "Invalid time threshold (could not convert to number).")
				return False
			
		#Check temp threshold
		for tempThresh in (self.tempThreshAdvOnE, self.tempThreshAdvOffE):
			try:
				#Populate with zero if empty
				if tempThresh.get() == "":
					tempThresh.insert(0, float(0))
				else:
					if float(tempThresh.get()) < 0:
						messagebox.showerror("Temperature threshold error (Advanced tab)", "Temperature threshold cannot be less than 0.")
						return False
			except ValueError:
				messagebox.showerror("Temperature threshold error (Advanced tab)", "Invalid temperature threshold (could not convert to number).")
				return False
				
		#Populate min slopes with zero if empty
		for minSlope in (self.minSlopeOnE, self.minSlopeOffE):
			if minSlope.get() == "":
				minSlope.insert(0, float(0))
			
		#Check if min slopes are valid
		try:
			if float(self.minSlopeOnE.get()) < 0:
				messagebox.showerror("Minimum slope error (Advanced tab)", "Minimum on-bout slope cannot be less than 0.")
				return False
			if float(self.minSlopeOffE.get()) > 0:
				messagebox.showerror("Minimum slope error (Advanced tab)", "Minimum off-bout slope cannot be greater than 0.")
				return False
		except ValueError:
			messagebox.showerror("Minimum slope error (Advanced tab)", "Invalid minimum slope (could not convert to number).")
			return False
			

		#Check slope ranges
		try:
			if float(self.slopeRangeOnE.get()) < 2:
				messagebox.showerror("Slope range error (Advanced tab)", "Slope range cannot be less than 2.")
				return False
			if float(self.slopeRangeOffE.get()) < 2:
				messagebox.showerror("Slope range error (Advanced tab)", "Slope range cannot be less than 2.")
				return False
		except ValueError:
			messagebox.showerror("Slope range error (Advanced tab)", "Invalid slope range (could not convert to number).")
			return False
			
		#(flag)Check vertex search downstream limit (done at end because dur thesh must be checked first)
		if not float(self.vertSearchDownLimE.get()).is_integer():
			messagebox.showerror("Vertex search downstream limit error (Advanced tab)", "Downstream limit must be integer.")
			return False
	
		minLimit = (min(round(float((self.timeThreshAdvOnE.get()))), (round(float((self.timeThreshAdvOffE.get()))) * (-1))))
		if not float(self.vertSearchDownLimE.get()) > minLimit:
			messagebox.showerror("Vertex search downstream limit error (Advanced tab)", "Downstream limit too low.")
			return False
	
		#Return true if all settings on main tab are valid
		return True
	

	
	#Check if provided input file is valid and show descriptive message if it is not
	def checkInFile(self, entry, root):
		#Make sure only one file provied for check
		if len(self.inPathName) > 1:
			messagebox.showerror("Multiple Input Files Error", ("Multiple input files provided.  Please check one file at a time."))
		else:
			try:
				#Make sure main and advanced tab settings are valid
				if self.checkValidMain() and self.checkValidAdv():
					checkList = []
					popCount   = 0
					popIndices = []
					
					#Set variables based on user provided settings
					self.setVars()
					
					#Open input file
					with open(self.inFile, "r") as csv:
						lines = csv.readlines()
					
					#Split individual cells of input file data
					for line in lines:
						checkList.append(line.split(","))
						
					#Detect where data starts (bypasses header line if present)
					if re.match("\d", lines[0]):
						lineStart = 1
					else:
						lineStart = 2
						
					#Record indices of lines not conforming to expected format (This deletes headers)
					for i in range(0, (len(checkList) - 1)):	
						if not re.search("\d", checkList[i][self.dataPointCol]):
							popIndices.append(i)
			
					#Delete extra line created as a result of the above for loop		
					del checkList[-1]
					
					#Remove lines not conforming to format
					for index in popIndices:
						checkList.pop(index - popCount)
						popCount += 1
					
					#Clear formatting characters sometimes present on first position
					search = re.search("\d+", checkList[0][self.dataPointCol])
					checkList[0][self.dataPointCol] = search.group(0)
							
					self.airValid = True
					localAirValid = True
					lineNum = lineStart			
					prevIndex = checkList[0][self.dataPointCol]
					for line in checkList:				
						#Check for correct number of columns and if columns are all populated
						if len(line) < 3 or line[self.dataPointCol] == "" or line[self.dateTimesCol] == "" or line[self.tempsCol] == "":
							messagebox.showwarning("Column Warning", 
							("Column missing on line " + str(lineNum) + "."))
							return False
						
						#Check if indecies are continuous and sequential
						if not lineNum == lineStart:
							if not int(line[self.dataPointCol]) == (int(prevIndex) + 1):
								messagebox.showerror("Data Point Error", 
								("Error on line " + str(lineNum) + ". Data point number is not sequential with regrad to previous index."))
								return False
								
						#Check dates and times	
						time = re.search("(\d+:\d+)", line[self.dateTimesCol])
						date = re.search("\d+\/\d+\/\d+", line[self.dateTimesCol])
						
						#Trigger error if no valid time found
						if not time:
							messagebox.showerror("Time Format Error", 
							("Error on line " + str(lineNum) + ". No time found.  Time should be in HH:MM format."))
							return False
						
						#Trigger error if no valid date found
						if not date:
							messagebox.showerror("Date Format Error", 
							("Error on line " + str(lineNum) + ". No date found.  Date should be in MM/DD/YYYY format."))
							return False
							
						#Display warning for missing egg temperature
						if not re.search("(\d)+(\.)?((\d)?)+", line[self.tempsCol]):
							messagebox.showwarning("Egg Temperature Warning", 
							("Warning on line " + str(lineNum) + ".  No egg temperature detected.  If left, the program will populate this cell with the temperature above it."))
						else:
							#Check if value is a float
							try:
								float(line[self.tempsCol])
							except:
								messagebox.showerror("Temperature Error",
								("Error on line " + str(lineNum) + ". Invalid temperature."))
								return False
						
						#Check air temperature column
						if localAirValid is True:
							#Display warning for missing air temperature
							if not re.search("(\d)+(\.)?((\d)?)+", line[self.airTempCol]):
								dataPoint = line[self.dataPointCol]
								messagebox.showwarning("Air Temperature Warning", ("No air temperature detected for data point " + dataPoint + ". Air temperatures will not be plotted or included in statistical output."))
								localAirValid = False
							else:
								#Check if value is a float
								try:
									float(line[self.airTempCol])
								except:
									dataPoint = line[self.dataPointCol]
									messagebox.showwarning("Air Temperature Warning", ("Invalid air temperature detected for data point " + dataPoint + ". Air temperatures will not be plotted or included in statistical output."))
									localAirValid = False
									
									
									
						prevIndex = line[self.dataPointCol]
						lineNum += 1
						
					#Announces successful file check	
					messagebox.showinfo("Check complete", 
					"Check of input file was successful.  File is correctly formatted.")
			#Announces unknown error if problem with input file could not be identified
			except:
				messagebox.showerror("Unknown Error",
				("The error regarding this input file could not be identified.\n\nPlease reference the NestIQ manual for details regarding proper input file format.  This can be accessed by clicking \"Help\" in the top right."))
				
				
	def checkAirValid(self, inFile = None):
		checkList = []
		popIndices = []
		popCount   = 0
		self.airValid = True
		
		#Set variables based on user provided settings
		self.setVars()
		
		if inFile is None:
			inFile = self.inFile
		
		#Open input file
		with open(inFile, "r") as csv:
			lines = csv.readlines()
		
		#Split individual cells of input file data
		for line in lines:
			checkList.append(line.split(","))
						
		#Record indices of lines not conforming to expected format (This deletes headers)
		for i in range(0, (len(checkList) - 1)):	
			if not re.search("\d", checkList[i][self.dataPointCol]):
				popIndices.append(i)

		#Delete extra line created as a result of the above for loop		
		del checkList[-1]
		
		#Remove lines not conforming to format
		for index in popIndices:
			checkList.pop(index - popCount)
			popCount += 1
		
		#Clear formatting characters sometimes present on first position
		search = re.search("\d+", checkList[0][self.dataPointCol])
		checkList[0][self.dataPointCol] = search.group(0)
						
		for line in checkList:			
			#Air temperature check
			if self.airValid is True:
				try:
					#Display warning for missing air temperature
					if not re.search("(\d)+(\.)?((\d)?)+", line[self.airTempCol]):
						dataPoint = line[self.dataPointCol]
						coreF.airTempWarn(self, dataPoint, "missing")
						self.airValid = False
					else:
						#Check if value is a float
						try:
							float(line[self.airTempCol])
						except:
							dataPoint = line[self.dataPointCol]
							coreF.airTempWarn(self, dataPoint, "invalid")
							self.airValid = False
				except IndexError:
					dataPoint = line[self.dataPointCol]
					coreF.airTempWarn(self, dataPoint, "missing")
					self.airValid = False
	
	
	#Set acquire names of provided input file(s)
	def getInFileName(self, entry):
		#Clear input file entry box
		entry.delete(0, "end")
		
		#Launch window allowing user to select input file(s)
		root.update()
		self.inPathName = filedialog.askopenfilename(multiple = True)
		root.update()
		
		#If the entry box isn't empty (the result of the user canceling out of the browse window)
		if self.inPathName != "":
			#If just one file selected:
			if len(self.inPathName) == 1:
				entry.insert(0, self.inPathName[0])
				
				#Update outfile names
				#Record input file root name for use in setting default output file names
				tempRE = re.search((".*\."), os.path.basename(os.path.normpath(self.inPathName[0])))
				if tempRE:
					self.inputRoot = tempRE.group(0)[:-1]
				else:
					self.inputRoot = os.path.basename(os.path.normpath(self.inPathName[0]))
						
				#Updating default name for graph file
				self.graphE.delete(0, "end")
				self.graphE.insert(0, (self.inputRoot + "Graph.html"))
					
				#Continue to add "(x)" until a non-existent file name is found
				i = 1
				while os.path.exists(self.graphE.get()):
					self.graphE.delete(0, "end")
					self.graphE.insert(0, (self.inputRoot + "Graph(" + str(i) + ").html"))
					i += 1
				
				#Updating default name for output stats file
				self.outE.delete(0, "end")
				self.outE.insert(0, (self.inputRoot + "Stats.csv"))
			
				#Continue to add "(x)" until a non-existent file name is found
				i = 1
				while os.path.exists(self.outE.get()):
					self.outE.delete(0, "end")
					self.outE.insert(0, (self.inputRoot + "Stats(" + str(i) + ").csv"))
					i += 1
			#Else if multiple input files were selected:
			else:
				entry.insert(0, self.inPathName)
				#Update out names if incubation data file is being changed 
				self.graphE.delete(0, "end")
				self.graphE.insert(0, "------------------")
				self.outE.delete(0, "end")
				self.outE.insert(0, "------------------")
	
	#Appropriately set file based on user actions in browse file window
	def getFileName(self, entry):	
		#Clear input file entry box
		entry.delete(0, "end")
		
		#Launch window allowing user to select input file(s)
		root.update()
		storageVar = filedialog.askopenfilename(multiple = True)
		root.update()
		
		#If the entry box isn't empty (the result of the user canceling out of the browse window)
		if storageVar != "":
			entry.insert(0, storageVar)
				
				
	#Appropriately set output directory based on user actions in browse directory window
	def getDirName(self, entry):
		entry.delete(0, "end")
		pathName = ""
		root.update()
		pathName = filedialog.askdirectory()
		root.update()
		entry.insert(0, pathName)
		if pathName != "":
			entry.insert(len(pathName), "/")
			
	#Output statistics for multiple input files
	def appendMultiInStats(self):
		with open(self.compileName, "a") as compileFile:
			#Used to indictate scope of certain statistics
			if self.restrictSearchBV.get() is True:
				qualifier = "(D),"
			else:
				qualifier = "(DN),"
		
			#Print header
			print ("Cumulative Summary", file = compileFile)
			
			#Output off-bout stats
			print ("Off-Bout Count", qualifier, str(len(self.multiInOffDurs)), file = compileFile)
			print ("Mean Off Dur", qualifier, str(round(statistics.mean(self.multiInOffDurs), 2)), file = compileFile)
			print ("Off Dur StDev", qualifier, str(round(statistics.stdev(self.multiInOffDurs), 2)), file = compileFile)
			print ("Mean Off Temp Drop", qualifier, str(round(statistics.mean(self.multiInOffDecs), 3)), file = compileFile)
			print ("Off Drop StDev", qualifier, str(round(statistics.stdev(self.multiInOffDecs), 3)), file = compileFile)
			
			#Output on-bout stats
			print ("On-Bout Count", qualifier, str(len(self.multiInOnDurs)), file = compileFile)
			print ("Mean On Dur", qualifier, str(round(statistics.mean(self.multiInOnDurs), 2)), file = compileFile)
			print ("On Dur StDev", qualifier, str(round(statistics.stdev(self.multiInOnDurs), 2)), file = compileFile)
			print ("Mean On Temp Rise", qualifier, str(round(statistics.mean(self.multiInOnIncs), 3)), file = compileFile)
			print ("On Rise StDev", qualifier, str(round(statistics.stdev(self.multiInOnIncs), 3)), file = compileFile)
			
			#Output daytime/nighttime stats
			print ("Full Day Count,", str(self.multiInFullDayCount), file = compileFile)
			print ("Mean Daytime Egg Temp,", str(round(statistics.mean(self.multiInDayTemps), 3)), file = compileFile)
			print ("Day Egg Temp StDev,", str(round(statistics.stdev(self.multiInDayTemps), 3)), file = compileFile)
			print ("Mean Nighttime Egg Temp,", str(round(statistics.mean(self.multiInNightTemps), 3)), file = compileFile)
			print ("Night Egg Temp StDev,", str(round(statistics.stdev(self.multiInNightTemps), 3)), file = compileFile)
			
			if self.airValid is True:
				print ("Mean Air Temp,", str(round(statistics.mean(self.multiInAirTemps), 3)), file = compileFile)
				print ("Min Air Temp,", str(min(self.multiInAirTemps)), file = compileFile)
				print ("Max Air Temp,", str(max(self.multiInAirTemps)), file = compileFile)
					
			print ("\n\n", file = compileFile)
	
	#Reset variables used to store data across multiple input files
	def resetMultiInVars(self):
		#Variables used for storing information accross multiple input files
		self.multiInOffDurs    = []
		self.multiInOffDecs    = []
		self.multiInOnDurs     = []
		self.multiInOnIncs     = []
		self.multiInDayTemps   = []
		self.multiInNightTemps = []		
		self.multiInAirTemps   = []
		self.multiInFullDayCount = 0
	
	#Generates graph in edit mode with no preselected vertices
	def selectVertices(self):
		editCKChange = False
		daysList = []
		nightsList = []
		
		self.checkAirValid(self.inputFileAdvE.get())
		
		if self.checkValidPlotOps() and self.checkValidAdv(_checkInput = True, _checkVerts = False):
			self.setVars()
			
			try:
				#Create 2D matrix from input file data
				self.masterList = coreF.prepareList(self, self.inputFileAdvE.get())
				
				#Get totalVerts
				masterBlock = coreC.block(self, 0, (len(self.masterList) - 1), False)
				
				#Get daysList and nightsList for plotting vertical lines
				coreF.splitDays(self, daysList, nightsList)
			except Exception:
				messagebox.showerror(("Input File Error (Advanced tab)"), 
				"Input file could not be processed. Try using the \"Check\" button in the main tab to identify the issue.")	
				traceback.print_exc()
				return False
			
			#Turn on edit mode
			if not self.editModeBV.get():
				self.editCK.select()
				editCKChange = True
			
			coreF.graph(self, daysList, nightsList, masterBlock, plotVertices = False)
			
			#Revert to original edit mode state
			if editCKChange:
				self.editCK.deselect()
	
	#Ensure valid parameters and initiate algorithm training
	def trainAlgo(self):
		#(flag)Fill entries with appropriate test files -- WILL BE DELETED LATER
		# self.inputFileAdvE.insert(0, "C:/Users/wxhaw/Desktop/github/whereabout/inputFiles/Testing/TresTest.csv")
		# self.vertexFileAdvE.insert(0, "C:/Users/wxhaw/Desktop/github/whereabout/inputFiles/Testing/tresTrainingVerts.html")
		
		#Initialize variables to hold best settings
		self.bestTimeThreshAdvOn = 0
		self.bestTimeThreshAdvOff = 0
		self.bestTempThreshAdvOn = 0
		self.bestTempThreshAdvOff = 0
		self.bestMinSlopeOn = 0
		self.bestMinSlopeOff = 0
		self.bestSlopeRangeOn = 0
		self.bestSlopeRangeOff = 0
		self.bestVertMigrationBV = 0

		


		#(flag)
		startTime = time.time()
		#Check if main tab settings
		if self.checkValidMain(True, True):
			self.setVars()
			#Check advanced tab settings
			if self.checkValidAdv(_checkInput = True):
				#Create 2D matrix from input file data
				self.masterList = coreF.prepareList(self, self.inputFileAdvE.get())
				
				#Get user-provided vertex locations
				userVertDPs = []
				userVertDPs = coreF.extractDPsFromHTML(self, self.vertexFileAdvE.get())
				
				#Take only the section of input file data corresponding to vertex selections
				self.masterList = coreF.sliceMasterList(self, userVertDPs)
				if self.masterList is False:
					messagebox.showerror(("Vertex Selection Error (Advanced tab)"), 
					"Provided vertex selection file does not appear to correspond with the provided input file.")
					return False
				
				#Commnse training
				bestScore = coreML.runTraining(self, userVertDPs)
				
				#Print final parameters
				print ("\n\nbest on time threshold =", self.bestTimeThreshAdvOn)
				print ("best off time threshold =", self.bestTimeThreshAdvOff)
				print ("best on temper threshold =", self.bestTempThreshAdvOn)
				print ("best off temper threshold =", self.bestTempThreshAdvOff)
				print ("best score =", bestScore)
				
				print ("\nbest min on slope =", self.bestMinSlopeOn)
				print ("best min off slope =", self.bestMinSlopeOff)
				print ("best on slope range =", self.bestSlopeRangeOn)
				print ("best off slope range =", self.bestSlopeRangeOff)
				
				print ("\nbest mirgration bool =", self.bestVertMigrationBV)
				
				#Populate entry boxes with best parameters	
				self.timeThreshAdvOnE.delete(0, "end")
				self.timeThreshAdvOnE.insert(0, self.bestTimeThreshAdvOn)
				self.timeThreshAdvOffE.delete(0, "end")
				self.timeThreshAdvOffE.insert(0, self.bestTimeThreshAdvOff)
				self.tempThreshAdvOnE.delete(0, "end")
				self.tempThreshAdvOnE.insert(0, self.bestTempThreshAdvOn)
				self.tempThreshAdvOffE.delete(0, "end")
				self.tempThreshAdvOffE.insert(0, self.bestTempThreshAdvOff)

				self.minSlopeOnE.delete(0, "end")
				self.minSlopeOnE.insert(0, self.bestMinSlopeOn)
				self.minSlopeOffE.delete(0, "end")
				self.minSlopeOffE.insert(0, self.bestMinSlopeOff)
				self.slopeRangeOnE.delete(0, "end")
				self.slopeRangeOnE.insert(0, self.bestSlopeRangeOn)
				self.slopeRangeOffE.delete(0, "end")
				self.slopeRangeOffE.insert(0, self.bestSlopeRangeOff)
				
				if self.bestVertMigrationBV == True:
					self.vertMigrationCK.select()
				else:
					self.vertMigrationCK.deselect()
				
				#Report duration of training
				endTime = time.time()
				trainDur = round((endTime - startTime), 2)
				print ("Train algorithm complete")
				print ("Duration = ", trainDur, "seconds\n\n")
				
				#Announces successful algorithm training	
				messagebox.showinfo("Training complete", 
				"Algorithm training was successful. Parameters have been updated.  Save settings with \"Save Config\" button at top of the Advanced tab.")
	
	
	#Check ensure valid parameters and execute processing
	def toggleRun(self, root):
		try:
			#If the user selected multiple input files:
			if self.inPathName and len(self.inPathName) > 1:
				
				successful = True
			
				#Clear variables holding information regarding cumulative statistics
				self.resetMultiInVars()
				
				#Set column identities
				# self.dataPointCol = (self.indicesColE.get() + 1)
				# self.dateTimesCol = (self.dateTimesColE.get() + 1)
				# self.tempsCol = (self.tempsColE.get() + 1)
				
				#Show error if "Use provided vertices" is selected while processing multiple files
				if self.useProvidedBV.get() is True:
					messagebox.showerror(("Settings Error (Main tab)"), 
					"\"Use provided vertices\" cannot be selected when processing multiple files.  Please disable this option for multifile processing.")
					return False
				
				firstIn = True
				i = 1
				#Process each input file
				for inFile in self.inPathName:
					#Update file names
					self.multiInSetup(inFile)
					#Check if all user inputs are valid
					if self.checkValidMain(firstIn) and self.checkValidPlotOps() and self.checkValidStatsOps() and self.checkValidAdv():
						#Check if a valid air temps column is present
						self.checkAirValid(inFile)
						
						self.run = True
						#Update run button
						self.runB["text"] = ("Running (file " + str(i) + ")...")
						self.runB.config(bg = "gray", fg = "white", width = 15, height = 1)
						i += 1
						# try:
						#(flag)
						root.update()
						# except:
							# print (" ")
							
						#Set variables based on user provided settings
						self.setVars()
						#Create 2D matrix from input file data
						self.masterList = coreF.prepareList(self, self.inFile)
						
						#(flag)
						# try:
							# Call primary function
						main(self, False)
						# except:
							# successful = False
							# print("flagB")
							# break
						
						#Update default output file names
						self.updateDefaultOuts()
						
						firstIn = False
					#Cancel run if error detected
					else:
						successful = False
						break
				
				#Output statistics for all input files if requested
				if successful and self.complileStatsBV.get():
					self.appendMultiInStats()
					
			#Single file processing
			else:
				#Check if all user inputs are valid
				if self.checkValidMain() and self.checkValidPlotOps() and self.checkValidStatsOps() and self.checkValidAdv():	
					#Check if a valid air temps column is present
					self.checkAirValid()
					
					self.run = True
					#Update run button
					self.runB["text"] = "Running..."
					self.runB.config(bg = "gray", fg = "white", width = 10, height = 1)
					root.update()
						
					#Set variables based on user provided settings	
					self.setVars()
					#Create 2D matrix from input file data
					self.masterList = coreF.prepareList(self, self.inFile)
					
					#Call primary function
					main(self, self.verticesProvided)
					#Update default output file names
					self.updateDefaultOuts()
					#Return run button to default state
					self.runB["text"] = "Run"
					
			#Return run button to default state
			self.runB["text"] = "Run"
			self.runB.config(bg = "red4", fg = "white", width = 10, height = 1)
			self.run = False		
		except Exception:
			traceback.print_exc()
			messagebox.showerror(("Unidentified Error"), "An unknown error has occered.  Please report this error to wxhawkins@gmail.com")									
		
	#Cleanly end program if user attempts to exit	
	def onClosing(self, root):
		self.valid = False
		sleep(0.5)
		root.destroy()
	
	#Extract default settings from configuration file
	def initConfig(self):
		#Connect to config file to set default value
		self.config = configparser.RawConfigParser()
		#If config file missing, copy from configStatic.ini
		#(flag) dont forget to add this file
		if not os.path.exists(os.path.join(self.coreDir, "config_files", "defaultConfig.ini")):
			copyfile(os.path.join(self.coreDir, "misc_files", "configStatic.ini"), os.path.join(self.coreDir, "config_files", "defaultConfig.ini"))
		
		# if not os.path.exists("./../config_files/defaultConfig.ini"):
			# copyfile("./../misc_files/configStatic.ini", "./../config_files/defaultConfig.ini")
			
		self.config.read(os.path.join(self.coreDir, "config_files", "defaultConfig.ini"))
		# self.config.read("./../config_files/defaultConfig.ini")
		
		# try:
		#Display warning if there is a discrepency in main tab and advance tab parameters
		if self.config.get("Main Settings", "duration_threshold") != "Adv.":
			if(
				self.config.get("Main Settings", "duration_threshold") != self.config.get("Advanced Settings", "duration_threshold(on)") or
				self.config.get("Main Settings", "duration_threshold") != self.config.get("Advanced Settings", "duration_threshold(off)")				
			  ):
				messagebox.showwarning("Duration Threshold Conflict", 
				("Config file duration threshold settings from the main and advanced tab are not in agreement.  NestIQ will be using the settings from the advanced tab."))

		if self.config.get("Main Settings", "temperature_threshold") != "Adv.":
			if(
				self.config.get("Main Settings", "temperature_threshold") != self.config.get("Advanced Settings", "temperature_threshold(on)") or
				self.config.get("Main Settings", "temperature_threshold") != self.config.get("Advanced Settings", "temperature_threshold(off)")				
			  ):
				messagebox.showwarning("Temperature Threshold Conflict", 
				("Config file temperature threshold settings from the main and advanced tab are not in agreement.  NestIQ will be using the settings from the advanced tab."))
	# except:
		# messagebox.showerror(("Config File Loading Error"), 
		# "defaultConfig.ini could not be read: reverting to old settings.")
		# copyfile(os.path.join(self.coreDir, "misc_files", "configStatic.ini"), os.path.join(self.coreDir, "config_files", "defaultConfig.ini"))
		# copyfile("./../misc_files/configStatic.ini", "./../config_files/defaultConfig.ini")
		# self.initConfig()
					
	#Rewrite configuration file with new default values
	def updateConfig(self, configFile = None):
		if configFile is None:
			configFile = os.path.join(self.coreDir, "config_files", "defaultConfig.ini")
	
		#Convert True to yes and False to no
		if self.vertMigrationBV.get():
			BVInsert = "yes"
		else:
			BVInsert = "no"
			
		#If advanced threshold for on and off bouts aren't the same, set the main tab value to "Adv."
		if self.tempThreshAdvOnE.get() != self.tempThreshAdvOffE.get():
			self.tempThreshMainInsert = "Adv."
		#If they do agree, set main tab value to match
		else:
			self.tempThreshMainInsert = self.tempThreshAdvOnE.get()

		with open(configFile, "w") as configFile:		
			#Set data time interval
			self.config.set("Main Settings", "data_time_interval", self.intervalE.get())
		
			#If advanced tab duration thresholds are in agreement, update main tab value to this thresold
			if self.timeThreshAdvOnE.get() == self.timeThreshAdvOffE.get():
				self.config.set("Main Settings", "duration_threshold", self.timeThreshAdvOnE.get())
			#Else, set to "Adv."
			else:
				self.config.set("Main Settings", "duration_threshold", "Adv.")
			#If advanced tab temperature thresholds are in agreement, update main tab value to this thresold
			if self.tempThreshAdvOnE.get() == self.tempThreshAdvOffE.get():
				self.config.set("Main Settings", "temperature_threshold", self.tempThreshAdvOnE.get())
			#Else, set to "Adv."
			else:
				self.config.set("Main Settings", "temperature_threshold", "Adv.")	

			#Set start times and restriction bool
			self.config.set("Main Settings", "day_start_time", self.dayStartE.get())
			self.config.set("Main Settings", "night_start_time", self.nightStartE.get())
			if self.restrictSearchBV.get() is True:
				self.config.set("Main Settings", "restrict_bout_search", "yes")
			else:
				self.config.set("Main Settings", "restrict_bout_search", "no")				
				
			#Set plot options tab default values
			if self.plotDimVar.get() == 1:
				self.config.set("Plot Options", "plot_dim_mode", "auto")
			else:
				self.config.set("Plot Options", "plot_dim_mode", "manual")
				
			self.config.set("Plot Options", "plot_x_dim", self.plotDimXE.get())
			self.config.set("Plot Options", "plot_y_dim", self.plotDimYE.get())
			
			self.config.set("Plot Options", "title_font_size", self.titleFontSizeE.get())
			self.config.set("Plot Options", "axis_title_font_size", self.axisTitleFontSizeE.get())
			self.config.set("Plot Options", "axis_label_font_size", self.axisLabelFontSizeE.get())
			self.config.set("Plot Options", "axis_tick_size", self.axisTickSizeE.get())
			self.config.set("Plot Options", "legend_font_size", self.legendFontSizeE.get())
			
			self.config.set("Plot Options", "egg_temp_point_color", self.eggTempPointColorVar.get())
			self.config.set("Plot Options", "egg_temp_line_color", self.eggTempLineColorVar.get())
			self.config.set("Plot Options", "bout_prediction_color", self.boutColorVar.get())
			self.config.set("Plot Options", "day_marker_color", self.dayMarkerColorVar.get())
			self.config.set("Plot Options", "air_temp_color", self.airTempColorVar.get())
			
			self.config.set("Plot Options", "egg_temp_point_size", self.eggTempPointSize_E.get())
			self.config.set("Plot Options", "egg_temp_line_size", self.eggTempLineSize_E.get())
			self.config.set("Plot Options", "bout_prediction_size", self.boutSize_E.get())
			self.config.set("Plot Options", "day_marker_size", self.dayMarkerSize_E.get())
			self.config.set("Plot Options", "air_temp_size", self.airTempSize_E.get())
			
			if self.showDayDelimsBV.get() is True:
				self.config.set("Plot Options", "show_day_marker", "yes")
			else:
				self.config.set("Plot Options", "show_day_marker", "no")
				
			if self.showDayDelimsBV.get() is True:
				self.config.set("Plot Options", "show_air_temp", "yes")
			else:
				self.config.set("Plot Options", "show_air_temp", "no")
				
			if self.showDayDelimsBV.get() is True:
				self.config.set("Plot Options", "show_grid", "yes")
			else:
				self.config.set("Plot Options", "show_grid", "no")
				
			
			#Set stats options tab default values
			self.config.set("Stats Options", "custom_time_over_temperature", self.superCustE.get())
			self.config.set("Stats Options", "custom_time_under_temperature", self.subCustE.get())
			
			#Set advanced tab default values
			self.config.set("Advanced Settings", "adjacent_Mean_Radius", self.adjMeanRadE.get())
			self.config.set("Advanced Settings", "vertex_Search_Downstream_Limit", self.vertSearchDownLimE.get())
			self.config.set("Advanced Settings", "duration_Threshold(on)", self.timeThreshAdvOnE.get())
			self.config.set("Advanced Settings", "duration_Threshold(off)",  self.timeThreshAdvOffE.get())				
			self.config.set("Advanced Settings", "temperature_Threshold(on)", self.tempThreshAdvOnE.get())
			self.config.set("Advanced Settings", "temperature_Threshold(off)", self.tempThreshAdvOffE.get())
			self.config.set("Advanced Settings", "minimum_Initial_Slope(on)", self.minSlopeOnE.get())
			self.config.set("Advanced Settings", "minimum_Initial_Slope(off)", self.minSlopeOffE.get())
			self.config.set("Advanced Settings", "initial_Slope_Range(on)", self.slopeRangeOnE.get())
			self.config.set("Advanced Settings", "initial_Slope_Range(off)", self.slopeRangeOffE.get())
			self.config.set("Advanced Settings", "vertex_Migration",  BVInsert)
			
			#Write configuration file
			self.config.write(configFile)

#Main function
def main(gui, verticesProvided):
	#Get start time for script duration calculation at end	
	startTime = time.time()
	
	#Print file delimiter/output header
	print ("----------------------------------------------------------")
	print ("Running NestIQ")
	print ("Input file:", gui.inputFileE.get())

	daysList   = []
	nightsList = []
	pairsList  = []
	masterBlock = None
	
	try:
		#Create object for every day and night period
		coreF.splitDays(gui, daysList, nightsList)
	except Exception:
		messagebox.showerror(("Input File Error (Main tab)"), 
		"Input file could not be processed. Try using the \"Check\" button to identify the issue.")	
		traceback.print_exc()
		return False
		
	#Get totalVerts
	masterBlock = coreC.block(gui, 0, (len(gui.masterList) - 1), False)
	
	#Store provided vertices
	if verticesProvided:
		masterBlock.vertices = coreF.extractVertsFromDPs(gui)
		coreF.checkAlternatingTemps(masterBlock)
	#If none provided, identify vertices
	else:		
		coreVD.getVerts(gui, masterBlock)
		
	#Extract bouts based on vertex locations	
	coreF.getBouts(gui, masterBlock)
	if masterBlock.getStats(gui) is False:
		return False
	
	if gui.restrictSearchBV.get() is False:
		masterBlock.depositMultiIns(gui)
	if gui.airValid is True:
			gui.multiInAirTemps += masterBlock.airTemps
	
	#Sort vertices by index
	masterBlock.vertices.sort(key = lambda x: x.index)

	#Acquire temperature and bout information for every daytime period
	for day in daysList:
		#Set vertices
		day.vertices = coreF.extractVertsInRange(gui, masterBlock.vertices, day.start, day.stop)
		#Extract bouts based on vertex locations
		coreF.getBouts(gui, day)
		#Get statistics for days
		day.getStats(gui)
		gui.multiInDayTemps += day.temps
		
		if gui.restrictSearchBV.get() is True:
			day.depositMultiIns(gui)

		
	#Acquire temperature and bout information for every nighttime period
	for night in nightsList:
		if gui.restrictSearchBV.get() is False:
			#Set vertices
			night.vertices = coreF.extractVertsInRange(gui, masterBlock.vertices, night.start, night.stop)
			#Extract bouts based on vertex locations
			coreF.getBouts(gui, night)
		#Get statistics for nights
		night.getStats(gui)
		gui.multiInNightTemps += night.temps
		
	
		
	#Calculate and print various statistics for days	
	days = coreC.blockGroup(gui, daysList)	
	if len(daysList) > 0:
		days.getStats(gui, append = False)
	
	#Calculate and print various statistics for nights	
	nights = coreC.blockGroup(gui, nightsList)
	if len(nightsList) > 0:
		nights.getStats(gui, append = False)
		
	#Create day/night pair objects
	if len(daysList) > 0 and len(nightsList) > 0:
		coreF.getPairs(gui, daysList, nightsList, pairsList)
		#Acquire temperature and bout information for day/night pairs
		for pair in pairsList:
			if gui.restrictSearchBV.get() is False:
				#Set vertices
				pair.vertices = coreF.extractVertsInRange(gui, masterBlock.vertices, pair.start, pair.stop)
				#Extract bouts based on vertex locations
				coreF.getBouts(gui, pair)
			#Get statistics for day/night pairs
			pair.getStats(gui)
			
	#Create blockGroup for day/night pairsList
	pairsBlockGroup = coreC.blockGroup(gui, pairsList)
	if len(pairsList) > 0:
		pairsBlockGroup.getStats(gui, append = False)
			
	#Create graph file if requested
	if gui.makeGraphBool:
		coreF.graph(gui, daysList, nightsList, masterBlock, plotVertices = True, showDragWarn = True)
	
	#Output statistics to file(s) depending on what options selected
	coreF.outStats(gui, days, nights, pairsBlockGroup, masterBlock)
	
	
	
	#Report duration of script run
	endTime = time.time()
	scriptDur = round((endTime - startTime), 2)

	#Print closer for file processing
	print ("Done")
	print ("Duration =", scriptDur, "seconds")
	print ("----------------------------------------------------------\n\n")
	
	#End run
	gui.run = False

# mainThread = threading.Thread(target = launch, args = ())
# mainThread.start()
# mainThread.join()

#Initialize GUI object
gui = guiClass()
