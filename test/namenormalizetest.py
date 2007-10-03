
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

        #naam: achter tussen voor initialen titels
        #self.assertEquals(("peters", "", "j", ["j", "j"]), breakUp("Peters, Jean-Jacques"))
        #self.assertEquals(("peters", "", "j", ["j", "j"]), breakUp("Peters, J.-J"))

    def testCompose(self):
        self.assertEquals("Helsing", helsing(("helsing", "ab", "van")))
        self.assertEquals("Helsing, A.", helsing_a_v(("helsing", "ab", "")))
        self.assertEquals("Helsing, A., v.", helsing_a_v(("helsing", "ab", "van")))
        self.assertEquals("Helsing, A., v.d.", helsing_a_v(("helsing", "ab", "van der")))
        self.assertEquals("Helsing, A.B.", helsing_ab_van(("helsing", "ab", "")))
        self.assertEquals("Helsing, A.B., van", helsing_ab_van(("helsing", "ab", "van")))
        self.assertEquals("Helsing, A.B., van der", helsing_ab_van(("helsing", "ab", "van der")))


    def testComponent(self):
        pass



#dc.creator                 -> echt alles
#dc.creator.nogmeer         -> Peters, H.J.M. prof dr ir
#dc.creator.all_initials    -> Peters, H.J.M.
#dc.creator.one_initial     -> Peters, H.
#dc.creator.lastname"       -> Peters
#dc.creator.isreally        -> Peters, H.M.J

#eerst: dd op query, field = grofmazig
#foreach term:
    #x = dd op query, term, field = orig
    #display: meest gevonden term uit x

#query: russische tractoren (34 resultaten)
#(verborgen info:)
#peters, h.j.m. (50)
#peters, hans (2)

#weergave:
#peters, h.j.m.

#Peters (80)
    #Peters, H. (25)
        #[x] #Peters, H.J.M. (20)
        #[x] #Peters, H. (2)
        #[ ] #Peters, Hans (3)
    ##Peters, E. (13)
    ##Peters, K. (12)
##Janssen (6)

#Peters, H : 25 dos


#x (Peters, H), (Peters HJM)
#0   ja              nee
#1   ja          nee
#2   nee         ja
#--------------------------------------+
    #2               1



#x 0 1 2 3 4 5 6
#0
#1
#2
#3