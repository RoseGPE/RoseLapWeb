#!/usr/bin/python3

import web
import database as db

render = web.template.render('webtemplates/')

urls = (
  '/overview/', 'overview',
  '/overview', 'overview',
  '/track', 'track',
  '/study', 'study',
  '/vehicle', 'vehicle',

  '/(.*)', 'login'
)
app = web.application(urls, globals())

class login:
    def GET(self, args):
        return 'Please log in.'

class overview:
  def GET(self):
    try:
      session = db.session()
      vehicles = session.query(db.Vehicle).all()
      tracks   = session.query(db.Track).all()
      studies  = session.query(db.Study).all()

      return render.overview(vehicles, tracks, studies)
    except Exception as e:
      print(e)

class vehicle:
  def GET(self):
    # return vehicle object
    pass

  def POST(self):
    # edit vehicle if name & version exists
    # error if name & version correspond to something used
    # validate processing
    # return vehicle object
    pass

class track:
  def GET(self):
    # return track object
    pass

  def POST(self):
    # edit track if name and version exists
    # error if name & version correspond to something used
    # new track if not
    # return track object
    pass

class study:
  def GET(self):
    # return study object
    pass

  def POST(self):
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