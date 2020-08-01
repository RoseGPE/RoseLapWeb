#!/usr/bin/python3

import web
from database import *
import json
import datetime
import time

render = web.template.render('webtemplates/', globals={'ctx': web.ctx})

web.config.debug = False

urls = (
  '/overview/', 'overview',
  '/overview', 'overview',
  '/track', 'track',
  '/study', 'study',
  '/vehicle', 'vehicle',

  '/login', 'login',
  '/logout', 'logout',
  '/(.*)', 'index'
)

##### DATABASE SETUP #####

db_session = scoped_session(sessionmaker(bind=engine))

def load_sqla(handler):
  web.ctx.orm = db_session()
  try:
    return handler()
  except OperationalError:
    web.ctx.orm.rollback()
    db_session.remove()
    raise
  except:
    web.ctx.orm.commit()
    db_session.remove()
    raise
  finally:
    web.ctx.orm.commit()
    db_session.remove()

app = web.application(urls, locals())
app.add_processor(load_sqla)

############################ AUTHENTICATION PROCESSING #############################3

def auth_app_processor(handle):
  global web
  web.ctx.request_time = time.time()
  web.ctx.use_layout = True
  try:
    web.ctx.mobile = False
    web.ctx.mobile = detect_mobile_browser(web.ctx.env['HTTP_USER_AGENT'])
  except: web.ctx.mobile = False
  cookie = web.cookies(username = None, password = None)
  web.ctx.username = cookie.username

  if not web.ctx.path in ['/login']:
    user = web.ctx.orm.query(User).filter(User.name == cookie.username).first()
    if user:
      if not user.check_password(cookie.password):
        web.ctx.username = None
        raise web.seeother('/login')
        return
    else:
      web.ctx.username = None
      raise web.seeother('/login')
      return
    web.ctx.username = cookie.username
     
  return handle()

app.add_processor(auth_app_processor)

class login:
  def GET(self):
    if web.ctx.username and web.ctx.username!='None':
      raise web.seeother('/overview')
    else:
      return render.login()

  def POST(self):
    i = web.input()
    user = web.ctx.orm.query(User).filter(User.name == i.username).first()
    if user:
      if user.check_password(i.password):
        web.setcookie('username', i.username, expires=3600*24*365)
        web.setcookie('password', i.password, expires=3600*24*365)
        raise web.seeother('/overview')
      else:
        web.setcookie('username', None)
        web.setcookie('password', None)
        raise web.seeother('/login?issue=password')
        return
    else:
      web.setcookie('username', None)
      web.setcookie('password', None)
      raise web.seeother('/login?issue=name')
      return
    
class logout:
  def GET(self):
    web.setcookie('username', None, expires=-1)
    web.setcookie('password', None, expires=-1)
    raise web.seeother('/login')

##################### WEB STUFF ##########################

class index:
  def GET(self, args):
    return "boring index page"

class overview:
  def GET(self):
    web.header('Content-type', 'text/html')
    try:
      # TODO: auth selectors
      vehicles = web.ctx.orm.query(Vehicle).order_by(Vehicle.version.desc()).all()
      vehicle_map = {}
      for vehicle in vehicles:
        if vehicle.name in vehicle_map:
          vehicle_map[vehicle.name].append(vehicle)
        else:
          vehicle_map[vehicle.name] = [vehicle]
      tracks   = web.ctx.orm.query(Track).all()
      studies  = web.ctx.orm.query(Study).all()
      # TODO: format timestamps

      return render.overview(vehicle_map, tracks, studies)
    except Exception as e:
      raise
      return json.dumps({'error': 'Server-side error.'})

class user_management:
  # TODO: user management
  def GET(self):
    pass

class view_study:
  # TODO: study view
  def GET(self):
    pass

class view_run:
  # TODO: run view
  def GET(self):
    pass

##################### REST API ###########################

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
    # edit vehicle if name and version correspond to something of status 0
    # otherwise, create a new vehicle if
    # - name does not exist (and provided version is 1)
    # - name exists, and provided version is 1 + version of the last vehicle with status = 1 (e.g. never have more than one version with status 0)
    # error otherwise
    # TODO: validate vehicle input

    try:
      data = web.input()
      vehicle = {}
      if 'name' in data and 'version' in data:
        name = str(data.name)
        version = int(data.version)
        filedata = str(data.filedata)
        vehicle = web.ctx.orm.query(Vehicle).filter(Vehicle.name==name).filter(Vehicle.version==version).first()
        if vehicle:
          print("Found your ride")
          if vehicle.status != 0:
            print("But it's archived.")
            return json.dumps({'error': 'Cannot edit archived vehicles.'})

          vehicle.filedata = filedata
          vehicle.edit_date = datetime.datetime.now().isoformat()
          return json.dumps(vehicle.as_dict())

        else:
          vehicles = web.ctx.orm.query(Vehicle).filter(Vehicle.name==name).all()
          if vehicles:
            vehicle = web.ctx.orm.query(Vehicle).filter(Vehicle.name==name).filter(Vehicle.status==1).order_by(Vehicle.version.desc()).first()
            if version != vehicle.version + 1:
              return json.dumps({'error': 'Nonsequential vehicle version (should be V%d, recieved V%d)' % (vehicle.version + 1, version)})

            vehicle = Vehicle()
            vehicle.name = name
            vehicle.version = version
            vehicle.filedata = filedata
            vehicle.edit_date = datetime.datetime.now().isoformat()
            vehicle.status = 0
            web.ctx.orm.add(vehicle)
            web.ctx.orm.commit()
            return json.dumps(vehicle.as_dict())
          else:
            if int(version) != 1:
              return json.dumps({'error': 'Vehicle versions must start at 1.'})

            vehicle = Vehicle()
            vehicle.name = name
            vehicle.version = version
            vehicle.filedata = filedata
            vehicle.edit_date = datetime.datetime.now().isoformat()
            vehicle.status = 0
            web.ctx.orm.add(vehicle)
            web.ctx.orm.commit()
            return json.dumps(vehicle.as_dict())

      else:
        return json.dumps({'error': 'Name/version not specified.'})
      
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