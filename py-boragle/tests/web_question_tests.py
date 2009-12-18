import base
from models import Boragle, Question, Avatar, Answer

class QuestionTests(base.ExtendedTestCase):
    def setUp(self):
        super(QuestionTests, self).setUp()
        self.boragle = Boragle(name='test1', slugs = ['t1'], desc = 'desc', creator = self.creator)
        self.boragle.put()
        self.avatar = Avatar(boragle = self.boragle, creator = self.creator)
        self.avatar.put()
        self.question = Question(boragle = self.boragle, text = "why ?", creator = self.avatar)
        self.question.put()
        
    def test_creation(self):
        self.app.post('/t1/ask', dict(text = 'why? why? why?', details = 'simply, maybe'))
        question = Question.find_by_slug('why-why-why')
        self.assertTrue(question)
        self.assertEqual("why? why? why?",question.text)
        self.assertEqual("simply, maybe",question.details)
        self.assertEqual(self.creator.name,question.creator.creator.name)
    

    def test_creation_security(self):
        self.logout()
        self.app.post('/t1/ask', dict(text = 'why? why? why?', details = 'simply, maybe'), 
                status = 403)
        
    def test_answering_question(self):
        self.app.post(self.question.url, dict(answer = 'zimbly'))
        question = Question.get(self.question.key())
        self.assertEqual('zimbly', question.answers[0].text)
        self.assertEqual(self.creator.name, question.answers[0].creator.name)
        self.assertEqual(1, question.answer_count)
        
    def test_answering_question_security(self):
        self.logout()
        self.app.post(self.question.url, dict(answer = 'zimbly'), status = 403)
    
    def test_smoke_question_page(self):
        self.app.get(self.question.url)
    
    def test_voting_security(self):
        answer = Answer.create(question = self.question, text= 'fake answer', creator = self.avatar)
        self.app.get(answer.voting_url+'/up', status = 302)
        answer = Answer.get(answer.key())
        self.assertEqual(answer.vote_count, 1)
        self.logout()
        self.app.get(answer.voting_url+'/down', status = 302)
        answer = Answer.get(answer.key())
        self.assertEqual(answer.vote_count, 1)        
        
    
    def test_voting_up(self):
        answer = Answer.create(question = self.question, text= 'fake answer', creator = self.avatar)
        self.app.get(answer.voting_url+'/up', status = 302)
        answer = Answer.get(answer.key())
        self.assertEqual(answer.vote_count,1)
        self.app.get(answer.voting_url+'/down', status = 302)
        answer = Answer.get(answer.key())
        self.assertEqual(answer.vote_count,-1)
        
        
        