import webapp2
import jinja2
import os
import StringIO
import json
import urllib
import logging

from google.appengine.ext import ndb
from google.appengine.api import users
from google.appengine.api import urlfetch

API_KEY = "AIzaSyDCv38dyT92Kalge4L8ibzHFVcLgvtps9Q"
classify_url = "https://language.googleapis.com/v1/documents:classifyText?key=" + API_KEY
entities_url = "https://language.googleapis.com/v1/documents:analyzeEntities?key=" + API_KEY
sentiment_url = "https://language.googleapis.com/v1/documents:analyzeSentiment?key=" + API_KEY


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

dead_words = ['is', 'are', 'was', 'were', 'am', 'has', 'have', 'had', 'be', 'been', 'look', 'take', 'took', 'make', 'run', 'ran', 'go', 'went', 'gone', 'do', 'did', 'came', 'come', 'helped']

action_words = ['achieved', 'improved', 'trained', 'maintained', 'mentored', 'managed', 'created', 'resolved', 'volunteered', 'influence', 'increased', 'decreased', 'ideas', 'launched', 'revenue', 'profits', 'under budget', 'won']


class MainPage(webapp2.RequestHandler):
    def get(self):
        logging.info('This is the main handler')
        #This part of the code is to direc the user to either login, logout, or create account
        login_url = users.create_login_url('/')
        logout_url = users.create_logout_url('/')
        create_account = users.create_login_url('/create')
        current_person = None
        current_user = users.get_current_user()
        # if not current_user:
        #     current_user = None
        # else:
        if current_user:
            current_email = current_user.email()
            #pinpoints the right account for the person who just logged in
            current_person = Profile.query().filter(Profile.email == current_email).get()
            if not current_person:
                self.redirect('/fail')
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
        key = profile.put().urlsafe()
        self.redirect('/profile?key=' + key)

class Display_Profile(webapp2.RequestHandler):
    def get(self):
        urlsafe_key = self.request.get('key')
        key = ndb.Key(urlsafe=urlsafe_key)
        profile=key.get()
        logging.info(profile)
        current_user = users.get_current_user()
        logout_url = users.create_logout_url('/')
        current_email = current_user.email()
        current_person = Profile.query().filter(Profile.email == current_email).get()
        templateVars = {
            'profile' : profile,
            'logout_url': logout_url,
            'current_person': current_person,
        }
        template = env.get_template('/templates/profile.html')
        self.response.write(template.render(templateVars))
    def post(self): #To do: if else to override or create new profile
        self.redirect("/update")

class Update_Profile(webapp2.RequestHandler):
    def get(self):
        template = env.get_template("/templates/update_profile.html")
        self.response.write(template.render())
    def post(self):
        current_email = users.get_current_user().email()
        profile = Profile.query().filter(Profile.email == current_email).get()
        first_name = self.request.get('first_name')
        last_name = self.request.get('last_name')
        education = self.request.get('education')
        experience = self.request.get('experience')
        industry = self.request.get('industry')
        if first_name != "none":
             profile.first_name = self.request.get("first_name")
        if (education != "none"):
             profile.education = self.request.get("education")
        if (experience != "none"):
             profile.experience = self.request.get("experience")
        if (industry != "none"):
            profile.industry = self.request.get("industry")
        key = profile.put().urlsafe()
        self.redirect('/profile?key=' + key)

# class ResumeReview(webapp2.RequestHandler):
#     def get(self):
#         template = env.get_template("templates/resume_upload.html")
#         self.response.write(template.render())

class ResumeUpload(webapp2.RequestHandler):
    def get(self):
        urlsafe_key = self.request.get('key')
        key = ndb.Key(urlsafe=urlsafe_key)
        profile=key.get()
        current_user = users.get_current_user()
        logout_url = users.create_logout_url('/')
        current_email = current_user.email()
        current_person = Profile.query().filter(Profile.email == current_email).get()
        templateVars = {
            'profile' : profile,
            'logout_url': logout_url,
            'current_person': current_person,
        }
        template = env.get_template("templates/resume_upload.html")
        self.response.write(template.render(templateVars))
    def post(self):
        current_user = users.get_current_user()
        current_email = current_user.email()
        profile = Profile.query().filter(Profile.email == current_email).get()
        resume = self.request.get('resume')
        profile.resume = resume
        profile.put()
        self.redirect('/resume_advice')

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

class ResumeAdvice(webapp2.RequestHandler):
    def get(self):
        current_user = users.get_current_user()
        logout_url = users.create_logout_url('/')
        current_email = current_user.email()
        current_person = Profile.query().filter(Profile.email == current_email).get()
        dead_match = find_dead_words()
        print dead_match
        action_match = find_action_words()
        if current_person.experience != 'None':
            job_descriptions = analyze_entities()
        categories = getCategories(classify_url)
        sentiment = getSentiment(sentiment_url)
        templateVars = {
            'dead_match' : dead_match,
            'action_match' : action_match,
            'logout_url': logout_url,
            'current_person': current_person,
            'job_descriptions' : job_descriptions,
            'categories': categories,
            'sentiment': sentiment,
        }
        template = env.get_template('templates/resume_advice.html')
        self.response.write(template.render(templateVars))


