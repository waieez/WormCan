import os
import webapp2
import jinja2

import re
import json

import hashlib
import string
import random

import datetime

from google.appengine.api import memcache
from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
env = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.join(template_dir)), autoescape = True)

QUERIED = re.compile("(?i)Queried\s+(\d+)(\.\d+)?\s+seconds?\s+ago")
uRE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
pRE = re.compile("^.{3,20}$")
eRE = re.compile("^[\S]+@[\S]+\.[\S]+$")

class Handler(webapp2.RequestHandler):

	def write(self, *a, **kw):
		self.response.out.write(*a, **kw)

	def render_str(self, template, **params):
		t = env.get_template(template)
		return t.render(params)

	def render(self, template, **kw):
		self.write(self.render_str(template, **kw))
	
	def setcookie(self, name, value):
		return self.response.headers.add_header('Set-Cookie', str('%s=%s; Path=/' %(name,value)))
	
	def getcookie(self, name):
		return self.request.cookies.get('%s' %name)
		
	def delcookies(self):
		self.setcookie('password', '')
		self.setcookie('username', '')
		self.setcookie('salt', '')
		
	def salty(self):
		salt = (random.sample(string.letters,5))
		return ''.join(salt)
		
	def hashy(self, tasteless, salt=None):
		if not salt:
			salt = self.salty()
		hash = hashlib.sha256(tasteless + salt).hexdigest()
		return hash, salt
		
	def verify_hash(self, tasteless, salt, hash):
		if self.hashy(tasteless, salt)[0] == hash:
			return True
		else:
			return False
	
	def validate_user(self):
		username = self.request.get("username")
		return username, uRE.match(username)
		
	def validate_pw(self):
		password = self.request.get("password")
		return password, pRE.match(password)

	def validate_email(self):
		email = self.request.get("email")
		return email, eRE.match(email)

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
		if verifypw==True and self.dbsearch(username) != None:
			error = True
			params['uerr'] = "Username already exists"

		return error, params
	
	def dbsearch(self, username):
		query = db.GqlQuery("SELECT * FROM Register WHERE regUser = '%s' " %username).get()
		if query == None:
			return None
		else:
			return query.regPassword, query.regSalt
			
	def isjson(self):
		if '.json' in self.request.path:
			return True
			
	def escgql(self, string):
		return r'%s' %string

	def create_json(self, post): # format a post object into json friendly dictionary
		dicty = {}
		#dicty['Key'] = self.escgql( post.key() )
		#dicty['ID'] = self.escgql( post.key().id() )
		dicty['created'] = self.escgql(post.created)
		dicty['subject'] = post.subject
		dicty['content'] = post.content
		return dicty
	
	def render_json(self, dictionary):
			self.response.headers['Content-Type']= "application/json; charset=utf-8"
			self.write( json.dumps(dictionary) )
			
	def set_memcache(self): ##still need to add a key:val for the last db.query made
		posts = ''
		if memcache.get_stats()['items'] < 2:
			posts = self.get_table()
		if posts:
			post_ids = []
			for post in posts:
				post_id = self.insert_memcache(post)				
				post_ids.append(post_id)
			memcache.set('ids', post_ids)
		return True
			
	def insert_memcache(self, post): #takes a post obj and insert into memcache dict['id'] = {dictionary of post}
		postdict = self.create_json(post)
		post_id = post.key().id()
		memcache.add(str(post_id), postdict) ##change to replace the key string and add self to memcache
		return str(post_id)
	
	def get_memcache(self):
		post_ids = memcache.get('ids')
		if post_ids:
			return memcache.get_multi(post_ids)
	
	def create_memtable(self):
		if self.set_memcache() == True:
			dict = self.get_memcache()
			list = []
			if dict:
				for key in dict:
					list.append(dict[key])
				return list
			
	def get_table(self):
		self.set_time('blog')
		return db.GqlQuery("SELECT * FROM Post ORDER BY created DESC LIMIT 10")

	def set_time(self, id):
		if not self.isjson():
			memcache.set('query', {id : datetime.datetime.now()} )
	
	def timediff(self, id):
		if not self.isjson():
			before = memcache.get('query')
			if before and id in before:
				time = (datetime.datetime.now() - before[id]).total_seconds()
				self.write("Queried %s seconds ago" %time)
			else:
				self.set_time(id)
				self.timediff(id)

class MainPage(Handler):	
	def get(self):
		food = self.request.get_all("food")
		self.render("jinja.html", food=food)

class FizzBuzz(Handler):

	def get(self):
		n = self.request.get("n")
		if n and n.isdigit()==True:
			n = int(n)
			self.render("fizzbuzz.html", n=n)
		else:
			self.render("fizzbuzz.html")

