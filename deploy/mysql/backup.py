import log
from public_module import to_bytes
from public_module.global_vars import getNotifier
from public_module.ssh_connect.paramiko_ssh import ParamikoConnection
from ui.myThread import MyThread


def display_log(channel,stdout):
    while(not channel.closed):
        data = stdout.readline()
        log.info()

def backup():
    cmd = to_bytes('/usr/bin/xtrabackup --defaults-file=/database/my3578/my.cnf -usuper -p8845  --target-dir="/data/backup/my3578/2020-03-09" --slave-info --safe-slave-backup  --backup  --safe-slave-backup-timeout=3000  --compress --compress-threads=4   --socket=/database/my3578/var/3578.socket > /data/backup/my3578/2020-03-09/backup.log 2>&1 ')
    pk = ParamikoConnection('10.45.156.201','mysql','8845')
    channel,stdin,stdout = pk.execute_cmd(cmd)
    logch,logstdin,logstdout = pk.execute_cmd('tail -f /data/backup/my3578/2020-03-09/backup.log')
    notifier = getNotifier()
    thread = MyThread()



