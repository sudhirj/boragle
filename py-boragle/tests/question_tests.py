
import base
from models import Boragle

class BoragleTest(base.ExtendedTestCase):
    def test_boragle_saves_vitals(self):
        koi_boragle = Boragle(name = "Koi", desc= "Boragle about koi fish", slugs = ["koi"])
        koi_boragle.put()
        
        