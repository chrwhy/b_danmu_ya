#!/bin/sh
#pid=`ps -ef | grep dmya | awk 'NR==1{print}' | awk '{print $2}'`
#kill $pid

kill `ps -ef | grep dmya | awk 'NR==1{print}' | awk '{print $2}'`
