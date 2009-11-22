import base
from models import Question, Boragle
from google.appengine.ext import db

class BoragleTest(base.ExtendedTestCase):
    boragle = Boragle(name='test', slugs=['slug1'], desc='desc')
    boragle.put()
    question = Question(boragle = boragle, text = 'why on earth?', details = 'Seriously, why?')
    question.put()
    def test_question_validations(self):
        self.assertRaises(db.BadValueError,Question,slugs = ['q1'])
        self.assertRaises(db.BadValueError,Question,slugs = ['q1'], boragle = self.boragle)
    
    def test_question_slugger(self):
        self.assertTrue('why-on-earth' in self.question.slugs)
        
    def test_url(self):
        self.assertEqual(self.boragle.url+'/'+self.question.slug,self.question.url)
        
        
        
