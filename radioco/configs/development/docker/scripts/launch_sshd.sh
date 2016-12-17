#!/bin/bash -x
# Activating SSHD
/usr/sbin/sshd
# Keep container running 
tail -f /dev/null