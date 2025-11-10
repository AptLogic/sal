#!/usr/local/sal/Python.framework/Versions/Current/bin/python3


import os
import subprocess

import sal


def main():
    sal.add_plugin_results('Bootstrap Token', {'Bootstrap Token Status': bs_status()})


def bs_status():
    if not os.path.exists('/usr/bin/profiles'):
        status = 'Not Supported'
    else: 

        cmd = ['/usr/bin/profiles', 'status', '-type', 'bootstraptoken']
        try:
            output = subprocess.check_output(cmd, stderr=subprocess.STDOUT, text=True)
        except subprocess.CalledProcessError as error:
            output = str(error.output)
        serverStatus = True if 'supported on server: YES' in output else False
        escrowStatus = True if 'escrowed to server: YES' in output else False
        status = 'Supported, Escrowed' if serverStatus and escrowStatus else 'Not Supported' if not serverStatus else 'Supported, Not Escrowed'

    return status


if __name__ == '__main__':
    main()
