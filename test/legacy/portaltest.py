## begin license ##
#
#    Meresco Core is part of Meresco.
#    Copyright (C) SURF Foundation. http://www.surf.nl
#    Copyright (C) Seek You Too B.V. (CQ2) http://www.cq2.nl
#    Copyright (C) SURFnet. http://www.surfnet.nl
#    Copyright (C) Stichting Kennisnet Ict op school.
#       http://www.kennisnetictopschool.nl
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
from observabletestcase import ObservableTestCase
from cq2utils.calltrace import CallTrace
from cStringIO import StringIO
from meresco.legacy.portal import Portal

PORTAL_PAGE = """<html>
    <body>
        <form method="post" action="%s">
            <table>
                <tr>
                    <td>version</td>
                    <td><input type="text" name="version" value="1.1"></td>
                </tr>
                <tr>
                    <td>operation</td>
                    <td><input type="text" name="operation" value="searchRetrieve"></td>
                </tr>
                <tr>
                    <td>query</td>
                    <td><input type="text" name="query" value=""></td>
                </tr>
                <tr>
                    <td>recordSchema</td>
                    <td><input type="text" name="recordSchema" value="LOMv1.0"></td>
                </tr>
                <tr>
                    <td>startRecord</td>
                    <td><input type="text" name="startRecord" value="1"></td>
                </tr>
                <tr>
                    <td colspan="2" align="right"><input type="submit" value="Query"></td>
                </tr>
            </table>
        </form>
    </body>
</html>"""

class PortalTest(ObservableTestCase):

    def getSubject(self):
        return Portal()

    def testRenderPortal(self):
        self.request = CallTrace('Request')
        self.request.path = '/testdatabase/portal'
        self.request.method = 'GET'
        self.request.args = {}
        self.request.getRequestHostname = lambda: 'localhost'
        class Host:
            def __init__(self):
                self.port = '8000'
        self.request.getHost = lambda: Host()
        self.stream = StringIO()
        self.request.write = self.stream.write
        self.subject.handleRequest(self.request)
        self.assertEqualsWS(PORTAL_PAGE % 'http://localhost:8000/testdatabase/portal', self.stream.getvalue())
