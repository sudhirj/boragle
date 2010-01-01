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
    
class Paginator:
    def __init__(self, current_page, page_size, item_count, getter = None):
        self.last = int((item_count-1) // page_size) + 1
        self.next = current_page + 1 if current_page < self.last else None
        self.prev = current_page - 1 if current_page > 1 else None
        self.current = current_page
        self.offset = (current_page - 1) * page_size
        self.first = 1
        self.page_size = page_size
        if getter:
            self.items = getter(count = self.page_size, offset = self.offset)[:self.page_size]
    
        