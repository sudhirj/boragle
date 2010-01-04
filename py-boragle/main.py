from google.appengine.dist import use_library
use_library('django', '1.1')

import wsgiref.handlers, settings, os
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.api import users
from models import Boragle, Question, Answer, Creator, Avatar
import utils, logging, time
from datetime import datetime

class PostingError(Exception):
    def __init__(self, message):
        self.message = message

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
            self.creator = Creator.get_by_key_name(current_user.user_id()) or Creator.get_or_insert(current_user.user_id(), user = current_user)
        return super(ExtendedHandler, self).initialize(request, response)
        
    def handle_exception(self, exception, debug):
        base_params = dict(authdetails = utils.authdetails(),
                                            creator = self.creator)
        if not debug:
            try:
                raise exception
            except PostingError, e: 
                base_params.update(dict(message = e.message))
            except Exception: 
                pass
            finally:    
                self.render_template('error', base_params)
        else:
            super(ExtendedHandler, self).handle_exception(exception, debug)
    
    def get_avatar_for_boragle(self, boragle):
        return Avatar.find_or_create(boragle = boragle, creator = self.creator) if self.creator else None
        
    @staticmethod    
    def calc_last_page(number, page_size):
        return int((number-1) // page_size) + 1
            
class MainHandler(ExtendedHandler):
    def get(self):
        self.render_template('main', dict(boragles = Boragle.get_latest(count = 5),
                                authdetails = utils.authdetails(),
                                creator = self.creator))

class QuestionHandler(ExtendedHandler):
    def get(self, boragle_slug, question_slug):
        question = Question.find_by_slug(question_slug)
        assert question
        paginator = utils.Paginator(current_page = int(self.read('page') or 1),
                                        page_size = settings.answer_page_size,
                                        item_count = question.answer_count,
                                        getter = question.get_answers_by_votes)
        avatar = self.get_avatar_for_boragle(question.boragle)
        self.render_template('qna', dict(question=question,
                                        boragle = question.boragle,
                                        authdetails = utils.authdetails(question.url),
                                        creator = avatar,
                                        answers = paginator.items,
                                        paginator = paginator
                                        ))
    
    @utils.authorize()
    def post(self, boragle_slug, question_slug):
        question = Question.find_by_slug(question_slug)
        avatar = self.get_avatar_for_boragle(question.boragle)
        assert avatar, question
        answer = self.read('answer')
        if not(answer and answer.strip()): raise PostingError('Please provide an answer')
        Answer.create(question = question, text = answer, creator = avatar)
        page = self.calc_last_page(question.answer_count, settings.answer_page_size)
        self.redirect(question.url+'?page='+str(page))

class BoragleHandler(ExtendedHandler):
    def get(self, boragle_slug):
        boragle = Boragle.find_by_slug(boragle_slug)
        avatar = Avatar.find_or_create(boragle=boragle, creator=self.creator) if self.creator else None
        start = self.read('start') or None
        questions = boragle.get_latest_questions(count = settings.question_page_size + 1, start = start)
        next = questions.pop().sort_date if len(questions) == settings.question_page_size + 1 else None
        self.render_template('boragle', dict(boragle=boragle,
                                                questions = questions,
                                                authdetails = utils.authdetails(boragle.url),
                                                creator = avatar,
                                                next = next))

class NewBoragleHandler(ExtendedHandler):
    def get(self):
        self.render_template('new', dict(authdetails = utils.authdetails(settings.urls['new']),
                                        creator = self.creator))
        
    @utils.authorize()
    def post(self):
        assert self.creator
        name = self.read('name')
        if not (name and name.strip()): raise PostingError("Please enter a name for your Boragle") 
        slug = utils.slugify(self.read('url'))
        if slug == '': slug = utils.slugify(name)
        if Boragle.find_by_slug(slug): raise PostingError('This url is already in use.')
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
                            authdetails = utils.authdetails(boragle.url+'/'+settings.urls['ask']),
                            creator = avatar))
        
    @utils.authorize()
    def post(self, boragle_slug):
        boragle = Boragle.find_by_slug(boragle_slug)
        avatar = self.get_avatar_for_boragle(boragle)
        text = self.read('text')
        if not text or not text.strip(): raise PostingError('Please enter a question.')
        assert avatar
        new_question = Question(text = text,
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
        user = Creator.find_by_id(user_id)
        self.render_template('user', dict(user = user, 
                                            authdetails = utils.authdetails(user.url),
                                            creator = self.creator))

class SearchHandler(ExtendedHandler):
    def get(self):
        self.render_template('search', dict(authdetails = utils.authdetails('/search'),
                                            creator = self.creator))
            
        
ROUTES =    [
            ('/search.*', SearchHandler),
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
    from google.appengine.ext.webapp import util
    # wsgiref.handlers.CGIHandler().run(create_app())
    util.run_wsgi_app(create_app())

if __name__ == '__main__':
    main()
