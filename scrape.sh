#!/bin/bash

uri="data"

for file in duang/*.html
do
    str=`grep 'action-type=\\\"feed_list_item' $file`
    str=${str#*html\":\"}
    str=${str%\\n*}
    echo "$str" >> $uri
done
