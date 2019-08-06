
import re
def time_to_seconds(t):
	#read in time in format hh:mm:ss, convert to # of seconds (since midnight)
	time=re.split(r":",t)
	time=[int(i) for i in time]
	return time[0]*3600+time[1]*60+time[2]




