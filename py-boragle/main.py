import wsgiref.handlers, settings
from google.appengine.ext import webapp

class MainHandler(webapp.RequestHandler):

  def get(self):
    self.response.out.write('Hello world!')

ROUTES = [('/', MainHandler)]

def create_app():
    return webapp.WSGIApplication(ROUTES, settings.debug)

def main():
  wsgiref.handlers.CGIHandler().run(application)

if __name__ == '__main__':
  main()
