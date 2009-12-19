
import base
from models import Boragle, Creator, Avatar
from google.appengine.ext import db
from google.appengine.api import users

class BoragleTest(base.ExtendedTestCase):
    def make_boragle(self):
        boragle = Boragle(name = "Koi", 
                desc= "Boragle about koi fish", 
                slugs = ["koi","koi-fish"],
                creator = self.creator)
        boragle.put()
        return boragle
    def test_avatar_ceation(self):
        self.assertRaises(db.BadValueError,Avatar,boragle = self.make_boragle())
        self.assertRaises(db.BadValueError, Avatar, creator = self.creator)
        avatar = Avatar(boragle = self.make_boragle(), creator = self.creator)
        self.assertEqual(1,avatar.rep)
    
    def test_avatar_delegates_property_getters(self):
        avatar = Avatar(boragle = self.make_boragle(), creator = self.creator)
        avatar.put()
        self.assertEqual(avatar.name,self.creator.name)
        self.assertEqual(avatar.email,self.creator.email)
        self.assertEqual(avatar.url,self.creator.url)
    
    def test_find_from_find_or_create(self):
        boragle = self.make_boragle()
        avatar = Avatar(boragle = boragle, creator = self.creator)
        avatar.put()
        
        creator2 = Creator(user = users.User('new_user@user.com'))
        creator2.put()
        avatar2 = Avatar(boragle = boragle, creator = creator2)
        avatar2.put()
        
        avatar_from_db = Avatar.find_or_create(boragle = boragle, creator = self.creator)
        self.assertEqual(avatar.key(),avatar_from_db.key())
        
        avatar_from_db = Avatar.find_or_create(boragle = boragle, creator = creator2)
        self.assertEqual(avatar2.key(),avatar_from_db.key())
        
    
    def test_create_from_find_or_create(self):
        boragle = self.make_boragle()
        avatar = Avatar.find_or_create(boragle = boragle, creator = self.creator)
        self.assertTrue(avatar.is_saved())
        self.assertEqual(boragle,avatar.boragle)
        self.assertEqual(self.creator, avatar.creator)
        
    
        
        
        
        
        
    
        
    
        
