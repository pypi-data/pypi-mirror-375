import math



def floor(v, cast=int):
	'''
	Returns the largest integer smaller than 'v', cast into the provided type.
	'''
	return cast(math.floor(v))

def ceil(v, cast=int):
	'''
	Returns the smallest integer larger than 'v', cast into the provided type.
	'''
	return cast(math.ceil(v))


def clamp(v, _min, _max):
	'''
	Clamps 'v' to between the range of '_min' and '_max'
	'''
	return min(max(v, _min), _max)
