import sys,os
sys.path.append(os.path.dirname(__file__))

import input_processing
import batcher
import packer
import MySQLdb as sql

if __name__ == "__main__":
	db = sql.connect("localhost", "rlapp", "gottagofast", "roselap")
	cur = db.cursor()

	cur.execute("SELECT run_Get_Next_Batch_Run()")
	ids = cur.fetchall()[0][0]

	r, b = ids.strip().split('|')
	runID = int(r)
	bcID = int(b)

	cur.execute("SELECT BCText FROM batch_config WHERE BCID = %s", [bcID])
	bcText = cur.fetchall()[0][0]

	cur.execute("CALL run_Process_Batch_Run(%s)", [runID])
	db.commit()

	conf = input_processing.process_web_config(bcText)

	cur.execute("SELECT VehicleText FROM vehicle_config WHERE Name = %s", [conf.vehicle])
	conf.vehicle = cur.fetchall()[0][0]

	for i, track in enumerate(conf.tracks):
		cur.execute("SELECT Path FROM track_config WHERE Name = %s", [track.dxf])
		conf.tracks[i].dxf = cur.fetchone()[0]
	
	tests, vehicle, tracks, model, out = input_processing.process_web_input(conf)

	print('batching...')
	results = batcher.batch(tests, vehicle, tracks, model, out[1] != 0)

	print('packing...')
	result_path = packer.pack(results, out[0])

	cur.execute("CALL run_Finish_Batch_Run(%s, %s)", [runID, result_path])
	print runID
	print cur.fetchall()
	db.commit()

	print('charting...')

	# make charting work

	print('done!')
