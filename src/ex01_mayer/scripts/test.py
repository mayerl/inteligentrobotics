#! /usr/bin/env python

import rospy
import numpy as np
import os
import geometry_msgs.msg
import nav_msgs.msg
from collections import deque
import math
import random

from operator import itemgetter

from Tkinter import Tk, Canvas, Frame, BOTH

from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan

a = []
lastX, lastY = 0, 0
lastReadings = deque(())

gStartCollision = False
gTurnDirection = 0
gDirection = ""

kDistanceToWall = 0.5
kSideSamples = 50
kLinearSpeed = 0.3
kAngularSpeed = 0.3

def printMatrix():

	#x coords
	min_x = min(a)[0]
	max_x = max(a)[0]

	#y coords
	min_y = min(a, key=itemgetter(1))[1]
	max_y = max(a, key=itemgetter(1))[1]
	#min_x, max_x, min_y, max_y = a[0][0], a[0][-1], a[1][0], a[1][-1]	
	print "min_x=%d, min_y=%d" %(min_x, min_y)
	print "max_x=%d, max_y=%d" %(max_x, max_y)
	x_index = max_x - min_x + 1
	y_index = max_y - min_y + 1
	
	#print x_index
	#print y_index
	
#	for j in range(max_y, min_y -1, -1):
#		s=''	
#		for i in range(min_x, max_x + 1):
#			if (i,j) in a:
#				s+='@'
#			else:
#				s+='-'
#		print s
	

def processOdometry(odoMsg):
	os.system('clear')
	#print "linear: x=%0.3f, y=%0.3f, z=%0.3f" %(odoMsg.pose.pose.position.x,odoMsg.pose.pose.position.y, odoMsg.pose.pose.position.z)
	#print "angular(quaternion): x=%0.2f, y=%0.2f, z=%0.2f, w=%0.2f" %(odoMsg.pose.pose.orientation.x,odoMsg.pose.pose.orientation.y, odoMsg.pose.pose.orientation.z, odoMsg.pose.pose.orientation.w)	
	x = int(odoMsg.pose.pose.position.x * 100 / 5)
	y = int(odoMsg.pose.pose.position.y * 100 / 5)
	tup = (x, y)	
	if tup not in a:
		a.append(tup)
	a.sort(key=itemgetter(0,1))
	
	avgLastX, avgLastY = 0.0, 0.0
	
	for i in lastReadings:
		avgLastX += i[0]
		avgLastY += i[1]
	avgLastX /= 3
	avgLastY /= 3
	
	currentX = tup[0]
	currentY = tup[1]

	print "current position: (%d, %d)" %(currentX, currentY)	

	if currentX > avgLastX:
		if currentY > avgLastY:
			print "going NE"
			direction = (0.5, 0.5)
		elif currentY < avgLastY:
			print "going SE"
			direction = (0.5, -0.5)
		else:
			print "going E"
			direction = (1, 0)
	elif currentX < avgLastX:
		if currentY > avgLastY:
			print "going NW"
			direction = (-0.5, 0.5)
		elif currentY < avgLastY:
			print "going SW"
			direction = (-0,5. -0.5)
		else:
			print "going W"
			direction = (-1,0)
	else:
		if currentY > avgLastY:
			print "going N"
			direction = (0, 1)
		elif currentY < avgLastY:
			print "going S"
			direction = (0, -1)
		else:
			print "not moving"
			direction = (0,0)	

	print "direction values: %s" %(direction,)
	if len(lastReadings) < 3:
		lastReadings.append(tup)
	else:
		lastReadings.popleft()
		lastReadings.append(tup)

	printMatrix()	
#def callback( sensor_data ):
	
	#sensor_data (LaserScan data type) has the laser scanner data
	#base_data (Twist data type) created to control the base robot
	
#	block_size = 50;
	
#	for i in range(len(sensor_data.ranges)/block_size):
		#print i
		#print np.mean(sensor_data.ranges[i*block_size:i*block_size+block_size])

#	base_data = Twist()
	#print len(sensor_data.ranges[0:50])
	#print np.mean(sensor_data.ranges[0:50])
	#base_data.linear.x = 0.3
	
	#base_data.linear.y = 0.3	
       
#	pub.publish( base_data )

def callback( sensor_data ):
	global gStartCollision
	global gTurnDirection
	global gDirection
	#sensor_data (LaserScan data type) has the laser scanner data
	#base_data (Twist data type) created to control the base robot
	collision = False
	leftMean = 0
	leftSamples = 0
	rightMean = 0
	rightSamples = 0
	turningAngle = 0
	readingSum = 0
	base_data = Twist()

	k = 0
	reading = []
	angles = []
	
	for index in range(len(sensor_data.ranges)):

		if math.isnan(sensor_data.ranges[index]):
			continue
		elif math.isinf(sensor_data.ranges[index]):
			reading.append(6.0)
			angles.append(sensor_data.angle_min + sensor_data.angle_increment*index)
		else:
			reading.append(sensor_data.ranges[index])
			angles.append(sensor_data.angle_min + sensor_data.angle_increment*index)

		if reading[k] < kDistanceToWall:
			collision = True


		k = k+1

	for index in range(len(reading)):

		if angles[index] < 0:
			rightMean = rightMean + reading[index]
			rightSamples = rightSamples + 1
		else:
			leftMean = leftMean + reading[index]
			leftSamples = leftSamples + 1

		turningAngle = turningAngle + angles[index] * reading[index]
		readingSum = readingSum + reading[index]

	leftMean = leftMean / leftSamples
	rightMean = rightMean / rightSamples
	turningAngle = turningAngle / readingSum

	#rospy.loginfo("Right mean: %f",rightMean)
	#rospy.loginfo("Left mean: %f",leftMean)

	if collision:
		if gStartCollision == False:
			if rightMean > leftMean:
				gTurnDirection = -1
				gDirection = "RIGHT"	
			else:
				gTurnDirection = 1
				gDirection = "LEFT" 
			gStartCollision = True

		base_data.angular.z = kAngularSpeed * gTurnDirection

		rospy.loginfo("Wall ahead. Turning " + gDirection)
	else:
		gStartCollision = False
		base_data.linear.x = kLinearSpeed	
		base_data.angular.z = turningAngle
		rospy.loginfo("Going towards %f",turningAngle);	
	
        pub.publish( base_data  )

if __name__ == '__main__':
	
	rospy.init_node('reactive_mover_node')
	rospy.Subscriber('base_scan', LaserScan, callback)
	#rospy.Subscriber('pose', processOdometry)
	odoSub = rospy.Subscriber('odom', nav_msgs.msg.Odometry, processOdometry)
 
	pub = rospy.Publisher('cmd_vel', Twist, queue_size=100)
    	rospy.spin()
