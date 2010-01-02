from google.appengine.ext import db
import utils, settings
    
class ExtendedModel(db.Model):
    created_at = db.DateTimeProperty(auto_now_add = True)
    updated_at = db.DateTimeProperty(auto_now = True)
    db_version = db.IntegerProperty(default = 1)
    
    @classmethod
    def _find_by(cls, key, value):
        matches = cls.all().filter(key+' =', value).fetch(1)
        return matches[0] if len(matches) else None
    
    def put(self):
        self.db_version = settings.db_version
        return super(ExtendedModel, self).put()

class Creator(ExtendedModel):
    name = db.StringProperty()
    email = db.EmailProperty()
    user = db.UserProperty(required = True)
    user_id = db.StringProperty()
    rep = db.IntegerProperty(default = 1)

    @property
    def url(self):
        return '/'+settings.urls['users']+'/'+self.user_id
        
    def put(self):
        if not self.is_saved():
            self.name = self.user.nickname()
            self.email = self.user.email()
            self.user_id = self.user.user_id()
        return super(Creator, self).put()
        
    @classmethod    
    def find_by_id(cls, user_id):
        return cls._find_by('user_id', user_id)

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
    
    def find_question_by_slug(self, slug):
        questions = self.questions.filter('slugs =', slug).fetch(1)
        return questions[0] if len(questions) else None
    
    def get_latest_questions(self, count, start):
        query = self.all_questions()
        if start: query.filter('sort_date <= ',start)
        return query.order('-sort_date').fetch(limit = count)

    def all_questions(self):
        """ For was done mostly for testability, but use for global restrictions"""
        return self.questions
        

class Avatar(ExtendedModel):
    boragle = db.ReferenceProperty(Boragle,collection_name='avatars', required=True)
    creator = db.ReferenceProperty(Creator,collection_name='avatars', required=True)
    rep = db.IntegerProperty(default=1)
    
    @property
    def name(self):
        return self.creator.name
    
    @property
    def email(self):
        return self.creator.email
    
    @property
    def url(self):
        return self.creator.url
    
    @classmethod
    def find_or_create(cls, boragle = None, creator = None):
        avatars = cls.all().filter('boragle =', boragle).filter('creator =', creator).fetch(1)
        if (len(avatars)): return avatars[0]
        avatar = Avatar(boragle = boragle, creator = creator)
        avatar.put()
        return avatar
        
class CommentableModel(ExtendedModel, HasComments, HasVotes):
    vote_count = db.IntegerProperty(default=0)
    
    def change_vote_count(self, vote, step = 1):
        if vote is None: return
        self.vote_count += step if vote else -(step)
        self.put()
    
    def find_vote_by_avatar(self, avatar):
        existing_votes = self.votes.ancestor(self).filter('creator = ', avatar).fetch(1)
        return existing_votes[0] if len(existing_votes) else None
        
    def vote(self, avatar, vote):
        def txn(item, avatar, vote):
            existing_vote = item.find_vote_by_avatar(avatar)
            if existing_vote is None and vote is None: return
            if existing_vote is None and vote is not None:
                Vote.create(owner = item, creator = avatar, vote = vote)
                return
            if vote is None and existing_vote is not None:
                existing_vote.delete()
                item.change_vote_count(existing_vote.vote, step = -1)
                return
            if (vote is existing_vote.vote): 
                return
            item.change_vote_count((vote and not existing_vote.vote), step = 2)
            existing_vote.vote=vote
            existing_vote.put()
            
        db.run_in_transaction(txn, self, avatar, vote)

class Vote(ExtendedModel, HasCreator):
    owner = db.ReferenceProperty(CommentableModel,collection_name='votes', required=True)
    creator = db.ReferenceProperty(Avatar,collection_name='votes', required=True)
    vote = db.BooleanProperty(required=True, default=True)
    
    @classmethod
    def create(cls, **kwds):
        kwds['parent'] = kwds['owner']
        vote = Vote(**kwds)
        vote.owner.change_vote_count(vote.vote)
        vote.put()
        return vote
    
class Comment(ExtendedModel, HasCreator):
    text = db.TextProperty()
    owner = db.ReferenceProperty(CommentableModel,collection_name='comments')
    creator = db.ReferenceProperty(Avatar,collection_name='comments', required = True)
    
class Question(CommentableModel, HasSlugs, HasCreator):
    boragle = db.ReferenceProperty(Boragle,collection_name='questions', required = True)
    text = db.StringProperty(required = True)
    details = db.TextProperty()
    slugs = db.StringListProperty()
    answer_count = db.IntegerProperty(default = 0)
    creator = db.ReferenceProperty(Avatar,collection_name='questions', required = True)
    sort_date = db.StringProperty()
    
    def put(self):
        slug = utils.slugify(self.text)
        if not slug in self.slugs: self.slugs.append(slug)
        self.sort_date = self.created_at.strftime('%Y%m%d%H%M%S') + '|' + self.slug
        return super(Question, self).put()
    
    @property
    def url(self):
        return self.boragle.url + '/' + self.slug
    
    def get_answer(self, key):
        return self.answers.filter('__key__ = ', db.Key(key)).fetch(1)[0]
    
    def get_answers_by_votes(self, count = 20, offset = 0):
        return self.answers.order('-vote_count').fetch(count, offset)
        
class Answer(CommentableModel, HasCreator):
    question = db.ReferenceProperty(Question, collection_name='answers', required=True)
    text = db.TextProperty(required = True)
    creator = db.ReferenceProperty(Avatar,collection_name='answers', required=True)
    
    @classmethod
    def create(cls, **kwds):
        assert kwds['question'], kwds['creator']
        kwds['parent'] = kwds['question']
        answer = Answer(**kwds)
        def txn(answer):
            answer.question.answer_count+=1
            answer.question.put()            
            answer.put()

        db.run_in_transaction(txn, answer)
        return answer
    
    @property
    def voting_url(self):
        return self.question.url + '/'+settings.urls['vote']+'/' + str(self.key())

    