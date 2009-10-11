from google.appengine.ext import db

def validate_slugs(slugs):
    if len(slugs) < 1: raise db.BadValueError

class Boragle(db.Model):
    name = db.StringProperty(required = True)
    slugs = db.StringListProperty(validator = validate_slugs)
    