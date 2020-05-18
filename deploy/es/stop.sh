#!/usr/bin/env bash
cpwd=$(cd `dirname $0`;pwd)
basedir=${cpwd%/*}
export ES_PATH_CONF=${basedir}/config
pkill -F ${basedir}/var/pid
