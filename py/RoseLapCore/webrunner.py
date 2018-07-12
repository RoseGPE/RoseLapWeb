import sys,os,traceback
sys.path.append('C:\wamp\www\RoseLap\py')

import logging
logging.basicConfig(filename='logs/temp.log', level=logging.INFO)

import input_processing
import batcher
import packer
import MySQLdb as sql
import time
from RoseLapCharter import dashboarder

if __name__ == "__main__":
	db = sql.connect("localhost", "rlapp", "gottagofast", "roselap")
	cur = db.cursor()

	cur.execute("SELECT run_Get_Next_Batch_Run()")
	ids = cur.fetchall()[0][0]

	r, b = ids.strip().split('|')
	runID = int(r)
	bcID = int(b)

	cur.execute("SELECT BCText, Name FROM batch_config WHERE BCID = %s", [bcID])
	bcText, bcName = cur.fetchall()[0]

	cur.execute("CALL run_Process_Batch_Run(%s)", [runID])
	db.commit()

	try:
		conf = input_processing.process_web_config(bcText)

		cur.execute("SELECT VehicleText FROM vehicle_config WHERE Name = %s", [conf.vehicle])
		conf.vehicle = cur.fetchall()[0][0]

		for i, track in enumerate(conf.tracks):
			logging.info(track.__dict__)
			cur.execute("SELECT Path FROM track_config WHERE Name = %s", [track.file])
			conf.tracks[i].path = cur.fetchone()[0]
		
		tests, vehicle, tracks, model, out = input_processing.process_web_input(conf)

		logging.info('batching...')
		results = batcher.batch(tests, vehicle, tracks, model, out[1] != 0)

		logging.info('packing...')
		result_path = packer.pack(results, out[0])

		unique_id = str(time.time()).split(".")[0]
		log_path = 'http://rosegpe.ddns.net/RoseLap/py/RoseLapCore/logs/' + unique_id + ".log"
		
		display_path = "../../graph/" + unique_id
		os.makedirs(display_path)
		display_link = "http://rosegpe.ddns.net/RoseLap/graph/" + unique_id + "/" + bcName + "-dashboard.php"

		cur.execute("CALL run_Finish_Batch_Run(%s, %s, %s, %s)", [runID, result_path, log_path, display_link])
		db.commit()

		logging.info('charting...')

		dashboarder.make_dashboard(results, bcName, display_path)

		logging.info('done!')
	except Exception:
		err = traceback.format_exc()
		logging.exception(err)

		cur.execute("CALL run_Fail_Batch_Run(%s, %s, %s)", [runID, log_path, err])
	 	db.commit()

 	with open("logs/temp.log", "r+") as temp:
		with open("logs/" + unique_id + ".log", "w") as log:
			log.write(temp.read())
		temp.truncate(0)
