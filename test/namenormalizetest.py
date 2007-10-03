
from unittest import TestCase

from meresco.components.namenormalize import NameNormalize, breakUp

class NameNormalizeTest(TestCase):

    def testRewrite(self):
        self.assertEquals(None, breakUp(""))
        self.assertEquals(("peters", "", "h", "h"), breakUp("Peters, H."))
        self.assertEquals(("peters", "", "h", "hjm"), breakUp("Peters, H.J.M."))
        self.assertEquals(("peters", "", "h", "h"), breakUp("Peters, Hans"))
        self.assertEquals(("peters", "", "h", "h"), breakUp("Peters, H"))
        self.assertEquals(("peters", "", "h", "h"), breakUp("Peters, H. (Hans)"))
        self.assertEquals(("peters", "", "h", "hjm"), breakUp("Peters, H.J.M. (Hans)"))
        self.assertEquals(("peters", "", "h", "h"), breakUp("Peters, H. (Hans Jan Marie)"))
        self.assertEquals(("peters", "", "h", "hjm"), breakUp("Peters, HJM"))
        self.assertEquals(("peters", "", "h", "hjm"), breakUp("Peters, Hans Jan Marie"))
        
        #self.assertEquals(("peters", "", "j", ["j", "j"]), breakUp("Peters, Jean-Jacques"))
        #self.assertEquals(("peters", "", "j", ["j", "j"]), breakUp("Peters, J.-J"))
        
        
        
        #dc.creator
        #dc.creator.all_initials
        #dc.creator.one_initial
        #dc.creator.lastname"

        #eerst: dd op query, field = grofmazig
        #foreach term:
            #x = dd op query, term, field = orig
            #display: meest gevonden term uit x

        #query: russische tractoren (34 resultaten)
        #Peters, H.J.M. (20)
        #Peters, H. (2)

        #Janssen (13)

    def testComonent(self):
        
        
        
