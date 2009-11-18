import base
from models import Boragle

class BoragleTests(base.ExtendedTestCase):
    def test_creation(self):
        self.app.post('/new', dict(name="test1", url = "t1", desc = 'desc'))
        new_boragle = Boragle.find_by_slug('t1')
        self.assertTrue(new_boragle)
        self.assertEqual("test1",new_boragle.name)
        self.assertEqual("desc",new_boragle.desc)
