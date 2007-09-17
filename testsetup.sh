set -e

rm -rf tmp build

python setup.py install --root tmp

export PYTHONPATH=`pwd`/tmp/usr/lib/python2.4/site-packages

(
cd test
python2.4 alltests.py
)

rm -rf tmp build