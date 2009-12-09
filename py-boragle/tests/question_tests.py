import base
from models import Question, Boragle, Answer, Avatar
from google.appengine.ext import db

class BoragleTest(base.ExtendedTestCase):
    def setUp(self):
        super(BoragleTest, self).setUp()
        self.boragle = Boragle(name='test', slugs=['slug1'], desc='desc', creator = self.creator)
        self.boragle.put()
        self.avatar = Avatar(boragle = self.boragle, creator = self.creator)
        self.avatar.put()
        self.question = Question(boragle = self.boragle, text = 'why on earth?', details = 'Seriously, why?', creator = self.avatar)
        self.question.put()
    def test_question_validations(self):
        self.assertRaises(db.BadValueError,Question,boragle = self.boragle)
        self.assertRaises(db.BadValueError,Question,boragle = self.boragle, text = "question1?")
    
    def test_question_slugger(self):
        self.assertTrue('why-on-earth' in self.question.slugs)
        
    def test_url(self):
        self.assertEqual(self.boragle.url+'/'+self.question.slug,self.question.url)
    
    def test_answering(self):
        answer = Answer.create(question = self.question, text = 'zimply', creator = self.avatar)
        answer.put()
        answer.put()
        self.assertEqual(1,self.question.answer_count)
        self.assertEqual('zimply',self.question.answers[0].text)
    
    def test_creator_required_for_answers(self):
        self.assertRaises(db.BadValueError,Answer,question = self.question, text = 'zimply')
    
    def test_answer_create_and_parentage(self):
        answer = Answer.create(question = self.question, text = 'zimply', creator = self.avatar)
        self.assertTrue(answer.is_saved())
        self.assertEqual(self.question,answer.parent())
        
    def test_answer_upvoting_and_downvoting_modifies_counts(self):
        answer = Answer.create(question = self.question, text = 'zimply', creator = self.avatar)
        self.assertEqual(0,answer.vote_count)
        answer.vote(self.avatar, True)
        self.assertEqual(1,answer.vote_count)
        answer.vote(self.avatar, False)
        self.assertEqual(-1,answer.vote_count)
        answer.vote(self.avatar, None)
        self.assertEqual(0,answer.vote_count)
        
        
        
        
        
        
        
        
        
        
