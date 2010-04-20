## begin license ##
#
#    Meresco Core is an open-source library containing components to build
#    searchengines, repositories and archives.
#    Copyright (C) 2007-2010 Seek You Too (CQ2) http://www.cq2.nl
#    Copyright (C) 2007-2009 SURF Foundation. http://www.surf.nl
#    Copyright (C) 2007-2009 Stichting Kennisnet Ict op school.
#       http://www.kennisnetictopschool.nl
#    Copyright (C) 2007 SURFnet. http://www.surfnet.nl
#
#    This file is part of Meresco Core.
#
#    Meresco Core is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    Meresco Core is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Meresco Core; if not, write to the Free Software
#    Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#
## end license ##
from cq2utils import CQ2TestCase
from os.path import join
from lxml.etree import parse, tostring, _ElementTree

from meresco.core import Observable, be
from meresco.components import XsltCrosswalk

xmlCode = """<?xml version="1.0"?>
<greeting>
  Hello, World!
</greeting>"""

expectedXml = """<html>
  <body>
    <h1>
  Hello, World!
</h1>
  </body>
</html>"""

XSLT = """<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
  <xsl:output method="html"/>

  <xsl:template match="/">
    <xsl:apply-templates select="greeting"/>
  </xsl:template>

  <xsl:template match="greeting">
    <html>
      <body>
        <h1>
          <xsl:value-of select="."/>
        </h1>
      </body>
    </html>
  </xsl:template>
</xsl:stylesheet>"""


class XsltCrosswalkTest(CQ2TestCase):

    def setUp(self):
        CQ2TestCase.setUp(self)
        self.xsltFilename = join(self.tempdir, 'stylesheet.xsl')
        self.xmlFilename = join(self.tempdir, 'source.xml')
        fp = open(self.xsltFilename, 'w')
        try:
            fp.write(XSLT)
        finally:
            fp.close()
        fp = open(self.xmlFilename, 'w')
        try:
            fp.write(xmlCode)
        finally:
            fp.close()

    def testCrosswalk(self):
        self.crosswalkedNode = []

        class Intercept:
            def someMessage(innerself, xmlNode):
                self.crosswalkedNode.append(tostring(xmlNode, pretty_print=True))
                self.assertEquals(_ElementTree, type(xmlNode))
        root = be(
            (Observable(),
                (XsltCrosswalk([self.xsltFilename]),
                    (Intercept(), )
                )
            )
        )
        root.do.someMessage(parse(open(self.xmlFilename)))
        self.assertEqualsWS(expectedXml, self.crosswalkedNode[0])
