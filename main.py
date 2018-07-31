import webapp2
import jinja2
import os
import StringIO
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
    #suggested_jobs = ndb.ListProperty()
    resume = ndb.BlobProperty()

dead_words = ['is', 'are,' 'was,' 'were,' 'am,' 'has,' 'have,' 'had,' 'be,' 'been,' 'look,' 'take,' 'took,' 'make,' 'run,' 'ran,' 'go,' 'went,' 'gone,' 'do,' 'did,' 'came,' 'come', 'helped']

action_words = ['Achieved', 'improved', 'trained', 'maintained', 'mentored', 'managed', 'created', 'resolved', 'volunteered', 'influence', 'increased', 'decreased', 'ideas', 'launched', 'revenue', 'profits', 'under budget', 'won']


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
            if Profile.query().filter(Profile.email == current_email).get():
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
            else:
                self.redirect('/fail')


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
        resume = self.request.get('resume')
        profile = Profile(email=email, first_name=first_name, last_name=last_name, education=education,
        experience=experience, industry=industry, resume = resume)
        key = profile.put().urlsafe()
        self.redirect('/profile?key=' + key)

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
    def post(self): #To do: if else to override or create new profile
        self.redirect("/update")

class Update(webapp2.RequestHandler):
    def get(self):
        template = env.get_template("/templates/update_profile.html")
        self.response.write(template)
    def post(self):



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

class Login_Fail(webapp2.RequestHandler):
    def get(self):
        logout_url = users.create_logout_url('/')
        templateVar = {
            'logout_url': logout_url
        }
        template = env.get_template('/templates/login_fail.html')
        self.response.write(template.render(templateVar))

class printAdvice(webapp2.RequestHandler):
    def get(self):
        dead_match = find_dead_words()
        action_match = find_action_words()

        templateVars = {
            'dead_match' : dead_match,
            'action_match' : action_match
        }
        template = env.get_template('templates/resume_advice')
        self.response.write(template.render(templateVars))

def parse_resume():
    current_user = users.get_current_user()
    current_profile = Profile.query().get()
    resume = current_profile.resume

    content = ' '.join(resume)#.replace('\n','').replace('\r','').lower()

    print content
    words = {}
    wordArray = content.split(" ")

    print wordArray
    for word in wordArray:
        if (word in words and word is not ''):
            words[word] += 1
        else:
            words[word] = 1

    return words

def find_action_words():
    action_match = {}
    words = parse_resume()
    for word in words:
        for action_word in action_words:
            if word == action_word and word not in match:
                action_match[word] = 1
            elif word == action_word:
                action_match[word] += 1
    return action_match

def find_dead_words():
    dead_match = {}
    words = parse_resume()
    for word in words:
        for dead_word in dead_words:
            if word == dead_word and word not in match:
                dead_match[word] = 1
            elif word == dead_word:
                dead_match[word] += 1
    return dead_match


app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/create', CreateProfile),
    ('/profile', Display_Profile),
    ('/upload_resume', ResumeUpload),
    ('/resume', ResumeHandler),
    ('/advice', printAdvice),
    ('/fail', Login_Fail),
    ('update', Update)
], debug=True)
