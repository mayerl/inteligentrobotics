#! /usr/bin/env python
# This basic node subscribes to incoming laser and sonar messages,
# decides what to do based on the incoming data, then publishes
# movement commands to the robot.

# Remember to comment your code so your team mates can understand it!

# @author Claudio Zito, Marco Becerra
import rospy
import random
import math
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan

gStartCollision = False
gTurnDirection = 0
gDirection = ""

kMaximumReading = 20
kMinimumReading = 0.3
kOutterSamples = 50
kRobotSpeed = 0.3
kRangeAccuracy = 20

def callback( sensor_data ):
	global gStartCollision
	global gTurnDirection
	global kOutterSamples
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

		if math.isinf(sensor_data.ranges[index]) or math.isnan(sensor_data.ranges[index]):
			continue
		else:
			reading.append(sensor_data.ranges[index])
			angles.append(sensor_data.angle_min + sensor_data.angle_increment*index)

		if reading[k] < kMinimumReading:
			collision = True


		k = k+1

	for index in range(len(reading)):

		if index < kOutterSamples:
			rightMean = rightMean + reading[index]
			rightSamples = rightSamples + 1
		elif index >= len(reading) - kOutterSamples:
			leftMean = leftMean + reading[index]
			leftSamples = leftSamples + 1

		turningAngle = turningAngle + angles[index] * reading[index]
		readingSum = readingSum + reading[index]

	#rospy.loginfo("highestIndex: %d",highestIndex)

	leftMean = leftMean / leftSamples
	rightMean = rightMean / rightSamples
	turningAngle = turningAngle / readingSum

	if collision:
		if gStartCollision == False:
			if rightMean > leftMean:
				gTurnDirection = -1
				gDirection = "RIGHT"	
			else:
				gTurnDirection = 1
				gDirection = "LEFT" 
			gStartCollision = True

		base_data.angular.z = kRobotSpeed * gTurnDirection

		rospy.loginfo("Wall ahead. Turning " + gDirection)
	else:
		gStartCollision = False
		base_data.linear.x = kRobotSpeed
		angle = turningAngle		
		base_data.angular.z = angle
		rospy.loginfo("Going towards %f",angle);
		#rospy.loginfo("Highest index: %d",highestIndex);	
	
        pub.publish( base_data  )

if __name__ == '__main__':
	rospy.init_node('reactive_mover_node',log_level=rospy.DEBUG)
	rospy.Subscriber('base_scan', LaserScan, callback)
	pub = rospy.Publisher('cmd_vel', Twist, queue_size=100)
	rospy.spin()
