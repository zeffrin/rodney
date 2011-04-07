#!/bin/zsh

PYTHON=/usr/bin/python
PID=`ps auxw | grep python | grep rodney.py | grep tylinial | awk {'print $2'}`

if  [ -z $PID ]; then
  echo "Rodney:  Loading"
  cd /home/tylinial/pyrodney
  $PYTHON -mcompileall .
  $PYTHON rodney.py &|
fi
