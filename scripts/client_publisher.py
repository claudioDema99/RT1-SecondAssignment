"""
.. module:: client_publisher
   :platform: Unix
   :synopsis: Python node that implements an action client, a publisher and a subscriber.
   .. moduleauthor:: Claudio Demaria (S5433737)

   This node implements an action client to the /reaching_goal topic in order to use a bug_as alghorithm to reach a desired position inside the environment.
   To do that, this node needs to subscribe to the /odom topic for knowing the robot current position. This node also publishes the current position and velocity 
   of the robot with a custom topic named /my_pos_vel. 

   Subscribers:
   /odom
   /reaching_goal/result  

   Publishers:
   /my_pos_vel

   Action clients:
   /reaching_goal
"""

import rospy
from geometry_msgs.msg import Point, Pose, Twist
from nav_msgs.msg import Odometry
import math
import actionlib
import actionlib.msg
import assignment_2_2022.msg
from std_srvs.srv import *
import time
import sys
import select
import os


# Import my custom message defined in the /msg folder inside the 'assignment_2_2022' package
from assignment_2_2022.msg import My_pos_vel
# Import my custom service defined in the /srv folder inside the 'assignment_2_2022' package
from assignment_2_2022.srv import Goals_number, Goals_numberRequest, Goals_numberResponse

goal_reached = False
""" Variable to know if the goal has been reached
"""

def callback_and_publish(msg):
	"""
	Callback of the subscriber to the \odom topic (and it also publish the custom message inside this callback) 
	
	Args:
	msg(Pose): the robot's current position
	"""
	# Get the position from the msg
	position_ = msg.pose.pose.position
	# Get the twist from the msg
	vel_lin = msg.twist.twist.linear
	# Create custom message
	pos_vel = My_pos_vel()
	pos_vel.x = position_.x
	pos_vel.y = position_.y
	pos_vel.vel_x = vel_lin.x
	pos_vel.vel_y = vel_lin.y
	# Publish the custom message
	publisher.publish(pos_vel)
	
def callback_result(msg):
	"""
	Callback of the subscriber to the /reaching_goal/result topic.
	It set the value of the boolean variable *goal_reached* in order to know that the goal has been reached.
	
	Args:
	msg(PlanningActionResult): the status of the result
	"""
	global goal_reached
	status = msg.status.status
	# If status = 3, the goal is reached
	if status == 3:
		goal_reached = True
		
def call_custom_server():
    """
    Function that calls the custom service for printing the number of goal reached and cancelled.
    """
    # Wait for the service to become available
    rospy.wait_for_service('goals_number')
    try:
        # Create a handle to the service
        goal_service = rospy.ServiceProxy('goals_number', Goals_number)
        
        # Create a request object
        request = Goals_numberRequest()
        
        # Send the request to the service
        response = goal_service(request)
    except rospy.ServiceException as e:
        print("\n Service call failed: %s" % e)
		

def target_goal():
	"""
	Function that manages the phases of the program:
	State 0 - Robot is stopped and waiting for a target goal;
	State 1 - Robot is reaching the goal and it can be stopped if the user cancel the goal, or the goal can be reached;
	State 2 - The goal is canceled by the user or is reached by the robot;
	"""

	flag = 0
	"""
	Flag variable to move between the states of the program.
	"""
	
	printed = False
	"""
	Boolean variable used to print a string only the first time inside a loop.
	"""
	
	global goal_reached
	"""
	Boolean variable used to know if the goal has been reached.
	"""
	
	# Messages to print in the different states
	message_0 = "\n\n Insert the target position.\n Enter 2 number for the x and y value, separated by a coma: [x, y]  "
	message_2 = "\n\n The goal has been canceled.\n Do you want to reach an other point? [Y/n]  "
	message_3 = "\n\n The goal has been reached!\n Do you want to reach an other point? [Y/n]  "
	message_killer = "\n\n\n Killing all nodes.. Goodbye!\n\n"
	
	while not rospy.is_shutdown():
		if flag == 0:
			# Waiting the target input by the user
			target_input = input(message_0)
			
			# Extract the x and y value from the string
			target_input = target_input.replace(" ","")
			target = target_input.split(",")
			x = float(target[0])
			y = float(target[1])
			
			# Create the goal to send to the server
			goal = assignment_2_2022.msg.PlanningGoal()
			goal.target_pose.pose.position.x = x
			goal.target_pose.pose.position.y = y
			
			# Send the goal to the action server
			client.send_goal(goal)
			
			# Go to the second state
			flag = 1
		elif flag == 1:
			# Print only 1 time
			if not printed:
				#time.sleep(0.1)
				print(f"\n\n The robot is reaching the position: {x}, {y} \n If you want to cancel the actual goal, enter 'c'  ")
				printed = True
			
			# Check continously if the user cancel the goal..
			cancel_input = select.select([sys.stdin], [], [], 1)[0]
			
			# If user cancel the goal
			if cancel_input:
				# Get the input string
				user_string = sys.stdin.readline().rstrip()
				user_string = user_string.replace(" ","")
				if user_string == "c":
					# Cancel the goal and go to the third state
					client.cancel_goal()
					flag = 2
			# Manca un if il goal è stato raggiunto..
			if goal_reached:
				flag = 2
		elif flag == 2:
			# Reset the printed to false
			printed = False
			# Call the custom service to print (on an other screen) the number of goals reached/cancelled
			time.sleep(1)
			call_custom_server()
			
			# Let the user the choice to set an other target or to quit
			if goal_reached:
				last_input = input(message_3)
			else:
				last_input = input(message_2)
			last_input = last_input.replace(" ","")
			last_input = last_input.lower()
			if last_input == "y":
				flag = 0
				goal_reached = False
			elif last_input == "n":
				print(message_killer)
				nodes = os.popen("rosnode list").readlines()
				for i in range(len(nodes)):
					nodes[i] = nodes[i].replace("\n","")
				for node in nodes:
					os.system("rosnode kill "+ node)

def client():
	"""
	Function that creates the action client and calls the function *target_goal* that manages the phases of the program.
	"""
	# Create the action client
	global client
	client = actionlib.SimpleActionClient('/reaching_goal', assignment_2_2022.msg.PlanningAction)
	# Wait for the server to be started
	client.wait_for_server()
	
	# Call the function that manages all the robot's action
	target_goal()

if __name__ == '__main__':
	"""
	This function initializes the ROS node, a publisher for the custom message /my_pos_vel, and two subscribers: one for the /odom topic and another for the /reaching_goal/result topic.
	In the end it calls a function that creates an action client for the /reaching_goal topic and calls a function that manages the logic of the program.
	"""
	try:
		# Initialize the rospy node
		rospy.init_node('client_publisher')
		# Inizialize the (global) publisher of the custom message (publish into the subscriber's callback)
		global publisher
		publisher = rospy.Publisher("/my_pos_vel", My_pos_vel, queue_size=1)
		# Inizialize the subscriber to the /odom topic
		# In the callback, we calculate postion and velocity, and also publish the custom message with the publisher (global) 
		subscriber = rospy.Subscriber("/odom", Odometry, callback_and_publish)
		# I also need to know the result topic, in order to ask at the user an other target goal
		sub_result = rospy.Subscriber('/reaching_goal/result', assignment_2_2022.msg.PlanningActionResult, callback_result)
		# Initialize the client and call the function that manages all the programs (target_goal)
		client()
	except rospy.ROSInterruptException:
		print("\n Program interrupted before completion", file=sys.stderr)
