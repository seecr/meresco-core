from urllib import urlopen, urlencode

HEADER = """<html>
	<body>
		<form method="post" action="%s">
			<table>"""

FOOTER = """
				<tr>
					<td colspan="2" align="right"><input type="submit" value="Query"></td>
				</tr>
			</table>
		</form>
	</body>
</html>"""

ROW_TEMPLATE = """
				<tr>
					<td>%(key)s</td>
					<td><input type="text" name="%(key)s" value="%(value)s"></td>
				</tr>"""


class Portal(object):
	def __init__(self):
		self._fieldsOrder = ['version', 'operation', 'query', 'recordSchema', 'startRecord']
		self._fields = {'version':'1.1', 'operation':'searchRetrieve', 'query':'', 'recordSchema':'LOMv1.0', 'startRecord':'1'}
	
	def notify(self, webrequest):
		if webrequest.path.endswith('/portal'):
			if webrequest.method == 'GET':
				webrequest.write(HEADER % self.getRequestUrl(webrequest))
				for key in self._fieldsOrder:
					value = self._fields[key]
					webrequest.write(self._generateHtmlRow(key, value))
				webrequest.write(FOOTER)
			else:
				queryArguments = {}
				for arg in self._fields.keys():
					queryArguments[arg] = webrequest.args.get(arg, [''])[0]
					
				#url = self.getRequestUrl(webrequest)
				#url.replace('/portal', '/sru')
				url = "http://sharelab.cq2.org:8000/lorenet/sru"
				url += "?" + urlencode(queryArguments)
				for line in urlopen(url).readlines():
					webrequest.write(line)

	def _generateHtmlRow(self, key, value):
		return ROW_TEMPLATE % locals()

	def undo(self, *args, **kwargs):
		pass
	
	def getRequestUrl(self, webRequest):
		return 'http://%s:%s' % (webRequest.getRequestHostname(), webRequest.getHost().port) + webRequest.path