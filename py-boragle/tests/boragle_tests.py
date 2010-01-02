
import base, mox
from models import Boragle, Creator
from google.appengine.ext import db
from google.appengine.api import users

class BoragleTest(base.ExtendedTestCase):
    def make_boragle(self):
        return Boragle(name = "Koi", 
                desc= "Boragle about koi fish", 
                slugs = ["koi","koi-fish"],
                creator = self.creator)
    def test_boragle_saves_vitals(self):
        koi_boragle = self.make_boragle()
        koi_boragle.put()
        boragle = Boragle.find_by_slug('koi')
        self.assertEqual(koi_boragle.name,boragle.name)
        self.assertEqual(koi_boragle.desc,boragle.desc)
        
    def test_slug_list_validator(self):
        self.assertRaises(db.BadValueError,Boragle,name = "Koi", desc = "some desc", slugs = [], creator=self.make_creator())
        self.assertRaises(db.BadValueError,Boragle,name = "Koi", desc = "some desc", slugs = ['sdf'])
    
    def test_finder_returns_none_no_match(self):
        self.assertEqual(None,Boragle.find_by_slug('blah'))

    def test_url(self):
        self.assertEqual('/koi',self.make_boragle().url)
    
    def test_get_latest_boragles(self):
        koi_boragle = self.make_boragle()
        koi_boragle.put()
        Boragle(name = "Koi2", desc= "Boragle about koi fish2", slugs = ["koi2"], creator = self.creator).put()
        Boragle(name = "Koi3", desc= "Boragle about koi fish3", slugs = ["koi3"], creator = self.creator).put()
        boragles = Boragle.get_latest(count = 2)
        self.assertEqual(2,len(boragles))
        self.assertEqual(boragles[0].slug,"koi3")
        self.assertEqual(boragles[1].slug,"koi2")
    
    def test_get_latest_questions(self):
        start = 'abc'
        boragle = self.make_boragle()
        boragle.put()
        questions = ['q1', 'q2']
        query = self.mox.CreateMock(db.Query)
        self.mox.StubOutWithMock(boragle, 'all_questions')
        boragle.all_questions().AndReturn(query)
        query.filter('sort_date <= ', start).AndReturn(query)
        query.order('-sort_date').AndReturn(query)
        query.fetch(limit = 42).AndReturn(questions)
        
        self.mox.ReplayAll()
        self.assertEqual(questions,boragle.get_latest_questions(start = start, count = 42))
        self.mox.VerifyAll()

    def test_get_latest_questions_does_not_apply_filter_on_first_call(self):
        boragle = self.make_boragle()
        boragle.put()
        questions = ['q1', 'q2']
        query = self.mox.CreateMock(db.Query)
        self.mox.StubOutWithMock(boragle, 'all_questions')
        boragle.all_questions().AndReturn(query)
        query.order('-sort_date').AndReturn(query)
        query.fetch(limit = 42).AndReturn(questions)
        self.mox.ReplayAll()
        self.assertEqual(questions,boragle.get_latest_questions(start = None, count = 42))
        self.mox.VerifyAll()


    def test_all_question(self):
        boragle = self.make_boragle()
        boragle.put()
        self.assertEqual(repr(boragle.questions),repr(boragle.all_questions()))
        
                
        
        
    
        
    
        
        