import os

import paramiko
from paramiko import SSHClient, SSHException


class HPCTask:
    def __init__(self, workdir='.'):
        self._ssh_jump = None
        self.jobid = None
        self.ssh_client = None
        self.workdir = workdir

    def connect(self, target_host, jump_host=None):
        """
        开启队列
        :return: jobid
        """
        # 建立 ssh 连接
        # 跳板机连接信息
        if self.ssh_client is None:
            try:
                # 使用隧道连接到目标服务器
                target_client = SSHClient()
                target_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                # 首先连接到跳板机
                if jump_host is not None:
                    # 创建SSH客户端
                    jump_client = SSHClient()
                    jump_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                    jump_client.connect(**jump_host)
                    # 在跳板机上创建到目标服务器的隧道
                    transport = jump_client.get_transport()
                    dest_addr = (target_host['hostname'], target_host['port'])
                    local_addr = ('127.0.0.1', 0)  # 本地任意端口
                    channel = transport.open_channel('direct-tcpip', dest_addr, local_addr)
                    target_client.connect('127.0.0.1',
                                          port=channel.getpeername()[1],
                                          username=target_host['username'],
                                          password=target_host['password'],
                                          sock=channel)
                    self._ssh_jump = jump_client
                else:
                    target_client.connect(**target_host)

                self.ssh_client = target_client
                print("Connect to SSH success.")
            except SSHException as e:
                raise e

    def prerun(self):
        # 提交任务，占据节点
        # TODO: 命令改成配置，适配常见 hpc

        if self.ssh_client is None:
            raise RuntimeError('ssh client is not connected')
        commands = [f'mkdir -p {self.workdir}',
                    f'cd {self.workdir}',
                    f'cp ~/bin/hpc_job.chess hpc_job.chess',
                    f'bsub < hpc_job.chess']
        stdin, stdout, stderr = self.ssh_client.exec_command(';'.join(commands))
        jobid = stdout.read().decode().strip()  # "Job <688518> is submitted to queue <proj>."
        jobid = jobid.split()[1].lstrip('<').rstrip('>')
        self.jobid = jobid
        return stdin, stdout, stderr

    def postrun(self):
        """
        说明：关闭任务节点占用
        bkill JOBID是从任务头部开始杀, KILL 信号会传递到子进程
        pkill gosh-remote 是直接杀
        二者可能相同, 也可能不相同. 取决于 bsub 时如何定义的.
        通常 bsub 是用一个 script 调 gosh-remote, 这时二者就不同了.
        那个主调script 可能会做信号处理, 会顺着 gosh-remote的调用进程下去, 逐一 KILL.
        gosh-remote我不记得是否有信号处理的逻辑, 得做实验确认一下.

        :return:

        TODO: 命令改成配置，适配常见 hpc
        """

        if self.ssh_client is None:
            raise RuntimeError('ssh client is not connected')
        commands = ['sleep 1', 'pkill gosh-remote', f'bkill {self.jobid}']
        stdin, stdout, stderr = self.ssh_client.exec_command(';'.join(commands))
        return stdin, stdout, stderr

    @property
    def status(self):
        """
        查询作业状态：排队，运行，结束
        # TODO: 统一不同的排队系统状态码
        :return:
        """
        if self.ssh_client is None:
            raise RuntimeError('ssh client is not connected')
        commands = [f'bjobs -noheader {self.jobid}',]
        stdin, stdout, stderr = self.ssh_client.exec_command(';'.join(commands))
        stat = stdout.read().decode().strip().split()  # 688559  renpeng RUN   proj       Khpcserver0 72*Knode44  scheduler  Sep  8 10:55
        if len(stat) > 5:
            return stat[2]
        else:
            return "UNKNOWN"

    def submit(self):
        """

        :return: None
        """
        return None

    def upload(self):
        """
        TODO: 使用 rsync
        :return: file sync status
        """
        if self.ssh_client is None:
            raise RuntimeError('ssh client is not connected')

        # 创建服务器目录，如果不存在
        self.ssh_client.exec_command(f'if [ ! -d "{self.workdir}" ]; then mkdir -p {self.workdir};fi')
        sftp_client = self.ssh_client.open_sftp()
        filelist = os.listdir(self.workdir)  # TODO: 递归所有文件夹
        for filename in filelist:
            sftp_client.put(os.path.join(self.workdir,filename), os.path.join(self.workdir,filename), confirm=False)
        sftp_client.close()
        return None

    def download(self):
        if self.ssh_client is None:
            raise RuntimeError('ssh client is not connected')

        sftp_client = self.ssh_client.open_sftp()
        for filename in sftp_client.listdir(self.workdir):  # TODO: 递归所有文件夹
            sftp_client.get(os.path.join(self.workdir,filename), os.path.join(self.workdir,filename))
        sftp_client.close()
        return None

    def close(self):
        """
        关闭队列
        """
        if self.ssh_client is not None:
            self.ssh_client.close()
        if self._ssh_jump is not None:
            self._ssh_jump.close()
        return None