#!/usr/bin/python3

import sys
import paramiko
import time
import subprocess
import os
import configparser

if len(sys.argv) != 2:
    print("Provide path to config file as command line argument: db_changer /path/to/config.ini.")
    sys.exit()
else:
    print("Config file: " + sys.argv[1])

parser = configparser.ConfigParser()
files = [str(sys.argv[1])]
ok_files = parser.read(files)

if len(ok_files) != len(files):
    raise ValueError("Failed to open/find all files")

key = parser['local']['private_key_path']
dump_location = parser['local']['base_dump_location']
hostname = parser['remote']['hostname']
remote_user = parser['remote']['user']
remote_dump_location = parser['remote']['dump_location']
postgres_database_name = parser['local']['postgres_database_name']
postgres_username = parser['local']['postgres_username']

k = paramiko.RSAKey.from_private_key_file(key)

# TODO: tar dump
dump_filename = "database_dump_" + str(time.time()) + ".dump"
com = "pg_dump -Fc > " + dump_filename

print("Generating db dump on remote location...")
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(hostname=hostname, username=remote_user, pkey=k)
ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(com)

stdout = ssh_stdout.readlines()

output = ""
for line in stdout:
    output = output+line

print("Downloading db dump...")
sftp = ssh.open_sftp()
sftp.get(remote_dump_location + dump_filename,
         dump_location + dump_filename)
sftp.close()

print("Cleaning remote machine...")
com2 = "rm " + dump_filename
ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(com2)

ssh.close()


drop_db = "dropdb -U " + postgres_username + " " + postgres_database_name
create_db = "createdb -U " + postgres_username + " " + postgres_database_name
restore_db = "pg_restore -d " + postgres_database_name + \
    " -U " + postgres_username + " " + dump_location + dump_filename
remove_dump = "rm " + dump_location + dump_filename

print("Drop and create db...")
process = subprocess.Popen(drop_db.split(), stdout=open(os.devnull, 'wb'))
output, error = process.communicate()

process = subprocess.Popen(create_db.split(), stdout=open(os.devnull, 'wb'))
output, error = process.communicate()

print("Restore db from dump...")
process = subprocess.Popen(restore_db.split(), stdout=open(
    os.devnull, 'wb'), stderr=open(os.devnull, 'wb'))
output, error = process.communicate()

print("Cleaning local machine...")
process = subprocess.Popen(remove_dump.split(), stdout=open(os.devnull, 'wb'))
output, error = process.communicate()
