## begin license ##
#
#    BitMatrix determines the cardinality of any given row with rows in a matrix.
#    Copyright (C) 2007-2008 Seek You Too (CQ2) http://www.cq2.nl
#
#    This file is part of BitMatrix
#
#    BitMatrix is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    BitMatrix is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with $PROGRAM; if not, write to the Free Software
#    Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#
## end license ##
from distutils.core import setup
from distutils.extension import Extension
from Pyrex.Distutils import build_ext

setup(
    name='collector',
    packages=['collector'],
    ext_modules = [
        Extension("collector.collector", ["collector/collector.pyx", "collector/collector_misc.c"],
        extra_compile_args = ['-O3'])
    ],
    cmdclass = {'build_ext': build_ext},
    version='%VERSION%',
    url='http://www.cq2.nl/view/Expertise.document',
    author='Seek You Too',
    author_email='info@cq2.nl',
    description='BitMatrix determines the cardinality of any given row with rows in a matrix.',
    long_description='BitMatrix determines the cardinality of any given row with rows in a matrix.',
    license='GNU Public License',
    platforms='all',
)
