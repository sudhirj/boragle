from google.appengine.dist import use_library
use_library('django', '1.1')

import wsgiref.handlers, settings, os
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from models import Boragle, Question, Answer

class ExtendedHandler(webapp.RequestHandler):
    def render_template(self, template_file, data = None):
        path = os.path.join(os.path.dirname(__file__), 'templates/'+template_file+'.dtl')
        self.response.out.write(template.render(path, data))
    def read(self, param):
        return self.request.get(param)

class MainHandler(ExtendedHandler):
    def get(self):
        self.render_template('main', dict(boragles = Boragle.get_latest(count = 5)))

class QuestionHandler(ExtendedHandler):
    def get(self, boragle_slug, question_slug):
        question = Question.find_by_slug(question_slug)
        self.render_template('qna', dict(question=question,
                                        boragle = question.boragle))
    
    def post(self, boragle_slug, question_slug):
        question = Question.find_by_slug(question_slug)
        Answer(question = question, text = self.read('answer')).put()
        self.redirect(question.url)

class BoragleHandler(ExtendedHandler):
    def get(self, boragle_slug):
        self.render_template('boragle', dict(boragle=Boragle.find_by_slug(boragle_slug)))

class NewBoragleHandler(ExtendedHandler):
    def get(self):
        self.render_template('new')
    def post(self):
        new_boragle = Boragle(name = self.read('name'),
                slugs = [self.read('url')],
                desc = self.read('desc'))
        new_boragle.put()
        self.redirect(new_boragle.url)
    
class AskQuestionHandler(ExtendedHandler):
    def get(self, boragle_slug):
        self.render_template('ask-question')
    def post(self, boragle_slug):
        boragle = Boragle.find_by_slug(boragle_slug)
        new_question = Question(text = self.read('text'),
                details = self.read('details'),
                boragle = boragle)
        new_question.put()
        self.redirect(new_question.url)
        
        
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
