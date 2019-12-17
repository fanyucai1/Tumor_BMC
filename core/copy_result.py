import argparse
import paramiko
from scp import SCPClient

Host = '192.168.1.118'
user = "root"
passwd = "2ghlmcl1hblsqT"
port =22
def run(local_file,To_dir):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(Host, port, user, passwd)
    ssh.exec_command('mkdir -p %s'%(To_dir))
    scpclient = SCPClient(ssh.get_transport())
    scpclient.put(local_file, recursive=True,remote_path=To_dir) # 上传到服务器指定文件
    ssh.close()

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("-d","--dir",help="your destiny directory",required=True)
    parser.add_argument("-f","--file",help="file that you want to copy",required=True)
    args=parser.parse_args()
    run(args.file,args.dir)