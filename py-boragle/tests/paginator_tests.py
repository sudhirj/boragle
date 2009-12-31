import base, logging
from utils import Paginator

class PaginatorTest(base.ExtendedTestCase):
    def test_paginator(self):
        paginator = Paginator(current_page = 1, page_size=10, item_count = 12)
        self.assertEqual(paginator.paginator.next,2)
        self.assertEqual(paginator.paginator.prev,None)
        self.assertEqual(paginator.paginator.current,1)
        self.assertEqual(paginator.paginator.last,2)
        self.assertEqual(paginator.paginator.offset,0)
                
        paginator = Paginator(current_page = 2, page_size=5, item_count = 12)
        self.assertEqual(paginator.paginator.next,3)
        self.assertEqual(paginator.paginator.prev,1)
        self.assertEqual(paginator.paginator.current,2)
        self.assertEqual(paginator.paginator.last,3)
        self.assertEqual(paginator.paginator.offset,5)
                
        paginator = Paginator(current_page = 2, page_size=5, item_count = 10)
        self.assertEqual(paginator.paginator.next,None)
        self.assertEqual(paginator.paginator.prev,1)
        self.assertEqual(paginator.paginator.current,2)
        self.assertEqual(paginator.paginator.last,2)
        self.assertEqual(paginator.paginator.offset,5)        