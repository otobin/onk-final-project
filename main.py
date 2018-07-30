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
    education = ndb.StringProperty()
    work_experience = ndb.StringProperty()
    current_industry = ndb.StringProperty()
    email = ndb.StringProperty()
    resume = ndb.BlobProperty()


class MainPage(webapp2.RequestHandler):
    def get(self):
        logging.info('This is the main handler')
        login_url = ''
        logout_url = ''
        current_user = users.get_current_user()
        if not current_user:
            login_url = users.create_login_url('/create')
        else:
            logout_url = users.create_logout_url('/')

        profile = Profile.query().get()
        templateVars = {
            'login_url': login_url,
            'profile': profile,
            'current_user': current_user,
            'logout_url': logout_url
        }
        template = env.get_template('templates/home.html')
        self.response.write(template.render(templateVars))


class CreateProfile(webapp2.RequestHandler):
    def get(self):
        template = env.get_template('templates/create_profile.html')
        self.response.write(template.render())
    def post(self):
        email = users.get_current_user().email()
        name = self.request.get('name')
        profile = Profile(email=email, name=name)
        profile.put()
        self.redirect('/')

class Display_Profile(webapp2.RequestHandler):
    def get(self):
        urlsafe_key = self.request.get('key')
        current_user = users.get_current_user()
        key = ndb.Key(urlsafe=urlsafe_key)
        profile=key.get()

        templateVars = {
            'profile' : profile,
        }
        template = env.get_template('templates/profile.html')
        self.response.write(template.render(templateVars))


class ResumeReview(webapp2.RequestHandler):
    def get(self):
        template = env.get_template("templates/resume_upload.html")
        self.response.write(template.render())

class ResumeUpload(webapp2.RequestHandler):
    def post(self):
        resume = self.request.get('resume')
        current_user = users.get_current_user()
        current_profile = Profile.query().filter(Profile.email == current_user.email()).get()
        current_profile.resume = resume
        current_profile.put()
        self.redirect('/resume?key=' + current_profile.key.urlsafe())

class ResumeHandler(webapp2.RequestHandler):
    def get(self):
        urlsafe_key = resume = self.request.get('key')
        key = ndb.Key(urlsafe=urlsafe_key)
        profile = key.get()
        self.response.headers['Content-Type'] = 'application/pdf'
        self.response.write(profile.resume)


app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/create', CreateProfile),
    ('/profile', Display_Profile),
    ('/resume_review', ResumeReview),
    ('/upload_resume', ResumeUpload),
    ('/resume', ResumeHandler),
], debug=True)
