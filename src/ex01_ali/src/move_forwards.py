#! /usr/bin/env python 

import rospy
import math
from random import randint
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan

def callback( sensor_data ):
	base_data = Twist()

	object_there_straight = False
	object_there_left = False
	object_there_right = False

	sum_right = 0
	sum_left = 0
	sum_straight = 0
	av_right = 0
	av_left = 0
	av_straight = 0
	inf_left = 0
	inf_right = 0
	inf_straight = 0

	number_of_loops = 0	

	counter = len(sensor_data.ranges)
	left_threshold = 2 * ((counter-1)/3)
	straight_threshold = ((counter - 1)/3)
	
	#furthest right distance
	#sensor_data.ranges[0]
	#furthest left distance
	#sensor_data.ranges[counter-1]
	
	for x in sensor_data.ranges:
		if number_of_loops < straight_threshold:
			if 0 < x <= 5.59999990463:
				sum_right = sum_right + x
			if x > 5.59999990463:
				inf_right = inf_right + 1
				sum_right = sum_right + 7#5.59999990463
			if x < 0.5:
				object_there_right = True
		elif number_of_loops < left_threshold:
			if 0 < x <= 5.59999990463:
				sum_straight = sum_straight + x
			if  x > 5.59999990463:
				inf_straight = inf_straight + 1
				sum_srtaight = sum_straight + 7 #5.59999990463
			if x < 0.5:
				object_there_straight = True
		else:
			if 0 < x <= 5.59999990463:
				sum_left = sum_left + x
			if  x > 5.59999990463:
				inf_left = inf_left + 1
				sum_left = sum_left + 7 #5.59999990463
			if x < 0.5:
				object_there_left = True
		number_of_loops = number_of_loops + 1

	av_left = sum_left / ((counter - 1)/3)
	av_right = sum_right / ((counter - 1)/3)
	av_straight = sum_straight / ((counter - 1)/3)
	
	base_data.linear.x = 0.25

	if object_there_straight:
		print "Object Ahead. Turning"
		base_data.angular.z = 0.5
		base_data.linear.x = 0
	elif object_there_right:
		print "Object Right. Turning"
		base_data.angular.z = 0.5
		base_data.linear.x = 0
	elif object_there_left:
		print "Object Left. Turning"
		base_data.angular.z = -0.5
		base_data.linear.x = 0
	else:
		
	
		turn_speed = 1
		#Compare
		print "Comparing"
		if av_left > av_right and av_left > av_straight:
			#Turn Left
			print "Left"
			base_data.angular.z = turn_speed
		elif av_right > av_straight:
			#Turn Right
			print "Right"
			base_data.angular.z = -turn_speed#0.25	
		else:	
			#Straight
			print "Straight"

	pub.publish( base_data )
	print av_straight
	print av_left
	print av_right
	print "==="
	print sum_straight
	print sum_left
	print sum_right
	print "==="
	print inf_straight
	print inf_left
	print inf_right
	print "--------------------------------"
	

if __name__ == '__main__':
	rospy.init_node('move_forwards')
	rospy.Subscriber('base_scan', LaserScan, callback)
	pub = rospy.Publisher('cmd_vel', Twist, queue_size=0.500)
	rospy.spin()
