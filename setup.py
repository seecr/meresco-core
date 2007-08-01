from distutils.core import setup

setup(
    name='meresco',
    packages=[
'meresco',
'meresco.legacy',
'meresco.legacy.plugins',
'meresco.components',
'meresco.components.http',
'meresco.components.http.oai',
'meresco.components.http.oai.data',
'meresco.components.http.sru',
'meresco.components.drilldown',
'meresco.components.drilldown.cpp',
'meresco.components.lucene',
'meresco.framework'
])
