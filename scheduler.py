#!/usr/bin/python3

import database as db
import socket
import time
import multiprocessing as mp
import sys
import os
import enhanced_yaml as yaml
import json as json
import traceback
from sim.track import Track
from sim.vehicle import Vehicle

def run(study_id):
  print("#### scheduler.run(study_id=%d) STARTED ####" % study_id)

  db_session = db.scoped_session(db.sessionmaker(bind=db.engine))
  stdout = None
  try:
    study = db_session.query(db.Study).filter(db.Study.id == study_id).first()

    ## Set up folder for study and redirect print statements to a log file there
    folder = "studies/"+str(study_id)
    if not os.path.exists(folder):
      os.makedirs(folder)
    stdout = sys.stdout = open(folder+"/log.log", 'w')

    print("#### scheduler.run(study_id=%d) STARTED ####" % study_id)
    print()

    ## Parse inputs from study

    print("------- Study Inputs -------")
    print("Fulltext of Study Specification: ", study.filedata)

    # Load spec from study
    spec = yaml.load(study.filedata)

    # Grab latest versions of vehicle and tracks used, set their status to used
    db_vehicle = db_session.query(db.Vehicle).filter(db.Vehicle.name == spec.vehicle).order_by(db.Vehicle.version.desc()).first()
    db_vehicle.status = db.STATUS_SUBMITTED
    vehicle = Vehicle(db_vehicle.filedata, 'yaml') # core vehicle object used in sim

    # Sort tracks by version (highest first). Then sort out each track uniquely
    raw_tracks = db_session.query(db.Track).filter(db.Track.name.in_(spec.tracks)).order_by(db.Track.version.desc()).all()
    db_tracks = []
    tracks    = []
    track_names = []
    for track in raw_tracks:
      if not track.name in track_names:
        track_names.append(track.name)
        db_tracks.append(track)
        tracks   .append(Track(track.filedata, track.filetype, track.unit))
        track.status = db.STATUS_SUBMITTED

    print("Vehicle: ", repr(db_vehicle))
    print("Tracks: ", repr(db_tracks))
    print("Sweeps: ", repr(spec.sweeps))
    print("Model: ", repr(spec.model))
    print("")

    # Figure out how many runs will happen in all (assume no searching)
    study.runs_total    = 1
    study.runs_complete = 0
    for axis in spec.sweeps:
      for variable in axis.variables:
        if type(variable.values) == type({}):
          variable.values = np.linspace(variable.values.start, variable.values.end, variable.values.length).tolist()
      study.runs_total *= len(axis.variables[0].values)

    print("Run size is %d runs." % study.runs_total)

    # Study actually runs from here; commit everything to the database
    study.run()
    db_session.commit()

    ## Dispatch workers to compute results

    ## Create a manifest file
    print("------ Building Manifest ------")
    manifest = {
      "study": study.as_dict(),
      "vehicle": db_vehicle.as_dict(),
      "tracks":  [track.as_dict() for track in db_tracks]
    }
    # TODO: Fully build manifest
    # TODO: Track / vehicle filedata store in external files
    with open(folder+"/manifest.json", "w") as f:
      f.write(json.dumps(manifest))
    print("Manifest saved.")

    print("#### scheduler.run(study_id=%d) FINISHED ####" % study_id)

    study.finish(db.STATUS_SUCCESS)
    db_session.commit()
  except:
    if stdout:
      sys.stdout = stdout
      
    print("#### scheduler.run(study_id=%d) ERROR ####" % study_id)
    traceback.print_exc()
    study.finish(db.STATUS_FAILURE)
    db_session.commit()


if __name__ == "__main__":
  db_session = db.scoped_session(db.sessionmaker(bind=db.engine))
  processes = []
  while True:
    time.sleep(1)
    queued_studies = db_session.query(db.Study).filter(db.Study.status==1).all()
    print("tick", queued_studies)
    for study in queued_studies:
      p = mp.Process(target=run, args=(study.id,))
      p.start()
      processes.append(p)
