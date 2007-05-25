from observabletestcase import ObservableTestCase

from observers.portal import Portal

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
		self.request.path = '/testdatabase/portal'
		self.request.args = {}
		self.request.method = 'GET'

		self.observable.changed(self.request)
		self.assertEqualsWS(PORTAL_PAGE % 'http://localhost:8000/testdatabase/portal', self.stream.getvalue())