#!/usr/bin/env bash
security_limit_update(){
#1 param_name
#2 param_value
hardlit=`grep -E '^'"$os_user_es"'\s*hard\s*'"${1}"'\s*([0-9]+|unlimited)\s*$' /etc/security/limits.conf|sed -r 's=\s+= =g'|cut -d ' ' -f 4|head -1`
softlim=`grep -E '^'"$os_user_es"'\s*soft\s*'"${1}"'\s*([0-9]+|unlimited)\s*$' /etc/security/limits.conf|sed -r 's=\s+= =g'|cut -d ' ' -f 4|head -1`
alllim=`grep -E '^'"$os_user_es"'\s*-\s*'"${1}"'\s*([0-9]+|unlimited)\s*$' /etc/security/limits.conf|sed -r 's=\s+= =g'|cut -d ' ' -f 4|head -1`
if [ "${alllim}" ];then
	if [ ${alllim} != 'unlimited' ] && [ "${alllim}" -lt  ${2} ];then
		 sed -i -r 's=(^'"$os_user_es"'\s*-\s*'"${1}"'\s*)([0-9]+|unlimited)\s*$=\1'" ${2}=" /etc/security/limits.conf 
		[ $? -ne 0 ] && return 1
	fi
else
	if [ ${hardlit}   ];then 
		if [ ${hardlit} != 'unlimited' ] && [ ${hardlit} -lt ${2} ];then 
			sed -i -r 's=(^'"$os_user_es"'\s*hard\s*'"${1}"'\s*)([0-9]+|unlimited)\s*$=\1'" ${2}=" /etc/security/limits.conf
			[ $? -ne 0 ] && return 1
		fi
	else
		echo "$os_user_es hard ${1} ${2}" >> /etc/security/limits.conf 
		[ $? -ne 0 ] && return 1
	fi
	if [ ${softlim}  ];then 
		if [ ${softlim} != 'unlimited' ] && [ ${softlim} -lt ${2} ];then
			sed -i -r 's=(^'"$os_user_es"'\s*soft\s*'"${1}"'\s*)([0-9]+|unlimited)\s*$=\1'" ${2}=" /etc/security/limits.conf
			[ $? -ne 0 ] && return 1
		fi
	else
		echo "$os_user_es soft ${1} ${2}" >> /etc/security/limits.conf 
		[ $? -ne 0 ] && return 1
	fi
fi
return 0
}

sysctl_update(){
v=`grep -E '^'"${1}"'=\s*[0-9]*\s*$' /etc/sysctl.conf|sed -r 's=\s+==g'|cut -d '=' -f 2|head -1`
if [ ! $v ];then 
	echo "${1}=${2}" >> /etc/sysctl.conf
else
	if [ $v -lt ${2} ];then 
		sed -i -r 's%'"${1}"'=[0-9]*%\1='"${2}"'%' /etc/sysctl.conf
	fi
fi
return 0
}

cur_time=`date +%Y-%m-%d-%H-%M-%S`
limit_file="/etc/security/limits.conf"
cp ${limit_file}   ./limit.conf.$cur_time
os_user_es="elasticsearch"
security_limit_update "nofile" 65536 
[ $? -ne 0 ] && echo " update ${limit_file} with nofile failed ." && exit 1
security_limit_update "memlock" "unlimited" 
[ $? -ne 0 ] && echo " update ${limit_file} with memlock failed ." && exit 1
security_limit_update "nproc" "2048" 
[ $? -ne 0 ] && echo " update ${limit_file} with nproc failed ." && exit 1
sysctl_update "vm.max_map_count" 262144 
[ $? -ne 0 ] && echo " update /etc/sysctl.conf with vm.max_map_count failed . " && exit 1
exit 0