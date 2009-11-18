import base
from models import Question, Boragle
from google.appengine.ext import db

class BoragleTest(base.ExtendedTestCase):
    boragle = Boragle(name='test', slugs=['slug1'], desc='desc')
    boragle.put()
    def test_question_validations(self):
        self.assertRaises(db.BadValueError,Question,slugs = ['q1'])
        self.assertRaises(db.BadValueError,Question,slugs = ['q1'], boragle = self.boragle)
    
    def test_question_slugger(self):
        question = Question(boragle = self.boragle, text = 'why on earth?', details = 'Seriously, why?')
        question.put()
        self.assertTrue('why-on-earth' in question.slugs)
        
