from distutils.core import setup
from distutils.extension import Extension
from Pyrex.Distutils import build_ext

setup(
    name='meresco',
    packages=[
        'meresco',
        'meresco.components',
        'meresco.components.drilldown',
        'meresco.components.drilldown.cpp',
        'meresco.components.http',
        'meresco.components.lucene',
        'meresco.components.oai',
        'meresco.components.sru',
        'meresco.legacy',
        'meresco.legacy.plugins',
        'meresco.framework'
    ],
    package_data={
        'meresco.components.oai': ['data/*']
    },
    ext_modules=[
        Extension("meresco.components.drilldown.cpp._bitarray", [
		"meresco/components/drilldown/cpp/bitarray_wrap.cxx",
		"meresco/components/drilldown/cpp/BitArray.cpp"]
		),
        Extension("meresco.components.drilldown.bitmatrix", [
		"meresco/components/drilldown/bitmatrix/bitmatrix.pyx",
		"meresco/components/drilldown/bitmatrix/bitmatrix_misc.c"],
        extra_compile_args = ['-O3']
		)
    ],
    cmdclass = {'build_ext': build_ext}
)
