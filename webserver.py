#!/usr/bin/python3

import web
from database import *
import json
import datetime

from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import scoped_session, sessionmaker

render = web.template.render('webtemplates/')

urls = (
  '/overview/', 'overview',
  '/overview', 'overview',
  '/track', 'track',
  '/study', 'study',
  '/vehicle', 'vehicle',

  '/(.*)', 'login'
)

Session = scoped_session(sessionmaker(bind=engine))

def load_sqla(handler):
    web.ctx.orm = Session()

    try:
        return handler()
    except OperationalError:
        web.ctx.orm.rollback()
        Session.remove()
        raise
    except:
        web.ctx.orm.commit()
        Session.remove()
        raise
    finally:
        web.ctx.orm.commit()
        Session.remove()

app = web.application(urls, locals())
app.add_processor(load_sqla)

class login:
    def GET(self, args):
        return 'Please log in.'

class overview:
  def GET(self):
    web.header('Content-type', 'text/html')
    try:
      vehicles = web.ctx.orm.query(Vehicle).all()
      tracks   = web.ctx.orm.query(Track).all()
      studies  = web.ctx.orm.query(Study).all()

      return render.overview(vehicles, tracks, studies)
    except Exception as e:
      print("ERROR: ", e)
      return json.dumps({'error': 'Server-side error.'})

class vehicle:
  def GET(self):
    web.header('Content-type', 'application/json')
    try:
      data = web.input()
      vehicle = {}
      if 'id' in data:
        id   = int(data.id)
        vehicle = web.ctx.orm.query(Vehicle).filter(Vehicle.id==id).first()
      elif 'name' in data and 'version' in data:
        name = str(data.name)
        version = int(data.version)
        vehicle = web.ctx.orm.query(Vehicle).filter(Vehicle.name==name).filter(Vehicle.version==version).first()
      else:
        json.dumps({'error': 'id or name/version not specified.'})

      return json.dumps(vehicle.as_dict())
    except:
      return json.dumps({'error': 'Server-side error.'})

  def POST(self):
    web.header('Content-type', 'application/json')
    # edit vehicle if name & version exists
    # create new if name & version correspond to something used
    # validate processing
    # return vehicle object
    try:
      data = web.input()
      vehicle = {}
      if 'id' in data:
        id   = int(data.id)
        vehicle = web.ctx.orm.query(Vehicle).filter(Vehicle.id==id).first()
      elif 'name' in data and 'version' in data:
        name = str(data.name)
        version = int(data.version)
        vehicle = web.ctx.orm.query(Vehicle).filter(Vehicle.name==name).filter(Vehicle.version==version).first()
      else:
        return json.dumps({'error': 'id or name/version not specified.'})

      print(data, vehicle.as_dict())
      if vehicle:
        vehicle.filedata = data.filedata
        vehicle.edit_date = datetime.datetime.now().isoformat()
      else:
        pass

      return json.dumps(vehicle.as_dict())
    except Exception as e:
      print(e)
      return json.dumps({'error': 'Server-side error.'})

class track:
  def GET(self):
    web.header('Content-type', 'application/json')
    try:
      data = web.input()
      track = {}
      if 'id' in data:
        id   = int(data.id)
        track = web.ctx.orm.query(Track).filter(Track.id==id).first()
      elif 'name' in data and 'version' in data:
        name = str(data.name)
        version = int(data.version)
        track = web.ctx.orm.query(Track).filter(Track.name==name).filter(Track.version==version).first()
      else:
        json.dumps({'error': 'id or name/version not specified.'})

      return json.dumps(track.as_dict())
    except e:
      return json.dumps({'error': 'Server-side error.'})

  def POST(self):
    web.header('Content-type', 'application/json')
    # edit track if name and version exists
    # error if name & version correspond to something used
    # new track if not
    # return track object
    pass

class study:
  def GET(self):
    web.header('Content-type', 'application/json')
    try:
      data = web.input()
      study = {}
      if 'id' in data:
        id   = int(data.id)
        study = web.ctx.orm.query(Study).filter(Study.id==id).first()
      elif 'name' in data and 'version' in data:
        name = str(data.name)
        version = int(data.version)
        study = web.ctx.orm.query(Study).filter(Study.name==name).filter(Study.version==version).first()
      else:
        json.dumps({'error': 'id or name/version not specified.'})

      return json.dumps(study.as_dict())
    except Exception as e:
      return json.dumps({'error': 'Server-side error.'})

  def POST(self):
    web.header('Content-type', 'application/json')
    # edit study if not submitted
    # error if name and version correspond to something submitted
    # new study if not
    # return study object
    pass

class submit:
  def POST(self):
    # submit a study to be ran
    pass

class view:
  def GET(self):
    # view a study
    pass

if __name__ == "__main__":
    app.run()