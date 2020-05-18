#!/usr/bin/env bash
cpwd=$(cd `dirname $0`;pwd)
basedir=${cpwd%/*}
MES_HOME=${basedir}/software/elasticsearch-5.4.3
export ES_PATH_CONF=${basedir}/config
${MES_HOME}/bin/elasticsearch -Epath.conf="${ES_PATH_CONF}" -d -p ${basedir}/var/pid
