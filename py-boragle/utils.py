import re
from google.appengine.api import users
import logging
import os

def path(file_path='/'):
    return os.path.join(os.path.dirname(__file__), "templates/"+file_path )
   
def authdetails(page = "/"):
    user = users.get_current_user()
    authenticated = True if user else False
    label = "sign out" if authenticated else "sign in"
    link = users.create_logout_url(page) if authenticated else users.create_login_url(page)
    return dict(link = link, label = label, authenticated = authenticated)
    
def authorize(role = "user"):
    def wrapper(handler_method):
        def check_login(self, *args, **kwargs):
            user = users.get_current_user()
            if not user:
                if self.request.method != 'GET':
                    self.error(403)
                else:
                    self.redirect(users.create_login_url(self.request.uri))
            elif role == "user" or (role == "admin" and users.is_current_user_admin()):
                handler_method(self, *args, **kwargs)
            else:
                if self.request.method == 'GET':
                    self.redirect("/403.html")
                else:
                    self.error(403)
        return check_login
    return wrapper

def slugify(text):
    removelist = ["a", "an", "as", "at", "before", "but", "by", "for","from","is", "in", "into", "like", "of", "off", "on", "onto","per","since", "than", "the", "this", "that", "to", "up", "via","with"];
    for word in removelist:
        slug = re.sub(r'\b'+word+r'\b','',text)
    slug = re.sub('[^\w\s-]', '', slug).strip().lower()
    slug = re.sub('\s+', '-', slug)
    return slug