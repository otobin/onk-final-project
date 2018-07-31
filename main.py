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
    first_name = ndb.StringProperty()
    last_name = ndb.StringProperty()
    education = ndb.StringProperty()
    experience = ndb.StringProperty()
    industry = ndb.StringProperty()
    email = ndb.StringProperty()
    resume = ndb.BlobProperty()


class MainPage(webapp2.RequestHandler):
    def get(self):
        logging.info('This is the main handler')
        #This part of the code is to direc the user to either login, logout, or create account
        login_url = users.create_login_url('/')
        logout_url = users.create_logout_url('/')
        create_account = users.create_login_url('/create')
        current_person = ''
        current_user = users.get_current_user()
        if not current_user:
            current_user = None
        else:
            current_email = current_user.email()
            #pinpoints the right account for the person who just logged in
            current_person = Profile.query().filter(Profile.email == current_email).get()

        templateVars = {
            'login_url': login_url,
            'current_user': current_user,
            'logout_url': logout_url,
            'create_account': create_account,
            'current_person': current_person,
        }
        template = env.get_template('templates/home.html')
        self.response.write(template.render(templateVars))


class CreateProfile(webapp2.RequestHandler):
    def get(self):
        template = env.get_template('templates/create_profile.html')
        self.response.write(template.render())

    def post(self):
        email = users.get_current_user().email()
        first_name = self.request.get('first_name')
        last_name = self.request.get('last_name')
        education = self.request.get('education')
        experience = self.request.get('experience')
        industry = self.request.get('industry')
        profile = Profile(email=email, first_name=first_name, last_name=last_name, education=education,
        experience=experience, industry=industry)
        profile.put()
        self.redirect('/')

class Display_Profile(webapp2.RequestHandler):
    def get(self):
        urlsafe_key = self.request.get('key')
        key = ndb.Key(urlsafe=urlsafe_key)
        profile=key.get()
        logging.info(profile)
        templateVars = {
            'profile' : profile,
        }
        template = env.get_template('/templates/profile.html')
        self.response.write(template.render(templateVars))


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
        self.response.headers['Content-Type'] = 'text/xml'
        self.response.write(profile.resume)
        # use I frame to display separate window within webpage

def parse_resume():
    current_user = users.get_current_user()
    current_profile = Profile.query().filter(Profile.email == current_user.email()).get()
    resume = current_profile.resume
    #os.rename(resume, 'shortened_resume.txt')
    with open('shortened_resume.txt') as f:
        content = ' '.join(f.readlines()).replace('\n','').replace('\r','').lower()

    words = {}
    wordArray = content.split(" ")

    for word in wordArray:
        if (word in words and word is not ""):
            words[word] += 1
        else:
            words[word] = 1

    return words

parse_resume()



app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/create', CreateProfile),
    ('/profile', Display_Profile),
    ('/upload_resume', ResumeUpload),
    ('/resume', ResumeHandler),
], debug=True)
