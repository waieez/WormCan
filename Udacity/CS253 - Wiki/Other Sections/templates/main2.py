import os
import webapp2
import cgi
import re
import jinja2

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_environment = jinja2.Environment(autoescape=True,
	loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')))

form = """
<form method="post">
	<input name="username" value="%(username)s"></input>
	<label name="unerror" style="color:red">%(unerror)s</label>
	<br>
	<input name="password" type="password"></input>
	<label name="pwerror" style="color:red">%(pwerror)s</label>
	<br>
	<input name="verify" type="password"></input>
	<label name="veerror" style="color:red">%(veerror)s</label>
	<br>
	<input name="email" value="%(email)s"></input>
	<label name="emerror" style="color:red">%(emerror)s<label>
	<br>
	<input type="submit"></input>
	<br>
</form>
"""

user_re = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
pw_re = re.compile(r"^.{3,20}$")
email_re = re.compile(r"^[\S]+@[\S]+\.[\S]+$")


class MainPage(webapp2.RequestHandler):
	def validate(self):
		unerror = "Invalid Username"
		pwerror = "Invalid Password"
		veerror = "Passwords Do Not Match"
		emerror = "Invalid Email"
		
		username = cgi.escape(self.request.get("username"), quote = True)
		password = cgi.escape(self.request.get("password"), quote = True)
		verify = cgi.escape(self.request.get("verify"), quote = True)
		email = cgi.escape(self.request.get("email"), quote = True)
		validpw = False
		
		if user_re.match(username):
			unerror = ''
		
		if pw_re.match(password):
			pwerror = ''			
			
		if password == verify:
			veerror = ''
		
		if email_re.match(email) or email=='':
			emerror = ''
			
		return username, email, unerror, pwerror, veerror, emerror
		
	
	def poop(self, username='', password='', verify='', email='', unerror='', pwerror='', veerror='', emerror=''):
		self.response.out.write(form %{"username":username, "password":password, "verify":verify, "email":email, "unerror":unerror, "pwerror":pwerror, "veerror":veerror, "emerror":emerror})
		
	def get(self):
		self.poop()
		
	def post(self):
		username, email, unerror, pwerror, veerror, emerror = self.validate()
		password = ''
		verify = ''
		
		if username and pwerror == veerror and emerror == '':
			self.redirect("/welcome?username="+username)
		else:
			self.poop(username,password,verify,email,unerror,pwerror,veerror,emerror)

class Welcome(webapp2.RequestHandler):
	def get(self):
		username = cgi.escape(self.request.get("username"), quote = True)
		if user_re.match(username):
			self.response.out.write("Welcome "+ username + "!")
		else:
			self.redirect("/")
			
class Handler(webapp2.RequestHandler):
	 def write(self, *a, **kw):
		 self.response.out.write(*a, **kw)
	
	 def render_str(self, template, **params):
		 t = jinja_environment.get_template(template)
		 return t.render(params)
		
	 def render(self, template, **kw):
		 self.write(self.render_str(template, **kw)
			
# class Jinja(webapp2.RequestHandler):
	# def get(self):
		# self.render("jinja.html")
	

app = webapp2.WSGIApplication([('/', MainPage),('/welcome', Welcome)], debug=True)