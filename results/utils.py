abbr_to_full_dict = {'calc' : 'Calculus', 'calc1' : 'Calculus 1', 'calc2' : 'Calculus 2', 
		'stats' : 'Statistics', 'precalc' : 'Precalculus', 'alg2' : 'Algebra 2', 'alg1' : 'Algebra 1',
		'geo' : 'Geometry', 'theta' : 'Theta', 'alpha' : 'Alpha', 'mu': 'Mu', 'open': 'Open'}

month_number = {1 : 'January', 2 : 'February', 3 : 'March', 4 : 'April', 5 : 'May', 
				6 : 'June', 7 : 'July', 8 : 'August', 9 : 'September', 10 : 'October',
				11 : 'November', 12 : 'December'}

month_full_name = {'jan' : 'January', 'feb' : 'February', 'mar' : 'March', 'apr' : 'April', 
					'may' : 'May', 'Jun' : 'June', 'Jul' : 'July', 'Aug' : 'August',
					'sept' : 'September', 'oct' : 'October', 'nov' : 'November', 'dec' : 'December',}

full_to_abbr_dict = {v: k for k, v in abbr_to_full_dict.items()}

name_to_number_dict = {v: k for k, v in month_number.items()}

full_to_abbr_month = {v: k for k, v in month_full_name.items()}

def get_full_division(div_name):
	return abbr_to_full_dict.get(div_name, div_name)

def get_division_abbr(full_name):
	return full_to_abbr_dict.get(full_name, full_name)

def get_name_month(month_num):
	return month_number[month_num]

def get_num_month(month_num):
	return name_to_number_dict[month_num]

def get_full_month(month_abbr):
	return month_full_name[month_abbr]

def get_month_abbr(month_full):
	return full_to_abbr_month[month_full]