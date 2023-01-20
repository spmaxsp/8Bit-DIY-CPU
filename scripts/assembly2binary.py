from ast import Pass
import yaml

variables = {}
used_jumppoints = {}
defined_jumppoints = {}

bin_output = []

bin_linecounter = 0

with open('the-zen-of-python.txt') as f:
    for line in f:
        actions = line.strip().split(" ")
        for action in actions:
            if action[0] == "/":
                if action[1] == "/":
                    pass
            elif action[0] == "%":
                if action[-1] == "%":
                    pass
                else:
                    pass
            elif action[0] == "$":
                if action[-1] == "$":
                    pass
                else:
                    pass

