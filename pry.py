'''
This script attempts to log into a subnet of Ubiquiti radios
for the purpose of determining the actual and desired airmax priority.
'''
import os
import sys
import getopt
import configparser
from time import sleep
from concurrent.futures import ThreadPoolExecutor
import ipcalc
import paramiko
from scp import SCPClient




def remote_access(ip_addr):
    '''
    Copies shell script to IP of ip_addr and executes it, taking the output.
    '''
    print('process id:', os.getpid())
    print(f'Logging into {ip_addr}')
    # paramiko.util.log_to_file("paramiko.log")
    result_string_list = []
    host = str(ip_addr)
    username = USERNAME
    password = PASSWORD
    port = str(PORT)
    ssh = paramiko.client.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(host, username=username, password=password, port=port)
        scp = SCPClient(ssh.get_transport())
        scp.put('rem_script.sh', 'rem_script.sh')
        _stdin, _stdout,_stderr = ssh.exec_command("chmod 755 rem_script.sh")
        _stdin, _stdout,_stderr = ssh.exec_command("./rem_script.sh")
        sleep(10)
        result = _stdout.read().decode()
        formatted_result = ((result.rstrip()).replace('\r', '')).split("\n")

        # Check actual priority against expected priority.

        if formatted_result[0] != formatted_result[1]:
            result_string_list.append(str(ip_addr))
            result_string_list.append(" fails expectations.  Desired priority:  ")
            result_string_list.append(str(formatted_result[0]))
            result_string_list.append(".  Actual priority:  ")
            result_string_list.append(str(formatted_result[1]))
            result_string_list.append(".")
            result_message = "".join(result_string_list)
            print(result_message)

        else:
            result_string_list.append(str(ip_addr))
            result_string_list.append(" is fine.")
            result_message = "".join(result_string_list)
            ssh.close()
        logfile.write(result_message + "\n")
    except paramiko.ssh_exception.NoValidConnectionsError:
        print(f'Could not connect to:  {ip_addr}')

def cleanup():
    '''
    Cleanup function.
    '''
    print('Cleaning up.')

def get_options():
    '''
    Pull switches from execution.
    '''
    _specified_network = None

    argv = sys.argv[1:]

    try:
        opts, arg = getopt.getopt(argv, "n:c")

    except getopt.GetoptError:
        print("Input error.  Usage is: python3 pry.py -n X.X.X.X/X")

    for opt, arg in opts:
        if opt in ['-n']:
            _specified_network = arg

        elif opt in ['-c']:
            cleanup()
    return _specified_network

if __name__ == '__main__':

    config = configparser.ConfigParser()
    config.read("pry.ini")
    USERNAME = config.get("pryvars", "username")
    PORT = int(config.get("pryvars", "port"))
    PASSWORD = config.get("pryvars", "password")
    specified_network = get_options()
    try:
        os.remove("log.txt")
    except FileNotFoundError:
        print("No log.txt found.  Creating..")

    with open("log.txt", "w") as logfile:

        print("Network: " + specified_network + " specified.")
        WORKERS = 10
        lister = ipcalc.Network(specified_network)
        with ThreadPoolExecutor(max_workers=WORKERS) as executor:
            executor.map(remote_access,lister)
