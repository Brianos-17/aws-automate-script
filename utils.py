#!/usr/bin/env python3

import time

# prompt: Message for user
# high: the max number input can't go over
def input_int(prompt):
    while True:
        # asks user for input
        print("Exit: ex")
        int_input = input(prompt)
        
        if int_input == "ex":
            print("Returning to menu...")
            time.sleep(3)
            return
        
        # checks to make sure user input is only a number
        # if not then it restarts loop
        if not int_input.isdigit():
            print('Invalid input: ' + str(int_input) + '\n')
            continue
        else:
            return int_input