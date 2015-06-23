#!/bin/bash

image_dir=$1

image_files=$(ls ${image_dir}/image_*.jpg)

dst_idx=1
for image_file in ${image_files}; do
	echo $image_file $(printf "%s/image_%02d.jpg" $image_dir $dst_idx)
	dst_idx=$(expr $dst_idx + 1)
done