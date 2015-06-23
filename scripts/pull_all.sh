#!/bin/bash

start=${1}
shift
end=${1}
shift
start=${start:=1}
end=${end:=8}

for node in $(seq $start $end); do 
  node_name="cam-${node}"
  echo -n "$node_name : "
  ssh pi@$node_name 'cd /home/pi/develop/projects/timeslice/camera_server; git pull >/dev/null 2>&1 &'
done

