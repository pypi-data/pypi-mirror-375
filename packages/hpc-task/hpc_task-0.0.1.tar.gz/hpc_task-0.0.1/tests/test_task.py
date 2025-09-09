import os

import pytest
import ase
from ase.calculators.vasp import Vasp
from hpc_task.hpc import HPCTask

jump_host = {
    'hostname': os.getenv("JUMP_HOST_IP"),
    'port': int(os.getenv("JUMP_HOST_PORT")),
    'username': os.getenv("JUMP_HOST_USER"),
    'password': os.getenv("JUMP_HOST_PASS"),  # 建议使用密钥认证而非密码
}

target_host = {
    'hostname': os.getenv("TARGET_HOST_IP"),
    'port': int(os.getenv("TARGET_HOST_PORT")),
    'username': os.getenv("TARGET_HOST_USER"),
    'password': os.getenv("TARGET_HOST_PASS"),  # 建议使用密钥认证而非密码
}

class TestHPCTask:
    def setup_method(self):
        pass

    def teardown_method(self):
        pass


    def test_connect(self):
        hpc = HPCTask()
        hpc.connect(target_host, jump_host)
        stdin, stdout, stderr = hpc.ssh_client.exec_command('hostname')
        print(stdout.read().decode().strip())
        hpc.close()

    def test_pre_post_run(self):
        workdir = 'test_hpc_run'
        hpc = HPCTask(workdir=workdir)
        hpc.connect(target_host, jump_host)
        stdin, stdout, stderr = hpc.prerun()
        print(hpc.jobid)
        print(f"Job {hpc.jobid} status: {hpc.status}")
        stdin, stdout, stderr = hpc.postrun()
        print(stdout.read().decode().strip())

    def test_upload(self):
        workdir = 'test_hpc_run'
        hpc = HPCTask(workdir=workdir)
        hpc.connect(target_host, jump_host)
        # 在本地创建 workdir
        if not os.path.exists(workdir):
            os.makedirs(workdir)
        # 新建一个空文件
        with open(os.path.join(workdir, 'test.xyz'), 'w') as f:
            f.write('test')
        hpc.upload()

    def test_download(self):
        workdir = 'test_hpc_run'
        hpc = HPCTask(workdir=workdir)
        hpc.connect(target_host, jump_host)
        if not os.path.exists(workdir):
            os.makedirs(workdir)
        hpc.download()

    def test_vasp_calc(self):
        atoms = ase.Atoms('N2', positions=[(0.,0.,0.),(1.4,0.,0.)],cell=[10,10,10], pbc=True)
        workdir = 'test_vasp_calc'
        curdir = os.path.abspath('.')
        python_command = [   # TODO: 写成一个python 的 template
            "from hpc_task.hpc import HPCTask",
            "import os",
            f"os.chdir('{curdir}')",
            f"hpc = HPCTask(workdir='{workdir}')",
            f"hpc.connect({target_host}, {jump_host})",
            "hpc.upload()",
            f"stdin,stdout,stderr = hpc.ssh_client.exec_command('cd {workdir};mpirun -np 2 vasp544_std')",
            "print(stdout.read().decode().strip())",
            "hpc.download()",
            "hpc.close()",
        ]
        calc_command = f'python -c "{';'.join(python_command)}"'
        calc = Vasp(xc='pbe',
                    command=calc_command,
                    directory=workdir,
                    gamma=True,
                    encut=400,
                    lwave=False,
                    lcharg=False,
                    )
        atoms.calc = calc
        e = atoms.get_potential_energy()
        print(f"Energy of N2 is {e} eV.")
