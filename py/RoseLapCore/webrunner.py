import sys,os,traceback
sys.path.append('C:\wamp\www\RoseLap\py')

import input_processing
import batcher
import packer
import MySQLdb as sql
import time
from RoseLapCharter import dashboarder

if __name__ == "__main__":
	db = sql.connect("localhost", "rlapp", "gottagofast", "roselap")
	cur = db.cursor()

	# cur.execute('''UPDATE batch_run
	# SET Status = 'Queued'
	# WHERE RunID = 113''')
	# db.commit()

	cur.execute("SELECT run_Get_Next_Batch_Run()")
	ids = cur.fetchall()[0][0]

	r, b = ids.strip().split('|')
	runID = int(r)
	bcID = int(b)

	cur.execute("SELECT BCText FROM batch_config WHERE BCID = %s", [bcID])
	bcText = cur.fetchall()[0][0]

	cur.execute("CALL run_Process_Batch_Run(%s)", [runID])
	db.commit()

	# try:
	conf = input_processing.process_web_config(bcText)

	cur.execute("SELECT VehicleText FROM vehicle_config WHERE Name = %s", [conf.vehicle])
	conf.vehicle = cur.fetchall()[0][0]

	for i, track in enumerate(conf.tracks):
		print(track.__dict__)
		cur.execute("SELECT Path FROM track_config WHERE Name = %s", [track.file])
		conf.tracks[i].path = cur.fetchone()[0]
	
	tests, vehicle, tracks, model, out = input_processing.process_web_input(conf)

	print('batching...')
	results = batcher.batch(tests, vehicle, tracks, model, out[1] != 0)

	print('packing...')
	result_path = packer.pack(results, out[0])
	display_name = str(time.time()).split(".")[0]
	display_path = "http://rosegpe.ddns.net/RoseLap/graph/" + display_name
	display_link = display_path + "/" + display_name + "-dashboard.php"

	cur.execute("CALL run_Finish_Batch_Run(%s, %s, %s)", [runID, result_path, display_link])
	db.commit()

	print('charting...')

	print(display_name)
	dashboarder.make_dashboard(results, display_name)

	print('done!')
	# except Exception:
	# 	cur.execute("CALL run_Fail_Batch_Run(%s, %s)", [runID, traceback.format_exc()])
	#  	db.commit()