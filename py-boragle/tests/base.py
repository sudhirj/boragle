from google.appengine.api import users
from google.appengine.ext import db
import unittest, datetime, random
from resources.webtest import TestApp
from resources.stubout import StubOutForTesting
from resources.mox import Mox
import main, os
from models import Creator


class ExtendedTestCase(unittest.TestCase): 
    app = TestApp(main.create_app())
    _login_stubs = StubOutForTesting()
    stubs = StubOutForTesting()
    
    
    def random(self):
        import hashlib, time
        return hashlib.md5((time.clock()*random.random()).__str__()).hexdigest()
    
    def setUp(self):
        os.environ['SERVER_NAME'] = 'test'
        os.environ['SERVER_PORT'] = '1234'
        self.mox = Mox()
        self.login()
        self.creator = self.make_creator()
        
    def clear_data(self):
        for model in []:
            for datum in model.all():
                datum.delete()
        
      
    def tearDown(self):
        self.logout()
        self.stubs.UnsetAll()
        self.clear_data()

    def login(self, user_email="sudhir.j@gmail.com", admin=False):
        os.environ['USER_EMAIL'] = user_email
        os.environ['USER_IS_ADMIN'] = '1' if admin else '0'
        os.environ['USER_ID'] = user_email

    def logout(self):
        os.environ['USER_EMAIL'] = ''
        os.environ['USER_ID'] = ''
        os.environ['USER_IS_ADMIN'] = '0'
        
    def make_creator(self):
        user = users.get_current_user()
        return Creator.get_or_insert(user.user_id(), user = user)

