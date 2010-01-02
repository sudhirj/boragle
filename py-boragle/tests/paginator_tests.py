import base, logging
from utils import Paginator

class PaginatorTest(base.ExtendedTestCase):
    def test_paginator(self):
        getter = self.mox.CreateMockAnything()
        items = [1,2,3,4,5,6,7,8,9,10,11,12]
        getter(count = 10, offset = 0).AndReturn(items)
        self.mox.ReplayAll()
        paginator = Paginator(current_page = 1, page_size=10, item_count = 12, getter = getter)
        self.assertEqual(paginator.next,2)
        self.assertEqual(paginator.prev,None)
        self.assertEqual(paginator.current,1)
        self.assertEqual(paginator.last,2)
        self.assertEqual(paginator.offset,0)
        self.mox.VerifyAll()
        self.assertEqual(paginator.items,items[:10])
                
        paginator = Paginator(current_page = 2, page_size=5, item_count = 12)
        self.assertEqual(paginator.next,3)
        self.assertEqual(paginator.prev,1)
        self.assertEqual(paginator.current,2)
        self.assertEqual(paginator.last,3)
        self.assertEqual(paginator.offset,5)
                                  
        paginator = Paginator(current_page = 2, page_size=5, item_count = 10)
        self.assertEqual(paginator.next,None)
        self.assertEqual(paginator.prev,1)
        self.assertEqual(paginator.current,2)
        self.assertEqual(paginator.last,2)
        self.assertEqual(paginator.offset,5)   
        self.assertEqual(paginator.page_size,5)     
                                  
        self.assertEqual(paginator.first,1)