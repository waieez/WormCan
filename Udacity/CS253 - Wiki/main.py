import os, webapp2, jinja2, json

import re, string, random, datetime

import hmac, hashlib

from google.appengine.api import memcache
from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
env = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.join(template_dir)), autoescape = True)

## could build a dictionary of  regexpressions
USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
PASS_RE = re.compile("^.{3,20}$")
EMAIL_RE = re.compile("^[\S]+@[\S]+\.[\S]+$")
QUERIED = re.compile("(?i)Queried\s+(\d+)(\.\d+)?\s+seconds?\s+ago")
PAGE_RE = r'(/(?:[a-zA-Z0-9_-]+/?)*)'

## bonus problem add a third property to Wiki db "History"
## takes the wikipage nformation , add to history when wiki is updated
## history page template should be similar to blog/w link to view
## hidden input url passing
##put json back in



class Handler(webapp2.RequestHandler):
		
		##------------------------------------------------------------------------------------------------------------creates pages out of Jinja Templates
	def write(self, *a, **kw):
		self.response.out.write(*a, **kw)

	def render_str(self, template, **params):
		t = env.get_template(template)
		return t.render(params)

	def render(self, template, **kw):
		self.write(self.render_str(template, **kw))
			
		##------------------------------------------------------------------------------------------------------------ hashes user information
	def hash_user(self, raw, salt=None):
		if not salt:
			salt = ''.join( (random.sample(string.letters,5)) )
		hash = hashlib.sha256(raw + salt).hexdigest()
		return '%s|%s|%s' %(raw, hash, salt)
	
	def hash_pw(self, raw):
		secret = 'omgnowai'
		return hmac.new(secret, raw).hexdigest()
	
	def verify_hash(self, raw, hash, salt=None):
		if salt:
			if self.hash_user(raw, salt).split('|')[1] == hash:
				return True
		if not salt:
			if self.hash_pw(raw) == hash:
				return True

		##------------------------------------------------------------------------------------------------------------ uses cookies for verification of state
	def get_cookie(self, name):
		return self.request.cookies.get('%s' %name)
				
	def set_cookie(self, name, value):
		return self.response.headers.add_header('Set-Cookie', str('%s=%s; Path=/' %(name,value)))
	
	def set_user_cookie(self, username):
			usercookie = self.hash_user(username)
			self.set_cookie('username', usercookie)
		
	def is_user(self):
		cookie = self.get_cookie('username')
		if cookie:
			raw, hash, salt = cookie.split('|')
			return self.verify_hash(raw, hash, salt), raw
		return False, None
		
	def set_url(self):
		url = self.get_cookie('url')
		if not url:
			url = '/'
		return url
			
	def controls(self): ## simplify
		login, username = self.is_user()
		if login:
			return login, "login"
		else:
			return login, "guest"
			
			
		##------------------------------------------------------------------------------------------------------------ signup validation	
	def validate_user(self):
		username = self.request.get("username")
		return username, USER_RE.match(username)
		
	def validate_pw(self):
		password = self.request.get("password")
		return password, PASS_RE.match(password)

	def validate_email(self):
		email = self.request.get("email")
		return email, EMAIL_RE.match(email)

	def validate(self, verifypw = True):
		username, uValid = self.validate_user()		
		password, pValid = self.validate_pw()
		email, eValid = self.validate_email()
		verify = self.request.get("verify")
		
		error = False
		params = dict(username = username, email = email)
		
		if not uValid:
			error = True
			params['uerr'] = "Username is Invalid"
		if not pValid:
			error = True
			params['pwerr'] = "Password is Invalid"
		elif verifypw==True and password != verify:
			error = True
			params['verr'] = 'Passwords Do Not Match!'
		if email != '' and not eValid:
			error = True
			params['emerr'] = "Email is Invalid"
		if verifypw==True and self.get_memcache(username) != None:
			error = True
			params['uerr'] = "Username already exists"

		return error, params, username, password, email

		##------------------------------------------------------------------------------------------------------------ Modifies Memcache
	def grab_memcache(self):
		wikis = db.GqlQuery("SELECT * FROM Wiki")
		users = db.GqlQuery("SELECT * FROM Register")
		for wiki in wikis:
			history = PageHistory.all().filter("url = ", wiki.url)
			wikidict = {}
			for event in history:
				hkey = str(event.key())
				wikidict[hkey] = (event.saved, event.content, hkey)
			self.set_memcache(wiki.url, (wiki.key(), wiki.content, wikidict))
		for user in users:
				self.set_memcache(user.username, user.password)
			
	def set_memcache(self, key, value):
		memcache.set(key, value)
	
	def get_memcache(self, key):
		if memcache.get_stats()['items'] < 1:
			self.grab_memcache()
		return memcache.get(key)
			
	def get_wiki(self, url):
		wiki = self.get_memcache(url) ###
		key, content, wikidict = '', '', {}
		if wiki:
			key, content, wikidict = wiki
		return key, content, wikidict
		
