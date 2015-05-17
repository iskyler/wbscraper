#!/bin/bash

uri="data"

for file in duang/*.html
do
    str=`grep 'action-type=\\\"feed_list_item' $file`
    str=${str#*html\":\"}
    str=${str%\\n*}
    echo "$str" >> $uri
done

sed -i 's/\\\"/"/g' $uri
sed -i 's/\\\//\//g' $uri
sed -i 's/\\t/ /g' $uri
sed -i 's/\\n/ /g' $uri
