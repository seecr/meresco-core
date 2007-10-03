
from unittest import TestCase

from meresco.components.namenormalize import NameNormalize, breakUp, helsing, helsing_a_v, helsing_ab_van

class NameNormalizeTest(TestCase):

    def testBreakup(self):
        self.assertEquals(None, breakUp(""))
        self.assertEquals(("peters", "h", ""), breakUp("Peters, H."))
        self.assertEquals(("peters", "hjm", ""), breakUp("Peters, H.J.M."))
        self.assertEquals(("peters", "h", ""), breakUp("Peters, Hans"))
        self.assertEquals(("peters", "h", ""), breakUp("Peters, H"))
        self.assertEquals(("peters", "h", ""), breakUp("Peters, H. (Hans)"))
        self.assertEquals(("peters", "hjm", ""), breakUp("Peters, H.J.M. (Hans)"))
        self.assertEquals(("peters", "h", ""), breakUp("Peters, H. (Hans Jan Marie)"))
        self.assertEquals(("peters", "hjm", ""), breakUp("Peters, HJM"))
        self.assertEquals(("peters", "hjm", ""), breakUp("Peters, Hans Jan Marie"))
        
        #self.assertEquals(("peters", "", "j", ["j", "j"]), breakUp("Peters, Jean-Jacques"))
        #self.assertEquals(("peters", "", "j", ["j", "j"]), breakUp("Peters, J.-J"))
    
    def testCompose(self):
        self.assertEquals("helsing", helsing(("helsing", "ab", "van")))
        self.assertEquals("helsing,a,v", helsing_a_v(("helsing", "ab", "van")))
        self.assertEquals("helsing,a,vd", helsing_a_v(("helsing", "ab", "van der")))
        self.assertEquals("helsing,ab,van", helsing_ab_van(("helsing", "ab", "van")))
        self.assertEquals("helsing,ab,vander", helsing_ab_van(("helsing", "ab", "van der")))
        
        
    def testComponent(self):
        pass
        
        
        
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

