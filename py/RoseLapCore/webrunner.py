import sys,os,traceback,inspect
# sys.stdout = open('c:/wamp/www/RoseLap/py/, 'w')
# print("hi mom")
sys.path.append(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))) + '/../')
import config

import logging,time
unique_id = str(time.time()).split(".")[0]
log_dir = config.file_dir + '/py/RoseLapCore/logs/' + unique_id + '.log'
log_path = config.web_dir + '/py/RoseLapCore/logs/' + unique_id + ".log"
logging.basicConfig(filename=log_dir, level=logging.DEBUG, format='%(asctime)-15s | %(levelname)-8s: %(message)s')

logging.info("start of log")

try:
    import input_processing
    import batcher
    import packer
    import MySQLdb as sql
    from RoseLapCharter import dashboarder
except:
    err = traceback.format_exc()
    logging.exception(err)

    # cur.execute("CALL run_Fail_Batch_Run(%s, %s, %s)", [runID, log_path, err])
    # db.commit()
    exit()

if __name__ == "__main__":
    try:
        runID = sys.argv[1]
        bcID = sys.argv[2]

        db = sql.connect("localhost", "rlapp", "gottagofast", "roselap")
        cur = db.cursor()

        # cur.execute("SELECT run_Get_Next_Batch_Run()")
        # ids = cur.fetchall()[0][0]
        # logging.debug("IDs: %s" % repr(ids))

        # r, b = ids.strip().split('|')
        # runID = int(r)
        # bcID = int(b)

        cur.execute("SELECT BCText, Name FROM batch_config WHERE BCID = %s", [bcID])
        cfa = cur.fetchall()
        logging.debug("bcNames: %s" % repr([a[1] for a in cfa]))
        bcText, bcName = cfa[0]

        cur.execute("CALL run_Process_Batch_Run(%s, %s)", [runID, log_path])
        db.commit()

        logging.info("starting up...")
    except:
        err = traceback.format_exc()
        logging.exception(err)

        # cur.execute("CALL run_Fail_Batch_Run(%s, %s, %s)", [runID, log_path, err])
        # db.commit()
        exit()

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
        
        display_dir = config.file_dir + "/graph/" + unique_id
        os.makedirs(display_dir)
        display_link = config.web_dir + "/graph/" + unique_id + "/" + bcName + "-dashboard.php"

        logging.info('done batching!')
    except Exception:
        err = traceback.format_exc()
        logging.exception(err)

        cur.execute("CALL run_Fail_Batch_Run(%s, %s, %s)", [runID, log_path, err])
        db.commit()
        exit()

    try:
        logging.info('charting...')
        dashboarder.make_dashboard(results, bcName, display_dir)
        logging.info('charted!')

        cur.execute("CALL run_Finish_Batch_Run(%s, %s, %s)", [runID, result_path, display_link])
        db.commit()
    except:
        err = traceback.format_exc()
        logging.exception(err)

        cur.execute("CALL run_Fail_Batch_Run(%s, %s, %s)", [runID, log_path, err])
        db.commit()