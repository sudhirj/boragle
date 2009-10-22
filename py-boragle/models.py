from google.appengine.ext import db

class ExtendedModel(db.Model):
    created_at = db.DateTimeProperty(auto_now_add = True)
    updated_at = db.DateTimeProperty(auto_now = True)
    
    @classmethod
    def _find_by(cls, key, value):
        matches = cls.all().filter(key+' =', value).fetch(1)
        return matches[0] if len(matches) else None

class HasSlugs:
    @staticmethod
    def validate_slugs(slugs):
        if not len(slugs): raise db.BadValueError

    @classmethod
    def find_by_slug(cls, slug):
        return cls._find_by('slugs', slug)

class HasComments:
    pass
    db.UserProperty()

class HasVotes:
    pass
    
class Boragle(ExtendedModel, HasSlugs):
    name = db.StringProperty(required = True)
    desc = db.TextProperty()
    slugs = db.StringListProperty(validator = HasSlugs.validate_slugs)

class CommentableModel(ExtendedModel, HasComments, HasVotes):
    votes = db.IntegerProperty()    

class Comment(ExtendedModel):
    text = db.TextProperty()
    owner = db.ReferenceProperty(CommentableModel,collection_name='comments')
    
class Question(CommentableModel, HasSlugs):
    boragle = db.ReferenceProperty(Boragle,collection_name='questions')
    slugs = db.StringListProperty(validator = HasSlugs.validate_slugs)
    
class Answer(CommentableModel):
    question = db.ReferenceProperty(Question,collection_name='answers')

class Borg(ExtendedModel):
    user_id = db.StringProperty(required = True)
    reputation = db.IntegerProperty(default = 1)
    
    
    