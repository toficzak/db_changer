db_changer.py

Script is used to replace current database on localhost with current database of remote server.
Uses ssh/scp/pg_dump/db_drop/db_create/pg_restore and rm to clean.

Works only for postgres.
Requires postgres password in .pgpass and rsa private key registered as authorized key on remote machine. Also assumes unrestricted access to pg_dump on remote machine.

Usage:
python3 db_changer.py /path.to.config.ini

This is my personal micro-tool, so it is fast and dirty.

Written in python3, just a challange for former java dev.
