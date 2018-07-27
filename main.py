import webapp2
import jinja2
import os


from google.appengine.ext import ndb
from google.appengine.api import users

env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)


class MainPage(webapp2.RequestHandler):
    def get(self):
        #1. Read request
        #2. Read/write to database
        #3. Render response

        templateVars = {

        }
        template = env.get_template('templates/home.html')
        self.response.write(template.render(templateVars))

class Profile(webapp2.RequestHandler):
    def get(self):
        template = env.get_template("templates/profile.html")
        self.response.write(template.render())


app = webapp2.WSGIApplication([
    ('/', MainPage),
    ("/profile", Profile)
], debug=True)