class Blog(Handler): #GQL

	def get(self):
		isjson = self.isjson()
		posts = self.create_memtable()
		revposts = None
		if posts:
			posts = sorted(posts, key=lambda posts:posts['created'])[-10:]
			revposts = reversed(posts)
		
		if isjson == True:
			self.render_json(posts)
			
		if posts and not isjson:
			self.render("blog.html", posts=revposts) ## need to change html to accept db query timestamp
			if "newpost" == self.request.get("newpost"):
				self.redirect("/blog/newpost")
			if "droptable" == self.request.get("droptable"):
				memcache.flush_all()
			self.timediff('blog')
		
		if not posts and not isjson:
			self.render("blog.html")
			if "newpost" == self.request.get("newpost"):
				self.redirect("/blog/newpost")
			if "droptable" == self.request.get("droptable"):
				memcache.flush_all()
			self.timediff('blog')

		
class Post(db.Model): #GQL
	subject = db.StringProperty(required=True)
	content = db.TextProperty(required=True)
	created = db.DateTimeProperty(required = True)
			
class Newpost(Handler):
	def get(self):
		self.render("newpost.html")
	
	def post(self):
		subject = self.request.get("subject")
		content = self.request.get("content")
		error = "Need to submit both Subject and Content"
		if subject and content:
			created = datetime.datetime.now()
			p = Post(subject=subject, content=content, created=created) ##why you no work
			p.put()
			
			
			post_id = self.insert_memcache(p) #insert {id: {subject: ..... created:..}} into memcache and returns id			
			self.set_time(post_id)
			ids = memcache.get('ids') + [post_id] # updates id list with newpost id which is used in /blog to fetch the posts
			memcache.set('ids', ids)
			
			
			self.redirect('/blog/%s' %post_id)
			#self.redirect('/blog')

		else:
			self.render("newpost.html", subject=subject, content=content, error=error)

class Blogpost(Handler): #had help with this

	def get(self, post_id):
		isjson = self.isjson()
		if isjson == True:
			post_id = post_id.split('.json')[0]
		if post_id:
			post = memcache.get(post_id)			
		if isjson == True:
			self.render_json(post)

		else:
			if not post:
				self.error(404)
			else:
				self.render('postpage.html', posts = post)
				self.timediff(post_id)
				
class Flush(Handler):

	def get(self):
		memcache.flush_all()
		self.redirect('/blog')
			
class Register(db.Model):
	regUser = db.StringProperty(required=True)
	regPassword = db.StringProperty(required=True)
	regSalt = db.StringProperty(required = True)

class gql(Handler): # test out how to make GQL work

	def get(self):
		self.render('valid.html')
	
	def post(self):
		un = self.request.get("username")
		pw, salt = '',''
		if self.dbsearch(un) != None:
			un, pw, salt = self.dbsearch(un)

		self.render('valid.html', un=un, pw=pw, salt=salt)
	
class Signup(Handler): ## can create cache + update

	def dbreg(self, username, pwhash, salt):
		Register(regUser = username, regPassword = pwhash, regSalt = salt).put()
		
	def get(self):
		self.render("signup.html")
		
	def post(self):
		error, params = self.validate()
		username = params['username']

		if error == True:
			self.render("signup.html", **params)
			
		else:
			un_hash, salt = self.hashy(username)
			pw_hash = self.hashy(self.request.get("password"),salt)[0]
			
			self.dbreg(username, pw_hash, salt)
			
			self.setcookie('username', '%s|%s' %(username,un_hash))
			self.setcookie('un_salt', salt)
			
			self.redirect('/blog/welcome')

class Welcome(Handler):

	def get(self):
		username, hash = self.getcookie('username').split('|')
		un_salt = self.getcookie("un_salt")
		#un_salt = 'fuck' #changed salt to test redirect
		if self.verify_hash(username, un_salt, hash) == False:
			self.delcookies()
			self.redirect('/blog/signup')
			
		else:
			self.render('welcome.html', username=username)
		
class Login(Handler): ## can benefit from caching

	def verify_login(self):
	
		username = self.request.get('username')
		password = self.request.get('password')
		verified_pw = False
		
		if self.dbsearch(username) != None:
			pw_hash, salt = self.dbsearch(username)
			verified_pw = self.verify_hash(password, salt, pw_hash)
		
		if verified_pw == True:
			un_hash, un_salt = self.hashy(username)
			self.setcookie('username', '%s|%s' %(username,un_hash))
			self.setcookie('un_salt', un_salt)
			return True
				
		else:
			return False
		
	def get(self):
		self.render("login.html")
	
	def post(self):
		error, params = self.validate(verifypw=False)

		if error == True or self.verify_login() == False:
			self.render("login.html", **params)
		else:
			self.redirect('/blog/welcome')

class Logout(Handler):

	def get(self):
		self.delcookies()		
		self.redirect('/blog/signup')

class Path(Handler): #testing grounds

	def get(self):
		self.set_memcache()
		fuck = self.get_memcache()
		self.write(fuck)

jsony = '(?:.json)?'
postid = '([0-9]+)'

app = webapp2.WSGIApplication([('/', MainPage),('/fb', FizzBuzz),
	('/blog/?' + jsony, Blog), ('/blog/' + postid + jsony, Blogpost),('/blog/newpost', Newpost),
	('/blog/signup', Signup), ('/blog/welcome', Welcome), ('/blog/login', Login), ('/blog/logout', Logout),
	('/gql', gql), ('/path/?' + jsony, Path), ('/blog/flush', Flush)
	], debug=True)