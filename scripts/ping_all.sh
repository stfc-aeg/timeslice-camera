#!/bin/bash

start=${1}
shift
end=${1}
shift
start=${start:=1}
end=${end:=48}
args=$*

num_alive=0
num_dead=0
for node in $(seq $start $end); do 
  node_name="cam-${node}"
  #echo -n "$node_name : "
  ping -w 1 -c 1 $node_name >/dev/null 2>&1
  if [ $? -eq 0 ]; then
    state="ALIVE"
    num_alive=$(expr $num_alive + 1)
  else
    num_dead=$(expr $num_dead + 1)
    state="DEAD"
  fi
  printf "%-6s : %-6s  " $node_name $state
  if [ $(expr $node % 8) -eq 0 ]; then
    echo ""
  elif [ $node -eq $end ]; then
    echo ""
  fi
done
printf "Alive: %d  Dead: %d \n" $num_alive $num_dead

