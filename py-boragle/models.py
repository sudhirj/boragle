from google.appengine.ext import db
import re

def slugify(text):
    removelist = ["a", "an", "as", "at", "before", "but", "by", "for","from","is", "in", "into", "like", "of", "off", "on", "onto","per","since", "than", "the", "this", "that", "to", "up", "via","with"];
    for word in removelist:
        slug = re.sub(r'\b'+word+r'\b','',text)
    slug = re.sub('[^\w\s-]', '', slug).strip().lower()
    slug = re.sub('\s+', '-', slug)
    return slug
    
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
    
    @property 
    def slug(self):
        return self.slugs[0]

class HasComments:
    pass

class HasVotes:
    pass
    
class Boragle(ExtendedModel, HasSlugs):
    name = db.StringProperty(required = True)
    desc = db.TextProperty()
    slugs = db.StringListProperty(validator = HasSlugs.validate_slugs)
    
    @property
    def url(self):
        return '/' + self.slug
    
    @classmethod
    def get_latest(cls, count = 5):
        return cls.all().order('-created_at').fetch(2)

class CommentableModel(ExtendedModel, HasComments, HasVotes):
    votes = db.IntegerProperty()    

class Comment(ExtendedModel):
    text = db.TextProperty()
    owner = db.ReferenceProperty(CommentableModel,collection_name='comments')
    
class Question(CommentableModel, HasSlugs):
    boragle = db.ReferenceProperty(Boragle,collection_name='questions', required = True)
    text = db.StringProperty(required = True)
    details = db.TextProperty()
    slugs = db.StringListProperty()
    answer_count = db.IntegerProperty(default = 0)
    
    def put(self):
        self.slugs.append(slugify(self.text))
        return super(Question, self).put()
    
    @property
    def url(self):
        return self.boragle.url + '/' + self.slug
    
class Answer(CommentableModel):
    question = db.ReferenceProperty(Question, collection_name='answers')
    text = db.TextProperty(required = True)
    
    def put(self):
        self.question.answer_count += 1
        self.question.put()
        return super(Answer, self).put()

class Borg(ExtendedModel):
    user_id = db.StringProperty(required = True)
    reputation = db.IntegerProperty(default = 1)
    
    
    