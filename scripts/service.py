"""
.. module:: service
   :platform: Unix
   :synopsis: Python node that implements a custom service and a subscriber.
   .. moduleauthor:: Claudio Demaria (S5433737)

   This node implements a custom service that updates counters each time an actionLib goal is reached or cancelled. It subscribes to the /reaching_goal/result topic.

   Subscribers:
   /reaching_goal/result

   Services:
   /goals_number
"""

import rospy
import assignment_2_2022.msg

# Import my custom service defined in the /srv folder inside the 'assignment_2_2022' package
from assignment_2_2022.srv import Goals_number, Goals_numberResponse

cancelled = 0
""" Counter variable to store the number of goals cancelled
"""
reached = 0
""" Counter variable to store the number of goals reached
"""

# Callback for result subscriber
def callback_result(msg):
	"""
	Callback of the subscriber to the /reaching_goal/result topic.
	It increases the correspondive counters.
	
	Args:
	msg(PlanningActionResult): the status of the result
	"""
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
	"""
	Service function that prints and returns the number of goals reached and cancelled
	"""
	global cancelled
	global reached
	
	# Print (and return) the number of goals reached and cancelled
	print(f"\n\n Number of goals reached: {reached}")
	print(f" Number of goals cancelled: {cancelled}")
	return Goals_numberResponse(reached, cancelled)

if __name__ == '__main__':
	"""
	This function initializes the ROS node and the service *goals_number*.
	It also subscribes to the /reaching_goal/result topic in order to get the status of the result once a goal has been reached or cancelled.
	"""
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
