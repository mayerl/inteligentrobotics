#! /usr/bin/env python

import rospy
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan

def normalise( sensor_data ):
    ranges = []
    for i in range(0, len(sensor_data.ranges) - 1):
        total = 0
        max = i + 2
        min = i - 2

        if max > len(sensor_data.ranges) - 1 :
            max = len(sensor_data.ranges) - 1

        if min < 0 :
            min = 0

            count = max - min
        total = 0
        for j in range(min, max) :
            if (j > sensor_data.range_min) | (j < sensor_data.range_max):
                total = total + sensor_data.ranges[j]

            ranges.append(total / count)

    return ranges

def is_collision(ranges) :
    total = 0
    for r in range((len(ranges) / 2) - 2, (len(ranges) / 2) + 2):
        total = total + ranges[r]

    return (total / 5) < 2

class MVector :
    def __init__(self, magnitude, direction) :
        self.magnitude = magnitude
        self.direction = direction
    def getMagnitude(self):
        return self.magnitude
    def getDirection(self):
        return self.direction

def callback( sensor_data ) :
    #sensor_data (LaserScan data type) has the laser scanner data
    #base_data (Twist data type) created to control the base robot
    speed = 0.4
    orientation = 0
    angle = 0

    base_data = Twist()

    ranges = normalise( sensor_data )

    if is_collision(ranges) :
        base_data.linear.x = 0
        base_data.angular.z = 10
        orientation = (orientation + 10) % 360
        angle = (angle + 10) % 360
        pub.publish(base_data)
    else :
        base_data.linear.x = speed
        base_data.angular.z = 0
        
        angle = 0
        pub.publish(base_data)





if __name__ == '__main__':
    rospy.init_node('testing')
    rospy.Subscriber('base_scan', LaserScan, callback)
    pub = rospy.Publisher('cmd_vel', Twist, queue_size=100)
    rospy.spin()
