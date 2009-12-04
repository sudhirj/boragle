import base
from models import Boragle, Question

class QuestionTests(base.ExtendedTestCase):
    def setUp(self):
        super(QuestionTests, self).setUp()
        self.boragle = Boragle(name='test1', slugs = ['t1'], desc = 'desc', creator = self.creator)
        self.boragle.put()
        self.question = Question(boragle = self.boragle, text = "why ?")
        self.question.put()
        
    def test_creation(self):
        self.app.post('/t1/ask', dict(text = 'why? why? why?', details = 'simply, maybe'))
        question = Question.find_by_slug('why-why-why')
        self.assertTrue(question)
        self.assertEqual("why? why? why?",question.text)
        self.assertEqual("simply, maybe",question.details)

    def test_creation_security(self):
        self.logout()
        self.app.post('/t1/ask', dict(text = 'why? why? why?', details = 'simply, maybe'), 
                status = 403)
        
    def test_answering_question(self):
        self.app.post(self.question.url, dict(answer = 'zimbly'))
        self.assertEqual('zimbly', self.question.answers[0].text)
        
    def test_answering_question_security(self):
        self.logout()
        self.app.post(self.question.url, dict(answer = 'zimbly'), status = 403)
        