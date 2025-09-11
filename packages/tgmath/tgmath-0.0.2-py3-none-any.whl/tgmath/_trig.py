import math

RADIANS = 0
DEGREES = 1

ANGLE_MODE = DEGREES
'''
Setting the angle mode will change the returned values from the functions.
'''

DEG2RAD = 3.14159 / 180
RAD2DEG = 180 / 3.14159

def degrees(r):
	'''
	Converts 'r' from radians to degrees.
	Equivilant to 'r * tmath.RAD2DEG'
	'''
	return r * RAD2DEG
def radians(d):
	'''
	Converts 'd' from degrees to radians.
	Equivilant to 'd * tmath.DEG2RAD'
	'''
	return d * DEG2RAD

def set_angle_mode(angle_mode):
	'''
	Sets the angle mode to dictate the return value of other trig functions.
	Options are 'tmath.RADIANS' or 'tmath.DEGREES'

	Equivilant to setting it directly: 'tmath.ANGLE_MODE = angle_mode'
	'''
	global ANGLE_MODE
	ANGLE_MODE = angle_mode


def sin(a):
	a *= DEG2RAD if ANGLE_MODE else 1
	return math.sin(a)

def cos(a):
	a *= DEG2RAD if ANGLE_MODE else 1
	return math.cos(a)

def tan(a):
	a *= DEG2RAD if ANGLE_MODE else 1
	return math.tan(a)

def asin(v):
	a = math.asin(v)
	a *= RAD2DEG if ANGLE_MODE else 1
	return a

def acos(v):
	a = math.acos(v)
	a *= RAD2DEG if ANGLE_MODE else 1
	return a

def atan(v):
	a = math.atan(v)
	a *= RAD2DEG if ANGLE_MODE else 1
	return a

def atan2(y, x):
	a = math.atan2(y, x)
	a *= RAD2DEG if ANGLE_MODE else 1
	return a