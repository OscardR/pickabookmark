# -*- coding: utf-8 -*-
from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.api import users
import jinja2
import os

jinja_environment = jinja2.Environment(\
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

class Bookmark(db.Model):
    user = db.StringProperty()
    name = db.StringProperty()
    url = db.StringProperty()
    icon = db.StringProperty()
    rating = db.StringProperty()
    tags = db.StringProperty()
    date = db.DateTimeProperty(auto_now_add=True)

class MainPage(webapp.RequestHandler):
    def get(self):
        user = users.get_current_user()
        bookmarks = db.GqlQuery("SELECT * "
            "FROM Bookmark WHERE user = :1", user.email() if user != None else None)
        allowed = False
        if user:
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
            url_img = 'logout'
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'
            url_img = 'login'

        template_values = {
            'bookmarks' : bookmarks,
            'url' : url,
            'url_linktext' : url_linktext,
            'user' : user,
            'allowed' : allowed,
            'url_img' : url_img
        }

        template = jinja_environment.get_template('index.html')
        self.response.out.write(template.render(template_values))

class Submit(webapp.RequestHandler):
    def post(self):
        bookmark = Bookmark()
        if users.get_current_user() != None:
            bookmark.user = users.get_current_user().email()
        else:
            bookmark.user = None
        bookmark.name = self.request.get('name')
        bookmark.url = self.request.get('url')
        bookmark.icon = self.request.get('icon')
        bookmark.rating = self.request.get('rating')
        bookmark.tags = self.request.get('tags')
        bookmark.put()
        self.redirect('/')

class Edit(webapp.RequestHandler):
    def post(self):
        bookmark = Bookmark()
        user = users.get_current_user()
        if user != None:
            bookmark.user = users.get_current_user().email()
        else:
            bookmark.user = None
        
        # Borrar el bookmark existente
        delete_bookmark(user, self.request.get('old_name'))
        
        # Añadir el bookmark cambiado
        bookmark.name = self.request.get('name')
        bookmark.url = self.request.get('url')
        bookmark.icon = self.request.get('icon')
        bookmark.rating = self.request.get('rating')
        bookmark.tags = self.request.get('tags')
        bookmark.put()
        self.redirect('/')

class Delete(webapp.RequestHandler):
    def get(self):
        user = users.get_current_user()
        name = self.request.get('b')
        delete_bookmark(user, name)
        self.redirect('/')

def delete_bookmark(user, name):
    bookmark = Bookmark.gql('WHERE name = :1 AND user = :2', name, user.email() if user != None else None)
    db.delete(bookmark)

app = webapp.WSGIApplication([('/', MainPage), ('/submit', Submit), ('/delete', Delete), ('/edit', Edit)], debug=True)
