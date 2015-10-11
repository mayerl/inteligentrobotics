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

kDistanceToWall = 0.5
kSideSamples = 50
kLinearSpeed = 0.2
kAngularSpeed = 0.3

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
	rospy.init_node('reactive_mover_node',log_level=rospy.DEBUG)
	rospy.Subscriber('base_scan', LaserScan, callback)
	pub = rospy.Publisher('cmd_vel', Twist, queue_size=100)
	rospy.spin()
