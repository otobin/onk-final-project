import webapp2
import jinja2
import os


from google.appengine.ext import ndb
from google.appengine.api import users

env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)


class Profile(ndb.Model):
    name = ndb.StringProperty()
    email = ndb.StringProperty()


class MainPage(webapp2.RequestHandler):
    def get(self):
        #1. Read request
        #2. Read/write to database
        #3. Render response

        template = env.get_template('templates/home.html')
        self.response.write(template.render())

class CreateProfile(webapp2.RequestHandler):
    def get(self):
        template = env.get_template('templates/create_profile.html')
        self.response.write(template.render())

    def post(self):
        self.redirect('/')

class Profile(webapp2.RequestHandler):
    def get(self):
        template = env.get_template('templates/profile.html')
        self.response.write(template.render())


class Profile(webapp2.RequestHandler):
    def get(self):
        template = env.get_template("templates/profile.html")
        self.response.write(template.render())


app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/create', CreateProfile),
<<<<<<< HEAD
    ('/profile', Profile)
=======
    ('/profile', Profile),
>>>>>>> a58ed9eed0bd2eb3c6f46ba74e0734683ab08fb4
], debug=True)
