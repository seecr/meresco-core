from distutils.core import setup
from distutils.extension import Extension

setup(
    name='meresco',
    packages=[
        'meresco',
        'meresco.legacy',
        'meresco.legacy.plugins',
        'meresco.components',
        'meresco.components.http',
        'meresco.components.http.oai',
        'meresco.components.http.sru',
        'meresco.components.drilldown',
        'meresco.components.drilldown.cpp',
        'meresco.components.lucene',
        'meresco.framework'
    ],
    package_data={
        'meresco.components.http.oai': ['data/*']
    },
    ext_modules=[
        Extension("meresco.components.drilldown.cpp._bitarray", [
		"meresco/components/drilldown/cpp/bitarray_wrap.cxx",
		"meresco/components/drilldown/cpp/BitArray.cpp"]
		)
    ]
)
