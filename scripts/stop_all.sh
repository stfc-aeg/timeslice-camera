#!/bin/bash

start=${1}
shift
end=${1}
shift
start=${start:=1}
end=${end:=48}

for node in $(seq $start $end); do 
  node_name="cam-${node}"
  echo -n "$node_name : "
#  ssh pi@$node_name 'sudo killall python >/dev/null 2>&1 &'
  ssh pi@$node_name 'sudo /usr/sbin/service timeslice stop'
done

