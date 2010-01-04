from google.appengine.dist import use_library
use_library('django', '1.1')  # Or '1.1'
import django

def webapp_add_wsgi_middleware(app):
  from appstats import recording
  app = recording.appstats_wsgi_middleware(app)
  return app