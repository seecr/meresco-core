rm -rf tmp

python setup.py install --root tmp

export PYTHONPATH=/home/erik/uitwisselplatform/meresco/trunk/tmp/usr/lib/python2.4/site-packages

(
cd test
python2.4 alltests.py
)

rm -rf tmp