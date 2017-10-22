#!/usr/bin/env python3

import subprocess

# Asks user if they wish to start running nginx
def run_nginx():
    #user input
    will_run = input('Start nginx?(yes/n): ')
    #converts to lower case
    will_run = str.lower(will_run)
    
    # checks user's input and will run nginx if input = 'y'
    if will_run == 'yes':
        (status, output) = subprocess.getstatusoutput('sudo service nginx start')
        print(output)
    elif will_run == 'n':
        print('nBoot ngin: Denied')
    # in case user inputs an invalid entry
    else:
        print('Invalid entry: ' + will_run)

# Asks user if they wish to stop nginx running
def stop_nginx():
    # user input
    will_stop = input('Stop nginx?(yes/n): ')
    #converts to lower case
    will_stop = str.lower(will_stop)
    
    # checks user input and will stop ngrinx if input = 'n'
    if will_stop == 'yes':
        (status, output) = subprocess.getstatusoutput('sudo service nginx stop')
        print(output)
    elif will_stop == 'n':
        print('Stop nginx: Denied')
    # in case user inputs an invalid entry
    else:
        print('Invalid entry: ' + will_stop)

# performs a grep search to look for any processes that involve nginx are running
def check_nginx():
    term = 'nginx'
    cmd = 'ps -A | grep ' + term
    
    # If command had a problem (status is non-zero)
    (status, output) = subprocess.getstatusoutput(cmd)
    
    # will prompt user if nginx processes are running or not
    # will ask the user if they wish to stop or run nginx
    if status > 0:
        print('NOT RUNNING')
        run_nginx()
    else:
        print('RUNNING')
        stop_nginx()

def main():
    check_nginx()

if __name__ == "__main__":
    main()