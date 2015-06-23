#!/bin/bash

image_dir=$1
start=$2
end=$3
offset=$4

for src_idx in $(seq $start $end); do

	dst_idx=$(expr $src_idx + $offset)
	src_file=$(printf "%s/image_%02d.jpg" ${image_dir} ${src_idx})
	dst_file=$(printf "%s/image_%02d.jpg" ${image_dir} ${dst_idx})
	cp -f $src_file $dst_file
done