import wsgiref.handlers, settings, os
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template

class ExtendedHandler(webapp.RequestHandler):
    def render_template(self, template_file, data = None):
        path = os.path.join(os.path.dirname(__file__), 'templates/'+template_file+'.dtl')
        self.response.out.write(template.render(path, data))

class MainHandler(ExtendedHandler):
    def get(self):
        self.render_template('main')

class QuestionHandler(ExtendedHandler):
    def get(self, boragle_slug, question_slug):
        self.render_template('qna')

class BoragleHandler(ExtendedHandler):
    def get(self, boragle_slug):
        self.render_template('boragle')

class NewBoragleHandler(ExtendedHandler):
    def get(self):
        self.render_template('new')

class AskQuestionHandler(ExtendedHandler):
    def get(self, boragle_slug):
        self.render_template('ask-question')
        
        
ROUTES =    [
            (r'/([\w-]+)/ask', AskQuestionHandler),
            (r'/new', NewBoragleHandler),
            (r'/([\w-]+)/([\w-]+)/*', QuestionHandler),
            (r'/([\w-]+)/*', BoragleHandler),
            (r'.*', MainHandler)
            ]

def create_app():
    return webapp.WSGIApplication(ROUTES, settings.debug)

def main():
    wsgiref.handlers.CGIHandler().run(create_app())

if __name__ == '__main__':
    main()
