#! /usr/bin/env python
# This basic node subscribes to incoming laser and sonar messages,
# decides what to do based on the incoming data, then publishes
# movement commands to the robot.

# Remember to comment your code so your team mates can understand it!

# @author Claudio Zito, Marco Becerra
import rospy
import random
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan

gStartCollision = False
gTurnDirection = 0

def callback( sensor_data ):
	global gStartCollision
	global gTurnDirection
	#sensor_data (LaserScan data type) has the laser scanner data
	#base_data (Twist data type) created to control the base robot
	collision = False
	leftMean = 0
	leftSamples = 0
	rightMean = 0
	rightSamples = 0
	base_data = Twist()
	
	for index in range(len(sensor_data.ranges)):
		if index < len(sensor_data.ranges)/2:
			leftMean = leftMean + sensor_data.ranges[index]
			leftSamples = leftSamples + 1
		else:
			rightMean = rightMean + sensor_data.ranges[index]
			rightSamples = rightSamples + 1

		if sensor_data.ranges[index] < 0.3:
			collision = True

	leftMean = leftMean / leftSamples
	rightMean = rightMean / rightSamples

	if collision:
		if gStartCollision == False:
			if leftMean > rightMean:
				gTurnDirection = -1
			else:
				gTurnDirection = 1
			gStartCollision = True

		base_data.angular.z = 0.5 * gTurnDirection
		if gTurnDirection: 
			direction = "RIGHT" 
		else: 
			direction = "LEFT"
		rospy.loginfo("Wall ahead. Turning " + direction)
	else:
		gStartCollision = False
		base_data.linear.x = 0.2
		rospy.loginfo("Going straight");	
	
        pub.publish( base_data  )

if __name__ == '__main__':
	rospy.init_node('reactive_mover_node',log_level=rospy.DEBUG)
	rospy.Subscriber('base_scan', LaserScan, callback)
	pub = rospy.Publisher('cmd_vel', Twist, queue_size=100)
	rospy.spin()
