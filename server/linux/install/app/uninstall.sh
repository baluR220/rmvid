#!/bin/bash
#run only as sudo.

#check if script is run by sudo
if [[ $EUID -ne 0 ]]
	then echo "[***] run this script as sudo. exiting"
	exit 1
fi

#change directory script directory
p=$(dirname $(realpath "$0" ))
cd $p

echo "[***] rmvid server uninstall started"
