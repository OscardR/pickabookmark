# coding:utf8
import os
import jinja2
import webapp2

from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.api import urlfetch
from google.appengine.api import images
from django.utils import simplejson

jinja_environment = jinja2.Environment( \
    loader=jinja2.FileSystemLoader( os.path.dirname( __file__ ) ) )

class ImageHandler ( webapp2.RequestHandler ):
    def get( self ):
        key = self.request.get( 'key' )
        bookmark = db.get( key )
        if bookmark.image:
            self.response.headers['Content-Type'] = 'image/png'
            self.response.out.write( bookmark.image )
        else:
            self.error( 404 )

class Bookmark( db.Model ):
    user = db.StringProperty()
    name = db.StringProperty()
    url = db.StringProperty()
    icon = db.StringProperty()
    image = db.BlobProperty()
    rating = db.StringProperty()
    tags = db.StringProperty()
    date = db.DateTimeProperty( auto_now_add=True )

class MainPage( webapp2.RequestHandler ):
    def get( self ):
        allowed = False
        user = users.get_current_user()
        bookmarks = db.GqlQuery( 'SELECT * '
            'FROM Bookmark WHERE user = :1', user.email() if user != None else None )

        if user:
            url = users.create_logout_url( self.request.uri )
            url_linktext = 'Logout'
            url_img = 'logout'
        else:
            url = users.create_login_url( self.request.uri )
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

        template = jinja_environment.get_template( 'index.html' )
        self.response.out.write( template.render( template_values ) )

class Submit( webapp2.RequestHandler ):
    def post( self ):
        # Crear un bookmark vacío
        bookmark = Bookmark()

        # Comprobar el usuario activo y asignarlo al bookmark
        user = users.get_current_user()
        if user != None:
            bookmark.user = user.email()
        else:
            bookmark.user = None

        # Procesar la imagen a partir de la URL
        try:
            image = urlfetch.Fetch( self.request.get( 'icon' ) )
            img = images.Image( image.content )
        except:
            image = urlfetch.Fetch( "http://upload.wikimedia.org/wikipedia/commons/thumb/c/c4/No_icon_red.svg/582px-No_icon_red.svg.png" )
            img = images.Image( image.content )
        finally:
            img.resize( 140, 80, False )
            img.execute_transforms( images.PNG )

        # Recopilar los datos introducidos
        bookmark.name = self.request.get( 'name' )
        bookmark.url = self.request.get( 'url' )
        bookmark.icon = self.request.get( 'icon' )
        bookmark.image = db.Blob( img._image_data )
        bookmark.rating = self.request.get( 'rating' )
        bookmark.tags = self.request.get( 'tags' )

        # Borrar el bookmark existente si es la operación de editar
        if self.request.get( 'action' ) == 'edit':
            delete_bookmark( user, self.request.get( 'old_name' ) )

        # Añadir el bookmark construído a partir de los datos
        bookmark.put()

        # Recargar la página si no es una petición AJAX
        if not self.request.get( 'ajax' ) == 'ajax':
            self.redirect( '/' )
        else:
            self.response.write( 'OK' )

class Delete( webapp2.RequestHandler ):
    def get( self ):
        user = users.get_current_user()
        name = self.request.get( 'b' )
        delete_bookmark( user, name )
        self.redirect( '/' )

class RPCHandler( webapp2.RequestHandler ):
    """ Allows the functions defined in the RPCMethods class to be RPCed."""

    def __init__( self, *args, **kwargs ):
        webapp2.RequestHandler.__init__( self )
        self.methods = RPCMethods()

    def get( self ):
        func = None

        action = self.request.get( 'action' )
        if action:
            if action[0] == '_':
                self.error( 403 )  # access denied
                return
            else:
                func = getattr( self.methods, action, None )

        if not func:
            self.error( 404 )  # file not found
            return

        args = ()
        while True:
            key = 'arg%d' % len( args )
            val = self.request.get( key )
            if val:
                args += ( simplejson.loads( val ), )
            else:
                break
        result = func( *args )
        self.response.out.write( simplejson.dumps( result ) )

class RPCMethods:
    """ Defines the methods that can be RPCed.
    NOTE: Do not allow remote callers access to private/protected "_*" methods.
    """
    def Delete( self, *args ):
        name = args[0]
        return 'deleted: %s' % name

    def Get( self, *args ):
        name = args[0]
        return 'get: %s' % name

class APIHandler( webapp2.RequestHandler ):
    def get( self ):
        user = users.get_current_user()
        bookmarks = db.GqlQuery( 'SELECT * '
            'FROM Bookmark WHERE user = :1', user.email() if user != None else None )
        cosas = {'bookmarks': bookmarks}

        self.response.headers['Content-Type'] = 'application/json'
        template = jinja_environment.get_template('bookmark.html')
        self.response.out.write(template.render(cosas))

def delete_bookmark( user, name ):
    bookmark = Bookmark.gql( 'WHERE name = :1 AND user = :2', name, user.email() if user != None else None )
    db.delete( bookmark )

urls = [( '/', MainPage ),
        ( '/submit', Submit ),
        ( '/delete', Delete ),
        ( '/display', ImageHandler ),
        ( '/api', APIHandler ),
        ( '/rpc', RPCHandler )]
app = webapp2.WSGIApplication( urls, debug=True )
