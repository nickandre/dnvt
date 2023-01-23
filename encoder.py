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

#Set high to enable debug graphs
GRAPH_DEBUG = 0

SCALE = 250
LINEAR_THRESHOLD = 0.8
SECOND_THRESHOLD = 0.9
MAX_GAIN = 20

def pcm_to_dnvt(input, output):
    current_value = 0
    coincidence_counter = 0
    ones_count = 0
    zeros_count = 0
    gain = 0
    one_instances = 0
    zero_instances = 0
    coincidences = 0
    sample = 0
    frames = input.getnframes()
    index = 0
    time                   = []
    graph_pcm_value        = []
    graph_filtered_pcm_val = []
    graph_cvsd_val         = []
    graph_gain             = []
    graph_bits             = []
    max_frames = 500000
    previous_pcm = 0
    for i in range(frames):
        #TODO: burn first byte
        bit_index = 3 - (i % 4)
        frame = input.readframes(1)
        pcm_value = int.from_bytes(frame, 'little', signed=True)
        # Y/X = 1 - a*z^-1
        # Y = X - Xaz^-1
        # y[n] = x[n] - ax[n-1]
        a = 0.0 # Emphesis disabled
        b = 1.0 # Emphesis disabled
        filtered_pcm_val = b*(pcm_value - previous_pcm * a)  # + prev2_val * 0.33
        previous_pcm = pcm_value
        if filtered_pcm_val >= current_value:
            current_bit = 1
        else:
            current_bit = 0
        sample |= current_bit << bit_index

        if abs(coincidence_counter) >= 3:
            if gain < MAX_GAIN:
                gain += 0.72

            coincidences += 1

        if current_bit == 1:
            one_instances += 1
            if coincidence_counter < 0:
                coincidence_counter = 1
            else:
                coincidence_counter += 1
            current_value += (gain + 1) * SCALE
        else:
            zero_instances += 1
            if coincidence_counter > 0:
                coincidence_counter = -1
            else:
                coincidence_counter -= 1
            current_value -= (gain + 1) * SCALE

        current_value *= 0.98
        gain *= 0.9875778



        if bit_index == 0:
            #output.write(sample.to_bytes(1, 'little'))
            output.write(f'{sample:x}')
            sample = 0
        index+=1 #time index
        time.append(index/32000)
        graph_pcm_value.append(pcm_value)
        graph_filtered_pcm_val.append(filtered_pcm_val)
        graph_cvsd_val.append(current_value)
        graph_gain.append(gain)
        graph_bits.append(current_bit)

        # tODO: The de-emphasis IIR filter implemented here is:
        # H(z) = 1 / (1 - az^-1) for 0.92 < a < 0.98
        # a = 0.90
        # filtered_val = (current_value + previous_filtered * a) / 2 # + prev2_val * 0.33
        # previous_filtered = filtered_val
        # y_sos, zi = signal.sosfilt(sos=sos, x=[filtered_val], zi=zi)
        # fir_val = y_sos[0]
        # if fir_val > 32767:
        #     fir_val = 32767
        # elif fir_val < -32768:
        #     fir_val = -32768
        # #if i % 4 == 0:
        # f.writeframes(int(fir_val).to_bytes(2, 'little', signed=True))
        # i += 1

    #print(f'coincidences {coincidences} samples {len(data) * 4}')
    imbalance = abs(one_instances - zero_instances)
    imbalance_percent = imbalance/(one_instances + zero_instances)*100
    print(f'Ones: {one_instances} Zeros: {zero_instances} Imbalance {imbalance} = {imbalance_percent} %')
    # from scipy.fft import fft, fftfreq
    #
    # # Number of samples in normalized_tone
    # N = SAMPLE_RATE * DURATION
    #
    # yf = fft(normalized_tone)
    # xf = fftfreq(N, 1 / SAMPLE_RATE)
    #
    # plt.plot(xf, np.abs(yf))
    # plt.show()

    if(GRAPH_DEBUG):
        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, constrained_layout=True, sharex=True)
        ax1.plot(time, graph_gain)
        ax2.plot(time, graph_cvsd_val, time, graph_pcm_value, time, graph_filtered_pcm_val)
        ax3.step(time, graph_bits, 'o--')
        plt.ylabel('Counts')
        plt.xlabel('Time (seconds)')
        ax1.set_title('Gain')
        ax2.set_title('Input and Regenerated Output')
        ax3.set_title('Output Bits')
        plt.show()

if __name__ == '__main__':
    with wave.open('wav_data/genesis-iir.wav', 'rb') as input:
        with open('cvsd_data/genesis_reencoded.hex', 'w') as output:
            pcm_to_dnvt(input, output)

