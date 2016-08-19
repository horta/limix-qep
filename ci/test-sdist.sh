#!/bin/bash

set -e -x

python setup.py sdist
FILENAME=`ls sdist/ | head -1`
pip install sdist/$FILENAME
python -c "import limix_qep; limix_qep.test()"