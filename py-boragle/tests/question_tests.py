import base
from models import Question, Boragle, Answer, Avatar
from google.appengine.ext import db
import logging

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
        question_from_db = Question.get(self.question.key())
        self.assertEqual(1,question_from_db.answer_count)
        self.assertEqual('zimply',question_from_db.answers[0].text)
    
    def test_creator_required_for_answers(self):
        self.assertRaises(db.BadValueError,Answer,question = self.question, text = 'zimply')
    
    def test_answer_create_and_parentage(self):
        answer = Answer.create(question = self.question, text = 'zimply', creator = self.avatar)
        self.assertTrue(answer.is_saved())
        self.assertEqual(self.question,answer.parent())
        
    def test_answer_upvoting_and_downvoting_modifies_counts(self):
        answer = Answer.create(question = self.question, text = 'zimply', creator = self.avatar)
        key = answer.key()
        answer = Answer.get(key)        
        self.assertEqual(0,answer.vote_count)
        answer = Answer.get(key)
        answer.vote(self.avatar, True)
        answer = Answer.get(key)
        self.assertEqual(1,answer.vote_count)
        answer = Answer.get(key)
        answer.vote(self.avatar, False)
        answer = Answer.get(key)
        self.assertEqual(-1,answer.vote_count)
        answer = Answer.get(key)
        answer.vote(self.avatar, None)
        answer = Answer.get(key)
        self.assertEqual(0,answer.vote_count)
        answer = Answer.get(key)
        answer.vote(self.avatar, False)
        answer = Answer.get(key)
        self.assertEqual(-1,answer.vote_count)
        answer = Answer.get(key)
        answer.vote(self.avatar, False)
        answer = Answer.get(key)
        self.assertEqual(-1,answer.vote_count)
        
    
    def test_answer_downvoting_and_upvoting_modifies_counts(self):
        answer = Answer.create(question = self.question, text = 'zimply', creator = self.avatar)
        key = answer.key()
        answer = Answer.get(key)
        self.assertEqual(0,answer.vote_count)
        answer = Answer.get(key)        
        answer.vote(self.avatar, False)
        answer = Answer.get(key)
        self.assertEqual(-1,answer.vote_count)
        answer = Answer.get(key)    
        answer.vote(self.avatar, True)
        answer = Answer.get(key)       
        self.assertEqual(1,answer.vote_count)
        answer = Answer.get(key)
        answer.vote(self.avatar, None)
        answer = Answer.get(key)
        self.assertEqual(0,answer.vote_count)  
        answer = Answer.get(key)    
        answer.vote(self.avatar, True)
        answer = Answer.get(key)       
        self.assertEqual(1,answer.vote_count)
        answer = Answer.get(key)    
        answer.vote(self.avatar, True)
        answer = Answer.get(key)       
        self.assertEqual(1,answer.vote_count)
        answer = Answer.get(key)    
        answer.vote(self.avatar, True)
        answer = Answer.get(key)       
        self.assertEqual(1,answer.vote_count)
        
    
    def test_answer_null_voting_modifies_nothing(self):
        answer = Answer.create(question = self.question, text = 'zimply', creator = self.avatar)
        key = answer.key()
        answer = Answer.get(key)        
        self.assertEqual(0,answer.vote_count)
        answer = Answer.get(key)
        answer.vote(self.avatar, None)
        answer = Answer.get(key)        
        self.assertEqual(0,answer.vote_count)
    
    def test_voting_url(self):
        answer = Answer.create(question = self.question, text = 'zimply', creator = self.avatar)
        self.assertEqual(answer.question.url+'/vote/'+str(answer.key()),answer.voting_url)
        
    def test_slugs_are_saved_only_once_on_questions(self):
        self.question.put()
        self.question.put()
        self.question.put()
        self.assertEqual(len(self.question.slugs),1)        
        
        
        
        
        
        
