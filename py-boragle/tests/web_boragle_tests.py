import base
from models import Boragle

class BoragleTests(base.ExtendedTestCase):
    def test_creation(self):
        self.app.post('/new', dict(name="test1", url = "t1", desc = 'desc'))
        new_boragle = Boragle.find_by_slug('t1')
        self.assertTrue(new_boragle)
        self.assertEqual("test1",new_boragle.name)
        self.assertEqual("desc",new_boragle.desc)
    
    def test_url_is_slugified_before_save(self):
        self.app.post('/new', dict(name="test1", url = ".t45 tes#t", desc = 'desc'))
        new_boragle = Boragle.find_by_slug('t45-test')
        self.assertTrue(new_boragle)
        
    def test_creation_security(self):
        self.logout()
        self.app.post('/new', dict(name="test1", url = "t1", desc = 'desc'), status = 403)

    def test_duplicate_urls_are_not_allowed(self):
        count = Boragle.all().count()
        self.app.post('/new', dict(name="test1", url = ".t1 tes#t", desc = 'desc'))
        self.assertEqual(count+1,Boragle.all().count())
        self.app.post('/new', dict(name="duplicate1", url = ".t1 tes#t", desc = 'duplicate desc'), status = 403)
        self.assertEqual(count+1,Boragle.all().count())
    
    def test_smoke_boragle(self):
        self.app.post('/new', dict(name="test1", url = "test1", desc = 'desc'))
        self.app.get('/test1')
        
    def test_leaving_url_empty_slugs_the_name(self):
        import utils
        name="test1 is the new thing"
        slug = utils.slugify(name)
        self.app.post('/new', dict(name=name, url = "  ", desc = 'desc'))
        new_boragle = Boragle.find_by_slug(slug)
        self.assertTrue(new_boragle)
        self.assertEqual(name,new_boragle.name)
        self.assertEqual("desc",new_boragle.desc)
        
