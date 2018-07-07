def compute_points(event_name, best_time, best_co2, times, co2s):
	if event_name == 'acceleration':
		return 95.5*(best_time*1.5/times - 1)/(1.5-1) + 4.5
	if event_name == 'acceleration_double':
		return 2*(95.5*(best_time*1.5/times - 1)/(1.5-1) + 4.5)
	if event_name == 'skidpad':
		return 71.5*((best_time*1.45/times)**2 - 1)/(1.45**2-1) + 3.5
	if event_name == 'autocross':
		return 118.5*(best_time*1.45/times - 1)/(1.45-1) + 6.5
	if event_name == 'skidpad_double':
		return 2*(71.5*((best_time*1.45/times)**2 - 1)/(1.45**2-1) + 3.5)
	if event_name == 'endurance_noeff':
		score_end= 250*(best_time*1.45/times - 1)/(1.45-1) + 25
		return score_end
	if event_name == 'endurance':
		EFi = best_time/times*best_co2/co2s
		EFmin = .25 # TODO? close enough
		EFmax = .80 # TODO? close enough
		score_end= 250*(best_time*1.45/times - 1)/(1.45-1) + 25
		score_eff= 100*(EFmin/EFi-1)/(EFmin/EFmax-1)
		return score_end #+score_eff