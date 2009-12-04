from google.appengine.ext import db
import utils
    
class ExtendedModel(db.Model):
    created_at = db.DateTimeProperty(auto_now_add = True)
    updated_at = db.DateTimeProperty(auto_now = True)
    
    @classmethod
    def _find_by(cls, key, value):
        matches = cls.all().filter(key+' =', value).fetch(1)
        return matches[0] if len(matches) else None

class Creator(ExtendedModel):
    name = db.StringProperty()
    email = db.EmailProperty()
    user = db.UserProperty(required = True)
    user_id = db.StringProperty()
    rep = db.IntegerProperty(default = 1)

    def put(self):
        if not self.is_saved():
            self.name = self.user.nickname()
            self.email = self.user.email()
            self.user_id = self.user.user_id()
        return super(Creator, self).put()

class HasSlugs:
    @staticmethod
    def validate_slugs(slugs):
        if not len(slugs): raise db.BadValueError

    @classmethod
    def find_by_slug(cls, slug):
        return cls._find_by('slugs', slug)
    
    @property 
    def slug(self):
        return self.slugs[0]

class HasCreator:
    pass
    

class HasComments:
    pass

class HasVotes:
    pass
    
class Boragle(ExtendedModel, HasSlugs, HasCreator):
    name = db.StringProperty(required = True)
    desc = db.TextProperty()
    slugs = db.StringListProperty(validator = HasSlugs.validate_slugs)
    creator = db.ReferenceProperty(Creator,collection_name='boragles', required = True)
    
    @property
    def url(self):
        return '/' + self.slug
    
    @classmethod
    def get_latest(cls, count = 5):
        return cls.all().order('-created_at').fetch(count)

class CommentableModel(ExtendedModel, HasComments, HasVotes):
    votes = db.IntegerProperty()    

class Comment(ExtendedModel, HasCreator):
    text = db.TextProperty()
    owner = db.ReferenceProperty(CommentableModel,collection_name='comments')
    
class Question(CommentableModel, HasSlugs, HasCreator):
    boragle = db.ReferenceProperty(Boragle,collection_name='questions', required = True)
    text = db.StringProperty(required = True)
    details = db.TextProperty()
    slugs = db.StringListProperty()
    answer_count = db.IntegerProperty(default = 0)
    
    def put(self):
        self.slugs.append(utils.slugify(self.text))
        return super(Question, self).put()
    
    @property
    def url(self):
        return self.boragle.url + '/' + self.slug
    
class Answer(CommentableModel, HasCreator):
    question = db.ReferenceProperty(Question, collection_name='answers')
    text = db.TextProperty(required = True)
    
    def put(self):
        self.question.answer_count += 1
        self.question.put()
        return super(Answer, self).put()

    
    
    