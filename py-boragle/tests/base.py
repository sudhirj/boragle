from google.appengine.api import users
from google.appengine.ext import db
import unittest, datetime, random
from resources.webtest import TestApp
from resources.stubout import StubOutForTesting
from resources.mox import Mox
import main


class ExtendedTestCase(unittest.TestCase): 
    app = TestApp(main.create_app())
    _login_stubs = StubOutForTesting()
    stubs = StubOutForTesting()
    
    def random(self):
        import hashlib, time
        return hashlib.md5((time.clock()*random.random()).__str__()).hexdigest()
    
    def setUp(self):
        self.mox = Mox()
        self.logout()
        
    def clear_data(self):
        for model in []:
            for datum in model.all():
                datum.delete()
        
      
    def tearDown(self):
        self.logout()
        self.stubs.UnsetAll()
        self.clear_data()

    def login(self, user="sudhir.j@gmail.com", admin=False):
        self._login_stubs.Set(users, 'get_current_user', lambda user = user : users.User(user))
        self._login_stubs.Set(users, 'is_current_user_admin', lambda admin = admin : admin)

    def logout(self):
        self._login_stubs.UnsetAll()


