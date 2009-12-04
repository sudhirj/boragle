import base
from models import Question, Boragle, Answer
from google.appengine.ext import db

class BoragleTest(base.ExtendedTestCase):
    def setUp(self):
        super(BoragleTest, self).setUp()
        self.boragle = Boragle(name='test', slugs=['slug1'], desc='desc', creator = self.creator)
        self.boragle.put()
        self.question = Question(boragle = self.boragle, text = 'why on earth?', details = 'Seriously, why?')
        self.question.put()
    def test_question_validations(self):
        self.assertRaises(db.BadValueError,Question,slugs = ['q1'])
        self.assertRaises(db.BadValueError,Question,slugs = ['q1'], boragle = self.boragle)
    
    def test_question_slugger(self):
        self.assertTrue('why-on-earth' in self.question.slugs)
        
    def test_url(self):
        self.assertEqual(self.boragle.url+'/'+self.question.slug,self.question.url)
    
    def test_answering(self):
        answer = Answer(question = self.question, text = 'zimply')
        answer.put()
        self.assertEqual(1,self.question.answer_count)
        self.assertEqual('zimply',self.question.answers[0].text)
        
        
        
        
