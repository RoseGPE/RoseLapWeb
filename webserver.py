#!/usr/bin/python3

import web
from database import *
import json
import datetime
import time

render = web.template.render('webtemplates/', globals={'ctx': web.ctx})

web.config.debug = True

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
  def GET(self):
    return "boring index page"

class overview:
  def GET(self):
    web.header('Content-type', 'text/html')
    try:
      #if not logged():
      #  return "You shouldn't be here."
      vehicles = web.ctx.orm.query(Vehicle).all()
      tracks   = web.ctx.orm.query(Track).all()
      studies  = web.ctx.orm.query(Study).all()

      return render.overview(vehicles, tracks, studies)
    except Exception as e:
      print("ERROR: ", e)
      return json.dumps({'error': 'Server-side error.'})



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