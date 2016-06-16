abbr_to_full_dict = {'calc' : 'Calculus', 'calc1' : 'Calculus 1', 'calc2' : 'Calculus 2', 
		'stats' : 'Statistics', 'precalc' : 'Precalculus', 'alg2' : 'Algebra 2', 'alg1' : 'Algebra 1',
		'geo' : 'Geometry', 'theta' : 'Theta', 'alpha' : 'Alpha'}

month_number = {1 : 'January', 2 : 'February', 3 : 'March', 4 : 'April', 5 : 'May', 
				6 : 'June', 7 : 'July', 8 : 'August', 9 : 'September', 10 : 'October',
				11 : 'November', 12 : 'December'}

full_to_abbr_dict = {v: k for k, v in abbr_to_full_dict.items()}

name_to_number_dict = {v: k for k, v in month_number.items()}

def get_full_division(divName):
	return abbr_to_full_dict[divName]

def get_division_abbr(fullName):
	return full_to_abbr_dict[fullName]

def get_name_month(monthNum):
	return month_number[monthNum]

def get_num_month(monthNum):
	return name_to_number_dict[monthNum]