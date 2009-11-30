import re

def slugify(text):
    removelist = ["a", "an", "as", "at", "before", "but", "by", "for","from","is", "in", "into", "like", "of", "off", "on", "onto","per","since", "than", "the", "this", "that", "to", "up", "via","with"];
    for word in removelist:
        slug = re.sub(r'\b'+word+r'\b','',text)
    slug = re.sub('[^\w\s-]', '', slug).strip().lower()
    slug = re.sub('\s+', '-', slug)
    return slug