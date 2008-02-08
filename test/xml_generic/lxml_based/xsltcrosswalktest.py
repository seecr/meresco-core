from cq2utils import CQ2TestCase
from os.path import join
from lxml.etree import parse, tostring, _ElementTree

from meresco.framework import Observable
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
        start = Observable()
        start.addObservers([
            (XsltCrosswalk([self.xsltFilename]), [
                Intercept(),
            ])
        ])
        start.do.someMessage(parse(open(self.xmlFilename)))
        self.assertEqualsWS(expectedXml, self.crosswalkedNode[0])