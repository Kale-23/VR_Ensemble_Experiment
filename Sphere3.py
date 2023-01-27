﻿import viz
import viztask
import vizact
import vizshape
import vizinfo
import os

import random
import math
from statistics import mean

import steamvr

##### GLOBALS #####
###################

# These adjust the number of trials of each distannce, and how far the spheres are shown on the z axis from zero
count = 5 # How many spheres trials to create at a certain distance
distance1 = 4 # Distance from zero of foreground trials
distance2 = 6 # Distance from zero of Middle trials
distance3 = 8 # Distance from zero of Background trials

# These adjust the parameters for the imaginary circumferencne the spheres are placed on
cirlceRadius = 2 # Radius of circumference
circleCenterX = 0 # where the center of the circumference will be placed on the x axis
jitter = 5 # degrees the spheres can jitter from thier placement angle (ie with jitter = 5, the sphere at 0 degrees will be randomly placed between 355 degrees and 5 degrees)

# Pause times between events of experiment
trialShowPause = 1 #time to pause after showing the trial spheres
fixationShowPause = 0.5 #time the fixation point is on screen before spheres show
betweenTrialPause = 0 #time between submission of probe sphere and next trial start

# Radius values for spheres
rLow = 0.2 # Lowest radius a sphere can randomly be given
rHigh = 0.4 # Highest radius a sphere can randomly be given
rAvgLow = 0.25 # minimum average radius for spheres in each trial, if below this value sphere values for trial will be deleted and new values will be generated
rAvgHigh = 0.35 # maximum average radius for spheres in each trial, if above this value, sphere values for trial will be deleted ad ew values will be generated

# probe parameters
probeRadLow = 0.25 # Lowest radius the probe can randomly be given
probeRadHigh = 0.35 # Highest radius the probe can randomly be given
scale_factor = 1 # factor by which the radius of the probe will be scaled by when shown.
valueToScaleBy = 1.005 # value by which the scale factor of the probe is increased/decreased during response

# response parameters
endResponseInput = steamvr.BUTTON_TRIGGER # participant input that confirms their probe size and ends response portion of trial.
timeToScale = 10 # max time participant has to scale probe sphere and submit answer.

# globals
sphereList = [] # All spheres and trials are pregenerated before running the experiment, each trial is stored in this list. The trials stored will be lists of 8 sphere parameters per trial.
spheresOut = [] # Will hold any sphere entity that is currently being shown in the environment, is emptied anytime removeSpheres is called
trialProbeResponse = [] # holds the data of participant probe sphere responses for each trial (probeRadius, probeResponseTime).


##### METHODS #####
###################

'''
Creates the '+' mark within the middle of the imaginary circumference. 
The fixation point will be shown at the same distance as the spheres, and will scale with distance so as to always appear to be same size.
'''
def showFixationPoint(dist):
	global spheresOut
	
	box1 = vizshape.addBox(size=(0.5, 0.1, 0.1), color = viz.WHITE)
	box2 = vizshape.addBox(size=(0.1, 0.5, 0.1), color = viz.WHITE)
	box1.setPosition(0,participantHeight,dist)
	box1.setScale([dist / distance2, dist / distance2, dist / distance2])
	box2.setPosition(0,participantHeight,dist)
	box2.setScale([dist / distance2, dist / distance2, dist / distance2])
	spheresOut.append(box1)
	spheresOut.append(box2)
	


'''
Creates 8 spheres for each trial. 
Sphere parameters will be gennerated every 45 degrees (+/- 'jitter') around the imaginary circumference starting at 0 degrees up to 315 degrees. 
The imaginary circumference will always appear to be the same size no matter the distance from the participant.
x parameter generated from getX(), y parameter generated from getY(), distance is z value from z = 0 given by 'distance', radius is randomly generated between 'rLow' and 'rHigh'.
If the average radius of all 8 spheres is between 'rAvgLow' and 'rAvgHigh', the trial is accepted and added to 'sphereList', else it is thrown out and new parameters are chosen.
'''
def makeSpheres(count, distance, rL, rH):
	
	'''
	finds the x value within the imaginary circumference to place the sphere at. 
	'''
	def getX(angle, distance):
		return circleCenterX + ((cirlceRadius * distance) * math.cos(angle))

	'''
	finds the y value within the imaginary circumferecne to place the sphere at. 
	'''
	def getY(angle, distance):
		return participantHeight + ((cirlceRadius * distance) * math.sin(angle))

	global sphereList
	placementAngle = [0, 45, 90, 135, 180, 225, 270, 315]
	
	
	tempCount = 0
	while tempCount < count:
	
		spheres = []
		meanRadius = []
		
		for i in placementAngle:
			angle = random.randint(i - jitter, i + jitter)
			radius = random.uniform(rL, rH)
			
			spheres.append([
			getX(math.radians(angle), distance / distance2),
			getY(math.radians(angle), distance / distance2), 
			distance,
			radius
			]) 
			meanRadius.append(radius)
		
		if rAvgHigh > mean(meanRadius) > rAvgLow:
			sphereList.append(spheres)
			tempCount += 1
	

