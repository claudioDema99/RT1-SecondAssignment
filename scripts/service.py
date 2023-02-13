#! /usr/bin/env python

import rospy
import assignment_2_2022.msg

# Import my custom service defined in the /srv folder inside the 'assignment_2_2022' package
from assignment_2_2022.srv import Goals_number, Goals_numberResponse

# Initialize counters for the goals cancelled/reached
cancelled = 0
reached = 0

# Callback for result subscriber
def callback_result(msg):
	global cancelled
	global reached
	
	# Get the status of the result
	status = msg.status.status
	
	# If status is 2, the goal was preempted
	if status == 2:
		cancelled += 1
	# If status is 3, the goal was reached
	elif status == 3:
		reached += 1
		
# Service function
def goals(req):
	global cancelled
	global reached
	
	# Print (and return) the number of goals reached and cancelled
	print(f"\n\n Number of goals reached: {reached}")
	print(f" Number of goals cancelled: {cancelled}")
	return Goals_numberResponse(reached, cancelled)

if __name__ == '__main__':
	try:
		# Initialize the rospy node
		rospy.init_node('service')
		# Initialize the service
		srv = s = rospy.Service('goals_number', Goals_number, goals)
		# Need to have the result topic
		sub_result = rospy.Subscriber('/reaching_goal/result', assignment_2_2022.msg.PlanningActionResult, callback_result)
		
		rospy.spin()
	except rospy.ROSInterruptException:
		print("\n Program interrupted before completion", file=sys.stderr)
