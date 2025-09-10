from datetime import datetime
def timenow():
	current_datetime = datetime.now()

	# Extract and format the time portion
	current_time = current_datetime.strftime("%H:%M:%S")

	# Print the formatted current time
	print("Current Time =", current_time)
	print("finished")
