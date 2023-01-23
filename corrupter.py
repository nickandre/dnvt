# 32 kbps CVSD Decoder for Digital Non-secure Voice Terminals with Exponential Average Filtering
# 
# Nick Andre and Robert Ruark
# 2023

import wave

import matplotlib.pyplot as plt
import numpy as np
import sys
import random

ERROR = 0.001

#Set high to enable debug graphs
GRAPH_DEBUG = 0

def corrupter(input, output):
    #print(type(input))
    #print(input)
    bitcount    = 0
    errorcount  = 0
    for nibble in input:
        #print(type(nibble))
        #print(nibble)
        bin = int(nibble, 16)
        sample = 0
        for i in range(4):
            bitcount += 1
            bitmask = 0b1 << i
            current_bit = 1 if bin & bitmask else 0
            if random.random() < ERROR:
                current_bit = not current_bit
                errorcount += 1
            sample |= current_bit << i
        output.write(f'{sample:x}')
    print(float(errorcount)/float(bitcount))

if __name__ == '__main__':
    with open('cvsd_data/genesis_reencoded.hex', 'r') as f:
        input = f.read()
        with open('cvsd_data/genesis_reencoded_corrupted_001.hex', 'w') as output:
            corrupter(input, output)