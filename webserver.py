#!/usr/bin/python3

import web

db = web.database(dbn='sqlite', db='database.db')

render = web.template.render('webtemplates/')

urls = (
	'/overview/', 'overview',
	'/overview', 'overview',
    '/(.*)', 'login'
)
app = web.application(urls, globals())

class login:
    def GET(self, args):
        return 'Please log in.'

class overview:
	def GET(self):
		vehicles = db.select('vehicles')
		return render.overview(vehicles, [], [])

if __name__ == "__main__":
    app.run()