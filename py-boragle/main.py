from google.appengine.dist import use_library
use_library('django', '1.1')

import wsgiref.handlers, settings, os
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.api import users
from models import Boragle, Question, Answer, Creator, Avatar
import utils, logging

class ExtendedHandler(webapp.RequestHandler):
    def render_template(self, template_file, data = None):
        path = os.path.join(os.path.dirname(__file__), 'templates/'+template_file+'.dtl')
        self.response.out.write(template.render(path, data))

    def read(self, param):
        return self.request.get(param)
        
    def initialize(self, request, response):
        self.creator = None
        current_user = users.get_current_user()
        if current_user:
            self.creator = Creator.get_or_insert(current_user.user_id(), user = current_user)
        return super(ExtendedHandler, self).initialize(request, response)
        
    def handle_exception(self, exception, debug):
        if not debug:
            self.response.out.write(exception)
            self.response.set_status(403)
        else:
            super(ExtendedHandler, self).handle_exception(exception, debug)
    
    def get_avatar_for_boragle(self, boragle):
        return Avatar.find_or_create(boragle = boragle, creator = self.creator) if self.creator else None


class MainHandler(ExtendedHandler):
    def get(self):
        self.render_template('main', dict(boragles = Boragle.get_latest(count = 5),
                                authdetails = utils.authdetails(),
                                creator = self.creator))

class QuestionHandler(ExtendedHandler):
    def get(self, boragle_slug, question_slug):
        question = Question.find_by_slug(question_slug)
        assert question
        avatar = self.get_avatar_for_boragle(question.boragle)
        self.render_template('qna', dict(question=question,
                                        boragle = question.boragle,
                                        authdetails = utils.authdetails(question.url),
                                        creator = avatar))
    
    @utils.authorize()
    def post(self, boragle_slug, question_slug):
        question = Question.find_by_slug(question_slug)
        avatar = self.get_avatar_for_boragle(question.boragle)
        assert avatar, question
        Answer.create(question = question, text = self.read('answer'), creator = avatar)
        self.redirect(question.url)

class BoragleHandler(ExtendedHandler):
    def get(self, boragle_slug):
        boragle = Boragle.find_by_slug(boragle_slug)
        avatar = Avatar.find_or_create(boragle=boragle, creator=self.creator) if self.creator else None
        self.render_template('boragle', dict(boragle=boragle,
                                                authdetails = utils.authdetails(),
                                                creator = avatar))

class NewBoragleHandler(ExtendedHandler):
    def get(self):
        self.render_template('new', dict(authdetails = utils.authdetails(settings.urls['new']),
                                        creator = self.creator))
        
    @utils.authorize()
    def post(self):
        assert self.creator
        slug = utils.slugify(self.read('url'))
        if slug == '': slug = utils.slugify(self.read('name'))
        if Boragle.find_by_slug(slug): raise Exception('This url is already in use.')
        new_boragle = Boragle(name = self.read('name'),
                slugs = [slug],
                desc = self.read('desc'),
                creator = self.creator)
        new_boragle.put()
        self.redirect(new_boragle.url)
    
class AskQuestionHandler(ExtendedHandler):
    def get(self, boragle_slug):
        boragle = Boragle.find_by_slug(boragle_slug)
        avatar = self.get_avatar_for_boragle(boragle)
        self.render_template('ask-question', dict(boragle = boragle,
                            authdetails = utils.authdetails(boragle.url+settings.urls['ask']),
                            creator = avatar))
        
    @utils.authorize()
    def post(self, boragle_slug):
        boragle = Boragle.find_by_slug(boragle_slug)
        avatar = self.get_avatar_for_boragle(boragle)
        assert avatar
        new_question = Question(text = self.read('text'),
                details = self.read('details'),
                boragle = boragle,
                creator = avatar)
        new_question.put()
        self.redirect(new_question.url)

class VotingHandler(ExtendedHandler):
    @utils.authorize()
    def get(self, boragle_slug, question_slug, answer_key,vote ):
        boragle = Boragle.find_by_slug(boragle_slug)
        avatar = self.get_avatar_for_boragle(boragle)
        question = boragle.find_question_by_slug(question_slug)
        answer = question.get_answer(answer_key)
        answer.vote(avatar, vote == 'up')
        self.redirect(question.url)

class UserHandler(ExtendedHandler):
    def get(self, user_id):
        creator = Creator.find_by_id(user_id)
        self.render_template('user', dict(creator = creator, authdetails = utils.authdetails(creator.url)))
            
        
ROUTES =    [
            ('/'+settings.urls['users']+r'/(\d+)', UserHandler),
            (r'/([\w-]+)/'+settings.urls['ask'], AskQuestionHandler),
            ('/'+settings.urls['new'], NewBoragleHandler),
            (r'/([\w-]+)/([\w-]+)/'+settings.urls['vote']+'/([\w-]+)/(up|down)/*', VotingHandler),
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
