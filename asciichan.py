'''
	Asciichan
	http://chris.com/ascii/
	An ascii message board using google app engine
'''
import os
import webapp2
import jinja2

from google.appengine.ext import db

#set templating directory with jinja. NOTE that jinja escapes html because I set autoescape = True
template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)

#handler class inherits from RequestHandler. Used to simplify writing and rendering to templates
class Handler(webapp2.RequestHandler):
	def write(self, *a, **kw):
		self.response.out.write(*a, **kw)

	def render_str(self, template, **params):
		t = jinja_env.get_template(template)
		return t.render(params)

	def render(self, template, **kw):
		#called by render_front in MainPage class
		self.write(self.render_str(template, **kw))

class Art(db.Model):
	'''
		This is how you work with the datastore!
		To define an entity(table), you define a class. This class inherits from db.model
		This class represents an submission of user art, to be stored and retrieved from the database
	'''
	#first, we must define the types/properties (columns) of the entity
	title = db.StringProperty(required = True) #declare a column to be of a string type. If you try to make an instance of art without a title, you'll get an exception because of the required = true.
	art = db.TextProperty(required = True) #text is larger than 500 characters, a restriction on the string property
	createdOn = db.DateTimeProperty(auto_now_add = True) #automatically add the current date and time to the entity (instance of art)

#handle requests for main page
class MainPage(Handler):
	def render_front(self, title="", art="", error=""):
		'''
			RENDER THE FRONT PAGE!
			a method for rendering the front page, passing variables into the template so we can use these variables in the form, 
			and putting art from the database there too.
		'''
		#run a query, select all the instances of Art from the database sorted by creation time, newest first
		arts = db.GqlQuery("SELECT * from Art ORDER BY createdOn DESC") #remember, arts is a cursor- a pointer to the results in the database.

		self.render("front.html", title=title, art=art, error=error, arts=arts)

	def get(self):
		self.render_front()

	#form handling
	def post(self):
		#get parameters out of the request
		title = self.request.get("title")
		art = self.request.get("art")

		#error handling
		if title and art:
			# make art!
			a = Art(title = title, art = art)#make a new instance of Art (kind of like a new row in a table)
			a.put()#store new art object in database
			self.redirect("/") #redirect to the frontpage

		else:
			error = "we need both a title and some artwork"
			# db.delete(Art.all(keys_only=True))
			self.render_front(title, art, error) #requires a place for the error and other variables in the template

#specify instance of the app
app = webapp2.WSGIApplication([('/', MainPage)], debug=True)

