import yaml
import math
import struct

#
#  Python Script for generating the microcode for the controll-logic:
#
#    - The microcode is stored in an yaml file. The file first defined all Instruction and output ControllLines
#    - In SubComands the file defines the actions the CPU can do and which controll lines should be active
#    - Instructions first defines the Fetch-Cycle which runs at the start of the sub-counter.
#    - in CMD the actual instructions are defined. All undefined states are filled with the "UNDEF" Instruction
#    - The BOOT_SEQUENCE runns when the BootFlagg Input is set;
#      it ignores everything and runns a loop that copies every adress from ROM to the system RAM
#       (it uses the ALU Overflow-Flagg to detect when it reaches the end)
#

def compare_optcode(first, seccond):
    if len(first) != len(seccond):
        return False
    for bit0, bit1 in zip(first, seccond):
        if bit0 != "X" or bit1 != "X":
            if bit0 == "1" or bit1 != "1":
                return False
            if bit0 == "0" or bit1 != "0":
                return False
    return True

def generate_all(word):
    o_list = [word]
    no_X = True
    for bit in range(len(word)):
        if word[bit] == "X":
            new_list = []
            for word in o_list:
                new_list.append(word[:bit] + "0" + word[bit+1:])
                new_list.append(word[:bit] + "1" + word[bit+1:])
            o_list = new_list
    return o_list

def get_memory_line(pins, word, step, boot):
    word_length = 0
    step_length = 0
    for p in pins:
        if p[0] == "C":
            step_length += 1
        if p[0] == "I":
            word_length += 1
    line = 0
    for p,n in zip(pins,reversed(range(len(pins)))):
        if p == "B_F":
            bit = (boot >> 0) & 1
        elif p[0] == "C":
            bit = (step >> int(p[2])) & 1
        elif p[0] == "I":
            bit = (int(word, 2) >> int(p[2])) & 1
        else:
            bit = 0
        line = line + (bit* pow(2,n))
    return line

#print(get_memory_line(input_pins, word, step_nr, False))

with open("microcode_DIY-8Bit-CPU.yaml", 'r') as stream:
    data_loaded = yaml.safe_load(stream)

input_pins = data_loaded["PinDefintion"]["InstrucionPins"]
output_pins = data_loaded["PinDefintion"]["ControllLines"]
all_commands = data_loaded["Instructions"]
command_lookup = data_loaded["SubComands"]
print(input_pins)
print(output_pins)

memory_size = pow(2, len(input_pins))
print(memory_size)

bin_table = []
for i in range(memory_size):
    bin_table.append({"Notes":"", "Data":[]})
    for j in range(len(output_pins)):
        bin_table[i]["Data"].append(0)

for CMD_NR in all_commands["FETCH_CYCLE"]:
    print(CMD_NR)
    CMD = all_commands["FETCH_CYCLE"][CMD_NR]
    step_nr = 0
    for step in CMD["Output"]:
        for word in generate_all(CMD["OpCode"]):
            line = get_memory_line(input_pins, word, step_nr, False)
            for action in step.split(", "):
                for subaction in command_lookup[action].split(", "):
                    bin_table[line]["Notes"] = CMD_NR + " " + str(step_nr)
                    bin_table[line]["Data"][output_pins.index(subaction)] = 1
        step_nr +=1

for CMD_NR in all_commands["CMD"]:
    print(CMD_NR)
    CMD = all_commands["CMD"][CMD_NR]
    for word in generate_all(CMD["OpCode"]):
        step_nr = 0
        while bin_table[get_memory_line(input_pins, word, step_nr, False)]["Notes"] != "":
            step_nr +=1
        for step in CMD["Output"]:
            line = get_memory_line(input_pins, word, step_nr, False)
            for action in step.split(", "):
                for subaction in command_lookup[action].split(", "):
                    bin_table[line]["Notes"] = CMD_NR + " " + str(step_nr)
                    bin_table[line]["Data"][output_pins.index(subaction)] = 1
            step_nr +=1

for CMD_NR in all_commands["UNDEFINED"]:
    print(CMD_NR)
    CMD = all_commands["UNDEFINED"][CMD_NR]
    for word in generate_all(CMD["OpCode"]):
        step_nr = 0
        while bin_table[get_memory_line(input_pins, word, step_nr, False)]["Notes"] != "":
            step_nr +=1
        while step_nr <= 7:
            line = get_memory_line(input_pins, word, step_nr, False)
            for action in step.split(", "):
                for subaction in command_lookup[action].split(", "):
                    bin_table[line]["Notes"] = CMD_NR + " " + str(step_nr)
                    bin_table[line]["Data"][output_pins.index(subaction)] = 1
            step_nr +=1

step_nr = 0
for step in all_commands["BOOT_SEQUENCE"]["Output"]:
    line = get_memory_line(input_pins, "00000000", step_nr, True)
    for subaction in step.split(", "):
        bin_table[line]["Notes"] = "BOOT" + " " + str(step_nr)
        bin_table[line]["Data"][output_pins.index(subaction)] = 1
    step_nr +=1
    

print("######################################################################")
print("LINE           DATA                              NOTE")
print("----------------------------------------------------------")
n = 0
for line in bin_table:
    print(format(n, '013b') + " | " + ",".join(str(e) for e in line["Data"]) + " <<<" + line["Notes"])
    n +=1

with open('microcode_DIY-8Bit-CPU.txt', 'w') as f:
    f.write("LINE           DATA                              NOTE\n")
    f.write("----------------------------------------------------------\n")
    n = 0
    for line in bin_table:
        f.write(format(n, '013b') + " | " + ",".join(str(e) for e in line["Data"]) + " <<<" + line["Notes"] + "\n")
        n +=1

with open('microcode_DIY-8Bit-CPU-part2.bin', 'wb') as f:
    for line in bin_table:
        data = int("".join(str(e) for e in line["Data"][:8]) ,2)
        f.write(bytes([data]))

with open('microcode_DIY-8Bit-CPU-part1.bin', 'wb') as f:
    for line in bin_table:
        data = int("".join(str(e) for e in line["Data"][8:16]) ,2)
        f.write(bytes([data]))



#with open('microcode_DIY-8Bit-CPU-part2.bin', 'wb') as f:
#    for line in range(pow(2,8)):
#        data = line
#        f.write(bytes([data]))