def parse_resume(type):
    current_user = users.get_current_user()
    current_email = current_user.email()
    current_profile = Profile.query().filter(Profile.email == current_email).get()
    resume = current_profile.resume
    if type is ' ' :
        resume = resume.replace('\n','').replace('\r','').lower()
    wordArray = resume.split(type)
    return wordArray
    #split resume by line, look for consistency

def find_action_words():
    action_match = {}
    words = parse_resume(' ')
    action_count = 0
    for word in words:
        for action_word in action_words:
            if word == action_word and word not in action_match:
                action_match[word] = 1
                action_count += 1
            elif word == action_word:
                action_match[word] += 1
                action_count += 1
    action_match['count'] = action_count
    return action_match

def find_dead_words():
    dead_match = {}
    words = parse_resume(' ')
    dead_count = 0
    for word in words:
        for dead_word in dead_words:
            if word == dead_word and word not in dead_match:
                dead_match[word] = 1
                dead_count += 1
            elif word == dead_word:
                dead_match[word] += 1
                dead_count += 1
    dead_match['count'] = dead_count
    return dead_match

def analyze_entities():
    resume = parse_resume('\n')
    linenum = 0
    joblines = []

    for resume_line in resume:
        data = {
         "document": {
            "type": "PLAIN_TEXT",
            "language": "EN",
            "content": resume_line,
          },
          "encodingType": "UTF8",
        }

        headers = {
            "Content-Type" : "application/json; charset=utf-8"
        }

        result = urlfetch.fetch(entities_url,
             method=urlfetch.POST,
             payload=data,
             headers=headers
        )

        placeindex = -1
        if result.status_code == 200:
            j = json.loads(result.content)
            type_list = []
            for i in range(len(j['entities'])):
                type_list.append(j['entities'][i]['type'])
            job_line = 0
            for type in type_list:
                #print type
                currentindex = type_list.index(type)
                if type == 'PERSON' and currentindex > placeindex:
                    placeindex = currentindex
                    job_line += 1
                elif type == 'ORGANIZATION' or type == 'OTHER' and currentindex > placeindex:
                    placeindex = currentindex
                    job_line += 1
                elif type == 'LOCATION' and currentindex > placeindex:
                    placeindex = currentindex
                    job_line += 1
                    joblines.append(linenum + 1)
        else:
            msg = 'Error accessing insight API:'+str(result.status_code)+" "+str(result.content)
            print msg
        linenum += 1

        #print job_line
    if len(joblines) > 0:
        return joblines
    else:
        return 0


def getCategories(url): #url is unique to categories function in api
    current_user = users.get_current_user()
    current_email = current_user.email()
    current_profile = Profile.query().filter(Profile.email == current_email).get()
    resume = current_profile.resume
    data = {
     "document": {
        "type": "PLAIN_TEXT",
        "language": "EN",
        "content": resume,
      }
    }
    headers = {
    "Content-Type" : "application/json; charset=utf-8"
    }
    jsondata = json.dumps(data)
    result = urlfetch.fetch(url, method=urlfetch.POST, payload=data,headers=headers)
    python_result = json.loads(result.content)
    string = ""
    for i in range(0, len(python_result["categories"])):
         string += "Your resume indicates the "
         string += python_result["categories"][i]["name"]
         string += " category with a "
         string += str(python_result["categories"][i]["confidence"])
         string += " level of confidence. \n"
    return string





def getSentiment(url): #url is unique to sentiment function in api
    current_user = users.get_current_user()
    current_email = current_user.email()
    current_profile = Profile.query().filter(Profile.email == current_email).get()
    resume = current_profile.resume
    data = {
        "document": {
        "type": "PLAIN_TEXT",
        "language": "EN",
        "content": resume,
      },
      "encodingType": "UTF32",
    }
    headers = {
    "Content-Type" : "application/json; charset=utf-8"
        }
    jsondata = json.dumps(data)
    result = urlfetch.fetch(url, method=urlfetch.POST, payload=data,headers=headers)
    python_result = json.loads(result.content)
    string = ""
    magnitude = python_result["documentSentiment"]["magnitude"]
    score = python_result["documentSentiment"]["score"]
    if (score < 0.0):
        string = "Your resume has a " + str(score) + " score  and a " + str(magnitude) + " magnitude. This reads as negative"
    elif (score > 0.0 and score < .5):
        string = "Your resume has a " + str(score) + " score  and a " + str(magnitude) + " magnitude. This reads as neutral"
    elif (score > .5):
        string = "Your resume has a " + str(score) + " score  and a " + str(magnitude) + " magnitude. This reads as positive"
    return string

app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/create', CreateProfile),
    ('/profile', Display_Profile),
    # ('/resume_review', ResumeReview),
    ('/resume_advice', ResumeAdvice),
    ('/upload_resume', ResumeUpload),
    ('/resume', ResumeHandler),
    ('/fail', Login_Fail),
    ('/update', Update_Profile)
], debug=True)
