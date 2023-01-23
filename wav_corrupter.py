# 32 kbps CVSD Encoder for Digital Non-secure Voice Terminals
# 
# Nick Andre and Robert Ruark
# 2023

import wave

from scipy import signal
from scipy.fft import fft, fftfreq
import matplotlib.pyplot as plt
import numpy as np
import sys
import random

ERROR = 0.001

def corrupt(input, file):
    frames = input.getnframes()
    for i in range(frames):
        frame = input.readframes(1)
        pcm_value = int.from_bytes(frame, 'little', signed=True)
        for j in range(16):
            bitmask = 0b1 << j
            if(random.random()<ERROR):
                pcm_value=pcm_value ^ bitmask
        if pcm_value > 32767:
            pcm_value = 32767
        elif pcm_value < -32768:
            pcm_value = -32768
        file.writeframes(int(pcm_value).to_bytes(2, 'little', signed=True))

if __name__ == '__main__':
    with wave.open('wav_data/genesis-iir.wav', 'rb') as input:
        with wave.open('wav_data/genesis-iir_corrupted_001.wav', 'wb') as f:
            f.setsampwidth(2)
            f.setnchannels(1)
            f.setframerate(32000)
            corrupt(input, f)

