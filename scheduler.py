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
import itertools
import copy
from sim.run_onetire import Run_Onetire
import numpy as np
import logging

run_species = {
  "onetire": Run_Onetire
}

def rset(obj, keys, value):
  if len(keys) == 1:
    setattr(obj, keys[0], value)
  else:
    rset(getattr(obj, keys[0]), keys[1:], value)

def rget(obj, keys):
  if len(keys) == 1:
    return getattr(obj, keys[0])
  else:
    return rget(getattr(obj, keys[0]), keys[1:])

def rscale(obj, keys, v):
  orig = rget(obj, keys)
  if isinstance(orig, list):
    rset(obj, keys, [x*v for x in orig])
  else:
    rset(obj, keys, orig*v)

class StudyInvalidError(Exception):
  def __init__(self, msg):
    Exception.__init__(self, "StudyInvalidError(%s)" % msg)

def run(study_id):
  print("#### scheduler.run(study_id=%d) STARTED ####" % study_id)

  db_session = db.scoped_session(db.sessionmaker(bind=db.engine))
  #stdout = None
  try:
    study = db_session.query(db.Study).filter(db.Study.id == study_id).first()

    ## Set up folder for study and redirect print statements to a log file there
    folder = "studies/"+str(study_id)
    if not os.path.exists(folder):
      os.makedirs(folder)

    logging.basicConfig(filename=folder+os.sep+"log.log", level=logging.DEBUG)
    #stdout = sys.stdout = open(folder+"/log.log", 'w')

    logging.info("#### scheduler.run(study_id=%d) STARTED ####\n" % study_id)

    ## Parse inputs from study

    logging.info("------- Study Inputs -------")
    logging.info("Fulltext of Study Specification: %s" % repr(study.filedata))

    # Load spec from study
    spec = yaml.load(study.filedata)

    # Grab latest versions of vehicle and tracks used, set their status to used
    db_vehicle = db_session.query(db.Vehicle).filter(db.Vehicle.name == spec.vehicle).order_by(db.Vehicle.version.desc()).first()
    db_vehicle.status = db.STATUS_SUBMITTED
    proto_vehicle = yaml.load(db_vehicle.filedata)
    #vehicle = Vehicle('yaml', db_vehicle.filedata) # core vehicle object used in sim

    # Sort tracks by version (highest first). Then sort out each track uniquely
    raw_tracks = db_session.query(db.Track).filter(db.Track.name.in_(spec.tracks)).order_by(db.Track.version.desc()).all()
    db_tracks = []
    tracks    = []
    track_names = []
    for track in raw_tracks:
      if not track.name in track_names:
        track_names.append(track.name)
        db_tracks.append(track)
        tracks   .append(Track(track.name, track.filetype, track.filedata, track.unit))
        track.status = db.STATUS_SUBMITTED

    logging.info("Vehicle: %s" % repr(db_vehicle))
    logging.info("Tracks: %s" % repr(db_tracks))
    logging.info("Model: %s" % repr(spec.model))
    logging.info("Settings: %s" % repr(spec.settings))
    logging.info("Sweeps: %s \n" % repr(spec.sweeps))

    # Figure out how many runs will happen in all
    study.runs_total    = 1
    study.runs_complete = 0
    axis_lengths = []
    axis_choices = []
    for axis in spec.sweeps:
      for variable in axis.variables:
        if type(variable.values) != type([]):
          variable.values = np.linspace(float(variable.values.start), float(variable.values.end), int(variable.values.length)).tolist()
      axis_lengths.append(len(axis.variables[0].values))
      axis_choices.append(range(axis_lengths[-1]))
      study.runs_total *= axis_lengths[-1]

    logging.info("Run size is %d runs.\n" % study.runs_total)

    # Study actually runs from here; commit everything to the database
    study.run()
    db_session.commit()

    ## Dispatch workers to compute results
    for permutation in itertools.product(*axis_choices):
      logging.info("Permutation %s" % repr(permutation))
      # @TODO: actual dispatch, thread pool, variable parse/edit

      # Clone vehicle/settings/tracks
      c_vehicle  = copy.deepcopy(proto_vehicle)
      c_settings = copy.deepcopy(spec.settings)
      c_tracks   = copy.deepcopy(tracks)

      prep = []
      for i, var_num in enumerate(permutation):
        for var in spec.sweeps[i].variables:
          try:
            v = var.values[var_num]
            prep.append("%s %s %s" % (var.varname, ('*' if var.operation=='scale' else '='), repr(v)))
            keys = var.varname.split('.')
            if keys[0] == 'settings':
              if var.operation == 'scale':
                rscale(c_settings, keys[1:], v)
              elif var.operation == 'replace':
                rset(c_settings, keys[1:], v)
              else:
                raise StudyInvalidError("Invalid operation for settings: %s" % repr(var.operation))
            elif keys[0] == 'model':
              if var.operation == 'replace':
                spec.model = v
              else:
                raise StudyInvalidError("Invalid operation for model: %s" % repr(var.operation))
            elif keys[0] == 'track':
              if keys[1] == 'scale':
                for track in c_tracks:
                  track.scale(v)
            else:
              if var.operation == 'scale':
                rscale(c_vehicle, keys, v)
              elif var.operation == 'replace':
                rset(c_vehicle, keys, v)
              else:
                raise StudyInvalidError("Invalid operation for vehicle: %s" % repr(var.operation))
          except Exception as e:
            logging.error("Error in parsing sweep for %s : %s : %s" % (repr(var.varname), repr(var.operation), repr(v)))
            raise e

      logging.info("Vars: %s" % repr(prep))
      run = run_species[spec.model](
        Vehicle('object', c_vehicle),
        c_tracks, c_settings)

      try:
        run.solve()
        # run.postproc() # @TODO: postproc
        # run.save()     # @TODO: save csv
      except Exception as e:
        logging.error(e, exc_info=True)

      study.runs_complete+=1
      db_session.commit()


    ## Create a manifest file
    logging.info("------ Building Manifest ------")
    manifest = {
      "study": study.as_dict(),
      "vehicle": db_vehicle.as_dict(),
      "tracks":  [track.as_dict() for track in db_tracks]
    }
    # @TODO: Fully build manifest
    # @TODO: Track / vehicle filedata store in external files
    with open(folder+"/manifest.json", "w") as f:
      f.write(json.dumps(manifest))
    logging.info("Manifest saved.")

    logging.info("#### scheduler.run(study_id=%d) FINISHED ####" % study_id)

    study.finish(db.STATUS_SUCCESS)
    db_session.commit()
  except Exception as e:
    #if stdout:
    #  sys.stdout = stdout
      
    #print("#### scheduler.run(study_id=%d) ERROR ####" % study_id)
    logging.error(e, exc_info=True)
    study.finish(db.STATUS_FAILURE)
    db_session.commit()


if __name__ == "__main__":
  db_session = db.scoped_session(db.sessionmaker(bind=db.engine))
  processes = []
  while True:
    time.sleep(1)
    queued_studies = db_session.query(db.Study).filter(db.Study.status==1).all()
    #print("tick", queued_studies)
    for study in queued_studies:
      p = mp.Process(target=run, args=(study.id,))
      p.start()
      processes.append(p)