'''
takes a list of sphere parameters, adds them to the environment, and adds them to 'spheresOut'.
'''
def addSpheres(spheres):
	global spheresOut
	
	for s in spheres:
		sphereAdd = vizshape.addSphere(s[3] * (s[2] / distance2))
		sphereAdd.setPosition(s[0], s[1], s[2])
		spheresOut.append(sphereAdd)

'''
removes any sphere entities within 'spheresOut' from the environement, and empties 'spheresOut'.
'''
def removeSpheres():
	global spheresOut
	
	for s in spheresOut:
		s.remove()
	spheresOut = []
	



'''
creates probe sphere parameters and puts the probe into the enviromet and into 'spheresOut'. 
The probe's radius is random between 'probeRadLow' and 'probeRadHigh', the distance is the same as the trial's that was just shown, and is always x = 0, y = 2.
Once the probe is shown, participant is allowed input (from keyboard/ joystick/ etc). Will call onKeyDown() on any input.
If 'endResponseInput' is input, the participant can no longer provide input until the next trial, and the current probe's initial radius and scale factor are returned.
'''
def response(dist):
	
	'''
	when called, if 'decreaseScaleFactorInput' is input, will call decrease_scale(),
	if 'increaseScaleFactorInput' is input, will call increase_scale(),
	and will do nothing if any other button is pressed
	'''
	def onKeyDown():
		'''
		will multiply 'scale_factor' by 'valueToScaleBy'.
		'''
		def increase_scale(sphere):
			global scale_factor
			scale_factor *= valueToScaleBy
			sphere.setScale([scale_factor, scale_factor, scale_factor])

		'''
		will divide 'scale_factor' by 'valueToScaleBy'.
		'''
		def decrease_scale(sphere):
			global scale_factor
			scale_factor /= valueToScaleBy
			sphere.setScale([scale_factor, scale_factor, scale_factor])
			
		if controller.getThumbstick()[0] < -0.1:
			decrease_scale(spheresOut[0])
		elif controller.getThumbstick()[0] > 0.1:
			increase_scale(spheresOut[0])
		else:
			pass


	global spheresOut
	global scale_factor
	spheresOut = []
	
	# Probe setupt and output to environment
	probeRadius = random.uniform(probeRadLow, probeRadHigh)
	probe = vizshape.addSphere(probeRadius)
	probe.setPosition(0, participantHeight, dist)
	spheresOut.append(probe)
	
	# Set the initial scaling factor for the probe in this trial
	scale_factor = 1.0

	# Allows participant input during this time until 'endResponseInput' is input.
	responseUpdater = vizact.onupdate(0, onKeyDown)
	responded = viztask.waitSensorDown(controller, endResponseInput)
	waitTime = viztask.waitTime(timeToScale)
	
	
	#waits until participant responds or time limit is reached, then stops participant input
	time = yield viztask.waitAny([waitTime,responded])
	responseUpdater.setEnabled(viz.OFF)
	
	#putput of variables
	noResponse = 0
	if time.condition == waitTime:
		noResponse = 1
	
	viztask.returnValue([probeRadius, scale_factor, probeRadius * scale_factor, noResponse])
	
'''

'''
def learningPhase():
	#participant sees this
	instructions = """This experiment """ #FINISH THIS
	panel.alignment(viz.ALIGN_LEFT_CENTER)
	panel.setBackdrop(viz.BACKDROP_RIGHT_BOTTOM)
	panel.resolution(1)
	panel.disable(viz.LIGHTING)
	panel.font('Arial')
	panel.fontSize(4)
	textLink = viz.link(viz.MainView,panel,mask=viz.LINK_POS)
	textLink.setOffset([-50,0,100])
	
	#instructor sees this
	info = vizinfo.InfoPanel("Have participant press") #FINISH THIS
	info.visible(viz.ON)
	
	#wait for conformation and removes info panels
	yield viztask.waitSensorDown(controller, [steamvr.BUTTON_TRIGGER])
	info.remove()
	panel.remove()
	

	
