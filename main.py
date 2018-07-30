import webapp2
import jinja2
import os
import logging

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
        logging.info('This is the main handler')
        login_url = users.create_login_url('/create')

        templateVars = {
            'login_url': login_url,
        }
        template = env.get_template('templates/home.html')
        self.response.write(template.render(templateVars))

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


class Login(webapp2.RequestHandler):
    def get(self):
        template = env.get_template("templates/login.html")
        self.response.write(template.render())


class ResumeReview(webapp2.RequestHandler):
    def get(self):
        template = env.get_template("templates/resume_upload.html")
        self.response.write(template.render())

class ResumeUpload(webapp2.RequestHandler):
    def post(self):
        resume = self.request.get('key')
        key = ndb.Key(urlsafe=urlsafe_key)
        person = key.get()


app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/create', CreateProfile),
    ('/login', Login),
    ('/profile', Profile),
    ('/resume_review', ResumeReview),
    ('/upload_resume', ResumeUpload)
], debug=True)