class UserSession: #not implemented
	username = ""
	password = ""
	email = ""
	
	def __init__(self, username, password, email):
		
		self.username = username
		self.password = password
		self.email = email
	
	def getInfo(self):
		return self.username, self.password, self.email
		
class Wiki(db.Model):
	url = db.StringProperty(required=True)
	content = db.TextProperty(required=False)
	created = db.DateTimeProperty(required = True)
	modified = db.DateTimeProperty(required = True)

class Register(db.Model):
	username = db.StringProperty(required=True)
	password = db.StringProperty(required=True)
	email =db.StringProperty(required=False)
	
class PageHistory(db.Model):
	url = db.StringProperty(required=True)
	content = db.TextProperty(required=False)
	saved = db.DateTimeProperty(required = True)

## -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------##
	
class Signup(Handler):
	def get(self):
		login, controls = self.controls()
		url = self.set_url()
		
		self.render("wikisignup.html", url=url, controls=controls)
	
	def post(self):
		url = self.set_url()
		login, controls = self.controls()
	
		errors, params, username, password, email = self.validate()
		password = self.hash_pw(password)
		
		if errors == False:
			self.set_user_cookie(username)
			self.set_memcache(username, password)
			Register(username = username, password = password, email = email).put()
			self.redirect(url)
			
		if errors == True:
			self.render("wikisignup.html", url=url, controls=controls, **params) 
		
class Login(Handler):
	def get(self):
		login, controls = self.controls()
		url = self.set_url()
		
		self.render("wikilogin.html", url=url, controls=controls)
	
	def post(self):
		login, controls = self.controls()
	
		url = self.set_url()
		
		errors, params , username, password, email= self.validate(verifypw=False)
		
		cached = self.get_memcache(username)
		success = self.verify_hash(password, cached)
		
		if success:
			self.set_user_cookie(username)
			self.redirect(url)
		if errors == True or not cached or not success:
			self.render("wikilogin.html", url=url, controls=controls, **params)

class Logout(Handler):
	def get(self):
		url = self.set_url()
		
		self.set_cookie('username', '')
		self.redirect(url)

class Edit(Handler):
	def get(self, url):
		login, controls = self.controls()
		#url = self.set_url()
		key, content, wikidict = self.get_wiki(url)
		
		version = self.request.get("v") ###
		if version:
			content = wikidict[version][1]
		
		if not login:
			self.redirect(url)
		if login == True:
			self.render("wikiedit.html", url=url, controls=controls, content=content)
			
	def post(self, url):
		#url = self.set_url()
		key, oldcontent, wikidict = self.get_wiki(url)
		
		content = self.request.get("content")
		
		if oldcontent == content: ##doesnt write to memcache or db if no update
			self.redirect(url)
		
		else:
			time = datetime.datetime.now()
				
			if key:
				wiki = db.get(key)
				wiki.content, wiki.modified= content, time ##
				wiki.put()
			
			if not key:
				wiki = Wiki(url=url, content = content, created=time, modified=time)
				wiki.put()
				key = wiki.key()
				
			history = PageHistory(url=url, saved=time, content=content)
			history.put()
			hkey = str(history.key())
			wikidict[hkey] = (time, content, hkey)

			self.set_memcache(url, (key, content, wikidict))
			self.redirect(url)
		
class History(Handler): ##edit link should not be avaliable to not logged in users
	def get(self, url):
		login, controls = self.controls()
		key, content, wikidict = self.get_wiki(url)
		
		wikilist = [wikidict[entry] for entry in wikidict]
		wikilist = sorted(wikilist, key=lambda wikilist:wikilist[0], reverse=True)
		
		self.render("wikihistory.html", url=url, controls=controls, history=wikilist)
		
class WikiPage(Handler):
	def get(self, url):
		login, controls = self.controls()
		self.write(controls)
		key, content, wikidict = self.get_wiki(url)
		
		version = self.request.get("v")
		if version:
			content = wikidict[version][1]

		
		self.set_cookie('url', url)
		
		if not key and login:
			self.redirect('/edit' + url)
		
		self.render("wiki.html", content = content, url=url, controls=controls)

		
app = webapp2.WSGIApplication([('/signup', Signup), ('/login', Login), ('/logout', Logout),
	('/edit' + PAGE_RE, Edit), ('/history' + PAGE_RE, History), (PAGE_RE, WikiPage)
	#('/', Test)
	], debug=True)