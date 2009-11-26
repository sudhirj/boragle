import base
from models import Boragle, Question

class QuestionTests(base.ExtendedTestCase):
    boragle = Boragle(name='test1', slugs = ['t1'], desc = 'desc')
    boragle.put()
    def test_creation(self):
        self.app.post('/t1/ask', dict(text = 'why? why? why?', details = 'simply, maybe'))
        question = Question.find_by_slug('why-why-why')
        self.assertTrue(question)
        self.assertEqual("why? why? why?",question.text)
        self.assertEqual("simply, maybe",question.details)
        
    def test_answering_question(self):
        question = Question(boragle = self.boragle, 
                    text = "why ?")
        question.put()
        self.app.post(question.url, dict(answer = 'zimbly'))
        self.assertEqual('zimbly', question.answers[0].text)
        
