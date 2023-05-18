"""
.. module:: subscriber
   :platform: Unix
   :synopsis: Python node that implements a subscriber.
   .. moduleauthor:: Claudio Demaria (S5433737)

   This node implements a subscriber to the custom topic /my_pos_vel that prints the distance from the desired position and the average speed of the robot, 
   using a particular frequency passed as a ROS parameter.

   Parameters:
   publish_frequency (double)

   Subscribers:
   /my_pos_vel
"""

import rospy
import math
import time

# Import my custom message defined in the /msg folder inside the 'assignment_2_2022' package
from assignment_2_2022.msg import My_pos_vel

freq = rospy.get_param("publish_frequency")
""" Variable to store the frequency of the printed information, passed as a ROS parameter
"""
dist = 0
""" Variable to store the distance between the robot and the desired position
"""
vel = 0
""" Variable to store the current velocity of the robot
"""


def callback(msg):
	"""
	Callback of the subscriber to the /my_pos_vel custom topic.
	It computes the distance between the robot and the desired position and the average speed of the robot.
	
	Args:
	msg(My_pos_vel): two variables for the position of the robot (*x* and *y*) and two for the robot's velocities (*vel_x* and *vel_y*) 
	"""
	global dist
	global vel
	# Retrieve the desired position
	x_desired = rospy.get_param("des_pos_x")
	y_desired = rospy.get_param("des_pos_y")
	# Retrieve the actual position
	x = msg.x
	y = msg.y
	# Compute the distance
	dist = math.dist([x_desired, y_desired], [x, y])
	# Compute the average speed
	vel = math.sqrt(msg.vel_x**2 + msg.vel_y**2)
	
def print_message():
	"""
	Function that prints the distance from the desired position and the current average speed of the robot.
	"""
	global dist
	global vel
	# Print the info
	print("Distance from the desired position: {:.2f}".format(dist))
	print("Average speed: {:.2f}".format(vel))
	print()
	

if __name__ == '__main__':
	"""
	This function initializes the ROS node and the subscriber to the */my_pos_vel* topic.
	It also set the ROS rate imported as a ROS parameter, in order to print the information at a given frequency.
	"""
	try:
		# Initialize the rospy node
		rospy.init_node('subscriber')
		# Inizialize the subscriber to the /my_pos_vel topic
		# In the callback, we calculate distance and average speed, and print the results 
		subscriber = rospy.Subscriber("/my_pos_vel", My_pos_vel, callback)
		# For setting the frequency imported from the launch file, set the ROS rate
		rate = rospy.Rate(freq)
		while not rospy.is_shutdown():
			print_message()
			rate.sleep()
	except rospy.ROSInterruptException:
		print("\n Program interrupted before completion", file=sys.stderr)
