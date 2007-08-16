from distutils.core import setup
from distutils.extension import Extension
from Pyrex.Distutils import build_ext

setup(
	name='bitmatrix',
	ext_modules = [
	 	Extension("bitmatrix", ["bitmatrix.pyx", "bitmatrix_misc.c"],
		   extra_compile_args = ['-O3'])
	   ],
	cmdclass = {'build_ext': build_ext}
)
