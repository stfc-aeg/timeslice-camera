#!/bin/bash

req_user="pi"
provision_dir=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
project_dir="/home/pi/develop/projects"
repo_url="pi@te7gala:/opt/git/projects/timeslice"
timeslice_dir=${project_dir}/timeslice

if [[ $USER != $req_user ]]; then
    echo "This script must be run as user $req_user"
    exit 1
fi

if [[ $# < 1 ]]; then
    echo "Must specify a node hostname"
    exit 1
fi

node=$1
echo "Provisioning timeslice camera node $node ..."

echo "Copying SSH keys ..."
scp ~pi/.ssh/id_dsa.pub ~pi/.ssh/id_dsa ~pi/.ssh/authorized_keys ${node}:.ssh/.

echo "Copying /etc/hosts file ..."
scp $provision_dir/hosts ${node}:/tmp/.
ssh -t ${node} 'sudo mv /tmp/hosts /etc/.'

echo -n "Checking if $project_dir exists ... "
ssh ${node} ls $project_dir >/dev/null 2>&1
exists=$?
if [[ $exists != 0 ]]; then
  echo -n "no. Creating it ... "
  ssh ${node} mkdir -p $project_dir
  echo "done."
else
  echo "yes."
fi

echo -n "Checking if $timeslice_dir working copy exists ... "
ssh ${node} ls $timeslice_dir >/dev/null 2>&1
exists=$?
if [[ $exists != 0 ]]; then
  echo "no. Cloning it from git repo."
  ssh -t ${node} git clone $repo_url $timeslice_dir
else
  echo "yes."
fi

