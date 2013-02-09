#!/bin/bash

TEMP_FILE=/tmp/version_switch_temp_file_$$

for file in `find . -iname '*.py'`
do
#  echo $file
  grep python2.6 $file > /dev/null
  if [ $? == 0 ] ;
  then
    echo "Fixing: $file"
    sed 's/python2\.6/python2/g' $file > $TEMP_FILE
    cat $TEMP_FILE > $file
  fi
done;

rm -f $TEMP_FILE