'''
for each trial in 'sphereList':
The fixation point will be shown for 'fixationShowPause' seconds.
The spheres of the trial will show for 'trialShowPause' seconds.
Both the fixation point and spheres will be taken off the screen, and the probe will appear.
The participant is allowed to adjust the size of the probe until they are satisfied, and then the probe is taken off the screen.
'''
def experiment():
	global SphereList
	global trialProbeResponse
	

	for i in range(len(sphereList)): # runs through all trials stored in 'sphereList'
		yield showFixationPoint(sphereList[i][0][2]) #shows fixation cross
		yield viztask.waitTime(fixationShowPause) #pause
		yield addSpheres(sphereList[i]) #shows trial spheres
		yield viztask.waitTime(trialShowPause) #pause
		yield removeSpheres() #removes cross and spheres
		
		startTime = viz.tick() #starts timing response time
		probe = yield response(sphereList[i][0][2]) #response portion of trial is performed
		responseTime = viz.tick() - startTime #response time is recorded
		resp = [probe, responseTime]
		trialProbeResponse.append(resp)
		yield removeSpheres() #removes probe sphere
		
	writeOut() #writes all data to file
	print("experiment over")



'''
Creates new file and records trial, sphereNumber, sphereX, sphereY, sphereDist, sphereRadius, probeAnswerRadius, probeAnswerTime for each sphere within a trial, for each trial.
'''
def writeOut():
	
	'''
	automatically gets and updates the current participant number for naming output file.
	'''
	def getParticipantNumber():
		if not os.path.exists('currentParticipant.txt'):
			with open('currentParticipant.txt','w') as f:
				f.write('1')
		with open('currentParticipant.txt','r') as f:
			st = int(f.read())
			out = st
			st+=1 
		with open('currentParticipant.txt','w') as f:
			f.write(str(st))
		
		return out
	
	'''
	outputs each trial sphere to string format that works with csv output
	'''
	def sphereToString(s):
		tempString = ""
		for i in range(len(s)):
			tempString += "(" + str(s[i][0]) + ";" + str(s[i][1]) + ";" + str(s[i][2]) + ";" + str(s[i][3]) + "),"
		return tempString[0:-1]

	'''
	gets average of trial sphere radii for a trial
	'''
	def sphereTrialAverageRadius(s):
		total = 0
		for i in range(len(s)):
			total += s[i][3]
		return total / len(s)
	
	path = "participantData"
	participantNumber = getParticipantNumber()
	
	if not os.path.exists(path):
		os.makedirs(path)

	filename = "Participant" + str(participantNumber) + ".csv"
	with open(os.path.join(path, filename), 'w') as outfile:
		try:
			outfile.write("ID,age,gender,hand,trial,sphereOne,sphereTwo,sphereThree,sphereFour,sphereFive,sphereSix,sphereSeven,sphereEight,sphereDistance, sphereAverageRadius,probeStartingRadius,probeAnswerRadius,probeScaleFactor,probeResponseTime,probeResponseOverTimeLimit\n")
			
			for i in range(len(sphereList)):
				outfile.write("{},{},{},{},{},{},{},{},{},{},{},{},{}\n".format(participantNumber, "ageTest", "genderTest", "handTest", i + 1, sphereToString(sphereList[i]), sphereList[i][0][2], sphereTrialAverageRadius(sphereList[i]), trialProbeResponse[i][0][0], trialProbeResponse[i][0][2], trialProbeResponse[i][0][1], trialProbeResponse[i][1], trialProbeResponse[i][0][3]))
		
		except IOError:
			viz.logWarn("Dont have the file permissions to log data")



##### MAIN #####
################

if __name__ == '__main__':
	
	#setup
	viz.setMultiSample(4)
	viz.fov(60)
	viz.go()
	
	#vr setup
	hmd = steamvr.HMD()
	if not hmd.getSensor():
		sys.exit('SteamVR HMD not detected')
	
	navigationNode = viz.addGroup()
	viewLink = viz.link(navigationNode, viz.MainView)
	viewLink.preMultLinkable(hmd.getSensor())
		
	for controller in steamvr.getControllerList():
		controller.model = controller.addModel(parent=navigationNode)
		controller.model.disable(viz.INTERSECTION)
		viz.link(controller, controller.model)
		
		viz.startLayer(viz.LINES)
		viz.vertexColor(viz.WHITE)
		viz.vertex([0,0,0])
		viz.vertex([0,0,100])
		controller.line = viz.endLayer(parent=controller.model)
		controller.line.disable([viz.INTERSECTION, viz.SHADOW_CASTING])
		controller.line.visible(True)#if it's set to true then we'll always see the controlller liner
	
	#getting participant height #### DO THIS SOMEWHERE ELSE AFTER TESTING ####
	participantHeight = 1.82
	
	#grey grid #### REMOVE/ CHANGE AFTER TESTING ####
	grid = vizshape.addGrid()
	grid.color(viz.GRAY)
	
	#experiment run from here
	makeSpheres(count, distance1, rLow, rHigh)
	makeSpheres(count, distance2, rLow, rHigh)
	makeSpheres(count, distance3, rLow, rHigh)
	random.shuffle(sphereList)

	theExperiment = viztask.schedule(experiment())
		
	
