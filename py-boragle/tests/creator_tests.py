
import base, logging
from models import Creator
from google.appengine.ext import db
from google.appengine.api import users

class CreatorTest(base.ExtendedTestCase):
    def test_init_values(self):
        user = users.User('s@g.com')    
        creator = Creator(user = user)
        creator.put()
        
        self.assertEqual(user.nickname(),creator.name)
        self.assertEqual(user.email(),creator.email)
        self.assertEqual(user.user_id(),creator.user_id)
        self.assertEqual(1,creator.rep)

    def test_values_are_initialized_only_once(self):
        user = users.User('s@g.com')    
        creator = Creator(user = user)
        creator.put()
        creator.name = "the new name"
        creator.email = 'new@mail.com'
        creator.rep = 100
        creator.put()
        self.assertEqual("the new name",creator.name)
        self.assertEqual('new@mail.com',creator.email)
        self.assertEqual(100,creator.rep)
    
    def test_creator_is_automatically_registered_on_first_login(self):
        old_count = Creator.all().count()
        self.login('new@user.com')
        self.app.get('/')
        self.assertEqual(1,Creator.all().count()-old_count)
        self.assertEqual('new@user.com',Creator.all().fetch(1)[0].name)
        
        
        
        
    
        
    
        
