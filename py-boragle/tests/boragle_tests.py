
import base
from models import Boragle
from google.appengine.ext import db

class BoragleTest(base.ExtendedTestCase):
    koi_boragle = Boragle(name = "Koi", desc= "Boragle about koi fish", slugs = ["koi"])
    def test_boragle_saves_vitals(self):
        self.koi_boragle.put()
        boragle = Boragle.find_by_slug('koi')
        self.assertEqual(self.koi_boragle.name,boragle.name)
        self.assertEqual(self.koi_boragle.desc,boragle.desc)
        
    def test_slug_list_validator(self):
        self.assertRaises(db.BadValueError,Boragle,name = "Koi", desc = "some desc", slugs = [])
    
    def test_finder_returns_none_no_match(self):
        self.assertEqual(None,Boragle.find_by_slug('blah'))

    def test_url(self):
        self.assertEqual('/koi',self.koi_boragle.url)
        
    
        
    
        
        