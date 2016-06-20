#!/bin/bash

start=${1}
shift
end=${1}
shift
start=${start:=1}
end=${end:=48}

cmd=$@

for node in $(seq $start $end); do 
  node_name="cam-${node}"
  echo -n "$node_name : "
  ssh pi@$node_name sudo /sbin/poweroff

done



